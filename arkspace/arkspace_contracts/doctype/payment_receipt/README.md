# Payment Receipt

> Auto-generated documentation

## Overview

No description provided.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| receipt_type | Select | Receipt Type |
| receipt_date | Date | Receipt Date |
| member | Link | Member |
| member_name | Data | Member Name |
| member_contract | Link | Contract |
| membership | Link | Membership |
| space_booking | Link | Booking |
| period_from | Date | From |
| period_to | Date | To |
| billing_cycle | Select | Billing Cycle |
| amount | Currency | Amount |
| currency | Link | Currency |
| payment_method | Select | Payment Method |
| reference_number | Data | Reference Number |
| payment_date | Date | Payment Date |
| notes | Small Text | Notes |
| amended_from | Link | Amended From |


## Usage

```python
# Create
doc = frappe.new_doc("Payment Receipt")
doc.insert()

# Query
records = frappe.get_all("Payment Receipt")
```

## Related DocTypes

_Add related DocTypes here_

---
*Last updated: 2026-04-07 22:22:34.416692*
