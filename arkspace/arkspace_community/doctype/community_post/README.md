# Community Post

> Auto-generated documentation

## Overview

No description provided.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| title | Data | Title |
| post_type | Select | Type |
| author | Link | Author |
| author_name | Data | Author Name |
| branch | Link | Branch |
| content | Text Editor | Content |
| tags | Small Text | Tags |
| likes_count | Int | Likes |
| comments_count | Int | Comments |
| views_count | Int | Views |
| is_pinned | Check | Pinned |
| is_anonymous | Check | Anonymous |
| status | Select | Status |


## Usage

```python
# Create
doc = frappe.new_doc("Community Post")
doc.insert()

# Query
records = frappe.get_all("Community Post")
```

## Related DocTypes

_Add related DocTypes here_

---
*Last updated: 2026-04-07 22:22:35.208865*
