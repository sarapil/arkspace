# Legal Document

> Auto-generated documentation

## Overview

No description provided.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| member | Link | Member |
| member_name | Data | Member Name |
| document_type | Select | Document Type |
| document_number | Data | Document Number |
| issue_date | Date | Issue Date |
| expiry_date | Date | Expiry Date |
| issuing_authority | Data | Issuing Authority |
| status | Select | Status |
| document_file | Attach Image | Document (Front) |
| document_file_back | Attach Image | Document (Back) |
| notes | Small Text | Notes |


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
*Last updated: 2026-04-07 22:22:34.692136*
