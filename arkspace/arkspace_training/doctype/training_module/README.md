# Training Module

> Auto-generated documentation

## Overview

No description provided.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| module_name | Data | Module Name |
| category | Select | Category |
| level | Select | Level |
| status | Select | Status |
| duration_hours | Float | Duration (Hours) |
| instructor | Data | Default Instructor |
| description | Text Editor | Description |
| prerequisites | Small Text | Prerequisites |
| syllabus | Text Editor | Syllabus / Content Outline |
| image | Attach Image | Cover Image |
| total_sessions | Int | Total Sessions |
| total_enrollments | Int | Total Enrollments |
| amended_from | Link | Amended From |


## Usage

```python
# Create
doc = frappe.new_doc("Training Module")
doc.insert()

# Query
records = frappe.get_all("Training Module")
```

## Related DocTypes

_Add related DocTypes here_

---
*Last updated: 2026-02-09 23:14:13.647862*
