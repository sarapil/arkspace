# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

"""Pricing Rule

Defines a dynamic pricing adjustment that can be applied to bookings.
"""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate


class PricingRule(Document):
	"""Controller for the Pricing Rule DocType."""

	def validate(self):
		self._validate_adjustment()
		self._validate_conditions()

	def _validate_adjustment(self):
		if self.adjustment_type == "Multiplier" and flt(self.adjustment_value) <= 0:
			frappe.throw(_("Multiplier must be greater than zero"))
		if self.adjustment_type == "Override Rate" and flt(self.adjustment_value) < 0:
			frappe.throw(_("Override rate cannot be negative"))

	def _validate_conditions(self):
		if self.condition_type == "Time Range":
			if not self.time_start or not self.time_end:
				frappe.throw(
					_("Time Range condition requires both start and end times")
				)
		elif self.condition_type == "Date Range":
			if not self.date_start or not self.date_end:
				frappe.throw(
					_("Date Range condition requires both start and end dates")
				)
			if getdate(self.date_start) > getdate(self.date_end):
				frappe.throw(_("Date start must be before date end"))
		elif self.condition_type == "Day of Week":
			if not self.day_of_week:
				frappe.throw(
					_("Day of Week condition requires a day selection")
				)

	def is_currently_valid(self):
		"""Check if this rule is currently within its validity window."""
		now = frappe.utils.now_datetime()
		if self.valid_from and now < self.valid_from:
			return False
		if self.valid_to and now > self.valid_to:
			return False
		return True
