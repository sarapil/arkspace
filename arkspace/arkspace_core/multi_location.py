# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

"""ARKSpace — Multi-Location / Branch Management API

Provides cross-location search, branch statistics, membership transfer,
and branch comparison for multi-site workspace management.
"""

import frappe
from frappe import _
from frappe.utils import cint, flt, get_first_day, getdate, nowdate


@frappe.whitelist(allow_guest=True)
def get_branches(active_only=True):
    """Get all ARKSpace branches with summary info.

    Args:
        active_only: If True, only return active branches.

    Returns:
        list of branch dicts with space counts and occupancy
    """
    filters = {}
    if cint(active_only):
        filters["is_active"] = 1

    branches = frappe.get_all(
        "ARKSpace Branch",
        filters=filters,
        fields=[
            "name", "branch_name", "branch_name_ar", "branch_code",
            "city", "country", "is_active", "image",
            "operating_hours_start", "operating_hours_end",
            "max_capacity", "current_occupancy",
            "latitude", "longitude", "phone", "email",
        ],
        order_by="branch_name asc",
    )

    for b in branches:
        branch_link = b.get("name")
        # Count spaces by status
        b["total_spaces"] = frappe.db.count(
            "Co-working Space", {"branch": branch_link},
        ) or 0
        b["available_spaces"] = frappe.db.count(
            "Co-working Space", {"branch": branch_link, "status": "Available"},
        ) or 0
        b["occupancy_rate"] = round(
            ((b["total_spaces"] - b["available_spaces"]) / b["total_spaces"] * 100)
            if b["total_spaces"] else 0, 1,
        )

    return branches


@frappe.whitelist()
def get_branch_details(branch):
    """Get full branch details including spaces breakdown and stats."""
    frappe.only_for(["System Manager", "ARK Admin", "ARK User"])
    doc = frappe.get_doc("ARKSpace Branch", branch)
    doc.check_permission("read")

    branch_link = doc.branch or doc.branch_name

    # Space breakdown by type
    space_types = frappe.db.sql("""
        SELECT space_type, COUNT(*) AS count,
               SUM(CASE WHEN status = 'Available' THEN 1 ELSE 0 END) AS available
        FROM `tabCo-working Space`
        WHERE branch = %s
        GROUP BY space_type
    """, (branch_link,), as_dict=True)

    # Today's bookings
    today = getdate(nowdate())
    todays_bookings = frappe.db.count("Space Booking", {
        "docstatus": 1,
        "space": ["in", frappe.get_all(
            "Co-working Space", {"branch": branch_link}, pluck="name",
        ) or ["__none__"]],
        "start_datetime": [">=", f"{today} 00:00:00"],
        "end_datetime": ["<=", f"{today} 23:59:59"],
    }) or 0

    # Active memberships
    active_members = frappe.db.count("Membership", {
        "docstatus": 1, "status": "Active", "branch": branch_link,
    }) or 0

    return {
        "branch": doc.as_dict(),
        "space_types": space_types,
        "todays_bookings": todays_bookings,
        "active_members": active_members,
    }


@frappe.whitelist(allow_guest=True)
def get_branch_spaces(branch, space_type=None, status=None):
    """Get all spaces in a branch, optionally filtered by type/status."""
    branch_doc = frappe.get_doc("ARKSpace Branch", branch)
    branch_link = branch_doc.branch or branch_doc.branch_name

    filters = {"branch": branch_link}
    if space_type:
        filters["space_type"] = space_type
    if status:
        filters["status"] = status

    spaces = frappe.get_all(
        "Co-working Space",
        filters=filters,
        fields=[
            "name", "space_name", "space_type", "status",
            "capacity", "hourly_rate", "daily_rate", "floor",
            "amenities_description", "image",
        ],
        order_by="space_name asc",
    )
    return spaces


@frappe.whitelist()
def get_branch_stats(branch, from_date=None, to_date=None):
    """Get comprehensive statistics for a branch."""
    frappe.only_for(["ARKSpace User", "ARKSpace Manager", "System Manager"])

    from_date = getdate(from_date or get_first_day(nowdate()))
    to_date = getdate(to_date or nowdate())

    branch_doc = frappe.get_doc("ARKSpace Branch", branch)
    branch_link = branch_doc.branch or branch_doc.branch_name

    space_names = frappe.get_all(
        "Co-working Space", {"branch": branch_link}, pluck="name",
    ) or ["__none__"]

    # Bookings in period
    bookings = frappe.db.sql("""
        SELECT COUNT(*) AS total,
               SUM(CASE WHEN status IN ('Checked In','Checked Out') THEN 1 ELSE 0 END) AS attended,
               SUM(CASE WHEN status = 'No Show' THEN 1 ELSE 0 END) AS no_shows,
               SUM(total_amount) AS revenue
        FROM `tabSpace Booking`
        WHERE docstatus = 1
          AND space IN ({placeholders})
          AND DATE(start_datetime) BETWEEN %s AND %s
    """.format(placeholders=",".join(["%s"] * len(space_names))),
        space_names + [from_date, to_date],
        as_dict=True,
    )[0]

    # Active memberships
    active_members = frappe.db.count("Membership", {
        "docstatus": 1, "status": "Active", "branch": branch_link,
    }) or 0

    # Day passes in period
    day_passes = frappe.db.count("Day Pass", {
        "docstatus": 1, "branch": branch_link,
        "pass_date": ["between", [from_date, to_date]],
    }) or 0

    # Visitors in period
    visitors = frappe.db.count("Visitor Log", {
        "branch": branch_link,
        "visit_date": ["between", [from_date, to_date]],
    }) or 0

    return {
        "branch": branch,
        "period": {"from": str(from_date), "to": str(to_date)},
        "total_spaces": len(space_names) if space_names != ["__none__"] else 0,
        "bookings": {
            "total": cint(bookings.total),
            "attended": cint(bookings.attended),
            "no_shows": cint(bookings.no_shows),
            "revenue": flt(bookings.revenue, 2),
        },
        "active_members": active_members,
        "day_passes": day_passes,
        "visitors": visitors,
    }


@frappe.whitelist(allow_guest=True)
def cross_location_search(
    space_type=None, date=None, start_time=None, end_time=None, city=None,
):
    """Search for available spaces across all branches.

    Returns available spaces grouped by branch for the given criteria.
    """
    date = getdate(date or nowdate())
    result = []

    branch_filters = {"is_active": 1}
    if city:
        branch_filters["city"] = city

    branches = frappe.get_all(
        "ARKSpace Branch",
        filters=branch_filters,
        fields=["name", "branch_name", "branch_name_ar", "city",
                "country", "image", "operating_hours_start", "operating_hours_end"],
    )

    for b in branches:
        branch_link = b.name  # ARKSpace Branch uses branch_name as name
        space_filters = {"branch": branch_link, "status": "Available"}
        if space_type:
            space_filters["space_type"] = space_type

        available = frappe.get_all(
            "Co-working Space",
            filters=space_filters,
            fields=["name", "space_name", "space_type", "capacity",
                     "hourly_rate", "daily_rate", "image"],
        )

        if start_time and end_time:
            # Filter out spaces that have conflicting bookings
            start_dt = f"{date} {start_time}"
            end_dt = f"{date} {end_time}"
            booked_spaces = frappe.db.sql_list("""
                SELECT DISTINCT space FROM `tabSpace Booking`
                WHERE docstatus = 1
                  AND status NOT IN ('Cancelled', 'No Show', 'Checked Out')
                  AND start_datetime < %s AND end_datetime > %s
            """, (end_dt, start_dt))

            available = [s for s in available if s.name not in booked_spaces]

        if available:
            result.append({
                "branch": b,
                "available_spaces": available,
                "count": len(available),
            })

    result.sort(key=lambda x: x["count"], reverse=True)
    return result


@frappe.whitelist()
def transfer_membership(membership, target_branch):
    """Transfer a membership from one branch to another.

    Creates a note on the membership and updates the branch field.
    """
    frappe.has_permission("AS Membership", "write", throw=True)
    mem = frappe.get_doc("Membership", membership)
    mem.check_permission("write")

    if mem.status != "Active":
        frappe.throw(_("Only active memberships can be transferred"))

    old_branch = mem.branch or _("No Branch")

    # Verify target branch exists
    if not frappe.db.exists("ARKSpace Branch", target_branch):
        frappe.throw(_("Target branch {0} not found").format(target_branch))

    target_doc = frappe.get_doc("ARKSpace Branch", target_branch)
    target_link = target_doc.branch or target_doc.branch_name

    mem.branch = target_link
    mem.add_comment("Info", _(
        "Membership transferred from {0} to {1}"
    ).format(old_branch, target_link))
    mem.save(ignore_permissions=True)

    frappe.publish_realtime("membership_transferred", {
        "membership": membership,
        "from_branch": old_branch,
        "to_branch": target_link,
        "member": mem.member,
    })

    return {
        "status": "success",
        "message": _("Membership transferred to {0}").format(target_link),
        "membership": membership,
    }


@frappe.whitelist()
def get_branch_comparison(branches=None, from_date=None, to_date=None):
    """Compare metrics across multiple branches side-by-side.

    Args:
        branches: JSON list of branch names, or None for all
    """
    frappe.only_for(["ARKSpace User", "ARKSpace Manager", "System Manager"])

    import json

    from_date = getdate(from_date or get_first_day(nowdate()))
    to_date = getdate(to_date or nowdate())

    if branches and isinstance(branches, str):
        branches = json.loads(branches)

    if not branches:
        branches = frappe.get_all("ARKSpace Branch", {"is_active": 1}, pluck="name")

    comparison = []
    for branch_name in branches:
        try:
            stats = get_branch_stats(branch_name, str(from_date), str(to_date))
            branch_doc = frappe.get_doc("ARKSpace Branch", branch_name)
            comparison.append({
                "branch": branch_name,
                "branch_name_ar": branch_doc.branch_name_ar,
                "city": branch_doc.city,
                **stats,
            })
        except Exception:
            frappe.log_error(f"Branch comparison error for {branch_name}")

    return {
        "branches": comparison,
        "period": {"from": str(from_date), "to": str(to_date)},
    }
