# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

# See license.txt

import frappe
from arkspace.tests.compat import ARKSpaceTestCase


class TestCoworkingSpace(ARKSpaceTestCase):
	"""Test cases for Co-working Space DocType."""

	def setUp(self):
		"""Create test prerequisites."""
		self.space_type = self._create_space_type()
		self.branch = self._create_branch()

	def _create_space_type(self):
		if frappe.db.exists("Space Type", "Test Hot Desk"):
			return frappe.get_doc("Space Type", "Test Hot Desk")
		return frappe.get_doc({
			"doctype": "Space Type",
			"type_name": "Test Hot Desk",
		}).insert(ignore_if_duplicate=True)

	def _create_branch(self):
		if frappe.db.exists("Branch", "Test Branch"):
			return frappe.get_doc("Branch", "Test Branch")
		return frappe.get_doc({
			"doctype": "Branch",
			"branch": "Test Branch",
		}).insert(ignore_if_duplicate=True)

	def _make_space(self, **kwargs):
		defaults = {
			"doctype": "Co-working Space",
			"space_name": frappe.generate_hash(length=8),
			"space_type": self.space_type.name,
			"branch": self.branch.name,
			"capacity": 10,
			"hourly_rate": 50,
			"daily_rate": 300,
			"monthly_rate": 5000,
		}
		defaults.update(kwargs)
		return frappe.get_doc(defaults)

	def test_create_space(self):
		"""Test basic space creation."""
		space = self._make_space()
		space.insert()
		self.assertTrue(space.name)
		self.assertEqual(space.status, "Available")
		self.assertTrue(space.name.startswith("SPC-"))

	def test_capacity_validation(self):
		"""Test that capacity must be >= 1."""
		space = self._make_space(capacity=0)
		self.assertRaises(frappe.ValidationError, space.insert)

	def test_negative_capacity(self):
		"""Test that negative capacity is rejected."""
		space = self._make_space(capacity=-5)
		self.assertRaises(frappe.ValidationError, space.insert)

	def test_pricing_warning(self):
		"""Test that missing pricing generates a message (not error)."""
		space = self._make_space(hourly_rate=0, daily_rate=0, monthly_rate=0)
		# Should insert without error (pricing is a warning, not validation error)
		space.insert()
		self.assertTrue(space.name)

	def test_space_autoname(self):
		"""Test that spaces get SPC-#### naming."""
		space = self._make_space()
		space.insert()
		self.assertRegex(space.name, r"^SPC-\d{4,}$")

	def test_default_status(self):
		"""Test default status is Available."""
		space = self._make_space()
		space.insert()
		self.assertEqual(space.status, "Available")
