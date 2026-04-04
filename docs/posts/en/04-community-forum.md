<!-- Post Type: Community Forum | Platform: discuss.frappe.io, GitHub Discussions -->
<!-- Target: Frappe developers and power users -->
<!-- Last Updated: 2026-04-04 -->

# [Announcement] ARKSpace — Coworking Space Management for ERPNext | Open Source

Hi Frappe Community! 👋

We're excited to share **ARKSpace**, a new open-source coworking app for Frappe/ERPNext.

## What it does

✅ Membership Plans & Billing
✅ Desk & Room Booking System
✅ Community Directory & Events
✅ Visitor Management & Access Control
✅ Resource Booking (Printers/AV/Meeting Rooms)
✅ Automated Invoicing & Payments
✅ Occupancy Analytics
✅ Virtual Office Services
✅ Mobile Check-in/Check-out
✅ Member Communication Portal

## Why we built it

- Coworking management tools are expensive ($120-$247/mo)
- Billing not connected to accounting system
- Manual desk booking via spreadsheets
- No community engagement tools
- Visitor management separate from member system

We couldn't find a good coworking solution that integrates natively with ERPNext, so we built one.

## Tech Stack

- **Backend:** Python, Frappe Framework v16
- **Frontend:** JavaScript, Frappe UI, frappe_visual components
- **Database:** MariaDB (standard Frappe)
- **License:** MIT
- **Dependencies:** frappe_visual, caps, arkan_help

## Installation

```bash
bench get-app https://github.com/sarapil/arkspace
bench --site your-site install-app arkspace
bench --site your-site migrate
```

## Screenshots

[Screenshots will be added to the GitHub repository]

## Roadmap

We're actively developing and would love community feedback on:
1. What features would you like to see?
2. What integrations are most important?
3. Any bugs or issues you encounter?

## Links

- 🔗 **GitHub:** https://github.com/sarapil/arkspace
- 📖 **Docs:** https://arkan.it.com/arkspace/docs
- 🏪 **Marketplace:** Frappe Cloud Marketplace
- 📧 **Contact:** support@arkan.it.com

## About Arkan Lab

We're building a complete ecosystem of open-source business apps for Frappe/ERPNext, covering hospitality, construction, CRM, communications, coworking, and more. All apps are designed to work together seamlessly.

Check out our full portfolio: https://arkan.it.com

---

*Feedback and contributions welcome! Star ⭐ the repo if you find it useful.*
