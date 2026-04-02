# Copyright (c) 2026, ARKSpace Team and contributors
# For license information, please see license.txt

import frappe
from arkspace.tests.compat import ARKSpaceTestCase
from frappe.utils import add_days, today


class TestPaymentReceipt(ARKSpaceTestCase):
    """Test cases for Payment Receipt DocType."""

    def _get_customer(self):
        if frappe.db.exists("Customer", "Test Receipt Customer"):
            return "Test Receipt Customer"
        c = frappe.get_doc({
            "doctype": "Customer",
            "customer_name": "Test Receipt Customer",
            "customer_group": "All Customer Groups",
            "territory": "All Territories",
        }).insert(ignore_if_duplicate=True)
        return c.name

    def _make_receipt(self, **kwargs):
        defaults = {
            "doctype": "Payment Receipt",
            "receipt_type": "Membership Payment / دفعة عضوية",
            "receipt_date": today(),
            "member": self._get_customer(),
            "amount": 5000,
            "currency": "EGP",
            "payment_method": "Cash / نقدي",
            "payment_date": today(),
        }
        defaults.update(kwargs)
        return frappe.get_doc(defaults)

    def test_create_receipt(self):
        """Test basic receipt creation."""
        r = self._make_receipt()
        r.insert()
        self.assertTrue(r.name)
        self.assertTrue(r.name.startswith("RCT-"))

    def test_zero_amount_fails(self):
        """Test that zero amount raises error."""
        r = self._make_receipt(amount=0)
        self.assertRaises(frappe.ValidationError, r.insert)

    def test_negative_amount_fails(self):
        """Test that negative amount raises error."""
        r = self._make_receipt(amount=-100)
        self.assertRaises(frappe.ValidationError, r.insert)

    def test_period_validation(self):
        """Test period_to must be after period_from."""
        r = self._make_receipt(
            period_from=today(),
            period_to=add_days(today(), -1),
        )
        self.assertRaises(frappe.ValidationError, r.insert)

    def test_valid_period(self):
        """Test valid period dates pass."""
        r = self._make_receipt(
            period_from=today(),
            period_to=add_days(today(), 30),
        )
        r.insert()
        self.assertTrue(r.name)

    def test_submit_sets_payment_date(self):
        """Test submit auto-fills payment_date if not set."""
        r = self._make_receipt(payment_date=None)
        r.insert()
        r.submit()
        self.assertEqual(str(r.payment_date), r.receipt_date)

    def test_submit_keeps_existing_payment_date(self):
        """Test submit preserves existing payment_date."""
        r = self._make_receipt(payment_date=add_days(today(), -5))
        r.insert()
        r.submit()
        self.assertEqual(str(r.payment_date), str(add_days(today(), -5)))

    def test_all_receipt_types(self):
        """Test all valid receipt types."""
        types = [
            "Membership Payment / دفعة عضوية",
            "Booking Payment / دفعة حجز",
            "Deposit / تأمين",
            "Setup Fee / رسوم تأسيس",
            "Amenity Fee / رسوم خدمات",
            "Other / أخرى",
        ]
        for rt in types:
            r = self._make_receipt(receipt_type=rt)
            r.insert()
            self.assertEqual(r.receipt_type, rt)

    def test_all_payment_methods(self):
        """Test all valid payment methods."""
        methods = [
            "Cash / نقدي",
            "Bank Transfer / تحويل بنكي",
            "Check / شيك",
            "Card / بطاقة",
            "Online / إلكتروني",
            "Other / أخرى",
        ]
        for pm in methods:
            r = self._make_receipt(payment_method=pm)
            r.insert()
            self.assertEqual(r.payment_method, pm)
