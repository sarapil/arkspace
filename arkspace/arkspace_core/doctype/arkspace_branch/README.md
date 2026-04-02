# ARKSpace Branch

> Auto-generated documentation

## Overview

No description provided.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| branch_name | Data | Branch Name / اسم الفرع |
| branch_name_ar | Data | Branch Name (Arabic) / الاسم بالعربية |
| branch_code | Data | Branch Code / رمز الفرع |
| branch | Link | ERPNext Branch / فرع ERPNext |
| company | Link | Company / الشركة |
| is_active | Check | Active / نشط |
| address_line_1 | Data | Address Line 1 / العنوان 1 |
| address_line_2 | Data | Address Line 2 / العنوان 2 |
| city | Data | City / المدينة |
| state | Data | State / Province / الولاية |
| country | Link | Country / الدولة |
| postal_code | Data | Postal Code / الرمز البريدي |
| latitude | Float | Latitude / خط العرض |
| longitude | Float | Longitude / خط الطول |
| branch_manager | Link | Branch Manager / مدير الفرع |
| phone | Phone | Phone / الهاتف |
| email | Data | Email / البريد الإلكتروني |
| website | Data | Website / الموقع الإلكتروني |
| operating_hours_start | Time | Opening Time / وقت الافتتاح |
| operating_hours_end | Time | Closing Time / وقت الإغلاق |
| timezone | Select | Timezone / المنطقة الزمنية |
| working_days | Small Text | Working Days / أيام العمل |
| total_desks | Int | Total Desks / إجمالي المكاتب |
| total_offices | Int | Total Offices / إجمالي المكاتب الخاصة |
| total_meeting_rooms | Int | Total Meeting Rooms / إجمالي قاعات الاجتماعات |
| max_capacity | Int | Max Capacity / السعة القصوى |
| current_occupancy | Int | Current Occupancy / الإشغال الحالي |
| default_currency | Link | Currency / العملة |
| default_rate_multiplier | Float | Rate Multiplier / مضاعف السعر |
| allow_walkin_bookings | Check | Allow Walk-in Bookings / السماح بالحجوزات المباشرة |
| allow_day_passes | Check | Allow Day Passes / السماح بتصاريح اليوم |
| image | Attach Image | Branch Image / صورة الفرع |
| description | Text Editor | Description / الوصف |
| description_ar | Text Editor | Description (Arabic) / الوصف بالعربية |


## Usage

```python
# Create
doc = frappe.new_doc("ARKSpace Branch")
doc.insert()

# Query
records = frappe.get_all("ARKSpace Branch")
```

## Related DocTypes

_Add related DocTypes here_

---
*Last updated: 2026-03-21 12:53:04.781443*
