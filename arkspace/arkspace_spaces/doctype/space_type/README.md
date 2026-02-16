# Space Type

> Auto-generated documentation

## Overview

No description provided.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| type_name | Data | Type Name |
| type_name_ar | Data | الاسم بالعربية |
| icon | Data | Icon |
| color | Color | Color |
| description | Text Editor | Description |
| default_capacity | Int | Default Capacity |
| hourly_booking | Check | Hourly Booking |
| daily_booking | Check | Daily Booking |
| monthly_booking | Check | Monthly Booking |


## Usage

```python
# Create
doc = frappe.new_doc("Space Type")
doc.insert()

# Query
records = frappe.get_all("Space Type")
```

## Related DocTypes

_Add related DocTypes here_

---
*Last updated: 2026-02-09 20:26:53.125578*
