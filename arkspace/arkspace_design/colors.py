# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

"""
لوحة الألوان — ARKSpace Color Palette
Centralized color definitions for the entire ARKSpace ecosystem.
"""

COLORS = {
    # Primary Colors — الألوان الأساسية
    "navy": "#1B365D",
    "gold": "#C4A962",

    # Action Colors — ألوان الأفعال
    "action_primary": "#2563EB",
    "action_success": "#10B981",
    "action_warning": "#F59E0B",
    "action_danger": "#EF4444",
    "action_info": "#6366F1",

    # Link Colors — ألوان الروابط
    "link_default": "#2563EB",
    "link_hover": "#1D4ED8",
    "link_visited": "#7C3AED",
    "link_active": "#1E40AF",

    # Button Colors — ألوان الأزرار
    "btn_primary": "#2563EB",
    "btn_primary_hover": "#1D4ED8",
    "btn_secondary": "#6B7280",
    "btn_secondary_hover": "#4B5563",
    "btn_success": "#10B981",
    "btn_danger": "#EF4444",
    "btn_gold": "#C4A962",

    # Background Colors — ألوان الخلفية
    "bg_primary": "#FFFFFF",
    "bg_secondary": "#F8FAFC",
    "bg_tertiary": "#F1F5F9",
    "bg_dark": "#1B365D",

    # Text Colors — ألوان النصوص
    "text_primary": "#1F2937",
    "text_secondary": "#6B7280",
    "text_muted": "#9CA3AF",
    "text_inverse": "#FFFFFF",

    # Status Colors — ألوان الحالات
    "status_active": "#10B981",
    "status_pending": "#F59E0B",
    "status_cancelled": "#EF4444",
    "status_draft": "#6B7280",
    "status_completed": "#2563EB",

    # Badge Colors — ألوان الشارات
    "badge_gold": "#C4A962",
    "badge_silver": "#9CA3AF",
    "badge_bronze": "#B45309",
    "badge_new": "#8B5CF6",
}


def get_color(name: str, default: str = "#6B7280") -> str:
    """Jinja helper — get a named color from the palette.

    Usage in templates:
        {{ get_color("navy") }}
    """
    return COLORS.get(name, default)
