# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

"""
مولد التوثيق التلقائي — Auto Documentation Generator
Generates documentation entries from code structure.
"""

import ast
import os
from typing import Optional

import frappe
from frappe import _


class DocumentationGenerator:
    """
    مولد التوثيق التلقائي
    Auto-generates documentation from code structure.
    """

    def generate_all(self):
        """Generate documentation for entire app."""
        self.generate_doctype_docs()
        self.generate_api_docs()
        self.generate_ai_context()

    def generate_doctype_docs(self):
        """
        توثيق جميع الـ DocTypes تلقائياً
        Auto-document all DocTypes in ARKSpace modules.
        """
        doctypes = frappe.get_all(
            "DocType",
            filters={"module": ["like", "ARKSpace%"]},
            fields=["name", "module"],
        )

        for dt in doctypes:
            doc = frappe.get_doc("DocType", dt.name)

            # Skip if doc entry already exists and is not auto-generated
            existing = frappe.db.exists(
                "Documentation Entry",
                {"related_doctype": dt.name, "auto_generated": 0},
            )
            if existing:
                continue

            # Create or update documentation entry
            entry_name = frappe.db.exists(
                "Documentation Entry",
                {"related_doctype": dt.name, "auto_generated": 1},
            )
            if entry_name:
                doc_entry = frappe.get_doc("Documentation Entry", entry_name)
            else:
                doc_entry = frappe.new_doc("Documentation Entry")

            doc_entry.title = dt.name
            doc_entry.title_ar = self._translate_title(dt.name)
            doc_entry.doc_type = "DocType"
            doc_entry.module_name = dt.module
            doc_entry.related_doctype = dt.name
            doc_entry.auto_generated = 1

            # Generate content
            doc_entry.summary = self._generate_doctype_summary(doc)
            doc_entry.content = self._generate_doctype_content(doc)

            # Add field documentation
            fields_md = self._document_fields(doc.fields)
            doc_entry.content += f"\n\n## Fields\n\n{fields_md}"

            # Clear and add code examples
            doc_entry.code_examples = []
            doc_entry.append(
                "code_examples",
                {
                    "language": "python",
                    "title": "Create new record",
                    "code": self._generate_create_example(doc),
                },
            )
            doc_entry.append(
                "code_examples",
                {
                    "language": "python",
                    "title": "Query records",
                    "code": self._generate_query_example(doc),
                },
            )

            doc_entry.save(ignore_permissions=True)

    def generate_api_docs(self):
        """
        توثيق جميع الـ APIs من الكود
        Document all whitelisted functions.
        """
        try:
            import arkspace as arkspace_module

            app_path = os.path.dirname(arkspace_module.__file__)
        except ImportError:
            app_path = frappe.get_app_path("arkspace")

        for root, _dirs, files in os.walk(app_path):
            for file in files:
                if file.endswith(".py"):
                    filepath = os.path.join(root, file)
                    try:
                        self._extract_api_docs(filepath)
                    except Exception:
                        pass  # Skip files that can't be parsed

    def _extract_api_docs(self, filepath: str):
        """Extract documentation from Python file."""
        with open(filepath) as f:
            source = f.read()

        tree = ast.parse(source)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for decorator in node.decorator_list:
                    if self._is_whitelist_decorator(decorator):
                        self._create_api_doc(node, filepath)

    def _is_whitelist_decorator(self, decorator) -> bool:
        """Check if decorator is @frappe.whitelist()"""
        if isinstance(decorator, ast.Call):
            func = decorator.func
            if isinstance(func, ast.Attribute):
                return func.attr == "whitelist"
        elif isinstance(decorator, ast.Attribute):
            return decorator.attr == "whitelist"
        return False

    def _create_api_doc(self, func_node: ast.FunctionDef, filepath: str):
        """Create API documentation entry."""
        frappe.only_for(["System Manager", "ARK Admin", "ARK User"])
        # Skip if already documented manually
        existing = frappe.db.exists(
            "Documentation Entry",
            {"title": func_node.name, "doc_type": "API", "auto_generated": 0},
        )
        if existing:
            return

        entry_name = frappe.db.exists(
            "Documentation Entry",
            {"title": func_node.name, "doc_type": "API", "auto_generated": 1},
        )
        if entry_name:
            doc_entry = frappe.get_doc("Documentation Entry", entry_name)
        else:
            doc_entry = frappe.new_doc("Documentation Entry")

        doc_entry.title = func_node.name
        doc_entry.doc_type = "API"
        doc_entry.auto_generated = 1

        # Extract docstring
        docstring = ast.get_docstring(func_node) or ""
        doc_entry.summary = (
            docstring.split("\n")[0][:200] if docstring else f"API: {func_node.name}"
        )

        # Build relative path
        rel_path = filepath
        try:
            app_path = frappe.get_app_path("arkspace")
            if filepath.startswith(app_path):
                rel_path = filepath[len(app_path) + 1 :]
        except Exception:
            pass

        # Extract parameters
        params = self._extract_parameters(func_node)

        doc_entry.content = f"""## Endpoint

`POST /api/method/arkspace.{func_node.name}`

## Description

{docstring}

## Parameters

{params}

## Source File

`{rel_path}`
"""
        doc_entry.save(ignore_permissions=True)

    def _extract_parameters(self, func_node: ast.FunctionDef) -> str:
        """Extract function parameters as markdown table."""
        params = []
        for arg in func_node.args.args:
            if arg.arg != "self":
                annotation = ""
                if arg.annotation:
                    try:
                        annotation = ast.unparse(arg.annotation)
                    except Exception:
                        annotation = "Any"
                params.append(f"| `{arg.arg}` | {annotation} | - |")

        if params:
            return (
                "| Parameter | Type | Description |\n|---|---|---|\n" + "\n".join(params)
            )
        return "No parameters"

    def generate_ai_context(self):
        """
        توليد ملف AI-CONTEXT.md المحدث
        Generate updated AI context file.
        """
        context = []
        context.append("# 🤖 AI Context — ARKSpace v5.0")
        context.append(f"\n> Auto-generated: {frappe.utils.now()}\n")

        # Stats
        doctype_count = frappe.db.count(
            "DocType", {"module": ["like", "ARKSpace%"]}
        )
        api_count = frappe.db.count(
            "Documentation Entry", {"doc_type": "API"}
        )

        context.append(
            f"## Quick Stats\n- DocTypes: {doctype_count}\n- APIs: {api_count}\n"
        )

        # DocType summary
        context.append("\n## DocTypes Overview\n")
        doctypes = frappe.get_all(
            "DocType",
            filters={"module": ["like", "ARKSpace%"]},
            fields=["name", "module"],
            order_by="module",
        )

        current_module = ""
        for dt in doctypes:
            if dt.module != current_module:
                current_module = dt.module
                context.append(f"\n### {current_module}\n")
            context.append(f"- `{dt.name}`")

        # Write file
        try:
            ai_context_path = os.path.join(
                frappe.get_app_path("arkspace"), "..", "AI-CONTEXT.md"
            )
            with open(ai_context_path, "w") as f:
                f.write("\n".join(context))
        except Exception:
            pass

    # --- Helper methods ---

    def _generate_doctype_summary(self, doc) -> str:
        field_count = len([f for f in doc.fields if f.fieldtype not in ("Section Break", "Column Break", "Tab Break")])
        return f"{doc.name} — {field_count} fields, Module: {doc.module}"

    def _generate_doctype_content(self, doc) -> str:
        is_sub = "Yes" if doc.is_submittable else "No"
        track = "Yes" if doc.track_changes else "No"
        return f"""# {doc.name}

**Module:** {doc.module}
**Is Submittable:** {is_sub}
**Track Changes:** {track}

## Description

{doc.description or "No description provided."}
"""

    def _document_fields(self, fields: list) -> str:
        rows = ["| Field | Type | Required | Options |", "|---|---|---|---|"]
        for field in fields:
            if field.fieldtype not in ("Section Break", "Column Break", "Tab Break"):
                reqd = "✅" if field.reqd else ""
                options = field.options or ""
                rows.append(
                    f"| `{field.fieldname}` | {field.fieldtype} | {reqd} | {options} |"
                )
        return "\n".join(rows)

    def _generate_create_example(self, doc) -> str:
        return f'doc = frappe.new_doc("{doc.name}")\n# Set required fields...\ndoc.insert()'

    def _generate_query_example(self, doc) -> str:
        return f'records = frappe.get_all(\n    "{doc.name}",\n    filters={{}},\n    fields=["name", "creation"]\n)'

    def _translate_title(self, title: str) -> str:
        translations = {
            "Co-working Space": "مساحة العمل المشترك",
            "Space Type": "نوع المساحة",
            "Membership Plan": "خطة العضوية",
            "Membership": "العضوية",
            "Space Booking": "حجز المساحة",
            "Workspace Lead": "عميل محتمل",
            "Workspace Tour": "جولة تعريفية",
            "Amenity": "مرفق",
            "ARKSpace Settings": "إعدادات أرك سبيس",
            "Member Credit Wallet": "محفظة العميل",
            "Documentation Entry": "مدخل التوثيق",
            "Design Configuration": "إعدادات التصميم",
            "Training Module": "وحدة تدريب",
            "Training Badge": "شارة إنجاز",
            "ARKAMOR Device": "جهاز أركمور",
        }
        return translations.get(title, title)


# --- Whitelisted methods for hooks / scheduled tasks ---


@frappe.whitelist()
def regenerate_documentation():
    """
    مهمة مجدولة لتحديث التوثيق
    Scheduled task to regenerate documentation.
    """
    frappe.only_for(["ARKSpace Manager", "System Manager"])

    generator = DocumentationGenerator()
    generator.generate_all()
    frappe.db.commit()


@frappe.whitelist()
def regenerate_single(doc_name: Optional[str] = None):
    """Regenerate a single documentation entry."""
    frappe.only_for(["ARKSpace Manager", "System Manager"])

    if doc_name:
        doc = frappe.get_doc("Documentation Entry", doc_name)
        if doc.related_doctype and doc.auto_generated:
            generator = DocumentationGenerator()
            dt_doc = frappe.get_doc("DocType", doc.related_doctype)
            doc.summary = generator._generate_doctype_summary(dt_doc)
            doc.content = generator._generate_doctype_content(dt_doc)
            doc.content += f"\n\n## Fields\n\n{generator._document_fields(dt_doc.fields)}"
            doc.save(ignore_permissions=True)
            frappe.db.commit()
    return {"success": True}
