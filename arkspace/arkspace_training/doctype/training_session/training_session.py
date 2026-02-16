# Copyright (c) 2026, ARKSpace Team and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class TrainingSession(Document):
	def validate(self):
		self._validate_times()
		self._update_registered_count()

	def on_submit(self):
		self._update_module_stats()

	def on_cancel(self):
		self._update_module_stats()
		self.db_set("status", "Cancelled")

	def _validate_times(self):
		if self.start_time and self.end_time and self.start_time >= self.end_time:
			frappe.throw(_("End Time must be after Start Time"))

	def _update_registered_count(self):
		self.registered_count = frappe.db.count(
			"User Training Progress",
			{"training_session": self.name},
		)

	def _update_module_stats(self):
		if self.training_module:
			module_doc = frappe.get_doc("Training Module", self.training_module)
			module_doc.update_stats()
			module_doc.save(ignore_permissions=True)
