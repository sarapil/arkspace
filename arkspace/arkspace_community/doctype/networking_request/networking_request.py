# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

"""Networking Request — طلب تواصل
Connection requests between workspace members.
"""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class NetworkingRequest(Document):
    def validate(self):
        if self.from_member == self.to_member:
            frappe.throw(_("Cannot send a networking request to yourself"))

        # Check for duplicate pending requests
        if self.is_new():
            existing = frappe.db.exists("Networking Request", {
                "from_member": self.from_member,
                "to_member": self.to_member,
                "status": "Pending",
            })
            if existing:
                frappe.throw(_("A pending request already exists"))

    @frappe.whitelist()
    def accept(self):
        """Accept the networking request."""
        frappe.only_for(["ARKSpace User", "ARKSpace Manager", "System Manager"])

        if frappe.session.user != self.to_member:
            frappe.throw(_("Only the recipient can accept this request"))
        self.status = "Accepted"
        self.responded_at = now_datetime()
        self.save(ignore_permissions=True)

        frappe.publish_realtime("networking_request_accepted", {
            "request": self.name,
            "from": self.from_member,
            "to": self.to_member,
        }, user=self.from_member)

        return {"status": "Accepted"}

    @frappe.whitelist()
    def decline(self):
        """Decline the networking request."""
        frappe.only_for(["ARKSpace User", "ARKSpace Manager", "System Manager"])

        if frappe.session.user != self.to_member:
            frappe.throw(_("Only the recipient can decline this request"))
        self.status = "Declined"
        self.responded_at = now_datetime()
        self.save(ignore_permissions=True)
        return {"status": "Declined"}
