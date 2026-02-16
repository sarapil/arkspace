# Co-working Space

> Auto-generated documentation

## Overview

No description provided.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| space_name | Data | Space Name |
| space_name_ar | Data | الاسم بالعربية |
| space_type | Link | Space Type |
| branch | Link | Branch |
| floor | Data | Floor |
| space_number | Data | Space Number |
| capacity | Int | Capacity |
| area_sqm | Float | Area (sqm) |
| hourly_rate | Currency | Hourly Rate |
| daily_rate | Currency | Daily Rate |
| monthly_rate | Currency | Monthly Rate |
| status | Select | Status |
| current_member | Link | Current Member |
| amenities | Table | Amenities |
| main_image | Attach Image | Main Image |
| gallery | Table | Gallery |


## Usage

```python
# Create
doc = frappe.new_doc("Co-working Space")
doc.insert()

# Query
records = frappe.get_all("Co-working Space")
```

## Related DocTypes

_Add related DocTypes here_

---
*Last updated: 2026-02-09 23:21:54.685819*
