# Copyright (c) 2026, ARKSpace Team and contributors
# For license information, please see license.txt

"""Community Event — فعالية مجتمعية
Meetups, workshops, hackathons, networking events.
"""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint, now_datetime


class CommunityEvent(Document):
    def validate(self):
        self._validate_dates()
        self._update_status()

    def _validate_dates(self):
        if self.start_datetime and self.end_datetime:
            if self.start_datetime >= self.end_datetime:
                frappe.throw(_("End time must be after start time"))

    def _update_status(self):
        now = now_datetime()
        if self.status not in ("Cancelled", "Draft"):
            if now > self.end_datetime:
                self.status = "Completed"
            elif now >= self.start_datetime:
                self.status = "In Progress"
            elif cint(self.current_attendees) >= cint(self.max_attendees):
                self.status = "Full"
            elif self.registration_required:
                self.status = "Open for Registration"
            else:
                self.status = "Upcoming"

    @frappe.whitelist()
    def register_attendee(self, user=None):
        """Register a user for this event."""
        frappe.only_for(["ARKSpace User", "ARKSpace Manager", "System Manager"])

        user = user or frappe.session.user

        if cint(self.current_attendees) >= cint(self.max_attendees) and cint(self.max_attendees) > 0:
            frappe.throw(_("This event is full"))

        # Check if already registered
        if frappe.db.exists("Comment", {
            "reference_doctype": "Community Event",
            "reference_name": self.name,
            "comment_type": "Info",
            "comment_email": user,
            "content": ["like", "%REGISTERED%"],
        }):
            frappe.throw(_("You are already registered for this event"))

        frappe.get_doc({
            "doctype": "Comment",
            "comment_type": "Info",
            "reference_doctype": "Community Event",
            "reference_name": self.name,
            "comment_email": user,
            "content": f"REGISTERED: {user}",
        }).insert(ignore_permissions=True)

        self.db_set("current_attendees", cint(self.current_attendees) + 1)

        frappe.publish_realtime("event_registration", {
            "event": self.name,
            "user": user,
            "attendees": cint(self.current_attendees) + 1,
        })

        return {"status": "registered", "attendees": cint(self.current_attendees) + 1}

    @frappe.whitelist()
    def cancel_registration(self, user=None):
        """Cancel a user's registration."""
        frappe.only_for(["ARKSpace Manager", "System Manager"])

        user = user or frappe.session.user

        existing = frappe.db.get_value("Comment", {
            "reference_doctype": "Community Event",
            "reference_name": self.name,
            "comment_type": "Info",
            "comment_email": user,
            "content": ["like", "%REGISTERED%"],
        })

        if not existing:
            frappe.throw(_("You are not registered for this event"))

        frappe.delete_doc("Comment", existing, ignore_permissions=True)
        self.db_set("current_attendees", max(0, cint(self.current_attendees) - 1))

        return {"status": "cancelled", "attendees": max(0, cint(self.current_attendees) - 1)}
