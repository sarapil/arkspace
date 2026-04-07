# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

import frappe
from frappe import _

def get_context(context):
	"""Member Self-Registration Page"""
	context.title = _("Join ARKSpace")
	context.no_cache = 1

	# If already logged in, redirect to portal
	if frappe.session.user != "Guest":
		context.logged_in = True
		context.redirect_url = "/arkspace_portal"

	# Load plans for selection
	context.plans = frappe.get_all(
		"Membership Plan",
		filters={"is_active": 1},
		fields=[
			"name", "plan_name", "plan_name_ar", "plan_type",
			"monthly_price", "quarterly_price", "yearly_price",
			"currency", "included_hours", "included_credits",
		],
		order_by="monthly_price asc",
	)
