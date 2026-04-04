# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class TrainingBadge(Document):
	def validate(self):
		self.total_awarded = frappe.db.count(
			"User Training Progress",
			{"badge": self.name},
		)
