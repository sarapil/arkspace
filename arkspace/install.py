"""
ARKSpace Installation Hooks
تثبيت التطبيق — إنشاء الأدوار والإعدادات الأولية
"""

import frappe
from frappe import _


def after_install():
    """Post-installation setup."""
    _create_roles()
    _create_default_space_types()
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
