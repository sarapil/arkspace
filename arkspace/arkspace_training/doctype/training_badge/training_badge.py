# Copyright (c) 2026, ARKSpace Team and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class TrainingBadge(Document):
	def validate(self):
		self.total_awarded = frappe.db.count(
			"User Training Progress",
			{"badge": self.name},
		)
