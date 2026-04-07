# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

"""
ARKSpace Installation Hooks
"""

import frappe
from frappe import _


def after_install(app_name=None):
    """Post-installation setup."""
    _create_roles()
    _create_default_space_types()
    # ── Desktop Icon injection (Frappe v16 /desk) ──
    from arkspace.desktop_utils import inject_app_desktop_icon
    inject_app_desktop_icon(
        app="arkspace",
        label="ARKSpace",
        route="/desk/arkspace",
        logo_url="/assets/arkspace/images/arkspace-logo.svg",
        bg_color="#1B365D",
    )
    frappe.db.commit()

    # Run full setup (workflows, notifications, charts)
    from arkspace.setup import setup_arkspace
    setup_arkspace()

    # Seed sample data in developer mode
    if frappe.conf.get("developer_mode"):
        try:
            from arkspace.seed_arkspace import run as seed_data
            seed_data()
            frappe.db.commit()
        except Exception as e:
            frappe.log_error(f"ARKSpace seed data error: {e}", "ARKSpace Install")
            print(f"⚠️  Sample data seeding skipped: {e}")


def before_uninstall(app_name=None):
    """v16: Cleanup before app uninstall — remove custom fields and fixtures."""
    _remove_custom_fields()
    _remove_fixtures()


def _remove_custom_fields():
    """Remove Custom Fields added by ARKSpace on Sales Invoice."""
    for fieldname in ("arkspace_section", "arkspace_booking", "arkspace_membership"):
        if frappe.db.exists("Custom Field", {"dt": "Sales Invoice", "fieldname": fieldname}):
            frappe.delete_doc("Custom Field", f"Sales Invoice-{fieldname}", force=True)


def _remove_fixtures():
    """Remove workflows, notifications, charts created by ARKSpace."""
    for wf in ("Space Booking Approval", "Membership Lifecycle", "Lead Pipeline"):
        if frappe.db.exists("Workflow", wf):
            frappe.delete_doc("Workflow", wf, force=True)

    for chart in frappe.get_all("Dashboard Chart", filters={"name": ["like", "ARKSpace%"]}, pluck="name"):
        frappe.delete_doc("Dashboard Chart", chart, force=True)

    for notif in frappe.get_all("Notification", filters={"name": ["like", "ARKSpace%"]}, pluck="name"):
        frappe.delete_doc("Notification", notif, force=True)


def _create_roles():
    """Create ARKSpace-specific roles."""
    roles = [
        "ARKSpace Admin",
        "ARKSpace Manager",
        "ARKSpace Sales",
        "ARKSpace Operations",
        "ARKSpace Front Desk",
        "ARKSpace Member",
        "ARKSpace Viewer",
    ]
    for role_name in roles:
        if not frappe.db.exists("Role", role_name):
            frappe.get_doc({"doctype": "Role", "role_name": role_name}).insert(ignore_permissions=True)


def _create_default_space_types():
    """Create default space types if module is ready."""
    # Will be populated after Space Type doctype is migrated
    pass
