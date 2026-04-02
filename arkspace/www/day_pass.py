# Copyright (c) 2026, ARKSpace Team and contributors
# For license information, please see license.txt

"""Day Pass Portal — Context Builder
تصريح اليوم — بوابة العملاء
"""

import frappe
from frappe.utils import nowdate


def get_context(context):
    """Build context for the Day Pass portal page."""
    context.no_cache = 1
    context.title = "Day Pass"

    # Available spaces
    context.spaces = frappe.get_all(
        "Co-working Space",
        filters={"status": ["in", ["Available", "Reserved"]]},
        fields=[
            "name", "space_name", "space_type", "hourly_rate",
            "daily_rate", "capacity", "main_image",
        ],
        order_by="space_name asc",
    )

    # Pass types with default pricing
    context.pass_types = [
        {"type": "Full Day", "label": "Full Day / يوم كامل"},
        {"type": "Half Day", "label": "Half Day / نصف يوم"},
        {"type": "Hourly", "label": "Hourly / بالساعة"},
        {"type": "Evening", "label": "Evening / مسائي"},
        {"type": "Weekend", "label": "Weekend / عطلة نهاية الأسبوع"},
    ]

    # Trial plans (if any)
    context.trial_plans = frappe.get_all(
        "Membership Plan",
        filters={"enable_trial": 1},
        fields=["name", "plan_name", "trial_days", "trial_price", "plan_type"],
    )

    context.today = nowdate()
    context.logged_in = frappe.session.user != "Guest"
