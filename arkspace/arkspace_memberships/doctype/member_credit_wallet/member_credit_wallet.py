# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, now_datetime

class MemberCreditWallet(Document):
	def validate(self):
		self.recalculate()

	def recalculate(self):
		"""Recalculate credit totals from transactions."""
		total = 0
		used = 0
		for txn in self.transactions:
			if txn.transaction_type == "Credit":
				total += flt(txn.credits)
			elif txn.transaction_type in ("Debit", "Expired"):
				used += flt(txn.credits)
			elif txn.transaction_type == "Refund":
				used -= flt(txn.credits)

		self.total_credits = flt(total, 2)
		self.used_credits = flt(used, 2)
		self.available_credits = flt(total - used, 2)

	def add_credits(self, credits, description="", reference_doctype=None, reference_name=None):
		"""Add credits to the wallet."""
		self.append("transactions", {
			"transaction_type": "Credit",
			"credits": credits,
			"description": description,
			"reference_doctype": reference_doctype,
			"reference_name": reference_name,
			"transaction_date": now_datetime(),
		})
		self.recalculate()
		self.save(ignore_permissions=True)
		return self.available_credits

	def debit_credits(self, credits, description="", reference_doctype=None, reference_name=None):
		"""Debit credits from the wallet."""
		if flt(credits) > self.available_credits:
			frappe.throw(_("Insufficient credits. Available: {0}, Requested: {1}").format(
				self.available_credits, credits
			))

		self.append("transactions", {
			"transaction_type": "Debit",
			"credits": credits,
			"description": description,
			"reference_doctype": reference_doctype,
			"reference_name": reference_name,
			"transaction_date": now_datetime(),
		})
		self.recalculate()
		self.save(ignore_permissions=True)
		return self.available_credits
