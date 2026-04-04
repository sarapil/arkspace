# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

"""ARKSpace — Permission Controllers
التحكم في الصلاحيات

Controls row-level security for ARKSpace DocTypes based on user roles.
"""

import frappe


def has_space_permission(doc, ptype="read", user=None):
    """Permission check for Co-working Space.

    - System Manager / ARKSpace Admin: full access
    - ARKSpace Manager / Operations: read all spaces
    - ARKSpace Front Desk: read all spaces
    - ARKSpace Member: read only if assigned via membership
    """
    if not user:
        user = frappe.session.user

    if user == "Administrator":
        return True

    roles = frappe.get_roles(user)

    # Full access roles
    if any(r in roles for r in ("System Manager", "ARKSpace Admin", "ARKSpace Manager", "ARKSpace Operations", "ARKSpace Front Desk")):
        return True

    # Members can see their assigned spaces
    if "ARKSpace Member" in roles:
        customer = _get_customer_for_user(user)
        if customer and ptype == "read":
            if doc.current_member == customer:
                return True
            # Also check if they have an active membership with this space
            has_membership = frappe.db.exists("Membership", {
                "member": customer,
                "assigned_space": doc.name,
                "docstatus": 1,
                "status": "Active",
            })
            if has_membership:
                return True

    return False


def get_space_conditions(user=None):
    """Query conditions for Co-working Space list views.

    Returns SQL WHERE clause to filter visible records.
    """
    if not user:
        user = frappe.session.user

    if user == "Administrator":
        return ""

    roles = frappe.get_roles(user)

    # Admin/Manager/Ops/FrontDesk see everything
    if any(r in roles for r in ("System Manager", "ARKSpace Admin", "ARKSpace Manager", "ARKSpace Operations", "ARKSpace Front Desk")):
        return ""

    # Members see only their assigned spaces
    if "ARKSpace Member" in roles:
        customer = _get_customer_for_user(user)
        if customer:
            return f"""((`tabCo-working Space`.current_member = {frappe.db.escape(customer)})
                OR (`tabCo-working Space`.name IN (
                    SELECT assigned_space FROM `tabMembership`
                    WHERE member = {frappe.db.escape(customer)}
                    AND docstatus = 1 AND status = 'Active'
                )))"""

    return "1=0"


def has_booking_permission(doc, ptype="read", user=None):
    """Permission check for Space Booking.

    - System Manager / ARKSpace Admin / Manager: full access
    - ARKSpace Front Desk: read/write all bookings
    - ARKSpace Member: read only their own bookings
    """
    if not user:
        user = frappe.session.user

    if user == "Administrator":
        return True

    roles = frappe.get_roles(user)

    if any(r in roles for r in ("System Manager", "ARKSpace Admin", "ARKSpace Manager", "ARKSpace Front Desk")):
        return True

    if "ARKSpace Member" in roles:
        customer = _get_customer_for_user(user)
        if customer and doc.member == customer:
            return True

    return False


def get_booking_conditions(user=None):
    """Query conditions for Space Booking list views."""
    if not user:
        user = frappe.session.user

    if user == "Administrator":
        return ""

    roles = frappe.get_roles(user)

    if any(r in roles for r in ("System Manager", "ARKSpace Admin", "ARKSpace Manager", "ARKSpace Front Desk")):
        return ""

    if "ARKSpace Member" in roles:
        customer = _get_customer_for_user(user)
        if customer:
            return f"`tabSpace Booking`.member = {frappe.db.escape(customer)}"

    return "1=0"


def has_membership_permission(doc, ptype="read", user=None):
    """Permission check for Membership.

    - System Manager / ARKSpace Admin / Manager / Sales: full access
    - ARKSpace Front Desk: read all memberships
    - ARKSpace Member: read only their own membership
    """
    if not user:
        user = frappe.session.user

    if user == "Administrator":
        return True

    roles = frappe.get_roles(user)

    if any(r in roles for r in ("System Manager", "ARKSpace Admin", "ARKSpace Manager", "ARKSpace Sales")):
        return True

    if "ARKSpace Front Desk" in roles and ptype == "read":
        return True

    if "ARKSpace Member" in roles:
        customer = _get_customer_for_user(user)
        if customer and doc.member == customer:
            return True

    return False


def get_membership_conditions(user=None):
    """Query conditions for Membership list views."""
    if not user:
        user = frappe.session.user

    if user == "Administrator":
        return ""

    roles = frappe.get_roles(user)

    if any(r in roles for r in ("System Manager", "ARKSpace Admin", "ARKSpace Manager", "ARKSpace Sales", "ARKSpace Front Desk")):
        return ""

    if "ARKSpace Member" in roles:
        customer = _get_customer_for_user(user)
        if customer:
            return f"`tabMembership`.member = {frappe.db.escape(customer)}"

    return "1=0"


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _get_customer_for_user(user):
    """Resolve user email to Customer name via Dynamic Link.

    Looks for Customer linked via Contact → Dynamic Link.
    """
    customer = frappe.db.get_value(
        "Dynamic Link",
        filters={
            "link_doctype": "Customer",
            "parenttype": "Contact",
            "parent": ["in", frappe.get_all(
                "Contact",
                filters={"email_id": user},
                pluck="name",
                limit=5,
            )],
        },
        fieldname="link_name",
    )
    return customer


def has_app_permission():
    """Check if the current user has permission to access the ARKSpace app.

    Returns True for any user with an ARKSpace role or System Manager.
    Used by add_to_apps_screen in hooks.py.
    """
    user = frappe.session.user
    if user == "Administrator":
        return True

    roles = frappe.get_roles(user)
    arkspace_roles = {
        "System Manager",
        "ARKSpace Admin",
        "ARKSpace Manager",
        "ARKSpace Operations",
        "ARKSpace Front Desk",
        "ARKSpace Member",
    }
    return bool(arkspace_roles & set(roles))
