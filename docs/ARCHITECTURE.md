# ARKSpace — System Architecture

> **Version:** 6.0.0 | **Updated:** 2026-03-21  
> Detailed architecture reference for ARKSpace.

---

## High-Level Architecture

```
                    ┌──────────────────────────┐
                    │     Browser / Client      │
                    │  Desk │ Portal │ Mobile   │
                    └───────────┬──────────────┘
                                │ HTTP/WS
                    ┌───────────┴──────────────┐
                    │   Gunicorn / Socketio     │
                    │   (Frappe Web Server)     │
                    └───────────┬──────────────┘
                                │
     ┌──────────────────────────┼──────────────────────────┐
     │              Frappe Framework v16                     │
     │                                                      │
     │  ┌────────────────────────────────────────────────┐ │
     │  │            ARKSpace Application                 │ │
     │  │                                                 │ │
     │  │  9 Modules  │  25 DocTypes  │  36 APIs         │ │
     │  │  2 Pages    │  3 Reports    │  7 Tasks         │ │
     │  │  3 Workflows│  7 Roles      │  4 Notifications │ │
     │  └────────────────────────────────────────────────┘ │
     │                                                      │
     │  ┌──────────┐  ┌──────────┐  ┌────────────────┐    │
     │  │ ERPNext  │  │ Redis    │  │ Background     │    │
     │  │ Customer │  │ Cache    │  │ Workers (RQ)   │    │
     │  │ Invoice  │  │ Queue    │  │ Schedule       │    │
     │  │ Employee │  │ Realtime │  │ Long/Short     │    │
     │  └──────────┘  └──────────┘  └────────────────┘    │
     └──────────────────────────┬──────────────────────────┘
                                │
                    ┌───────────┴──────────────┐
                    │     MariaDB 10.6+        │
                    │     25 app tables         │
                    └──────────────────────────┘
```

---

## Module Architecture

### Module Dependency Graph

```
arkspace_core ─────────────────────────────────────────────┐
  │                                                         │
  ├── arkspace_design (standalone — theming)                │
  │                                                         │
  ├── arkspace_spaces ──── arkspace_memberships             │
  │       │                       │                         │
  │       │                  arkspace_crm                   │
  │       │                       │                         │
  │       └── arkspace_contracts (uses Spaces + Members)    │
  │                                                         │
  ├── arkspace_training (standalone — uses Customer)        │
  │                                                         │
  ├── arkspace_integrations (bridges Spaces + Members → ERPNext)
  │                                                         │
  └── arkspace_documentation (standalone — auto-generation) │
```

### Module Responsibilities

| Module | Responsibility | Key Patterns |
|--------|----------------|--------------|
| **Core** | Settings, permissions, shared tasks | Single DocType pattern, permission hooks |
| **Spaces** | Space CRUD, booking lifecycle | State machine, conflict detection, real-time events |
| **Memberships** | Subscription management | Credit wallet, auto-renewal, plan-based pricing |
| **CRM** | Lead-to-customer pipeline | Multi-step workflow, conversion actions |
| **Contracts** | Document management | Jinja templating, bilingual rendering, child tables |
| **Training** | Learning management | Gamification (badges), progress tracking |
| **Integrations** | ERPNext bridge | Event-driven invoice creation, doc_events hooks |
| **Documentation** | Auto-generated docs | Cron-based regeneration, DocType introspection |
| **Design** | Theming system | CSS variables, Jinja helpers, RTL support |

---

## Data Flow Patterns

### Booking Flow

```
[User]                    [ARKSpace]                 [ERPNext]
  │                          │                          │
  ├─ Create Booking ────────>│                          │
  │                          ├─ Validate availability   │
  │                          ├─ Calculate pricing       │
  │<── Booking (Pending) ───┤                          │
  │                          │                          │
  ├─ Submit ─────────────────>│                          │
  │                          ├─ Check overlap           │
  │                          ├─ Set Confirmed           │
  │                          ├─ on_submit hook ────────>│
  │                          │                          ├─ Create Invoice
  │<── Booking (Confirmed)──┤<── Invoice link ─────────┤
  │                          │                          │
  ├─ Check In ───────────────>│                          │
  │                          ├─ Set Checked In          │
  │                          ├─ Update Space status     │
  │                          ├─ publish_realtime()      │
  │                          │                          │
  ├─ Check Out ──────────────>│                          │
  │                          ├─ Set Checked Out         │
  │                          ├─ Update Space → Available│
  │                          ├─ publish_realtime()      │
```

### Membership Lifecycle

```
[Admin]                   [ARKSpace]                 [Scheduler]
  │                          │                          │
  ├─ Create Membership ────>│                          │
  │                          ├─ Link to Plan            │
  │                          ├─ Create Credit Wallet    │
  │                          ├─ Allocate Credits        │
  │                          │                          │
  ├─ Submit ─────────────────>│                          │
  │                          ├─ Set Active              │
  │                          ├─ on_submit → Invoice     │
  │                          │                          │
  │                          │              ┌───────────┤
  │                          │              │ Daily task │
  │                          │              ├───────────┘
  │                          │<─ check_expiry ──────────┤
  │                          ├─ Mark Expired            │
  │                          │<─ auto_renew ────────────┤
  │                          ├─ Create new Membership   │
  │                          ├─ publish_realtime()      │
```

---

## Frontend Architecture

### Asset Loading

```python
# hooks.py
app_include_css = [
    "/assets/arkspace/css/design-system.css",   # CSS variables, colors, RTL
    "/assets/arkspace/css/arkspace.css",         # App-specific styles
]
app_include_js = [
    "/assets/arkspace/js/arkspace.js",           # Main JS bundle
]
web_include_css = "/assets/arkspace/css/arkspace_portal.css"
web_include_js = "/assets/arkspace/js/arkspace_portal.js"
```

### JavaScript Namespace

```javascript
arkspace = {
    floor_plan: { /* Floor Plan page logic */ },
    ark_live:   { /* ARK Live page logic */ },
    // Form scripts loaded per-DocType
};
```

### Real-time Events

| Event | Publisher | Subscriber | Data |
|-------|----------|------------|------|
| `space_status_changed` | Booking check-in/out | Floor Plan, ARK Live | `{space, status}` |
| `booking_update` | Booking lifecycle | Booking list views | `{booking_id, status}` |
| `membership_renewed` | Auto-renewal task | Membership forms | `{membership, plan}` |

---

## Database Schema

### Table Statistics

| Category | Tables | Records (typical) |
|----------|--------|--------------------|
| Space management | 5 | 50–500 spaces |
| Booking management | 1 | 1,000–100,000 bookings |
| Membership management | 4 | 100–10,000 members |
| CRM | 2 | 500–5,000 leads |
| Contracts | 5 | 100–5,000 contracts |
| Training | 4 | 50–500 modules |
| Documentation | 4 | Auto-generated |
| Configuration | 2 | 1 each (Single) |

### Key Indexes

- `tabSpace Booking`: `(space, start_datetime, end_datetime)` — overlap queries
- `tabSpace Booking`: `(status, start_datetime)` — active bookings
- `tabMembership`: `(member, status, end_date)` — expiry checks
- `tabWorkspace Lead`: `(status, assigned_to)` — pipeline queries

---

## Security Architecture

### Authentication Flow

```
[User] ─── Login ──> [Frappe Auth] ──> [Session Cookie]
   │                                         │
   ├─ Desk Access ──> Role-based UI ─────────┤
   │                                         │
   ├─ Portal Access ──> Website User ────────┤
   │                                         │
   └─ API Access ──> Token/Session auth ─────┘
```

### Permission Layers

1. **DocType Permissions**: Standard Frappe role-based permissions per DocType
2. **Row-Level Security**: Custom `has_permission()` and `permission_query_conditions()` in `permissions.py`
3. **API Guards**: `frappe.has_permission()` checks in all whitelisted methods
4. **Portal Guards**: Login checks in all `www/` page controllers

---

## Deployment Architecture

### Single-Server (Development)

```
┌─────────────────────────────────────┐
│          Docker Container            │
│                                      │
│  bench start                         │
│  ├── gunicorn (web) :8000           │
│  ├── socketio :9000                 │
│  ├── redis-cache :13000             │
│  ├── redis-queue :11000             │
│  ├── worker-short                   │
│  ├── worker-long                    │
│  └── scheduler                      │
│                                      │
│  MariaDB :3306                      │
└─────────────────────────────────────┘
```

### Production (Recommended)

```
┌─────────┐     ┌──────────────┐     ┌──────────┐
│  Nginx  │────>│  Gunicorn    │────>│ MariaDB  │
│  :443   │     │  :8000       │     │ :3306    │
└─────────┘     └──────────────┘     └──────────┘
     │          ┌──────────────┐     ┌──────────┐
     └────────>│  Socketio    │────>│ Redis    │
                │  :9000       │     │ :6379    │
                └──────────────┘     └──────────┘
                ┌──────────────┐
                │  Workers     │
                │  Scheduler   │
                └──────────────┘
```

---

*See also: [TECHNICAL_IMPLEMENTATION.md](TECHNICAL_IMPLEMENTATION.md) | [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)*
