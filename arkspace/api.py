# Copyright (c) 2026, ARKSpace Team and contributors
# For license information, please see license.txt

"""ARKSpace — Top-level API Hub
واجهة برمجة التطبيقات الرئيسية

Re-exports key endpoints so they are accessible at:
    /api/method/arkspace.api.<function_name>
"""

import frappe  # noqa: I001

# ──────────────────────── Integrations ─────────────────
from arkspace.arkspace_integrations.api import (  # noqa: F401
	get_integration_status,
	get_unpaid_invoices,
)

# ──────────────────────── Memberships ───────────────────
from arkspace.arkspace_memberships.api import (  # noqa: F401
	create_membership,
	get_active_memberships,
	get_member_dashboard,
	get_membership_plans,
	get_payment_history,
	get_renewal_options,
	get_wallet_balance,
	register_member,
	renew_membership,
	toggle_auto_renew,
	upgrade_membership,
)

# ──────────────────────── Spaces ────────────────────────
from arkspace.arkspace_spaces.api import (  # noqa: F401
	check_in,
	check_out,
	create_booking,
	get_available_spaces,
)

# ──────────────────────── Day Pass ──────────────────────
from arkspace.arkspace_spaces.day_pass_api import (  # noqa: F401
	convert_day_pass_to_membership,
	create_day_pass,
	day_pass_check_in,
	day_pass_check_out,
	get_available_trial_plans,
	get_day_pass,
	get_day_pass_stats,
	get_todays_day_passes,
)

# ──────────────────────── Visitors ─────────────────────
from arkspace.arkspace_spaces.visitor_management import (  # noqa: F401
	approve_visitor,
	get_active_visitors,
	get_todays_visitors,
	get_visitor_badge_html,
	get_visitor_stats,
	preregister_visitor,
	reject_visitor,
	visitor_check_in,
	visitor_check_out,
	walk_in_visitor,
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

# ──────────────────────── Analytics ────────────────────
from arkspace.arkspace_core.analytics_engine import (  # noqa: F401
	get_booking_patterns,
	get_comparison_report,
	get_dashboard_kpis,
	get_member_analytics,
	get_occupancy_heatmap,
	get_revenue_forecast,
	get_revenue_trends,
	get_space_utilization,
)

# ──────────────────────── Multi-Location ───────────────
from arkspace.arkspace_core.multi_location import (  # noqa: F401
	cross_location_search,
	get_branch_comparison,
	get_branch_details,
	get_branch_spaces,
	get_branch_stats,
	get_branches,
	transfer_membership,
)

# ──────────────────────── Community ────────────────────
from arkspace.arkspace_community.community import (  # noqa: F401
	cancel_event_registration,
	create_post,
	get_community_feed,
	get_event_attendees,
	get_events,
	get_member_directory,
	get_member_profile,
	get_my_connections,
	get_pending_requests,
	like_post,
	register_for_event,
	respond_to_request,
	send_networking_request,
)

# ──────────────────────── Visual ───────────────────────
from arkspace.arkspace_core.visual_api import (  # noqa: F401
	get_booking_flow,
	get_command_center_graph,
	get_command_center_kpis,
	get_community_graph,
	get_crm_pipeline,
	get_entity_detail,
	get_onboarding_data,
	get_space_explorer,
)


# ──────────────────────── Health ────────────────────────
@frappe.whitelist(allow_guest=True)
def ping():
	"""Simple health-check endpoint."""
	return {"app": "arkspace", "version": "6.0.0", "status": "ok"}


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
