# ARKSpace — English Documentation

> **Version:** 6.0.0 | **Language:** English

---

## About ARKSpace

ARKSpace is a comprehensive coworking and shared-space management application built natively on the Frappe Framework with deep ERPNext integration. It provides operators with everything they need to manage their spaces — from lead generation to billing — in a single, unified platform.

## Documentation Index

### Getting Started
- [User Guide](USER_GUIDE.md) — For members, front desk, and sales staff
- [Admin Guide](ADMIN_GUIDE.md) — For system administrators
- [Features Overview](FEATURES.md) — Complete feature reference

### For Developers
- [Developer Guide](../DEVELOPER_GUIDE.md) — Development setup and workflows
- [Architecture](../ARCHITECTURE.md) — System architecture and diagrams
- [API Reference](../API_REFERENCE.md) — All API endpoints
- [Technical Specs](../TECHNICAL_SPECS.md) — Technical specifications

### Other Resources
- [Troubleshooting](../TROUBLESHOOTING.md) — Common issues and solutions
- [Security](../SECURITY.md) — Security documentation
- [Sales & Marketing](../SALES_PITCH.md) — Product overview for stakeholders
- [Marketplace Listing](../MARKETPLACE_LISTING.md) — Frappe Marketplace content

## Quick Start

```bash
# Install
bench get-app https://github.com/arkan/arkspace.git
bench --site your-site install-app arkspace
bench --site your-site migrate
bench build --app arkspace

# Access
# Desk: http://your-site/desk/arkspace
# Portal: http://your-site/member-portal
# Floor Plan: http://your-site/desk/arkspace/floor-plan
```

## Key Features

| Module | Description |
|--------|-------------|
| **Spaces** | 6 space types, interactive floor plans, real-time occupancy |
| **Bookings** | Hourly/daily/monthly, auto check-in/out, bulk operations |
| **Memberships** | Plans with credit wallets, auto-renewal, expiry notifications |
| **CRM** | Lead pipeline, tour scheduling, one-click conversion |
| **Contracts** | Bilingual templates, legal documents, payment receipts |
| **Training** | Modules, sessions, badges, progress tracking |
| **Billing** | Native ERPNext integration, auto-invoicing |
| **Analytics** | 3 reports, dashboard with cards and charts |

## Support

- **Email:** dev@arkspace.io
- **Issues:** [GitHub Issues](https://github.com/arkan/arkspace/issues)
- **Arabic docs:** [docs/ar/](../ar/)

---

*ARKSpace Team | MIT License*
