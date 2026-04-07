# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, time_diff_in_hours

class SpaceBooking(Document):
	def validate(self):
		self.calculate_duration()
		self.calculate_amenity_costs()
		self._apply_dynamic_pricing()
		self.calculate_amounts()
		self.check_availability()

	def on_submit(self):
		self.status = "Confirmed"
		self.db_set("status", "Confirmed")
		self._generate_qr_code()

	def on_cancel(self):
		self.status = "Cancelled"
		self.db_set("status", "Cancelled")
		# Free up the space if it was occupied by this booking
		if self.space:
			space_status = frappe.db.get_value("Co-working Space", self.space, "status")
			current_member = frappe.db.get_value("Co-working Space", self.space, "current_member")
			if space_status == "Occupied" and current_member == self.member:
				frappe.db.set_value("Co-working Space", self.space, {
					"status": "Available",
					"current_member": None,
				})

	def calculate_duration(self):
		"""Calculate booking duration."""
		if self.start_datetime and self.end_datetime:
			self.duration_hours = flt(
				time_diff_in_hours(self.end_datetime, self.start_datetime), 2
			)
			if self.duration_hours <= 0:
				frappe.throw(_("End time must be after start time"))

	def _apply_dynamic_pricing(self):
		"""Apply dynamic pricing rules to the rate.

		Adjusts self.rate based on active Pricing Rules. Skips if the user
		has manually set a rate and flagged skip_dynamic_pricing.
		"""
		if self.flags.get("skip_dynamic_pricing"):
			return
		if not self.space or not self.rate:
			return

		try:
			from arkspace.arkspace_spaces.pricing_engine import (
				calculate_dynamic_rate,
			)
		except ImportError:
			return

		space_doc = frappe.get_cached_doc("Co-working Space", self.space)

		context = {
			"base_rate": flt(self.rate),
			"booking_type": self.booking_type,
			"start_datetime": self.start_datetime,
			"end_datetime": self.end_datetime,
			"duration_hours": flt(self.duration_hours),
			"space": self.space,
			"space_type": space_doc.space_type if space_doc else "",
			"member": self.member,
		}

		result = calculate_dynamic_rate(context)

		if result.get("adjustments"):
			self.rate = flt(result["final_rate"], 2)
			# Store adjustment details as a comment for audit trail
			adj_summary = ", ".join(
				f"{a['rule_name']} ({a['change_pct']:+.1f}%)"
				for a in result["adjustments"]
				if "change_pct" in a
			)
			if adj_summary:
				self.add_comment(
					"Info",
					_("Dynamic pricing applied: {0}").format(adj_summary),
				)

	def calculate_amounts(self):
		"""Calculate total and net amounts."""
		if not self.rate or not self.duration_hours:
			return

		if self.booking_type == "Hourly":
			self.total_amount = flt(self.rate * self.duration_hours, 2)
		elif self.booking_type == "Daily":
			days = max(1, self.duration_hours / 24)
			self.total_amount = flt(self.rate * days, 2)
		else:  # Monthly
			months = max(1, self.duration_hours / (24 * 30))
			self.total_amount = flt(self.rate * months, 2)

		# Add amenity costs
		self.total_amount = flt(self.total_amount + flt(self.amenity_total), 2)

		discount = flt(self.discount_percent or 0)
		self.net_amount = flt(self.total_amount * (1 - discount / 100), 2)

	def calculate_amenity_costs(self):
		"""Calculate add-on amenity costs."""
		self.amenity_total = 0
		if not self.get("booking_amenities"):
			return

		rate_field_map = {
			"Hourly": "hourly_price",
			"Daily": "daily_price",
			"Monthly": "monthly_price",
		}
		rate_field = rate_field_map.get(self.booking_type, "hourly_price")

		for row in self.booking_amenities:
			if not row.amenity:
				continue
			amenity = frappe.get_cached_doc("Amenity", row.amenity)
			if amenity.is_complimentary:
				row.rate = 0
				row.amount = 0
			else:
				row.rate = flt(getattr(amenity, rate_field, 0))
				qty = flt(row.quantity) or 1
				if self.booking_type == "Hourly":
					row.amount = flt(row.rate * qty * flt(self.duration_hours), 2)
				else:
					row.amount = flt(row.rate * qty, 2)
			self.amenity_total += flt(row.amount)

	def check_availability(self):
		"""Ensure space is available for the time range."""
		if not self.space or not self.start_datetime or not self.end_datetime:
			return

		conflicting = frappe.db.exists(
			"Space Booking",
			{
				"space": self.space,
				"name": ["!=", self.name],
				"docstatus": 1,
				"status": ["not in", ["Cancelled", "No Show", "Checked Out"]],
				"start_datetime": ["<", self.end_datetime],
				"end_datetime": [">", self.start_datetime],
			},
		)

		if conflicting:
			frappe.throw(
				_("Space {0} is already booked for this time period (Booking: {1})").format(
					self.space, conflicting
				)
			)

	def _generate_qr_code(self):
		"""Auto-generate QR on submit."""
		try:
			from arkspace.arkspace_spaces.qr_checkin import generate_booking_qr
			generate_booking_qr(self.name)
		except Exception:
			frappe.log_error(
				title=_("QR Generation Error"),
				message=_("Failed to generate QR for booking {0}").format(self.name),
			)
