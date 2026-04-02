# ARKSpace — AI Assistant Instructions

> Use this document when working with AI assistants on this codebase.  
> For token-efficient context, see [AI_CONTEXT.md](AI_CONTEXT.md).

---

## Application Identity

| Property | Value |
|----------|-------|
| **Name** | ARKSpace |
| **Type** | Frappe v16 Application (v15 compatible) |
| **Domain** | Enterprise Co-Working Space Management |
| **Version** | 6.0.0 |
| **Language** | Python / JavaScript |
| **Required** | ERPNext |
| **Publisher** | ARKSpace Team |
| **License** | MIT |

---

## Quick Context

ARKSpace is a bilingual (Arabic/English) co-working space management platform built on Frappe Framework + ERPNext. It provides:

- **Space Management** — Define spaces, amenities, interactive floor plans, real-time occupancy tracking
- **Booking System** — Full lifecycle: Reserve → Confirm → Check-In → Check-Out, bulk operations
- **Membership Engine** — Plans, billing cycles, credit wallets, auto-renewal
- **CRM Pipeline** — Lead capture → Tour scheduling → Conversion to Customer/Membership
- **Contract Management** — Bilingual templates with Jinja rendering, legal document tracking, payment receipts
- **Training Platform** — Modules, sessions, badges, progress tracking
- **ERPNext Integration** — Auto-creates Sales Invoices from bookings/memberships
- **Member Portal** — Self-service portal for booking, profile management

---

## Code Conventions

### Python
- Use `@frappe.whitelist()` for API endpoints
- Use `_("text")` for all translatable strings
- Follow PEP 8 (enforced via ruff: F, E, W, I rules)
- Tabs for indentation (project standard)
- Type hints encouraged but not required
- All DocType controllers inherit from `Document`

### JavaScript
- Use `frappe.call()` for backend calls
- Use `__("text")` for translatable strings
- ES6+ syntax preferred
- Frontend namespace: `arkspace.*` (e.g., `arkspace.floor_plan`)
- Real-time updates via `frappe.realtime.on()`

### DocTypes
- Naming: `snake_case` for field names
- Bilingual fields use `_ar` suffix (e.g., `plan_name_ar`)
- Contract module uses bilingual Select options: `"English / العربية"`
- Always add `description` for complex fields
- Child tables use parent prefix (e.g., `Space Amenity` for `Co-working Space`)

### Translations
- All user-facing strings MUST use `_()` (Python) or `__()` (JS)
- Translation files: `arkspace/translations/{ar,en}.csv`
- Format: `source_text,translated_text,context`
- Contract Select options are intentionally bilingual — do NOT "fix" them

---

## Key Files

| Purpose | Location |
|---------|----------|
| Hooks & config | `arkspace/hooks.py` |
| Version | `arkspace/__init__.py` |
| Core APIs | `arkspace/api.py` |
| Space APIs | `arkspace/arkspace_spaces/api.py` |
| Membership APIs | `arkspace/arkspace_memberships/api.py` |
| Training APIs | `arkspace/arkspace_training/api.py` |
| Integration APIs | `arkspace/arkspace_integrations/api.py` |
| Billing bridge | `arkspace/arkspace_integrations/billing.py` |
| Scheduled tasks | `arkspace/tasks.py` |
| Permissions | `arkspace/permissions.py` |
| Setup wizard | `arkspace/setup_wizard.py` |
| Post-install | `arkspace/install.py` / `arkspace/setup.py` |
| Floor Plan JS | `arkspace/arkspace_spaces/page/floor_plan/` |
| ARK Live JS | `arkspace/arkspace_spaces/page/ark_live/` |
| Main JS bundle | `arkspace/public/js/arkspace.js` |
| Portal CSS | `arkspace/public/css/arkspace_portal.css` |
| Design system CSS | `arkspace/public/css/design-system.css` |
| Translations (AR) | `arkspace/translations/ar.csv` |
| Translations (EN) | `arkspace/translations/en.csv` |
| DocTypes | `arkspace/arkspace_*/doctype/*/` |
| Portal pages | `arkspace/www/arkspace_portal/` |

---

## Module Architecture

```
arkspace/
├── arkspace_core/          # Settings, revenue report
├── arkspace_spaces/        # Spaces, bookings, floor plans, bulk ops
├── arkspace_memberships/   # Plans, memberships, credit wallets
├── arkspace_crm/           # Leads, tours, conversion pipeline
├── arkspace_contracts/     # Templates, legal docs, contracts, receipts
├── arkspace_training/      # Modules, sessions, badges, progress
├── arkspace_integrations/  # ERPNext billing bridge
├── arkspace_documentation/ # Auto-generated DocType docs
└── arkspace_design/        # Colors, icons, RTL theming
```

---

## Common Tasks

### Add New DocType

1. Create DocType via Frappe UI or `bench new-doctype`
2. Define fields in the JSON file
3. Add controller logic in `{doctype}.py`
4. Add client script in `{doctype}.js`
5. Register events in `hooks.py` if needed
6. Add translation strings to `ar.csv` and `en.csv`
7. Add help documentation to `arkspace/help/`

### Add Translation

1. Add to `ar.csv`: `"English Source","الترجمة العربية","Context"`
2. Add to `en.csv`: `"English Source","English Source","Context"`
3. Use `_("English Source")` in Python
4. Use `__("English Source")` in JavaScript
5. Rebuild: `bench build --app arkspace`

### Add API Endpoint

```python
import frappe
from frappe import _

@frappe.whitelist()
def my_function(param):
    """Docstring with purpose."""
    frappe.has_permission("DocType", "read", throw=True)
    # Business logic
    return {"status": "success", "data": result}
```

### Add Scheduled Task

```python
# In arkspace/tasks.py
def my_daily_task():
    """Brief description."""
    # Logic here
    frappe.db.commit()
```

```python
# In hooks.py
scheduler_events = {
    "daily": ["arkspace.tasks.my_daily_task"],
}
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Client Layer                          │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐             │
│  │ Desk UI  │  │ Portal   │  │ REST API  │             │
│  └────┬─────┘  └────┬─────┘  └─────┬─────┘             │
└───────┼──────────────┼──────────────┼───────────────────┘
        │              │              │
┌───────┴──────────────┴──────────────┴───────────────────┐
│               Frappe Framework v16                       │
│  ┌────────────────────────────────────────────────────┐ │
│  │              ARKSpace v6.0.0                        │ │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────────┐  │ │
│  │  │ Spaces │ │Members │ │  CRM   │ │ Contracts  │  │ │
│  │  └────────┘ └────────┘ └────────┘ └────────────┘  │ │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────────┐  │ │
│  │  │Training│ │Integr. │ │ Design │ │Documentation│  │ │
│  │  └────────┘ └────────┘ └────────┘ └────────────┘  │ │
│  └────────────────────────────────────────────────────┘ │
└──────────────────────────┬──────────────────────────────┘
                           │
┌──────────────────────────┴──────────────────────────────┐
│                    Data Layer                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │ MariaDB  │  │  Redis   │  │ ERPNext  │              │
│  └──────────┘  └──────────┘  └──────────┘              │
└─────────────────────────────────────────────────────────┘
```

---

## Roles & Permissions

| Role | Scope |
|------|-------|
| ARKSpace Admin | Full access to all modules |
| ARKSpace Manager | Manage spaces, memberships, reports |
| ARKSpace Sales | CRM, leads, tours, conversions |
| ARKSpace Operations | Bookings, check-in/out, bulk operations |
| ARKSpace Front Desk | Day-to-day booking management |
| ARKSpace Member | Self-service portal access |
| ARKSpace Viewer | Read-only access |

---

## Testing

```bash
bench --site dev.localhost run-tests --app arkspace
bench --site dev.localhost run-tests --app arkspace --module arkspace.arkspace_spaces
```

## Deployment

```bash
bench get-app arkspace
bench --site {site} install-app arkspace
bench --site {site} migrate
bench build --app arkspace
bench restart
```

---

_For full context, see [CONTEXT.md](CONTEXT.md)_  
_For API details, see [API_REFERENCE.md](API_REFERENCE.md)_  
_For DocType schemas, see [DOCTYPES_REFERENCE.md](DOCTYPES_REFERENCE.md)_
