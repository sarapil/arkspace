# ARKSpace Roadmap

> **Version:** 6.0.0 | **Updated:** 2026-03-21

## Version History

### v6.0.0 — Enterprise Release 🟢

All three phases completed successfully.

#### Phase 1: Core Foundation 🟢
- [x] ARKSpace Settings (Single DocType)
- [x] Space Type & Amenity DocTypes
- [x] Co-working Space management
- [x] Space Booking with full lifecycle
- [x] Membership Plans & Subscriptions
- [x] Member Credit Wallet system
- [x] Design Configuration & theming
- [x] Setup Wizard (4 stages)
- [x] 7 custom roles with row-level security
- [x] Floor Plan interactive page

#### Phase 2: CRM & Documentation 🟢
- [x] Workspace Lead with pipeline management
- [x] Workspace Tour scheduling & tracking
- [x] Lead → Customer conversion
- [x] Documentation Entry system
- [x] Auto-documentation generator (nightly cron)
- [x] README auto-generation for DocTypes

#### Phase 3: Contracts, Training & Integrations 🟢
- [x] Contract Template with Jinja rendering
- [x] Legal Document management (10 document types)
- [x] Member Contract with digital signatures
- [x] Payment Receipt system
- [x] Training Module & Session management
- [x] Training Badge gamification
- [x] User Training Progress tracking
- [x] ERPNext billing bridge
- [x] Employee → Customer auto-linking
- [x] Bulk operations (check-in/out/cancel/no-show)

---

## Upcoming Features

### v6.1.0 — Enhanced Analytics 🟡
**Target:** Q2 2026 | **Status:** In Progress

- [ ] Advanced occupancy analytics dashboard
- [ ] Revenue forecasting reports
- [ ] Member retention metrics
- [ ] Space utilization heatmaps
- [ ] Export to Excel/PDF for all reports

**Blockers:** None

### v6.2.0 — Mobile & Portal 🔴
**Target:** Q3 2026 | **Status:** Not Started

- [ ] Progressive Web App (PWA) for members
- [ ] QR code check-in/out
- [ ] Mobile-optimized booking flow
- [ ] Push notifications
- [ ] Member self-service portal enhancements

**Blockers:** None

### v6.3.0 — Multi-tenant & Marketplace 🔴
**Target:** Q4 2026 | **Status:** Not Started

- [ ] ARKANOOR Marketplace integration
- [ ] Multi-branch inventory management
- [ ] Inter-branch booking transfers
- [ ] Marketplace listing for available spaces
- [ ] Partner API for third-party bookings

**Blockers:** ARKANOOR API specification

### v7.0.0 — AI & IoT 🔴
**Target:** 2027 | **Status:** Not Started

- [ ] AI-powered space recommendations
- [ ] Predictive occupancy planning
- [ ] ARKAMOR IoT sensor integration
- [ ] Automated climate & lighting control
- [ ] Smart access control integration

**Blockers:** ARKAMOR hardware availability

---

## Technical Debt & Improvements

### High Priority 🟡

| Item | Status | Notes |
|------|--------|-------|
| Add comprehensive test suite | 🟡 In Progress | Unit tests for all controllers |
| Improve error handling in APIs | 🔴 Not Started | Standardize error responses |
| Add rate limiting to public APIs | 🔴 Not Started | Prevent abuse |
| Optimize N+1 queries in dashboards | 🟡 In Progress | Use `frappe.get_all` efficiently |

### Medium Priority

| Item | Status | Notes |
|------|--------|-------|
| Add WebSocket tests | 🔴 Not Started | Test realtime events |
| Improve RTL CSS edge cases | 🟡 In Progress | Some components misaligned |
| Add Playwright E2E tests | 🔴 Not Started | Critical user flows |
| Document all Jinja template variables | 🟢 Completed | In contract template docs |

### Low Priority

| Item | Status | Notes |
|------|--------|-------|
| Dark mode support | 🔴 Not Started | Design Configuration extension |
| CSV export for translations | 🟢 Completed | Using bench commands |
| API versioning | ⚪ Blocked | Waiting for Frappe v17 support |

---

## Suggestions Log

| Date | Suggestion | Status |
|------|-----------|--------|
| 2026-03-21 | Complete documentation restructure | 🟢 Done |
| 2026-03-21 | Add GitHub issue/PR templates | 🟢 Done |
| 2026-03-21 | Add CI workflow | 🟢 Done |
| 2026-03-21 | Create bilingual CONTRIBUTING.md | 🟢 Done |
| 2026-03-21 | Add en.csv reference translations | 🟢 Done |
| 2026-02-17 | Bulk operations for bookings | 🟢 Completed in v6.0 |
| 2026-02-10 | Floor plan interactive page | 🟢 Completed in v6.0 |
| 2026-01-15 | Training gamification with badges | 🟢 Completed in v6.0 |

---

## Status Legend

| Emoji | Meaning |
|-------|---------|
| 🔴 | Not Started |
| 🟡 | In Progress |
| 🟢 | Completed |
| 🔵 | Testing |
| ⚪ | Blocked |

---

*See also: [FEATURES_EN.md](FEATURES_EN.md) | [CHANGELOG.md](../CHANGELOG.md)*
