# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class DocumentationEntry(Document):
	def validate(self):
		if self.summary and len(self.summary) > 200:
			frappe.throw(_("Summary must be 200 characters or less"))

	def before_save(self):
		if not self.version:
			self.version = "1.0"
