# Contract Legal Document

> Auto-generated documentation

## Overview

No description provided.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| legal_document | Link | Legal Document |
| document_type | Data | Type |
| document_number | Data | Number |
| expiry_date | Date | Expiry |
| status | Data | Status |


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
*Last updated: 2026-04-07 22:22:34.927429*
