# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_months, flt, getdate


class Membership(Document):
	def validate(self):
		self.set_rate_from_plan()
		self.calculate_end_date()
		self.calculate_net_amount()
		self.provision_credits()

	def on_submit(self):
		self.status = "Active"
		self.db_set("status", "Active")
		self.assign_space_if_needed()
		self.create_or_update_wallet()

	def on_cancel(self):
		self.status = "Cancelled"
		self.db_set("status", "Cancelled")
		self.release_space()

	def set_rate_from_plan(self):
		"""Set rate based on plan and billing cycle."""
		if not self.membership_plan:
			return
		plan = frappe.get_doc("Membership Plan", self.membership_plan)
		rate_map = {
			"Monthly": plan.monthly_price,
			"Quarterly": plan.quarterly_price or (plan.monthly_price * 3),
			"Yearly": plan.yearly_price or (plan.monthly_price * 12),
		}
		if not self.rate:
			self.rate = rate_map.get(self.billing_cycle, plan.monthly_price)

		self.initial_credits = plan.included_credits or 0

	def calculate_end_date(self):
		"""حساب تاريخ الانتهاء — Auto-calculate end date from start + cycle."""
		if not self.start_date:
			return
		months_map = {"Monthly": 1, "Quarterly": 3, "Yearly": 12}
		months = months_map.get(self.billing_cycle, 1)
		self.end_date = add_months(getdate(self.start_date), months)

	def calculate_net_amount(self):
		"""Calculate net amount after discount."""
		if not self.rate:
			return
		discount = flt(self.discount_percent or 0)
		self.net_amount = flt(self.rate * (1 - discount / 100), 2)

	def provision_credits(self):
		"""Provision credits from the plan benefits."""
		if not self.membership_plan:
			return
		plan = frappe.get_cached_doc("Membership Plan", self.membership_plan)
		self.initial_credits = plan.included_credits or 0

	def assign_space_if_needed(self):
		"""If a dedicated/private plan, reserve the assigned space."""
		if self.assigned_space:
			frappe.db.set_value("Co-working Space", self.assigned_space, {
				"status": "Reserved",
				"current_member": self.member,
			})

	def release_space(self):
		"""Release the assigned space on cancellation."""
		if self.assigned_space:
			frappe.db.set_value("Co-working Space", self.assigned_space, {
				"status": "Available",
				"current_member": None,
			})

	def create_or_update_wallet(self):
		"""Ensure member has a credit wallet and add initial credits."""
		if not self.initial_credits:
			return

		wallet_name = frappe.db.exists("Member Credit Wallet", {"member": self.member})
		if wallet_name:
			wallet = frappe.get_doc("Member Credit Wallet", wallet_name)
		else:
			wallet = frappe.get_doc({
				"doctype": "Member Credit Wallet",
				"member": self.member,
			})
			wallet.insert(ignore_permissions=True)

		wallet.add_credits(
			self.initial_credits,
			description=_("Membership plan {0} — {1}").format(
				self.membership_plan, self.billing_cycle
			),
			reference_doctype="Membership",
			reference_name=self.name,
		)
		self.db_set("credit_wallet", wallet.name)
