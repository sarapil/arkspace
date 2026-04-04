# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class WorkspaceTour(Document):
	def validate(self):
		if self.status == "Completed" and not self.feedback:
			frappe.msgprint(_("Consider adding feedback for completed tours"), indicator="orange")

	@frappe.whitelist()
	def mark_completed(self, interest_level=None, feedback=None, outcome=None):
		"""Mark the tour as completed with feedback."""
		frappe.only_for(["ARKSpace Manager", "System Manager"])

		self.status = "Completed"
		if interest_level:
			self.interest_level = interest_level
		if feedback:
			self.feedback = feedback
		if outcome:
			self.outcome = outcome
		self.save(ignore_permissions=True)

		# Update lead status
		if self.lead:
			lead = frappe.get_doc("Workspace Lead", self.lead)
			if outcome == "Converted":
				lead.status = "Negotiating"
			elif outcome == "Not Interested":
				lead.status = "Lost"
			else:
				lead.status = "Contacted"
			lead.save(ignore_permissions=True)

		return {"status": "Completed"}
