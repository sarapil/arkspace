# Copyright (c) 2026, ARKSpace Team and contributors
# For license information, please see license.txt

import frappe
from arkspace.tests.compat import ARKSpaceTestCase
from frappe.utils import today, add_days


class TestWorkspaceTour(ARKSpaceTestCase):
	"""Test cases for Workspace Tour DocType."""

	def setUp(self):
		"""Create test prerequisites."""
		self.lead = self._get_lead()

	def _get_lead(self):
		name = "Test Tour Lead"
		existing = frappe.db.exists("Workspace Lead", {"lead_name": name})
		if existing:
			return existing
		lead = frappe.get_doc({
			"doctype": "Workspace Lead",
			"lead_name": name,
			"email": f"tour_lead_{frappe.generate_hash(length=4)}@test.com",
			"phone": "01234567890",
			"status": "Tour Scheduled",
		}).insert(ignore_if_duplicate=True)
		return lead.name

	def _make_tour(self, **kwargs):
		defaults = {
			"doctype": "Workspace Tour",
			"lead": self.lead,
			"scheduled_date": today(),
			"scheduled_time": "10:00",
			"status": "Scheduled",
		}
		defaults.update(kwargs)
		return frappe.get_doc(defaults)

	def test_create_tour(self):
		"""Test basic tour creation."""
		tour = self._make_tour()
		tour.insert()
		self.assertTrue(tour.name)

	def test_default_status_scheduled(self):
		"""Test default status is Scheduled."""
		tour = self._make_tour()
		tour.insert()
		self.assertEqual(tour.status, "Scheduled")

	def test_mark_completed(self):
		"""Test mark_completed method."""
		tour = self._make_tour()
		tour.insert()
		tour.mark_completed(
			interest_level=0.8,
			feedback="Great space!",
			outcome="Converted",
		)
		tour.reload()
		self.assertEqual(tour.status, "Completed")
		self.assertEqual(tour.interest_level, 0.8)
		self.assertEqual(tour.feedback, "Great space!")

	def test_mark_completed_updates_lead_negotiating(self):
		"""Test mark_completed with Converted outcome sets lead to Negotiating."""
		lead = frappe.get_doc({
			"doctype": "Workspace Lead",
			"lead_name": f"Lead {frappe.generate_hash(length=6)}",
			"email": f"neg_{frappe.generate_hash(length=4)}@test.com",
			"phone": "01234567890",
			"status": "Tour Scheduled",
		}).insert()

		tour = self._make_tour(lead=lead.name)
		tour.insert()
		tour.mark_completed(outcome="Converted")

		lead.reload()
		self.assertEqual(lead.status, "Negotiating")

	def test_mark_completed_updates_lead_lost(self):
		"""Test mark_completed with Not Interested sets lead to Lost."""
		lead = frappe.get_doc({
			"doctype": "Workspace Lead",
			"lead_name": f"Lead {frappe.generate_hash(length=6)}",
			"email": f"lost_{frappe.generate_hash(length=4)}@test.com",
			"phone": "01234567890",
			"status": "Tour Scheduled",
		}).insert()

		tour = self._make_tour(lead=lead.name)
		tour.insert()
		tour.mark_completed(outcome="Not Interested")

		lead.reload()
		self.assertEqual(lead.status, "Lost")

	def test_mark_completed_updates_lead_contacted(self):
		"""Test mark_completed with other outcome sets lead to Contacted."""
		lead = frappe.get_doc({
			"doctype": "Workspace Lead",
			"lead_name": f"Lead {frappe.generate_hash(length=6)}",
			"email": f"cont_{frappe.generate_hash(length=4)}@test.com",
			"phone": "01234567890",
			"status": "Tour Scheduled",
		}).insert()

		tour = self._make_tour(lead=lead.name)
		tour.insert()
		tour.mark_completed(outcome="Need Follow Up")

		lead.reload()
		self.assertEqual(lead.status, "Contacted")
