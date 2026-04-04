# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

"""Analytics Snapshot — لقطة تحليلية
Stores daily, weekly, or monthly analytics snapshots for historical reporting.
"""

import frappe
from frappe.model.document import Document


class AnalyticsSnapshot(Document):
    def validate(self):
        if not self.snapshot_id:
            branch_slug = (self.branch or "ALL").replace(" ", "-")
            self.snapshot_id = f"{self.snapshot_date}-{branch_slug}-{self.period_type}"

    def before_insert(self):
        # Prevent duplicate snapshots for the same date/branch/period
        existing = frappe.db.exists("Analytics Snapshot", {
            "snapshot_date": self.snapshot_date,
            "branch": self.branch or "",
            "period_type": self.period_type,
        })
        if existing:
            frappe.throw(
                f"Analytics Snapshot already exists for {self.snapshot_date} "
                f"({self.branch or 'All Branches'}, {self.period_type})"
            )
