# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

"""ARKSpace — Community & Networking API

Provides community feed, member directory, skill matching,
events, and networking request management.
"""

import frappe  # noqa: I001
from frappe import _
from frappe.utils import cint, now_datetime


# ──────────────────────── Community Feed ───────────────────────────────

@frappe.whitelist(allow_guest=True)
def get_community_feed(branch=None, post_type=None, page=0, page_size=20):
    """Get paginated community feed with posts and engagement counts.

    Args:
        branch: Filter by branch
        post_type: Filter by type (Discussion, Announcement, etc.)
        page: Page number (0-indexed)
        page_size: Items per page
    """
    filters = {"status": "Published"}
    if branch:
        filters["branch"] = branch
    if post_type:
        filters["post_type"] = post_type

    posts = frappe.get_all(
        "Community Post",
        filters=filters,
        fields=[
            "name", "title", "post_type", "author", "author_name",
            "branch", "content", "tags", "likes_count", "comments_count",
            "views_count", "is_pinned", "is_anonymous", "creation",
        ],
        order_by="is_pinned desc, creation desc",
        start=cint(page) * cint(page_size),
        limit_page_length=cint(page_size),
    )

    # Check if current user liked each post
    user = frappe.session.user
    if user != "Guest":
        for p in posts:
            p["user_liked"] = bool(frappe.db.exists("Comment", {
                "reference_doctype": "Community Post",
                "reference_name": p.name,
                "comment_type": "Like",
                "comment_email": user,
            }))
            if p.get("is_anonymous"):
                p["author"] = ""
                p["author_name"] = _("Anonymous Member")

    total = frappe.db.count("Community Post", filters)

    return {
        "posts": posts,
        "total": total,
        "page": cint(page),
        "page_size": cint(page_size),
        "has_more": (cint(page) + 1) * cint(page_size) < total,
    }


@frappe.whitelist()
def create_post(title, content, post_type="Discussion", tags=None, branch=None, is_anonymous=False):
    """Create a new community post."""
    frappe.only_for(["ARKSpace Manager", "System Manager"])

    post = frappe.get_doc({
        "doctype": "Community Post",
        "title": title,
        "content": content,
        "post_type": post_type,
        "tags": tags,
        "branch": branch,
        "author": frappe.session.user,
        "is_anonymous": cint(is_anonymous),
        "status": "Published",
    })
    post.insert(ignore_permissions=True)

    frappe.publish_realtime("new_community_post", {
        "post": post.name,
        "title": title,
        "post_type": post_type,
        "author": frappe.session.user if not cint(is_anonymous) else "Anonymous",
    })

    return post.as_dict()


@frappe.whitelist()
def like_post(post):
    """Toggle like on a community post."""
    frappe.only_for(["ARKSpace User", "ARKSpace Manager", "System Manager"])

    doc = frappe.get_doc("Community Post", post)
    return doc.toggle_like()


# ──────────────────────── Member Directory ─────────────────────────────

@frappe.whitelist()
def get_member_directory(branch=None, skills=None, search=None, page=0, page_size=20):
    """Get searchable member directory with skills and profiles.

    Args:
        branch: Filter by branch
        skills: Comma-separated skill names to filter by
        search: Free-text search on member name/email
        page: Page number
        page_size: Items per page
    """
    frappe.only_for(["ARKSpace User", "ARKSpace Manager", "System Manager"])

    # Get members with active memberships
    filters = {"docstatus": 1, "status": "Active"}
    if branch:
        filters["branch"] = branch

    members = frappe.get_all(
        "Membership",
        filters=filters,
        fields=["member", "member_name", "membership_plan", "branch"],
        group_by="member",
        order_by="member_name asc",
        start=cint(page) * cint(page_size),
        limit_page_length=cint(page_size),
    )

    result = []
    for m in members:
        if search and search.lower() not in (m.member_name or "").lower():
            continue

        # Get user info
        user_info = frappe.db.get_value("User", m.member, [
            "full_name", "user_image", "bio",
        ], as_dict=True) or {}

        member_data = {
            "member": m.member,
            "name": user_info.get("full_name") or m.member_name,
            "image": user_info.get("user_image"),
            "bio": user_info.get("bio"),
            "plan": m.membership_plan,
            "branch": m.branch,
            "skills": [],
        }

        # This would normally come from a user-linked skills table
        # For now, check if there are Community Posts that reveal skills via tags
        result.append(member_data)

    # If skills filter is provided, we'd filter here
    # (Placeholder for when Member Skill table is linked to User)

    return {
        "members": result,
        "total": len(result),
        "page": cint(page),
    }


@frappe.whitelist()
def get_member_profile(member):
    """Get public profile for a specific member."""
    frappe.only_for(["ARKSpace User", "ARKSpace Manager", "System Manager"])

    user_info = frappe.db.get_value("User", member, [
        "full_name", "user_image", "bio", "location",
    ], as_dict=True)

    if not user_info:
        frappe.throw(_("Member not found"))

    # Get active membership
    membership = frappe.db.get_value("Membership", {
        "member": member, "docstatus": 1, "status": "Active",
    }, ["name", "membership_plan", "branch", "start_date"], as_dict=True)

    # Get recent posts
    recent_posts = frappe.get_all("Community Post", {
        "author": member,
        "status": "Published",
        "is_anonymous": 0,
    }, ["name", "title", "post_type", "creation", "likes_count"],
        order_by="creation desc", limit=5)

    # Get networking connections
    connections = frappe.db.count("Networking Request", {
        "status": "Accepted",
        "from_member": member,
    }) + frappe.db.count("Networking Request", {
        "status": "Accepted",
        "to_member": member,
    })

    # Check if current user has a pending request
    current_user = frappe.session.user
    connection_status = None
    if current_user != member:
        req = frappe.db.get_value("Networking Request", {
            "from_member": ["in", [current_user, member]],
            "to_member": ["in", [current_user, member]],
            "status": ["in", ["Pending", "Accepted"]],
        }, ["status", "from_member"], as_dict=True)
        if req:
            connection_status = req.status

    return {
        "member": member,
        "name": user_info.full_name,
        "image": user_info.user_image,
        "bio": user_info.bio,
        "location": user_info.location,
        "membership": membership,
        "recent_posts": recent_posts,
        "connections": connections,
        "connection_status": connection_status,
    }


# ──────────────────────── Networking ───────────────────────────────────

@frappe.whitelist()
def send_networking_request(to_member, message=None):
    """Send a networking/connection request to another member."""
    frappe.only_for(["ARKSpace Manager", "System Manager"])

    if frappe.session.user == to_member:
        frappe.throw(_("Cannot send a request to yourself"))

    req = frappe.get_doc({
        "doctype": "Networking Request",
        "from_member": frappe.session.user,
        "to_member": to_member,
        "message": message,
        "status": "Pending",
    })
    req.insert(ignore_permissions=True)

    frappe.publish_realtime("new_networking_request", {
        "request": req.name,
        "from": frappe.session.user,
        "from_name": frappe.db.get_value("User", frappe.session.user, "full_name"),
        "message": message,
    }, user=to_member)

    return {"status": "sent", "request": req.name}


@frappe.whitelist()
def respond_to_request(request, action):
    """Accept or decline a networking request.

    Args:
        request: Networking Request name
        action: 'accept' or 'decline'
    """
    frappe.only_for(["ARKSpace User", "ARKSpace Manager", "System Manager"])

    doc = frappe.get_doc("Networking Request", request)

    if action == "accept":
        return doc.accept()
    elif action == "decline":
        return doc.decline()
    else:
        frappe.throw(_("Invalid action. Use 'accept' or 'decline'."))


@frappe.whitelist()
def get_my_connections():
    """Get current user's accepted connections."""
    frappe.only_for(["ARKSpace User", "ARKSpace Manager", "System Manager"])

    user = frappe.session.user

    # Connections where user is from_member
    sent = frappe.get_all("Networking Request", {
        "from_member": user,
        "status": "Accepted",
    }, ["to_member as connected_to", "creation"])

    # Connections where user is to_member
    received = frappe.get_all("Networking Request", {
        "to_member": user,
        "status": "Accepted",
    }, ["from_member as connected_to", "creation"])

    connections = []
    for c in sent + received:
        user_info = frappe.db.get_value("User", c.connected_to, [
            "full_name", "user_image",
        ], as_dict=True) or {}
        connections.append({
            "member": c.connected_to,
            "name": user_info.get("full_name", c.connected_to),
            "image": user_info.get("user_image"),
            "connected_since": c.creation,
        })

    return connections


@frappe.whitelist()
def get_pending_requests():
    """Get networking requests pending for current user."""
    frappe.only_for(["ARKSpace User", "ARKSpace Manager", "System Manager"])

    user = frappe.session.user

    incoming = frappe.get_all("Networking Request", {
        "to_member": user,
        "status": "Pending",
    }, ["name", "from_member", "from_member_name", "message", "creation"])

    outgoing = frappe.get_all("Networking Request", {
        "from_member": user,
        "status": "Pending",
    }, ["name", "to_member", "to_member_name", "message", "creation"])

    return {"incoming": incoming, "outgoing": outgoing}


# ──────────────────────── Events ───────────────────────────────────────

@frappe.whitelist(allow_guest=True)
def get_events(branch=None, event_type=None, from_date=None, upcoming_only=True):
    """Get community events."""
    filters = {}
    if branch:
        filters["branch"] = branch
    if event_type:
        filters["event_type"] = event_type

    if cint(upcoming_only):
        filters["start_datetime"] = [">=", now_datetime()]
        filters["status"] = ["not in", ["Cancelled", "Draft"]]
    elif from_date:
        filters["start_datetime"] = [">=", from_date]

    events = frappe.get_all(
        "Community Event",
        filters=filters,
        fields=[
            "name", "event_name", "event_name_ar", "event_type",
            "organizer_name", "branch", "space", "image",
            "start_datetime", "end_datetime",
            "max_attendees", "current_attendees",
            "registration_required", "is_free", "fee",
            "status", "is_featured", "description",
        ],
        order_by="is_featured desc, start_datetime asc",
        limit_page_length=50,
    )

    # Check registration status for current user
    user = frappe.session.user
    if user != "Guest":
        for e in events:
            e["user_registered"] = bool(frappe.db.exists("Comment", {
                "reference_doctype": "Community Event",
                "reference_name": e.name,
                "comment_type": "Info",
                "comment_email": user,
                "content": ["like", "%REGISTERED%"],
            }))

    return events


@frappe.whitelist()
def register_for_event(event):
    """Register current user for an event."""
    frappe.only_for(["ARKSpace User", "ARKSpace Manager", "System Manager"])

    doc = frappe.get_doc("Community Event", event)
    return doc.register_attendee()


@frappe.whitelist()
def cancel_event_registration(event):
    """Cancel current user's event registration."""
    frappe.only_for(["ARKSpace Manager", "System Manager"])

    doc = frappe.get_doc("Community Event", event)
    return doc.cancel_registration()


@frappe.whitelist()
def get_event_attendees(event):
    """Get list of registered attendees for an event."""
    frappe.only_for(["ARKSpace User", "ARKSpace Manager", "System Manager"])

    regs = frappe.get_all("Comment", {
        "reference_doctype": "Community Event",
        "reference_name": event,
        "comment_type": "Info",
        "content": ["like", "%REGISTERED%"],
    }, ["comment_email", "creation"], order_by="creation asc")

    attendees = []
    for r in regs:
        user_info = frappe.db.get_value("User", r.comment_email, [
            "full_name", "user_image",
        ], as_dict=True) or {}
        attendees.append({
            "email": r.comment_email,
            "name": user_info.get("full_name", r.comment_email),
            "image": user_info.get("user_image"),
            "registered_at": r.creation,
        })

    return attendees


# ──────────────────────── Update Event Statuses ────────────────────────

def update_event_statuses():
    """Scheduler task: update community event statuses based on time."""
    now = now_datetime()

    # Mark completed events
    completed = frappe.get_all("Community Event", {
        "status": ["not in", ["Completed", "Cancelled", "Draft"]],
        "end_datetime": ["<", now],
    }, pluck="name")

    for name in completed:
        frappe.db.set_value("Community Event", name, "status", "Completed")

    # Mark in-progress events
    in_progress = frappe.get_all("Community Event", {
        "status": ["in", ["Upcoming", "Open for Registration", "Full"]],
        "start_datetime": ["<=", now],
        "end_datetime": [">=", now],
    }, pluck="name")

    for name in in_progress:
        frappe.db.set_value("Community Event", name, "status", "In Progress")

    if completed or in_progress:
        frappe.db.commit()
        frappe.logger("arkspace").info(
            f"Updated event statuses: {len(completed)} completed, "
            f"{len(in_progress)} in progress"
        )
