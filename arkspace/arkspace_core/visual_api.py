# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

"""ARKSpace — Visual API

Provides graph-ready data (nodes + edges) for all visual screens:
  1. Command Center  — KPIs + space/booking/member overview graph
  2. Space Explorer  — radial relationships from any entity
  3. Booking Flow    — workflow pipeline with live statuses
  4. Community Graph — member network + events + posts
  5. Onboarding      — summary data for storyboard wizard
"""

import frappe  # noqa: I001
from frappe import _
from frappe.utils import (
    cint,
    flt,
    get_url,
    getdate,
    nowdate,
)

# ─────────────────── Colour & type constants ──────────────────────────

_STATUS_COLOR = {
    "Available": "active",
    "Occupied": "warning",
    "Maintenance": "error",
    "Reserved": "settings",
    # Booking
    "Pending": "warning",
    "Confirmed": "master",
    "Checked In": "active",
    "Checked Out": "settings",
    "Cancelled": "error",
    "No Show": "disabled",
    # Membership
    "Draft": "settings",
    "Active": "active",
    "Expired": "error",
    "Suspended": "warning",
    # Lead
    "New": "action",
    "Contacted": "master",
    "Tour Scheduled": "meeting",
    "Negotiating": "warning",
    "Converted": "active",
    "Lost": "disabled",
    # Community Post
    "Published": "active",
    "Archived": "disabled",
    "Reported": "error",
    # Community Event
    "Upcoming": "action",
    "Open for Registration": "master",
    "Full": "warning",
    "In Progress": "active",
    "Completed": "settings",
    # Networking
    "Accepted": "active",
    "Declined": "error",
    "Withdrawn": "disabled",
}


def _sc(status: str) -> str:
    """Return frappe_visual node type for a given status."""
    return _STATUS_COLOR.get(status, "settings")


# ═════════════════════════════════════════════════════════════════════
# 1. COMMAND CENTER
# ═════════════════════════════════════════════════════════════════════


@frappe.whitelist()
def get_command_center_kpis(branch=None):
    """Return top-level KPI cards for the Command Center dashboard."""
    frappe.only_for(["ARKSpace User", "ARKSpace Manager", "System Manager"])

    filters_space = {}
    if branch:
        filters_space["branch"] = branch

    total = frappe.db.count("Co-working Space", filters_space)
    available = frappe.db.count("Co-working Space", {**filters_space, "status": "Available"})
    occupied = frappe.db.count("Co-working Space", {**filters_space, "status": "Occupied"})

    today = nowdate()
    booking_filters = {"docstatus": 1}
    if branch:
        spaces_in_branch = frappe.get_all(
            "Co-working Space", {"branch": branch}, pluck="name",
        ) or ["__none__"]
        booking_filters["space"] = ["in", spaces_in_branch]

    todays_bookings = frappe.db.count("Space Booking", {
        **booking_filters,
        "start_datetime": [">=", f"{today} 00:00:00"],
        "end_datetime": ["<=", f"{today} 23:59:59"],
    }) or 0

    active_members = frappe.db.count("Membership", {
        "docstatus": 1, "status": "Active",
        **({"branch": branch} if branch else {}),
    }) or 0

    todays_visitors = frappe.db.count("Visitor Log", {
        "expected_arrival": ["between", [f"{today} 00:00:00", f"{today} 23:59:59"]],
        "status": ["in", ["Expected", "Checked In"]],
        **({"visiting_branch": branch} if branch else {}),
    }) or 0

    checked_in_now = frappe.db.count("Space Booking", {
        **booking_filters, "status": "Checked In",
    }) or 0

    # Revenue this month
    first_of_month = getdate(today).replace(day=1)
    month_revenue = frappe.db.sql("""
        SELECT COALESCE(SUM(net_amount), 0) FROM `tabSpace Booking`
        WHERE docstatus = 1 AND start_datetime >= %s
    """, (f"{first_of_month} 00:00:00",))[0][0] or 0

    occupancy_rate = round(occupied / total * 100, 1) if total else 0

    return [
        {
            "label": _("Total Spaces"), "value": str(total), "icon": "🏢",
            "color": "#6366f1", "subtitle": _(f"{available} available"),
        },
        {
            "label": _("Occupancy"), "value": f"{occupancy_rate}%", "icon": "📊",
            "color": "#f59e0b" if occupancy_rate > 80 else "#10b981",
            "subtitle": _(f"{occupied} of {total}"),
        },
        {
            "label": _("Today's Bookings"), "value": str(todays_bookings), "icon": "📅",
            "color": "#3b82f6", "subtitle": _(f"{checked_in_now} checked in"),
        },
        {
            "label": _("Active Members"), "value": str(active_members), "icon": "👥",
            "color": "#10b981", "subtitle": _("Active subscriptions"),
        },
        {
            "label": _("Visitors Today"), "value": str(todays_visitors), "icon": "🚶",
            "color": "#8b5cf6", "subtitle": _("Expected & checked in"),
        },
        {
            "label": _("Monthly Revenue"), "value": frappe.format_value(
                month_revenue, {"fieldtype": "Currency"},
            ), "icon": "💰",
            "color": "#059669", "subtitle": getdate(today).strftime("%B %Y"),
        },
    ]


@frappe.whitelist()
def get_command_center_graph(branch=None):
    """Build the main overview graph: branches → spaces grouped by type → active bookings."""
    frappe.only_for(["ARKSpace User", "ARKSpace Manager", "System Manager"])

    nodes = []
    edges = []

    # ── Branches ──
    branch_filters = {"is_active": 1}
    if branch:
        branch_filters["name"] = branch
    branches = frappe.get_all(
        "ARKSpace Branch",
        branch_filters,
        ["name", "branch_name", "branch_name_ar", "max_capacity", "current_occupancy"],
    )

    if not branches:
        # Fallback: single virtual branch
        branches = [{"name": "__all__", "branch_name": _("All Spaces"), "max_capacity": 0}]

    for br in branches:
        nodes.append({
            "id": f"br-{br['name']}",
            "label": br.get("branch_name_ar") or br["branch_name"],
            "type": "server",
            "doctype": "ARKSpace Branch",
            "docname": br["name"],
            "badge": _("{0} capacity").format(br.get("max_capacity") or "—"),
            "status": "active",
        })

    # ── Spaces grouped by type inside branches ──
    space_filters = {}
    if branch:
        space_filters["branch"] = branch

    spaces = frappe.get_all(
        "Co-working Space",
        space_filters,
        ["name", "space_name", "space_type", "branch", "status",
         "capacity", "hourly_rate", "daily_rate", "monthly_rate",
         "current_member"],
        order_by="branch, space_type, name",
    )

    # Group by (branch, space_type) to make compound nodes
    groups = {}
    for sp in spaces:
        br_key = sp.get("branch") or "__all__"
        grp_key = f"{br_key}::{sp['space_type']}"
        groups.setdefault(grp_key, []).append(sp)

    for grp_key, grp_spaces in groups.items():
        br_key, stype = grp_key.split("::", 1)
        grp_id = f"grp-{grp_key.replace('::', '-').replace(' ', '_')}"
        available_count = sum(1 for s in grp_spaces if s["status"] == "Available")
        occupied_count = sum(1 for s in grp_spaces if s["status"] == "Occupied")

        nodes.append({
            "id": grp_id,
            "label": stype,
            "type": "module",
            "parent": f"br-{br_key}",
            "summary": {
                "total": len(grp_spaces),
                "available": available_count,
                "occupied": occupied_count,
            },
            "badge": f"{occupied_count}/{len(grp_spaces)}",
        })

        edges.append({
            "source": f"br-{br_key}",
            "target": grp_id,
            "type": "child",
        })

        for sp in grp_spaces:
            node_type = _sc(sp["status"])
            sp_node = {
                "id": f"sp-{sp['name']}",
                "label": sp.get("space_name") or sp["name"],
                "type": node_type,
                "parent": grp_id,
                "doctype": "Co-working Space",
                "docname": sp["name"],
                "status": sp["status"].lower().replace(" ", "-"),
                "badge": sp["status"],
                "meta": {
                    "capacity": sp.get("capacity"),
                    "hourly_rate": sp.get("hourly_rate"),
                    "daily_rate": sp.get("daily_rate"),
                    "monthly_rate": sp.get("monthly_rate"),
                    "current_member": sp.get("current_member"),
                },
            }
            nodes.append(sp_node)

            # Edge: group → space
            edges.append({
                "source": grp_id,
                "target": f"sp-{sp['name']}",
                "type": "child",
            })

    # ── Active bookings (today) ──
    today = nowdate()
    active_bookings = frappe.get_all(
        "Space Booking",
        {
            "docstatus": 1,
            "status": ["in", ["Pending", "Confirmed", "Checked In"]],
            "start_datetime": [">=", f"{today} 00:00:00"],
        },
        ["name", "space", "member", "status", "booking_type",
         "start_datetime", "end_datetime", "total_amount"],
        limit=50,
        order_by="start_datetime",
    )

    seen_members = set()
    for bk in active_bookings:
        nodes.append({
            "id": f"bk-{bk['name']}",
            "label": bk["name"],
            "type": "transaction" if bk["status"] != "Checked In" else "active",
            "doctype": "Space Booking",
            "docname": bk["name"],
            "badge": bk["status"],
            "status": bk["status"].lower().replace(" ", "-"),
            "meta": {
                "booking_type": bk.get("booking_type"),
                "amount": bk.get("total_amount"),
            },
        })
        # Edge: space → booking (animated if checked in)
        edges.append({
            "source": f"sp-{bk['space']}",
            "target": f"bk-{bk['name']}",
            "type": "flow",
            "animated": bk["status"] == "Checked In",
            "label": bk.get("booking_type", ""),
        })

        # Member node (deduplicated)
        if bk.get("member") and bk["member"] not in seen_members:
            seen_members.add(bk["member"])
            member_name = frappe.db.get_value(
                "Customer", bk["member"], "customer_name",
            ) or bk["member"]
            nodes.append({
                "id": f"mbr-{bk['member']}",
                "label": member_name,
                "type": "user",
                "doctype": "Customer",
                "docname": bk["member"],
            })

        if bk.get("member"):
            edges.append({
                "source": f"mbr-{bk['member']}",
                "target": f"bk-{bk['name']}",
                "type": "link",
                "label": _("booked"),
            })

    return {"nodes": nodes, "edges": edges}


# ═════════════════════════════════════════════════════════════════════
# 2. SPACE EXPLORER  (Radial from any entity)
# ═════════════════════════════════════════════════════════════════════


@frappe.whitelist()
def get_space_explorer(doctype, docname, depth=1):
    """Build a radial exploration graph centered on any ARKSpace entity."""
    frappe.only_for(["ARKSpace User", "ARKSpace Manager", "System Manager"])

    depth = cint(depth) or 1
    nodes = []
    edges = []
    visited = set()

    def _add(dt, dn, level=0):
        uid = f"{dt}::{dn}"
        if uid in visited or level > depth:
            return
        visited.add(uid)
        nid = f"n-{dt.replace(' ', '_')}-{dn.replace(' ', '_')}"

        # Determine node type & label
        type_map = {
            "Co-working Space": "device",
            "Space Booking": "transaction",
            "Membership": "master",
            "Membership Plan": "module",
            "Customer": "user",
            "Day Pass": "transaction",
            "Visitor Log": "log",
            "Online Payment": "transaction",
            "Workspace Lead": "action",
            "Workspace Tour": "meeting",
            "Member Contract": "master",
            "Training Session": "meeting",
            "Training Module": "module",
            "Community Post": "whatsapp",
            "Community Event": "meeting",
            "Networking Request": "call",
            "ARKSpace Branch": "server",
            "Analytics Snapshot": "dashboard",
            "Pricing Rule": "settings",
            "Member Credit Wallet": "master",
        }
        ntype = type_map.get(dt, "doctype")

        # Fetch display value
        doc = frappe.get_doc(dt, dn)
        label = (
            doc.get("space_name")
            or doc.get("branch_name")
            or doc.get("customer_name")
            or doc.get("member_name")
            or doc.get("event_name")
            or doc.get("title")
            or dn
        )
        status = doc.get("status") or ""
        badge = status or dt

        nodes.append({
            "id": nid,
            "label": str(label),
            "type": ntype if not status else _sc(status),
            "doctype": dt,
            "docname": dn,
            "badge": badge,
            "status": status.lower().replace(" ", "-") if status else "",
        })

        if level >= depth:
            return

        # Follow Link fields outward
        meta = frappe.get_meta(dt)
        for field in meta.fields:
            if field.fieldtype == "Link" and field.options and field.options != dt:
                val = doc.get(field.fieldname)
                if val and frappe.db.exists(field.options, val):
                    child_nid = f"n-{field.options.replace(' ', '_')}-{val.replace(' ', '_')}"
                    _add(field.options, val, level + 1)
                    if child_nid != nid:
                        edges.append({
                            "source": nid,
                            "target": child_nid,
                            "type": "link",
                            "label": field.label or field.fieldname,
                        })

        # Follow reverse links (who links TO this doc)
        if level < depth:
            linked_doctypes = [
                "Space Booking", "Membership", "Day Pass", "Visitor Log",
                "Online Payment", "Workspace Lead", "Workspace Tour",
                "Member Contract", "Community Event", "Networking Request",
            ]
            for ldt in linked_doctypes:
                lmeta = frappe.get_meta(ldt)
                for lf in lmeta.fields:
                    if lf.fieldtype == "Link" and lf.options == dt:
                        linked_docs = frappe.get_all(
                            ldt, {lf.fieldname: dn}, ["name"], limit=10,
                        )
                        for ld in linked_docs:
                            child_nid = f"n-{ldt.replace(' ', '_')}-{ld['name'].replace(' ', '_')}"
                            _add(ldt, ld["name"], level + 1)
                            if child_nid != nid:
                                edges.append({
                                    "source": nid,
                                    "target": child_nid,
                                    "type": "reference",
                                    "label": ldt,
                                })

    _add(doctype, docname, 0)
    return {"nodes": nodes, "edges": edges}


# ═════════════════════════════════════════════════════════════════════
# 3. BOOKING FLOW MONITOR
# ═════════════════════════════════════════════════════════════════════


@frappe.whitelist()
def get_booking_flow(branch=None, date=None):
    """Pipeline graph: booking statuses as columns, individual bookings as nodes."""
    frappe.only_for(["ARKSpace User", "ARKSpace Manager", "System Manager"])

    date = date or nowdate()
    nodes = []
    edges = []

    # Pipeline stages
    stages = [
        ("Pending", "warning", "⏳"),
        ("Confirmed", "master", "✅"),
        ("Checked In", "active", "🏠"),
        ("Checked Out", "settings", "🚪"),
        ("Cancelled", "error", "❌"),
        ("No Show", "disabled", "👻"),
    ]

    for i, (status, ntype, icon) in enumerate(stages):
        nodes.append({
            "id": f"stage-{status.replace(' ', '_')}",
            "label": f"{icon} {_(status)}",
            "type": ntype,
            "meta": {"is_stage": True},
        })
        if i > 0:
            prev = stages[i - 1][0]
            edges.append({
                "source": f"stage-{prev.replace(' ', '_')}",
                "target": f"stage-{status.replace(' ', '_')}",
                "type": "flow",
                "animated": True,
            })

    # Actual bookings for the date
    filters = {
        "docstatus": 1,
        "start_datetime": [">=", f"{date} 00:00:00"],
        "end_datetime": ["<=", f"{date} 23:59:59"],
    }
    if branch:
        branch_spaces = frappe.get_all(
            "Co-working Space", {"branch": branch}, pluck="name",
        ) or ["__none__"]
        filters["space"] = ["in", branch_spaces]

    bookings = frappe.get_all(
        "Space Booking",
        filters,
        ["name", "space", "member", "status", "booking_type",
         "start_datetime", "end_datetime", "total_amount", "net_amount"],
        order_by="start_datetime",
        limit=100,
    )

    # Count per status for stage badges
    counts = {}
    for bk in bookings:
        counts[bk["status"]] = counts.get(bk["status"], 0) + 1

    for status, ntype, icon in stages:
        # Update stage badge
        for n in nodes:
            if n["id"] == f"stage-{status.replace(' ', '_')}":
                n["badge"] = str(counts.get(status, 0))
                n["summary"] = {"count": counts.get(status, 0)}
                break

    for bk in bookings:
        space_name = frappe.db.get_value("Co-working Space", bk["space"], "space_name") or bk["space"]
        member_name = ""
        if bk.get("member"):
            member_name = frappe.db.get_value("Customer", bk["member"], "customer_name") or bk["member"]

        nodes.append({
            "id": f"bk-{bk['name']}",
            "label": f"{bk['name']}",
            "type": _sc(bk["status"]),
            "doctype": "Space Booking",
            "docname": bk["name"],
            "badge": bk.get("booking_type", ""),
            "status": bk["status"].lower().replace(" ", "-"),
            "meta": {
                "space": space_name,
                "member": member_name,
                "amount": flt(bk.get("total_amount")),
                "start": str(bk.get("start_datetime", "")),
                "end": str(bk.get("end_datetime", "")),
            },
        })

        stage_id = f"stage-{bk['status'].replace(' ', '_')}"
        edges.append({
            "source": stage_id,
            "target": f"bk-{bk['name']}",
            "type": "child",
        })

    return {"nodes": nodes, "edges": edges, "counts": counts, "total": len(bookings)}


# ═════════════════════════════════════════════════════════════════════
# 4. COMMUNITY NETWORK GRAPH
# ═════════════════════════════════════════════════════════════════════


@frappe.whitelist()
def get_community_graph(branch=None, limit=50):
    """Social graph: members, networking connections, events, popular posts."""
    frappe.only_for(["ARKSpace User", "ARKSpace Manager", "System Manager"])

    limit = cint(limit) or 50
    nodes = []
    edges = []
    seen = set()

    # ── Members with accepted connections ──
    connections = frappe.get_all(
        "Networking Request",
        {"status": "Accepted", **({"branch": branch} if branch else {})},
        ["from_member", "from_member_name", "to_member", "to_member_name"],
        limit=limit,
    )

    for conn in connections:
        for field, name_field in [("from_member", "from_member_name"), ("to_member", "to_member_name")]:
            uid = conn[field]
            if uid not in seen:
                seen.add(uid)
                nodes.append({
                    "id": f"u-{uid}",
                    "label": conn.get(name_field) or uid,
                    "type": "user",
                    "doctype": "User",
                    "docname": uid,
                })
        edges.append({
            "source": f"u-{conn['from_member']}",
            "target": f"u-{conn['to_member']}",
            "type": "link",
            "label": _("connected"),
        })

    # ── Community Events (upcoming/in-progress) ──
    events = frappe.get_all(
        "Community Event",
        {
            "status": ["in", ["Upcoming", "Open for Registration", "In Progress"]],
            **({"branch": branch} if branch else {}),
        },
        ["name", "event_name", "event_type", "status",
         "current_attendees", "max_attendees", "organizer"],
        limit=20,
    )

    for evt in events:
        nodes.append({
            "id": f"evt-{evt['name']}",
            "label": evt["event_name"],
            "type": "meeting",
            "doctype": "Community Event",
            "docname": evt["name"],
            "badge": f"{evt.get('current_attendees', 0)}/{evt.get('max_attendees', '∞')}",
            "status": _sc(evt["status"]),
            "meta": {"event_type": evt.get("event_type")},
        })
        # Link organizer
        if evt.get("organizer") and evt["organizer"] in seen:
            edges.append({
                "source": f"u-{evt['organizer']}",
                "target": f"evt-{evt['name']}",
                "type": "flow",
                "label": _("organizes"),
                "animated": True,
            })

    # ── Popular Posts (top 10 by likes) ──
    posts = frappe.get_all(
        "Community Post",
        {
            "status": "Published",
            **({"branch": branch} if branch else {}),
        },
        ["name", "title", "post_type", "author", "author_name",
         "likes_count", "comments_count", "views_count"],
        order_by="likes_count desc",
        limit=10,
    )

    for post in posts:
        nodes.append({
            "id": f"post-{post['name']}",
            "label": post["title"] or post["name"],
            "type": "whatsapp",
            "doctype": "Community Post",
            "docname": post["name"],
            "badge": f"❤ {post.get('likes_count', 0)}",
            "meta": {
                "post_type": post.get("post_type"),
                "comments": post.get("comments_count", 0),
                "views": post.get("views_count", 0),
            },
        })
        # Link author
        if post.get("author") and post["author"] in seen:
            edges.append({
                "source": f"u-{post['author']}",
                "target": f"post-{post['name']}",
                "type": "reference",
                "label": _("posted"),
            })

    return {"nodes": nodes, "edges": edges}


# ═════════════════════════════════════════════════════════════════════
# 5. CRM PIPELINE
# ═════════════════════════════════════════════════════════════════════


@frappe.whitelist()
def get_crm_pipeline(branch=None):
    """Visualize lead → tour → membership conversion funnel."""
    frappe.only_for(["ARKSpace User", "ARKSpace Manager", "System Manager"])

    nodes = []
    edges = []

    # Pipeline stages
    crm_stages = [
        ("New", "action", "🆕"),
        ("Contacted", "master", "📞"),
        ("Tour Scheduled", "meeting", "🗓️"),
        ("Negotiating", "warning", "🤝"),
        ("Converted", "active", "🎉"),
        ("Lost", "disabled", "💔"),
    ]

    for i, (status, ntype, icon) in enumerate(crm_stages):
        nodes.append({
            "id": f"crm-stage-{status.replace(' ', '_')}",
            "label": f"{icon} {_(status)}",
            "type": ntype,
            "meta": {"is_stage": True},
        })

    # Flow edges (main pipeline)
    for i in range(len(crm_stages) - 2):  # exclude Lost
        edges.append({
            "source": f"crm-stage-{crm_stages[i][0].replace(' ', '_')}",
            "target": f"crm-stage-{crm_stages[i + 1][0].replace(' ', '_')}",
            "type": "flow",
            "animated": True,
        })
    # Branch to Lost from Contacted & Negotiating
    for src in ["Contacted", "Negotiating"]:
        edges.append({
            "source": f"crm-stage-{src.replace(' ', '_')}",
            "target": "crm-stage-Lost",
            "type": "flow",
            "label": _("lost"),
        })

    # Actual leads
    leads = frappe.get_all(
        "Workspace Lead",
        {**({"branch": branch} if branch else {})},
        ["name", "lead_name", "status", "source", "budget_monthly",
         "interested_plan", "assigned_to"],
        order_by="creation desc",
        limit=60,
    )

    counts = {}
    for ld in leads:
        counts[ld["status"]] = counts.get(ld["status"], 0) + 1
        nodes.append({
            "id": f"ld-{ld['name']}",
            "label": ld.get("lead_name") or ld["name"],
            "type": _sc(ld["status"]),
            "doctype": "Workspace Lead",
            "docname": ld["name"],
            "badge": ld.get("source", ""),
            "meta": {
                "budget": flt(ld.get("budget_monthly")),
                "plan": ld.get("interested_plan"),
                "assigned": ld.get("assigned_to"),
            },
        })
        edges.append({
            "source": f"crm-stage-{ld['status'].replace(' ', '_')}",
            "target": f"ld-{ld['name']}",
            "type": "child",
        })

    # Update stage badges with counts
    for n in nodes:
        if n.get("meta", {}).get("is_stage"):
            status_key = n["id"].replace("crm-stage-", "").replace("_", " ")
            n["badge"] = str(counts.get(status_key, 0))
            n["summary"] = {"count": counts.get(status_key, 0)}

    return {"nodes": nodes, "edges": edges, "counts": counts}


# ═════════════════════════════════════════════════════════════════════
# 6. ONBOARDING DATA
# ═════════════════════════════════════════════════════════════════════


@frappe.whitelist()
def get_onboarding_data():
    """Summary data for the interactive onboarding storyboard."""
    frappe.only_for(["ARKSpace User", "ARKSpace Manager", "System Manager"])

    return {
        "total_spaces": frappe.db.count("Co-working Space") or 0,
        "total_members": frappe.db.count("Membership", {"docstatus": 1, "status": "Active"}) or 0,
        "total_branches": frappe.db.count("ARKSpace Branch", {"is_active": 1}) or 0,
        "total_plans": frappe.db.count("Membership Plan") or 0,
        "total_bookings": frappe.db.count("Space Booking", {"docstatus": 1}) or 0,
        "space_types": frappe.get_all("Space Type", pluck="type_name"),
        "branches": frappe.get_all(
            "ARKSpace Branch", {"is_active": 1}, ["name", "branch_name"],
        ),
        "plans": frappe.get_all(
            "Membership Plan", fields=["name", "plan_name", "plan_type", "monthly_price"],
            limit=10,
        ),
        "app_url": get_url(),
    }


# ═════════════════════════════════════════════════════════════════════
# 7. ENTITY DETAIL (for FloatingWindow content)
# ═════════════════════════════════════════════════════════════════════


@frappe.whitelist()
def get_entity_detail(doctype, docname):
    """Return formatted HTML detail card for any ARKSpace entity."""
    frappe.has_permission(doctype, "read", throw=True)
    doc = frappe.get_doc(doctype, docname)

    if doctype == "Co-working Space":
        return _space_detail(doc)
    if doctype == "Space Booking":
        return _booking_detail(doc)
    if doctype == "Customer":
        return _member_detail(doc)
    if doctype == "Membership":
        return _membership_detail(doc)
    if doctype == "Community Event":
        return _event_detail(doc)
    if doctype == "Workspace Lead":
        return _lead_detail(doc)

    # Generic fallback
    return _generic_detail(doc)


def _detail_card(title, icon, color, rows):
    """Build an HTML detail card."""
    rows_html = "".join(
        f'<div style="display:flex;justify-content:space-between;padding:4px 0;'
        f'border-bottom:1px solid var(--border-color)">'
        f'<span style="color:var(--text-muted)">{k}</span>'
        f'<strong>{v}</strong></div>'
        for k, v in rows
    )
    return (
        f'<div style="padding:12px">'
        f'<div style="font-size:24px;text-align:center;margin-bottom:8px">{icon}</div>'
        f'<div style="text-align:center;font-weight:700;font-size:15px;'
        f'color:{color};margin-bottom:12px">{title}</div>'
        f'{rows_html}'
        f'</div>'
    )


def _space_detail(doc):
    return _detail_card(
        doc.space_name or doc.name, "🏢", "#6366f1",
        [
            (_("Type"), doc.space_type or "—"),
            (_("Status"), doc.status or "—"),
            (_("Capacity"), str(doc.capacity or "—")),
            (_("Hourly Rate"), frappe.format_value(doc.hourly_rate, {"fieldtype": "Currency"})),
            (_("Daily Rate"), frappe.format_value(doc.daily_rate, {"fieldtype": "Currency"})),
            (_("Monthly Rate"), frappe.format_value(doc.monthly_rate, {"fieldtype": "Currency"})),
            (_("Current Member"), doc.current_member or "—"),
        ],
    )


def _booking_detail(doc):
    member_name = ""
    if doc.member:
        member_name = frappe.db.get_value("Customer", doc.member, "customer_name") or doc.member
    return _detail_card(
        doc.name, "📅", "#3b82f6",
        [
            (_("Space"), doc.space or "—"),
            (_("Member"), member_name or "—"),
            (_("Status"), doc.status or "—"),
            (_("Type"), doc.booking_type or "—"),
            (_("Start"), str(doc.start_datetime or "—")),
            (_("End"), str(doc.end_datetime or "—")),
            (_("Amount"), frappe.format_value(doc.total_amount, {"fieldtype": "Currency"})),
        ],
    )


def _member_detail(doc):
    active_mem = frappe.db.count("Membership", {
        "member": doc.name, "docstatus": 1, "status": "Active",
    })
    total_bookings = frappe.db.count("Space Booking", {
        "member": doc.name, "docstatus": 1,
    })
    return _detail_card(
        doc.customer_name or doc.name, "👤", "#10b981",
        [
            (_("Customer ID"), doc.name),
            (_("Active Memberships"), str(active_mem)),
            (_("Total Bookings"), str(total_bookings)),
            (_("Customer Type"), doc.customer_type or "—"),
            (_("Territory"), doc.territory or "—"),
        ],
    )


def _membership_detail(doc):
    return _detail_card(
        doc.name, "🎫", "#8b5cf6",
        [
            (_("Plan"), doc.membership_plan or "—"),
            (_("Status"), doc.status or "—"),
            (_("Member"), doc.member or "—"),
            (_("Start Date"), str(doc.start_date or "—")),
            (_("End Date"), str(doc.end_date or "—")),
            (_("Amount"), frappe.format_value(doc.net_amount, {"fieldtype": "Currency"})),
            (_("Branch"), doc.branch or "—"),
        ],
    )


def _event_detail(doc):
    return _detail_card(
        doc.event_name or doc.name, "🎉", "#f59e0b",
        [
            (_("Type"), doc.event_type or "—"),
            (_("Status"), doc.status or "—"),
            (_("Start"), str(doc.start_datetime or "—")),
            (_("End"), str(doc.end_datetime or "—")),
            (_("Attendees"), f"{doc.current_attendees or 0}/{doc.max_attendees or '∞'}"),
            (_("Fee"), _("Free") if doc.is_free else frappe.format_value(
                doc.fee, {"fieldtype": "Currency"},
            )),
        ],
    )


def _lead_detail(doc):
    return _detail_card(
        doc.lead_name or doc.name, "🎯", "#f97316",
        [
            (_("Status"), doc.status or "—"),
            (_("Source"), doc.source or "—"),
            (_("Budget"), frappe.format_value(doc.budget_monthly, {"fieldtype": "Currency"})),
            (_("Interested Plan"), doc.interested_plan or "—"),
            (_("Assigned To"), doc.assigned_to or "—"),
            (_("Team Size"), str(doc.team_size or "—")),
        ],
    )


def _generic_detail(doc):
    rows = []
    meta = frappe.get_meta(doc.doctype)
    for f in meta.fields[:10]:
        if f.fieldtype in ("Link", "Data", "Select", "Currency", "Int", "Date", "Datetime"):
            val = doc.get(f.fieldname)
            if val:
                rows.append((f.label or f.fieldname, str(val)))
    return _detail_card(
        str(doc.get("name")), "📋", "#6b7280", rows,
    )
