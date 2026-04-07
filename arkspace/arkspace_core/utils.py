# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

"""
"""

import frappe
from frappe import _

def get_arkspace_settings():
    """
    Get ARKSpace Settings singleton.
    """
    return frappe.get_single("ARKSpace Settings")

def get_default_currency() -> str:
    """Get default currency from settings."""
    settings = get_arkspace_settings()
    return settings.default_currency or "AED"

def is_feature_enabled(feature: str) -> bool:
    """
    Check if a feature is enabled in settings.

    Args:
        feature: voip, arkamor, arkanoor, ai
    """
    settings = get_arkspace_settings()
    field_map = {
        "voip": "enable_voip",
        "arkamor": "enable_arkamor",
        "arkanoor": "enable_arkanoor",
        "ai": "enable_ai",
    }
    field = field_map.get(feature)
    if field:
        return bool(getattr(settings, field, 0))
    return False

def standard_response(success: bool, data=None, message: str = "", errors: list = None) -> dict:
    """
    Standardized API response format.
    """
    return {
        "success": success,
        "data": data,
        "message": message,
        "errors": errors or [],
    }
