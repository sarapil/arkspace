# Copyright (c) 2026, ARKSpace Team and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestWorkspaceLead(FrappeTestCase):
	"""Test cases for Workspace Lead DocType."""

	def _make_lead(self, **kwargs):
		defaults = {
			"doctype": "Workspace Lead",
			"lead_name": f"Test Lead {frappe.generate_hash(length=6)}",
			"email": f"lead{frappe.generate_hash(length=4)}@test.com",
			"phone": "05551234567",
			"source": "Website",
			"status": "New",
		}
		defaults.update(kwargs)
		return frappe.get_doc(defaults)

	def test_create_lead(self):
		"""Test basic lead creation."""
		lead = self._make_lead()
		lead.insert()
		self.assertTrue(lead.name)
		self.assertEqual(lead.status, "New")

	def test_lead_statuses(self):
		"""Test valid lead statuses."""
		for status in ["New", "Contacted", "Tour Scheduled", "Negotiating"]:
			lead = self._make_lead(status=status)
			lead.insert()
			self.assertEqual(lead.status, status)

	def test_converted_requires_customer(self):
		"""Test that Converted status requires linked customer."""
		lead = self._make_lead(status="Converted")
		self.assertRaises(frappe.ValidationError, lead.insert)

	def test_convert_to_customer(self):
		"""Test lead to customer conversion."""
		lead = self._make_lead(
			lead_name="Convert Test Lead",
			email="convert@test.com",
		)
		lead.insert()
		lead.convert_to_customer()
		lead.reload()
		self.assertEqual(lead.status, "Converted")
		self.assertTrue(lead.converted_customer)

		# Verify customer was created
		self.assertTrue(frappe.db.exists("Customer", lead.converted_customer))

	def test_schedule_tour(self):
		"""Test scheduling a tour from lead."""
		lead = self._make_lead()
		lead.insert()
		lead.schedule_tour()
		lead.reload()
		self.assertEqual(lead.status, "Tour Scheduled")

	def test_lead_with_interest_details(self):
		"""Test lead with interest/budget fields."""
		lead = self._make_lead(
			budget_monthly=5000,
			team_size=10,
		)
		lead.insert()
		self.assertEqual(lead.budget_monthly, 5000)
		self.assertEqual(lead.team_size, 10)

	def test_lead_lost_status(self):
		"""Test marking lead as lost."""
		lead = self._make_lead()
		lead.insert()
		lead.status = "Lost"
		lead.save()
		self.assertEqual(lead.status, "Lost")
