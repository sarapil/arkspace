# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

"""ARKSpace Integrations — API Endpoints

Public-facing endpoints for billing, payments, and integration status.
"""

import frappe
from frappe import _
from frappe.utils import flt


@frappe.whitelist()
def get_unpaid_invoices(member=None):
	"""Proxy to billing.get_unpaid_invoices."""
	frappe.only_for(["System Manager", "ARK Admin", "ARK User"])
	from arkspace.arkspace_integrations.billing import get_unpaid_invoices as _get
	return _get(member)


@frappe.whitelist()
def get_integration_status():
	"""Return which integrations are available on this site."""
	frappe.only_for(["System Manager", "ARK Admin", "ARK User"])
	installed = frappe.get_installed_apps()
	return {
		"erpnext": "erpnext" in installed,
		"hrms": "hrms" in installed,
		"payments": "payments" in installed,
	}


# ═══════════════════════════════════════════════════════════════════════════
# Online Payments API
# ═══════════════════════════════════════════════════════════════════════════


@frappe.whitelist()
def initiate_payment(
	reference_doctype,
	reference_name,
	amount,
	currency="AED",
	gateway=None,
	member=None,
	payment_for=None,
):
	"""Start an online payment flow and return a checkout URL.

	Args:
		reference_doctype: e.g. "Space Booking", "Membership", "Sales Invoice"
		reference_name: Document name
		amount: Payment amount
		currency: Currency code (default AED)
		gateway: Gateway name (Stripe/Tap) — falls back to site default
		member: Customer name
		payment_for: Category label

	Returns:
		dict with checkout_url, payment_name, gateway
	"""
	frappe.has_permission("AS Booking", "write", throw=True)
	frappe.only_for(["System Manager", "ARK Admin", "ARK User"])
	from arkspace.arkspace_integrations.payment_gateway import (
		initiate_payment as _initiate,
	)

	return _initiate(
		reference_doctype=reference_doctype,
		reference_name=reference_name,
		amount=flt(amount),
		currency=currency,
		gateway=gateway,
		member=member,
		payment_for=payment_for,
	)


@frappe.whitelist()
def verify_payment(payment_name):
	"""Check the status of an online payment with the gateway.

	Args:
		payment_name: Online Payment document name

	Returns:
		dict with status, gateway_status
	"""
	frappe.only_for(["System Manager", "ARK Admin", "ARK User"])
	from arkspace.arkspace_integrations.payment_gateway import (
		confirm_payment,
	)

	return confirm_payment(payment_name)


@frappe.whitelist()
def refund_payment(payment_name, amount=None, reason=None):
	"""Initiate a refund for a completed online payment.

	Args:
		payment_name: Online Payment document name
		amount: Refund amount (None = full refund)
		reason: Reason for refund

	Returns:
		dict with status, refund_id
	"""
	frappe.only_for(["System Manager", "ARKSpace Admin"])

	from arkspace.arkspace_integrations.payment_gateway import (
		request_refund,
	)

	return request_refund(
		payment_name,
		amount=flt(amount) if amount else None,
		reason=reason,
	)


@frappe.whitelist(allow_guest=True)
def payment_webhook(**kwargs):
	"""Universal webhook endpoint for all payment gateways.

	Route: /api/method/arkspace.arkspace_integrations.api.payment_webhook
	Accepts POST with gateway query param: ?gateway=Stripe or ?gateway=Tap
	"""
	from arkspace.arkspace_integrations.payment_gateway import (
		process_webhook,
	)

	gateway = frappe.form_dict.get("gateway") or frappe.request.args.get("gateway", "Stripe")
	payload = frappe.request.get_data()
	headers = dict(frappe.request.headers)

	frappe.set_user("Administrator")  # Webhooks run as system

	try:
		result = process_webhook(gateway, payload, headers)
		frappe.db.commit()
		return result
	except frappe.AuthenticationError:
		frappe.local.response["http_status_code"] = 401
		return {"status": "unauthorized"}
	except Exception:
		frappe.log_error(
			title=_("Payment Webhook Error"),
			message=frappe.get_traceback(),
		)
		frappe.db.rollback()
		return {"status": "error"}


@frappe.whitelist()
def get_payment_status(reference_doctype, reference_name):
	"""Get the latest payment status for a reference document.

	Args:
		reference_doctype: DocType name
		reference_name: Document name

	Returns:
		dict with has_payment, latest_status, payments list
	"""
	frappe.only_for(["System Manager", "ARK Admin", "ARK User"])
	payments = frappe.get_all(
		"Online Payment",
		filters={
			"reference_doctype": reference_doctype,
			"reference_name": reference_name,
		},
		fields=["name", "status", "amount", "currency", "gateway", "initiated_at", "completed_at"],
		order_by="creation desc",
	)

	return {
		"has_payment": len(payments) > 0,
		"latest_status": payments[0]["status"] if payments else None,
		"payments": payments,
	}


@frappe.whitelist()
def get_checkout_url(reference_doctype, reference_name):
	"""Get or create a checkout URL for a document.

	If an active (Initiated/Pending) payment exists, returns its URL.
	Otherwise, creates a new payment and returns the checkout URL.
	"""
	frappe.only_for(["System Manager", "ARK Admin", "ARK User"])
	# Check for existing active payment
	existing = frappe.db.get_value(
		"Online Payment",
		{
			"reference_doctype": reference_doctype,
			"reference_name": reference_name,
			"status": ["in", ["Initiated", "Pending"]],
		},
		["name", "checkout_url"],
		as_dict=True,
	)

	if existing and existing.checkout_url:
		return {
			"payment_name": existing.name,
			"checkout_url": existing.checkout_url,
			"existing": True,
		}

	# Fetch document to get amount and member
	doc = frappe.get_doc(reference_doctype, reference_name)

	amount = flt(doc.get("net_amount") or doc.get("grand_total") or doc.get("outstanding_amount"))
	member = doc.get("member") or doc.get("customer")
	currency = doc.get("currency") or "AED"

	if not amount:
		frappe.throw(_("Cannot determine payment amount from {0}").format(reference_name))

	return initiate_payment(
		reference_doctype=reference_doctype,
		reference_name=reference_name,
		amount=amount,
		currency=currency,
		member=member,
	)
