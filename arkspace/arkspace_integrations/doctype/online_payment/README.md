# Online Payment

> Auto-generated documentation

## Overview

No description provided.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| payment_id | Data | Payment ID / معرّف الدفع |
| gateway | Select | Gateway / بوابة الدفع |
| status | Select | Status / الحالة |
| payment_for | Select | Payment For / الدفع مقابل |
| reference_doctype | Link | Reference Type |
| reference_name | Dynamic Link | Reference / المرجع |
| member | Link | Member / العضو |
| member_name | Data | Member Name / اسم العضو |
| amount | Currency | Amount / المبلغ |
| currency | Link | Currency / العملة |
| gateway_fee | Currency | Gateway Fee / رسوم البوابة |
| net_received | Currency | Net Received / صافي المستلم |
| exchange_rate | Float | Exchange Rate / سعر الصرف |
| base_amount | Currency | Base Amount / المبلغ الأساسي |
| gateway_reference | Data | Gateway Reference / مرجع البوابة |
| gateway_status | Data | Gateway Status / حالة البوابة |
| gateway_response_json | Code | Gateway Response |
| checkout_url | Data | Checkout URL |
| payment_method_type | Data | Payment Method / طريقة الدفع |
| card_last_four | Data | Card Last 4 / آخر 4 أرقام |
| initiated_at | Datetime | Initiated At / بدأ في |
| completed_at | Datetime | Completed At / اكتمل في |
| expires_at | Datetime | Expires At / ينتهي في |
| cancelled_at | Datetime | Cancelled At / ألغي في |
| sales_invoice | Link | Sales Invoice / فاتورة المبيعات |
| payment_receipt | Link | Payment Receipt / إيصال الدفع |
| payment_entry | Link | Payment Entry / قيد الدفع |
| notes | Small Text | Notes / ملاحظات |
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
*Last updated: 2026-03-21 11:34:36.069732*
