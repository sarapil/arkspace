# ARKSpace Admin Guide

> **Version:** 6.0.0 | **Language:** English  
> For system administrators and ARKSpace Admin role holders.

---

## Table of Contents

1. [Installation & Setup](#installation--setup)
2. [Configuration](#configuration)
3. [User & Role Management](#user--role-management)
4. [Space Setup](#space-setup)
5. [Membership Plans](#membership-plans)
6. [Workflows](#workflows)
7. [Scheduled Tasks](#scheduled-tasks)
8. [Backups & Maintenance](#backups--maintenance)
9. [Monitoring](#monitoring)

---

## Installation & Setup

### Requirements

- Frappe v16 (or v15)
- ERPNext (required dependency)
- Python 3.12+, MariaDB 10.6+, Redis 6+

### Install

```bash
bench get-app https://github.com/arkan/arkspace.git
bench --site your-site install-app arkspace
bench --site your-site migrate
bench build --app arkspace
```

### Setup Wizard

On first access, the 4-stage setup wizard guides you through:

1. **Company Info** — Name, currency, timezone
2. **Space Setup** — Define initial space types and spaces
3. **Membership Plans** — Configure your first plans
4. **Design** — Logo, colors, branding

### Post-Installation

```bash
# Import fixtures (roles, workflows, notifications)
bench --site your-site migrate

# Clear cache
bench --site your-site clear-cache

# Verify
bench --site your-site list-apps
```

---

## Configuration

### ARKSpace Settings

Navigate to **ARKSpace > Settings** (or search for "ARKSpace Settings").

| Setting | Description | Default |
|---------|-------------|---------|
| Company | ERPNext company for billing | (first company) |
| Currency | Default currency | USD |
| Date Format | Display format | dd-mm-yyyy |
| Timezone | Server timezone | UTC |
| Default Language | ar or en | en |
| Booking Prefix | Booking ID prefix | BK |
| Membership Prefix | Membership ID prefix | MEM |
| Invoice Prefix | Invoice prefix | INV |
| Lead Prefix | Lead ID prefix | WL |

### Feature Toggles

| Feature | Description |
|---------|-------------|
| Enable VoIP | VoIP/softphone integration |
| Enable ARKAMOR IoT | IoT device integration |
| Enable ARKANOOR | Marketplace integration |
| Enable AI Features | AI-powered analytics |

### Integration Credentials

| Integration | Fields |
|-------------|--------|
| FreePBX | URL, Username, Password |
| OpenAI | API Key, Model |
| ARKANOOR | API URL, API Key |

---

## User & Role Management

### Custom Roles

| Role | Typical User | Key Permissions |
|------|-------------|-----------------|
| ARKSpace Admin | System admin | Full access to all DocTypes |
| ARKSpace Manager | Operations manager | Create, read, update, submit |
| ARKSpace Sales | Sales team | CRM access + read spaces |
| ARKSpace Operations | Ops staff | Booking/space management |
| ARKSpace Front Desk | Reception | Check-in/out operations |
| ARKSpace Member | Customer | Read own records only |
| ARKSpace Viewer | Stakeholder | Read-only access |

### Assigning Roles

1. Go to **User** list
2. Open the user
3. In **Roles** section, check the appropriate ARKSpace role
4. Save

### Row-Level Security

Members with "ARKSpace Member" role automatically see only their own:
- Space Bookings
- Memberships
- Credit Wallets

This is enforced at the database query level — no additional configuration needed.

---

## Space Setup

### 1. Define Space Types

Navigate to **Spaces > Space Type > + New**

Available types: Hot Desk, Dedicated Desk, Private Office, Meeting Room, Event Space, Virtual Office.

Configure: icon, color, whether bookable, default pricing.

### 2. Define Amenities

Navigate to **Spaces > Amenity > + New**

Set: name, hourly/daily/monthly price, complimentary flag.

### 3. Create Spaces

Navigate to **Spaces > Co-working Space > + New**

Configure:
- Name (English and Arabic)
- Space type, branch, floor
- Capacity, area (sqm)
- Hourly, daily, monthly rates
- Status (Available, Occupied, Maintenance, Reserved)
- Linked amenities
- Image gallery

---

## Membership Plans

### Creating a Plan

Navigate to **Memberships > Membership Plan > + New**

| Field | Description |
|-------|-------------|
| Plan Name | Display name (e.g., "Gold Hot Desk") |
| Plan Type | Hot Desk, Dedicated Desk, etc. |
| Monthly Price | Monthly subscription rate |
| Quarterly Price | Quarterly rate (optional) |
| Yearly Price | Yearly rate (optional) |
| Setup Fee | One-time setup fee |
| Included Hours | Monthly included hours |
| Credits | Monthly credit allocation |
| Guest Passes | Included guest passes |
| Meeting Room Hours | Included meeting room hours |
| Printing Pages | Included printing pages |
| Storage | Included storage allocation |

### Plan Strategy

- Create at least one plan per space type
- Set quarterly/yearly prices lower for commitment incentives
- Use credits for flexible usage beyond included hours

---

## Workflows

ARKSpace includes 3 pre-configured workflows:

### Space Booking Approval
```
Draft → Pending → Confirmed → Checked In → Checked Out
              ↘ Cancelled
              ↘ No Show
```

### Membership Lifecycle
```
Draft → Active → Expired
            ↘ Suspended
            ↘ Cancelled
```

### Lead Pipeline
```
New → Contacted → Tour Scheduled → Negotiating → Converted
                                               ↘ Lost
```

Workflows are exported as fixtures and auto-applied on `bench migrate`.

---

## Scheduled Tasks

| Task | Frequency | What It Does |
|------|-----------|-------------|
| `check_membership_expiry` | Daily | Marks memberships past end date as Expired |
| `auto_renew_memberships` | Daily | Renews memberships with auto-renew enabled |
| `send_membership_expiry_reminders` | Daily | Emails at 7d and 1d before expiry |
| `cleanup_expired_wallet_credits` | Daily | Marks expired credit transactions |
| `mark_no_show_bookings` | Hourly | Marks no-show after 2-hour grace |
| `auto_checkout_expired_bookings` | Hourly | Auto-checks out overdue bookings |
| `generate_all_documentation` | 02:00 daily | Regenerates auto-documentation |

All tasks run via Frappe's scheduler (Redis queue). Ensure workers are running:

```bash
# Check worker status
bench doctor

# Restart workers
supervisorctl restart all
```

---

## Backups & Maintenance

### Backups

```bash
# Manual backup
bench --site your-site backup --with-files

# Scheduled (add to crontab)
0 2 * * * cd /home/frappe/frappe-bench && bench --site your-site backup --with-files
```

### Cache Management

```bash
# Clear all cache
bench --site your-site clear-cache

# Clear website cache
bench --site your-site clear-website-cache
```

### Updates

```bash
# Update app
cd apps/arkspace && git pull

# Run migrations
bench --site your-site migrate

# Rebuild assets
bench build --app arkspace

# Restart
bench restart
```

---

## Monitoring

### Key Metrics to Watch

| Metric | How to Check |
|--------|-------------|
| Active bookings | Revenue Summary report |
| Space occupancy | Space Occupancy report |
| Membership health | Membership Analytics report |
| Unpaid invoices | ERPNext Accounts Receivable |
| Scheduler status | `bench doctor` |
| Error logs | `bench --site your-site show-logs` |

### Dashboard

The ARKSpace dashboard (desk home) shows:
- **Number Cards**: Total spaces, active bookings, active memberships, revenue
- **Charts**: Booking trends, occupancy rates, membership distribution, revenue over time, lead pipeline

---

*See also: [User Guide](USER_GUIDE.md) | [Features](FEATURES.md) | [Troubleshooting](../TROUBLESHOOTING.md)*
