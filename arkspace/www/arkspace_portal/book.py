import frappe
from frappe import _


def get_context(context):
	"""صفحة حجز المساحات — Space Booking Page"""
	if frappe.session.user == "Guest":
		frappe.throw(_("Please login to book a space"), frappe.PermissionError)

	from arkspace.arkspace_spaces.api import get_available_spaces

	space_type = frappe.form_dict.get("space_type")
	branch = frappe.form_dict.get("branch")

	context.title = _("Book a Space — ARKSpace")
	context.spaces = get_available_spaces(space_type=space_type, branch=branch)
	context.space_types = frappe.get_all("Space Type", pluck="name", order_by="type_name asc")
	context.branches = frappe.get_all("Branch", pluck="name", order_by="name asc")
	context.selected_type = space_type
	context.selected_branch = branch
