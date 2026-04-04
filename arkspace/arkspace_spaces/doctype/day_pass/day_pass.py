# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

"""Day Pass DocType controller
تصريح اليوم — منطق الأعمال

Handles day-pass lifecycle: creation, validation, check-in/out,
expiry, and optional conversion to full membership.
"""

import frappe
from frappe import _
from frappe.utils import flt, get_time, getdate, now_datetime, nowdate, time_diff_in_hours


class DayPass(frappe.model.document.Document):
    """Day Pass — single-day or hourly workspace access."""

    # ── Lifecycle Hooks ──────────────────────────────────────────────

    def validate(self):
        self._calculate_duration()
        self._calculate_net_amount()
        self._validate_pass_date()

    def on_submit(self):
        self.status = "Active"
        self._generate_qr()

    def on_cancel(self):
        self.status = "Cancelled"

    # ── Public Methods ───────────────────────────────────────────────

    def check_in(self):
        """Mark day pass as checked in."""
        if self.status != "Active":
            frappe.throw(
                _("Day pass must be Active to check in (current: {0})").format(self.status)
            )
        if getdate(self.pass_date) != getdate(nowdate()):
            frappe.throw(_("This day pass is not valid today"))

        self.status = "Checked In"
        self.checked_in_at = now_datetime()
        if not self.start_time:
            self.start_time = now_datetime().strftime("%H:%M:%S")
        self.save(ignore_permissions=True)

        frappe.publish_realtime(
            "day_pass_checked_in",
            {"day_pass": self.name, "guest_name": self.guest_name},
            after_commit=True,
        )

    def check_out(self):
        """Mark day pass as checked out."""
        if self.status != "Checked In":
            frappe.throw(_("Day pass is not checked in"))

        self.status = "Checked Out"
        self.checked_out_at = now_datetime()
        if not self.end_time:
            self.end_time = now_datetime().strftime("%H:%M:%S")
        self._calculate_duration()
        self.save(ignore_permissions=True)

        frappe.publish_realtime(
            "day_pass_checked_out",
            {"day_pass": self.name, "guest_name": self.guest_name},
            after_commit=True,
        )

    def convert_to_membership(self, plan, billing_cycle="Monthly"):
        """Convert this day pass into a full membership.

        Applies the day-pass amount as credit toward the first invoice.

        Args:
            plan: Membership Plan name
            billing_cycle: Monthly / Quarterly / Yearly

        Returns:
            Membership name
        """
        if self.converted_to_membership:
            frappe.throw(_("This day pass has already been converted"))

        # Resolve or create Customer for the guest
        customer = self._get_or_create_customer()

        membership = frappe.get_doc({
            "doctype": "Membership",
            "member": customer,
            "membership_plan": plan,
            "billing_cycle": billing_cycle,
            "start_date": nowdate(),
        })
        membership.insert(ignore_permissions=True)
        membership.submit()

        # Mark conversion
        self.converted_to_membership = 1
        self.membership = membership.name
        self.membership_credit_applied = self.net_amount or 0
        self.save(ignore_permissions=True)

        return membership.name

    # ── Private Helpers ──────────────────────────────────────────────

    def _calculate_duration(self):
        """Calculate duration in hours from start_time/end_time."""
        if self.start_time and self.end_time:
            start = get_time(self.start_time)
            end = get_time(self.end_time)
            today = getdate(self.pass_date or nowdate())
            from datetime import datetime
            dt_start = datetime.combine(today, start)
            dt_end = datetime.combine(today, end)
            self.duration_hours = flt(
                time_diff_in_hours(dt_end, dt_start), 2
            )
        elif self.pass_type == "Full Day":
            self.duration_hours = 8
        elif self.pass_type == "Half Day":
            self.duration_hours = 4
        elif self.pass_type == "Evening":
            self.duration_hours = 4

    def _calculate_net_amount(self):
        """Apply discount to rate."""
        rate = flt(self.rate)
        discount = flt(self.discount_percent)
        self.net_amount = rate - (rate * discount / 100)

    def _validate_pass_date(self):
        """Ensure pass date is not in the past (for new passes)."""
        if self.is_new() and self.pass_date:
            if getdate(self.pass_date) < getdate(nowdate()):
                frappe.throw(_("Day pass date cannot be in the past"))

    def _generate_qr(self):
        """Generate a QR code for quick check-in."""
        try:
            from arkspace.arkspace_spaces.qr_checkin import _create_qr_image
        except ImportError:
            return

        import hashlib
        secret = frappe.utils.password.get_encryption_key()
        token = hashlib.sha256(
            f"{secret}:{self.name}:{frappe.conf.db_name}".encode()
        ).hexdigest()[:32]
        self.qr_token = token

        url = frappe.utils.get_url(
            f"/api/method/arkspace.arkspace_spaces.day_pass_api"
            f".scan_day_pass?token={token}&pass_name={self.name}"
        )

        import json as _json
        qr_data = _json.dumps({
            "type": "arkspace_day_pass",
            "pass": self.name,
            "url": url,
        })
        img_bytes = _create_qr_image(qr_data)

        from frappe.utils.file_manager import save_file
        filename = f"day-pass-qr-{self.name}.png"
        file_doc = save_file(
            filename, img_bytes, "Day Pass", self.name, is_private=0,
        )
        self.qr_code = file_doc.file_url

    def _get_or_create_customer(self):
        """Find or create a Customer record for the guest.

        Returns:
            Customer name
        """
        # Try matching by email first
        if self.guest_email:
            existing = frappe.db.get_value(
                "Customer", {"email_id": self.guest_email}, "name"
            )
            if existing:
                return existing

        # Create new customer
        customer = frappe.get_doc({
            "doctype": "Customer",
            "customer_name": self.guest_name,
            "customer_type": "Individual",
            "customer_group": frappe.db.get_single_value(
                "Selling Settings", "customer_group"
            ) or "Individual",
            "territory": frappe.db.get_single_value(
                "Selling Settings", "territory"
            ) or "All Territories",
            "email_id": self.guest_email,
            "mobile_no": self.guest_phone,
        })
        customer.insert(ignore_permissions=True)
        return customer.name
