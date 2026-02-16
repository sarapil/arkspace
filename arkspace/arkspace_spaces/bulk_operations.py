"""ARKSpace Bulk Operations — العمليات المجمعة

Provides server-side bulk action endpoints for Space Bookings.
"""

import frappe
from frappe import _
from frappe.utils import now_datetime


@frappe.whitelist()
def bulk_check_in(bookings):
	"""Bulk check-in multiple confirmed bookings.

	Args:
		bookings: JSON list of booking names or comma-separated string
	"""
	bookings = _parse_list(bookings)
	results = {"success": [], "failed": []}

	for booking_name in bookings:
		try:
			doc = frappe.get_doc("Space Booking", booking_name)
			if doc.docstatus != 1:
				raise frappe.ValidationError(_("Booking {0} is not submitted").format(booking_name))
			if doc.status != "Confirmed":
				raise frappe.ValidationError(
					_("Booking {0} status is {1}, expected Confirmed").format(booking_name, doc.status)
				)

			now = now_datetime()
			doc.db_set("status", "Checked In", update_modified=False)
			doc.db_set("checked_in_at", now, update_modified=False)

			frappe.db.set_value("Co-working Space", doc.space, {
				"status": "Occupied",
				"current_member": doc.member,
			})

			results["success"].append(booking_name)
		except Exception as e:
			results["failed"].append({"booking": booking_name, "error": str(e)})

	frappe.db.commit()

	frappe.publish_realtime("bulk_operation_complete", {
		"action": "check_in",
		"results": results,
	})

	return results


@frappe.whitelist()
def bulk_check_out(bookings):
	"""Bulk check-out multiple checked-in bookings.

	Args:
		bookings: JSON list of booking names or comma-separated string
	"""
	bookings = _parse_list(bookings)
	results = {"success": [], "failed": []}

	for booking_name in bookings:
		try:
			doc = frappe.get_doc("Space Booking", booking_name)
			if doc.docstatus != 1:
				raise frappe.ValidationError(_("Booking {0} is not submitted").format(booking_name))
			if doc.status != "Checked In":
				raise frappe.ValidationError(
					_("Booking {0} status is {1}, expected Checked In").format(booking_name, doc.status)
				)

			now = now_datetime()
			doc.db_set("status", "Checked Out", update_modified=False)
			doc.db_set("checked_out_at", now, update_modified=False)

			frappe.db.set_value("Co-working Space", doc.space, {
				"status": "Available",
				"current_member": None,
			})

			results["success"].append(booking_name)
		except Exception as e:
			results["failed"].append({"booking": booking_name, "error": str(e)})

	frappe.db.commit()

	frappe.publish_realtime("bulk_operation_complete", {
		"action": "check_out",
		"results": results,
	})

	return results


@frappe.whitelist()
def bulk_cancel(bookings):
	"""Bulk cancel multiple submitted bookings.

	Args:
		bookings: JSON list of booking names or comma-separated string
	"""
	bookings = _parse_list(bookings)
	results = {"success": [], "failed": []}

	for booking_name in bookings:
		try:
			doc = frappe.get_doc("Space Booking", booking_name)
			if doc.docstatus != 1:
				raise frappe.ValidationError(_("Booking {0} is not submitted").format(booking_name))
			if doc.status in ("Cancelled", "Checked Out"):
				raise frappe.ValidationError(
					_("Booking {0} is already {1}").format(booking_name, doc.status)
				)

			doc.cancel()
			results["success"].append(booking_name)
		except Exception as e:
			results["failed"].append({"booking": booking_name, "error": str(e)})

	frappe.db.commit()

	frappe.publish_realtime("bulk_operation_complete", {
		"action": "cancel",
		"results": results,
	})

	return results


@frappe.whitelist()
def bulk_mark_no_show(bookings):
	"""Bulk mark multiple confirmed bookings as No Show.

	Args:
		bookings: JSON list of booking names or comma-separated string
	"""
	bookings = _parse_list(bookings)
	results = {"success": [], "failed": []}

	for booking_name in bookings:
		try:
			doc = frappe.get_doc("Space Booking", booking_name)
			if doc.docstatus != 1:
				raise frappe.ValidationError(_("Booking {0} is not submitted").format(booking_name))
			if doc.status != "Confirmed":
				raise frappe.ValidationError(
					_("Booking {0} status is {1}, expected Confirmed").format(booking_name, doc.status)
				)

			doc.db_set("status", "No Show", update_modified=False)
			results["success"].append(booking_name)
		except Exception as e:
			results["failed"].append({"booking": booking_name, "error": str(e)})

	frappe.db.commit()

	frappe.publish_realtime("bulk_operation_complete", {
		"action": "no_show",
		"results": results,
	})

	return results


def _parse_list(value):
	"""Parse a JSON list or comma-separated string into a Python list."""
	if isinstance(value, str):
		import json
		try:
			value = json.loads(value)
		except (json.JSONDecodeError, ValueError):
			value = [v.strip() for v in value.split(",") if v.strip()]
	return value or []
