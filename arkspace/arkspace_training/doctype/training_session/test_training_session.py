# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

import frappe
from arkspace.tests.compat import ARKSpaceTestCase
from frappe.utils import today


class TestTrainingSession(ARKSpaceTestCase):
	"""Test cases for Training Session DocType."""

	def setUp(self):
		"""Create test prerequisites."""
		self.module = self._get_module()

	def _get_module(self):
		name = "Test Session Module"
		if frappe.db.exists("Training Module", {"module_name": name}):
			return frappe.get_value("Training Module", {"module_name": name}, "name")
		mod = frappe.get_doc({
			"doctype": "Training Module",
			"module_name": name,
			"description": "Module for session tests",
			"category": "Technical",
			"status": "Published",
		}).insert(ignore_if_duplicate=True)
		return mod.name

	def _make_session(self, **kwargs):
		defaults = {
			"doctype": "Training Session",
			"title": f"Session {frappe.generate_hash(length=6)}",
			"training_module": self.module,
			"session_date": today(),
			"start_time": "09:00",
			"end_time": "11:00",
			"status": "Scheduled",
		}
		defaults.update(kwargs)
		return frappe.get_doc(defaults)

	def test_create_session(self):
		"""Test basic session creation."""
		session = self._make_session()
		session.insert()
		self.assertTrue(session.name)

	def test_time_validation(self):
		"""Test end_time must be after start_time."""
		session = self._make_session(start_time="14:00", end_time="10:00")
		self.assertRaises(frappe.ValidationError, session.insert)

	def test_same_times_fail(self):
		"""Test same start and end times fail."""
		session = self._make_session(start_time="10:00", end_time="10:00")
		self.assertRaises(frappe.ValidationError, session.insert)

	def test_valid_times(self):
		"""Test valid time range passes."""
		session = self._make_session(start_time="09:00", end_time="17:00")
		session.insert()
		self.assertTrue(session.name)

	def test_registered_count_zero(self):
		"""Test initial registered_count is 0."""
		session = self._make_session()
		session.insert()
		self.assertEqual(session.registered_count, 0)

	def test_submit_updates_module_stats(self):
		"""Test submitting a session updates module stats."""
		session = self._make_session()
		session.insert()
		session.submit()

		mod = frappe.get_doc("Training Module", self.module)
		self.assertGreaterEqual(mod.total_sessions, 1)

	def test_cancel_sets_status(self):
		"""Test cancelling sets status to Cancelled."""
		session = self._make_session()
		session.insert()
		session.submit()
		session.cancel()
		session.reload()
		self.assertEqual(session.status, "Cancelled")
