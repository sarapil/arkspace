# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

"""ARKSpace — Version Compatibility Utilities
أدوات التوافق بين الإصدارات

Provides helper functions that abstract Frappe v15/v16 API differences,
so the rest of the codebase can remain clean and version-agnostic.
"""

import frappe


def get_frappe_major_version():
    """Return the major version number of the installed Frappe framework."""
    try:
        return int(frappe.__version__.split(".")[0])
    except Exception:
        return 15


def is_v16_or_later():
    """Check if running on Frappe v16 or later."""
    return get_frappe_major_version() >= 16


def desk_route():
    """Return the desk route prefix — /desk for v16+, /app for v15.

    Usage::

        from arkspace.utils.compat import desk_route
        url = f"{desk_route()}/sales-invoice/{name}"
    """
    return "/desk" if is_v16_or_later() else "/app"


def doc_link(doctype, name, label=None):
    """Return an HTML link to a document that works on both v15 and v16.

    Args:
        doctype: e.g. "Sales Invoice"
        name: Document name
        label: Display text (defaults to name)

    Returns:
        HTML anchor string
    """
    slug = doctype.lower().replace(" ", "-")
    route = desk_route()
    display = label or name
    return f'<a href="{route}/{slug}/{name}">{display}</a>'
