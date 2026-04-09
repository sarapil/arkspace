# Contract Template

> Auto-generated documentation

## Overview

No description provided.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| template_name | Data | Template Name |
| language | Select | Language |
| contract_type | Select | Contract Type |
| is_active | Check | Active |
| terms_ar | Text Editor | Terms (Arabic) |
| terms_en | Text Editor | Terms (English) |
| available_placeholders | Small Text | Placeholders |
| amended_from | Link | Amended From |


## Usage

```python
# Create
doc = frappe.new_doc("Contract Template")
doc.insert()

# Query
records = frappe.get_all("Contract Template")
```

## Related DocTypes

_Add related DocTypes here_

---
*Last updated: 2026-04-09 20:07:10.167230*
