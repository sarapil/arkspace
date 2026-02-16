# Copyright (c) 2026, ARKSpace Team and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today


class LegalDocument(Document):
    def validate(self):
        self._check_expiry()

    def _check_expiry(self):
        """Auto-set status to Expired if expiry_date has passed."""
        if self.expiry_date and getdate(self.expiry_date) < getdate(today()):
            self.status = "Expired / منتهي"
