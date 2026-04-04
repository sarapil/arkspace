# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

# Portal context for community page

import frappe
from frappe.utils import cint


def get_context(context):
    context.no_cache = 1
    context.title = "Community — المجتمع"

    # Get branches for filter
    context.branches = frappe.get_all("Branch", pluck="name")

    # Get pinned/recent posts
    context.pinned_posts = frappe.get_all(
        "Community Post",
        filters={"status": "Published", "is_pinned": 1},
        fields=["name", "title", "post_type", "author_name", "creation",
                "likes_count", "comments_count", "content"],
        order_by="creation desc",
        limit=5,
    )

    context.recent_posts = frappe.get_all(
        "Community Post",
        filters={"status": "Published"},
        fields=["name", "title", "post_type", "author_name", "creation",
                "likes_count", "comments_count", "is_anonymous", "tags"],
        order_by="creation desc",
        limit=20,
    )

    # Mask anonymous authors
    for p in context.recent_posts:
        if cint(p.get("is_anonymous")):
            p["author_name"] = "Anonymous Member"

    # Upcoming events
    context.upcoming_events = frappe.get_all(
        "Community Event",
        filters={
            "status": ["not in", ["Cancelled", "Draft", "Completed"]],
        },
        fields=["name", "event_name", "event_type", "start_datetime",
                "max_attendees", "current_attendees", "is_free", "image"],
        order_by="start_datetime asc",
        limit=5,
    )
