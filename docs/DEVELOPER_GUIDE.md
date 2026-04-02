# ARKSpace Developer Guide

> **Version:** 6.0.0 | **Updated:** 2026-03-21  
> Complete guide for developers working on ARKSpace.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Development Environment](#development-environment)
3. [Code Architecture](#code-architecture)
4. [Development Workflow](#development-workflow)
5. [Testing](#testing)
6. [Debugging](#debugging)
7. [Translations](#translations)

---

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 18+
- MariaDB 10.6+
- Redis 6+
- Frappe Bench (v16)
- ERPNext (required dependency)

### Quick Setup

```bash
# Clone and install
cd frappe-bench
bench get-app https://github.com/arkan/arkspace.git
bench --site dev.localhost install-app arkspace
bench --site dev.localhost migrate
bench build --app arkspace
bench start
```

### Development Site Setup

```bash
# Enable developer mode
bench --site dev.localhost set-config developer_mode 1

# Clear cache
bench --site dev.localhost clear-cache

# Watch for JS/CSS changes
bench watch
```

---

## Development Environment

### Recommended VS Code Extensions

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "charliermarsh.ruff",
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "GitHub.copilot"
  ]
}
```

### Linting Configuration

ARKSpace uses **ruff** for Python linting with these rules:

```toml
# pyproject.toml
[tool.ruff]
line-length = 110
target-version = "py312"

[tool.ruff.lint]
select = ["F", "E", "W", "I"]
```

Run lint: `ruff check arkspace/`

---

## Code Architecture

### Directory Structure

```
arkspace/
├── arkspace/
│   ├── __init__.py              # App version (6.0.0)
│   ├── hooks.py                 # Frappe hooks configuration
│   ├── api.py                   # Core API endpoints
│   ├── tasks.py                 # Scheduled tasks
│   ├── permissions.py           # Row-level security
│   ├── install.py               # Post-install hooks
│   ├── setup.py                 # Post-migrate setup
│   ├── setup_wizard.py          # 4-stage setup wizard
│   │
│   ├── arkspace_core/
│   │   ├── doctype/arkspace_settings/    # Single DocType
│   │   └── report/revenue_summary/       # Script report
│   │
│   ├── arkspace_spaces/
│   │   ├── doctype/                      # 5 DocTypes
│   │   ├── api.py                        # Space/Booking APIs
│   │   ├── ark_live.py                   # ARK Live data API
│   │   ├── floor_plan.py                 # Floor Plan data API
│   │   ├── bulk_operations.py            # Bulk check-in/out/cancel
│   │   ├── page/ark_live/                # Interactive map page
│   │   ├── page/floor_plan/              # Floor plan page
│   │   └── report/space_occupancy/       # Script report
│   │
│   ├── arkspace_memberships/
│   │   ├── doctype/                      # 4 DocTypes
│   │   ├── api.py                        # Membership APIs
│   │   └── report/membership_analytics/  # Script report
│   │
│   ├── arkspace_crm/
│   │   └── doctype/                      # 2 DocTypes with methods
│   │
│   ├── arkspace_contracts/
│   │   └── doctype/                      # 5 DocTypes
│   │
│   ├── arkspace_training/
│   │   ├── doctype/                      # 4 DocTypes
│   │   └── api.py                        # Training APIs
│   │
│   ├── arkspace_integrations/
│   │   ├── api.py                        # Integration APIs
│   │   └── billing.py                    # ERPNext billing bridge
│   │
│   ├── arkspace_documentation/
│   │   ├── doctype/                      # 4 DocTypes
│   │   ├── auto_generator.py             # Auto-doc generation
│   │   └── readme_generator.py           # DocType README creation
│   │
│   ├── arkspace_design/
│   │   ├── doctype/design_configuration/ # Single DocType
│   │   ├── icons.py                      # Jinja icon helper
│   │   └── colors.py                     # Jinja color helper
│   │
│   ├── public/
│   │   ├── js/arkspace.js                # Main JS bundle
│   │   ├── js/arkspace_portal.js         # Portal JS
│   │   ├── js/setup_wizard.js            # Setup wizard stages
│   │   ├── css/design-system.css         # CSS variables & themes
│   │   ├── css/arkspace.css              # App styles
│   │   ├── css/arkspace_portal.css       # Portal styles
│   │   └── images/                       # Logo, icons
│   │
│   ├── templates/                        # Email/print templates
│   ├── www/arkspace_portal/              # Member portal pages
│   └── translations/
│       ├── ar.csv                        # Arabic (706 entries)
│       └── en.csv                        # English reference
│
├── docs/                                 # Documentation
├── .github/                              # GitHub templates/CI
├── README.md                             # English README
├── README_AR.md                          # Arabic README
├── CHANGELOG.md                          # Version history
├── CONTRIBUTING.md                       # Contribution guide
├── LICENSE                               # MIT license
└── pyproject.toml                        # Python config
```

### Hooks Reference

Key hooks in `arkspace/hooks.py`:

| Hook | Purpose |
|------|---------|
| `required_apps = ["erpnext"]` | ERPNext dependency |
| `app_include_css` / `app_include_js` | Desk asset loading |
| `web_include_css` / `web_include_js` | Portal asset loading |
| `doc_events` | DocType lifecycle handlers |
| `scheduler_events` | Background task scheduling |
| `has_permission` | Custom permission functions |
| `permission_query_conditions` | Row-level security |
| `fixtures` | Exported roles, workflows, notifications |
| `jinja` | Custom Jinja template methods |
| `setup_wizard_stages` | Setup wizard configuration |
| `after_migrate` | Post-migration setup |

### API Pattern

```python
# arkspace/arkspace_{module}/api.py

import frappe
from frappe import _

@frappe.whitelist()
def my_endpoint(required_param, optional_param=None):
    """
    Brief description of what this endpoint does.

    Args:
        required_param (str): Description
        optional_param (str, optional): Description

    Returns:
        dict: Response with status and data
    """
    # 1. Permission check
    frappe.has_permission("DocType", "read", throw=True)

    # 2. Input validation
    if not required_param:
        frappe.throw(_("Parameter is required"))

    # 3. Business logic
    result = frappe.get_all("DocType",
        filters={"field": required_param},
        fields=["name", "status"]
    )

    # 4. Return response
    return {"status": "success", "data": result}
```

### Frontend Pattern

```javascript
// arkspace/arkspace_{module}/doctype/{doctype}/{doctype}.js

frappe.ui.form.on("{DocType}", {
    refresh(frm) {
        // Add custom buttons
        if (frm.doc.status === "Confirmed") {
            frm.add_custom_button(__("Check In"), () => {
                frappe.call({
                    method: "arkspace.arkspace_spaces.api.check_in",
                    args: { booking_id: frm.doc.name },
                    callback: (r) => {
                        if (!r.exc) frm.reload_doc();
                    }
                });
            }, __("Actions"));
        }
    },

    validate(frm) {
        // Client-side validation
        if (!frm.doc.required_field) {
            frappe.throw(__("Required field is missing"));
        }
    }
});
```

---

## Development Workflow

### Feature Development

```bash
# 1. Create feature branch
git checkout -b feature/my-feature

# 2. Make changes
# ... code ...

# 3. Add translations (if new strings)
# Edit arkspace/translations/ar.csv
# Edit arkspace/translations/en.csv

# 4. Lint check
cd apps/arkspace && ruff check arkspace/ --select F

# 5. Build
bench build --app arkspace

# 6. Test
bench --site dev.localhost run-tests --app arkspace

# 7. Commit
git add -A && git commit -m "feat: add my feature"

# 8. Push
git push origin feature/my-feature
```

### DocType Development

```bash
# Via Frappe UI (recommended in developer mode)
# 1. Go to /desk/doctype/new-doctype-1
# 2. Define fields, permissions, naming
# 3. Save → auto-creates JSON + controller files
# 4. Edit the .py controller for business logic
# 5. Edit the .js for client-side logic
```

### Adding a Scheduled Task

```python
# 1. Add function in arkspace/tasks.py
def my_new_task():
    """Brief description."""
    # Logic here
    frappe.db.commit()

# 2. Register in hooks.py
scheduler_events = {
    "daily": [
        "arkspace.tasks.my_new_task",
    ],
}
```

---

## Testing

### Running Tests

```bash
# All app tests
bench --site dev.localhost run-tests --app arkspace

# Specific module
bench --site dev.localhost run-tests --module arkspace.arkspace_spaces

# Specific DocType
bench --site dev.localhost run-tests --doctype "Space Booking"

# With coverage
bench --site dev.localhost run-tests --app arkspace --coverage
```

### Test Structure

```python
# arkspace/arkspace_spaces/doctype/space_booking/test_space_booking.py

import frappe
import unittest

class TestSpaceBooking(unittest.TestCase):

    def setUp(self):
        frappe.db.rollback()

    def test_booking_creation(self):
        doc = frappe.get_doc({
            "doctype": "Space Booking",
            "space": "test-space",
            "member": "test-customer",
            "booking_type": "Hourly",
            "start_datetime": "2026-01-01 09:00:00",
            "end_datetime": "2026-01-01 10:00:00"
        })
        doc.insert()
        self.assertTrue(doc.name)

    def test_overlap_detection(self):
        # Create first booking, then test overlap
        pass
```

---

## Debugging

### Enable Debug Mode

```python
# site_config.json
{
    "developer_mode": 1,
    "disable_website_cache": 1
}
```

### Debug Logging

```python
# Server-side
frappe.log_error("Debug message", "Debug Title")
frappe.logger("arkspace").info("Info message")
frappe.logger("arkspace").debug("Debug detail")

# Check logs
# tail -f ~/frappe-bench/logs/frappe.log
```

### Database Debugging

```python
# Enable SQL logging
frappe.db.set_debug()

# Print last query
print(frappe.db.last_query)

# Direct SQL
frappe.db.sql("SELECT * FROM `tabSpace Booking` LIMIT 5", as_dict=True)
```

### Frontend Debugging

```javascript
// Console
console.log(cur_frm.doc);           // Current form document
console.log(frappe.boot);            // Boot data
console.log(frappe.session.user);    // Current user

// Debug API calls
frappe.xcall("arkspace.api.test_ping").then(console.log);
```

---

## Translations

### Adding New Strings

1. Use `_("English text")` in Python
2. Use `__("English text")` in JavaScript
3. Add entry to `arkspace/translations/ar.csv`:
   ```csv
   "English text",الترجمة العربية,Context
   ```
4. Add to `arkspace/translations/en.csv`:
   ```csv
   "English text","English text",Context
   ```
5. Rebuild: `bench build --app arkspace`

### Bilingual Select Options (Contracts Module)

The Contracts module uses bilingual select options like `"Active / ساري"`. These are the actual database-stored values and must match exactly in controllers and client scripts. Do **not** attempt to "fix" these — they are by design.

### Verifying Coverage

```bash
# Quick check from app directory
python3 -c "
import csv, re, glob
sources = set()
with open('arkspace/translations/ar.csv', 'r') as f:
    for row in csv.reader(f): sources.add(row[0])
strings = set()
for p in glob.glob('arkspace/**/*.py', recursive=True):
    for m in re.finditer(r'_\([\"\\'](.+?)[\"\\']', open(p).read()):
        strings.add(m.group(1))
missing = strings - sources
print(f'Coverage: {len(strings)-len(missing)}/{len(strings)} ({(1-len(missing)/max(len(strings),1))*100:.0f}%)')
if missing: print('Missing:', missing)
"
```

---

*See also: [API_REFERENCE.md](API_REFERENCE.md) | [ARCHITECTURE.md](ARCHITECTURE.md) | [CONTRIBUTING.md](../CONTRIBUTING.md)*
