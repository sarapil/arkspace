# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class PaymentReceipt(Document):
    def validate(self):
        if flt(self.amount) <= 0:
            frappe.throw(_("Amount must be greater than zero"))
        if self.period_from and self.period_to:
            from frappe.utils import getdate
            if getdate(self.period_to) < getdate(self.period_from):
                frappe.throw(_("Period To must be after Period From"))

    def before_submit(self):
        if not self.payment_date:
            self.payment_date = self.receipt_date
