# ARKSpace — Brand Identity Guide

> **Maintained by Arkan Lab** · Organisation: `moatazarkan6-lab`
> Last updated: 2025-01-01

---

## 1. App Identity

| Key | Value |
|-----|-------|
| **App Name** | ARKSpace |
| **App Title** | ARKSpace — Co-Working & Shared Space Management |
| **Version** | 6.0.0 |
| **Publisher** | Arkan Lab |
| **Prefix** | `AS` |
| **Domain** | Co-Working & Shared Space Management + ARKANOOR Marketplace |
| **Framework** | Frappe v16+ / ERPNext |
| **License** | MIT |
| **Repository** | `moatazarkan6-lab/arkspace` |

---

## 2. Color Palette

### Primary Colors

| Token | Hex | Usage |
|-------|-----|-------|
| **Navy** (Primary) | `#1B365D` | Brand anchor, headers, sidebar, primary buttons |
| **Gold** (Secondary) | `#C4A962` | Accents, highlights, premium badges, CTAs |
| **Light Navy** | `#2A4A7F` | Hover states, secondary elements |
| **Dark Navy** | `#0F1F3A` | Deep backgrounds, footers |

### Semantic Colors

| Token | Light Mode | Dark Mode | Usage |
|-------|-----------|-----------|-------|
| `--as-success` | `#28a745` | `#48d175` | Active, confirmed, available |
| `--as-warning` | `#ffc107` | `#ffca2c` | Pending, expiring soon |
| `--as-danger` | `#dc3545` | `#ff6b7a` | Cancelled, expired, full |
| `--as-info` | `#17a2b8` | `#4fc3f7` | Notes, tooltips, hints |

### Surface Colors

| Token | Light Mode | Dark Mode |
|-------|-----------|-----------|
| `--as-surface-bg` | `#f8f9fa` | `#1a1a2e` |
| `--as-surface-card` | `#ffffff` | `#16213e` |
| `--as-surface-hover` | `#e9ecef` | `#1f3056` |
| `--as-text-primary` | `#1B365D` | `#e0e0e0` |
| `--as-text-muted` | `#6c757d` | `#9e9e9e` |
| `--as-border` | `#dee2e6` | `#2a3a5c` |

### CSS Custom Properties

All colors are defined in `public/css/arkspace-variables.css` using `--as-*` prefixed tokens.
Dark mode is handled via `[data-theme="dark"]` selectors.

```css
:root {
  --as-navy: #1B365D;
  --as-primary: var(--as-navy);
  --as-secondary: #C4A962;
  /* ... full palette in arkspace-variables.css */
}
```

---

## 3. Typography

| Context | Font | Weight | Size |
|---------|------|--------|------|
| Headings (H1–H3) | System default (Frappe stack) | 700 | 1.5rem–2.5rem |
| Body text | System default | 400 | 0.875rem–1rem |
| Labels/Captions | System default | 500 | 0.75rem |
| Code/Mono | `monospace` | 400 | 0.875rem |
| Arabic text | `--font-stack` (includes Arabic fonts) | 400–700 | Same as above |

**Note:** ARKSpace inherits Frappe's font stack which includes Arabic-compatible fonts. RTL layout is automatic via Frappe's built-in `lang="ar"` / `dir="rtl"` support.

---

## 4. Logo & Iconography

### Logo Files

| File | Size | Format | Usage |
|------|------|--------|-------|
| `arkspace-logo-animated.svg` | 512×512 | SVG + SMIL | Splash screen, About page hero |
| `arkspace-logo.svg` | 512×512 | SVG static | General branding |
| `arkspace-logo.png` | 512×512 | PNG | Fallback |
| `arkspace-topbar.svg` | 40×40 | SVG | Navbar brand icon |
| `arkspace-favicon.svg` | 32×32 | SVG | Browser tab |
| `favicon.svg` / `favicon.png` | 32×32 | SVG/PNG | Alternate favicon |
| `arkspace-splash.svg` | 256×256 | SVG | Loading splash screen |
| `arkspace-login.svg` | 256×256 | SVG | Login page decoration |

### Desktop Icons (Workspace Cards)

Each workspace card has **solid** and **subtle** icon variants:

| Icon | Solid (Navy bg, white glyph) | Subtle (Light bg, navy glyph) |
|------|------|--------|
| Main | `arkspace-desk-main.svg` | `arkspace-desk-subtle-main.svg` |
| Spaces | `arkspace-desk-spaces.svg` | `arkspace-desk-subtle-spaces.svg` |
| Members | `arkspace-desk-members.svg` | `arkspace-desk-subtle-members.svg` |
| CRM | `arkspace-desk-crm.svg` | `arkspace-desk-subtle-crm.svg` |
| Training | `arkspace-desk-training.svg` | `arkspace-desk-subtle-training.svg` |
| Contracts | `arkspace-desk-contracts.svg` | `arkspace-desk-subtle-contracts.svg` |
| Settings | `arkspace-desk-settings.svg` | `arkspace-desk-subtle-settings.svg` |
| Visual | `arkspace-desk-visual.svg` | `arkspace-desk-subtle-visual.svg` |
| Reports | `arkspace-desk-reports.svg` | `arkspace-desk-subtle-reports.svg` |

**Icon sizes:** Solid/Subtle = 54×54 px. All located in `public/images/`.

### Tabler Icons Integration

All UI icons use **Tabler Icons v3.30+** via `frappe.visual.icons`:

```javascript
frappe.visual.icons.render("building", { size: "lg", color: "var(--as-navy)" })
frappe.visual.icons.forDocType("Co-working Space")
frappe.visual.icons.statusBadge("Active")
```

---

## 5. Target Personas

| # | Persona (AR) | Persona (EN) | Role | Key Workflows |
|---|-------------|--------------|------|---------------|
| 1 | **مالك مساحة مشتركة** | Space Owner | ARKSpace Admin | Full control: settings, pricing, reports, analytics, branding |
| 2 | **مدير عمليات** | Operations Manager | ARKSpace Manager | Bookings, memberships, CRM, contracts, day-to-day ops |
| 3 | **عضو / مستأجر** | Member / Tenant | ARKSpace Member | Portal: book spaces, view invoices, community, training |
| 4 | **محاسب** | Accountant | ERPNext Account User | Invoices, payment receipts, revenue reports, credit wallets |

Additional roles: `ARKSpace Front Desk` (check-in/out, visitor log, day pass), `ARKSpace Operations` (facilities, maintenance), `ARKSpace Sales` (leads, CRM pipeline).

---

## 6. Sales Tone & Messaging

| Key | Value |
|-----|-------|
| **Tone** | حيوي وعصري — Lively & Modern |
| **Tagline (AR)** | إدارة مساحتك بالكامل من نظام واحد |
| **Tagline (EN)** | Manage your entire space from one system |
| **Elevator Pitch** | ARKSpace is the all-in-one co-working management platform built on ERPNext — spaces, members, bookings, billing, CRM, community, and marketplace in a single unified system. |

### Value Propositions

1. **Unified Platform** — No more juggling 5 different tools for spaces, billing, CRM, and community
2. **ERPNext Native** — Full accounting, HR, and asset management built-in
3. **Multi-Location** — Manage branches, zones, and floors from one dashboard
4. **Community-First** — Events, networking, training, and member directory
5. **Arabic-First** — Complete RTL support with 1,790+ Arabic translations
6. **ARKANOOR Marketplace** — Members discover services and opportunities across the network

---

## 7. Competitor Positioning

| Feature | ARKSpace | Nexudus | OfficeRnD | Cobot | Optix |
|---------|----------|---------|-----------|-------|-------|
| ERP Integration | ✅ Native | ❌ | ❌ | ❌ | ❌ |
| Arabic / RTL | ✅ Full | ⚠️ Partial | ❌ | ❌ | ❌ |
| Self-Hosted | ✅ | ❌ | ❌ | ❌ | ❌ |
| Open Source | ✅ MIT | ❌ | ❌ | ❌ | ❌ |
| CRM Pipeline | ✅ Built-in | ✅ | ⚠️ | ❌ | ❌ |
| Member Portal | ✅ | ✅ | ✅ | ✅ | ✅ |
| Community Features | ✅ Full | ⚠️ | ⚠️ | ❌ | ⚠️ |
| Training / LMS | ✅ | ❌ | ❌ | ❌ | ❌ |
| Contract Management | ✅ Bilingual | ⚠️ | ⚠️ | ❌ | ❌ |
| Visual Analytics | ✅ frappe_visual | ⚠️ | ⚠️ | ❌ | ⚠️ |
| CAPS (Fine-Grained Perms) | ✅ | ❌ | ❌ | ❌ | ❌ |
| Multi-Location | ✅ | ✅ | ✅ | ⚠️ | ✅ |
| Day Pass System | ✅ | ✅ | ⚠️ | ✅ | ⚠️ |
| QR Check-in | ✅ | ⚠️ | ✅ | ⚠️ | ✅ |
| Visitor Management | ✅ | ⚠️ | ⚠️ | ❌ | ❌ |
| Credit Wallet | ✅ | ✅ | ⚠️ | ✅ | ❌ |
| Marketplace | ✅ ARKANOOR | ❌ | ❌ | ❌ | ❌ |

---

## 8. Modules & Structure

| # | Module | Prefix | DocType Count | Description |
|---|--------|--------|---------------|-------------|
| 1 | ARKSpace Core | `arkspace_core` | 4 | Settings, branches, analytics, onboarding |
| 2 | Spaces | `arkspace_spaces` | 7 | Space types, bookings, amenities, floor plans |
| 3 | Memberships | `arkspace_memberships` | 5 | Plans, memberships, credits, wallets, skills |
| 4 | CRM | `arkspace_crm` | 2 | Leads, pipeline management |
| 5 | Contracts | `arkspace_contracts` | 4 | Templates, contracts, legal documents |
| 6 | Training | `arkspace_training` | 4 | Sessions, modules, badges, progress |
| 7 | Community | `arkspace_community` | 5 | Events, posts, networking, tours |
| 8 | Integrations | `arkspace_integrations` | 2 | Online payments, payment receipts |
| 9 | Documentation | `arkspace_documentation` | 4 | Docs, examples, prerequisites, relations |
| 10 | Design | `arkspace_design` | 1 | Design configuration |

**Total: 36 DocTypes · 103+ API endpoints · 8 whitelisted endpoints in visual_api.py**

---

## 9. CAPS Integration

ARKSpace uses the **CAPS (Capability-Based Access Control)** app:

- **33 Capabilities** — 10 Module, 15 Action, 4 Field, 4 Report
- **5 Role Bundles** — Admin (33), Manager (26), Front Desk (11), Operations (13), Member (6)
- **8 Field Maps** — Mask cost/revenue fields based on capabilities
- **6 Action Maps** — Approve, cancel, check-in/out, renew, manage pricing
- Defined in `caps_integration_pack.json`

---

## 10. Pages & Navigation

### Desk Pages (6)

| Page | Route | Description |
|------|-------|-------------|
| ARK Command | `/app/ark-command` | Main dashboard with Overview / Bookings / CRM tabs |
| ARK Explorer | `/app/ark-explorer` | Visual entity browser with interactive graphs |
| ARK Live | `/app/ark-live` | Real-time floor plan + grid view |
| ARK Community | `/app/ark-community` | Events, posts, networking hub |
| ARK Onboarding | `/app/ark-onboarding` | Interactive storyboard wizard |
| ARKSpace About | `/app/arkspace-about` | 11-slide showcase for decision makers |

### Portal Pages (11 routes)

| Route | Description |
|-------|-------------|
| `/arkspace-portal` | Member portal home |
| `/arkspace-portal/book` | Space booking |
| `/arkspace-portal/profile` | Member profile |
| `/register` | New member registration |
| `/directory` | Member directory |
| `/events` | Community events |
| `/payments` | Payment history |
| `/day-pass` | Day pass purchase |
| `/arkspace-about` | Public About page |
| `/arkspace-onboarding` | Public Onboarding |
| `/عن-arkspace` | Arabic About page |

---

## 11. File Inventory

```
arkspace/
├── public/
│   ├── css/
│   │   ├── arkspace-variables.css    # Brand tokens
│   │   ├── arkspace-design-system.css # Component styles
│   │   └── arkspace.css              # Page-specific styles
│   ├── js/
│   │   ├── arkspace.js               # Core client scripts
│   │   ├── arkspace_help.js           # ❓ Contextual help system
│   │   └── ... (8 more feature JS files)
│   └── images/
│       ├── arkspace-logo-animated.svg # SMIL animated logo
│       ├── arkspace-desk-*.svg        # 18 desktop icons
│       └── ... (31 total image files)
├── translations/
│   ├── ar.csv                         # 1,790 Arabic translations
│   └── en.csv                         # 707 English translations
├── caps_integration_pack.json         # 33 capabilities + 5 bundles
├── hooks.py                           # 225 lines, full configuration
├── permissions.py                     # 226 lines, RBAC logic
├── install.py                         # 7 roles + seed data
├── setup_wizard.py / .js              # Setup wizard integration
└── BRAND.md                           # ← This file
```

---

*This document is auto-maintained alongside the ARKSpace codebase. For visual component usage, see the [frappe_visual AI Design Guide](../../.github/ai-design-guide.md).*
