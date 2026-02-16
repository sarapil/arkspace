# Contract Legal Document

> Auto-generated documentation

## Overview

No description provided.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| legal_document | Link | Legal Document / المستند القانوني |
| document_type | Data | Type / النوع |
| document_number | Data | Number / الرقم |
| expiry_date | Date | Expiry / الانتهاء |
| status | Data | Status / الحالة |


## Usage

```python
# Create
doc = frappe.new_doc("Contract Legal Document")
doc.insert()

# Query
records = frappe.get_all("Contract Legal Document")
```

## Related DocTypes

_Add related DocTypes here_

---
*Last updated: 2026-02-15 16:46:39.799654*
