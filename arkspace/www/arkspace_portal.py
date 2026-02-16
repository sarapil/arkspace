import frappe
from frappe import _


def get_context(context):
	"""بوابة الأعضاء — Member Portal Dashboard"""
	if frappe.session.user == "Guest":
		frappe.throw(_("Please login to access the member portal"), frappe.PermissionError)

	# Find Customer linked to this user
	member = _get_member_for_user()
	if not member:
		context.no_membership = True
		context.title = _("ARKSpace — Member Portal")
		return

	# Use the memberships API
	from arkspace.arkspace_memberships.api import get_member_dashboard
	dashboard = get_member_dashboard(member)

	context.title = _("ARKSpace — Member Portal")
	context.member = member
	context.member_name = frappe.db.get_value("Customer", member, "customer_name")
	context.memberships = dashboard.get("memberships", [])
	context.recent_bookings = dashboard.get("recent_bookings", [])
	context.upcoming_bookings = dashboard.get("upcoming_bookings", [])
	context.wallet = dashboard.get("wallet", {})
	context.stats = dashboard.get("stats", {})


def _get_member_for_user():
	"""Find Customer linked to the current user via Dynamic Link."""
	customer = frappe.db.get_value(
		"Dynamic Link",
		{"parenttype": "Contact", "link_doctype": "Customer", "parent": ["in",
			frappe.get_all("Contact", filters={"user": frappe.session.user}, pluck="name")
		]},
		"link_name",
	)
	if not customer:
		# Fallback: check if Customer has email matching user
		customer = frappe.db.get_value("Customer", {"email_id": frappe.session.user}, "name")
	return customer
