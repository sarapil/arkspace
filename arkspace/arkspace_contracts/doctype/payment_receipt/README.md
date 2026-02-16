# Payment Receipt

> Auto-generated documentation

## Overview

No description provided.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| receipt_type | Select | Receipt Type / نوع الإيصال |
| receipt_date | Date | Receipt Date / تاريخ الإيصال |
| member | Link | Member / العميل |
| member_name | Data | Member Name / اسم العميل |
| member_contract | Link | Contract / العقد |
| membership | Link | Membership / العضوية |
| space_booking | Link | Booking / الحجز |
| period_from | Date | From / من |
| period_to | Date | To / إلى |
| billing_cycle | Select | Billing Cycle / دورة الفوترة |
| amount | Currency | Amount / المبلغ |
| currency | Link | Currency / العملة |
| payment_method | Select | Payment Method / طريقة الدفع |
| reference_number | Data | Reference Number / رقم المرجع |
| payment_date | Date | Payment Date / تاريخ الدفع |
| notes | Small Text | Notes / ملاحظات |
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
*Last updated: 2026-02-15 16:51:00.893512*
