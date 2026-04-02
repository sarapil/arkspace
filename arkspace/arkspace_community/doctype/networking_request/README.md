# Networking Request

> Auto-generated documentation

## Overview

No description provided.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| from_member | Link | From / من |
| from_member_name | Data | From Name / اسم المرسل |
| to_member | Link | To / إلى |
| to_member_name | Data | To Name / اسم المستلم |
| message | Text | Message / الرسالة |
| branch | Link | Branch / الفرع |
| status | Select | Status / الحالة |
| responded_at | Datetime | Responded At / تاريخ الرد |


## Usage

```python
# Create
doc = frappe.new_doc("Networking Request")
doc.insert()

# Query
records = frappe.get_all("Networking Request")
```

## Related DocTypes

_Add related DocTypes here_

---
*Last updated: 2026-03-21 12:53:07.070791*
