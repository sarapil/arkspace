# ARKSpace — Technical Context

## Overview

**Enterprise Co-Working Space Management + ARKANOOR Marketplace.** ARKSpace is a comprehensive co-working space management platform covering space bookings, memberships, day passes, QR check-in, visitor management, dynamic pricing, online payments, multi-location support, community features, training modules, contracts, analytics, and a member portal. It includes a full self-service portal for members and a setup wizard for initial configuration.

- **Publisher:** Arkan Lab
- **Version:** (latest)
- **License:** MIT
- **Color:** `#1B365D` (navy blue)
- **Dependencies:** `erpnext`

## Architecture

- **Framework:** Frappe v16
- **Modules:** 10 (ARKSpace Core, Documentation, Design, Spaces, Memberships, CRM, Integrations, Training, Contracts, Community)
- **DocTypes:** 37 (including child tables)
- **API Files:** 5 (core + module-specific)
- **Pages:** 6 (desk pages)
- **Reports:** 3
- **Portal Pages:** 12 (member self-service)
- **Scheduled Tasks:** 12 (daily + hourly)

### Module Architecture

| Module | Directory | Purpose |
|--------|-----------|---------|
| ARKSpace Core | `arkspace_core/` | Analytics engine, multi-location, utilities, visual API |
| ARKSpace Documentation | `arkspace_documentation/` | Auto-generated DocType documentation |
| ARKSpace Design | `arkspace_design/` | Design system: icons, colors, CSS variables |
| ARKSpace Spaces | `arkspace_spaces/` | Space management, bookings, floor plans, pricing |
| ARKSpace Memberships | `arkspace_memberships/` | Membership plans, lifecycle, renewals |
| ARKSpace CRM | `arkspace_crm/` | Workspace leads and sales pipeline |
| ARKSpace Integrations | `arkspace_integrations/` | ERPNext billing, payment gateways |
| ARKSpace Training | `arkspace_training/` | Member training modules and progress |
| ARKSpace Contracts | `arkspace_contracts/` | Legal documents, member contracts, templates |
| ARKSpace Community | `arkspace_community/` | Events, posts, networking, member directory |

## Key Components

### Core Engine Files

| File | Module | Purpose |
|------|--------|---------|
| `analytics_engine.py` | Core | Occupancy analytics, revenue tracking, snapshots |
| `multi_location.py` | Core | Multi-branch location management |
| `visual_api.py` | Core | Data providers for frappe_visual components |
| `utils.py` | Core | Shared utility functions |
| `pricing_engine.py` | Spaces | Dynamic pricing with rules and time-based rates |
| `floor_plan.py` | Spaces | Visual floor plan management |
| `qr_checkin.py` | Spaces | QR code check-in/check-out |
| `visitor_management.py` | Spaces | Visitor registration and tracking |
| `day_pass_api.py` | Spaces | Day pass purchase and management |
| `ark_live.py` | Spaces | Real-time space availability |
| `bulk_operations.py` | Spaces | Bulk booking and membership operations |
| `billing.py` | Integrations | ERPNext Sales Invoice creation on booking/membership/day-pass |
| `payment_gateway.py` | Integrations | Online payment processing |
| `community.py` | Community | Community posts, events, networking |
| `auto_generator.py` | Documentation | Auto-generate documentation on migrate |
| `readme_generator.py` | Documentation | DocType README generation on create/update |
| `icons.py` | Design | Tabler icon helper (Jinja) |
| `colors.py` | Design | Brand color helper (Jinja) |

### API Layer (5 files)

| File | Purpose |
|------|---------|
| `api.py` (root) | Core API: space availability, booking, member info |
| `arkspace_spaces/api.py` | Space listing, search, availability check |
| `arkspace_memberships/api.py` | Membership plans, status, renewal |
| `arkspace_integrations/api.py` | Payment and billing endpoints |
| `arkspace_training/api.py` | Training module enrollment and progress |

### Pages (Desk)

| Page | Route | Purpose |
|------|-------|---------|
| `ark_command` | `/desk/ark-command` | Command center / main dashboard |
| `ark_live` | `/desk/ark-live` | Real-time space availability map |
| `ark_explorer` | `/desk/ark-explorer` | Space exploration and search |
| `ark_community` | `/desk/ark-community` | Community hub |
| `ark_onboarding` | `/desk/ark-onboarding` | Guided onboarding |
| `arkspace_about` | `/desk/arkspace-about` | App showcase |

### Portal Pages (Member Self-Service, `/www/`)

| Route | Page | Purpose |
|-------|------|---------|
| `/arkspace_portal` | Dashboard | Member dashboard with bookings, credits, stats |
| `/arkspace_portal/book` | Booking | Self-service space booking |
| `/arkspace_portal/profile` | Profile | Member profile management |
| `/memberships` | Memberships | View/manage memberships |
| `/payments` | Payments | Payment history |
| `/day_pass` | Day Pass | Purchase day passes |
| `/analytics` | Analytics | Usage analytics (ARKSpace Admin only) |
| `/community` | Community | Community feed and posts |
| `/events` | Events | Community events |
| `/directory` | Directory | Member directory |
| `/register` | Register | New member registration |

### Frontend

**Desk Assets:**
| File | Purpose |
|------|---------|
| `arkspace.js` | Core initialization and workspace |
| `arkspace_help.js` | Help/onboarding system |
| `online_payments.js` | Payment processing UI |
| `dynamic_pricing.js` | Pricing rule configuration UI |
| `qr_checkin.js` | QR check-in/check-out UI |
| `visitor_management.js` | Visitor registration UI |
| `day_pass.js` | Day pass management UI |
| `analytics.js` | Analytics dashboard components |
| `multi_location.js` | Multi-location switcher |
| `community.js` | Community features UI |
| `setup_wizard.js` | Setup wizard steps |

**Portal Assets:**
| File | Purpose |
|------|---------|
| `arkspace_portal.js` | Member portal interactivity |
| `arkspace_portal.css` | Portal styling |

**Design System:**
| File | Purpose |
|------|---------|
| `arkspace-variables.css` | CSS custom properties (colors, spacing, typography) |
| `design-system.css` | Reusable component styles |
| `arkspace.css` | Core application styles |

## DocType Summary

### Configuration & Core

| DocType | Module | Purpose |
|---------|--------|---------|
| ARKSpace Settings | Core | Global configuration |
| ARKSpace Branch | Core | Multi-location branch definitions |
| Design Configuration | Design | UI/UX configuration |
| Analytics Snapshot | Core | Daily occupancy and revenue snapshots |

### Spaces & Bookings

| DocType | Module | Purpose |
|---------|--------|---------|
| Co-working Space | Spaces | Individual space/desk/room definitions |
| Space Type | Spaces | Types of spaces (desk, office, meeting room) |
| Space Amenity | Spaces | Child: amenity linked to a space |
| Space Image | Spaces | Child: images for a space |
| Amenity | Spaces | Amenity master (WiFi, projector, whiteboard) |
| Space Booking | Spaces | Booking records with approval workflow |
| Pricing Rule | Spaces | Dynamic pricing rules (peak/off-peak, duration) |
| Day Pass | Spaces | Single-day access passes |
| Visitor Log | Spaces | Visitor check-in/check-out records |

### Memberships

| DocType | Module | Purpose |
|---------|--------|---------|
| Membership Plan | Memberships | Plan definitions (basic, premium, enterprise) |
| Membership | Memberships | Active membership records with lifecycle |
| Member Credit Wallet | Memberships | Booking credit balance per member |
| Credit Transaction | Memberships | Credit additions/deductions log |

### CRM

| DocType | Module | Purpose |
|---------|--------|---------|
| Workspace Lead | CRM | Sales leads for space rentals |

### Payments

| DocType | Module | Purpose |
|---------|--------|---------|
| Online Payment | Integrations | Online payment transaction records |
| Payment Receipt | Integrations | Payment receipt generation |

### Training

| DocType | Module | Purpose |
|---------|--------|---------|
| Training Module | Training | Training content modules |
| Training Session | Training | Scheduled training sessions |
| Training Badge | Training | Achievement badges for training |
| User Training Progress | Training | Individual user progress tracking |
| Member Skill | Training | Skills acquired through training |

### Contracts

| DocType | Module | Purpose |
|---------|--------|---------|
| Contract Template | Contracts | Reusable contract templates |
| Member Contract | Contracts | Signed member contracts |
| Legal Document | Contracts | Legal document master |
| Contract Legal Document | Contracts | Child: legal doc linked to contract |

### Community

| DocType | Module | Purpose |
|---------|--------|---------|
| Community Event | Community | Community events with RSVP |
| Community Post | Community | Member posts/announcements |
| Networking Request | Community | Member-to-member networking requests |

### Documentation (Auto-Generated)

| DocType | Module | Purpose |
|---------|--------|---------|
| Documentation Entry | Documentation | Auto-generated DocType documentation |
| Documentation Code Example | Documentation | Child: code examples |
| Documentation Prerequisite | Documentation | Child: prerequisite references |
| Documentation Relation | Documentation | Child: related documentation links |
| Workspace Tour | Documentation | Guided workspace tours |

## Reports

| Report | Purpose |
|--------|---------|
| Space Occupancy | Space utilization rates and trends |
| Revenue Summary | Revenue by space type, membership plan, period |
| Membership Analytics | Membership growth, churn, renewal rates |

## Scheduled Tasks

| Schedule | Tasks |
|----------|-------|
| Daily (2 AM) | Regenerate documentation |
| Daily | Check membership expiry, auto-renew memberships, send expiry reminders, generate daily occupancy snapshot, bulk generate booking QR codes, expire day passes, capture analytics snapshot |
| Hourly | Mark no-show bookings, auto-checkout expired bookings, expire stale online payments, auto-checkout day passes, update community event statuses |

## Integration Points

- **ERPNext:** Deep integration via `arkspace_integrations/billing.py` — creates Sales Invoices on booking submit, membership submit, day pass submit; links Employees to Customers; handles cancellations
- **Payment Gateways:** Online payment processing via `payment_gateway.py`
- **Frappe Core:** Custom permissions with `has_permission` and `permission_query_conditions` for spaces, bookings, memberships; setup wizard integration; fixtures for roles, workflows, notifications, number cards, dashboard charts, print formats
- **frappe_visual (indirect):** `visual_api.py` provides data for visual components; design system with icons and colors
- **HRMS (indirect):** Employee → Customer linking for staff who are also members

## Permissions Model

Custom permission handlers for multi-tenant data isolation:
- `has_space_permission` / `get_space_conditions` — Branch-based space access
- `has_booking_permission` / `get_booking_conditions` — User sees own bookings; admins see all
- `has_membership_permission` / `get_membership_conditions` — User sees own memberships

## Roles

Declared via fixtures: `ARKSpace%` pattern (ARKSpace Admin, ARKSpace Manager, ARKSpace Member, etc.)

## Setup Wizard

Custom setup wizard stages via `setup_wizard.py` with frontend in `setup_wizard.js` for initial branch, space type, and membership plan configuration.

## Portal Menu

10 portal menu items providing full member self-service: Dashboard, My Memberships, My Payments, Book a Space, My Profile, Day Pass, Analytics (admin only), Community, Events, Member Directory.
