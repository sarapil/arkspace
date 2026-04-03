# Pricing Rule

> Auto-generated documentation

## Overview

No description provided.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| rule_name | Data | Rule Name / اسم القاعدة |
| rule_type | Select | Rule Type / نوع القاعدة |
| enabled | Check | Enabled / مفعّل |
| priority | Int | Priority / الأولوية |
| description | Small Text | Description / الوصف |
| apply_to_all_spaces | Check | All Spaces / جميع المساحات |
| space_type | Link | Space Type / نوع المساحة |
| specific_space | Link | Specific Space / مساحة محددة |
| apply_to_all_booking_types | Check | All Booking Types / جميع أنواع الحجز |
| booking_type | Select | Booking Type / نوع الحجز |
| membership_plan | Link | Membership Plan / خطة العضوية |
| condition_type | Select | Condition / الشرط |
| time_start | Time | Start Time / وقت البداية |
| time_end | Time | End Time / وقت النهاية |
| day_of_week | Select | Day of Week / يوم الأسبوع |
| date_start | Date | Date From / من تاريخ |
| date_end | Date | Date To / إلى تاريخ |
| min_hours | Float | Min Hours / الحد الأدنى (ساعات) |
| max_hours | Float | Max Hours / الحد الأقصى (ساعات) |
| member_tier | Select | Member Tier / مستوى العضوية |
| adjustment_type | Select | Adjustment Type / نوع التعديل |
| adjustment_value | Float | Value / القيمة |
| max_adjustment_amount | Currency | Max Adjustment Cap / حد أقصى للتعديل |
| min_rate | Currency | Minimum Rate / الحد الأدنى للسعر |
| stackable | Check | Stackable / قابل للتراكم |
| stacking_group | Data | Stacking Group / مجموعة التراكم |
| valid_from | Datetime | Valid From / صالح من |
| valid_to | Datetime | Valid To / صالح حتى |
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
*Last updated: 2026-04-03 04:21:05.349136*
