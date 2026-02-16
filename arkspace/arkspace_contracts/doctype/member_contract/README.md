# Member Contract

> Auto-generated documentation

## Overview

No description provided.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| contract_title | Data | Contract Title / عنوان العقد |
| contract_date | Date | Contract Date / تاريخ العقد |
| contract_template | Link | Contract Template / نموذج العقد |
| status | Select | Status / الحالة |
| member | Link | Member / العميل |
| member_name | Data | Member Name / اسم العميل |
| member_email | Data | Email / البريد الإلكتروني |
| member_phone | Data | Phone / الهاتف |
| member_address | Small Text | Address / العنوان |
| space | Link | Space / الوحدة |
| space_type | Data | Space Type / نوع الوحدة |
| branch | Link | Branch / الفرع |
| floor | Data | Floor / الطابق |
| unit_details | Small Text | Unit Description / وصف الوحدة |
| membership | Link | Membership / العضوية |
| membership_plan | Data | Plan / الخطة |
| billing_cycle | Data | Billing Cycle / دورة الفوترة |
| start_date | Date | Start Date / تاريخ البداية |
| end_date | Date | End Date / تاريخ النهاية |
| auto_renew | Check | Auto Renew / تجديد تلقائي |
| rate | Currency | Rate / القيمة |
| currency | Link | Currency / العملة |
| discount_percent | Percent | Discount % / نسبة الخصم |
| net_amount | Currency | Net Amount / الصافي |
| deposit_amount | Currency | Security Deposit / التأمين |
| legal_documents | Table | Attached Legal Documents / المستندات المرفقة |
| contract_terms_ar | Text Editor | Terms (Arabic) / الشروط بالعربية |
| contract_terms_en | Text Editor | Terms (English) / الشروط بالإنجليزية |
| company_signatory | Data | Company Representative / ممثل الشركة |
| company_signatory_title | Data | Title / المسمى الوظيفي |
| member_signature | Signature | Member Signature / توقيع العميل |
| signed_date | Date | Signed Date / تاريخ التوقيع |
| witness_name | Data | Witness Name / اسم الشاهد |
| witness_id | Data | Witness ID / رقم هوية الشاهد |
| notes | Text Editor | Notes / ملاحظات |
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
*Last updated: 2026-02-15 16:51:00.038604*
