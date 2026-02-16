# Copyright (c) 2026, ARKSpace Team and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ContractTemplate(Document):
    def validate(self):
        if self.language == "Bilingual" and not (self.terms_ar and self.terms_en):
            frappe.throw(
                frappe._("Bilingual template requires both Arabic and English terms")
            )
        if self.language == "Arabic" and not self.terms_ar:
            frappe.throw(frappe._("Arabic terms are required"))
        if self.language == "English" and not self.terms_en:
            frappe.throw(frappe._("English terms are required"))
