# ARKSpace — Complete Application Context

> Comprehensive reference for deep understanding of ARKSpace.  
> For token-efficient version, see [AI_CONTEXT.md](AI_CONTEXT.md).

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Data Model](#data-model)
4. [Business Logic](#business-logic)
5. [User Interface](#user-interface)
6. [Integrations](#integrations)
7. [Configuration](#configuration)
8. [Security](#security)

---

## Overview

### Purpose

ARKSpace is an enterprise-grade, bilingual (Arabic/English) co-working space management platform. It solves the problem of fragmented tools for managing co-working operations by providing a unified system covering space inventory, booking lifecycle, membership subscriptions, CRM pipeline, contracts, training, and billing — all integrated with ERPNext.

### Target Users

| User Type | Description | Primary Use Cases |
|-----------|-------------|-------------------|
| Space Admin | System administrator | Configure settings, manage roles, monitor system |
| Branch Manager | Branch-level manager | Space management, reports, membership oversight |
| Sales Rep | CRM/Sales team | Lead capture, tour scheduling, conversion |
| Front Desk | Day-to-day operations | Check-in/out, bookings, walk-in management |
| Member | Co-working space user | Portal: view bookings, profile, book spaces |
| Trainer | Training instructor | Manage sessions, track participant progress |

### Key Features

1. **Space Management**: Define space types, individual spaces with amenities, images, pricing tiers (hourly/daily/monthly). Interactive floor plans with real-time status.
2. **Booking Engine**: Full lifecycle (Pending → Confirmed → Checked In → Checked Out), support for hourly/daily/monthly bookings, bulk operations, conflict detection, amenity add-ons.
3. **Membership System**: Flexible plans (Hot Desk, Dedicated Desk, Private Office, Meeting Room, Event Space, Virtual Office), billing cycles (Monthly/Quarterly/Yearly), credit wallets, auto-renewal.
4. **CRM Pipeline**: Lead capture from multiple sources, interest tracking, tour scheduling with outcome recording, automated conversion to Customer + Membership.
5. **Contract Management**: Bilingual contract templates with Jinja variable rendering, legal document management (10 document types), digital signatures, payment receipts.
6. **Training Platform**: Training modules with sessions, badge/gamification system (Bronze→Platinum), progress tracking per user, fee management.
7. **ERPNext Integration**: Automatic Sales Invoice creation from bookings and memberships, Employee→Customer linking.
8. **Member Portal**: Self-service web portal for booking spaces, viewing profile/membership details, managing bookings.
9. **Setup Wizard**: 4-stage guided setup (Workspace → Branches → Space Types → First Plan).

---

## Architecture

### System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                       Client Layer                            │
│   ┌──────────┐   ┌──────────────┐   ┌───────────────────┐   │
│   │ Frappe   │   │ Member       │   │ REST API          │   │
│   │ Desk UI  │   │ Portal (www) │   │ /api/method/...   │   │
│   └────┬─────┘   └──────┬───────┘   └─────────┬─────────┘   │
└────────┼────────────────┼──────────────────────┼─────────────┘
         │                │                      │
┌────────┴────────────────┴──────────────────────┴─────────────┐
│                   Frappe Framework v16                         │
│                                                               │
│   ┌───────────────────────────────────────────────────────┐  │
│   │                 ARKSpace v6.0.0                         │  │
│   │                                                         │  │
│   │   ┌─────────────┐  ┌──────────────┐  ┌─────────────┐  │  │
│   │   │ Spaces      │  │ Memberships  │  │ CRM         │  │  │
│   │   │ • Types     │  │ • Plans      │  │ • Leads     │  │  │
│   │   │ • Bookings  │  │ • Wallets    │  │ • Tours     │  │  │
│   │   │ • Amenities │  │ • Credits    │  │ • Pipeline  │  │  │
│   │   │ • Floor Plan│  │ • Auto-renew │  │ • Conversion│  │  │
│   │   └─────────────┘  └──────────────┘  └─────────────┘  │  │
│   │                                                         │  │
│   │   ┌─────────────┐  ┌──────────────┐  ┌─────────────┐  │  │
│   │   │ Contracts   │  │ Training     │  │ Integrations│  │  │
│   │   │ • Templates │  │ • Modules    │  │ • Billing   │  │  │
│   │   │ • Legal Docs│  │ • Sessions   │  │ • Invoicing │  │  │
│   │   │ • Contracts │  │ • Badges     │  │ • Employee  │  │  │
│   │   │ • Receipts  │  │ • Progress   │  │   linking   │  │  │
│   │   └─────────────┘  └──────────────┘  └─────────────┘  │  │
│   │                                                         │  │
│   │   ┌─────────────┐  ┌──────────────┐  ┌─────────────┐  │  │
│   │   │ Core        │  │ Design       │  │Documentation│  │  │
│   │   │ • Settings  │  │ • Colors     │  │ • Auto-gen  │  │  │
│   │   │ • Tasks     │  │ • Icons      │  │ • README    │  │  │
│   │   │ • Roles     │  │ • RTL        │  │ • Entries   │  │  │
│   │   │ • Perms     │  │ • Fonts      │  │ • Relations │  │  │
│   │   └─────────────┘  └──────────────┘  └─────────────┘  │  │
│   └───────────────────────────────────────────────────────┘  │
│                                                               │
│   ┌───────────┐   ┌──────────┐   ┌──────────────────────┐   │
│   │ Workflows │   │ Fixtures │   │ Scheduled Tasks      │   │
│   │ 3 defined │   │ 6 types  │   │ 4 daily + 2 hourly  │   │
│   └───────────┘   └──────────┘   └──────────────────────┘   │
└──────────────────────────────┬───────────────────────────────┘
                               │
┌──────────────────────────────┴───────────────────────────────┐
│                       Data Layer                              │
│   ┌──────────┐   ┌──────────┐   ┌────────────────────────┐  │
│   │ MariaDB  │   │  Redis   │   │ ERPNext (Customer,     │  │
│   │ 25 tables│   │ Cache/Q  │   │ Invoice, Employee)     │  │
│   └──────────┘   └──────────┘   └────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

### Module Dependencies

```
arkspace_core (Settings, Roles, Permissions)
├── arkspace_spaces (Spaces, Bookings, Floor Plans)
│   └── arkspace_memberships (Plans, Subscriptions, Credits)
│       └── arkspace_crm (Leads, Tours, Conversion)
├── arkspace_contracts (Templates, Legal Docs, Contracts)
├── arkspace_training (Modules, Sessions, Badges)
├── arkspace_integrations (ERPNext Billing Bridge)
├── arkspace_documentation (Auto-generated Docs)
└── arkspace_design (Theming, Colors, RTL)
```

---

## Data Model

### Entity Relationship Overview

```
[Space Type] 1────N [Co-working Space] 1────N [Space Booking]
                         │                          │
                    N [Space Amenity]           1 [Membership]
                    N [Space Image]                  │
                                              1 [Membership Plan]
                                                     │
                                              1 [Member Credit Wallet]
                                                     │
                                              N [Credit Transaction]

[Workspace Lead] ──(convert)──> [Customer] + [Membership]
       │
  1 [Workspace Tour]

[Contract Template] ──(populate)──> [Member Contract]
                                          │
                                    N [Contract Legal Document]
                                    N [Payment Receipt]

[Legal Document] ──(standalone)──> Member's legal docs

[Training Module] 1────N [Training Session]
                             │
                        N [User Training Progress]
                             │
                        1 [Training Badge]
```

### Core DocType Details

#### Co-working Space
- **Fields**: space_name, branch, floor, space_number, space_type (Link), capacity, area_sqm, hourly_rate, daily_rate, monthly_rate, status (Available/Occupied/Maintenance/Reserved), current_member, main_image
- **Child Tables**: Space Amenity, Space Image
- **Business Rules**: Capacity must be ≥ 1. Setting a pricing warning if no tiers set. Status changes on check-in/out.

#### Space Booking
- **Fields**: booking_id, space (Link), member (Link:Customer), booking_type (Hourly/Daily/Monthly), start/end datetime, duration_hours, rate, total_amount, discount_percent, net_amount, status, checked_in_at, checked_out_at, sales_invoice
- **Submittable**: Yes
- **Workflow**: Pending → Confirmed → Checked In → Checked Out (also: No Show, Cancelled)
- **Business Rules**: Overlap detection, rate auto-calculation, ERPNext invoice on submit.

#### Membership
- **Fields**: member (Link:Customer), membership_plan (Link), billing_cycle, start_date, end_date, auto_renew, status, credit_wallet (Link), assigned_space (Link)
- **Submittable**: Yes
- **Workflow**: Draft → Active → Expired/Suspended
- **Business Rules**: Auto-renewal via daily task. Credit allocation. Invoice on submit.

#### Workspace Lead
- **Fields**: lead_name, email, phone, company, source, interested_plan, interested_space_type, team_size, monthly_budget, status, assigned_to, converted_customer, converted_membership
- **Workflow**: New → Contacted → Tour Scheduled → Negotiating → Converted/Lost
- **Actions**: `convert_to_customer()` — creates Customer + Membership from lead data.

#### Member Contract
- **Fields**: contract_title, contract_date, member (Link:Customer), space (Link), membership, template (Link), start_date, end_date, rate, currency, discount, net_amount, security_deposit, terms_ar, terms_en, signatures, status
- **Submittable**: Yes
- **Bilingual**: All labels and Select options are bilingual ("English / العربية")
- **Actions**: `populate_from_template()` — fills terms from Jinja template with document variables.

---

## Business Logic

### Core Processes

#### Booking Flow
```
Member selects Space → Checks availability → Creates Booking (Pending)
  → Submit (Confirmed) → Check In → Check Out → Invoice generated
                                                  ↓
                                          Space status → Available
```

#### Membership Lifecycle
```
Create Plan → Create Membership → Submit (Active) → Credits allocated
  → Daily task checks expiry → Auto-renew OR Mark Expired
  → Invoice generated on submit
```

#### Lead Conversion
```
New Lead → Contact → Schedule Tour → Complete Tour → Negotiation
  → Convert: Creates Customer + Membership + marks Lead as Converted
```

### Scheduled Tasks

| Schedule | Task | Purpose |
|----------|------|---------|
| Daily 02:00 | `regenerate_documentation` | Auto-generate DocType documentation |
| Daily | `check_membership_expiry` | Mark expired memberships |
| Daily | `auto_renew_memberships` | Create new memberships for auto-renew |
| Daily | `send_membership_expiry_reminders` | Email reminders before expiry |
| Daily | `generate_daily_occupancy_snapshot` | Record occupancy metrics |
| Hourly | `mark_no_show_bookings` | Mark unattended bookings as No Show |
| Hourly | `auto_checkout_expired_bookings` | Force check-out overdue bookings |

### Automation Rules

| Trigger | Condition | Action |
|---------|-----------|--------|
| Space Booking on_submit | Has linked Customer | Create Sales Invoice |
| Space Booking on_cancel | Has Sales Invoice | Cancel linked Invoice |
| Membership on_submit | Has linked Customer | Create membership Invoice |
| Employee after_insert | — | Link Employee to Customer |
| DocType after_insert | Developer mode | Auto-generate README |

---

## User Interface

### Workspaces (Desk)

| Workspace | Contents |
|-----------|----------|
| ARKSpace Management | All DocTypes, Reports, Pages, Quick actions |

### Custom Pages

| Page | Route | Purpose |
|------|-------|---------|
| Floor Plan | `/desk/floor-plan` | Interactive SVG floor plan with space status |
| ARK Live | `/desk/ark-live` | Real-time space monitoring with quick booking |

### Reports

| Report | Type | Purpose |
|--------|------|---------|
| Revenue Summary | Script Report | Booking + Membership revenue by period |
| Space Occupancy | Script Report | Space utilization and hours booked |
| Membership Analytics | Script Report | Plan distribution, growth, retention |

### Portal Pages (www/)

| Page | Route | Purpose |
|------|-------|---------|
| Portal Home | `/arkspace_portal` | Member dashboard with stats |
| Book a Space | `/arkspace_portal/book` | Self-service space booking |
| My Profile | `/arkspace_portal/profile` | View/edit profile and membership |

---

## Integrations

### ERPNext (Required)

| Integration | Direction | Purpose |
|-------------|-----------|---------|
| Customer | Read/Write | Members are linked to ERPNext Customers |
| Sales Invoice | Write | Auto-created from bookings and memberships |
| Employee | Read | Auto-link to Customer on creation |

### Real-time Events

| Event | Trigger | Data |
|-------|---------|------|
| `space_status_changed` | Check-in/out, booking | `{space, status, member}` |
| `booking_update` | Any booking change | `{booking_id, status}` |
| `membership_renewed` | Auto-renewal task | `{membership, plan}` |

---

## Configuration

### ARKSpace Settings (Single DocType)

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| fiscal_year_start | Date | — | Fiscal year start for reports |
| primary_language | Select | Arabic | Primary UI language |
| secondary_language | Select | English | Secondary UI language |
| timezone | Data | — | Default timezone |
| booking_prefix | Data | BK- | Booking ID prefix |
| membership_prefix | Data | MEM- | Membership ID prefix |
| default_currency | Link:Currency | EGP | Default currency |
| enable_voip | Check | 0 | Enable VoIP integration |
| enable_ai | Check | 0 | Enable AI features |

### Design Configuration (Single DocType)

| Setting | Type | Description |
|---------|------|-------------|
| primary_color | Color | Brand primary color |
| secondary_color | Color | Brand secondary color |
| enable_rtl | Check | Enable RTL layout |
| arabic_font | Data | Arabic font family |
| english_font | Data | English font family |

---

## Security

### Permission Model

| Role | Spaces | Bookings | Memberships | CRM | Contracts | Training | Settings |
|------|--------|----------|-------------|-----|-----------|----------|----------|
| Admin | CRUD | CRUD | CRUD | CRUD | CRUD | CRUD | CRUD |
| Manager | CRUD | CRUD | CRUD | CRU | CR | CRU | R |
| Sales | R | R | R | CRUD | CR | R | — |
| Operations | RU | CRUD | RU | R | R | R | — |
| Front Desk | R | CRU | R | R | — | R | — |
| Member | R(own) | CR(own) | R(own) | — | R(own) | R(own) | — |
| Viewer | R | R | R | R | R | R | — |

### Row-Level Security

Implemented in `arkspace/permissions.py`:
- Members only see their own bookings, memberships, and contracts
- Branch-level filtering for Manager/Operations roles
- Custom `has_permission` and `permission_query_conditions` for core DocTypes

### Data Protection

- PII fields: member email, phone, address (in contracts)
- Legal documents store sensitive identification
- Portal authentication required for all member actions
- No API endpoints allow guest access except `test_ping`

---

*This is the complete context. For token-efficient version, see [AI_CONTEXT.md](AI_CONTEXT.md).*  
*For API details, see [API_REFERENCE.md](API_REFERENCE.md).*
