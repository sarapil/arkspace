# ARKSpace — Technical Specifications

> **Version:** 6.0.0 | **Updated:** 2026-03-21  
> Detailed technical reference for system requirements, data models, and performance characteristics.

---

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Application Metadata](#application-metadata)
3. [Module Inventory](#module-inventory)
4. [DocType Registry](#doctype-registry)
5. [API Endpoint Catalog](#api-endpoint-catalog)
6. [Scheduled Tasks](#scheduled-tasks)
7. [Fixtures & Configuration](#fixtures--configuration)
8. [Frontend Assets](#frontend-assets)
9. [Database Schema Summary](#database-schema-summary)
10. [Performance Characteristics](#performance-characteristics)

---

## System Requirements

### Minimum

| Component | Requirement |
|-----------|------------|
| Python | 3.12+ |
| Node.js | 18+ |
| MariaDB | 10.6+ |
| Redis | 6.0+ |
| Frappe | v15 or v16 |
| ERPNext | Matching Frappe version |
| Disk | 500 MB (app) + database |
| RAM | 2 GB (shared with Frappe bench) |

### Recommended (Production)

| Component | Recommendation |
|-----------|---------------|
| CPU | 2+ cores |
| RAM | 4 GB+ |
| Disk | SSD, 10 GB+ |
| OS | Ubuntu 22.04 / Debian 12 |
| Reverse Proxy | Nginx with SSL |
| Backup | Daily automated |

---

## Application Metadata

```toml
# pyproject.toml
[project]
name = "arkspace"
version = "6.0.0"
requires-python = ">=3.12"
dependencies = ["frappe", "erpnext"]
authors = [{ name = "ARKSpace Team", email = "dev@arkspace.io" }]
license = { text = "MIT" }
```

```python
# arkspace/__init__.py
__version__ = "6.0.0"
```

```python
# hooks.py
app_name = "arkspace"
app_title = "ARKSpace"
app_publisher = "ARKSpace Team"
app_email = "dev@arkspace.io"
app_license = "mit"
required_apps = ["erpnext"]
```

---

## Module Inventory

| # | Module | DocTypes | APIs | Reports | Pages |
|---|--------|----------|------|---------|-------|
| 1 | arkspace_core | 1 | 2 | 1 | — |
| 2 | arkspace_spaces | 5 | 9 | 1 | 2 |
| 3 | arkspace_memberships | 4 | 5 | 1 | — |
| 4 | arkspace_crm | 2 | 3 | — | — |
| 5 | arkspace_contracts | 5 | 1 | — | — |
| 6 | arkspace_training | 4 | 7 | — | — |
| 7 | arkspace_integrations | — | 3 | — | — |
| 8 | arkspace_documentation | 4 | 2 | — | — |
| 9 | arkspace_design | 1 | — | — | — |
| **Total** | | **26** | **32+** | **3** | **2** |

---

## DocType Registry

### Standalone DocTypes (18)

| DocType | Module | Submittable | Single | Naming |
|---------|--------|-------------|--------|--------|
| ARKSpace Settings | core | No | Yes | — |
| Space Type | spaces | No | No | field:space_type_name |
| Amenity | spaces | No | No | field:amenity_name |
| Co-working Space | spaces | No | No | field:space_name |
| Space Booking | spaces | Yes | No | format: BK-.##### |
| Membership Plan | memberships | No | No | field:plan_name |
| Membership | memberships | Yes | No | format: MEM-.##### |
| Member Credit Wallet | memberships | No | No | field:customer |
| Wallet Transaction | memberships | No | No | autoname |
| Workspace Lead | crm | No | No | format: WL-.##### |
| Workspace Tour | crm | No | No | autoname |
| Contract Template | contracts | No | No | field:template_name |
| Legal Document | contracts | No | No | autoname |
| Member Contract | contracts | Yes | No | autoname |
| Payment Receipt | contracts | Yes | No | autoname |
| Training Module | training | No | No | field:module_name |
| Training Session | training | Yes | No | autoname |
| Training Badge | training | No | No | field:badge_name |
| User Training Progress | training | No | No | autoname |
| Documentation Entry | documentation | No | No | field:title |
| Design Configuration | design | No | Yes | — |

### Child Tables (7)

| Child Table | Parent DocType | Purpose |
|-------------|---------------|---------|
| Space Amenity | Co-working Space | Linked amenities |
| Space Image | Co-working Space | Image gallery |
| Membership Benefit | Membership Plan | Plan benefits |
| Contract Legal Document | Member Contract | Linked documents |
| Documentation Code Example | Documentation Entry | Code samples |
| Documentation Relation | Documentation Entry | Related docs |
| Documentation Prerequisite | Documentation Entry | Prerequisites |

---

## API Endpoint Catalog

### Core (`arkspace.api`)

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `test_ping` | GET | Yes | Health check |
| `get_app_info` | GET | Yes | App version and config |

### Spaces (`arkspace.arkspace_spaces.api`)

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `get_available_spaces` | GET | Yes | Query available spaces |
| `create_booking` | POST | Yes | Create a booking |
| `check_in` | POST | Yes | Check in to booking |
| `check_out` | POST | Yes | Check out from booking |
| `get_space_types` | GET | Yes | List space types |
| `get_amenities` | GET | Yes | List amenities |
| `get_space_status` | GET | Yes | Real-time status |
| `bulk_check_in` | POST | Yes | Bulk check-in |
| `bulk_check_out` | POST | Yes | Bulk check-out |

### Spaces — Pages (`arkspace.arkspace_spaces.floor_plan` / `ark_live`)

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `get_floor_plan_data` | GET | Yes | Floor plan visualization |
| `get_ark_live_data` | GET | Yes | Live occupancy data |

### Memberships (`arkspace.arkspace_memberships.api`)

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `get_membership_plans` | GET | Yes | Available plans |
| `create_membership` | POST | Yes | Create membership |
| `get_active_memberships` | GET | Yes | Active memberships |
| `get_wallet_balance` | GET | Yes | Credit wallet balance |
| `get_member_dashboard` | GET | Yes | Unified member view |

### CRM (Workspace Lead / Tour whitelisted methods)

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `convert_to_customer` | POST | Yes | Lead → Customer |
| `schedule_tour` | POST | Yes | Create tour from lead |
| `complete_tour` | POST | Yes | Mark tour complete |

### Contracts (`arkspace.arkspace_contracts`)

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `render_contract_terms` | POST | Yes | Render Jinja template |

### Training (`arkspace.arkspace_training.api`)

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `get_training_catalog` | GET | Yes | Published modules |
| `get_upcoming_sessions` | GET | Yes | Scheduled sessions |
| `get_available_badges` | GET | Yes | Active badges |
| `get_user_badges` | GET | Yes | User's earned badges |
| `enroll_user` | POST | Yes | Enroll in module |
| `update_progress` | POST | Yes | Update + award badges |
| `get_user_progress` | GET | Yes | User progress records |

### Integrations (`arkspace.arkspace_integrations.api`)

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `get_integration_status` | GET | Yes | Installed apps check |
| `get_unpaid_invoices` | GET | Yes | Outstanding invoices |
| `sync_employee_customer` | POST | Yes | Link employee ↔ customer |

### Documentation (`arkspace.arkspace_documentation`)

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `generate_documentation` | POST | Yes | Trigger auto-generation |
| `generate_readme` | POST | Yes | Generate DocType README |

---

## Scheduled Tasks

```python
# hooks.py → scheduler_events
scheduler_events = {
    "daily": [
        "arkspace.tasks.check_membership_expiry",
        "arkspace.tasks.auto_renew_memberships",
        "arkspace.tasks.send_membership_expiry_reminders",
        "arkspace.tasks.cleanup_expired_wallet_credits",
    ],
    "hourly": [
        "arkspace.tasks.mark_no_show_bookings",
        "arkspace.tasks.auto_checkout_expired_bookings",
    ],
    "cron": {
        "0 2 * * *": [
            "arkspace.arkspace_documentation.auto_generator.generate_all_documentation"
        ]
    },
}
```

| Task | Frequency | Purpose |
|------|-----------|---------|
| `check_membership_expiry` | Daily | Marks expired memberships |
| `auto_renew_memberships` | Daily | Auto-renews eligible memberships |
| `send_membership_expiry_reminders` | Daily | Sends 7-day and 1-day reminders |
| `cleanup_expired_wallet_credits` | Daily | Marks expired credit transactions |
| `mark_no_show_bookings` | Hourly | Marks no-show after 2-hour grace |
| `auto_checkout_expired_bookings` | Hourly | Auto-checkouts overdue bookings |
| `generate_all_documentation` | 02:00 daily | Regenerates documentation entries |

---

## Fixtures & Configuration

```python
# hooks.py → fixtures
fixtures = [
    {"dt": "Role", "filters": [["name", "like", "ARKSpace%"]]},
    {"dt": "Workflow", "filters": [["name", "like", "ARKSpace%"]]},
    {"dt": "Workflow State", "filters": [["name", "like", "ARKSpace%"]]},
    {"dt": "Workflow Action Master", "filters": [["name", "like", "ARKSpace%"]]},
    {"dt": "Notification", "filters": [["name", "like", "ARKSpace%"]]},
    {"dt": "Print Format", "filters": [["name", "like", "ARKSpace%"]]},
]
```

### Exported Fixtures

| Type | Count | Items |
|------|-------|-------|
| Roles | 7 | Admin, Manager, Sales, Operations, Front Desk, Member, Viewer |
| Workflows | 3 | Booking Approval, Membership Lifecycle, Lead Pipeline |
| Notifications | 4 | Booking confirmation, check-in, membership expiry, renewal |
| Print Formats | 3 | Booking Confirmation, Membership Card, Membership Receipt |

---

## Frontend Assets

### Desk (Back-office)

```python
# hooks.py
app_include_css = "/assets/arkspace/css/arkspace.css"
app_include_js = "/assets/arkspace/js/arkspace.js"
```

| Asset | Path | Size (approx) |
|-------|------|------|
| Main CSS | `public/css/arkspace.css` | ~15 KB |
| Design System | `public/css/design-system.css` | ~8 KB |
| Main JS | `public/js/arkspace.js` | ~20 KB |
| Setup Wizard | `public/js/setup_wizard.js` | ~5 KB |

### Portal (Member-facing)

```python
web_include_css = "/assets/arkspace/css/arkspace_portal.css"
web_include_js = "/assets/arkspace/js/arkspace_portal.js"
```

| Asset | Path | Size (approx) |
|-------|------|------|
| Portal CSS | `public/css/arkspace_portal.css` | ~10 KB |
| Portal JS | `public/js/arkspace_portal.js` | ~8 KB |

### Images

| Asset | Path |
|-------|------|
| App Logo | `public/images/arkspace-logo.png` |
| App Icon | `public/images/arkspace-icon.svg` |

---

## Database Schema Summary

### Table Count

- 25 tables (18 standalone + 7 child)
- Estimated rows for medium deployment: ~50K records
- All tables use Frappe's standard columns: `name`, `owner`, `creation`, `modified`, `modified_by`, `docstatus`

### Key Indexes

Standard Frappe indexes on:
- `name` (primary key, VARCHAR 140)
- `modified` (for sync and queries)
- `parent` + `parentfield` + `parenttype` (child tables)
- Custom: `customer`, `status`, `booking_date`, `membership_plan`

### Estimated Storage

| Component | Size Estimate |
|-----------|--------------|
| App code (installed) | ~50 MB |
| Database (100 seats, 1 year) | ~200 MB |
| File attachments (legal docs) | Variable |
| Translations | ~100 KB |
| **Total (typical)** | **~300 MB** |

---

## Performance Characteristics

### API Response Times (Typical)

| Endpoint Category | Expected | Notes |
|-------------------|----------|-------|
| Simple reads | < 100ms | Cached queries |
| List queries | < 200ms | With permission filters |
| Create/update | < 300ms | With validations |
| Bulk operations | < 1s per 50 items | Batched commits |
| Report generation | < 2s | With date filters |
| Floor plan data | < 500ms | Aggregated query |

### Scalability Notes

- Row-level security adds ~10-20% overhead to list queries
- Credit wallet transactions are append-only, minimal lock contention
- Scheduled tasks designed for short execution (< 60s each)
- Real-time events use Frappe's socketio, scales with Redis pub/sub

---

*For detailed implementation: [TECHNICAL_IMPLEMENTATION.md](TECHNICAL_IMPLEMENTATION.md) | [ARCHITECTURE.md](ARCHITECTURE.md)*
