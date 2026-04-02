# Community Post

> Auto-generated documentation

## Overview

No description provided.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| title | Data | Title / العنوان |
| post_type | Select | Type / النوع |
| author | Link | Author / الكاتب |
| author_name | Data | Author Name / اسم الكاتب |
| branch | Link | Branch / الفرع |
| content | Text Editor | Content / المحتوى |
| tags | Small Text | Tags / الوسوم |
| likes_count | Int | Likes / إعجابات |
| comments_count | Int | Comments / تعليقات |
| views_count | Int | Views / مشاهدات |
| is_pinned | Check | Pinned / مثبت |
| is_anonymous | Check | Anonymous / مجهول |
| status | Select | Status / الحالة |


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
*Last updated: 2026-03-21 12:53:07.651562*
