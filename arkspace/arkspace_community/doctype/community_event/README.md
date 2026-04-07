# Community Event

> Auto-generated documentation

## Overview

No description provided.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| event_name | Data | Event Name |
| event_name_ar | Data | Event Name (Arabic) |
| event_type | Select | Type |
| organizer | Link | Organizer |
| organizer_name | Data | Organizer Name |
| branch | Link | Branch |
| space | Link | Space |
| start_datetime | Datetime | Start |
| end_datetime | Datetime | End |
| registration_deadline | Datetime | Registration Deadline |
| description | Text Editor | Description |
| image | Attach Image | Image |
| max_attendees | Int | Max Attendees |
| current_attendees | Int | Registered |
| registration_required | Check | Registration Required |
| is_free | Check | Free Event |
| fee | Currency | Fee |
| status | Select | Status |
| is_featured | Check | Featured |


## Usage

```python
# Create
doc = frappe.new_doc("Community Event")
doc.insert()

# Query
records = frappe.get_all("Community Event")
```

## Related DocTypes

_Add related DocTypes here_

---
*Last updated: 2026-04-07 22:22:35.332026*
