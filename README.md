# 🏢 ARKSpace v5.0 — أرك سبيس

> Enterprise Co-Working Space Management + ARKANOOR Marketplace  
> Built on Frappe v15 / ERPNext v15

## Overview

ARKSpace is a comprehensive co-working space management platform consisting of:

- **ARKSpace** — Frappe app for managing workspaces, memberships, bookings & CRM
- **ARKANOOR** — Centralized marketplace connecting all co-working spaces
- **ARKAMOR** — IoT device for real-time environmental monitoring

## Quick Start

```bash
cd frappe-bench
bench get-app arkspace   # or bench get-app /path/to/arkspace
bench --site dev.localhost install-app arkspace
bench --site dev.localhost migrate
bench start
```

## Modules

| Module | Description | الوصف |
|--------|-------------|-------|
| Core | Settings & branch management | الإعدادات والفروع |
| Documentation | Auto-generated docs & AI context | التوثيق التلقائي |
| Design | UI components & theming | نظام التصميم |
| Spaces | Space types, units & bookings | المساحات والحجوزات |
| Memberships | Plans, contracts & billing | العضويات والفوترة |
| CRM | Leads, tours & pipeline | المبيعات والعملاء |
| Integrations | ERPNext HR/Accounting/LMS | التكاملات |
| Workspaces | Role-based dashboards | لوحات الأدوار |
| Training | Courses, quizzes & badges | التدريب والشارات |
| ARKANOOR | Marketplace hub | السوق المركزي |
| VoIP | FreePBX / call tracking | الاتصالات |
| IoT | ARKAMOR sensors | أجهزة البيئة |
| AI | Analytics & recommendations | الذكاء الاصطناعي |

## License

MIT
