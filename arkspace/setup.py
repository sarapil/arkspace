# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

"""ARKSpace — Setup Workflows, Notifications & Dashboard Charts
إعداد سير العمل والإشعارات والرسوم البيانية
"""

import frappe
from frappe import _


# =============================================================================
# WORKFLOWS — سير العمل
# =============================================================================

def create_workflow_states():
    """Create Workflow State records if they don't exist."""
    states = [
        # Booking states
        {"name": "Pending", "style": "Warning"},
        {"name": "Confirmed", "style": "Primary"},
        {"name": "Checked In", "style": "Info"},
        {"name": "Completed", "style": "Success"},
        {"name": "Cancelled", "style": "Danger"},
        {"name": "No Show", "style": "Danger"},
        # Membership states
        {"name": "Draft", "style": ""},
        {"name": "Active", "style": "Success"},
        {"name": "Expired", "style": "Warning"},
        {"name": "Suspended", "style": "Danger"},
        # Lead states
        {"name": "New", "style": "Primary"},
        {"name": "Contacted", "style": "Info"},
        {"name": "Tour Scheduled", "style": "Warning"},
        {"name": "Negotiating", "style": "Primary"},
        {"name": "Converted", "style": "Success"},
        {"name": "Lost", "style": "Danger"},
    ]

    for state in states:
        if not frappe.db.exists("Workflow State", state["name"]):
            doc = frappe.new_doc("Workflow State")
            doc.workflow_state_name = state["name"]
            doc.style = state.get("style", "")
            try:
                doc.insert(ignore_permissions=True)
            except Exception:
                pass


def create_workflow_actions():
    """Create Workflow Action Master records."""
    actions = [
        "Confirm", "Check In", "Check Out", "Cancel", "Mark No Show",
        "Approve", "Activate", "Suspend", "Renew",
        "Contact", "Schedule Tour", "Negotiate", "Convert", "Mark Lost",
    ]

    for action in actions:
        if not frappe.db.exists("Workflow Action Master", action):
            doc = frappe.new_doc("Workflow Action Master")
            doc.workflow_action_name = action
            try:
                doc.insert(ignore_permissions=True)
            except Exception:
                pass


def create_booking_workflow():
    """Create Space Booking Workflow.
    Flow: Pending → Confirmed → Checked In → Completed
    """
    wf_name = "Space Booking Approval"

    if frappe.db.exists("Workflow", wf_name):
        frappe.delete_doc("Workflow", wf_name, force=True)

    wf = frappe.new_doc("Workflow")
    wf.workflow_name = wf_name
    wf.document_type = "Space Booking"
    wf.is_active = 1
    wf.override_status = 1
    wf.send_email_alert = 0

    # States
    wf.append("states", {
        "state": "Pending",
        "doc_status": "0",
        "update_field": "status",
        "update_value": "Pending",
        "allow_edit": "ARKSpace Front Desk",
    })
    wf.append("states", {
        "state": "Confirmed",
        "doc_status": "1",
        "update_field": "status",
        "update_value": "Confirmed",
        "allow_edit": "ARKSpace Manager",
    })
    wf.append("states", {
        "state": "Checked In",
        "doc_status": "1",
        "update_field": "status",
        "update_value": "Checked In",
        "allow_edit": "ARKSpace Front Desk",
    })
    wf.append("states", {
        "state": "Completed",
        "doc_status": "1",
        "update_field": "status",
        "update_value": "Checked Out",
        "allow_edit": "ARKSpace Manager",
    })
    wf.append("states", {
        "state": "Cancelled",
        "doc_status": "2",
        "update_field": "status",
        "update_value": "Cancelled",
        "allow_edit": "ARKSpace Manager",
        "is_optional_state": 1,
    })
    wf.append("states", {
        "state": "No Show",
        "doc_status": "1",
        "update_field": "status",
        "update_value": "No Show",
        "allow_edit": "ARKSpace Manager",
        "is_optional_state": 1,
    })

    # Transitions
    wf.append("transitions", {
        "state": "Pending",
        "action": "Confirm",
        "next_state": "Confirmed",
        "allowed": "ARKSpace Front Desk",
        "allow_self_approval": 1,
    })
    wf.append("transitions", {
        "state": "Pending",
        "action": "Confirm",
        "next_state": "Confirmed",
        "allowed": "ARKSpace Manager",
        "allow_self_approval": 1,
    })
    wf.append("transitions", {
        "state": "Confirmed",
        "action": "Check In",
        "next_state": "Checked In",
        "allowed": "ARKSpace Front Desk",
        "allow_self_approval": 1,
    })
    wf.append("transitions", {
        "state": "Confirmed",
        "action": "Cancel",
        "next_state": "Cancelled",
        "allowed": "ARKSpace Manager",
        "allow_self_approval": 1,
    })
    wf.append("transitions", {
        "state": "Confirmed",
        "action": "Mark No Show",
        "next_state": "No Show",
        "allowed": "ARKSpace Front Desk",
        "allow_self_approval": 1,
    })
    wf.append("transitions", {
        "state": "Checked In",
        "action": "Check Out",
        "next_state": "Completed",
        "allowed": "ARKSpace Front Desk",
        "allow_self_approval": 1,
    })

    wf.insert(ignore_permissions=True)
    return wf_name


def create_membership_workflow():
    """Create Membership Workflow.
    Flow: Draft → Active → Expired/Suspended/Cancelled
    """
    wf_name = "Membership Lifecycle"

    if frappe.db.exists("Workflow", wf_name):
        frappe.delete_doc("Workflow", wf_name, force=True)

    wf = frappe.new_doc("Workflow")
    wf.workflow_name = wf_name
    wf.document_type = "Membership"
    wf.is_active = 1
    wf.override_status = 1
    wf.send_email_alert = 0

    # States
    wf.append("states", {
        "state": "Draft",
        "doc_status": "0",
        "update_field": "status",
        "update_value": "Draft",
        "allow_edit": "ARKSpace Sales",
    })
    wf.append("states", {
        "state": "Active",
        "doc_status": "1",
        "update_field": "status",
        "update_value": "Active",
        "allow_edit": "ARKSpace Manager",
    })
    wf.append("states", {
        "state": "Suspended",
        "doc_status": "1",
        "update_field": "status",
        "update_value": "Suspended",
        "allow_edit": "ARKSpace Manager",
        "is_optional_state": 1,
    })
    wf.append("states", {
        "state": "Expired",
        "doc_status": "1",
        "update_field": "status",
        "update_value": "Expired",
        "allow_edit": "ARKSpace Admin",
        "is_optional_state": 1,
    })
    wf.append("states", {
        "state": "Cancelled",
        "doc_status": "2",
        "update_field": "status",
        "update_value": "Cancelled",
        "allow_edit": "ARKSpace Admin",
        "is_optional_state": 1,
    })

    # Transitions
    wf.append("transitions", {
        "state": "Draft",
        "action": "Activate",
        "next_state": "Active",
        "allowed": "ARKSpace Sales",
        "allow_self_approval": 1,
    })
    wf.append("transitions", {
        "state": "Draft",
        "action": "Activate",
        "next_state": "Active",
        "allowed": "ARKSpace Manager",
        "allow_self_approval": 1,
    })
    wf.append("transitions", {
        "state": "Active",
        "action": "Suspend",
        "next_state": "Suspended",
        "allowed": "ARKSpace Manager",
        "allow_self_approval": 1,
    })
    wf.append("transitions", {
        "state": "Active",
        "action": "Cancel",
        "next_state": "Cancelled",
        "allowed": "ARKSpace Admin",
        "allow_self_approval": 1,
    })
    wf.append("transitions", {
        "state": "Suspended",
        "action": "Activate",
        "next_state": "Active",
        "allowed": "ARKSpace Manager",
        "allow_self_approval": 1,
    })
    wf.append("transitions", {
        "state": "Suspended",
        "action": "Cancel",
        "next_state": "Cancelled",
        "allowed": "ARKSpace Admin",
        "allow_self_approval": 1,
    })
    wf.append("transitions", {
        "state": "Expired",
        "action": "Renew",
        "next_state": "Active",
        "allowed": "ARKSpace Sales",
        "allow_self_approval": 1,
    })

    wf.insert(ignore_permissions=True)
    return wf_name


def create_lead_workflow():
    """Create Workspace Lead Workflow.
    Flow: New → Contacted → Tour Scheduled → Negotiating → Converted/Lost
    """
    wf_name = "Lead Pipeline"

    if frappe.db.exists("Workflow", wf_name):
        frappe.delete_doc("Workflow", wf_name, force=True)

    wf = frappe.new_doc("Workflow")
    wf.workflow_name = wf_name
    wf.document_type = "Workspace Lead"
    wf.is_active = 1
    wf.override_status = 1
    wf.send_email_alert = 0

    # States
    for state_data in [
        {"state": "New", "doc_status": "0", "update_value": "New", "allow_edit": "ARKSpace Sales"},
        {"state": "Contacted", "doc_status": "0", "update_value": "Contacted", "allow_edit": "ARKSpace Sales"},
        {"state": "Tour Scheduled", "doc_status": "0", "update_value": "Tour Scheduled", "allow_edit": "ARKSpace Sales"},
        {"state": "Negotiating", "doc_status": "0", "update_value": "Negotiating", "allow_edit": "ARKSpace Sales"},
        {"state": "Converted", "doc_status": "0", "update_value": "Converted", "allow_edit": "ARKSpace Manager"},
        {"state": "Lost", "doc_status": "0", "update_value": "Lost", "allow_edit": "ARKSpace Manager", "is_optional_state": 1},
    ]:
        row = {
            "state": state_data["state"],
            "doc_status": state_data["doc_status"],
            "update_field": "status",
            "update_value": state_data["update_value"],
            "allow_edit": state_data["allow_edit"],
        }
        if state_data.get("is_optional_state"):
            row["is_optional_state"] = 1
        wf.append("states", row)

    # Transitions
    transitions = [
        ("New", "Contact", "Contacted", "ARKSpace Sales"),
        ("New", "Mark Lost", "Lost", "ARKSpace Manager"),
        ("Contacted", "Schedule Tour", "Tour Scheduled", "ARKSpace Sales"),
        ("Contacted", "Negotiate", "Negotiating", "ARKSpace Sales"),
        ("Contacted", "Mark Lost", "Lost", "ARKSpace Manager"),
        ("Tour Scheduled", "Negotiate", "Negotiating", "ARKSpace Sales"),
        ("Tour Scheduled", "Convert", "Converted", "ARKSpace Manager"),
        ("Tour Scheduled", "Mark Lost", "Lost", "ARKSpace Manager"),
        ("Negotiating", "Convert", "Converted", "ARKSpace Manager"),
        ("Negotiating", "Mark Lost", "Lost", "ARKSpace Manager"),
    ]

    for state, action, next_state, role in transitions:
        wf.append("transitions", {
            "state": state,
            "action": action,
            "next_state": next_state,
            "allowed": role,
            "allow_self_approval": 1,
        })

    wf.insert(ignore_permissions=True)
    return wf_name


# =============================================================================
# NOTIFICATIONS — الإشعارات
# =============================================================================

def create_booking_confirmation_notification():
    """Notification when a booking is submitted (confirmed)."""
    name = "ARKSpace - Booking Confirmation"

    if frappe.db.exists("Notification", name):
        frappe.delete_doc("Notification", name, force=True)

    n = frappe.new_doc("Notification")
    n.name = name
    n.enabled = 1
    n.is_standard = 1
    n.module = "ARKSpace Spaces"
    n.channel = "Email"
    n.send_system_notification = 1
    n.subject = _("Booking Confirmed — {{ doc.booking_id or doc.name }}")
    n.event = "Submit"
    n.document_type = "Space Booking"
    n.attach_print = 1
    n.print_format = "Booking Confirmation"
    n.message_type = "HTML"
    n.message = """<div style="font-family: 'Inter', sans-serif; max-width: 600px; margin: 0 auto;">
<div style="background: linear-gradient(135deg, #1B365D 0%, #2A4A7F 100%); color: #fff; padding: 24px 30px; border-radius: 12px 12px 0 0;">
    <h2 style="margin: 0; font-size: 20px;">✅ {{ _("Booking Confirmed") }}</h2>
    <p style="margin: 4px 0 0; opacity: 0.85; font-size: 13px;">{{ doc.booking_id or doc.name }}</p>
</div>
<div style="border-bottom: 4px solid #C4A962;"></div>
<div style="padding: 24px 30px; background: #fff; border: 1px solid #E5E7EB; border-top: none; border-radius: 0 0 12px 12px;">
    <p>{{ _("Dear") }} <strong>{{ doc.member_name or doc.member }}</strong>,</p>
    <p>{{ _("Your booking has been confirmed with the following details") }}:</p>
    <table style="width: 100%; border-collapse: collapse; margin: 16px 0;">
        <tr><td style="padding: 8px 0; color: #6B7280; width: 40%;">{{ _("Space") }}</td><td style="padding: 8px 0; font-weight: 600;">{{ doc.space }}</td></tr>
        <tr><td style="padding: 8px 0; color: #6B7280;">{{ _("Type") }}</td><td style="padding: 8px 0; font-weight: 600;">{{ doc.booking_type }}</td></tr>
        <tr><td style="padding: 8px 0; color: #6B7280;">{{ _("Start") }}</td><td style="padding: 8px 0; font-weight: 600;">{{ doc.get_formatted("start_datetime") }}</td></tr>
        <tr><td style="padding: 8px 0; color: #6B7280;">{{ _("End") }}</td><td style="padding: 8px 0; font-weight: 600;">{{ doc.get_formatted("end_datetime") }}</td></tr>
        <tr><td style="padding: 8px 0; color: #6B7280;">{{ _("Amount") }}</td><td style="padding: 8px 0; font-weight: 700; color: #1B365D; font-size: 16px;">{{ doc.get_formatted("net_amount") }}</td></tr>
    </table>
    <p style="color: #9CA3AF; font-size: 12px; margin-top: 20px;">ARKSpace — {{ _("Co-working Space Management") }}</p>
</div>
</div>"""

    n.append("recipients", {"receiver_by_document_field": "member_email"})
    n.insert(ignore_permissions=True)


def create_membership_welcome_notification():
    """Welcome notification when a new membership is activated."""
    name = "ARKSpace - Membership Welcome"

    if frappe.db.exists("Notification", name):
        frappe.delete_doc("Notification", name, force=True)

    n = frappe.new_doc("Notification")
    n.name = name
    n.enabled = 1
    n.is_standard = 1
    n.module = "ARKSpace Memberships"
    n.channel = "Email"
    n.send_system_notification = 1
    n.subject = _("Welcome to ARKSpace — {{ doc.membership_plan }}")
    n.event = "Submit"
    n.document_type = "Membership"
    n.attach_print = 1
    n.print_format = "Membership Card"
    n.message_type = "HTML"
    n.message = """<div style="font-family: 'Inter', sans-serif; max-width: 600px; margin: 0 auto;">
<div style="background: linear-gradient(135deg, #1B365D 0%, #0F1D33 100%); color: #fff; padding: 24px 30px; border-radius: 12px 12px 0 0;">
    <h2 style="margin: 0; font-size: 20px;">🎉 {{ _("Welcome to ARKSpace!") }}</h2>
    <p style="margin: 4px 0 0; opacity: 0.85; font-size: 13px;">{{ _("Your membership is now active") }}</p>
</div>
<div style="border-bottom: 4px solid #C4A962;"></div>
<div style="padding: 24px 30px; background: #fff; border: 1px solid #E5E7EB; border-top: none; border-radius: 0 0 12px 12px;">
    <p>{{ _("Dear") }} <strong>{{ doc.member_name or doc.member }}</strong>,</p>
    <p>{{ _("Your membership has been activated successfully") }}:</p>
    <table style="width: 100%; border-collapse: collapse; margin: 16px 0;">
        <tr><td style="padding: 8px 0; color: #6B7280; width: 40%;">{{ _("Plan") }}</td><td style="padding: 8px 0;"><span style="background: linear-gradient(135deg, #C4A962, #A38B4C); color: #1B365D; padding: 3px 12px; border-radius: 12px; font-weight: 700; font-size: 12px;">{{ doc.membership_plan }}</span></td></tr>
        <tr><td style="padding: 8px 0; color: #6B7280;">{{ _("Type") }}</td><td style="padding: 8px 0; font-weight: 600;">{{ doc.plan_type }}</td></tr>
        <tr><td style="padding: 8px 0; color: #6B7280;">{{ _("Period") }}</td><td style="padding: 8px 0; font-weight: 600;">{{ doc.get_formatted("start_date") }} — {{ doc.get_formatted("end_date") }}</td></tr>
        <tr><td style="padding: 8px 0; color: #6B7280;">{{ _("Billing Cycle") }}</td><td style="padding: 8px 0; font-weight: 600;">{{ doc.billing_cycle }}</td></tr>
        {% if doc.assigned_space %}<tr><td style="padding: 8px 0; color: #6B7280;">{{ _("Space") }}</td><td style="padding: 8px 0; font-weight: 600;">{{ doc.assigned_space }}</td></tr>{% endif %}
        {% if doc.initial_credits %}<tr><td style="padding: 8px 0; color: #6B7280;">{{ _("Credits") }}</td><td style="padding: 8px 0; font-weight: 700; color: #C4A962;">{{ doc.initial_credits }}</td></tr>{% endif %}
    </table>
    <p style="color: #9CA3AF; font-size: 12px; margin-top: 20px;">ARKSpace — {{ _("Co-working Space Management") }}</p>
</div>
</div>"""

    n.append("recipients", {"receiver_by_document_field": "member_email"})
    n.insert(ignore_permissions=True)


def create_membership_expiry_notification():
    """Notification sent 7 days before membership expiry."""
    name = "ARKSpace - Membership Expiry Reminder"

    if frappe.db.exists("Notification", name):
        frappe.delete_doc("Notification", name, force=True)

    n = frappe.new_doc("Notification")
    n.name = name
    n.enabled = 1
    n.is_standard = 1
    n.module = "ARKSpace Memberships"
    n.channel = "Email"
    n.send_system_notification = 1
    n.subject = _("Membership Expiring Soon — {{ doc.membership_plan }}")
    n.event = "Days Before"
    n.document_type = "Membership"
    n.date_changed = "end_date"
    n.days_in_advance = 7
    n.condition = "doc.docstatus == 1 and doc.status == 'Active'"
    n.message_type = "HTML"
    n.message = """<div style="font-family: 'Inter', sans-serif; max-width: 600px; margin: 0 auto;">
<div style="background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%); color: #fff; padding: 24px 30px; border-radius: 12px 12px 0 0;">
    <h2 style="margin: 0; font-size: 20px;">⏰ {{ _("Membership Expiring Soon") }}</h2>
    <p style="margin: 4px 0 0; opacity: 0.9; font-size: 13px;">{{ doc.name }}</p>
</div>
<div style="border-bottom: 4px solid #C4A962;"></div>
<div style="padding: 24px 30px; background: #fff; border: 1px solid #E5E7EB; border-top: none; border-radius: 0 0 12px 12px;">
    <p>{{ _("Dear") }} <strong>{{ doc.member_name or doc.member }}</strong>,</p>
    <p>{{ _("Your membership is expiring on") }} <strong>{{ doc.get_formatted("end_date") }}</strong>.</p>
    <div style="background: #FFFBEB; border: 1px solid #FDE68A; border-radius: 8px; padding: 14px 18px; margin: 16px 0;">
        <strong style="color: #92400E;">{{ _("Plan") }}:</strong> {{ doc.membership_plan }}<br>
        <strong style="color: #92400E;">{{ _("Auto Renew") }}:</strong> {{ _("Yes") if doc.auto_renew else _("No") }}
    </div>
    {% if not doc.auto_renew %}
    <p>{{ _("Please contact us to renew your membership and continue enjoying our services.") }}</p>
    {% else %}
    <p>{{ _("Your membership will be automatically renewed. No action is needed.") }}</p>
    {% endif %}
    <p style="color: #9CA3AF; font-size: 12px; margin-top: 20px;">ARKSpace — {{ _("Co-working Space Management") }}</p>
</div>
</div>"""

    n.append("recipients", {"receiver_by_document_field": "member_email"})
    n.insert(ignore_permissions=True)


def create_booking_cancelled_notification():
    """Notification when a booking is cancelled."""
    name = "ARKSpace - Booking Cancelled"

    if frappe.db.exists("Notification", name):
        frappe.delete_doc("Notification", name, force=True)

    n = frappe.new_doc("Notification")
    n.name = name
    n.enabled = 1
    n.is_standard = 1
    n.module = "ARKSpace Spaces"
    n.channel = "Email"
    n.send_system_notification = 1
    n.subject = _("Booking Cancelled — {{ doc.booking_id or doc.name }}")
    n.event = "Cancel"
    n.document_type = "Space Booking"
    n.message_type = "HTML"
    n.message = """<div style="font-family: 'Inter', sans-serif; max-width: 600px; margin: 0 auto;">
<div style="background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%); color: #fff; padding: 24px 30px; border-radius: 12px 12px 0 0;">
    <h2 style="margin: 0; font-size: 20px;">❌ {{ _("Booking Cancelled") }}</h2>
    <p style="margin: 4px 0 0; opacity: 0.85; font-size: 13px;">{{ doc.booking_id or doc.name }}</p>
</div>
<div style="border-bottom: 4px solid #C4A962;"></div>
<div style="padding: 24px 30px; background: #fff; border: 1px solid #E5E7EB; border-top: none; border-radius: 0 0 12px 12px;">
    <p>{{ _("Dear") }} <strong>{{ doc.member_name or doc.member }}</strong>,</p>
    <p>{{ _("Your booking has been cancelled") }}:</p>
    <table style="width: 100%; border-collapse: collapse; margin: 16px 0;">
        <tr><td style="padding: 8px 0; color: #6B7280; width: 40%;">{{ _("Space") }}</td><td style="padding: 8px 0; font-weight: 600;">{{ doc.space }}</td></tr>
        <tr><td style="padding: 8px 0; color: #6B7280;">{{ _("Start") }}</td><td style="padding: 8px 0; font-weight: 600;">{{ doc.get_formatted("start_datetime") }}</td></tr>
        <tr><td style="padding: 8px 0; color: #6B7280;">{{ _("End") }}</td><td style="padding: 8px 0; font-weight: 600;">{{ doc.get_formatted("end_datetime") }}</td></tr>
    </table>
    <p>{{ _("If you have any questions, please contact our front desk.") }}</p>
    <p style="color: #9CA3AF; font-size: 12px; margin-top: 20px;">ARKSpace — {{ _("Co-working Space Management") }}</p>
</div>
</div>"""

    n.append("recipients", {"receiver_by_document_field": "member_email"})
    n.insert(ignore_permissions=True)


# =============================================================================
# DASHBOARD CHARTS — الرسوم البيانية
# =============================================================================

def create_dashboard_charts():
    """Create Dashboard Charts for the ARKSpace workspace."""

    charts = [
        {
            "name": "ARKSpace - Monthly Bookings",
            "chart_name": "Monthly Bookings",
            "chart_type": "Count",
            "document_type": "Space Booking",
            "based_on": "start_datetime",
            "timespan": "Last Year",
            "time_interval": "Monthly",
            "timeseries": 1,
            "type": "Bar",
            "color": "#2563EB",
            "is_public": 1,
            "module": "ARKSpace Spaces",
            "filters_json": "[[\"Space Booking\",\"docstatus\",\"=\",\"1\"]]",
        },
        {
            "name": "ARKSpace - Revenue Trend",
            "chart_name": "Revenue Trend",
            "chart_type": "Sum",
            "document_type": "Space Booking",
            "based_on": "start_datetime",
            "value_based_on": "net_amount",
            "timespan": "Last Year",
            "time_interval": "Monthly",
            "timeseries": 1,
            "type": "Line",
            "color": "#C4A962",
            "is_public": 1,
            "module": "ARKSpace Spaces",
            "filters_json": "[[\"Space Booking\",\"docstatus\",\"=\",\"1\"]]",
        },
        {
            "name": "ARKSpace - Membership Distribution",
            "chart_name": "Membership Distribution",
            "chart_type": "Group By",
            "document_type": "Membership",
            "group_by_type": "Count",
            "group_by_based_on": "plan_type",
            "timespan": "Last Year",
            "time_interval": "Monthly",
            "timeseries": 0,
            "type": "Donut",
            "color": "#10B981",
            "is_public": 1,
            "module": "ARKSpace Memberships",
            "filters_json": "[[\"Membership\",\"docstatus\",\"=\",\"1\"],[\"Membership\",\"status\",\"=\",\"Active\"]]",
        },
        {
            "name": "ARKSpace - Space Utilization",
            "chart_name": "Space Utilization by Type",
            "chart_type": "Group By",
            "document_type": "Co-working Space",
            "group_by_type": "Count",
            "group_by_based_on": "status",
            "timespan": "Last Year",
            "time_interval": "Monthly",
            "timeseries": 0,
            "type": "Pie",
            "color": "#6366F1",
            "is_public": 1,
            "module": "ARKSpace Spaces",
            "filters_json": "[]",
        },
        {
            "name": "ARKSpace - Lead Pipeline",
            "chart_name": "Lead Pipeline",
            "chart_type": "Group By",
            "document_type": "Workspace Lead",
            "group_by_type": "Count",
            "group_by_based_on": "status",
            "timespan": "Last Year",
            "time_interval": "Monthly",
            "timeseries": 0,
            "type": "Bar",
            "color": "#1B365D",
            "is_public": 1,
            "module": "ARKSpace CRM",
            "filters_json": "[]",
        },
    ]

    for chart_data in charts:
        chart_name = chart_data.pop("name")
        if frappe.db.exists("Dashboard Chart", chart_name):
            continue

        chart = frappe.new_doc("Dashboard Chart")
        chart.update(chart_data)
        try:
            chart.insert(ignore_permissions=True, ignore_if_duplicate=True)
            # Rename to desired name
            if chart.name != chart_name:
                frappe.rename_doc("Dashboard Chart", chart.name, chart_name, force=True)
        except Exception:
            frappe.log_error(f"Error creating chart {chart_name}")


# =============================================================================
# CUSTOM FIELDS — حقول مخصصة لربط ERPNext
# =============================================================================

def create_custom_fields():
    """Create Custom Fields on Sales Invoice for ARKSpace integration.
    These fields link invoices back to Space Bookings and Memberships.
    """
    if not _erpnext_installed():
        return

    from frappe.custom.doctype.custom_field.custom_field import create_custom_fields as _create

    custom_fields = {
        "Sales Invoice": [
            {
                "fieldname": "arkspace_section",
                "fieldtype": "Section Break",
                "label": "ARKSpace",
                "insert_after": "remarks",
                "collapsible": 1,
            },
            {
                "fieldname": "arkspace_booking",
                "fieldtype": "Link",
                "label": "Space Booking",
                "options": "Space Booking",
                "insert_after": "arkspace_section",
                "read_only": 1,
                "no_copy": 1,
            },
            {
                "fieldname": "arkspace_membership",
                "fieldtype": "Link",
                "label": "Membership",
                "options": "Membership",
                "insert_after": "arkspace_booking",
                "read_only": 1,
                "no_copy": 1,
            },
        ]
    }

    _create(custom_fields, update=True)
    frappe.db.commit()


def _erpnext_installed():
    """Check if ERPNext is available."""
    try:
        return "erpnext" in frappe.get_installed_apps()
    except Exception:
        return False


# =============================================================================
# MAIN SETUP FUNCTION — دالة الإعداد الرئيسية
# =============================================================================

def setup_arkspace():
    """Main function to set up all workflows, notifications, and charts.
    Call this from bench console or after_install.
    """
    print("🔧 Setting up ARKSpace Workflows, Notifications & Charts...")

    print("  → Creating Workflow States...")
    create_workflow_states()

    print("  → Creating Workflow Actions...")
    create_workflow_actions()

    print("  → Creating Custom Fields for ERPNext integration...")
    create_custom_fields()

    print("  → Creating Space Booking Workflow...")
    create_booking_workflow()

    print("  → Creating Membership Lifecycle Workflow...")
    create_membership_workflow()

    print("  → Creating Lead Pipeline Workflow...")
    create_lead_workflow()

    print("  → Creating Booking Confirmation Notification...")
    create_booking_confirmation_notification()

    print("  → Creating Membership Welcome Notification...")
    create_membership_welcome_notification()

    print("  → Creating Membership Expiry Reminder...")
    create_membership_expiry_notification()

    print("  → Creating Booking Cancelled Notification...")
    create_booking_cancelled_notification()

    print("  → Creating Dashboard Charts...")
    create_dashboard_charts()

    frappe.db.commit()
    print("✅ ARKSpace setup complete!")
