# Workspace Tour

> Auto-generated documentation

## Overview

No description provided.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| lead | Link | Lead |
| lead_name | Data | Lead Name |
| branch | Link | Branch |
| assigned_to | Link | Assigned To |
| scheduled_date | Date | Date |
| scheduled_time | Time | Time |
| duration_minutes | Int | Duration (min) |
| status | Select | Status |
| spaces_to_show | Small Text | Spaces to Show (comma-separated names) |
| interest_level | Rating | Interest Level |
| feedback | Text Editor | Tour Feedback |
| outcome | Select | Outcome |
| follow_up_date | Date | Follow Up Date |
| converted_membership | Link | Converted Membership |


## Usage

```python
# Create
doc = frappe.new_doc("Workspace Tour")
doc.insert()

# Query
records = frappe.get_all("Workspace Tour")
```

## Related DocTypes

_Add related DocTypes here_

---
*Last updated: 2026-02-09 20:26:55.446016*
