# Training Session

> Auto-generated documentation

## Overview

No description provided.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| naming_series | Select | Naming Series |
| title | Data | Session Title |
| training_module | Link | Training Module |
| status | Select | Status |
| session_date | Date | Session Date |
| start_time | Time | Start Time |
| end_time | Time | End Time |
| venue | Data | Venue Name |
| space | Link | Space |
| branch | Link | Branch |
| max_participants | Int | Max Participants |
| registered_count | Int | Registered |
| instructor | Data | Instructor |
| description | Text Editor | Description |
| notes | Text | Session Notes |
| is_online | Check | Online Session |
| meeting_url | Data | Meeting URL |
| is_free | Check | Free Session |
| fee_amount | Currency | Fee Amount |
| amended_from | Link | Amended From |


## Usage

```python
# Create
doc = frappe.new_doc("Training Session")
doc.insert()

# Query
records = frappe.get_all("Training Session")
```

## Related DocTypes

_Add related DocTypes here_

---
*Last updated: 2026-02-09 23:14:13.265127*
