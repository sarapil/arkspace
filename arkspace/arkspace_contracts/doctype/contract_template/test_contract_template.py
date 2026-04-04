# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

import frappe
from arkspace.tests.compat import ARKSpaceTestCase


class TestContractTemplate(ARKSpaceTestCase):
    """Test cases for Contract Template DocType."""

    def _make_template(self, **kwargs):
        defaults = {
            "doctype": "Contract Template",
            "template_name": f"Test Template {frappe.generate_hash(length=6)}",
            "language": "Bilingual",
            "contract_type": "Membership",
            "terms_ar": "<p>شروط العقد باللغة العربية</p>",
            "terms_en": "<p>Contract terms in English</p>",
        }
        defaults.update(kwargs)
        return frappe.get_doc(defaults)

    def test_create_template(self):
        """Test basic template creation."""
        tpl = self._make_template()
        tpl.insert()
        self.assertTrue(tpl.name)
        self.assertTrue(tpl.name.startswith("CTPL-"))

    def test_bilingual_requires_both_terms(self):
        """Test that bilingual templates need both AR and EN terms."""
        tpl = self._make_template(language="Bilingual", terms_en="")
        self.assertRaises(frappe.ValidationError, tpl.insert)

        tpl2 = self._make_template(language="Bilingual", terms_ar="")
        self.assertRaises(frappe.ValidationError, tpl2.insert)

    def test_arabic_requires_ar_terms(self):
        """Test that Arabic template requires Arabic terms."""
        tpl = self._make_template(language="Arabic", terms_ar="", terms_en="<p>EN only</p>")
        self.assertRaises(frappe.ValidationError, tpl.insert)

    def test_english_requires_en_terms(self):
        """Test that English template requires English terms."""
        tpl = self._make_template(language="English", terms_ar="<p>AR only</p>", terms_en="")
        self.assertRaises(frappe.ValidationError, tpl.insert)

    def test_arabic_only(self):
        """Test Arabic-only template creation."""
        tpl = self._make_template(language="Arabic", terms_ar="<p>شروط</p>", terms_en="")
        tpl.insert()
        self.assertTrue(tpl.name)

    def test_english_only(self):
        """Test English-only template creation."""
        tpl = self._make_template(language="English", terms_ar="", terms_en="<p>Terms</p>")
        tpl.insert()
        self.assertTrue(tpl.name)

    def test_all_contract_types(self):
        """Test all valid contract types."""
        for ctype in ["Membership", "Booking", "Office Rental", "Event Space", "Virtual Office", "Other"]:
            tpl = self._make_template(contract_type=ctype)
            tpl.insert()
            self.assertEqual(tpl.contract_type, ctype)
