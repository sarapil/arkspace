# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate, today


class MemberContract(Document):
    def validate(self):
        self._calculate_net_amount()
        self._validate_dates()
        self._check_status()

    def before_submit(self):
        if not self.contract_terms_ar and not self.contract_terms_en:
            frappe.throw(_("Contract terms (Arabic or English) are required before submission"))
        self.status = "Active"

    def on_cancel(self):
        self.status = "Cancelled"

    def _calculate_net_amount(self):
        """Calculate net amount after discount."""
        if self.rate:
            discount = flt(self.discount_percent)
            self.net_amount = flt(self.rate) * (1 - discount / 100)

    def _validate_dates(self):
        """Ensure end_date is after start_date."""
        if self.start_date and self.end_date:
            if getdate(self.end_date) <= getdate(self.start_date):
                frappe.throw(_("End date must be after start date"))

    def _check_status(self):
        """Auto-set expired status."""
        if (
            self.docstatus == 1
            and self.end_date
            and getdate(self.end_date) < getdate(today())
            and self.status == "Active"
        ):
            self.status = "Expired"

    @frappe.whitelist()
    def populate_from_template(self):
        """Fill contract terms from selected template."""
        frappe.only_for(["ARKSpace User", "ARKSpace Manager", "System Manager"])

        if not self.contract_template:
            frappe.throw(_("Please select a Contract Template first"))

        template = frappe.get_doc("Contract Template", self.contract_template)
        context = self._get_template_context()

        if template.terms_ar:
            self.contract_terms_ar = frappe.render_template(
                template.terms_ar, context
            )
        if template.terms_en:
            self.contract_terms_en = frappe.render_template(
                template.terms_en, context
            )

        return {"message": _("Terms populated from template")}

    def _get_template_context(self):
        """Build context dictionary for template rendering."""
        return {
            "member_name": self.member_name or "",
            "member_email": self.member_email or "",
            "member_id": self.member or "",
            "member_phone": self.member_phone or "",
            "member_address": self.member_address or "",
            "space_name": self.space or "",
            "space_type": self.space_type or "",
            "branch": self.branch or "",
            "floor": self.floor or "",
            "unit_details": self.unit_details or "",
            "plan_name": self.membership_plan or "",
            "plan_type": "",
            "start_date": frappe.format(self.start_date, "Date") if self.start_date else "",
            "end_date": frappe.format(self.end_date, "Date") if self.end_date else "",
            "rate": frappe.format(self.rate, "Currency") if self.rate else "",
            "currency": self.currency or "EGP",
            "billing_cycle": self.billing_cycle or "",
            "net_amount": frappe.format(self.net_amount, "Currency") if self.net_amount else "",
            "deposit_amount": frappe.format(self.deposit_amount, "Currency") if self.deposit_amount else "",
            "contract_date": frappe.format(self.contract_date, "Date") if self.contract_date else "",
            "contract_number": self.name or "",
            "company_name": frappe.defaults.get_defaults().get("company", ""),
            "company_address": "",
        }
