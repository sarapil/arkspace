# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

"""ARKSpace Payment Gateway Controller
محرك بوابات الدفع الإلكتروني

Unified interface for multiple payment gateways (Stripe, Tap, PayPal, etc.).
Each gateway is implemented as a strategy class that plugs into the controller.
"""

import hashlib
import hmac
import json

import frappe
from frappe import _
from frappe.utils import flt, get_url, now_datetime

# ═══════════════════════════════════════════════════════════════════════════
# Public API
# ═══════════════════════════════════════════════════════════════════════════


def initiate_payment(
	*,
	reference_doctype,
	reference_name,
	amount,
	currency="AED",
	gateway=None,
	member=None,
	payment_for=None,
	redirect_url=None,
):
	"""Create an Online Payment record and obtain a checkout URL.

	Args:
		reference_doctype: DocType being paid for (Space Booking, Membership, Sales Invoice)
		reference_name: Document name
		amount: Payment amount
		currency: Currency code (default AED)
		gateway: Gateway name (Stripe/Tap) — falls back to site default
		member: Customer name
		payment_for: Category label
		redirect_url: URL to redirect after payment

	Returns:
		dict with checkout_url, payment_name, gateway
	"""
	settings = _get_settings()
	if not settings.get("enable_online_payments"):
		frappe.throw(_("Online payments are not enabled. Please contact the administrator."))

	gateway = gateway or settings.get("default_payment_gateway") or "Stripe"
	handler = _get_gateway_handler(gateway, settings)

	# Create the Online Payment record
	payment = frappe.new_doc("Online Payment")
	payment.reference_doctype = reference_doctype
	payment.reference_name = reference_name
	payment.member = member
	payment.amount = flt(amount)
	payment.currency = currency
	payment.gateway = gateway
	payment.payment_for = payment_for or _infer_payment_for(reference_doctype)
	payment.status = "Initiated"
	payment.initiated_at = now_datetime()

	# Resolve sales invoice if applicable
	if reference_doctype == "Sales Invoice":
		payment.sales_invoice = reference_name
	elif reference_doctype in ("Space Booking", "Membership"):
		si = _find_linked_invoice(reference_doctype, reference_name)
		if si:
			payment.sales_invoice = si

	payment.flags.ignore_permissions = True
	payment.insert()

	# Ask the gateway to create a checkout session
	checkout = handler.create_checkout(
		payment_name=payment.name,
		amount=flt(amount),
		currency=currency,
		description=_("{0}: {1}").format(reference_doctype, reference_name),
		customer_email=payment.member_name,
		redirect_url=redirect_url or _default_redirect_url(payment.name),
		metadata={
			"arkspace_payment": payment.name,
			"reference_doctype": reference_doctype,
			"reference_name": reference_name,
		},
	)

	payment.db_set({
		"checkout_url": checkout.get("url"),
		"gateway_reference": checkout.get("session_id"),
		"status": "Pending",
	})

	return {
		"payment_name": payment.name,
		"checkout_url": checkout.get("url"),
		"gateway": gateway,
		"session_id": checkout.get("session_id"),
	}


def confirm_payment(payment_name):
	"""Verify a payment's status with the gateway and update the record.

	Called after redirect back from checkout, or via polling.
	"""
	payment = frappe.get_doc("Online Payment", payment_name)
	if payment.status in ("Completed", "Refunded"):
		return {"status": payment.status}

	settings = _get_settings()
	handler = _get_gateway_handler(payment.gateway, settings)

	result = handler.verify_payment(payment.gateway_reference)

	_apply_gateway_result(payment, result)

	return {
		"status": payment.status,
		"gateway_status": payment.gateway_status,
	}


def process_webhook(gateway, payload, headers):
	"""Process an incoming webhook from a payment gateway.

	Args:
		gateway: Gateway name (Stripe/Tap)
		payload: Raw request body (bytes)
		headers: Request headers dict
	"""
	settings = _get_settings()
	handler = _get_gateway_handler(gateway, settings)

	# Verify webhook signature
	if not handler.verify_webhook_signature(payload, headers):
		frappe.throw(_("Invalid webhook signature"), frappe.AuthenticationError)

	event = handler.parse_webhook(payload)
	if not event:
		return {"status": "ignored"}

	payment_name = event.get("payment_name")
	if not payment_name:
		frappe.log_error(
			title=_("Webhook: No payment reference"),
			message=json.dumps(event, default=str),
		)
		return {"status": "no_reference"}

	if not frappe.db.exists("Online Payment", payment_name):
		frappe.log_error(
			title=_("Webhook: Payment not found"),
			message=f"Payment {payment_name} not found for webhook",
		)
		return {"status": "not_found"}

	payment = frappe.get_doc("Online Payment", payment_name)

	result = {
		"status": event.get("status"),
		"gateway_reference": event.get("gateway_reference"),
		"gateway_status": event.get("gateway_status"),
		"payment_method_type": event.get("payment_method_type"),
		"card_last_four": event.get("card_last_four"),
		"gateway_fee": event.get("gateway_fee"),
		"gateway_response": event.get("raw"),
	}

	_apply_gateway_result(payment, result)

	return {"status": "processed", "payment_status": payment.status}


def request_refund(payment_name, amount=None, reason=None):
	"""Initiate a refund for a completed payment.

	Args:
		payment_name: Online Payment name
		amount: Refund amount (defaults to full amount)
		reason: Reason for refund
	"""
	payment = frappe.get_doc("Online Payment", payment_name)
	if payment.status not in ("Completed",):
		frappe.throw(_("Only completed payments can be refunded"))

	settings = _get_settings()
	handler = _get_gateway_handler(payment.gateway, settings)

	refund_amount = flt(amount) or flt(payment.amount)

	result = handler.create_refund(
		gateway_reference=payment.gateway_reference,
		amount=refund_amount,
		currency=payment.currency,
		reason=reason,
	)

	new_status = "Refunded" if flt(refund_amount) >= flt(payment.amount) else "Partially Refunded"
	payment.db_set({
		"status": new_status,
		"notes": (payment.notes or "") + f"\nRefund: {refund_amount} {payment.currency} — {reason or ''}",
	})

	return {
		"status": new_status,
		"refund_id": result.get("refund_id"),
	}


# ═══════════════════════════════════════════════════════════════════════════
# Gateway Handlers (Strategy Pattern)
# ═══════════════════════════════════════════════════════════════════════════


class BaseGatewayHandler:
	"""Abstract base for payment gateway integrations."""

	def __init__(self, settings):
		self.settings = settings

	def create_checkout(self, **kwargs):
		raise NotImplementedError

	def verify_payment(self, gateway_reference):
		raise NotImplementedError

	def verify_webhook_signature(self, payload, headers):
		raise NotImplementedError

	def parse_webhook(self, payload):
		raise NotImplementedError

	def create_refund(self, **kwargs):
		raise NotImplementedError


class StripeHandler(BaseGatewayHandler):
	"""Stripe payment gateway integration.

	Uses Stripe Checkout Sessions for payment collection.
	"""

	def __init__(self, settings):
		super().__init__(settings)
		self._init_stripe()

	def _init_stripe(self):
		try:
			import stripe as stripe_mod
			self.stripe = stripe_mod
			self.stripe.api_key = self.settings.get("stripe_secret_key")
		except ImportError:
			frappe.throw(_("Stripe Python library is not installed. Run: pip install stripe"))

	def create_checkout(self, **kwargs):
		session = self.stripe.checkout.Session.create(
			payment_method_types=["card"],
			line_items=[{
				"price_data": {
					"currency": kwargs["currency"].lower(),
					"product_data": {
						"name": kwargs.get("description", "ARKSpace Payment"),
					},
					"unit_amount": int(flt(kwargs["amount"]) * 100),
				},
				"quantity": 1,
			}],
			mode="payment",
			success_url=(
				kwargs.get("redirect_url", get_url())
				+ "?payment={CHECKOUT_SESSION_ID}&status=success"
			),
			cancel_url=(
				kwargs.get("redirect_url", get_url())
				+ "?payment={CHECKOUT_SESSION_ID}&status=cancel"
			),
			metadata=kwargs.get("metadata", {}),
			customer_email=kwargs.get("customer_email"),
		)

		return {
			"url": session.url,
			"session_id": session.id,
		}

	def verify_payment(self, gateway_reference):
		session = self.stripe.checkout.Session.retrieve(gateway_reference)
		payment_intent = None

		if session.payment_intent:
			payment_intent = self.stripe.PaymentIntent.retrieve(session.payment_intent)

		status_map = {
			"complete": "Completed",
			"expired": "Expired",
			"open": "Pending",
		}

		result = {
			"status": status_map.get(session.status, "Pending"),
			"gateway_reference": session.payment_intent or gateway_reference,
			"gateway_status": session.status,
		}

		if payment_intent:
			charges = payment_intent.get("charges", {}).get("data", [])
			if charges:
				charge = charges[0]
				result["payment_method_type"] = charge.get("payment_method_details", {}).get("type", "card")
				card = charge.get("payment_method_details", {}).get("card", {})
				result["card_last_four"] = card.get("last4")
				result["gateway_fee"] = flt(charge.get("balance_transaction", {}).get("fee", 0)) / 100

		result["gateway_response"] = json.dumps({"session": session.to_dict()}, default=str)
		return result

	def verify_webhook_signature(self, payload, headers):
		secret = self.settings.get("stripe_webhook_secret")
		if not secret:
			return True  # No secret configured — skip verification

		sig = headers.get("Stripe-Signature") or headers.get("stripe-signature")
		if not sig:
			return False

		try:
			self.stripe.Webhook.construct_event(payload, sig, secret)
			return True
		except Exception:
			return False

	def parse_webhook(self, payload):
		data = json.loads(payload) if isinstance(payload, (bytes, str)) else payload
		event_type = data.get("type", "")

		if event_type not in (
			"checkout.session.completed",
			"checkout.session.expired",
			"charge.refunded",
			"payment_intent.payment_failed",
		):
			return None

		obj = data.get("data", {}).get("object", {})
		metadata = obj.get("metadata", {})

		status_map = {
			"checkout.session.completed": "Completed",
			"checkout.session.expired": "Expired",
			"charge.refunded": "Refunded",
			"payment_intent.payment_failed": "Failed",
		}

		return {
			"payment_name": metadata.get("arkspace_payment"),
			"status": status_map.get(event_type, "Pending"),
			"gateway_reference": obj.get("payment_intent") or obj.get("id"),
			"gateway_status": event_type,
			"raw": json.dumps(data, default=str),
		}

	def create_refund(self, **kwargs):
		refund = self.stripe.Refund.create(
			payment_intent=kwargs["gateway_reference"],
			amount=int(flt(kwargs["amount"]) * 100),
			reason=kwargs.get("reason", "requested_by_customer"),
		)
		return {"refund_id": refund.id, "status": refund.status}


class TapHandler(BaseGatewayHandler):
	"""Tap Payments gateway integration (popular in GCC / Middle East).

	Uses Tap Charges API for payment collection.
	https://developers.tap.company/reference
	"""

	API_BASE = "https://api.tap.company/v2"

	def __init__(self, settings):
		super().__init__(settings)
		self.secret_key = self.settings.get("tap_secret_key")
		if not self.secret_key:
			frappe.throw(_("Tap secret key is not configured in ARKSpace Settings"))

	def _headers(self):
		return {
			"Authorization": f"Bearer {self.secret_key}",
			"Content-Type": "application/json",
		}

	def create_checkout(self, **kwargs):
		import requests

		payload = {
			"amount": flt(kwargs["amount"]),
			"currency": kwargs["currency"],
			"description": kwargs.get("description", "ARKSpace Payment"),
			"metadata": {"udf1": kwargs.get("metadata", {}).get("arkspace_payment", "")},
			"reference": {"transaction": kwargs.get("metadata", {}).get("arkspace_payment", "")},
			"receipt": {"email": True},
			"customer": {
				"email": kwargs.get("customer_email", ""),
				"first_name": kwargs.get("description", ""),
			},
			"source": {"id": "src_all"},
			"redirect": {"url": kwargs.get("redirect_url", get_url())},
			"post": {"url": get_url("/api/method/arkspace.arkspace_integrations.api.payment_webhook")},
		}

		resp = requests.post(
			f"{self.API_BASE}/charges",
			json=payload,
			headers=self._headers(),
			timeout=30,
		)
		resp.raise_for_status()
		data = resp.json()

		return {
			"url": data.get("transaction", {}).get("url"),
			"session_id": data.get("id"),
		}

	def verify_payment(self, gateway_reference):
		import requests

		resp = requests.get(
			f"{self.API_BASE}/charges/{gateway_reference}",
			headers=self._headers(),
			timeout=30,
		)
		resp.raise_for_status()
		data = resp.json()

		tap_status = data.get("status", "").upper()
		status_map = {
			"CAPTURED": "Completed",
			"AUTHORIZED": "Completed",
			"FAILED": "Failed",
			"CANCELLED": "Cancelled",
			"TIMEDOUT": "Expired",
			"DECLINED": "Failed",
		}

		card_info = data.get("card", {}) or {}
		return {
			"status": status_map.get(tap_status, "Pending"),
			"gateway_reference": data.get("id"),
			"gateway_status": tap_status,
			"payment_method_type": data.get("source", {}).get("payment_method", ""),
			"card_last_four": card_info.get("last_four") or card_info.get("last4"),
			"gateway_fee": flt(data.get("fees", {}).get("amount", 0)),
			"gateway_response": json.dumps(data, default=str),
		}

	def verify_webhook_signature(self, payload, headers):
		"""Tap uses HMAC-SHA256 with the secret key."""
		secret = self.settings.get("tap_webhook_secret")
		if not secret:
			return True

		sig = headers.get("Hashstring") or headers.get("hashstring")
		if not sig:
			return False

		body = payload if isinstance(payload, bytes) else payload.encode("utf-8")
		expected = hmac.new(
			secret.encode("utf-8"),
			body,
			hashlib.sha256,
		).hexdigest()

		return hmac.compare_digest(expected, sig)

	def parse_webhook(self, payload):
		data = json.loads(payload) if isinstance(payload, (bytes, str)) else payload

		obj = data.get("object", data)
		metadata = obj.get("metadata", {})
		ref_txn = obj.get("reference", {}).get("transaction", "")

		tap_status = obj.get("status", "").upper()
		status_map = {
			"CAPTURED": "Completed",
			"AUTHORIZED": "Completed",
			"FAILED": "Failed",
			"CANCELLED": "Cancelled",
			"TIMEDOUT": "Expired",
			"DECLINED": "Failed",
		}

		return {
			"payment_name": metadata.get("udf1") or ref_txn,
			"status": status_map.get(tap_status, "Pending"),
			"gateway_reference": obj.get("id"),
			"gateway_status": tap_status,
			"raw": json.dumps(data, default=str),
		}

	def create_refund(self, **kwargs):
		import requests

		payload = {
			"charge_id": kwargs["gateway_reference"],
			"amount": flt(kwargs["amount"]),
			"currency": kwargs.get("currency", "AED"),
			"reason": kwargs.get("reason", "requested_by_customer"),
		}

		resp = requests.post(
			f"{self.API_BASE}/refunds",
			json=payload,
			headers=self._headers(),
			timeout=30,
		)
		resp.raise_for_status()
		data = resp.json()

		return {"refund_id": data.get("id"), "status": data.get("status")}


# ═══════════════════════════════════════════════════════════════════════════
# Internal helpers
# ═══════════════════════════════════════════════════════════════════════════

_GATEWAY_MAP = {
	"Stripe": StripeHandler,
	"Tap": TapHandler,
}


def _apply_gateway_result(payment, result):
	"""Apply a gateway verification/webhook result to an Online Payment doc."""
	updates = {}

	if result.get("status"):
		updates["status"] = result["status"]
	if result.get("gateway_reference"):
		updates["gateway_reference"] = result["gateway_reference"]
	if result.get("gateway_status"):
		updates["gateway_status"] = result["gateway_status"]
	if result.get("payment_method_type"):
		updates["payment_method_type"] = result["payment_method_type"]
	if result.get("card_last_four"):
		updates["card_last_four"] = result["card_last_four"]
	if result.get("gateway_fee") is not None:
		updates["gateway_fee"] = flt(result["gateway_fee"])
	if result.get("gateway_response"):
		updates["gateway_response_json"] = result["gateway_response"]

	if updates:
		payment.db_set(updates, update_modified=True)
		payment.reload()


def _get_settings():
	"""Load payment-related settings from ARKSpace Settings."""
	try:
		doc = frappe.get_cached_doc("ARKSpace Settings")
	except frappe.DoesNotExistError:
		frappe.throw(_("ARKSpace Settings not found. Please configure ARKSpace first."))

	return {
		"enable_online_payments": getattr(doc, "enable_online_payments", 0),
		"default_payment_gateway": getattr(
			doc, "default_payment_gateway", "Stripe"
		),
		"stripe_publishable_key": getattr(
			doc, "stripe_publishable_key", ""
		),
		"stripe_secret_key": (
			doc.get_password("stripe_secret_key", raise_exception=False)
			if hasattr(doc, "stripe_secret_key") else ""
		),
		"stripe_webhook_secret": (
			doc.get_password("stripe_webhook_secret", raise_exception=False)
			if hasattr(doc, "stripe_webhook_secret") else ""
		),
		"tap_publishable_key": getattr(
			doc, "tap_publishable_key", ""
		),
		"tap_secret_key": (
			doc.get_password("tap_secret_key", raise_exception=False)
			if hasattr(doc, "tap_secret_key") else ""
		),
		"tap_webhook_secret": (
			doc.get_password("tap_webhook_secret", raise_exception=False)
			if hasattr(doc, "tap_webhook_secret") else ""
		),
	}


def _get_gateway_handler(gateway, settings):
	"""Return the gateway handler instance for the given gateway name."""
	cls = _GATEWAY_MAP.get(gateway)
	if not cls:
		frappe.throw(_("Unsupported payment gateway: {0}").format(gateway))
	return cls(settings)


def _infer_payment_for(reference_doctype):
	"""Infer the payment_for category from the reference DocType."""
	return {
		"Space Booking": "Space Booking",
		"Membership": "Membership",
		"Sales Invoice": "Other",
	}.get(reference_doctype, "Other")


def _find_linked_invoice(doctype, name):
	"""Find a Sales Invoice linked to a booking or membership."""
	if doctype == "Space Booking":
		return frappe.db.get_value(
			"Sales Invoice",
			{"arkspace_booking": name, "docstatus": 1},
			"name",
		)
	elif doctype == "Membership":
		return frappe.db.get_value(
			"Sales Invoice",
			{"arkspace_membership": name, "docstatus": 1},
			"name",
		)
	return None


def _default_redirect_url(payment_name):
	"""Build the default redirect URL after payment."""
	from arkspace.utils.compat import desk_route
	return get_url(f"{desk_route()}/online-payment/{payment_name}")
