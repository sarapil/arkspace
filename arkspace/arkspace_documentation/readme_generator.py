"""
مولد README التلقائي — Auto README Generator
Generates README.md files for DocType directories.
"""

import os

import frappe


def create_doctype_readme(doc, method):
    """
    إنشاء README.md لـ DocType جديد
    Create README.md for new DocType.
    Called via doc_events hook on DocType after_insert.
    """
    if not doc.module or not doc.module.startswith("ARKSpace"):
        return

    _write_readme(doc)


def update_doctype_readme(doc, method):
    """
    تحديث README.md عند تعديل DocType
    Update README.md when DocType changes.
    Called via doc_events hook on DocType on_update.
    """
    if not doc.module or not doc.module.startswith("ARKSpace"):
        return

    _write_readme(doc)


def _write_readme(doc):
    """Write or overwrite README for a DocType directory."""
    readme_content = f"""# {doc.name}

> Auto-generated documentation

## Overview

{doc.description or "No description provided."}

## Fields

| Field | Type | Description |
|-------|------|-------------|
"""

    for field in doc.fields:
        if field.fieldtype not in ("Section Break", "Column Break", "Tab Break"):
            readme_content += f"| {field.fieldname} | {field.fieldtype} | {field.label or ''} |\n"

    readme_content += f"""

## Usage

```python
# Create
doc = frappe.new_doc("{doc.name}")
doc.insert()

# Query
records = frappe.get_all("{doc.name}")
```

## Related DocTypes

_Add related DocTypes here_

---
*Last updated: {frappe.utils.now()}*
"""

    try:
        doctype_path = frappe.get_module_path(
            doc.module, "doctype", frappe.scrub(doc.name)
        )
        if os.path.exists(doctype_path):
            readme_path = os.path.join(doctype_path, "README.md")
            with open(readme_path, "w") as f:
                f.write(readme_content)
    except Exception:
        pass  # Non-critical — skip silently
