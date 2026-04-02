# Community Event

> Auto-generated documentation

## Overview

No description provided.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| event_name | Data | Event Name / اسم الفعالية |
| event_name_ar | Data | Event Name (Arabic) / الاسم بالعربية |
| event_type | Select | Type / النوع |
| organizer | Link | Organizer / المنظم |
| organizer_name | Data | Organizer Name / اسم المنظم |
| branch | Link | Branch / الفرع |
| space | Link | Space / المساحة |
| start_datetime | Datetime | Start / البداية |
| end_datetime | Datetime | End / النهاية |
| registration_deadline | Datetime | Registration Deadline / آخر موعد للتسجيل |
| description | Text Editor | Description / الوصف |
| image | Attach Image | Image / الصورة |
| max_attendees | Int | Max Attendees / أقصى عدد حضور |
| current_attendees | Int | Registered / المسجلون |
| registration_required | Check | Registration Required / التسجيل مطلوب |
| is_free | Check | Free Event / فعالية مجانية |
| fee | Currency | Fee / الرسوم |
| status | Select | Status / الحالة |
| is_featured | Check | Featured / مميز |


## Usage

```python
# Create
doc = frappe.new_doc("Community Event")
doc.insert()

# Query
records = frappe.get_all("Community Event")
```

## Related DocTypes

_Add related DocTypes here_

---
*Last updated: 2026-03-21 12:53:07.447323*
