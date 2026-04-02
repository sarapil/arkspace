<p align="center">
  <img src="arkspace/public/images/arkspace-logo-animated.svg" alt="ARKSpace Logo" width="128">
</p>

<h1 align="center">ARKSpace v6.0.0 — أرك سبيس</h1>

<p align="center">
  <strong>Complete Coworking & Shared Space Management for ERPNext</strong>
</p>

<p align="center">
  <a href="#installation"><img src="https://img.shields.io/badge/Frappe-v15%20%7C%20v16-blue" alt="Frappe Version"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-green" alt="License"></a>
  <a href="#"><img src="https://img.shields.io/badge/Python-3.12%2B-blue" alt="Python"></a>
  <a href="#"><img src="https://img.shields.io/badge/Translations-706%20strings-orange" alt="Translations"></a>
  <a href="#"><img src="https://img.shields.io/badge/Language-Arabic%20%2B%20English-purple" alt="Languages"></a>
</p>

<p align="center">
  <a href="README_AR.md">العربية</a> •
  <a href="docs/en/README.md">English Docs</a> •
  <a href="docs/ar/README.md">التوثيق العربي</a> •
  <a href="CONTRIBUTING.md">Contributing</a> •
  <a href="CHANGELOG.md">Changelog</a>
</p>

---

## Overview

ARKSpace is a comprehensive, bilingual (Arabic/English) coworking space management platform built natively on the Frappe Framework with deep ERPNext integration. It manages the complete lifecycle of coworking operations — from lead generation to billing — in a single, unified platform.

### ✨ Highlights

- 🏢 **6 Space Types** with interactive floor plans and real-time occupancy
- 📅 **Smart Booking Engine** with auto check-in/out and no-show detection
- 🎫 **Membership Platform** with credit wallets and auto-renewal
- 📊 **Built-in CRM** with lead pipeline and tour scheduling
- 📝 **Contract Management** with bilingual Jinja templates
- 🎓 **Training & Gamification** with badges and progress tracking
- 💰 **Native ERPNext Billing** — auto-invoicing, no middleware
- 🌐 **Full Arabic + English** — 706 translated strings, RTL-ready

---

## Installation

```bash
cd frappe-bench
bench get-app https://github.com/arkan/arkspace.git
bench --site your-site install-app arkspace
bench --site your-site migrate
bench build --app arkspace
```

### Access Points

| Interface | URL |
|-----------|-----|
| Desk (Back-office) | `http://your-site/desk/arkspace` |
| Floor Plan | `http://your-site/desk/arkspace/floor-plan` |
| ARK Live | `http://your-site/desk/arkspace/ark-live` |
| Member Portal | `http://your-site/member-portal` |

---

## Modules (9)

| Module | Description | الوصف |
|--------|-------------|-------|
| **Core** | Settings, feature toggles, utilities | الإعدادات والأدوات |
| **Spaces** | Space types, amenities, bookings, floor plan | المساحات والحجوزات |
| **Memberships** | Plans, credit wallets, auto-renewal | العضويات والمحافظ |
| **CRM** | Leads, tours, sales pipeline | المبيعات والعملاء |
| **Contracts** | Templates, legal docs, receipts | العقود والمستندات |
| **Training** | Modules, sessions, badges, progress | التدريب والشارات |
| **Integrations** | ERPNext billing bridge | تكامل ERPNext |
| **Documentation** | Auto-generated docs | التوثيق التلقائي |
| **Design** | Theming, icons, RTL support | نظام التصميم |

---

## Key Statistics

| Metric | Count |
|--------|-------|
| DocTypes | 25 (18 standalone + 7 child tables) |
| API Endpoints | 36 |
| Custom Roles | 7 |
| Workflows | 3 |
| Scheduled Tasks | 7 |
| Print Formats | 3 |
| Notifications | 4 |
| Script Reports | 3 |
| Custom Pages | 2 |
| Translations (Arabic) | 706 strings |

---

## Documentation

### 📘 User Documentation

| Document | English | العربية |
|----------|---------|---------|
| User Guide | [docs/en/USER_GUIDE.md](docs/en/USER_GUIDE.md) | [docs/ar/USER_GUIDE.md](docs/ar/USER_GUIDE.md) |
| Admin Guide | [docs/en/ADMIN_GUIDE.md](docs/en/ADMIN_GUIDE.md) | [docs/ar/ADMIN_GUIDE.md](docs/ar/ADMIN_GUIDE.md) |
| Features | [docs/en/FEATURES.md](docs/en/FEATURES.md) | [docs/ar/FEATURES.md](docs/ar/FEATURES.md) |

### 🔧 Technical Documentation

| Document | Purpose |
|----------|---------|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | System architecture & diagrams |
| [docs/TECHNICAL_SPECS.md](docs/TECHNICAL_SPECS.md) | Technical specifications |
| [docs/API_REFERENCE.md](docs/API_REFERENCE.md) | All 36 API endpoints |
| [docs/DOCTYPES_REFERENCE.md](docs/DOCTYPES_REFERENCE.md) | All 25 DocType schemas |
| [docs/DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md) | Developer onboarding |
| [docs/SECURITY.md](docs/SECURITY.md) | Security architecture |

### 📋 Project

| Document | Purpose |
|----------|---------|
| [CHANGELOG.md](CHANGELOG.md) | Version history |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to contribute |
| [docs/ROADMAP.md](docs/ROADMAP.md) | Product roadmap |
| [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Common issues & fixes |
| [docs/SESSION_LOG.md](docs/SESSION_LOG.md) | Development session log |

### 🤖 AI & Context

| Document | Purpose |
|----------|---------|
| [docs/AI_PROMPT.md](docs/AI_PROMPT.md) | AI assistant instructions |
| [docs/CONTEXT.md](docs/CONTEXT.md) | Complete application context |
| [docs/AI_CONTEXT.md](docs/AI_CONTEXT.md) | Token-efficient LLM reference |

### 📦 Marketplace

| Document | Purpose |
|----------|---------|
| [docs/SALES_PITCH.md](docs/SALES_PITCH.md) | Sales & marketing content |
| [docs/MARKETPLACE_LISTING.md](docs/MARKETPLACE_LISTING.md) | Frappe Marketplace listing |
| [marketplace/listing.json](marketplace/listing.json) | Machine-readable listing |

---

## Requirements

| Component | Version |
|-----------|---------|
| Frappe | v15 or v16 |
| ERPNext | Matching Frappe version |
| Python | 3.12+ |
| MariaDB | 10.6+ |
| Redis | 6.0+ |
| Node.js | 18+ |

---

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Security

For vulnerability reports, see [SECURITY.md](SECURITY.md).

## License

[MIT](LICENSE) — ARKSpace Team (dev@arkspace.io)
