# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

import frappe
from arkspace.tests.compat import ARKSpaceTestCase


class TestTrainingModule(ARKSpaceTestCase):
	"""Test cases for Training Module DocType."""

	def _make_module(self, **kwargs):
		defaults = {
			"doctype": "Training Module",
			"module_name": f"Test Module {frappe.generate_hash(length=6)}",
			"description": "Test training module description",
			"category": "Technical",
			"level": "Beginner",
			"status": "Draft",
		}
		defaults.update(kwargs)
		return frappe.get_doc(defaults)

	def test_create_module(self):
		"""Test basic module creation."""
		mod = self._make_module()
		mod.insert()
		self.assertTrue(mod.name)

	def test_default_stats_zero(self):
		"""Test that stats default to 0."""
		mod = self._make_module()
		mod.insert()
		self.assertEqual(mod.total_sessions, 0)
		self.assertEqual(mod.total_enrollments, 0)

	def test_update_stats(self):
		"""Test update_stats counts sessions and enrollments."""
		mod = self._make_module()
		mod.insert()

		# Create a session linked to this module
		frappe.get_doc({
			"doctype": "Training Session",
			"title": f"Session {frappe.generate_hash(length=6)}",
			"training_module": mod.name,
			"session_date": frappe.utils.today(),
			"start_time": "09:00",
			"end_time": "10:00",
			"status": "Scheduled",
		}).insert()

		# Reload and check stats
		mod.reload()
		mod.update_stats()
		self.assertEqual(mod.total_sessions, 1)

	def test_status_values(self):
		"""Test valid status values."""
		for status in ["Draft", "Published", "Archived"]:
			mod = self._make_module(status=status)
			mod.insert()
			self.assertEqual(mod.status, status)
