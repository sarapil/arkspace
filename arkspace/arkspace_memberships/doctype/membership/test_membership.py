# Copyright (c) 2026, ARKSpace Team and Contributors
# See license.txt

import frappe
from arkspace.tests.compat import ARKSpaceTestCase
from frappe.utils import today, add_months, flt, getdate


class TestMembership(ARKSpaceTestCase):
	"""Test cases for Membership DocType."""

	def setUp(self):
		"""Create test prerequisites."""
		self.customer = self._get_or_create_customer()
		self.plan = self._get_or_create_plan()

	def _get_or_create_customer(self):
		name = "Test Membership Customer"
		if frappe.db.exists("Customer", name):
			return frappe.get_doc("Customer", name)
		return frappe.get_doc({
			"doctype": "Customer",
			"customer_name": name,
			"customer_type": "Individual",
		}).insert()

	def _get_or_create_plan(self):
		name = "Test Standard Plan"
		if frappe.db.exists("Membership Plan", {"plan_name": name}):
			return frappe.get_doc("Membership Plan", {"plan_name": name})
		return frappe.get_doc({
			"doctype": "Membership Plan",
			"plan_name": name,
			"plan_type": "Hot Desk",
			"monthly_price": 1000,
			"quarterly_price": 2850,
			"yearly_price": 10800,
			"included_credits": 20,
			"is_active": 1,
		}).insert()

	def _make_membership(self, **kwargs):
		defaults = {
			"doctype": "Membership",
			"member": self.customer.name,
			"membership_plan": self.plan.name,
			"billing_cycle": "Monthly",
			"start_date": today(),
			"rate": 1000,
		}
		defaults.update(kwargs)
		return frappe.get_doc(defaults)

	def test_create_membership(self):
		"""Test basic membership creation."""
		mem = self._make_membership()
		mem.insert()
		self.assertTrue(mem.name)
		self.assertTrue(mem.name.startswith("MEM-"))
		self.assertEqual(mem.status, "Draft")

	def test_end_date_monthly(self):
		"""Test end_date is 1 month from start for Monthly billing."""
		mem = self._make_membership(billing_cycle="Monthly")
		mem.insert()
		expected = getdate(add_months(today(), 1))
		self.assertEqual(getdate(mem.end_date), expected)

	def test_end_date_quarterly(self):
		"""Test end_date is 3 months from start for Quarterly billing."""
		mem = self._make_membership(billing_cycle="Quarterly")
		mem.insert()
		expected = getdate(add_months(today(), 3))
		self.assertEqual(getdate(mem.end_date), expected)

	def test_end_date_yearly(self):
		"""Test end_date is 12 months from start for Yearly billing."""
		mem = self._make_membership(billing_cycle="Yearly")
		mem.insert()
		expected = getdate(add_months(today(), 12))
		self.assertEqual(getdate(mem.end_date), expected)

	def test_rate_from_plan(self):
		"""Test rate is fetched from plan based on billing cycle."""
		mem = self._make_membership(rate=0, billing_cycle="Monthly")
		mem.insert()
		self.assertEqual(flt(mem.rate), flt(self.plan.monthly_price))

	def test_net_amount_with_discount(self):
		"""Test net amount calculation with discount."""
		mem = self._make_membership(rate=1000, discount_percent=20)
		mem.insert()
		# net = 1000 * (1 - 0.20) = 800
		self.assertEqual(flt(mem.net_amount, 2), 800.0)

	def test_net_amount_no_discount(self):
		"""Test net amount equals rate when no discount."""
		mem = self._make_membership(rate=1000, discount_percent=0)
		mem.insert()
		self.assertEqual(flt(mem.net_amount, 2), 1000.0)

	def test_submit_activates(self):
		"""Test that submitting sets status to Active."""
		mem = self._make_membership()
		mem.insert()
		mem.submit()
		self.assertEqual(mem.status, "Active")

	def test_cancel_membership(self):
		"""Test that cancelling sets status to Cancelled."""
		mem = self._make_membership()
		mem.insert()
		mem.submit()
		mem.cancel()
		self.assertEqual(mem.status, "Cancelled")

	def test_credit_provisioning(self):
		"""Test that initial credits are set from plan."""
		mem = self._make_membership()
		mem.insert()
		if self.plan.included_credits:
			self.assertEqual(flt(mem.initial_credits), flt(self.plan.included_credits))

	def test_wallet_creation_on_submit(self):
		"""Test that wallet is created/linked on submit."""
		cust = frappe.get_doc({
			"doctype": "Customer",
			"customer_name": f"Wallet Test {frappe.generate_hash(length=6)}",
			"customer_type": "Individual",
		}).insert()

		mem = self._make_membership(member=cust.name)
		mem.insert()
		mem.submit()
		if mem.credit_wallet:
			wallet = frappe.get_doc("Member Credit Wallet", mem.credit_wallet)
			self.assertEqual(wallet.member, cust.name)
			self.assertGreater(flt(wallet.available_credits), 0)
