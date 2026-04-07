# Analytics Snapshot

> Auto-generated documentation

## Overview

No description provided.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| snapshot_date | Date | Date |
| branch | Link | Branch |
| period_type | Select | Period |
| snapshot_id | Data | Snapshot ID |
| total_spaces | Int | Total Spaces |
| occupied_spaces | Int | Occupied |
| available_spaces | Int | Available |
| occupancy_rate | Percent | Occupancy Rate |
| maintenance_spaces | Int | Maintenance |
| reserved_spaces | Int | Reserved |
| total_bookings | Int | Total Bookings |
| new_bookings | Int | New Bookings |
| cancelled_bookings | Int | Cancelled |
| no_shows | Int | No Shows |
| checked_in_count | Int | Checked In |
| avg_booking_duration | Float | Avg Duration (hrs) |
| active_members | Int | Active Members |
| new_members | Int | New Members |
| churned_members | Int | Churned |
| retention_rate | Percent | Retention Rate |
| total_revenue | Currency | Total Revenue |
| booking_revenue | Currency | Booking Revenue |
| membership_revenue | Currency | Membership Revenue |
| day_pass_revenue | Currency | Day Pass Revenue |
| other_revenue | Currency | Other Revenue |
| avg_revenue_per_booking | Currency | Avg Revenue/Booking |
| day_pass_count | Int | Day Passes |
| visitor_count | Int | Visitors |
| trial_conversions | Int | Trial Conversions |
| peak_hour | Int | Peak Hour |
| popular_space_type | Data | Popular Space Type |
| popular_booking_type | Data | Popular Booking Type |
| busiest_day | Data | Busiest Day |


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
*Last updated: 2026-04-07 22:22:32.976869*
