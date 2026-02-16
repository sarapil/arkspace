# Copyright (c) 2026, ARKSpace Team and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class WorkspaceLead(Document):
	def validate(self):
		self.validate_conversion()

	def validate_conversion(self):
		"""Ensure converted leads have a linked customer."""
		if self.status == "Converted" and not self.converted_customer:
			frappe.throw(_("Please link a Customer before marking as Converted"))

	@frappe.whitelist()
	def convert_to_customer(self):
		"""Convert this lead to a Customer and optionally create a Membership."""
		if self.status == "Converted":
			frappe.throw(_("Lead already converted"))

		# Create Customer
		customer = frappe.get_doc({
			"doctype": "Customer",
			"customer_name": self.lead_name,
			"customer_type": "Company" if self.company_name else "Individual",
			"customer_group": "Commercial",
			"territory": "All Territories",
		})
		customer.insert(ignore_permissions=True)

		self.status = "Converted"
		self.converted_customer = customer.name
		self.save(ignore_permissions=True)

		return {"customer": customer.name}

	@frappe.whitelist()
	def schedule_tour(self):
		"""Create a Workspace Tour for this lead."""
		tour = frappe.get_doc({
			"doctype": "Workspace Tour",
			"lead": self.name,
			"lead_name": self.lead_name,
			"branch": self.branch,
			"assigned_to": self.assigned_to,
		})
		tour.insert(ignore_permissions=True)

		self.status = "Tour Scheduled"
		self.save(ignore_permissions=True)

		return {"tour": tour.name}
