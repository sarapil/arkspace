# Day Pass

> Auto-generated documentation

## Overview

No description provided.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| guest_name | Data | Guest Name |
| guest_email | Data | Email |
| guest_phone | Data | Phone |
| guest_company | Data | Company |
| guest_type | Select | Guest Type |
| existing_member | Link | Referred By / Corporate Account |
| pass_type | Select | Pass Type |
| pass_date | Date | Date |
| start_time | Time | Start Time |
| end_time | Time | End Time |
| duration_hours | Float | Duration (Hours) |
| space | Link | Space |
| branch | Link | Branch |
| seat_number | Data | Seat / Desk Number |
| rate | Currency | Rate |
| discount_percent | Percent | Discount % |
| net_amount | Currency | Net Amount |
| payment_method | Select | Payment Method |
| status | Select | Status |
| checked_in_at | Datetime | Checked In At |
| checked_out_at | Datetime | Checked Out At |
| qr_code | Attach Image | QR Code |
| qr_token | Data | QR Token |
| converted_to_membership | Check | Converted to Membership |
| membership | Link | Membership |
| membership_credit_applied | Currency | Credit Applied to Membership |
| is_trial | Check | Is Trial Pass |
| trial_plan | Link | Trial for Plan |
| trial_days_remaining | Int | Trial Days Remaining |
| sales_invoice | Link | Sales Invoice |
| source | Select | Source |
| referral_code | Data | Referral Code |
| notes | Small Text | Notes |
| amended_from | Link | Amended From |


## Usage

```python
# Create
doc = frappe.new_doc("Day Pass")
doc.insert()

# Query
records = frappe.get_all("Day Pass")
```

## Related DocTypes

_Add related DocTypes here_

---
*Last updated: 2026-03-21 11:34:34.967062*
