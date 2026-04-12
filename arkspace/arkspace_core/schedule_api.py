# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

"""
ARKSpace Schedule API
=================================================

Provides backend endpoints for the ark-scheduler resource-timeline page.
Each endpoint returns data for the Kanban-Timeline grid:
  - Columns = individual spaces of a given type
  - Rows    = hourly time slots across a date
  - Cards   = bookings / day passes placed on the grid

Operations:
  - get_schedule_data   : full grid for a date + space type
  - move_booking        : reassign a booking to a different space/time
  - extend_booking      : extend or shrink a booking's end time
  - swap_bookings       : swap two bookings between their spaces
  - quick_book          : create an instant booking from the grid
  - split_booking       : split one booking across two spaces
  - block_slot          : mark a slot as maintenance/reserved
  - check_conflicts     : verify if a slot is available
  - get_space_types     : list all space types with counts
"""

import frappe
from frappe import _
from frappe.utils import (
    getdate, nowdate, now_datetime, get_datetime,
    add_to_date, time_diff_in_hours, cint, flt,
    format_datetime, format_time,
)
from datetime import datetime, timedelta, time as dt_time


# ── Helper: status → CSS color token ──
_STATUS_COLORS = {
    "Pending":     "#f59e0b",
    "Confirmed":   "#3b82f6",
    "Checked In":  "#10b981",
    "Checked Out": "#6b7280",
    "Cancelled":   "#ef4444",
    "No Show":     "#9ca3af",
    # Day Pass statuses
    "Draft":       "#9ca3af",
    "Active":      "#3b82f6",
    "Expired":     "#ef4444",
    # Space statuses
    "Available":    "#10b981",
    "Occupied":     "#f59e0b",
    "Maintenance":  "#ef4444",
    "Reserved":     "#8b5cf6",
}


def _booking_card(b, card_type="booking"):
    """Format a booking/day-pass record as a timeline card dict."""
    start = get_datetime(b.get("start_datetime") or b.get("start_time") or b.get("start"))
    end = get_datetime(b.get("end_datetime") or b.get("end_time") or b.get("end"))

    return {
        "id": b.get("name"),
        "type": card_type,
        "space": b.get("space"),
        "space_name": b.get("space_name", ""),
        "member": b.get("member") or b.get("guest_name", ""),
        "member_name": b.get("member_name") or b.get("guest_name", ""),
        "start_hour": start.hour + start.minute / 60.0,
        "end_hour": end.hour + end.minute / 60.0 if end.date() == start.date() else 24.0,
        "start_time": str(start),
        "end_time": str(end),
        "status": b.get("status", ""),
        "booking_type": b.get("booking_type", ""),
        "color": _STATUS_COLORS.get(b.get("status", ""), "#6b7280"),
        "rate": flt(b.get("rate", 0)),
        "net_amount": flt(b.get("net_amount", 0)),
        "doctype": "Space Booking" if card_type == "booking" else "Day Pass",
        "docstatus": cint(b.get("docstatus", 0)),
    }


@frappe.whitelist()
def get_space_types():
    """Return all space types with their space counts and colors."""
    frappe.has_permission("Space Type", "read", throw=True)
    types = frappe.get_all(
        "Space Type",
        fields=["name", "type_name", "type_name_ar", "icon", "color",
                "hourly_booking", "daily_booking", "monthly_booking"],
        order_by="type_name asc",
    )

    for t in types:
        t["space_count"] = frappe.db.count(
            "Co-working Space",
            filters={"space_type": t["name"], "status": ["!=", ""]},
        )
        t["available_count"] = frappe.db.count(
            "Co-working Space",
            filters={"space_type": t["name"], "status": "Available"},
        )

    return types


@frappe.whitelist()
def get_schedule_data(space_type, date=None, branch=None, business_hours_only=0):
    """
    Return the full schedule grid for a given space type on a date.

    Returns:
        {
            "date": "2026-04-03",
            "space_type": { ... },
            "spaces": [ { name, space_name, status, capacity, floor, ... } ],
            "bookings": [ { card dict } ],
            "day_passes": [ { card dict } ],
            "blocked_slots": [ { space, start_hour, end_hour, reason } ],
            "hours": { "start": 0, "end": 24, "step": 1 },
        }
    """
    frappe.has_permission("AS Booking", "read", throw=True)
    frappe.has_permission("Co-working Space", "read", throw=True)
    date = getdate(date or nowdate())
    day_start = datetime.combine(date, dt_time(0, 0))
    day_end = datetime.combine(date, dt_time(23, 59, 59))

    # Business hours config
    bh = cint(business_hours_only)
    settings = None
    try:
        settings = frappe.get_cached_doc("ARKSpace Settings")
    except Exception:
        pass

    hour_start = 0
    hour_end = 24
    if bh and settings:
        hour_start = cint(getattr(settings, "business_hour_start", 0))
        hour_end = cint(getattr(settings, "business_hour_end", 24))

    # Space type info
    st = frappe.get_doc("Space Type", space_type)

    # All spaces of this type
    filters = {"space_type": space_type}
    if branch:
        filters["branch"] = branch

    spaces = frappe.get_all(
        "Co-working Space",
        filters=filters,
        fields=["name", "space_name", "space_name_ar", "status", "capacity",
                "floor", "space_number", "branch", "current_member",
                "hourly_rate", "daily_rate", "monthly_rate", "main_image"],
        order_by="floor asc, space_number asc, space_name asc",
    )

    space_names = [s.name for s in spaces]
    if not space_names:
        return {
            "date": str(date),
            "space_type": st.as_dict(),
            "spaces": [],
            "bookings": [],
            "day_passes": [],
            "blocked_slots": [],
            "hours": {"start": hour_start, "end": hour_end, "step": 1},
        }

    # Bookings for these spaces on this date
    bookings_raw = frappe.get_all(
        "Space Booking",
        filters=[
            ["space", "in", space_names],
            ["start_datetime", ">=", day_start],
            ["start_datetime", "<=", day_end],
            ["docstatus", "=", 1],
            ["status", "not in", ["Cancelled", "No Show"]],
        ],
        fields=["name", "space", "member", "member_name", "start_datetime", "end_datetime",
                "status", "booking_type", "rate", "net_amount", "total_amount",
                "discount_percent", "docstatus"],
        order_by="start_datetime asc",
    )

    # Also get bookings that SPAN into this date (started before, ends during/after)
    spanning = frappe.get_all(
        "Space Booking",
        filters={
            "space": ["in", space_names],
            "start_datetime": ["<", day_start],
            "end_datetime": [">", day_start],
            "docstatus": 1,
            "status": ["not in", ["Cancelled", "No Show"]],
        },
        fields=["name", "space", "member", "member_name", "start_datetime", "end_datetime",
                "status", "booking_type", "rate", "net_amount", "total_amount",
                "discount_percent", "docstatus"],
        order_by="start_datetime asc",
    )

    seen = {b.name for b in bookings_raw}
    for s in spanning:
        if s.name not in seen:
            bookings_raw.append(s)

    bookings = [_booking_card(b, "booking") for b in bookings_raw]

    # Day passes (those assigned to a space on this date)
    day_passes_raw = frappe.get_all(
        "Day Pass",
        filters={
            "space": ["in", space_names],
            "pass_date": date,
            "docstatus": 1,
            "status": ["not in", ["Cancelled", "Expired"]],
        },
        fields=["name", "space", "guest_name", "start_time", "end_time",
                "pass_date", "status", "pass_type", "rate", "net_amount", "docstatus"],
        order_by="start_time asc",
    )

    day_passes = []
    for dp in day_passes_raw:
        # Day Pass uses Time fields; convert to full datetime for grid
        dp_start = dp.start_time or dt_time(hour_start, 0)
        dp_end = dp.end_time or dt_time(hour_end, 0)
        if isinstance(dp_start, str):
            parts = dp_start.split(":")
            dp_start = dt_time(int(parts[0]), int(parts[1]) if len(parts) > 1 else 0)
        if isinstance(dp_end, str):
            parts = dp_end.split(":")
            dp_end = dt_time(int(parts[0]), int(parts[1]) if len(parts) > 1 else 0)

        dp["start"] = datetime.combine(date, dp_start)
        dp["end"] = datetime.combine(date, dp_end)
        dp["member_name"] = dp.get("guest_name", "")
        day_passes.append(_booking_card(dp, "day_pass"))

    return {
        "date": str(date),
        "space_type": st.as_dict(),
        "spaces": spaces,
        "bookings": bookings,
        "day_passes": day_passes,
        "blocked_slots": [],
        "hours": {"start": hour_start, "end": hour_end, "step": 1},
    }


@frappe.whitelist()
def check_conflicts(space, start_time, end_time, exclude_booking=None):
    """
    Check if a time slot has any conflicts.

    Returns:
        {
            "has_conflict": True/False,
            "conflicts": [ { name, member_name, start_time, end_time, status } ],
            "space_status": "Available"
        }
    """
    frappe.has_permission("Space Booking", "read", throw=True)
    start = get_datetime(start_time)
    end = get_datetime(end_time)

    filters = {
        "space": space,
        "docstatus": 1,
        "status": ["not in", ["Cancelled", "No Show", "Checked Out"]],
        "start_datetime": ["<", end],
        "end_datetime": [">", start],
    }

    if exclude_booking:
        filters["name"] = ["!=", exclude_booking]

    conflicts = frappe.get_all(
        "Space Booking",
        filters=filters,
        fields=["name", "member_name", "start_datetime", "end_datetime", "status"],
    )

    space_status = frappe.db.get_value("Co-working Space", space, "status") or "Available"

    return {
        "has_conflict": len(conflicts) > 0,
        "conflicts": conflicts,
        "space_status": space_status,
    }


@frappe.whitelist()
def move_booking(booking, new_space, new_start_time=None, new_end_time=None):
    """
    Move a booking to a different space and/or time slot.
    This is the core drag-and-drop handler.

    Args:
        booking: Space Booking name
        new_space: Target Co-working Space name
        new_start_time: New start datetime (optional, keeps original if None)
        new_end_time: New end datetime (optional, keeps original if None)

    Returns:
        { "success": True, "booking": updated_booking_card }
    """
    frappe.has_permission("AS Booking", "write", throw=True)
    frappe.only_for(["System Manager", "ARKSpace Admin", "ARKSpace Manager", "ARKSpace Front Desk"])

    doc = frappe.get_doc("Space Booking", booking)

    if doc.docstatus != 1:
        frappe.throw(_("Only submitted bookings can be moved."))

    if doc.status in ("Checked Out", "Cancelled", "No Show"):
        frappe.throw(_("Cannot move a {0} booking.").format(_(doc.status)))

    old_space = doc.space
    old_start = doc.start_datetime
    old_end = doc.end_datetime

    new_start = get_datetime(new_start_time) if new_start_time else doc.start_datetime
    new_end = get_datetime(new_end_time) if new_end_time else doc.end_datetime

    # Validate duration
    if new_end <= new_start:
        frappe.throw(_("End time must be after start time."))

    # Check conflicts at destination
    conflict = check_conflicts(new_space, str(new_start), str(new_end), exclude_booking=booking)
    if isinstance(conflict, str):
        import json
        conflict = json.loads(conflict)

    if conflict.get("has_conflict"):
        names = ", ".join([c["name"] for c in conflict["conflicts"]])
        frappe.throw(_("Conflict with existing bookings: {0}").format(names))

    # Check space status
    space_doc = frappe.get_doc("Co-working Space", new_space)
    if space_doc.status == "Maintenance":
        frappe.throw(_("Space {0} is under maintenance.").format(space_doc.space_name))

    # Apply changes via amend-like pattern (direct update for submitted docs)
    frappe.db.set_value("Space Booking", booking, {
        "space": new_space,
        "start_datetime": new_start,
        "end_datetime": new_end,
    }, update_modified=True)

    # Update duration
    duration = time_diff_in_hours(new_end, new_start)
    frappe.db.set_value("Space Booking", booking, "duration_hours", duration)

    # Update old space status if it was Occupied by this booking
    if old_space != new_space:
        _update_space_status(old_space)
        _update_space_status(new_space, doc.member)

    # Log the move
    doc.add_comment("Info", _(
        "Booking moved from {0} ({1} - {2}) to {3} ({4} - {5})"
    ).format(
        old_space,
        format_datetime(old_start, "HH:mm"),
        format_datetime(old_end, "HH:mm"),
        new_space,
        format_datetime(new_start, "HH:mm"),
        format_datetime(new_end, "HH:mm"),
    ))

    frappe.db.commit()

    # Return updated card
    updated = frappe.get_doc("Space Booking", booking)
    return {
        "success": True,
        "booking": _booking_card(updated.as_dict(), "booking"),
    }


@frappe.whitelist()
def extend_booking(booking, new_end_time):
    """
    Extend or shrink a booking's end time.
    Used when dragging the bottom edge of a card.
    """
    frappe.only_for(["System Manager", "ARKSpace Admin", "ARKSpace Manager", "ARKSpace Front Desk"])

    doc = frappe.get_doc("Space Booking", booking)

    if doc.docstatus != 1:
        frappe.throw(_("Only submitted bookings can be extended."))

    if doc.status in ("Checked Out", "Cancelled", "No Show"):
        frappe.throw(_("Cannot extend a {0} booking.").format(_(doc.status)))

    new_end = get_datetime(new_end_time)

    if new_end <= doc.start_datetime:
        frappe.throw(_("End time must be after start time."))

    # Check conflicts (only if extending, not shrinking)
    if new_end > doc.end_datetime:
        conflict = check_conflicts(doc.space, str(doc.end_datetime), str(new_end), exclude_booking=booking)
        if isinstance(conflict, str):
            import json
            conflict = json.loads(conflict)

        if conflict.get("has_conflict"):
            names = ", ".join([c["name"] for c in conflict["conflicts"]])
            frappe.throw(_("Cannot extend — conflict with: {0}").format(names))

    old_end = doc.end_datetime

    frappe.db.set_value("Space Booking", booking, "end_datetime", new_end)
    duration = time_diff_in_hours(new_end, doc.start_datetime)
    frappe.db.set_value("Space Booking", booking, "duration_hours", duration)

    doc.add_comment("Info", _(
        "Booking {0}: end time changed from {1} to {2}"
    ).format(
        "extended" if new_end > old_end else "shortened",
        format_datetime(old_end, "HH:mm"),
        format_datetime(new_end, "HH:mm"),
    ))

    frappe.db.commit()

    updated = frappe.get_doc("Space Booking", booking)
    return {
        "success": True,
        "booking": _booking_card(updated.as_dict(), "booking"),
    }


@frappe.whitelist()
def swap_bookings(booking_a, booking_b):
    """
    Swap two bookings between their respective spaces.
    Useful for resolving scheduling conflicts.
    """
    frappe.only_for(["System Manager", "ARKSpace Admin", "ARKSpace Manager", "ARKSpace Front Desk"])

    doc_a = frappe.get_doc("Space Booking", booking_a)
    doc_b = frappe.get_doc("Space Booking", booking_b)

    for doc, label in [(doc_a, "A"), (doc_b, "B")]:
        if doc.docstatus != 1:
            frappe.throw(_("Booking {0} is not submitted.").format(doc.name))
        if doc.status in ("Checked Out", "Cancelled", "No Show"):
            frappe.throw(_("Cannot swap a {0} booking ({1}).").format(_(doc.status), doc.name))

    space_a = doc_a.space
    space_b = doc_b.space

    if space_a == space_b:
        frappe.throw(_("Both bookings are in the same space. Nothing to swap."))

    # Check conflicts: A's time in B's space (excluding B)
    conflict = check_conflicts(space_b, str(doc_a.start_datetime), str(doc_a.end_datetime), exclude_booking=booking_b)
    if isinstance(conflict, str):
        import json
        conflict = json.loads(conflict)
    if conflict.get("has_conflict"):
        frappe.throw(_("Cannot swap — conflict for {0} in {1}").format(booking_a, space_b))

    # Check conflicts: B's time in A's space (excluding A)
    conflict = check_conflicts(space_a, str(doc_b.start_datetime), str(doc_b.end_datetime), exclude_booking=booking_a)
    if isinstance(conflict, str):
        import json
        conflict = json.loads(conflict)
    if conflict.get("has_conflict"):
        frappe.throw(_("Cannot swap — conflict for {0} in {1}").format(booking_b, space_a))

    # Perform swap
    frappe.db.set_value("Space Booking", booking_a, "space", space_b)
    frappe.db.set_value("Space Booking", booking_b, "space", space_a)

    doc_a.add_comment("Info", _("Swapped with {0} — moved from {1} to {2}").format(booking_b, space_a, space_b))
    doc_b.add_comment("Info", _("Swapped with {0} — moved from {1} to {2}").format(booking_a, space_b, space_a))

    _update_space_status(space_a)
    _update_space_status(space_b)

    frappe.db.commit()

    return {
        "success": True,
        "booking_a": _booking_card(frappe.get_doc("Space Booking", booking_a).as_dict(), "booking"),
        "booking_b": _booking_card(frappe.get_doc("Space Booking", booking_b).as_dict(), "booking"),
    }


@frappe.whitelist()
def quick_book(space, start_time, end_time, member=None, guest_name=None, booking_type="Hourly"):
    """
    Create a new booking directly from the scheduler grid.
    Used when clicking an empty slot.
    """
    frappe.only_for(["System Manager", "ARKSpace Admin", "ARKSpace Manager", "ARKSpace Front Desk"])

    start = get_datetime(start_time)
    end = get_datetime(end_time)

    if end <= start:
        frappe.throw(_("End time must be after start time."))

    # Check conflicts
    conflict = check_conflicts(space, start_time, end_time)
    if isinstance(conflict, str):
        import json
        conflict = json.loads(conflict)
    if conflict.get("has_conflict"):
        frappe.throw(_("Time slot has conflicts."))

    space_doc = frappe.get_doc("Co-working Space", space)
    if space_doc.status == "Maintenance":
        frappe.throw(_("Space is under maintenance."))

    # Determine rate
    rate = 0
    if booking_type == "Hourly":
        rate = flt(space_doc.hourly_rate)
    elif booking_type == "Daily":
        rate = flt(space_doc.daily_rate)
    elif booking_type == "Monthly":
        rate = flt(space_doc.monthly_rate)

    doc = frappe.get_doc({
        "doctype": "Space Booking",
        "space": space,
        "member": member,
        "booking_type": booking_type,
        "start_datetime": start,
        "end_datetime": end,
        "rate": rate,
        "status": "Confirmed",
    })

    doc.insert()
    doc.submit()

    return {
        "success": True,
        "booking": _booking_card(doc.as_dict(), "booking"),
    }


@frappe.whitelist()
def split_booking(booking, split_time, second_space):
    """
    Split a booking into two parts at split_time.
    First part stays in the original space (start → split_time).
    Second part moves to second_space (split_time → end).

    Scenario: Meeting runs 10:00–14:00. At 12:00 the original room is needed.
    Split at 12:00 → Part 1: 10:00–12:00 (original). Part 2: 12:00–14:00 (new room).
    """
    frappe.only_for(["System Manager", "ARKSpace Admin", "ARKSpace Manager", "ARKSpace Front Desk"])

    doc = frappe.get_doc("Space Booking", booking)

    if doc.docstatus != 1:
        frappe.throw(_("Only submitted bookings can be split."))

    if doc.status in ("Checked Out", "Cancelled", "No Show"):
        frappe.throw(_("Cannot split a {0} booking.").format(_(doc.status)))

    split = get_datetime(split_time)

    if split <= doc.start_datetime or split >= doc.end_datetime:
        frappe.throw(_("Split time must be between booking start and end."))

    # Check conflicts for the second part
    conflict = check_conflicts(second_space, str(split), str(doc.end_datetime))
    if isinstance(conflict, str):
        import json
        conflict = json.loads(conflict)
    if conflict.get("has_conflict"):
        frappe.throw(_("Conflict in target space for the second part."))

    original_end = doc.end_datetime

    # Shrink original booking to end at split time
    frappe.db.set_value("Space Booking", booking, "end_datetime", split)
    duration1 = time_diff_in_hours(split, doc.start_datetime)
    frappe.db.set_value("Space Booking", booking, "duration_hours", duration1)

    # Create second booking
    new_doc = frappe.get_doc({
        "doctype": "Space Booking",
        "space": second_space,
        "member": doc.member,
        "booking_type": doc.booking_type,
        "start_datetime": split,
        "end_datetime": original_end,
        "rate": doc.rate,
        "status": doc.status,
    })
    new_doc.insert()
    new_doc.submit()

    doc.add_comment("Info", _(
        "Booking split at {0}. Second part: {1} in {2}"
    ).format(
        format_datetime(split, "HH:mm"),
        new_doc.name,
        second_space,
    ))

    new_doc.add_comment("Info", _(
        "Created from split of {0} at {1}"
    ).format(booking, format_datetime(split, "HH:mm")))

    frappe.db.commit()

    return {
        "success": True,
        "original": _booking_card(frappe.get_doc("Space Booking", booking).as_dict(), "booking"),
        "new_booking": _booking_card(new_doc.as_dict(), "booking"),
    }


@frappe.whitelist()
def block_slot(space, start_time, end_time, reason="Maintenance"):
    """
    Block a time slot on a space (sets space to Maintenance for a period).
    Creates a placeholder booking-like record (or just updates space status).
    """
    frappe.only_for(["System Manager", "ARKSpace Admin", "ARKSpace Manager"])

    start = get_datetime(start_time)
    end = get_datetime(end_time)

    # Check existing bookings in range
    conflict = check_conflicts(space, start_time, end_time)
    if isinstance(conflict, str):
        import json
        conflict = json.loads(conflict)
    if conflict.get("has_conflict"):
        names = ", ".join([c["name"] for c in conflict["conflicts"]])
        frappe.throw(_("Cannot block — existing bookings: {0}. Move them first.").format(names))

    # For full-day blocks, set space status
    space_doc = frappe.get_doc("Co-working Space", space)
    space_doc.status = "Maintenance"
    space_doc.save(ignore_permissions=True)

    space_doc.add_comment("Info", _(
        "Blocked for {0}: {1} to {2}"
    ).format(reason, format_datetime(start, "HH:mm"), format_datetime(end, "HH:mm")))

    frappe.db.commit()

    return {
        "success": True,
        "space": space,
        "reason": reason,
        "start_hour": start.hour + start.minute / 60.0,
        "end_hour": end.hour + end.minute / 60.0,
    }


@frappe.whitelist()
def unblock_slot(space):
    """Remove maintenance block from a space."""
    frappe.only_for(["System Manager", "ARKSpace Admin", "ARKSpace Manager"])

    frappe.db.set_value("Co-working Space", space, "status", "Available")
    frappe.db.commit()

    return {"success": True, "space": space}


@frappe.whitelist()
def checkin_booking(booking):
    """Quick check-in from the scheduler grid."""
    frappe.only_for(["System Manager", "ARKSpace Admin", "ARKSpace Manager", "ARKSpace Front Desk"])

    doc = frappe.get_doc("Space Booking", booking)
    if doc.status != "Confirmed":
        frappe.throw(_("Only confirmed bookings can be checked in."))

    doc.status = "Checked In"
    doc.checked_in_at = now_datetime()
    doc.save(ignore_permissions=True)

    _update_space_status(doc.space, doc.member)

    frappe.db.commit()

    return {
        "success": True,
        "booking": _booking_card(doc.as_dict(), "booking"),
    }


@frappe.whitelist()
def checkout_booking(booking):
    """Quick check-out from the scheduler grid."""
    frappe.only_for(["System Manager", "ARKSpace Admin", "ARKSpace Manager", "ARKSpace Front Desk"])

    doc = frappe.get_doc("Space Booking", booking)
    if doc.status != "Checked In":
        frappe.throw(_("Only checked-in bookings can be checked out."))

    doc.status = "Checked Out"
    doc.checked_out_at = now_datetime()
    doc.save(ignore_permissions=True)

    _update_space_status(doc.space)

    frappe.db.commit()

    return {
        "success": True,
        "booking": _booking_card(doc.as_dict(), "booking"),
    }


@frappe.whitelist()
def get_available_spaces(space_type, start_time, end_time, branch=None):
    """
    Find all spaces of a type that are free during a time slot.
    Used by the "find empty room" feature.
    """
    frappe.has_permission("Co-working Space", "read", throw=True)
    start = get_datetime(start_time)
    end = get_datetime(end_time)

    filters = {"space_type": space_type, "status": ["!=", "Maintenance"]}
    if branch:
        filters["branch"] = branch

    all_spaces = frappe.get_all(
        "Co-working Space",
        filters=filters,
        fields=["name", "space_name", "status", "capacity", "floor"],
        order_by="space_name asc",
    )

    available = []
    for sp in all_spaces:
        conflict = check_conflicts(sp.name, str(start), str(end))
        if isinstance(conflict, str):
            import json
            conflict = json.loads(conflict)
        if not conflict.get("has_conflict"):
            available.append(sp)

    return available


# ── Internal helpers ──

def _update_space_status(space_name, member=None):
    """Update space status based on current bookings."""
    now = now_datetime()

    active = frappe.get_all(
        "Space Booking",
        filters={
            "space": space_name,
            "docstatus": 1,
            "status": "Checked In",
            "start_datetime": ["<=", now],
            "end_datetime": [">=", now],
        },
        fields=["member"],
        limit=1,
    )

    if active:
        frappe.db.set_value("Co-working Space", space_name, {
            "status": "Occupied",
            "current_member": active[0].member,
        })
    else:
        # Check if there's a confirmed booking right now
        confirmed = frappe.get_all(
            "Space Booking",
            filters={
                "space": space_name,
                "docstatus": 1,
                "status": "Confirmed",
                "start_datetime": ["<=", now],
                "end_datetime": [">=", now],
            },
            limit=1,
        )
        if confirmed:
            frappe.db.set_value("Co-working Space", space_name, {
                "status": "Reserved",
                "current_member": member,
            })
        else:
            space_status = frappe.db.get_value("Co-working Space", space_name, "status")
            if space_status not in ("Maintenance",):
                frappe.db.set_value("Co-working Space", space_name, {
                    "status": "Available",
                    "current_member": None,
                })
