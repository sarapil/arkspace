# 🏗️ Architecture — ARKSpace v5.0

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Framework | Frappe v15 |
| ERP | ERPNext v15 |
| Backend | Python 3.10+ |
| Frontend | JavaScript ES6+, Frappe UI |
| Database | MariaDB 10.6+ |
| Cache/Queue | Redis |
| Realtime | Socket.IO |
| Mobile | Flutter (Phase 5) |
| IoT | ESP32 / ARKAMOR (Phase 4) |

## Application Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Frappe Bench                      │
│  ┌───────────┐  ┌───────────┐  ┌─────────────────┐  │
│  │  Frappe    │  │  ERPNext  │  │    ARKSpace      │  │
│  │  (Core)   │  │  (ERP)    │  │    (Co-Work)     │  │
│  └───────────┘  └───────────┘  └─────────────────┘  │
│                                                      │
│  ┌───────────┐  ┌───────────┐  ┌─────────────────┐  │
│  │  HRMS     │  │  Payments │  │  Other Apps…     │  │
│  └───────────┘  └───────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────┘
         │              │                │
    ┌────▼────┐   ┌─────▼─────┐   ┌─────▼──────┐
    │ MariaDB │   │   Redis   │   │ Socket.IO  │
    └─────────┘   └───────────┘   └────────────┘
```

## Module Dependencies

```
arkspace_core
├── arkspace_spaces  ← depends on core (Branch, Settings)
│   ├── arkspace_memberships  ← depends on spaces
│   └── arkspace_crm  ← depends on spaces
├── arkspace_documentation  ← standalone
├── arkspace_design  ← standalone
├── arkspace_integrations  ← depends on spaces, memberships
├── arkspace_workspaces  ← depends on all above
├── arkspace_training  ← standalone
├── arkspace_voip  ← depends on crm
├── arkspace_iot  ← depends on core
├── arkspace_arkanoor  ← depends on spaces, memberships
└── arkspace_ai  ← depends on all
```

## Directory Structure

```
arkspace/
├── arkspace/                         # Python package root
│   ├── __init__.py                   # __version__
│   ├── hooks.py                      # Frappe hooks config
│   ├── modules.txt                   # Module list
│   ├── patches.txt                   # Migration patches
│   ├── install.py                    # Post-install setup
│   ├── api.py                        # Top-level API endpoints
│   │
│   ├── arkspace_core/                # Core module
│   │   ├── doctype/
│   │   │   ├── arkspace_settings/    # Global settings (Single)
│   │   │   └── ...
│   │   └── utils.py
│   │
│   ├── arkspace_spaces/              # Spaces & Bookings
│   │   ├── doctype/
│   │   │   ├── space_type/
│   │   │   ├── co_working_space/
│   │   │   ├── space_booking/
│   │   │   └── amenity/
│   │   └── api.py
│   │
│   ├── arkspace_memberships/         # Memberships & Billing
│   │   ├── doctype/
│   │   │   ├── membership_plan/
│   │   │   ├── membership/
│   │   │   └── member_credit_wallet/
│   │   └── api.py
│   │
│   ├── arkspace_crm/                 # Leads & Sales
│   │   ├── doctype/
│   │   │   ├── workspace_lead/
│   │   │   └── workspace_tour/
│   │   └── api.py
│   │
│   ├── arkspace_documentation/       # Auto-docs
│   │   ├── doctype/
│   │   │   ├── documentation_entry/
│   │   │   └── documentation_code_example/
│   │   ├── auto_generator.py
│   │   └── readme_generator.py
│   │
│   ├── arkspace_design/              # UI & Theming
│   │   ├── doctype/
│   │   │   └── design_configuration/
│   │   ├── colors.py
│   │   └── icons.py
│   │
│   ├── arkspace_integrations/        # ERPNext integrations
│   ├── arkspace_workspaces/          # Role-based dashboards
│   ├── arkspace_training/            # Training & Badges
│   ├── arkspace_arkanoor/            # Marketplace
│   ├── arkspace_voip/                # VoIP
│   ├── arkspace_iot/                 # ARKAMOR IoT
│   └── arkspace_ai/                  # AI Engine
│
├── public/                           # Static assets
│   ├── css/
│   │   ├── design-system.css
│   │   └── arkspace.css
│   └── js/
│       ├── arkspace.js
│       └── components/
│
├── docs/                             # Extended documentation
│   ├── modules/
│   ├── doctypes/
│   ├── apis/
│   └── tutorials/
│
├── AI-CONTEXT.md
├── ARCHITECTURE.md
├── QUICK-START.md
├── GLOSSARY.md
└── README.md
```

## Data Flow

### Booking Flow
```
Lead → Tour → Membership → Booking → Check-In → Check-Out → Invoice
```

### Membership Lifecycle
```
Plan Selection → Contract → Payment → Active → [Renew | Expire | Cancel]
```

### IoT Data Flow
```
ARKAMOR Device → HTTP POST → receive_reading API → DB Storage → Threshold Check → Alert
```
