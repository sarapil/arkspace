# ARKSpace — AI Context (LLM-Optimized)

> Token-efficient reference for AI assistants. Version 6.0.0 | 2026-03-21

## Identity

```
APP: arkspace | TITLE: ARKSpace | VERSION: 6.0.0
FRAMEWORK: Frappe v16 | DEPENDS: erpnext
BILINGUAL: Arabic (primary) + English | RTL: Yes
LICENSE: MIT | PUBLISHER: ARKSpace Team
BRAND: Navy #1B365D / Gold #C4A962
```

## Stats

```
MODULES: 9 | DOCTYPES: 25 (18 standalone + 7 child)
SUBMITTABLE: 5 | SINGLE: 2 | APIS: ~30
ROLES: 7 | WORKFLOWS: 3 | TASKS: 7
PRINT_FORMATS: 7 | NOTIFICATIONS: 4 | REPORTS: 3
```

## Module → DocType Map

```
CORE:       ARKSpace Settings (Single)
SPACES:     Space Type, Amenity, Co-working Space, Space Booking (Submit),
            Space Amenity (Child), Space Image (Child)
MEMBERS:    Membership Plan, Membership (Submit), Member Credit Wallet,
            Credit Transaction (Child)
CRM:        Workspace Lead, Workspace Tour
CONTRACTS:  Contract Template, Legal Document, Member Contract (Submit),
            Payment Receipt (Submit), Contract Legal Document (Child)
TRAINING:   Training Module, Training Session (Submit), Training Badge,
            User Training Progress
DESIGN:     Design Configuration (Single)
DOCS:       Documentation Entry, Documentation Code Example (Child),
            Documentation Relation (Child), Documentation Prerequisite (Child)
INTEGRATIONS: (no doctypes — billing.py, api.py only)
```

## Key Relationships

```
Customer → Membership → Membership Plan
Customer → Space Booking → Co-working Space → Space Type
Customer → Member Contract → Contract Template
Customer → Member Credit Wallet → Credit Transaction[]
Customer → Legal Document[]
Workspace Lead → Workspace Tour → (converts to) Customer
Training Module → Training Session
Training Module → User Training Progress → Training Badge
Co-working Space → Space Amenity[] → Amenity
Co-working Space → Space Image[]
```

## DocType Quick Ref

```
DOCTYPE: ARKSpace Settings | MODULE: Core | SINGLE: Yes
PURPOSE: App-wide config — company, currency, prefixes, feature toggles, API keys

DOCTYPE: Space Type | MODULE: Spaces | AUTONAME: field:type_name
PURPOSE: Categories of spaces (Hot Desk, Private Office, etc.)
KEY_FIELDS: type_name (Data) [REQ], type_name_ar, icon, color, capacity, booking toggles

DOCTYPE: Co-working Space | MODULE: Spaces | AUTONAME: field:space_name
PURPOSE: Individual bookable space units
KEY_FIELDS: space_name [REQ], space_type (Link→Space Type) [REQ], branch [REQ], capacity [REQ], rates, status (Available/Occupied/Maintenance/Reserved)
WORKFLOWS: status managed via booking check-in/out

DOCTYPE: Space Booking | MODULE: Spaces | SUBMIT: Yes | AUTONAME: naming_series:BK-.YYYY.-.#####
PURPOSE: Space reservations with full lifecycle
KEY_FIELDS: space [REQ], member (Link→Customer) [REQ], booking_type [REQ], start/end [REQ], rate [REQ], status
WORKFLOWS: Pending → Confirmed → Checked In → Checked Out | Cancelled | No Show
ACTIONS: check_in, check_out, cancel

DOCTYPE: Membership Plan | MODULE: Memberships | AUTONAME: field:plan_name
PURPOSE: Subscription plan definitions
KEY_FIELDS: plan_name [REQ], plan_type [REQ] (6 types), price [REQ], benefits (hours/credits/guests)

DOCTYPE: Membership | MODULE: Memberships | SUBMIT: Yes | AUTONAME: naming_series:MEM-.YYYY.-.#####
PURPOSE: Active member subscriptions
KEY_FIELDS: member [REQ], plan [REQ], billing_cycle [REQ], dates [REQ], rate [REQ], auto_renew, status
WORKFLOWS: Draft → Active → Expired → Cancelled → Suspended

DOCTYPE: Workspace Lead | MODULE: CRM | AUTONAME: naming_series:WL-.YYYY.-.#####
PURPOSE: Sales pipeline prospects
KEY_FIELDS: lead_name [REQ], email, phone, source, status, interested_plan, budget, team_size
WORKFLOWS: New → Contacted → Tour Scheduled → Negotiating → Converted → Lost
ACTIONS: convert_to_customer, schedule_tour

DOCTYPE: Member Contract | MODULE: Contracts | SUBMIT: Yes | AUTONAME: naming_series:MC-.YYYY.-.#####
PURPOSE: Legal agreements with members
KEY_FIELDS: member [REQ], template, terms (Jinja), dates [REQ], signature, status
WORKFLOWS: Draft → Active → Expired → Terminated → Cancelled

DOCTYPE: Training Session | MODULE: Training | SUBMIT: Yes | AUTONAME: naming_series:TS-.YYYY.-.#####
PURPOSE: Scheduled training events
KEY_FIELDS: title [REQ], module [REQ], session_date [REQ], times [REQ], venue, instructor, fee
```

## API Endpoints (Top-Level Re-exports)

```
SPACES:  get_available_spaces, create_booking, check_in, check_out
MEMBERS: get_membership_plans, create_membership, get_active_memberships, get_wallet_balance, get_member_dashboard
TRAIN:   get_training_catalog, get_upcoming_sessions, get_available_badges, get_user_badges, enroll_user, update_progress, get_user_progress
INTEG:   get_integration_status, get_unpaid_invoices
HEALTH:  ping (guest), get_dashboard_stats
```

## Scheduled Tasks

```
DAILY:  check_membership_expiry, auto_renew_memberships, send_membership_expiry_reminders, generate_daily_occupancy_snapshot
HOURLY: mark_no_show_bookings, auto_checkout_expired_bookings
CRON:   0 2 * * * → regenerate_documentation
```

## Roles

```
ARKSpace Admin     → Full CRUD + Submit all
ARKSpace Manager   → Branch management, reports
ARKSpace Sales     → CRM leads/tours, memberships
ARKSpace Operations → Spaces, bookings
ARKSpace Front Desk → Check-in/out, basic bookings
ARKSpace Member    → Self-service own records
ARKSpace Viewer    → Read-only (placeholder)
```

## Conventions

```
BILINGUAL: _ar suffix fields (space_name_ar), bilingual Select options "English / العربي"
NAMING: field:name or naming_series:PREFIX-.YYYY.-.#####
PREFIXES: BK (booking), MEM (membership), WL (lead), WT (tour), MC (contract), PR (receipt), TS (session), UTP (progress)
MODULES: arkspace_ prefix (arkspace_spaces, arkspace_memberships, etc.)
PERMISSION: Admin/Manager/Ops/FrontDesk = all; Member = own records via Customer link
REALTIME: space_status_changed, occupancy_snapshot, membership_renewed
```

## File Map

```
hooks.py          → App config, doc_events, scheduler, permissions, fixtures
install.py        → after_install: roles, space types, seed data
setup.py          → after_migrate: workflows, notifications, charts
tasks.py          → 7 scheduled tasks
permissions.py    → Row-level security for spaces, bookings, memberships
api.py            → Top-level API hub (re-exports + health + dashboard)
```

---

*Full docs: docs/TECHNICAL_IMPLEMENTATION.md | docs/API_REFERENCE.md | docs/DOCTYPES_REFERENCE.md*
