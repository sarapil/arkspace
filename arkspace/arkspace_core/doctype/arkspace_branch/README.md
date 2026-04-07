# ARKSpace Branch

> Auto-generated documentation

## Overview

No description provided.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| branch_name | Data | Branch Name |
| branch_name_ar | Data | Branch Name (Arabic) |
| branch_code | Data | Branch Code |
| branch | Link | ERPNext Branch |
| company | Link | Company |
| is_active | Check | Active |
| address_line_1 | Data | Address Line 1 |
| address_line_2 | Data | Address Line 2 |
| city | Data | City |
| state | Data | State / Province |
| country | Link | Country |
| postal_code | Data | Postal Code |
| latitude | Float | Latitude |
| longitude | Float | Longitude |
| branch_manager | Link | Branch Manager |
| phone | Phone | Phone |
| email | Data | Email |
| website | Data | Website |
| operating_hours_start | Time | Opening Time |
| operating_hours_end | Time | Closing Time |
| timezone | Select | Timezone |
| working_days | Small Text | Working Days |
| total_desks | Int | Total Desks |
| total_offices | Int | Total Offices |
| total_meeting_rooms | Int | Total Meeting Rooms |
| max_capacity | Int | Max Capacity |
| current_occupancy | Int | Current Occupancy |
| default_currency | Link | Currency |
| default_rate_multiplier | Float | Rate Multiplier |
| allow_walkin_bookings | Check | Allow Walk-in Bookings |
| allow_day_passes | Check | Allow Day Passes |
| image | Attach Image | Branch Image |
| description | Text Editor | Description |
| description_ar | Text Editor | Description (Arabic) |


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
*Last updated: 2026-04-07 22:22:33.373566*
