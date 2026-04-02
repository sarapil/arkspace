# Copyright (c) 2026, ARKSpace Team and contributors
# For license information, please see license.txt

"""Online Payment — بوابة الدفع الإلكتروني

Tracks every online payment attempt (Stripe, Tap, PayPal, etc.) and links
the result back to its originating booking, membership, or invoice.
"""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, now_datetime


class OnlinePayment(Document):
	"""Controller for the Online Payment DocType."""

	def validate(self):
		self._validate_amount()
		self._set_base_amount()

	def before_insert(self):
		if not self.initiated_at:
			self.initiated_at = now_datetime()
		if not self.payment_id:
			self.payment_id = self.name

	def on_update(self):
		"""React to status transitions."""
		prev = self.get_doc_before_save()
		if prev and prev.status != self.status:
			self._handle_status_change(prev.status, self.status)

	# ── Validation helpers ──────────────────────────────────────────

	def _validate_amount(self):
		if flt(self.amount) <= 0:
			frappe.throw(_("Payment amount must be greater than zero"))

	def _set_base_amount(self):
		rate = flt(self.exchange_rate) or 1
		self.base_amount = flt(self.amount) * rate

	# ── Status machine ──────────────────────────────────────────────

	def _handle_status_change(self, old_status, new_status):
		if new_status == "Completed":
			self.completed_at = now_datetime()
			self._calculate_net_received()
			self._create_payment_receipt()
			self._update_reference_status()
			frappe.publish_realtime(
				"online_payment_completed",
				{"payment": self.name, "reference": self.reference_name},
				user=frappe.session.user,
			)
		elif new_status == "Failed":
			self._update_reference_on_failure()
		elif new_status == "Cancelled":
			self.cancelled_at = now_datetime()
		elif new_status == "Refunded":
			self._process_refund()

	def _calculate_net_received(self):
		self.net_received = flt(self.amount) - flt(self.gateway_fee)

	# ── Payment Receipt integration ─────────────────────────────────

	def _create_payment_receipt(self):
		"""Create an ARKSpace Payment Receipt on successful payment."""
		if self.payment_receipt:
			return
		if not frappe.db.exists("DocType", "Payment Receipt"):
			return

		receipt_type = self._get_receipt_type()

		receipt = frappe.new_doc("Payment Receipt")
		receipt.member = self.member
		receipt.receipt_type = receipt_type
		receipt.payment_method = "Online"
		receipt.amount = flt(self.amount)
		receipt.currency = self.currency
		receipt.reference_no = self.gateway_reference or self.name
		receipt.payment_date = frappe.utils.nowdate()
		receipt.remarks = _("Auto-created from Online Payment {0}").format(self.name)
		receipt.flags.ignore_permissions = True
		receipt.insert()
		receipt.submit()

		self.db_set("payment_receipt", receipt.name, update_modified=False)

	def _get_receipt_type(self):
		mapping = {
			"Space Booking": "Booking Payment",
			"Membership": "Membership Payment",
			"Day Pass": "Other",
			"Event": "Other",
			"Deposit": "Deposit",
		}
		return mapping.get(self.payment_for, "Other")

	# ── Reference document updates ──────────────────────────────────

	def _update_reference_status(self):
		"""Notify the originating document that payment is complete."""
		if not self.reference_doctype or not self.reference_name:
			return

		if self.reference_doctype == "Sales Invoice":
			self._reconcile_invoice()

	def _update_reference_on_failure(self):
		"""Log failure against the reference document."""
		if not self.reference_doctype or not self.reference_name:
			return
		frappe.get_doc(
			"Comment",
			{
				"comment_type": "Info",
				"reference_doctype": self.reference_doctype,
				"reference_name": self.reference_name,
				"content": _("Online payment {0} failed — {1}").format(
					self.name, self.failure_reason or _("Unknown error")
				),
			},
		).insert(ignore_permissions=True)

	def _reconcile_invoice(self):
		"""Create a Payment Entry for the linked Sales Invoice."""
		if not frappe.db.exists("Sales Invoice", self.sales_invoice):
			return
		try:
			from erpnext.accounts.doctype.payment_entry.payment_entry import (
				get_payment_entry,
			)

			pe = get_payment_entry("Sales Invoice", self.sales_invoice)
			pe.reference_no = self.gateway_reference or self.name
			pe.reference_date = frappe.utils.nowdate()
			pe.remarks = _("Online payment via {0} — {1}").format(
				self.gateway, self.name
			)
			pe.flags.ignore_permissions = True
			pe.insert()
			pe.submit()
			self.db_set("payment_entry", pe.name, update_modified=False)
		except Exception:
			frappe.log_error(
				title=_("Payment Reconciliation Error"),
				message=frappe.get_traceback(),
			)

	def _process_refund(self):
		"""Handle refund accounting (stub — gateway-specific logic in controller)."""
		if self.payment_entry:
			frappe.get_doc(
				"Comment",
				{
					"comment_type": "Info",
					"reference_doctype": "Payment Entry",
					"reference_name": self.payment_entry,
					"content": _("Refund processed via {0} for {1}").format(
						self.gateway, self.name
					),
				},
			).insert(ignore_permissions=True)
