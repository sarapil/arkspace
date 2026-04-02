# ARKSpace — Frappe Marketplace Listing

> Content prepared for submission to [frappecloud.com/marketplace](https://frappecloud.com/marketplace)

---

## App Name

**ARKSpace** — Coworking & Shared Space Management

## Tagline

Complete coworking space management — bookings, memberships, CRM, contracts, billing — natively integrated with ERPNext.

## Category

Business Tools / Real Estate / Workspace Management

## Version

6.0.0

## Pricing

Free & Open Source (MIT License)

## Author

ARKSpace Team  
dev@arkspace.io

## Repository

https://github.com/arkan/arkspace

---

## Short Description (≤160 characters)

Manage coworking spaces end-to-end: space bookings, memberships, CRM pipeline, contracts, training, billing — all integrated natively with ERPNext.

---

## Long Description

### What is ARKSpace?

ARKSpace is a comprehensive coworking and shared-space management application built natively on the Frappe Framework with deep ERPNext integration. It provides everything operators need to manage their spaces — from lead generation to billing — in a single, unified platform.

### Who is it for?

- **Coworking space operators** managing bookings, memberships, and billing
- **Corporate facility managers** running internal shared desks and meeting rooms
- **Training centers** that combine workspace with education programs
- **Community hubs** needing member management and event spaces

### Key Features

#### 🏢 Space Management
Manage 6 space types (Hot Desk, Dedicated Desk, Private Office, Meeting Room, Event Space, Virtual Office) with interactive visual floor plans, real-time occupancy tracking, and amenity management.

#### 📅 Smart Booking Engine
Full booking lifecycle with availability checking, conflict detection, hourly/daily/monthly pricing, automatic check-in/out, no-show detection, and bulk operations for front-desk efficiency.

#### 🎫 Membership Platform
6 plan types with tiered pricing (monthly/quarterly/yearly), credit wallet system for prepaid hours, automatic renewal and expiry notifications, and a comprehensive member dashboard.

#### 📊 Built-in CRM
Track leads from 6 acquisition channels through a full pipeline (New → Contacted → Tour Scheduled → Negotiating → Converted), schedule facility tours, and convert prospects to customers with one click.

#### 📝 Contract Management
Jinja-powered contract templates supporting Arabic, English, and bilingual formats. Digital document management for 10 legal document types, payment receipt generation, and 3 professional print formats.

#### 🎓 Training & Community
Built-in learning management with training modules, scheduled sessions, a gamification system with Bronze-to-Platinum badges, and per-member progress tracking.

#### 💰 Native ERPNext Billing
Automatic Sales Invoice creation on booking and membership submission. Handles cancellation credits, employee-customer linking, and unpaid invoice tracking — all without middleware or API glue.

#### 📈 Reports & Analytics
Three script reports (Revenue Summary, Space Occupancy, Membership Analytics) plus a dashboard with number cards and charts for real-time business intelligence.

#### 🌐 Bilingual Support
Full Arabic and English support with 700+ translated strings, RTL-ready design, bilingual contracts, and dual-language field support throughout.

### Architecture

- **9 modules** for clean separation of concerns
- **25 DocTypes** (18 standalone + 7 child tables)
- **36 API endpoints** for automation and integration
- **7 custom roles** with row-level security
- **3 workflows** for booking approval, membership lifecycle, and lead pipeline
- **7 scheduled tasks** for automation (renewals, reminders, no-show detection)
- **4-stage setup wizard** for guided configuration

### Requirements

- Frappe v16 (v15 compatible)
- ERPNext (required dependency)
- Python 3.12+
- MariaDB 10.6+

### Installation

```bash
bench get-app https://github.com/arkan/arkspace.git
bench --site your-site install-app arkspace
bench --site your-site migrate
bench build --app arkspace
```

---

## Screenshots

> Place screenshots in `marketplace/screenshots/`

1. **Dashboard** — Overview with number cards and charts
2. **Floor Plan** — Interactive visual floor plan with color-coded spaces
3. **Space Booking** — Booking form with calendar view
4. **Membership** — Membership management with credit wallet
5. **CRM Pipeline** — Lead tracking and tour scheduling
6. **Contract** — Bilingual contract with template rendering
7. **Training** — Training module catalog with badges
8. **Member Portal** — Self-service member interface
9. **Setup Wizard** — 4-stage guided configuration

---

## Tags

`coworking`, `shared-space`, `workspace-management`, `booking`, `membership`, `crm`, `contracts`, `training`, `billing`, `erpnext`, `arabic`, `rtl`, `bilingual`

---

## listing.json

```json
{
  "name": "arkspace",
  "title": "ARKSpace",
  "description": "Complete coworking space management with bookings, memberships, CRM, contracts, training, and billing — natively integrated with ERPNext.",
  "version": "6.0.0",
  "author": "ARKSpace Team",
  "email": "dev@arkspace.io",
  "license": "MIT",
  "repository": "https://github.com/arkan/arkspace",
  "category": "Business Tools",
  "tags": [
    "coworking",
    "workspace",
    "booking",
    "membership",
    "crm",
    "billing",
    "erpnext"
  ],
  "required_apps": ["erpnext"],
  "supported_versions": ["v15", "v16"],
  "pricing": "free",
  "languages": ["en", "ar"],
  "screenshots": [
    "marketplace/screenshots/dashboard.png",
    "marketplace/screenshots/floor-plan.png",
    "marketplace/screenshots/booking.png",
    "marketplace/screenshots/membership.png",
    "marketplace/screenshots/crm.png",
    "marketplace/screenshots/contract.png"
  ]
}
```

---

## Marketplace Checklist

- [x] README.md with installation instructions
- [x] LICENSE file (MIT)
- [x] CHANGELOG.md with version history
- [x] CONTRIBUTING.md with guidelines
- [x] pyproject.toml with proper metadata
- [x] hooks.py with `add_to_apps_screen` configuration
- [x] Arabic translations (706 entries)
- [x] GitHub Actions CI pipeline
- [x] Issue and PR templates
- [ ] Screenshots (to be captured from running instance)
- [ ] Demo video (recommended)
- [ ] Frappe Cloud one-click install testing

---

*Prepared by ARKSpace Team | dev@arkspace.io*
