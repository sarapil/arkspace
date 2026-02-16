# Amenity

> Auto-generated documentation

## Overview

No description provided.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| amenity_name | Data | Amenity Name |
| amenity_name_ar | Data | الاسم بالعربية |
| icon | Data | Icon |
| color | Color | Color |
| hourly_price | Currency | Hourly Price |
| daily_price | Currency | Daily Price |
| monthly_price | Currency | Monthly Price |
| is_complimentary | Check | Complimentary |
| description | Small Text | Description |


## Usage

```python
# Create
doc = frappe.new_doc("Amenity")
doc.insert()

# Query
records = frappe.get_all("Amenity")
```

## Related DocTypes

_Add related DocTypes here_

---
*Last updated: 2026-02-15 14:44:00.192484*
