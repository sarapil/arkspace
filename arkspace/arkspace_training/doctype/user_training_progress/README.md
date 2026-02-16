# User Training Progress

> Auto-generated documentation

## Overview

No description provided.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| naming_series | Select | Naming Series |
| user | Link | User |
| member | Link | Member (Customer) |
| training_module | Link | Training Module |
| training_session | Link | Training Session |
| status | Select | Status |
| progress_percent | Percent | Progress % |
| score | Float | Score |
| enrollment_date | Date | Enrollment Date |
| completion_date | Date | Completion Date |
| badge | Link | Awarded Badge |
| badge_awarded_on | Date | Badge Awarded On |
| feedback | Small Text | Feedback |
| rating | Rating | Rating |
| notes | Text | Internal Notes |


## Usage

```python
# Create
doc = frappe.new_doc("User Training Progress")
doc.insert()

# Query
records = frappe.get_all("User Training Progress")
```

## Related DocTypes

_Add related DocTypes here_

---
*Last updated: 2026-02-09 23:14:12.855702*
