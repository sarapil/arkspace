# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class TrainingModule(Document):
	def validate(self):
		self.update_stats()

	def update_stats(self):
		self.total_sessions = frappe.db.count(
			"Training Session",
			{"training_module": self.name, "docstatus": ["!=", 2]},
		)
		self.total_enrollments = frappe.db.count(
			"User Training Progress",
			{"training_module": self.name},
		)
