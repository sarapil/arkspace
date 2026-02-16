# Legal Document

> Auto-generated documentation

## Overview

No description provided.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| member | Link | Member / العميل |
| member_name | Data | Member Name / اسم العميل |
| document_type | Select | Document Type / نوع المستند |
| document_number | Data | Document Number / رقم المستند |
| issue_date | Date | Issue Date / تاريخ الإصدار |
| expiry_date | Date | Expiry Date / تاريخ الانتهاء |
| issuing_authority | Data | Issuing Authority / جهة الإصدار |
| status | Select | Status / الحالة |
| document_file | Attach Image | Document (Front) / المستند (وجه أمامي) |
| document_file_back | Attach Image | Document (Back) / المستند (وجه خلفي) |
| notes | Small Text | Notes / ملاحظات |


## Usage

```python
# Create
doc = frappe.new_doc("Legal Document")
doc.insert()

# Query
records = frappe.get_all("Legal Document")
```

## Related DocTypes

_Add related DocTypes here_

---
*Last updated: 2026-02-15 16:48:51.309413*
