# Contributing to ARKSpace — المساهمة في أرك سبيس

> Thank you for your interest in contributing to ARKSpace!  
> شكراً لاهتمامك بالمساهمة في أرك سبيس!

## Table of Contents / جدول المحتويات

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Coding Standards](#coding-standards)
- [Bilingual Requirements](#bilingual-requirements)
- [Pull Request Process](#pull-request-process)
- [Reporting Bugs](#reporting-bugs)

---

## Code of Conduct

Be respectful, inclusive, and constructive. We welcome contributions from everyone regardless of experience level, gender, identity, orientation, disability, ethnicity, or religion.

---

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 20+
- MariaDB 10.6+
- Redis 7+
- Frappe v16 bench environment
- ERPNext v16

### Development Setup

```bash
# 1. Clone and set up bench
bench init --frappe-branch version-16 frappe-bench
cd frappe-bench

# 2. Install ERPNext
bench get-app --branch version-16 erpnext

# 3. Clone ARKSpace
bench get-app arkspace <your-fork-url>

# 4. Create a development site
bench new-site dev.local --admin-password admin
bench --site dev.local install-app erpnext
bench --site dev.local install-app arkspace

# 5. Enable developer mode
bench --site dev.local set-config developer_mode 1

# 6. Build and start
bench build --app arkspace
bench start
```

---

## Making Changes

### Branch Naming

```
feature/short-description
fix/issue-number-description
docs/what-was-updated
i18n/language-updates
```

### Workflow

1. Fork the repository
2. Create a feature branch from `main`
3. Make your changes
4. Write/update tests
5. Update documentation
6. Submit a pull request

---

## Coding Standards

### Python

- Follow [PEP 8](https://peps.python.org/pep-0008/) conventions
- Use `ruff` for linting (configured in `pyproject.toml`)
- Maximum line length: 110 characters
- Add docstrings to all public functions
- Use type hints where practical

```bash
# Lint check
ruff check arkspace/

# Format check
ruff format --check arkspace/
```

### JavaScript

- Use Frappe's JS conventions
- Prefer `const`/`let` over `var`
- Use arrow functions where appropriate
- Add JSDoc comments for complex functions

### DocType Naming

- **DocType name**: Title Case with spaces (e.g., `Space Booking`)
- **Field names**: snake_case (e.g., `booking_type`)
- **Module names**: `arkspace_` prefix (e.g., `arkspace_spaces`)

### API Conventions

```python
@frappe.whitelist()
def my_function(required_param, optional_param=None):
    """Brief description of what this does.

    Args:
        required_param (str): Description
        optional_param (str, optional): Description

    Returns:
        dict: Description of return value
    """
    frappe.has_permission("DocType", "read", throw=True)
    # Implementation
    return {"status": "success"}
```

---

## Bilingual Requirements

### All UI Strings Must Be Translatable

```python
# ✅ Correct
frappe.throw(_("Space {0} is already booked").format(space_name))

# ❌ Wrong
frappe.throw(f"Space {space_name} is already booked")
```

### Arabic Translation Process

1. Add English string in code wrapped with `_()`
2. Add translation to `arkspace/translations/ar.csv`:
   ```csv
   source_text,translated_text,context
   "Space {0} is already booked","المساحة {0} محجوزة بالفعل","Validation"
   ```
3. Preserve `{0}`, `{1}` placeholders
4. Keep HTML tags intact
5. No trailing spaces
6. UTF-8 encoding

### Arabic Translation Glossary

| English | Arabic | Notes |
|---------|--------|-------|
| Lead | عميل محتمل | NOT رصيد |
| Customer | عميل | |
| Contact | جهة اتصال | |
| Booking | حجز | |
| Membership | عضوية | |
| Space | مساحة | |
| Amenity | مرفق | |
| Submit | اعتماد | For submittable docs |
| Save | حفظ | |
| Cancel | إلغاء | |
| Status | الحالة | |
| Enabled | مفعّل | |
| Template | قالب | |
| Schedule | جدولة | |
| Badge | شارة | |

### DocType Bilingual Fields

For fields visible to users, add an `_ar` suffix field:

```json
{
    "fieldname": "space_name",
    "fieldtype": "Data",
    "label": "Space Name",
    "reqd": 1
},
{
    "fieldname": "space_name_ar",
    "fieldtype": "Data",
    "label": "Space Name (Arabic)"
}
```

### Bilingual Select Options

Use the format `"English / العربي"`:

```json
{
    "fieldname": "document_type",
    "fieldtype": "Select",
    "options": "National ID / البطاقة الشخصية\nPassport / جواز السفر\nCommercial Register / السجل التجاري"
}
```

---

## Pull Request Process

### Before Submitting

- [ ] All new strings are translatable (`_()` or `__()`)
- [ ] Arabic translations added for new strings
- [ ] Tests written and passing
- [ ] Documentation updated
- [ ] `CHANGELOG.md` updated
- [ ] `ruff check` passes
- [ ] Works in both LTR and RTL
- [ ] No console errors

### PR Template

Use the [Pull Request Template](/.github/PULL_REQUEST_TEMPLATE.md) provided.

### Review Process

1. Automated CI runs (lint, test, translation check)
2. Code review by maintainer
3. Testing on development site
4. Merge to `main`

---

## Reporting Bugs

Use the [Bug Report Template](/.github/ISSUE_TEMPLATE/bug_report.md) and include:

1. Steps to reproduce
2. Expected vs actual behavior
3. Browser console errors
4. Server logs (if applicable)
5. Environment details (Frappe/ERPNext/ARKSpace versions)

---

## Documentation Updates

When making changes, update the relevant files:

| Changed | Update |
|---------|--------|
| New feature | `docs/FEATURES_EN.md`, `docs/FEATURES_AR.md` |
| New/changed API | `docs/API_REFERENCE.md` |
| New/changed DocType | `docs/DOCTYPES_REFERENCE.md` |
| Architecture change | `docs/TECHNICAL_IMPLEMENTATION.md` |
| New strings | `arkspace/translations/ar.csv` |
| Any change | `CHANGELOG.md` |

---

## Getting Help

- Open an issue with the **question** label
- Check [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for common issues
- Review existing documentation in the `docs/` directory

---

*Thank you for contributing to ARKSpace! — !شكراً لمساهمتكم في أرك سبيس*
