# Copyright (c) 2026, ARKSpace Team and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class CoworkingSpace(Document):
	def validate(self):
		self.validate_capacity()
		self.validate_pricing()

	def validate_capacity(self):
		if self.capacity and self.capacity < 1:
			frappe.throw(_("Capacity must be at least 1"))

	def validate_pricing(self):
		"""Ensure at least one pricing tier is set."""
		if not any([self.hourly_rate, self.daily_rate, self.monthly_rate]):
			frappe.msgprint(
				_("Consider setting at least one pricing tier (hourly, daily, or monthly)"),
				indicator="orange",
				alert=True,
			)
