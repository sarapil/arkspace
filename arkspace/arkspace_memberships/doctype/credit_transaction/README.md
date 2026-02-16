# Credit Transaction

> Auto-generated documentation

## Overview

No description provided.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| transaction_type | Select | Type |
| credits | Float | Credits |
| description | Small Text | Description |
| reference_doctype | Link | Reference Type |
| reference_name | Dynamic Link | Reference Name |
| transaction_date | Datetime | Date |


## Usage

```python
# Create
doc = frappe.new_doc("Credit Transaction")
doc.insert()

# Query
records = frappe.get_all("Credit Transaction")
```

## Related DocTypes

_Add related DocTypes here_

---
*Last updated: 2026-02-09 20:26:54.287079*
