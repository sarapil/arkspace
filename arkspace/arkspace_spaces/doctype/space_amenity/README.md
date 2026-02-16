# Space Amenity

> Auto-generated documentation

## Overview

No description provided.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| amenity | Link | Amenity |
| quantity | Int | Qty |
| rate | Currency | Rate |
| amount | Currency | Amount |
| notes | Data | Notes |


## Usage

```python
# Create
doc = frappe.new_doc("Space Amenity")
doc.insert()

# Query
records = frappe.get_all("Space Amenity")
```

## Related DocTypes

_Add related DocTypes here_

---
*Last updated: 2026-02-15 14:44:01.077973*
