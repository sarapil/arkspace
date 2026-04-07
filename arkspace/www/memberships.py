# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

import frappe
from frappe import _

def get_context(context):
	"""Membership Management Portal Page"""
	if frappe.session.user == "Guest":
		frappe.throw(_("Please login to access your memberships"), frappe.PermissionError)

	member = _get_member_for_user()
	if not member:
		context.no_member = True
		context.title = _("My Memberships")
		return

	from arkspace.arkspace_memberships.api import (
		get_active_memberships,
		get_membership_plans,
		get_wallet_balance,
	)

	context.title = _("My Memberships")
	context.member = member
	context.member_name = frappe.db.get_value("Customer", member, "customer_name")

	# All memberships (active + expired)
	context.active_memberships = get_active_memberships(member)

	expired = frappe.get_all(
		"Membership",
		filters={"docstatus": 1, "member": member, "status": ["in", ["Expired", "Cancelled"]]},
		fields=[
			"name", "membership_plan", "plan_type", "billing_cycle",
			"start_date", "end_date", "net_amount", "status",
		],
		order_by="end_date desc",
		limit=10,
	)
	context.expired_memberships = expired

	# Available plans for upgrade
	context.plans = get_membership_plans()

	# Wallet
	context.wallet = get_wallet_balance(member)

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
