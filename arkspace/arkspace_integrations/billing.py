# Copyright (c) 2026, ARKSpace Team and contributors
# For license information, please see license.txt

"""ARKSpace Integrations — ERPNext Billing Bridge
جسر الفوترة — ربط الحجوزات والاشتراكات بالفواتير

Automatically creates Sales Invoices when Space Bookings or Memberships
are submitted, and handles payment reconciliation.
"""

import frappe
from frappe import _
from frappe.utils import flt, getdate, nowdate

# ─────────────────── Sales Invoice from Space Booking ────────────────────

def on_booking_submit(doc, method):
	"""Create a Sales Invoice when a Space Booking is submitted."""
	if not _erpnext_installed():
		return
	if doc.flags.skip_invoice:
		return

	# Check if invoice already exists
	if frappe.db.exists("Sales Invoice", {"arkspace_booking": doc.name, "docstatus": ["!=", 2]}):
		return

	customer = _resolve_customer(doc.member)
	if not customer:
		frappe.msgprint(
			_("No linked Customer found for {0}. Sales Invoice was not created.").format(doc.member),
			alert=True,
		)
		return

	si = frappe.new_doc("Sales Invoice")
	si.customer = customer
	si.posting_date = getdate(nowdate())
	si.due_date = getdate(nowdate())
	si.arkspace_booking = doc.name
	si.set_posting_time = 1
	si.remarks = _("Auto-generated from Space Booking {0}").format(doc.name)

	# Determine item and rate
	item = _get_or_create_service_item("Space Booking", _("Co-Working Space Booking"))
	hours = flt(doc.duration_hours, 2) or 1

	si.append("items", {
		"item_code": item,
		"qty": hours if doc.booking_type == "Hourly" else 1,
		"rate": flt(doc.net_amount) / (hours if doc.booking_type == "Hourly" and hours else 1),
		"description": _("{0} — {1} ({2})").format(
			doc.space, doc.booking_type, doc.name
		),
	})

	# Apply discount
	if flt(doc.discount_percent) > 0:
		si.additional_discount_percentage = flt(doc.discount_percent)

	si.flags.ignore_permissions = True
	si.insert()
	si.submit()

	frappe.msgprint(
		_("Sales Invoice {0} created for booking {1}").format(
			f'<a href="{_desk_route()}/sales-invoice/{si.name}">{si.name}</a>',
			doc.name,
		),
		alert=True,
	)


def on_booking_cancel(doc, method):
	"""Cancel linked Sales Invoice when a Space Booking is cancelled."""
	if not _erpnext_installed():
		return

	invoices = frappe.get_all(
		"Sales Invoice",
		filters={"arkspace_booking": doc.name, "docstatus": 1},
		pluck="name",
	)
	for inv_name in invoices:
		inv = frappe.get_doc("Sales Invoice", inv_name)
		inv.flags.ignore_permissions = True
		inv.cancel()
		frappe.msgprint(
			_("Sales Invoice {0} cancelled").format(inv_name),
			alert=True,
		)


# ─────────────────── Sales Invoice from Membership ───────────────────────

def on_membership_submit(doc, method):
	"""Create a Sales Invoice when a Membership is submitted."""
	if not _erpnext_installed():
		return
	if doc.flags.skip_invoice:
		return

	if frappe.db.exists("Sales Invoice", {"arkspace_membership": doc.name, "docstatus": ["!=", 2]}):
		return

	customer = _resolve_customer(doc.member)
	if not customer:
		frappe.msgprint(
			_("No linked Customer for {0}. Invoice not created.").format(doc.member),
			alert=True,
		)
		return

	si = frappe.new_doc("Sales Invoice")
	si.customer = customer
	si.posting_date = getdate(nowdate())
	si.due_date = getdate(nowdate())
	si.arkspace_membership = doc.name
	si.set_posting_time = 1
	si.remarks = _("Auto-generated from Membership {0}").format(doc.name)

	item = _get_or_create_service_item("Membership Fee", _("Co-Working Membership Fee"))

	si.append("items", {
		"item_code": item,
		"qty": 1,
		"rate": flt(doc.net_amount),
		"description": _("Membership {0} — Plan: {1} ({2})").format(
			doc.name, doc.membership_plan, doc.billing_cycle
		),
	})

	if flt(doc.discount_percent) > 0:
		si.additional_discount_percentage = flt(doc.discount_percent)

	si.flags.ignore_permissions = True
	si.insert()
	si.submit()

	frappe.msgprint(
		_("Sales Invoice {0} created for membership {1}").format(
			f'<a href="{_desk_route()}/sales-invoice/{si.name}">{si.name}</a>',
			doc.name,
		),
		alert=True,
	)


def on_membership_cancel(doc, method):
	"""Cancel linked Sales Invoice when a Membership is cancelled."""
	if not _erpnext_installed():
		return

	invoices = frappe.get_all(
		"Sales Invoice",
		filters={"arkspace_membership": doc.name, "docstatus": 1},
		pluck="name",
	)
	for inv_name in invoices:
		inv = frappe.get_doc("Sales Invoice", inv_name)
		inv.flags.ignore_permissions = True
		inv.cancel()


# ─────────────────── Payment Reconciliation ──────────────────────────────

@frappe.whitelist()
def get_unpaid_invoices(member=None):
	"""Return outstanding Sales Invoices linked to ARKSpace bookings/memberships.

	Args:
		member: Customer name (optional)

	Returns:
		list of dicts with invoice details
	"""
	frappe.only_for(["ARKSpace User", "ARKSpace Manager", "System Manager"])

	filters = {
		"docstatus": 1,
		"outstanding_amount": [">", 0],
	}

	if member:
		filters["customer"] = member

	# Only ARKSpace-related invoices (have either booking or membership ref)
	invoices = frappe.get_all(
		"Sales Invoice",
		filters=filters,
		or_filters={
			"arkspace_booking": ["is", "set"],
			"arkspace_membership": ["is", "set"],
		},
		fields=[
			"name",
			"customer",
			"customer_name",
			"posting_date",
			"grand_total",
			"outstanding_amount",
			"arkspace_booking",
			"arkspace_membership",
		],
		order_by="posting_date desc",
	)
	return invoices


# ─────────────────── HR Bridge ───────────────────────────────────────────

def link_employee_to_customer(doc, method):
	"""When an Employee is created/updated with a user, try to link
	them to an ARKSpace Customer (if one exists for that user's email)."""
	if not doc.user_id:
		return

	customer = frappe.db.get_value("Customer", {"email_id": doc.user_id}, "name")
	if not customer:
		return

	# Add Employee custom field link (if it exists)
	if frappe.db.has_column("Customer", "linked_employee"):
		frappe.db.set_value("Customer", customer, "linked_employee", doc.name)


# ─────────────────── Helpers ─────────────────────────────────────────────

def _erpnext_installed():
	"""Check if ERPNext is installed in the current site."""
	try:
		installed_apps = frappe.get_installed_apps()
		return "erpnext" in installed_apps
	except Exception:
		return False


def _resolve_customer(member_name):
	"""Resolve a member name to a Customer.

	Tries:
		1. Direct Customer lookup by name
		2. Dynamic Link on Contact
	"""
	if not member_name:
		return None

	if frappe.db.exists("Customer", member_name):
		return member_name

	# Try via Contact Dynamic Link
	customer = frappe.db.get_value(
		"Dynamic Link",
		{"parenttype": "Contact", "link_doctype": "Customer", "parent": member_name},
		"link_name",
	)
	return customer


def _get_or_create_service_item(item_code, item_name):
	"""Get or create a service Item for invoicing."""
	if not frappe.db.exists("Item", item_code):
		item = frappe.new_doc("Item")
		item.item_code = item_code
		item.item_name = item_name
		item.item_group = "Services"
		item.is_stock_item = 0
		item.include_item_in_manufacturing = 0
		item.description = item_name
		item.flags.ignore_permissions = True
		item.insert()
	return item_code


def _desk_route():
	"""Return the desk route prefix — /desk for v16+, /app for v15."""
	from arkspace.utils.compat import desk_route
	return desk_route()


# ─────────────────── Sales Invoice from Day Pass ─────────────────────────

def on_day_pass_submit(doc, method):
	"""Create a Sales Invoice when a Day Pass is submitted (paid passes only)."""
	if not _erpnext_installed():
		return
	if doc.payment_method == "Free" or not flt(doc.net_amount):
		return

	# Try to resolve customer from guest info
	customer = None
	if doc.guest_email:
		customer = frappe.db.get_value("Customer", {"email_id": doc.guest_email}, "name")

	if not customer:
		# Use walk-in customer if configured
		customer = frappe.db.get_single_value("Selling Settings", "default_customer")

	if not customer:
		return

	si = frappe.new_doc("Sales Invoice")
	si.customer = customer
	si.posting_date = getdate(nowdate())
	si.due_date = getdate(nowdate())
	si.set_posting_time = 1
	si.remarks = _("Auto-generated from Day Pass {0}").format(doc.name)

	item = _get_or_create_service_item("Day Pass Fee", _("Co-Working Day Pass Fee"))

	si.append("items", {
		"item_code": item,
		"qty": 1,
		"rate": flt(doc.net_amount),
		"description": _("Day Pass {0} — {1} ({2})").format(
			doc.name, doc.pass_type, doc.guest_name
		),
	})

	si.flags.ignore_permissions = True
	si.insert()
	si.submit()

	doc.db_set("sales_invoice", si.name, update_modified=False)


def on_day_pass_cancel(doc, method):
	"""Cancel linked Sales Invoice when a Day Pass is cancelled."""
	if not _erpnext_installed():
		return

	if doc.sales_invoice:
		si = frappe.get_doc("Sales Invoice", doc.sales_invoice)
		if si.docstatus == 1:
			si.flags.ignore_permissions = True
			si.cancel()
