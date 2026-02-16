# Copyright (c) 2026, ARKSpace Team and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import flt


class TestMemberCreditWallet(FrappeTestCase):
	"""Test cases for Member Credit Wallet DocType."""

	def _get_or_create_customer(self, suffix=""):
		name = f"Test Wallet Customer {suffix or frappe.generate_hash(length=6)}"
		if frappe.db.exists("Customer", name):
			return frappe.get_doc("Customer", name)
		return frappe.get_doc({
			"doctype": "Customer",
			"customer_name": name,
			"customer_type": "Individual",
		}).insert()

	def _make_wallet(self, customer=None):
		if not customer:
			customer = self._get_or_create_customer()
		return frappe.get_doc({
			"doctype": "Member Credit Wallet",
			"member": customer.name,
		}).insert()

	def test_create_wallet(self):
		"""Test basic wallet creation."""
		wallet = self._make_wallet()
		self.assertTrue(wallet.name)
		self.assertEqual(flt(wallet.total_credits), 0)
		self.assertEqual(flt(wallet.available_credits), 0)

	def test_add_credits(self):
		"""Test adding credits to wallet."""
		wallet = self._make_wallet()
		wallet.add_credits(
			credits=50,
			description="Test credit addition",
			ref_doctype="Membership",
			ref_name="MEM-0001",
		)
		wallet.reload()
		self.assertEqual(flt(wallet.total_credits), 50)
		self.assertEqual(flt(wallet.available_credits), 50)

	def test_debit_credits(self):
		"""Test debiting credits from wallet."""
		wallet = self._make_wallet()
		wallet.add_credits(100, "Initial credits", "Membership", "MEM-0001")
		wallet.reload()
		wallet.debit_credits(30, "Room booking", "Space Booking", "BK-0001")
		wallet.reload()
		self.assertEqual(flt(wallet.total_credits), 100)
		self.assertEqual(flt(wallet.used_credits), 30)
		self.assertEqual(flt(wallet.available_credits), 70)

	def test_insufficient_credits(self):
		"""Test that debiting more than available raises error."""
		wallet = self._make_wallet()
		wallet.add_credits(10, "Small credit", "Membership", "MEM-0001")
		wallet.reload()
		self.assertRaises(
			frappe.ValidationError,
			wallet.debit_credits,
			50, "Too much", "Space Booking", "BK-0001",
		)

	def test_multiple_transactions(self):
		"""Test multiple credit/debit transactions."""
		wallet = self._make_wallet()
		wallet.add_credits(100, "Initial", "Membership", "MEM-0001")
		wallet.reload()
		wallet.debit_credits(20, "Booking 1", "Space Booking", "BK-0001")
		wallet.reload()
		wallet.add_credits(30, "Bonus", "Membership", "MEM-0002")
		wallet.reload()
		wallet.debit_credits(50, "Booking 2", "Space Booking", "BK-0002")
		wallet.reload()

		self.assertEqual(flt(wallet.total_credits), 130)  # 100 + 30
		self.assertEqual(flt(wallet.used_credits), 70)  # 20 + 50
		self.assertEqual(flt(wallet.available_credits), 60)  # 130 - 70

	def test_transaction_records(self):
		"""Test that transactions are recorded in child table."""
		wallet = self._make_wallet()
		wallet.add_credits(50, "Test", "Membership", "MEM-0001")
		wallet.reload()
		self.assertEqual(len(wallet.transactions), 1)
		txn = wallet.transactions[0]
		self.assertEqual(txn.transaction_type, "Credit")
		self.assertEqual(flt(txn.credits), 50)
