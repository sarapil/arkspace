# Documentation Entry

> Auto-generated documentation

## Overview

No description provided.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| title | Data | Title / العنوان |
| title_ar | Data | العنوان بالعربية |
| doc_type | Select | Documentation Type |
| module_name | Link | Module |
| related_doctype | Link | Related DocType |
| summary | Small Text | Summary (max 200 chars) |
| summary_ar | Small Text | الملخص بالعربية |
| content | Markdown Editor | Full Documentation |
| content_ar | Markdown Editor | التوثيق بالعربية |
| code_examples | Table | Code Examples |
| related_docs | Table | Related Documents |
| prerequisites | Table | Prerequisites |
| version | Data | Version |
| auto_generated | Check | Auto Generated |
| last_reviewed | Date | Last Reviewed |
| reviewed_by | Link | Reviewed By |


## Usage

```python
# Create
doc = frappe.new_doc("Documentation Entry")
doc.insert()

# Query
records = frappe.get_all("Documentation Entry")
```

## Related DocTypes

_Add related DocTypes here_

---
*Last updated: 2026-02-09 20:26:50.208770*
