# Space Booking

> Auto-generated documentation

## Overview

No description provided.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| booking_id | Data | Booking ID |
| space | Link | Space |
| member | Link | Member |
| member_name | Data | Member Name |
| member_email | Data | Member Email |
| booking_type | Select | Booking Type |
| start_datetime | Datetime | Start |
| end_datetime | Datetime | End |
| duration_hours | Float | Duration (hours) |
| booking_amenities | Table | Amenities |
| amenity_total | Currency | Amenity Total |
| rate | Currency | Rate |
| total_amount | Currency | Total Amount |
| discount_percent | Percent | Discount % |
| net_amount | Currency | Net Amount |
| status | Select | Status |
| checked_in_at | Datetime | Checked In At |
| checked_out_at | Datetime | Checked Out At |
| qr_code | Attach Image | QR Code |
| qr_token | Data | QR Token |
| sales_invoice | Link | Sales Invoice |
| amended_from | Link | Amended From |


## Usage

```python
# Create
doc = frappe.new_doc("Space Booking")
doc.insert()

# Query
records = frappe.get_all("Space Booking")
```

## Related DocTypes

_Add related DocTypes here_

---
*Last updated: 2026-03-21 11:34:33.681188*
