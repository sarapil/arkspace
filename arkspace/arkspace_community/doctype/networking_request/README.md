# Networking Request

> Auto-generated documentation

## Overview

No description provided.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| from_member | Link | From |
| from_member_name | Data | From Name |
| to_member | Link | To |
| to_member_name | Data | To Name |
| message | Text | Message |
| branch | Link | Branch |
| status | Select | Status |
| responded_at | Datetime | Responded At |


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
*Last updated: 2026-04-07 22:22:35.028812*
