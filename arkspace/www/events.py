# Copyright (c) 2026, ARKSpace Team and contributors
# Portal context for events page

import frappe


def get_context(context):
    context.no_cache = 1
    context.title = "Events — الفعاليات"

    # Upcoming events
    context.upcoming_events = frappe.get_all(
        "Community Event",
        filters={
            "status": ["not in", ["Cancelled", "Draft", "Completed"]],
        },
        fields=[
            "name", "event_name", "event_name_ar", "event_type",
            "organizer_name", "branch", "space", "image",
            "start_datetime", "end_datetime",
            "max_attendees", "current_attendees",
            "registration_required", "is_free", "fee",
            "status", "is_featured", "description",
        ],
        order_by="is_featured desc, start_datetime asc",
        limit=50,
    )

    # Past events
    context.past_events = frappe.get_all(
        "Community Event",
        filters={"status": "Completed"},
        fields=["name", "event_name", "event_type", "start_datetime",
                "current_attendees", "image"],
        order_by="start_datetime desc",
        limit=10,
    )

    context.branches = frappe.get_all("Branch", pluck="name")
