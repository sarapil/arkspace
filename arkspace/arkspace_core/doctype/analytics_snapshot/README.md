# Analytics Snapshot

> Auto-generated documentation

## Overview

No description provided.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| snapshot_date | Date | Date / التاريخ |
| branch | Link | Branch / الفرع |
| period_type | Select | Period / الفترة |
| snapshot_id | Data | Snapshot ID |
| total_spaces | Int | Total Spaces / إجمالي المساحات |
| occupied_spaces | Int | Occupied / مشغولة |
| available_spaces | Int | Available / متاحة |
| occupancy_rate | Percent | Occupancy Rate / نسبة الإشغال |
| maintenance_spaces | Int | Maintenance / صيانة |
| reserved_spaces | Int | Reserved / محجوزة |
| total_bookings | Int | Total Bookings / إجمالي الحجوزات |
| new_bookings | Int | New Bookings / حجوزات جديدة |
| cancelled_bookings | Int | Cancelled / ملغاة |
| no_shows | Int | No Shows / لم يحضر |
| checked_in_count | Int | Checked In / تسجيل دخول |
| avg_booking_duration | Float | Avg Duration (hrs) / متوسط المدة |
| active_members | Int | Active Members / أعضاء نشطون |
| new_members | Int | New Members / أعضاء جدد |
| churned_members | Int | Churned / مغادرون |
| retention_rate | Percent | Retention Rate / معدل الاحتفاظ |
| total_revenue | Currency | Total Revenue / إجمالي الإيرادات |
| booking_revenue | Currency | Booking Revenue / إيرادات الحجوزات |
| membership_revenue | Currency | Membership Revenue / إيرادات العضويات |
| day_pass_revenue | Currency | Day Pass Revenue / إيرادات التصاريح |
| other_revenue | Currency | Other Revenue / إيرادات أخرى |
| avg_revenue_per_booking | Currency | Avg Revenue/Booking / متوسط الإيرادات لكل حجز |
| day_pass_count | Int | Day Passes / تصاريح اليوم |
| visitor_count | Int | Visitors / الزوار |
| trial_conversions | Int | Trial Conversions / تحويلات التجربة |
| peak_hour | Int | Peak Hour / ساعة الذروة |
| popular_space_type | Data | Popular Space Type / نوع المساحة الأكثر طلباً |
| popular_booking_type | Data | Popular Booking Type / نوع الحجز الأكثر شيوعاً |
| busiest_day | Data | Busiest Day / أكثر الأيام ازدحاماً |


## Usage

```python
# Create
doc = frappe.new_doc("Analytics Snapshot")
doc.insert()

# Query
records = frappe.get_all("Analytics Snapshot")
```

## Related DocTypes

_Add related DocTypes here_

---
*Last updated: 2026-03-21 11:34:32.127686*
