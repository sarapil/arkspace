# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

"""ARK Live — Interactive 2D Floor Plan API
"""

import frappe
from frappe import _
from datetime import datetime, timedelta


@frappe.whitelist()
def get_live_plan_data(branch=None):
    """Return all spaces with their live booking/membership status for the interactive floor plan.

    Returns:
        dict with spaces list, each containing status, current occupant, dates, etc.
    """
    frappe.only_for(["ARKSpace User", "ARKSpace Manager", "System Manager"])

    filters = {}
    if branch:
        filters["branch"] = branch

    spaces = frappe.get_all(
        "Co-working Space",
        filters=filters,
        fields=[
            "name", "space_name", "space_name_ar", "space_type", "branch",
            "floor", "capacity", "area_sqm", "status",
            "hourly_rate", "daily_rate", "monthly_rate",
        ],
        order_by="branch asc, floor asc, space_name asc",
    )

    now = frappe.utils.now_datetime()

    for space in spaces:
        space["occupancy"] = _get_space_occupancy(space.name, now)
        space["upcoming_bookings"] = _get_upcoming_bookings(space.name, now)

    # Get branches for filter
    branches = frappe.get_all("Branch", pluck="name", order_by="name asc")

    # Summary stats
    total = len(spaces)
    available = sum(1 for s in spaces if s.status == "Available" and not s["occupancy"])
    occupied = sum(1 for s in spaces if s["occupancy"])
    maintenance = sum(1 for s in spaces if s.status == "Maintenance")

    return {
        "spaces": spaces,
        "branches": branches,
        "summary": {
            "total": total,
            "available": available,
            "occupied": occupied,
            "maintenance": maintenance,
        },
    }


def _get_space_occupancy(space_name, now):
    """Check if the space is currently occupied by an active booking or membership."""
    # Check active bookings (Checked In)
    booking = frappe.db.get_value(
        "Space Booking",
        {
            "space": space_name,
            "docstatus": 1,
            "status": "Checked In",
        },
        ["name", "member", "start_datetime", "end_datetime", "booking_type"],
        as_dict=True,
    )
    if booking:
        member_name = frappe.db.get_value("Customer", booking.member, "customer_name")
        return {
            "type": "booking",
            "booking": booking.name,
            "member": booking.member,
            "member_name": member_name,
            "start": str(booking.start_datetime),
            "end": str(booking.end_datetime),
            "booking_type": booking.booking_type,
        }

    # Check confirmed bookings that overlap with now
    confirmed = frappe.db.get_value(
        "Space Booking",
        {
            "space": space_name,
            "docstatus": 1,
            "status": "Confirmed",
            "start_datetime": ["<=", now],
            "end_datetime": [">=", now],
        },
        ["name", "member", "start_datetime", "end_datetime", "booking_type"],
        as_dict=True,
    )
    if confirmed:
        member_name = frappe.db.get_value("Customer", confirmed.member, "customer_name")
        return {
            "type": "confirmed",
            "booking": confirmed.name,
            "member": confirmed.member,
            "member_name": member_name,
            "start": str(confirmed.start_datetime),
            "end": str(confirmed.end_datetime),
            "booking_type": confirmed.booking_type,
        }

    # Check active membership assignment
    membership = frappe.db.get_value(
        "Membership",
        {
            "assigned_space": space_name,
            "docstatus": 1,
            "status": "Active",
        },
        ["name", "member", "start_date", "end_date", "membership_plan"],
        as_dict=True,
    )
    if membership:
        member_name = frappe.db.get_value("Customer", membership.member, "customer_name")
        plan_name = frappe.db.get_value("Membership Plan", membership.membership_plan, "plan_name") if membership.membership_plan else ""
        return {
            "type": "membership",
            "membership": membership.name,
            "member": membership.member,
            "member_name": member_name,
            "start": str(membership.start_date),
            "end": str(membership.end_date),
            "plan": plan_name,
        }

    return None


def _get_upcoming_bookings(space_name, now, limit=3):
    """Get upcoming bookings for a space."""
    bookings = frappe.get_all(
        "Space Booking",
        filters={
            "space": space_name,
            "docstatus": 1,
            "status": ["in", ["Confirmed", "Pending"]],
            "start_datetime": [">", now],
        },
        fields=["name", "member", "start_datetime", "end_datetime", "status", "booking_type"],
        order_by="start_datetime asc",
        limit=limit,
    )
    for b in bookings:
        b["member_name"] = frappe.db.get_value("Customer", b.member, "customer_name")
    return bookings


@frappe.whitelist()
def quick_book_space(space, member, booking_type, start_datetime, end_datetime, notes=None):
    """Create a quick booking from the ARK Live floor plan.

    Args:
        space: Co-working Space name
        member: Customer name
        booking_type: Hourly/Daily/Monthly
        start_datetime: Start datetime string
        end_datetime: End datetime string
        notes: Optional notes

    Returns:
        dict with booking name and details
    """
    frappe.has_permission("AS Booking", "create", throw=True)
    frappe.only_for(["ARKSpace User", "ARKSpace Manager", "System Manager"])

    space_doc = frappe.get_doc("Co-working Space", space)

    # Get rate based on booking type
    rate_map = {
        "Hourly": space_doc.hourly_rate,
        "Daily": space_doc.daily_rate,
        "Monthly": space_doc.monthly_rate,
    }
    rate = rate_map.get(booking_type, 0) or 0

    # Calculate total
    start_dt = frappe.utils.get_datetime(start_datetime)
    end_dt = frappe.utils.get_datetime(end_datetime)
    duration_hours = (end_dt - start_dt).total_seconds() / 3600

    if booking_type == "Hourly":
        total = rate * max(1, round(duration_hours))
    elif booking_type == "Daily":
        days = max(1, round(duration_hours / 24))
        total = rate * days
    else:
        total = rate

    booking = frappe.get_doc({
        "doctype": "Space Booking",
        "space": space,
        "member": member,
        "booking_type": booking_type,
        "start_datetime": start_dt,
        "end_datetime": end_dt,
        "rate": rate,
        "total_amount": total,
        "net_amount": total,
        "status": "Confirmed",
        "notes": notes,
    })
    booking.insert()
    booking.submit()

    return {
        "booking": booking.name,
        "space_name": space_doc.space_name,
        "member_name": frappe.db.get_value("Customer", member, "customer_name"),
        "total": total,
    }
