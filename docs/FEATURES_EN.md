# ARKSpace Features — English

> **Version:** 6.0.0 | **Updated:** 2026-03-21 | **Modules:** 9

## Table of Contents

- [1. ARKSpace Core](#1-arkspace-core)
- [2. ARKSpace Spaces](#2-arkspace-spaces)
- [3. ARKSpace Memberships](#3-arkspace-memberships)
- [4. ARKSpace CRM](#4-arkspace-crm)
- [5. ARKSpace Contracts](#5-arkspace-contracts)
- [6. ARKSpace Training](#6-arkspace-training)
- [7. ARKSpace Integrations](#7-arkspace-integrations)
- [8. ARKSpace Documentation](#8-arkspace-documentation)
- [9. ARKSpace Design](#9-arkspace-design)

---

## 1. ARKSpace Core

Central configuration and utilities for the entire application.

### Capabilities

- **ARKSpace Settings** (Single DocType): company info, currency, timezone, date format, language preferences
- Configurable prefixes for bookings (`BK`), memberships (`MEM`), invoices, and leads (`WL`)
- Feature toggles: VoIP, ARKAMOR IoT, ARKANOOR Marketplace, AI features
- Integration credentials: FreePBX, OpenAI, ARKANOOR API
- Utility functions for cross-module use

### User Roles

All roles can read settings; only **ARKSpace Admin** can modify.

---

## 2. ARKSpace Spaces

Manages co-working space inventory, types, amenities, and bookings.

### Capabilities

- **Space Type**: Define categories (Hot Desk, Dedicated Desk, Private Office, Meeting Room, Event Space, Virtual Office) with icons, colors, and booking toggles
- **Amenity**: Define add-on services with hourly/daily/monthly pricing and complimentary flag
- **Co-working Space**: Individual units with name (bilingual), type, branch, floor, capacity, area, hourly/daily/monthly rates, status tracking, amenities table, image gallery
- **Space Booking** (Submittable): Full booking lifecycle — Pending → Confirmed → Checked In → Checked Out, with cancel/no-show support
- **Check-in/Check-out**: Real-time status with `frappe.publish_realtime("space_status_changed")` events
- **Floor Plan Page**: Interactive visual floor plan with color-coded status, quick-book modal, live occupancy stats, floor filtering
- **Bulk Operations**: Mass check-in, check-out, cancel, and no-show from list view
- **Hourly Auto-tasks**: `mark_no_show_bookings` (2-hour grace), `auto_checkout_expired_bookings`

### API Endpoints

| Endpoint | Description |
|----------|-------------|
| `get_available_spaces` | Query spaces by type, branch, date range |
| `create_booking` | Create and submit a booking |
| `check_in` | Check in to a confirmed booking |
| `check_out` | Check out from a booking |

### Related

- [Memberships](#3-arkspace-memberships) — Membership bookings use credit wallets
- [Integrations](#7-arkspace-integrations) — Booking submit creates Sales Invoice

---

## 3. ARKSpace Memberships

Subscription management with plans, credit wallets, and lifecycle automation.

### Capabilities

- **Membership Plan**: 6 plan types with pricing tiers (monthly/quarterly/yearly), setup fees, included hours, credits, guests, meeting room hours, printing pages, storage
- **Membership** (Submittable): Full lifecycle — Draft → Active → Expired → Cancelled → Suspended, with auto-renew option
- **Member Credit Wallet**: Per-customer wallet with credit/debit/expired/refund transactions
- **Auto-renewal**: Daily task renews eligible memberships, creates new billing periods
- **Expiry Reminders**: Automated emails at 7 days and 1 day before expiry
- **Member Dashboard API**: Unified endpoint returning memberships, bookings, wallet, and stats

### API Endpoints

| Endpoint | Description |
|----------|-------------|
| `get_membership_plans` | Available plans filtered by type |
| `create_membership` | Create and activate a membership |
| `get_active_memberships` | List active memberships |
| `get_wallet_balance` | Credit wallet balance |
| `get_member_dashboard` | Comprehensive member overview |

### Scheduled Tasks

- `check_membership_expiry` — Daily: marks expired memberships
- `auto_renew_memberships` — Daily: auto-renews eligible
- `send_membership_expiry_reminders` — Daily: email reminders

---

## 4. ARKSpace CRM

Lead management and sales pipeline for converting prospects to members.

### Capabilities

- **Workspace Lead**: Track prospects with source (Website, Walk-in, Referral, Social Media, Event, Partner), pipeline status (New → Contacted → Tour Scheduled → Negotiating → Converted → Lost), interested plan/space type, budget, team size
- **Workspace Tour**: Schedule and track facility tours with rating, outcome tracking, and automatic conversion
- **Convert to Customer**: One-click lead conversion creates Customer record and links to membership
- **Schedule Tour**: Creates Workspace Tour and updates lead status automatically
- **Complete Tour**: Records tour outcome, propagates status to lead

### Whitelisted Methods

| Method | DocType | Description |
|--------|---------|-------------|
| `convert_to_customer` | Workspace Lead | Creates Customer, marks Converted |
| `schedule_tour` | Workspace Lead | Creates Workspace Tour |
| `complete_tour` | Workspace Tour | Marks complete, updates lead |

---

## 5. ARKSpace Contracts

Legal document management, contract templates, and payment receipts.

### Capabilities

- **Contract Template**: Jinja-powered templates for Membership, Booking, Office Rental, Event Space, Virtual Office contracts; supports Arabic, English, and Bilingual; placeholder auto-population
- **Legal Document**: Store and track member legal documents (National ID, Passport, Commercial Register, Tax Card, etc.) with front/back file uploads, expiry tracking, validation status
- **Member Contract** (Submittable): Full contract lifecycle — Draft → Active → Expired → Terminated → Cancelled; member signatures, witness support, company signatory, linked legal documents
- **Payment Receipt** (Submittable): 6 bilingual receipt types with payment methods (Cash, Bank Transfer, Credit Card, Check, Online Payment, Wallet), period tracking, linked to contracts/memberships/bookings
- **Template Rendering**: `render_contract_terms` whitelisted method populates Jinja templates with member details, space info, plan data, dates, and financials

### Print Formats

- Booking Confirmation
- Membership Card
- Membership Receipt

---

## 6. ARKSpace Training

Learning management with modules, sessions, badges, and progress tracking.

### Capabilities

- **Training Module**: Categorized (Technical, Business, Creative, Wellness, Community, Onboarding) with levels (Beginner, Intermediate, Advanced), syllabus, prerequisites, enrollment tracking
- **Training Session** (Submittable): Scheduled sessions with venue (physical or online), instructor, fee management, capacity tracking
- **Training Badge**: Gamification with badge categories (Completion, Streak, Mastery, Community, Special) and levels (Bronze, Silver, Gold, Platinum), points system
- **User Training Progress**: Individual progress tracking per user per module, automatic badge awarding on completion

### API Endpoints

| Endpoint | Description |
|----------|-------------|
| `get_training_catalog` | Published modules by category/level |
| `get_upcoming_sessions` | Scheduled sessions |
| `get_available_badges` | All active badges |
| `get_user_badges` | Badges earned by a user |
| `enroll_user` | Enroll in a module |
| `update_progress` | Update progress, award badges |
| `get_user_progress` | User's progress records |

---

## 7. ARKSpace Integrations

Bridges between ARKSpace and ERPNext for billing and employee management.

### Capabilities

- **Billing Bridge**: Automatic Sales Invoice creation on booking/membership submit and cancellation
- **Employee Linking**: Auto-links employees to customers for member portal access
- **Integration Status API**: Reports which apps (ERPNext, HRMS, Payments) are installed
- **Unpaid Invoices API**: Retrieves outstanding invoices for a member

### Events

| DocType | Event | Handler |
|---------|-------|---------|
| Space Booking | on_submit | `billing.on_booking_submit` |
| Space Booking | on_cancel | `billing.on_booking_cancel` |
| Membership | on_submit | `billing.on_membership_submit` |
| Membership | on_cancel | `billing.on_membership_cancel` |
| Employee | after_insert/on_update | `billing.link_employee_to_customer` |

---

## 8. ARKSpace Documentation

Auto-generated documentation system for the application itself.

### Capabilities

- **Documentation Entry**: Structured docs for Modules, DocTypes, APIs, Workflows, Tutorials, FAQs — bilingual with code examples, prerequisites, and related doc links
- **Auto-Generator**: Nightly cron (2 AM) regenerates documentation entries from code introspection
- **README Generator**: Auto-creates/updates DocType READMEs on insert/update via `doc_events`

### Child Tables

- Documentation Code Example (language, title, code)
- Documentation Relation (related entry, relation type)
- Documentation Prerequisite (prerequisite entry, mandatory flag)

---

## 9. ARKSpace Design

Theming, icons, and RTL support configuration.

### Capabilities

- **Design Configuration** (Single DocType): Centralized theme control — primary/secondary/accent/success/danger colors, button styling, link styling, icon library selection (Font Awesome 6, Material Icons, Custom), RTL toggle, Arabic/English font families
- **CSS Design System**: `design-system.css` with CSS custom properties, RTL-aware layouts
- **Jinja Helpers**: `get_icon()` and `get_color()` available in templates
- **Brand Colors**: Navy (#1B365D) primary, Gold (#C4A962) accent

---

## Summary Statistics

| Metric | Count |
|--------|-------|
| Modules | 9 |
| DocTypes (standalone) | 18 |
| DocTypes (child tables) | 7 |
| Submittable DocTypes | 5 |
| Single DocTypes | 2 |
| API Endpoints | ~30 |
| Custom Roles | 7 |
| Workflows | 3 |
| Scheduled Tasks | 7 |
| Print Formats | 7 |
| Notifications | 4 |
| Reports | 3 |
| Number Cards | 4 |
| Dashboard Charts | 5 |

---

*See also: [FEATURES_AR.md](FEATURES_AR.md) | [API_REFERENCE.md](API_REFERENCE.md) | [DOCTYPES_REFERENCE.md](DOCTYPES_REFERENCE.md)*
