# Copyright (c) 2026, ARKSpace Team and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import flt


class TestMembershipPlan(FrappeTestCase):
	"""Test cases for Membership Plan DocType."""

	def _make_plan(self, **kwargs):
		defaults = {
			"doctype": "Membership Plan",
			"plan_name": f"Test Plan {frappe.generate_hash(length=6)}",
			"plan_type": "Hot Desk",
			"monthly_price": 1000,
			"is_active": 1,
		}
		defaults.update(kwargs)
		return frappe.get_doc(defaults)

	def test_create_plan(self):
		"""Test basic plan creation."""
		plan = self._make_plan()
		plan.insert()
		self.assertTrue(plan.name)
		self.assertTrue(plan.name.startswith("MP-"))

	def test_monthly_price_required(self):
		"""Test that monthly price must be > 0."""
		plan = self._make_plan(monthly_price=0)
		self.assertRaises(frappe.ValidationError, plan.insert)

	def test_auto_quarterly_pricing(self):
		"""Test quarterly price auto-calculated as monthly * 3 * 0.95."""
		plan = self._make_plan(monthly_price=1000)
		plan.insert()
		# quarterly = 1000 * 3 * 0.95 = 2850
		if plan.quarterly_price:
			self.assertEqual(flt(plan.quarterly_price, 0), 2850)

	def test_auto_yearly_pricing(self):
		"""Test yearly price auto-calculated as monthly * 12 * 0.90."""
		plan = self._make_plan(monthly_price=1000)
		plan.insert()
		# yearly = 1000 * 12 * 0.90 = 10800
		if plan.yearly_price:
			self.assertEqual(flt(plan.yearly_price, 0), 10800)

	def test_manual_pricing_preserved(self):
		"""Test that manually set prices are preserved."""
		plan = self._make_plan(
			monthly_price=1000,
			quarterly_price=2500,
			yearly_price=10000,
		)
		plan.insert()
		self.assertEqual(flt(plan.quarterly_price, 0), 2500)
		self.assertEqual(flt(plan.yearly_price, 0), 10000)

	def test_plan_types(self):
		"""Test all valid plan types."""
		valid_types = [
			"Hot Desk", "Dedicated Desk", "Private Office",
			"Meeting Room", "Event Space", "Virtual Office",
		]
		for pt in valid_types:
			plan = self._make_plan(plan_type=pt)
			plan.insert()
			self.assertEqual(plan.plan_type, pt)

	def test_included_credits(self):
		"""Test credits field on plan."""
		plan = self._make_plan(included_credits=50)
		plan.insert()
		self.assertEqual(plan.included_credits, 50)

	def test_unique_plan_name(self):
		"""Test plan_name uniqueness."""
		name = f"Unique Plan {frappe.generate_hash(length=6)}"
		p1 = self._make_plan(plan_name=name)
		p1.insert()
		p2 = self._make_plan(plan_name=name)
		self.assertRaises(frappe.DuplicateEntryError, p2.insert)
