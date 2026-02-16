# Membership

> Auto-generated documentation

## Overview

No description provided.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| member | Link | Member |
| member_name | Data | Member Name |
| member_email | Data | Member Email |
| membership_plan | Link | Membership Plan |
| plan_type | Data | Plan Type |
| billing_cycle | Select | Billing Cycle |
| start_date | Date | Start Date |
| end_date | Date | End Date |
| auto_renew | Check | Auto Renew |
| status | Select | Status |
| rate | Currency | Rate |
| discount_percent | Percent | Discount % |
| net_amount | Currency | Net Amount |
| currency | Link | Currency |
| setup_fee_charged | Check | Setup Fee Charged |
| assigned_space | Link | Assigned Space |
| branch | Link | Branch |
| initial_credits | Int | Initial Credits |
| credit_wallet | Link | Credit Wallet |
| notes | Text Editor | Notes |
| amended_from | Link | Amended From |


## Usage

```python
# Create
doc = frappe.new_doc("Membership")
doc.insert()

# Query
records = frappe.get_all("Membership")
```

## Related DocTypes

_Add related DocTypes here_

---
*Last updated: 2026-02-15 16:25:10.074338*
