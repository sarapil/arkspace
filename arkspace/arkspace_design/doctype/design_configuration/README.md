# Design Configuration

> Auto-generated documentation

## Overview

No description provided.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| primary_color | Color | Primary Color |
| secondary_color | Color | Secondary Color |
| accent_color | Color | Accent Color |
| success_color | Color | Success Color |
| danger_color | Color | Danger Color |
| button_border_radius | Int | Button Border Radius (px) |
| button_font_weight | Select | Button Font Weight |
| link_color | Color | Link Color |
| link_hover_color | Color | Link Hover Color |
| link_underline | Check | Underline Links |
| icon_library | Select | Icon Library |
| default_icon_size | Select | Default Icon Size |
| enable_rtl | Check | Enable RTL |
| arabic_font | Data | Arabic Font |
| english_font | Data | English Font |


## Usage

```python
# Create
doc = frappe.new_doc("Design Configuration")
doc.insert()

# Query
records = frappe.get_all("Design Configuration")
```

## Related DocTypes

_Add related DocTypes here_

---
*Last updated: 2026-02-09 20:26:51.167530*
