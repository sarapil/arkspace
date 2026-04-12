# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

"""ARKSpace Spaces — Public API
"""

import frappe
from frappe import _
from frappe.utils import now_datetime


@frappe.whitelist()
def get_available_spaces(space_type=None, branch=None, booking_type=None, start=None, end=None):
    frappe.only_for(["AS User", "AS Manager", "System Manager"])
def get_available_spaces(space_type=None, branch=None, booking_type=None, start=None, end=None):
	"""Return spaces that are available for the given time range.

	Args:
		space_type: Filter by Space Type name
		branch: Filter by Branch name
		booking_type: Hourly / Daily / Monthly
		start: ISO datetime string — period start
		end: ISO datetime string — period end

	Returns:
		list of dicts with space details and availability
	"""
	frappe.has_permission("AS Space", "read", throw=True)
	frappe.only_for(["ARKSpace User", "ARKSpace Manager", "System Manager"])

	filters = {"status": ["in", ["Available", "Reserved"]]}

	if space_type:
		filters["space_type"] = space_type
	if branch:
		filters["branch"] = branch

	spaces = frappe.get_all(
		"Co-working Space",
		filters=filters,
		fields=[
			"name",
			"space_name",
			"space_type",
			"branch",
			"capacity",
			"hourly_rate",
			"daily_rate",
			"monthly_rate",
			"status",
			"main_image",
		],
		order_by="space_name asc",
	)

	# If time range given, exclude spaces with conflicting bookings
	if start and end:
		booked_spaces = frappe.get_all(
			"Space Booking",
			filters={
				"docstatus": 1,
				"status": ["not in", ["Cancelled", "No Show", "Checked Out"]],
				"start_datetime": ["<", end],
				"end_datetime": [">", start],
			},
			pluck="space",
		)
		spaces = [s for s in spaces if s.name not in booked_spaces]

	# Add relevant rate based on booking_type
	if booking_type:
		rate_field = {
			"Hourly": "hourly_rate",
			"Daily": "daily_rate",
			"Monthly": "monthly_rate",
		}.get(booking_type)
		for s in spaces:
			s["applicable_rate"] = s.get(rate_field, 0)

	return spaces


@frappe.whitelist()
def create_booking(space, member, booking_type, start_datetime, end_datetime, discount_percent=0):
    frappe.only_for(["AS User", "AS Manager", "System Manager"])
def create_booking(space, member, booking_type, start_datetime, end_datetime, discount_percent=0):
	"""Create and optionally submit a new Space Booking.

	Args:
		space: Co-working Space name
		member: Customer name
		booking_type: Hourly / Daily / Monthly
		start_datetime: ISO datetime
		end_datetime: ISO datetime
		discount_percent: optional discount

	Returns:
		dict with booking name and status
	"""
	frappe.has_permission("AS Booking", "create", throw=True)
	frappe.only_for(["ARKSpace Manager", "System Manager"])

	space_doc = frappe.get_doc("Co-working Space", space)

	rate_map = {
		"Hourly": space_doc.hourly_rate,
		"Daily": space_doc.daily_rate,
		"Monthly": space_doc.monthly_rate,
	}
	rate = rate_map.get(booking_type, 0)
	if not rate:
		frappe.throw(_("No {0} rate configured for space {1}").format(booking_type, space))

	booking = frappe.get_doc({
		"doctype": "Space Booking",
		"space": space,
		"member": member,
		"booking_type": booking_type,
		"start_datetime": start_datetime,
		"end_datetime": end_datetime,
		"rate": rate,
		"discount_percent": discount_percent,
	})
	booking.insert()
	booking.submit()

	return {"booking": booking.name, "status": booking.status, "net_amount": booking.net_amount}


@frappe.whitelist()
def check_in(booking):
	"""Mark a confirmed booking as Checked In and occupy the space.

	Args:
		booking: Space Booking name

	Returns:
		dict with updated status
	"""
	frappe.only_for(["ARKSpace User", "ARKSpace Manager", "System Manager"])

	doc = frappe.get_doc("Space Booking", booking)
	if doc.docstatus != 1:
		frappe.throw(_("Booking must be submitted before check-in"))
	if doc.status != "Confirmed":
		frappe.throw(_("Only Confirmed bookings can be checked in. Current status: {0}").format(doc.status))

	now = now_datetime()
	doc.db_set("status", "Checked In", update_modified=False)
	doc.db_set("checked_in_at", now, update_modified=False)

	# Occupy the space
	frappe.db.set_value("Co-working Space", doc.space, {
		"status": "Occupied",
		"current_member": doc.member,
	})

	frappe.publish_realtime("space_status_changed", {
		"space": doc.space,
		"status": "Occupied",
		"booking": booking,
	})

	return {"booking": booking, "status": "Checked In", "checked_in_at": str(now)}


@frappe.whitelist()
def check_out(booking):
	"""Mark a Checked In booking as Checked Out and free the space.

	Args:
		booking: Space Booking name

	Returns:
		dict with updated status
	"""
	frappe.only_for(["ARKSpace User", "ARKSpace Manager", "System Manager"])

	doc = frappe.get_doc("Space Booking", booking)
	if doc.docstatus != 1:
		frappe.throw(_("Booking must be submitted"))
	if doc.status != "Checked In":
		frappe.throw(_("Only Checked In bookings can be checked out. Current status: {0}").format(doc.status))

	now = now_datetime()
	doc.db_set("status", "Checked Out", update_modified=False)
	doc.db_set("checked_out_at", now, update_modified=False)

	# Free the space
	frappe.db.set_value("Co-working Space", doc.space, {
		"status": "Available",
		"current_member": None,
	})

	frappe.publish_realtime("space_status_changed", {
		"space": doc.space,
		"status": "Available",
		"booking": booking,
	})

	return {"booking": booking, "status": "Checked Out", "checked_out_at": str(now)}
