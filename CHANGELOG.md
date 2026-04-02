# Changelog — سجل التغييرات

All notable changes to ARKSpace will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [6.0.0] — 2026-03-21

### Added — الإضافات

#### Documentation & Localization
- Complete `docs/` directory with 15 documentation files
- GitHub issue templates (bug report, feature request) — bilingual
- Pull request template with comprehensive checklist
- CI workflow (lint, test, translation check) via GitHub Actions
- `README_AR.md` — Full Arabic README
- `CONTRIBUTING.md` — Bilingual contribution guide
- `CHANGELOG.md` — This file
- `arkspace/translations/en.csv` — English reference translations

#### Phase 3: Contracts, Training & Integrations
- **Contract Template** DocType with Jinja rendering (Arabic/English/Bilingual)
- **Legal Document** DocType with 10 bilingual document types
- **Member Contract** DocType (submittable) with digital signatures
- **Payment Receipt** DocType (submittable) with 6 payment methods
- **Training Module** DocType with categories and levels
- **Training Session** DocType (submittable) with venue management
- **Training Badge** DocType with gamification (4 levels)
- **User Training Progress** DocType with automatic badge awarding
- ERPNext billing bridge (booking/membership → Sales Invoice)
- Employee → Customer auto-linking
- Bulk operations: check-in, check-out, cancel, no-show from list view
- Training API: catalog, sessions, badges, enrollment, progress
- Contract term rendering with Jinja templates

#### Phase 2: CRM & Documentation
- **Workspace Lead** DocType with full sales pipeline
- **Workspace Tour** DocType with scheduling and outcome tracking
- Lead → Customer conversion (one-click)
- Tour scheduling from lead form
- **Documentation Entry** DocType (bilingual, with code examples)
- Auto-documentation generator (nightly cron at 2 AM)
- DocType README auto-creation via doc_events

#### Phase 1: Core Foundation
- 9-module architecture (Core, Spaces, Memberships, CRM, Contracts, Training, Integrations, Documentation, Design)
- **ARKSpace Settings** (Single DocType) — company config, feature toggles, API keys
- **Space Type** DocType — 6 space categories
- **Amenity** DocType — add-on services with pricing
- **Co-working Space** DocType — individual space units with bilingual names
- **Space Booking** DocType (submittable) — full lifecycle (Pending → Confirmed → Checked In → Checked Out)
- **Membership Plan** DocType — 6 plan types with benefits
- **Membership** DocType (submittable) — subscription lifecycle with auto-renew
- **Member Credit Wallet** DocType — credit system with transactions
- **Design Configuration** (Single DocType) — theming, RTL, fonts
- 7 custom roles (Admin, Manager, Sales, Operations, Front Desk, Member, Viewer)
- Row-level security (members see only own records)
- 3 workflows (Space Booking Approval, Membership Lifecycle, Lead Pipeline)
- 4 notifications (Booking Confirmation, Membership Welcome, Expiry Reminder, Booking Cancelled)
- 7 scheduled tasks (expiry check, auto-renew, reminders, occupancy, no-show, auto-checkout, doc regeneration)
- Floor Plan interactive page with color-coded status and quick-book
- Member Portal (self-service dashboard, booking, cancellation)
- Setup Wizard (4 stages)
- 7 print formats
- 3 script reports (Revenue Summary, Space Occupancy, Membership Analytics)
- 4 number cards, 5 dashboard charts
- 272 Arabic translations
- CSS design system with RTL support
- Jinja helpers (get_icon, get_color)
- Real-time events (space_status_changed, occupancy_snapshot, membership_renewed)

### Fixed — الإصلاحات

- v16 compatibility for `has_permission` hooks (explicit True/False return)
- URL routing for v16 (`/desk/` vs `/app/`)
- Test compatibility layer for v15/v16

---

## [Unreleased]

### Planned
- Enhanced analytics dashboard (v6.1.0)
- Mobile PWA with QR check-in (v6.2.0)
- ARKANOOR Marketplace integration (v6.3.0)
- AI & IoT features (v7.0.0)

---

*See [docs/ROADMAP.md](docs/ROADMAP.md) for detailed future plans.*
