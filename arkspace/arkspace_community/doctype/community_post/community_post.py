# Copyright (c) 2026, ARKSpace Team and contributors
# For license information, please see license.txt

"""Community Post — منشور مجتمعي
Posts, discussions, announcements, questions in the ARKSpace community.
"""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint


class CommunityPost(Document):
    def validate(self):
        if not self.author:
            self.author = frappe.session.user
        if not self.author_name:
            self.author_name = frappe.db.get_value("User", self.author, "full_name")

    def on_update(self):
        # Update comment count
        self.db_set("comments_count", frappe.db.count("Comment", {
            "reference_doctype": "Community Post",
            "reference_name": self.name,
            "comment_type": "Comment",
        }))

    @frappe.whitelist()
    def toggle_like(self):
        """Toggle like for the current user."""
        frappe.only_for(["ARKSpace Manager", "System Manager"])

        user = frappe.session.user
        existing = frappe.db.exists("Comment", {
            "reference_doctype": "Community Post",
            "reference_name": self.name,
            "comment_type": "Like",
            "comment_email": user,
        })

        if existing:
            frappe.delete_doc("Comment", existing, ignore_permissions=True)
            self.db_set("likes_count", max(0, cint(self.likes_count) - 1))
            return {"liked": False, "count": max(0, cint(self.likes_count) - 1)}
        else:
            frappe.get_doc({
                "doctype": "Comment",
                "comment_type": "Like",
                "reference_doctype": "Community Post",
                "reference_name": self.name,
                "comment_email": user,
                "content": _("Liked"),
            }).insert(ignore_permissions=True)
            self.db_set("likes_count", cint(self.likes_count) + 1)
            return {"liked": True, "count": cint(self.likes_count) + 1}

    @frappe.whitelist()
    def increment_views(self):
        """Increment view count."""
        frappe.only_for(["ARKSpace User", "ARKSpace Manager", "System Manager"])

        self.db_set("views_count", cint(self.views_count) + 1)
