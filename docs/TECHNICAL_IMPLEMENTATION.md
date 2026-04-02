# ARKSpace Technical Implementation

> **Version:** 6.0.0 | **Updated:** 2026-03-21  
> Deep-dive into architecture, patterns, and implementation details.

## Table of Contents

- [System Architecture](#system-architecture)
- [Data Flow](#data-flow)
- [Module Architecture](#module-architecture)
- [Controller Patterns](#controller-patterns)
- [Permission System](#permission-system)
- [Scheduled Tasks](#scheduled-tasks)
- [Frontend Architecture](#frontend-architecture)
- [Integration Architecture](#integration-architecture)
- [Database Schema](#database-schema)
- [Hooks Configuration](#hooks-configuration)
- [Setup & Installation](#setup--installation)
- [Testing Strategy](#testing-strategy)

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Browser                               │
│  ┌──────────┐  ┌──────────────┐  ┌─────────────────────┐   │
│  │ Desk SPA │  │ Member Portal│  │ Socket.IO Client    │   │
│  │ (v16)    │  │ (www/)       │  │ (realtime events)   │   │
│  └────┬─────┘  └──────┬───────┘  └──────────┬──────────┘   │
└───────┼────────────────┼────────────────────┼───────────────┘
        │                │                    │
        ▼                ▼                    ▼
┌───────────────────────────────────────────────────────┐
│              Frappe Web Server :8000                    │
│  ┌──────────────────────────────────────────────┐     │
│  │              ARKSpace App Layer               │     │
│  │  ┌─────────┐ ┌──────────┐ ┌───────────────┐ │     │
│  │  │ Spaces  │ │ Members  │ │ CRM           │ │     │
│  │  │ Module  │ │ Module   │ │ Module        │ │     │
│  │  └────┬────┘ └────┬─────┘ └───────┬───────┘ │     │
│  │  ┌────┴────┐ ┌────┴─────┐ ┌───────┴───────┐ │     │
│  │  │Contract │ │ Training │ │ Integrations  │ │     │
│  │  │ Module  │ │ Module   │ │ Module        │ │     │
│  │  └─────────┘ └──────────┘ └───────┬───────┘ │     │
│  └───────────────────────────────────┼──────────┘     │
│                                      │                 │
│              ┌───────────────────────┘                 │
│              ▼                                         │
│  ┌──────────────────┐                                  │
│  │  ERPNext Bridge   │──→ Sales Invoice, Customer,     │
│  │  (billing.py)     │    Employee linking              │
│  └──────────────────┘                                  │
└───────────────────────────────────────────────────────┘
        │                           │
        ▼                           ▼
┌──────────────┐           ┌──────────────────┐
│ MariaDB 10.6 │           │ Redis 7          │
│  (Database)  │           │ (Cache + Queue)  │
└──────────────┘           └──────────────────┘
```

## Data Flow

### Booking Flow

```
1. Member selects space → get_available_spaces() queries DB
2. create_booking() → validates dates, pricing, overlaps
3. on_submit → status = "Confirmed", publishes realtime event
4. check_in() → status = "Checked In", space = "Occupied"
   └── publishes "space_status_changed" via Socket.IO
5. check_out() → status = "Checked Out", space = "Available"
   └── billing.on_booking_submit() → creates Sales Invoice
6. Hourly cron: mark_no_show_bookings(), auto_checkout_expired_bookings()
```

### Membership Flow

```
1. create_membership() → validates plan, calculates end_date
2. on_submit → status = "Active", creates/updates Credit Wallet
   └── billing.on_membership_submit() → creates Sales Invoice
3. Daily cron: check_membership_expiry() → status = "Expired"
4. Daily cron: auto_renew_memberships() → creates new period
   └── publishes "membership_renewed" via Socket.IO
5. Daily cron: send_membership_expiry_reminders() → emails at 7d and 1d
```

### Lead → Customer Flow

```
1. Workspace Lead created (New status)
2. Contact → status = "Contacted"
3. schedule_tour() → creates Workspace Tour, status = "Tour Scheduled"
4. complete_tour() → records outcome, rating
5. convert_to_customer() → creates Customer, status = "Converted"
   └── Optionally creates Membership
```

---

## Module Architecture

### Directory Structure

```
arkspace/
├── hooks.py              # Central configuration
├── install.py            # after_install: creates roles, space types, sample data
├── setup.py              # after_migrate: sets up workflows, notifications, charts
├── tasks.py              # 7 scheduled tasks
├── permissions.py        # Row-level security
├── api.py                # Top-level API hub (re-exports + health + dashboard)
│
├── arkspace_core/
│   ├── doctype/arkspace_settings/    # Single DocType
│   ├── utils.py                       # Shared utilities
│   ├── report/                        # Revenue, Occupancy, Analytics
│   └── workspace/                     # Navigation workspace
│
├── arkspace_spaces/
│   ├── api.py                         # get_available_spaces, create_booking, check_in/out
│   ├── ark_live.py                    # Live dashboard logic
│   ├── bulk_operations.py             # Mass check-in/out/cancel
│   ├── floor_plan.py                  # Floor plan page logic
│   ├── doctype/                       # Space Type, Amenity, Co-working Space, Booking
│   ├── page/                          # Floor Plan page
│   ├── report/                        # Space reports
│   ├── notification/                  # Booking notifications
│   ├── number_card/                   # Dashboard cards
│   └── print_format/                  # Booking Confirmation
│
├── arkspace_memberships/
│   ├── api.py                         # Plans, memberships, wallet, dashboard
│   ├── doctype/                       # Plan, Membership, Wallet, Transaction
│   ├── notification/                  # Membership notifications
│   ├── number_card/                   # Membership cards
│   ├── report/                        # Membership reports
│   └── print_format/                  # Membership Card, Receipt
│
├── arkspace_crm/
│   └── doctype/                       # Workspace Lead, Tour
│
├── arkspace_contracts/
│   ├── doctype/                       # Template, Legal Doc, Contract, Receipt
│   └── print_format/                  # Contract formats
│
├── arkspace_training/
│   ├── api.py                         # Catalog, sessions, badges, enrollment
│   └── doctype/                       # Module, Session, Badge, Progress
│
├── arkspace_integrations/
│   ├── api.py                         # Status, unpaid invoices
│   └── billing.py                     # ERPNext billing bridge
│
├── arkspace_documentation/
│   ├── auto_generator.py              # Nightly documentation regeneration
│   ├── readme_generator.py            # DocType README auto-creation
│   └── doctype/                       # Documentation Entry + child tables
│
├── arkspace_design/
│   ├── colors.py                      # Jinja helper: get_color()
│   ├── icons.py                       # Jinja helper: get_icon()
│   └── doctype/                       # Design Configuration
│
├── translations/
│   ├── ar.csv                         # 272 Arabic translations
│   └── en.csv                         # English reference
│
├── public/
│   ├── js/arkspace.js                 # Main JS bundle
│   ├── js/arkspace_portal.js          # Portal JS
│   ├── css/design-system.css          # CSS design system
│   ├── css/arkspace.css               # Main CSS
│   └── css/arkspace_portal.css        # Portal CSS
│
├── templates/                         # Jinja templates
├── www/                               # Portal pages
├── tests/                             # Test suite
│   └── compat.py                      # v15/v16 test case adapter
└── utils/
    └── compat.py                      # v15/v16 compatibility utils
```

---

## Controller Patterns

### Standard Lifecycle

```python
class SpaceBooking(Document):
    def validate(self):
        """Pre-save validations — called on save and submit."""
        self.validate_dates()           # end > start
        self.validate_pricing()         # rate exists for booking type
        self.validate_overlap()         # no double-booking
        self.calculate_totals()         # amount calculations

    def on_submit(self):
        """Post-submit actions."""
        self.db_set("status", "Confirmed")
        # Billing integration
        from arkspace.arkspace_integrations.billing import on_booking_submit
        on_booking_submit(self, "on_submit")

    def on_cancel(self):
        """Cancellation rollback."""
        self.db_set("status", "Cancelled")
        # Free the space
        frappe.db.set_value("Co-working Space", self.space, "status", "Available")
```

### Whitelisted Methods

```python
@frappe.whitelist()
def check_in(booking):
    """Check in to a confirmed booking."""
    doc = frappe.get_doc("Space Booking", booking)
    if doc.docstatus != 1:
        frappe.throw(_("Booking must be submitted before check-in"))
    if doc.status != "Confirmed":
        frappe.throw(_("Only Confirmed bookings can be checked in. Current status: {0}").format(doc.status))

    doc.db_set("status", "Checked In")
    doc.db_set("checked_in_at", frappe.utils.now())
    frappe.db.set_value("Co-working Space", doc.space, "status", "Occupied")

    frappe.publish_realtime("space_status_changed", {
        "space": doc.space,
        "status": "Occupied",
        "booking": booking
    }, user=frappe.session.user)

    return doc
```

---

## Permission System

### Role Hierarchy

```
ARKSpace Admin         → System Manager equivalent for ARKSpace
  └── ARKSpace Manager → Branch-level management
       ├── ARKSpace Sales      → CRM + Memberships
       ├── ARKSpace Operations → Spaces + Bookings
       └── ARKSpace Front Desk → Check-in/out + Basic bookings
            └── ARKSpace Member → Self-service only
                 └── ARKSpace Viewer → Read-only
```

### Row-Level Security (permissions.py)

```python
def has_booking_permission(doc, user, permission_type):
    """Members can only see their own bookings."""
    roles = frappe.get_roles(user)
    if any(r in roles for r in ["ARKSpace Admin", "ARKSpace Manager",
                                  "ARKSpace Operations", "ARKSpace Front Desk"]):
        return True

    if "ARKSpace Member" in roles:
        customer = get_customer_for_user(user)
        return doc.member == customer

    return False

def get_booking_conditions(user):
    """SQL condition for list views."""
    roles = frappe.get_roles(user)
    if any(r in roles for r in ["ARKSpace Admin", "ARKSpace Manager"]):
        return ""  # No restriction
    customer = get_customer_for_user(user)
    return f"`tabSpace Booking`.member = '{customer}'"
```

---

## Scheduled Tasks

| Task | Schedule | Description | Module |
|------|----------|-------------|--------|
| `check_membership_expiry` | Daily | Marks expired memberships | tasks.py |
| `auto_renew_memberships` | Daily | Renews eligible auto-renew memberships | tasks.py |
| `send_membership_expiry_reminders` | Daily | Email 7d + 1d reminders | tasks.py |
| `generate_daily_occupancy_snapshot` | Daily | Records daily occupancy stats | tasks.py |
| `mark_no_show_bookings` | Hourly | No-show after 2-hour grace | tasks.py |
| `auto_checkout_expired_bookings` | Hourly | Auto-checkout past end time | tasks.py |
| `regenerate_documentation` | Cron 0 2 * * * | Nightly doc regeneration | auto_generator.py |

---

## Frontend Architecture

### JavaScript Bundles

| File | Hook | Purpose |
|------|------|---------|
| `arkspace.js` | `app_include_js` | Main desk JS — form scripts, list customizations |
| `arkspace_portal.js` | `web_include_js` | Portal JS — booking, dashboard, member self-service |

### CSS Bundles

| File | Hook | Purpose |
|------|------|---------|
| `design-system.css` | `app_include_css` | CSS custom properties, variables |
| `arkspace.css` | `app_include_css` | Component styles, RTL overrides |
| `arkspace_portal.css` | `web_include_css` | Portal-specific styles |

### Pages

| Page | Module | Purpose |
|------|--------|---------|
| Floor Plan | Spaces | Interactive space status visualization |
| Member Portal | www/ | Self-service member dashboard |

---

## Integration Architecture

### ERPNext Billing Bridge

```
arkspace_integrations/billing.py
├── on_booking_submit()    → Creates Sales Invoice from booking
├── on_booking_cancel()    → Cancels related Sales Invoice
├── on_membership_submit() → Creates Sales Invoice from membership
├── on_membership_cancel() → Cancels related Sales Invoice
└── link_employee_to_customer() → Links Employee to Customer record
```

### Doc Events (hooks.py)

```python
doc_events = {
    "Space Booking": {
        "on_submit": "arkspace.arkspace_integrations.billing.on_booking_submit",
        "on_cancel": "arkspace.arkspace_integrations.billing.on_booking_cancel",
    },
    "Membership": {
        "on_submit": "arkspace.arkspace_integrations.billing.on_membership_submit",
        "on_cancel": "arkspace.arkspace_integrations.billing.on_membership_cancel",
    },
    "Employee": {
        "after_insert": "arkspace.arkspace_integrations.billing.link_employee_to_customer",
        "on_update": "arkspace.arkspace_integrations.billing.link_employee_to_customer",
    },
}
```

---

## Database Schema

### Core Tables

```sql
-- Key tables (all prefixed with `tab`)
tabARKSpace Settings        -- Single: 1 row
tabSpace Type               -- ~6 rows (space categories)
tabAmenity                  -- ~10 rows (amenity catalog)
tabCo-working Space         -- Space inventory
tabSpace Booking            -- Reservations (high volume)
tabMembership Plan          -- ~6 rows (plan catalog)
tabMembership               -- Active subscriptions
tabMember Credit Wallet     -- 1 per customer
tabWorkspace Lead           -- Sales pipeline
tabWorkspace Tour           -- Tour records
tabContract Template        -- ~5 rows (template catalog)
tabLegal Document           -- Member legal documents
tabMember Contract          -- Signed contracts
tabPayment Receipt          -- Payment records
tabTraining Module          -- Training catalog
tabTraining Session         -- Training events
tabTraining Badge           -- Badge catalog
tabUser Training Progress   -- Per-user per-module
tabDesign Configuration     -- Single: 1 row
tabDocumentation Entry      -- Auto-generated docs
```

### Key Indexes

- `tabSpace Booking`: (`space`, `start_datetime`, `end_datetime`) for overlap queries
- `tabMembership`: (`member`, `status`) for active membership lookups
- `tabWorkspace Lead`: (`status`) for pipeline views

---

## Hooks Configuration

### Fixtures

```python
fixtures = [
    {"dt": "Role", "filters": [["role_name", "like", "ARKSpace%"]]},
    {"dt": "Workflow", "filters": [["name", "in", [
        "Space Booking Approval",
        "Membership Lifecycle",
        "Lead Pipeline"
    ]]]},
    {"dt": "Notification", "filters": [["name", "like", "ARKSpace%"]]},
    {"dt": "Number Card", "filters": [["name", "in", [
        "Available Spaces", "Occupied Spaces",
        "Active Memberships", "Checked In Now"
    ]]]},
    {"dt": "Dashboard Chart", "filters": [["name", "like", "ARKSpace%"]]},
    {"dt": "Print Format", "filters": [["name", "in", [
        "Booking Confirmation", "Membership Card", "Membership Receipt"
    ]]]},
]
```

### Jinja Helpers

```python
jinja = {
    "methods": [
        "arkspace.arkspace_design.icons.get_icon",
        "arkspace.arkspace_design.colors.get_color",
    ],
}
```

---

## Setup & Installation

### Install Flow

```
1. bench get-app arkspace
2. bench --site {site} install-app arkspace
   └── triggers after_install (install.py):
       ├── Create 7 custom roles
       ├── Create default space types (6)
       ├── Create ARKSpace Settings
       └── Seed sample data (optional)
3. bench --site {site} migrate
   └── triggers after_migrate (setup.py):
       ├── Create/update workflows (3)
       ├── Create/update notifications (4)
       ├── Create/update number cards (4)
       └── Create/update dashboard charts (5)
4. bench build --app arkspace
```

### Setup Wizard

```python
# 4 stages:
# 1. Welcome + basic config (name, currency, timezone)
# 2. Branches (up to 3 locations)
# 3. Space Types (checkboxes for 6 types)
# 4. First Membership Plan (name, type, price)
```

---

## Testing Strategy

### Test Runner

```bash
# All tests
cd frappe-bench/sites && ../env/bin/python -m pytest ../apps/arkspace/ -x -v

# Specific module
cd frappe-bench/sites && ../env/bin/python -m pytest ../apps/arkspace/arkspace/arkspace_spaces/ -x -v

# Specific test file
cd frappe-bench/sites && ../env/bin/python -m pytest ../apps/arkspace/arkspace/arkspace_contracts/doctype/member_contract/test_member_contract.py -x -v
```

### Test Patterns

```python
from arkspace.tests.compat import ARKSpaceTestCase

class TestSpaceBooking(ARKSpaceTestCase):
    def setUp(self):
        # Create test fixtures
        self.space = make_test_space()
        self.customer = make_test_customer()

    def test_booking_lifecycle(self):
        booking = create_booking(self.space.name, self.customer.name, ...)
        self.assertEqual(booking.status, "Confirmed")
        check_in(booking.name)
        booking.reload()
        self.assertEqual(booking.status, "Checked In")
```

---

*See also: [DOCTYPES_REFERENCE.md](DOCTYPES_REFERENCE.md) | [API_REFERENCE.md](API_REFERENCE.md) | [AI_CONTEXT.md](AI_CONTEXT.md)*
