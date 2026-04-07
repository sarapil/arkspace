# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

import frappe
from arkspace.tests.compat import ARKSpaceTestCase
from frappe.utils import add_days, today, getdate


class TestLegalDocument(ARKSpaceTestCase):
    """Test cases for Legal Document DocType."""

    def _get_customer(self):
        if frappe.db.exists("Customer", "Test Legal Customer"):
            return "Test Legal Customer"
        c = frappe.get_doc({
            "doctype": "Customer",
            "customer_name": "Test Legal Customer",
            "customer_group": "All Customer Groups",
            "territory": "All Territories",
        }).insert(ignore_if_duplicate=True)
        return c.name

    def _make_legal_doc(self, **kwargs):
        defaults = {
            "doctype": "Legal Document",
            "member": self._get_customer(),
            "document_type": "National ID",
            "document_number": f"ID-{frappe.generate_hash(length=6)}",
            "issue_date": today(),
            "expiry_date": add_days(today(), 365),
            "issuing_authority": "Test Authority",
            "status": "Valid",
        }
        defaults.update(kwargs)
        return frappe.get_doc(defaults)

    def test_create_legal_document(self):
        """Test basic legal document creation."""
        doc = self._make_legal_doc()
        doc.insert()
        self.assertTrue(doc.name)
        self.assertTrue(doc.name.startswith("LDOC-"))

    def test_valid_status_when_not_expired(self):
        """Test document stays valid when expiry is in the future."""
        doc = self._make_legal_doc(expiry_date=add_days(today(), 365))
        doc.insert()
        self.assertEqual(doc.status, "Valid")

    def test_auto_expired_status(self):
        """Test that past expiry_date auto-sets status to Expired."""
        doc = self._make_legal_doc(
            expiry_date=add_days(today(), -1),
            status="Valid",
        )
        doc.insert()
        self.assertEqual(doc.status, "Expired")

    def test_no_expiry_date_stays_valid(self):
        """Test document without expiry_date stays valid."""
        doc = self._make_legal_doc(expiry_date=None)
        doc.insert()
        self.assertEqual(doc.status, "Valid")

    def test_all_document_types(self):
        """Test all valid document types."""
        doc_types = [
            "National ID",
            "Passport",
            "Driver License",
            "Tax Card",
            "Commercial Register",
            "Company License",
            "Foreign Company Docs",
            "Power of Attorney",
            "Notarized Document",
            "Other",
        ]
        for dtype in doc_types:
            doc = self._make_legal_doc(document_type=dtype)
            doc.insert()
            self.assertEqual(doc.document_type, dtype)

    def test_pending_status(self):
        """Test document can be created with Pending status."""
        doc = self._make_legal_doc(status="Pending")
        doc.insert()
        self.assertEqual(doc.status, "Pending")
