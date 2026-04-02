import frappe
from frappe import _


def get_context(context):
	"""سجل المدفوعات — Payment History Portal Page"""
	if frappe.session.user == "Guest":
		frappe.throw(_("Please login to view your payments"), frappe.PermissionError)

	member = _get_member_for_user()
	if not member:
		context.no_member = True
		context.title = _("My Payments")
		return

	from arkspace.arkspace_memberships.api import get_payment_history

	context.title = _("My Payments")
	context.member = member
	context.member_name = frappe.db.get_value("Customer", member, "customer_name")

	history = get_payment_history(member, limit=50)
	context.invoices = history.get("invoices", [])
	context.online_payments = history.get("online_payments", [])
	context.summary = history.get("summary", {})


def _get_member_for_user():
	"""Find Customer linked to the current user."""
	contacts = frappe.get_all("Contact", filters={"user": frappe.session.user}, pluck="name")
	if contacts:
		customer = frappe.db.get_value(
			"Dynamic Link",
			{"parenttype": "Contact", "link_doctype": "Customer", "parent": ["in", contacts]},
			"link_name",
		)
		if customer:
			return customer
	return frappe.db.get_value("Customer", {"email_id": frappe.session.user}, "name")
