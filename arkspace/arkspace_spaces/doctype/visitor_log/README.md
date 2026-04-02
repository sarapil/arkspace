# Visitor Log

> Auto-generated documentation

## Overview

No description provided.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| visitor_name | Data | Visitor Name |
| visitor_email | Data | Visitor Email |
| visitor_phone | Data | Visitor Phone |
| visitor_company | Data | Visitor Company |
| id_type | Select | ID Type |
| id_number | Data | ID Number |
| visitor_image | Attach Image | Photo |
| purpose | Select | Purpose |
| purpose_details | Small Text | Purpose Details |
| host | Link | Host (Member) |
| host_name | Data | Host Name |
| host_department | Data | Host Department |
| visiting_space | Link | Space |
| visiting_branch | Link | Branch |
| expected_arrival | Datetime | Expected Arrival |
| expected_departure | Datetime | Expected Departure |
| status | Select | Status |
| checked_in_at | Datetime | Checked In At |
| checked_out_at | Datetime | Checked Out At |
| badge_number | Data | Badge Number |
| badge_printed | Check | Badge Printed |
| qr_token | Data | QR Token |
| preregistered | Check | Pre-registered |
| preregistered_by | Link | Pre-registered By |
| approval_status | Select | Approval Status |
| approved_by | Link | Approved By |
| notes | Text Editor | Notes |
| amended_from | Link | Amended From |


## Usage

```python
# Create
doc = frappe.new_doc("Visitor Log")
doc.insert()

# Query
records = frappe.get_all("Visitor Log")
```

## Related DocTypes

_Add related DocTypes here_

---
*Last updated: 2026-03-21 11:34:33.221559*
