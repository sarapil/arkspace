# Copyright (c) 2026, ARKSpace Team and contributors
# For license information, please see license.txt

import frappe
from arkspace.tests.compat import ARKSpaceTestCase


class TestTrainingBadge(ARKSpaceTestCase):
	"""Test cases for Training Badge DocType."""

	def _make_badge(self, **kwargs):
		defaults = {
			"doctype": "Training Badge",
			"badge_name": f"Badge {frappe.generate_hash(length=6)}",
			"description": "Test badge description",
			"category": "Completion",
			"level": "Bronze",
		}
		defaults.update(kwargs)
		return frappe.get_doc(defaults)

	def test_create_badge(self):
		"""Test basic badge creation."""
		badge = self._make_badge()
		badge.insert()
		self.assertTrue(badge.name)

	def test_total_awarded_default_zero(self):
		"""Test total_awarded defaults to 0."""
		badge = self._make_badge()
		badge.insert()
		self.assertEqual(badge.total_awarded, 0)

	def test_validate_updates_count(self):
		"""Test validate recalculates total_awarded."""
		badge = self._make_badge()
		badge.insert()

		# total_awarded should be 0 since no progress records reference it
		badge.reload()
		badge.save()
		self.assertEqual(badge.total_awarded, 0)

