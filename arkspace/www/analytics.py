# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

# Portal page context for analytics dashboard

import frappe
from frappe.utils import add_days, nowdate


def get_context(context):
    context.no_cache = 1
    context.title = "Analytics — التحليلات"

    if frappe.session.user == "Guest":
        frappe.throw("Please log in to view analytics", frappe.PermissionError)

    # Check if user has analytics access
    roles = frappe.get_roles(frappe.session.user)
    if not any(r in roles for r in ["System Manager", "ARKSpace Admin", "ARKSpace Manager"]):
        frappe.throw("Insufficient permissions to view analytics", frappe.PermissionError)

    # Load recent snapshots for server-side rendering
    context.recent_snapshots = frappe.get_all(
        "Analytics Snapshot",
        filters={"period_type": "Daily", "branch": ""},
        fields=["snapshot_date", "occupancy_rate", "total_bookings",
                "active_members", "total_revenue"],
        order_by="snapshot_date desc",
        limit=30,
    )

    context.branches = frappe.get_all("Branch", pluck="name")
    context.from_date = add_days(nowdate(), -30)
    context.to_date = nowdate()
