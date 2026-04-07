# Member Contract

> Auto-generated documentation

## Overview

No description provided.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| contract_title | Data | Contract Title |
| contract_date | Date | Contract Date |
| contract_template | Link | Contract Template |
| status | Select | Status |
| member | Link | Member |
| member_name | Data | Member Name |
| member_email | Data | Email |
| member_phone | Data | Phone |
| member_address | Small Text | Address |
| space | Link | Space |
| space_type | Data | Space Type |
| branch | Link | Branch |
| floor | Data | Floor |
| unit_details | Small Text | Unit Description |
| membership | Link | Membership |
| membership_plan | Data | Plan |
| billing_cycle | Data | Billing Cycle |
| start_date | Date | Start Date |
| end_date | Date | End Date |
| auto_renew | Check | Auto Renew |
| rate | Currency | Rate |
| currency | Link | Currency |
| discount_percent | Percent | Discount % |
| net_amount | Currency | Net Amount |
| deposit_amount | Currency | Security Deposit |
| legal_documents | Table | Attached Legal Documents |
| contract_terms_ar | Text Editor | Terms (Arabic) |
| contract_terms_en | Text Editor | Terms (English) |
| company_signatory | Data | Company Representative |
| company_signatory_title | Data | Title |
| member_signature | Signature | Member Signature |
| signed_date | Date | Signed Date |
| witness_name | Data | Witness Name |
| witness_id | Data | Witness ID |
| notes | Text Editor | Notes |
| amended_from | Link | Amended From |


## Usage

```python
# Create
doc = frappe.new_doc("Member Contract")
doc.insert()

# Query
records = frappe.get_all("Member Contract")
```

## Related DocTypes

_Add related DocTypes here_

---
*Last updated: 2026-04-07 22:22:34.841259*
