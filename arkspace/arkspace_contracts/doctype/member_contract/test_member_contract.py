# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

import frappe
from arkspace.tests.compat import ARKSpaceTestCase
from frappe.utils import add_days, today, getdate

class TestMemberContract(ARKSpaceTestCase):
    """Test cases for Member Contract DocType."""

    def setUp(self):
        """Create test prerequisites."""
        self.customer = self._get_customer()
        self.template = self._get_template()

    def _get_customer(self):
        if frappe.db.exists("Customer", "Test Contract Customer"):
            return "Test Contract Customer"
        c = frappe.get_doc({
            "doctype": "Customer",
            "customer_name": "Test Contract Customer",
            "customer_group": "All Customer Groups",
            "territory": "All Territories",
        }).insert(ignore_if_duplicate=True)
        return c.name

    def _get_template(self):
        name = "Test Contract Template"
        if frappe.db.exists("Contract Template", {"template_name": name}):
            return frappe.get_value("Contract Template", {"template_name": name}, "name")
        tpl = frappe.get_doc({
            "doctype": "Contract Template",
            "template_name": name,
            "language": "Bilingual",
            "contract_type": "Membership",
            "terms_ar": "<p>شروط العقد - اسم العضو: {{ member_name }}</p>",
            "terms_en": "<p>Contract Terms - Member: {{ member_name }}</p>",
        }).insert(ignore_if_duplicate=True)
        return tpl.name

    def _make_contract(self, **kwargs):
        defaults = {
            "doctype": "Member Contract",
            "contract_title": f"Test Contract {frappe.generate_hash(length=6)}",
            "contract_date": today(),
            "member": self.customer,
            "start_date": today(),
            "end_date": add_days(today(), 365),
            "rate": 5000,
            "currency": "EGP",
            "contract_terms_ar": "<p>شروط</p>",
            "contract_terms_en": "<p>Terms</p>",
        }
        defaults.update(kwargs)
        return frappe.get_doc(defaults)

    def test_create_contract(self):
        """Test basic contract creation."""
        contract = self._make_contract()
        contract.insert()
        self.assertTrue(contract.name)
        self.assertTrue(contract.name.startswith("CTR-"))

    def test_default_status(self):
        """Test default status is Draft."""
        contract = self._make_contract()
        contract.insert()
        self.assertEqual(contract.status, "Draft")

    def test_net_amount_no_discount(self):
        """Test net_amount equals rate when no discount."""
        contract = self._make_contract(rate=5000, discount_percent=0)
        contract.insert()
        self.assertEqual(contract.net_amount, 5000)

    def test_net_amount_with_discount(self):
        """Test net_amount calculation with discount."""
        contract = self._make_contract(rate=5000, discount_percent=20)
        contract.insert()
        self.assertEqual(contract.net_amount, 4000)

    def test_net_amount_half_discount(self):
        """Test 50% discount."""
        contract = self._make_contract(rate=10000, discount_percent=50)
        contract.insert()
        self.assertEqual(contract.net_amount, 5000)

    def test_date_validation_end_before_start(self):
        """Test end_date must be after start_date."""
        contract = self._make_contract(
            start_date=today(),
            end_date=add_days(today(), -1),
        )
        self.assertRaises(frappe.ValidationError, contract.insert)

    def test_date_validation_same_dates(self):
        """Test end_date same as start_date is rejected."""
        contract = self._make_contract(
            start_date=today(),
            end_date=today(),
        )
        self.assertRaises(frappe.ValidationError, contract.insert)

    def test_submit_sets_active(self):
        """Test that submitting sets status to Active."""
        contract = self._make_contract()
        contract.insert()
        contract.submit()
        self.assertEqual(contract.status, "Active")

    def test_cancel_sets_cancelled(self):
        """Test that cancelling sets status to Cancelled."""
        contract = self._make_contract()
        contract.insert()
        contract.submit()
        contract.cancel()
        self.assertEqual(contract.status, "Cancelled")

    def test_submit_without_terms_fails(self):
        """Test that submitting without any terms raises error."""
        contract = self._make_contract(contract_terms_ar="", contract_terms_en="")
        contract.insert()
        self.assertRaises(frappe.ValidationError, contract.submit)

    def test_populate_from_template(self):
        """Test populate_from_template fills terms from template."""
        contract = self._make_contract(
            contract_template=self.template,
            contract_terms_ar="",
            contract_terms_en="",
        )
        contract.insert()
        contract.populate_from_template()
        self.assertIn("Test Contract Customer", contract.contract_terms_en or "")
        self.assertTrue(contract.contract_terms_ar)

    def test_populate_without_template_fails(self):
        """Test populate_from_template without template raises error."""
        contract = self._make_contract(contract_template=None)
        contract.insert()
        self.assertRaises(frappe.ValidationError, contract.populate_from_template)
