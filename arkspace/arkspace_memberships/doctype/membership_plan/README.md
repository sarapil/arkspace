# Membership Plan

> Auto-generated documentation

## Overview

No description provided.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| plan_name | Data | Plan Name |
| plan_name_ar | Data | Plan Name (Arabic) |
| plan_type | Select | Plan Type |
| space_type | Link | Space Type |
| is_active | Check | Active |
| monthly_price | Currency | Monthly Price |
| quarterly_price | Currency | Quarterly Price |
| yearly_price | Currency | Yearly Price |
| currency | Link | Currency |
| setup_fee | Currency | Setup Fee |
| included_hours | Int | Included Hours / Month |
| included_credits | Int | Included Credits |
| max_guests | Int | Max Guests |
| meeting_room_hours | Int | Meeting Room Hours / Month |
| printing_pages | Int | Printing Pages / Month |
| storage_gb | Float | Cloud Storage (GB) |
| description | Text Editor | Description |
| description_ar | Text Editor | Description (Arabic) |
| enable_trial | Check | Enable Trial / تفعيل التجربة |
| trial_days | Int | Trial Days / أيام التجربة |
| trial_price | Currency | Trial Price / سعر التجربة |
| trial_includes_benefits | Check | Trial Includes Benefits / التجربة تشمل المزايا |


## Usage

```python
# Create
doc = frappe.new_doc("Membership Plan")
doc.insert()

# Query
records = frappe.get_all("Membership Plan")
```

## Related DocTypes

_Add related DocTypes here_

---
*Last updated: 2026-03-21 11:34:35.556811*
