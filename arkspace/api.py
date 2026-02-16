# Copyright (c) 2026, ARKSpace Team and contributors
# For license information, please see license.txt

"""ARKSpace — Top-level API Hub
واجهة برمجة التطبيقات الرئيسية

Re-exports key endpoints so they are accessible at:
    /api/method/arkspace.api.<function_name>
"""

import frappe
from frappe import _

# ──────────────────────── Spaces ────────────────────────
from arkspace.arkspace_spaces.api import (  # noqa: F401
	check_in,
	check_out,
	create_booking,
	get_available_spaces,
)

# ──────────────────────── Memberships ───────────────────
from arkspace.arkspace_memberships.api import (  # noqa: F401
	create_membership,
	get_active_memberships,
	get_member_dashboard,
	get_membership_plans,
	get_wallet_balance,
)

# ──────────────────────── Integrations ─────────────────
from arkspace.arkspace_integrations.api import (  # noqa: F401
	get_integration_status,
	get_unpaid_invoices,
)

# ──────────────────────── Training ─────────────────────
from arkspace.arkspace_training.api import (  # noqa: F401
	enroll_user,
	get_available_badges,
	get_training_catalog,
	get_upcoming_sessions,
	get_user_badges,
	get_user_progress,
	update_progress,
)


# ──────────────────────── Health ────────────────────────
@frappe.whitelist(allow_guest=True)
def ping():
	"""Simple health-check endpoint."""
	return {"app": "arkspace", "version": "5.0.0", "status": "ok"}


@frappe.whitelist()
def get_dashboard_stats():
	"""Return high-level KPIs for the ARKSpace dashboard.

	Returns:
		dict with total_spaces, occupied, available, bookings_today, active_members
	"""
	from frappe.utils import getdate, nowdate

	today = getdate(nowdate())

	total_spaces = frappe.db.count("Co-working Space")
	occupied = frappe.db.count("Co-working Space", {"status": "Occupied"})
	available = frappe.db.count("Co-working Space", {"status": "Available"})

	bookings_today = frappe.db.sql(
		"""
		SELECT COUNT(*) FROM `tabSpace Booking`
		WHERE docstatus = 1
		AND start_datetime >= %s
		AND start_datetime < %s
		AND status NOT IN ('Cancelled', 'No Show')
		""",
		(today, frappe.utils.add_days(today, 1)),
	)[0][0] or 0

	active_members = frappe.db.count(
		"Space Booking",
		{
			"docstatus": 1,
			"status": "Checked In",
		},
	)

	return {
		"total_spaces": total_spaces,
		"occupied": occupied,
		"available": available,
		"bookings_today": bookings_today,
		"active_members": active_members,
	}
