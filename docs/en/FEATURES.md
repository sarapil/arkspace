# ARKSpace Features

> **Version:** 6.0.0 | **Language:** English | **Modules:** 9

---

## Module Overview

| # | Module | DocTypes | Key Capabilities |
|---|--------|----------|-----------------|
| 1 | Core | 1 | Settings, configuration, feature toggles |
| 2 | Spaces | 5 | Space types, amenities, bookings, floor plan, ARK Live |
| 3 | Memberships | 4 | Plans, subscriptions, credit wallets, renewals |
| 4 | CRM | 2 | Lead pipeline, tour scheduling, conversion |
| 5 | Contracts | 5 | Templates, legal docs, contracts, receipts |
| 6 | Training | 4 | Modules, sessions, badges, progress |
| 7 | Integrations | — | ERPNext billing bridge, employee linking |
| 8 | Documentation | 4 | Auto-docs, README generation |
| 9 | Design | 1 | Theming, colors, RTL support |

---

## 1. Core — Central Configuration

- **ARKSpace Settings** (Single DocType): Company, currency, timezone, language, prefixes
- Feature toggles for VoIP, IoT, Marketplace, AI
- Integration credentials management
- Cross-module utility functions

## 2. Spaces — Space Management

- **6 Space Types**: Hot Desk, Dedicated Desk, Private Office, Meeting Room, Event Space, Virtual Office
- **Interactive Floor Plan**: Color-coded status, quick-book modal, floor filtering
- **ARK Live**: Real-time space monitoring page
- **Amenity Management**: Hourly/daily/monthly pricing, complimentary flag
- **Space Booking** (Submittable): Full lifecycle — Pending → Confirmed → Checked In → Checked Out
- **Bulk Operations**: Mass check-in, check-out, cancel, no-show from list view
- **Real-time Updates**: `frappe.publish_realtime("space_status_changed")` on every status change
- **Auto-tasks**: No-show detection (2hr grace) and auto-checkout (hourly)

## 3. Memberships — Subscription Platform

- **6 Plan Types** with tiered pricing (monthly/quarterly/yearly)
- **Credit Wallet**: Per-member prepaid credit system with transaction ledger
- **Auto-Renewal**: Daily task for eligible memberships
- **Expiry Reminders**: Email at 7 days and 1 day before expiry
- **Member Dashboard API**: Unified endpoint for memberships, bookings, wallet, stats

## 4. CRM — Sales Pipeline

- **Lead Tracking**: 6 acquisition channels (Website, Walk-in, Referral, Social Media, Event, Partner)
- **Pipeline**: New → Contacted → Tour Scheduled → Negotiating → Converted / Lost
- **Tour Scheduling**: Creates Workspace Tour, auto-updates lead status
- **One-Click Conversion**: Lead → Customer → ready for membership

## 5. Contracts — Legal Management

- **Jinja Templates**: Arabic, English, and Bilingual contract generation
- **Legal Documents**: 10 document types with front/back uploads, expiry tracking
- **Member Contracts** (Submittable): Digital signatures, witness, company signatory
- **Payment Receipts** (Submittable): 6 payment methods, period tracking
- **Print Formats**: Booking Confirmation, Membership Card, Receipt

## 6. Training — Learning Platform

- **Training Modules**: Categorized (Technical, Business, Creative, Wellness, Community, Onboarding) with levels
- **Training Sessions** (Submittable): Scheduled with venue, instructor, capacity, fees
- **Gamification**: Badge system (Bronze, Silver, Gold, Platinum) across 5 categories
- **Progress Tracking**: Per-user per-module with automatic badge awarding

## 7. Integrations — ERPNext Bridge

- **Auto-Invoicing**: Sales Invoice on booking/membership submit
- **Cancellation Credits**: Handles billing on cancellation
- **Employee Linking**: Auto-links Employee ↔ Customer records
- **Integration Status**: Reports installed apps (ERPNext, HRMS, Payments)
- **Unpaid Invoices**: API for outstanding balance queries

## 8. Documentation — Self-Documenting

- **Documentation Entry**: Structured docs for Modules, DocTypes, APIs, Workflows, Tutorials, FAQs
- **Auto-Generator**: Nightly cron regenerates documentation from code introspection
- **README Generator**: Auto-creates DocType READMEs on insert/update

## 9. Design — Theming & Branding

- **Design Configuration**: Primary/secondary/accent colors, button/link styling
- **Icon Library**: Font Awesome 6, Material Icons, or Custom
- **RTL Support**: Full right-to-left toggle
- **Font Configuration**: Separate Arabic and English font families
- **Jinja Helpers**: `get_icon()` and `get_color()` for templates
- **Brand**: Navy (#1B365D) primary, Gold (#C4A962) accent

---

## Statistics

| Metric | Count |
|--------|-------|
| Modules | 9 |
| DocTypes (standalone) | 18 |
| DocTypes (child tables) | 7 |
| Submittable DocTypes | 5 |
| Single DocTypes | 2 |
| API Endpoints | 36 |
| Custom Roles | 7 |
| Workflows | 3 |
| Scheduled Tasks | 7 |
| Print Formats | 3 |
| Notifications | 4 |
| Reports | 3 |
| Pages | 2 |
| Translations | 706 (Arabic) |

---

*See also: [User Guide](USER_GUIDE.md) | [Admin Guide](ADMIN_GUIDE.md) | [Arabic version](../ar/FEATURES.md)*
