# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

"""
نظام الأيقونات — ARKSpace Icon System
Font Awesome 6 icon mappings for all modules.
"""

ICONS = {
    # Navigation Icons — أيقونات التنقل
    "dashboard": "fa-solid fa-gauge-high",
    "home": "fa-solid fa-house",
    "settings": "fa-solid fa-gear",
    "menu": "fa-solid fa-bars",
    "back": "fa-solid fa-arrow-right",
    "forward": "fa-solid fa-arrow-left",

    # Module Icons — أيقونات الوحدات
    "spaces": "fa-solid fa-building",
    "bookings": "fa-solid fa-calendar-check",
    "memberships": "fa-solid fa-id-card",
    "members": "fa-solid fa-users",
    "leads": "fa-solid fa-user-plus",
    "sales": "fa-solid fa-chart-line",
    "marketing": "fa-solid fa-bullhorn",
    "finance": "fa-solid fa-coins",
    "hr": "fa-solid fa-user-tie",
    "reports": "fa-solid fa-chart-bar",
    "support": "fa-solid fa-headset",
    "voip": "fa-solid fa-phone",
    "iot": "fa-solid fa-microchip",

    # Action Icons — أيقونات الأفعال
    "add": "fa-solid fa-plus",
    "edit": "fa-solid fa-pen",
    "delete": "fa-solid fa-trash",
    "save": "fa-solid fa-floppy-disk",
    "cancel": "fa-solid fa-xmark",
    "search": "fa-solid fa-magnifying-glass",
    "filter": "fa-solid fa-filter",
    "export": "fa-solid fa-download",
    "import": "fa-solid fa-upload",
    "print": "fa-solid fa-print",
    "share": "fa-solid fa-share-nodes",
    "copy": "fa-solid fa-copy",
    "refresh": "fa-solid fa-rotate",
    "expand": "fa-solid fa-expand",
    "collapse": "fa-solid fa-compress",

    # Status Icons — أيقونات الحالات
    "success": "fa-solid fa-circle-check",
    "warning": "fa-solid fa-triangle-exclamation",
    "error": "fa-solid fa-circle-xmark",
    "info": "fa-solid fa-circle-info",
    "pending": "fa-solid fa-clock",
    "active": "fa-solid fa-circle-play",
    "inactive": "fa-solid fa-circle-pause",
    "verified": "fa-solid fa-badge-check",

    # Business Icons — أيقونات العمل
    "invoice": "fa-solid fa-file-invoice-dollar",
    "payment": "fa-solid fa-credit-card",
    "contract": "fa-solid fa-file-signature",
    "receipt": "fa-solid fa-receipt",
    "wallet": "fa-solid fa-wallet",
    "discount": "fa-solid fa-percent",
    "offer": "fa-solid fa-tag",

    # Communication Icons — أيقونات التواصل
    "email": "fa-solid fa-envelope",
    "phone_call": "fa-solid fa-phone-volume",
    "whatsapp": "fa-brands fa-whatsapp",
    "sms": "fa-solid fa-comment-sms",
    "video_call": "fa-solid fa-video",
    "meeting": "fa-solid fa-people-group",

    # Rating Icons — أيقونات التقييم
    "star_full": "fa-solid fa-star",
    "star_half": "fa-solid fa-star-half-stroke",
    "star_empty": "fa-regular fa-star",
    "thumbs_up": "fa-solid fa-thumbs-up",
    "thumbs_down": "fa-solid fa-thumbs-down",
    "heart": "fa-solid fa-heart",

    # Amenity Icons — أيقونات المرافق
    "wifi": "fa-solid fa-wifi",
    "parking": "fa-solid fa-square-parking",
    "coffee": "fa-solid fa-mug-hot",
    "printer": "fa-solid fa-print",
    "projector": "fa-solid fa-display",
    "ac": "fa-solid fa-snowflake",
    "locker": "fa-solid fa-lock",
    "kitchen": "fa-solid fa-utensils",
    "shower": "fa-solid fa-shower",
    "gym": "fa-solid fa-dumbbell",
    "prayer_room": "fa-solid fa-mosque",

    # Environment Icons — أيقونات البيئة (ARKAMOR)
    "temperature": "fa-solid fa-temperature-half",
    "humidity": "fa-solid fa-droplet",
    "co2": "fa-solid fa-cloud",
    "noise": "fa-solid fa-volume-high",
    "light": "fa-solid fa-lightbulb",
    "air_quality": "fa-solid fa-wind",

    # Badge Icons — أيقونات الشارات
    "badge_gold": "fa-solid fa-medal",
    "badge_certified": "fa-solid fa-certificate",
    "badge_top_rated": "fa-solid fa-trophy",
    "badge_new": "fa-solid fa-sparkles",
    "badge_eco": "fa-solid fa-leaf",
}


def get_icon(name: str, color: str = None, size: str = "md") -> str:
    """
    الحصول على HTML للأيقونة
    Get icon HTML with optional color and size.

    Args:
        name: Icon name from ICONS dict
        color: CSS color value
        size: sm, md, lg, xl
    """
    icon_class = ICONS.get(name, "fa-solid fa-circle-question")

    size_classes = {"sm": "fa-sm", "md": "", "lg": "fa-lg", "xl": "fa-2x"}
    size_class = size_classes.get(size, "")
    style = f' style="color: {color};"' if color else ""

    return f'<i class="{icon_class} {size_class}"{style}></i>'
