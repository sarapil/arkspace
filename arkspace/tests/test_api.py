# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

# See license.txt

import frappe
from arkspace.tests.compat import ARKSpaceTestCase


class TestArkspaceAPI(ARKSpaceTestCase):
	"""Test cases for ARKSpace API endpoints."""

	def test_ping(self):
		"""Test health check endpoint."""
		from arkspace.api import ping
		result = ping()
		self.assertEqual(result["app"], "arkspace")
		self.assertEqual(result["version"], "6.0.0")
		self.assertEqual(result["status"], "ok")

	def test_get_dashboard_stats(self):
		"""Test dashboard stats returns expected keys."""
		from arkspace.api import get_dashboard_stats
		result = get_dashboard_stats()
		self.assertIn("total_spaces", result)
		self.assertIn("occupied", result)
		self.assertIn("available", result)
		self.assertIn("bookings_today", result)
		self.assertIn("active_members", result)

	def test_get_available_spaces(self):
		"""Test available spaces API."""
		from arkspace.arkspace_spaces.api import get_available_spaces
		result = get_available_spaces()
		self.assertIsInstance(result, list)

	def test_get_membership_plans(self):
		"""Test membership plans API."""
		from arkspace.arkspace_memberships.api import get_membership_plans
		result = get_membership_plans()
		self.assertIsInstance(result, list)
