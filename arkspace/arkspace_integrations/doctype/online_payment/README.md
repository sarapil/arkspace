# Online Payment

> Auto-generated documentation

## Overview

No description provided.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| payment_id | Data | Payment ID |
| gateway | Select | Gateway |
| status | Select | Status |
| payment_for | Select | Payment For |
| reference_doctype | Link | Reference Type |
| reference_name | Dynamic Link | Reference |
| member | Link | Member |
| member_name | Data | Member Name |
| amount | Currency | Amount |
| currency | Link | Currency |
| gateway_fee | Currency | Gateway Fee |
| net_received | Currency | Net Received |
| exchange_rate | Float | Exchange Rate |
| base_amount | Currency | Base Amount |
| gateway_reference | Data | Gateway Reference |
| gateway_status | Data | Gateway Status |
| gateway_response_json | Code | Gateway Response |
| checkout_url | Data | Checkout URL |
| payment_method_type | Data | Payment Method |
| card_last_four | Data | Card Last 4 |
| initiated_at | Datetime | Initiated At |
| completed_at | Datetime | Completed At |
| expires_at | Datetime | Expires At |
| cancelled_at | Datetime | Cancelled At |
| sales_invoice | Link | Sales Invoice |
| payment_receipt | Link | Payment Receipt |
| payment_entry | Link | Payment Entry |
| notes | Small Text | Notes |
| amended_from | Link | Amended From |


## Usage

```python
# Create
doc = frappe.new_doc("Online Payment")
doc.insert()

# Query
records = frappe.get_all("Online Payment")
```

## Related DocTypes

_Add related DocTypes here_

---
*Last updated: 2026-04-07 22:22:34.102114*
