# Training Badge

> Auto-generated documentation

## Overview

No description provided.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| badge_name | Data | Badge Name |
| badge_code | Data | Badge Code |
| category | Select | Category |
| level | Select | Level |
| points | Int | Points |
| description | Text Editor | Description |
| criteria | Small Text | Award Criteria |
| icon | Data | Icon Class |
| image | Attach Image | Badge Image |
| total_awarded | Int | Total Awarded |
| is_active | Check | Active |


## Usage

```python
# Create
doc = frappe.new_doc("Training Badge")
doc.insert()

# Query
records = frappe.get_all("Training Badge")
```

## Related DocTypes

_Add related DocTypes here_

---
*Last updated: 2026-02-09 23:14:13.965700*
