# Copyright (c) 2026, ARKSpace Team and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestDocumentationEntry(FrappeTestCase):
	"""Test cases for Documentation Entry DocType."""

	def _make_entry(self, **kwargs):
		defaults = {
			"doctype": "Documentation Entry",
			"title": f"Doc Entry {frappe.generate_hash(length=6)}",
			"content": "Test documentation content.",
			"summary": "Short summary of documentation.",
			"doc_type": "Tutorial",
		}
		defaults.update(kwargs)
		return frappe.get_doc(defaults)

	def test_create_entry(self):
		"""Test basic documentation entry creation."""
		entry = self._make_entry()
		entry.insert()
		self.assertTrue(entry.name)

	def test_summary_length_validation(self):
		"""Test summary must be 200 chars or less."""
		long_summary = "x" * 201
		entry = self._make_entry(summary=long_summary)
		self.assertRaises(frappe.ValidationError, entry.insert)

	def test_summary_exactly_200(self):
		"""Test summary at exactly 200 chars passes."""
		summary_200 = "x" * 200
		entry = self._make_entry(summary=summary_200)
		entry.insert()
		self.assertEqual(len(entry.summary), 200)

	def test_default_version(self):
		"""Test default version is set to 1.0."""
		entry = self._make_entry(version=None)
		entry.insert()
		self.assertEqual(entry.version, "1.0")

	def test_explicit_version_preserved(self):
		"""Test explicitly set version is preserved."""
		entry = self._make_entry(version="2.5")
		entry.insert()
		self.assertEqual(entry.version, "2.5")

	def test_no_summary_passes(self):
		"""Test entry without summary passes validation."""
		entry = self._make_entry(summary=None)
		entry.insert()
		self.assertTrue(entry.name)
