# Pricing Rule

> Auto-generated documentation

## Overview

No description provided.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| rule_name | Data | Rule Name |
| rule_type | Select | Rule Type |
| enabled | Check | Enabled |
| priority | Int | Priority |
| description | Small Text | Description |
| apply_to_all_spaces | Check | All Spaces |
| space_type | Link | Space Type |
| specific_space | Link | Specific Space |
| apply_to_all_booking_types | Check | All Booking Types |
| booking_type | Select | Booking Type |
| membership_plan | Link | Membership Plan |
| condition_type | Select | Condition |
| time_start | Time | Start Time |
| time_end | Time | End Time |
| day_of_week | Select | Day of Week |
| date_start | Date | Date From |
| date_end | Date | Date To |
| min_hours | Float | Min Hours |
| max_hours | Float | Max Hours |
| member_tier | Select | Member Tier |
| adjustment_type | Select | Adjustment Type |
| adjustment_value | Float | Value |
| max_adjustment_amount | Currency | Max Adjustment Cap |
| min_rate | Currency | Minimum Rate |
| stackable | Check | Stackable |
| stacking_group | Data | Stacking Group |
| valid_from | Datetime | Valid From |
| valid_to | Datetime | Valid To |
| amended_from | Link | Amended From |


## Usage

```python
# Create
doc = frappe.new_doc("Pricing Rule")
doc.insert()

# Query
records = frappe.get_all("Pricing Rule")
```

## Related DocTypes

_Add related DocTypes here_

---
*Last updated: 2026-04-10 00:57:32.405086*
