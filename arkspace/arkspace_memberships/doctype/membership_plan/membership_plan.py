# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

class MembershipPlan(Document):
	def validate(self):
		self.validate_pricing()

	def validate_pricing(self):
		"""At least monthly price is required."""
		if not self.monthly_price or self.monthly_price <= 0:
			frappe.throw(_("Monthly price must be greater than zero"))

		# Auto-calculate quarterly/yearly if not provided
		if not self.quarterly_price and self.monthly_price:
			self.quarterly_price = self.monthly_price * 3 * 0.95  # 5% discount
		if not self.yearly_price and self.monthly_price:
			self.yearly_price = self.monthly_price * 12 * 0.9  # 10% discount
