# Copyright (c) 2026, ARKSpace Team and contributors
# For license information, please see license.txt

"""ARKSpace Branch — فرع ARKSpace
Extended branch management with workspace-specific settings,
operating hours, location, and capacity tracking.
"""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint


class ARKSpaceBranch(Document):
    def validate(self):
        self._validate_code()
        self._validate_hours()
        self._calculate_capacity()

    def _validate_code(self):
        if not self.branch_code:
            # Auto-generate code from name
            self.branch_code = self.branch_name[:3].upper().replace(" ", "")

    def _validate_hours(self):
        if self.operating_hours_start and self.operating_hours_end:
            if str(self.operating_hours_start) >= str(self.operating_hours_end):
                frappe.throw(_("Opening time must be before closing time"))

    def _calculate_capacity(self):
        """Auto-calculate max capacity from linked spaces."""
        spaces = frappe.get_all(
            "Co-working Space",
            filters={"branch": self.branch or self.branch_name},
            fields=["capacity"],
        )
        self.max_capacity = sum(cint(s.capacity) for s in spaces)
        self.current_occupancy = frappe.db.count(
            "Co-working Space",
            {"branch": self.branch or self.branch_name, "status": "Occupied"},
        ) or 0

    def on_update(self):
        # Sync to ERPNext Branch if linked
        if self.branch and frappe.db.exists("Branch", self.branch):
            frappe.db.set_value("Branch", self.branch, "branch", self.branch_name)

    @frappe.whitelist()
    def recalculate_capacity(self):
        """Recalculate capacity from linked spaces."""
        self._calculate_capacity()
        self.save()
        return {
            "max_capacity": self.max_capacity,
            "current_occupancy": self.current_occupancy,
        }
