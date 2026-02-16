# Copyright (c) 2026, ARKSpace Team and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today, getdate


class TestUserTrainingProgress(FrappeTestCase):
	"""Test cases for User Training Progress DocType."""

	def setUp(self):
		"""Create test prerequisites."""
		self.module = self._get_module()
		self.session = self._get_session()

	def _create_test_user(self, prefix="tp"):
		"""Create a real User record for link validation."""
		email = f"{prefix}_{frappe.generate_hash(length=4)}@test.com"
		if not frappe.db.exists("User", email):
			user = frappe.get_doc({
				"doctype": "User",
				"email": email,
				"first_name": f"Test {prefix}",
				"enabled": 1,
				"send_welcome_email": 0,
			}).insert(ignore_permissions=True)
		return email

	def _get_module(self):
		name = "Test Progress Module"
		if frappe.db.exists("Training Module", {"module_name": name}):
			return frappe.get_value("Training Module", {"module_name": name}, "name")
		mod = frappe.get_doc({
			"doctype": "Training Module",
			"module_name": name,
			"description": "Module for progress tests",
			"category": "Technical",
			"status": "Published",
		}).insert(ignore_if_duplicate=True)
		return mod.name

	def _get_session(self):
		name = "Test Progress Session"
		existing = frappe.db.exists("Training Session", {"title": name})
		if existing:
			return existing
		session = frappe.get_doc({
			"doctype": "Training Session",
			"title": name,
			"training_module": self.module,
			"session_date": today(),
			"start_time": "09:00",
			"end_time": "10:00",
			"status": "Scheduled",
		}).insert(ignore_if_duplicate=True)
		return session.name

	def _make_progress(self, **kwargs):
		defaults = {
			"doctype": "User Training Progress",
			"user": "Administrator",
			"training_module": self.module,
			"training_session": self.session,
			"status": "Enrolled",
			"enrollment_date": today(),
			"progress_percent": 0,
		}
		defaults.update(kwargs)
		return frappe.get_doc(defaults)

	def test_create_progress(self):
		"""Test basic progress creation."""
		p = self._make_progress()
		p.insert()
		self.assertTrue(p.name)

	def test_completed_sets_date(self):
		"""Test Completed status auto-sets completion_date."""
		p = self._make_progress(status="Completed", completion_date=None)
		p.insert()
		self.assertEqual(p.completion_date, getdate(today()))

	def test_completed_sets_100_percent(self):
		"""Test Completed status auto-sets progress to 100%."""
		p = self._make_progress(status="Completed", progress_percent=50)
		p.insert()
		self.assertEqual(p.progress_percent, 100)

	def test_enrolled_no_completion_date(self):
		"""Test Enrolled status doesn't set completion_date."""
		p = self._make_progress(status="Enrolled")
		p.insert()
		self.assertFalse(p.completion_date)

	def test_session_count_updated_on_insert(self):
		"""Test that inserting progress updates session registered_count."""
		# Get initial count
		session = frappe.get_doc("Training Session", self.session)
		initial_count = session.registered_count or 0

		test_user = self._create_test_user("cnt")
		p = self._make_progress(user=test_user)
		p.insert()

		session.reload()
		self.assertEqual(session.registered_count, initial_count + 1)

	def test_enroll_user_api(self):
		"""Test enroll_user whitelisted API."""
		from arkspace.arkspace_training.doctype.user_training_progress.user_training_progress import enroll_user

		user_email = self._create_test_user("enroll")
		result = enroll_user(user_email, self.module, self.session)
		self.assertEqual(result["status"], "Enrolled")
		self.assertEqual(result["user"], user_email)

	def test_enroll_duplicate_fails(self):
		"""Test enrolling same user twice raises error."""
		from arkspace.arkspace_training.doctype.user_training_progress.user_training_progress import enroll_user

		user_email = self._create_test_user("dup")
		enroll_user(user_email, self.module, self.session)
		self.assertRaises(frappe.ValidationError, enroll_user, user_email, self.module, self.session)

	def test_update_progress_api(self):
		"""Test update_progress whitelisted API."""
		from arkspace.arkspace_training.doctype.user_training_progress.user_training_progress import (
			enroll_user,
			update_progress,
		)

		user_email = self._create_test_user("upd")
		enrollment = enroll_user(user_email, self.module, self.session)

		result = update_progress(enrollment["name"], status="In Progress", progress_percent=50)
		self.assertEqual(result["status"], "In Progress")
		self.assertEqual(result["progress_percent"], 50)

	def test_get_user_progress_api(self):
		"""Test get_user_progress whitelisted API."""
		from arkspace.arkspace_training.doctype.user_training_progress.user_training_progress import (
			enroll_user,
			get_user_progress,
		)

		user_email = self._create_test_user("get")
		enroll_user(user_email, self.module, self.session)

		records = get_user_progress(user_email)
		self.assertGreaterEqual(len(records), 1)
		self.assertEqual(records[0]["user"], user_email)

