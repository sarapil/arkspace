# ARKSpace — Copilot Instructions

> These instructions help GitHub Copilot and other AI coding assistants understand the ARKSpace application.
> Last updated: 2026-03-21 | Version: 6.0.0

## What is ARKSpace?

ARKSpace is a **Frappe v16** application for enterprise co-working space management. It depends on **ERPNext** and provides: space management, bookings, memberships, CRM, contracts, training, billing integration, and member portals. It is **bilingual** (Arabic + English) with full RTL support.

## Version Compatibility

- **v6.0.0** targets Frappe v16 / ERPNext v16
- Uses `arkspace.tests.compat.ARKSpaceTestCase` for tests (auto-selects v15/v16 base class)
- Uses `arkspace.utils.compat.desk_route()` for `/app/` vs `/desk/` URL generation
- Always return `True`/`False` explicitly from `has_permission` hooks (v16 requirement)

## Quick Reference Files

| File | Purpose |
|------|---------|
| `docs/AI_CONTEXT.md` | Token-efficient LLM-optimized context |
| `docs/FEATURES_EN.md` | Complete features in English |
| `docs/FEATURES_AR.md` | مميزات التطبيق بالعربية |
| `docs/API_REFERENCE.md` | All API endpoints with signatures |
| `docs/DOCTYPES_REFERENCE.md` | DocType schemas & relationships |
| `docs/TECHNICAL_IMPLEMENTATION.md` | Architecture deep-dive |
| `docs/ROADMAP.md` | Product roadmap & version history |
| `docs/ADMIN_GUIDE.md` | Installation & admin documentation |
| `docs/USER_GUIDE.md` | End-user guide |
| `docs/INTEGRATIONS.md` | External system integrations |
| `docs/TROUBLESHOOTING.md` | Common issues & solutions |
| `CHANGELOG.md` | Version-by-version changes |

**Read `docs/AI_CONTEXT.md` first for quick understanding. Read `docs/TECHNICAL_IMPLEMENTATION.md` for full details.**

---

## App Structure

```
apps/arkspace/arkspace/
├── hooks.py              # Central configuration
├── install.py            # after_install: roles, types, setup, seed
├── setup.py              # after_migrate: workflows, notifications, charts
├── tasks.py              # 7 scheduled tasks
├── permissions.py        # Row-level security
├── api.py                # Top-level API (health, dashboard)
├── arkspace_core/        # Settings, utils
├── arkspace_spaces/      # Spaces, bookings, amenities, floor plan
├── arkspace_memberships/ # Plans, memberships, credit wallets
├── arkspace_crm/         # Leads, tours
├── arkspace_contracts/   # Templates, legal docs, contracts, receipts
├── arkspace_training/    # Modules, sessions, badges, progress
├── arkspace_integrations/# ERPNext billing bridge
├── arkspace_documentation/# Auto-doc generator
├── arkspace_design/      # Colors, icons, design config
└── public/               # JS (3 files) + CSS (3 files)
```

## Key Conventions

### Naming
- **DocType autoname patterns:**
  - Simple DocTypes: `field:name_field` (e.g., `field:plan_name`)
  - Transactional DocTypes: `naming_series:PREFIX-.YYYY.-.#####`
  - Prefixes: BK (Booking), MEM (Membership), WL (Lead), WT (Tour), MC (Contract), PR (Receipt), TS (Session), UTP (Progress)
- **Module naming:** `arkspace_` prefix (e.g., `arkspace_spaces`)

### Bilingual Support
- Most DocTypes have `_ar` suffix fields for Arabic (e.g., `space_name` + `space_name_ar`)
- Select fields have bilingual options: `"English / العربي"`
- Contract terms have both `contract_terms_ar` and `contract_terms_en`

### Select Field Values
- **CRITICAL:** Select field options are bilingual strings like `"National ID / البطاقة الشخصية"` — always match the exact string from the DocType JSON, including the Arabic part
- Status fields follow: Draft, Active, Expired, Cancelled, Suspended patterns

### Controllers
```python
class MyDocType(Document):
    def validate(self):
        # Pre-save: calculations, validations
        self.calculate_totals()
        self.validate_dates()
    
    def on_submit(self):
        # Post-submit: status change, integrations
        self.db_set("status", "Active")
    
    def on_cancel(self):
        # Rollback: free resources, cancel invoices
        self.db_set("status", "Cancelled")
```

### APIs
```python
@frappe.whitelist()
def my_endpoint(required_param, optional_param=None):
    """Docstring explaining what it does."""
    frappe.has_permission("DocType", "read", throw=True)
    # Implementation
    return {"status": "success", "data": result}

@frappe.whitelist(allow_guest=True)
def public_endpoint():
    """No auth required."""
    pass
```

### Realtime Events
```python
frappe.publish_realtime("space_status_changed", {
    "space": space_name,
    "status": "Occupied",
    "booking": booking_name
}, user=frappe.session.user)
```

### Form Scripts
```javascript
frappe.ui.form.on("Space Booking", {
    refresh(frm) {
        // Status indicator colors
        frm.set_indicator_formatter("status", (doc) => { ... });
        // Action buttons based on status
        if (frm.doc.status === "Confirmed") {
            frm.add_custom_button(__("Check In"), () => { ... });
        }
    }
});
```

---

## Roles (7 Custom)

| Role | Key Access |
|------|-----------|
| ARKSpace Admin | Everything (CRUD + Submit) |
| ARKSpace Manager | Branch management, reports |
| ARKSpace Sales | CRM, memberships |
| ARKSpace Operations | Spaces, bookings (some read-only) |
| ARKSpace Front Desk | Check-in/out, basic bookings |
| ARKSpace Member | Self-service, training |
| ARKSpace Viewer | Read-only (defined but not yet used) |

---

## DocType Quick Reference (25 Total)

### Standalone (18)
| DocType | Module | Submittable | Key Fields |
|---------|--------|-------------|------------|
| ARKSpace Settings | Core | ❌ (Single) | company, currency, prefixes, toggles |
| Space Type | Spaces | ❌ | type_name, icon, color, booking toggles |
| Amenity | Spaces | ❌ | amenity_name, prices, is_complimentary |
| Co-working Space | Spaces | ❌ | space_name, type, branch, capacity, rates, status |
| Space Booking | Spaces | ✅ | space, member, type, dates, rate, status |
| Membership Plan | Memberships | ❌ | plan_name, type, prices, benefits |
| Membership | Memberships | ✅ | member, plan, cycle, dates, rate, status |
| Member Credit Wallet | Memberships | ❌ | member (unique), credits, transactions[] |
| Workspace Lead | CRM | ❌ | name, contact, source, status, pipeline |
| Workspace Tour | CRM | ❌ | lead, date/time, status, outcome |
| Contract Template | Contracts | ❌ | name, language, type, Jinja terms |
| Legal Document | Contracts | ❌ | member, type, number, dates, status, files |
| Member Contract | Contracts | ✅ | member, template, space, terms, signature |
| Payment Receipt | Contracts | ✅ | member, type, amount, method, period |
| Training Module | Training | ❌ | name, category, level, stats |
| Training Session | Training | ✅ | module, date, times, venue, fee |
| Training Badge | Training | ❌ | name, category, level, points |
| User Training Progress | Training | ❌ | user, module, session, status, progress |
| Design Configuration | Design | ❌ (Single) | colors, fonts, RTL |
| Documentation Entry | Documentation | ❌ | title, type, content, code examples |

### Child Tables (7)
Space Amenity, Space Image, Credit Transaction, Contract Legal Document, Documentation Code Example, Documentation Relation, Documentation Prerequisite

---

## Testing

```bash
# Run all ARKSpace tests
cd frappe-bench/sites && ../env/bin/python -m pytest ../apps/arkspace/ -x -v

# Run specific module tests
cd frappe-bench/sites && ../env/bin/python -m pytest ../apps/arkspace/arkspace/arkspace_spaces/ -x -v

# Run specific test file
cd frappe-bench/sites && ../env/bin/python -m pytest ../apps/arkspace/arkspace/arkspace_contracts/doctype/member_contract/test_member_contract.py -x -v
```

---

## Common Tasks

### Adding a new DocType
1. Create JSON + Python controller in the module's `doctype/` folder
2. Add test file with `TestClassName(FrappeTestCase)`
3. Update `setup.py` if it needs workflow/notification/chart
4. Update workspace JSON if it should appear in navigation
5. Update `docs/FEATURES_EN.md`, `docs/FEATURES_AR.md`, `docs/AI_CONTEXT.md`

### Adding a new API
1. Add function with `@frappe.whitelist()` in the module's `api.py`
2. Add test in `tests/test_api.py`
3. Update `docs/AI_CONTEXT.md` and `docs/API_REFERENCE.md`

### Modifying hooks
1. Edit `arkspace/hooks.py`
2. Run `bench --site dev.localhost migrate`
3. Clear cache: `bench --site dev.localhost clear-cache`

---

## Environment

| Key | Value |
|-----|-------|
| Bench dir | `/workspace/development/frappe-bench/` |
| App dir | `apps/arkspace/` |
| Python venv | `env/bin/python` |
| Site | `dev.localhost` |
| Web port | 8000 |
| Socket.IO port | 9000 |
| Database | MariaDB (host: `mariadb`) |
| Cache | Redis (hosts: `redis-cache`, `redis-queue`) |

---

## Documentation Update Policy

When making changes to ARKSpace, **always update these files:**
- `docs/FEATURES_AR.md` and `docs/FEATURES_EN.md` — if new features added
- `docs/AI_CONTEXT.md` — if new DocTypes, APIs, roles, or patterns added
- `docs/DOCTYPES_REFERENCE.md` — if DocType schemas change
- `docs/API_REFERENCE.md` — if API endpoints added/changed
- `docs/TECHNICAL_IMPLEMENTATION.md` — if relationships or architecture change
- `docs/ROADMAP.md` — add to Suggestions Log with date and description
- `CHANGELOG.md` — add entry for the change
- This file (`copilot-instructions.md`) — if conventions or structure change
