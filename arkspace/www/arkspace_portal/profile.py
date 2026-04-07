# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

import frappe
from frappe import _

def get_context(context):
	"""Member Profile Page"""
	if frappe.session.user == "Guest":
		frappe.throw(_("Please login to view your profile"), frappe.PermissionError)

	context.title = _("My Profile — ARKSpace")
	context.user_doc = frappe.get_doc("User", frappe.session.user)
	context.user_name = context.user_doc.full_name
	context.email = context.user_doc.email
	context.mobile_no = context.user_doc.mobile_no
	context.user_image = context.user_doc.user_image

	# Try to find linked Customer
	from arkspace.www.arkspace_portal import _get_member_for_user
	member = _get_member_for_user()
	if member:
		context.member = member
		context.member_doc = frappe.get_doc("Customer", member)
	else:
		context.member = None
		context.member_doc = None
