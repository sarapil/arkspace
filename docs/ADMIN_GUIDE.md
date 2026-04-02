# ARKSpace Admin Guide

> **Version:** 6.0.0 | **Updated:** 2026-03-21  
> Guide for system administrators installing, configuring, and managing ARKSpace.

## Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [User & Role Management](#user--role-management)
- [Space Management](#space-management)
- [Membership Management](#membership-management)
- [Scheduled Tasks](#scheduled-tasks)
- [Backup & Maintenance](#backup--maintenance)
- [Monitoring](#monitoring)

---

## Installation

### Prerequisites

- Frappe v16 bench environment
- ERPNext v16 installed
- MariaDB 10.6+
- Redis 7+
- Node.js 20+
- Python 3.12+

### Install Steps

```bash
# 1. Get the app
cd frappe-bench
bench get-app arkspace

# 2. Install on your site
bench --site {site} install-app arkspace

# 3. Run migrations
bench --site {site} migrate

# 4. Build frontend assets
bench build --app arkspace

# 5. Restart bench
bench start
```

### Post-Installation

After installation, the Setup Wizard will appear on first access:

1. **Welcome**: Set workspace name, currency, timezone
2. **Branches**: Add your co-working locations
3. **Space Types**: Select offered space types
4. **First Plan**: Create your first membership plan

### Upgrade

```bash
cd frappe-bench/apps/arkspace
git pull
cd ../..
bench --site {site} migrate
bench build --app arkspace
bench --site {site} clear-cache
```

---

## Configuration

### ARKSpace Settings

Navigate to: **ARKSpace > Settings > ARKSpace Settings**

| Setting | Description | Default |
|---------|-------------|---------|
| Company | ERPNext company for billing | Required |
| Default Currency | Currency for pricing | From ERPNext |
| Primary Language | Main UI language | Arabic |
| Secondary Language | Secondary language | English |
| Timezone | System timezone | UTC |
| Booking Prefix | Booking ID prefix | BK |
| Membership Prefix | Membership ID prefix | MEM |
| Lead Prefix | Lead ID prefix | WL |

### Feature Toggles

| Toggle | Description |
|--------|-------------|
| Enable VoIP | VoIP calling integration |
| Enable ARKAMOR IoT | IoT sensor integration |
| Enable ARKANOOR Hub | Marketplace integration |
| Enable AI Features | AI-powered features |

### Design Configuration

Navigate to: **ARKSpace > Settings > Design Configuration**

- **Colors**: Primary (#1B365D), Secondary, Accent (#C4A962), Success, Danger
- **Typography**: Arabic font, English font
- **RTL**: Enable/disable right-to-left layout
- **Icons**: Font Awesome 6 / Material Icons / Custom

---

## User & Role Management

### Roles

| Role | Recommended For | Key Permissions |
|------|----------------|-----------------|
| ARKSpace Admin | IT/System admin | Full CRUD + Submit on all |
| ARKSpace Manager | Branch manager | Branch management, all reports |
| ARKSpace Sales | Sales team | CRM, membership creation |
| ARKSpace Operations | Operations staff | Space and booking management |
| ARKSpace Front Desk | Receptionist | Check-in/out, basic bookings |
| ARKSpace Member | Members/tenants | Self-service own records |
| ARKSpace Viewer | Observers | Read-only access |

### Assigning Roles

```
User > Roles & Permissions > Add Row > Select ARKSpace role
```

Or via command:
```bash
bench --site {site} execute frappe.client.add_to_roles --args '["user@example.com", "ARKSpace Manager"]'
```

### Setting Up Member Access

1. Create **Customer** in ERPNext
2. Create **Contact** linked to the Customer
3. Set **User** email on the Contact
4. Assign **ARKSpace Member** role to the User
5. Member can now access the portal and their own records

---

## Space Management

### Setting Up Spaces

1. **Create Space Types**: Settings → Space Type
   - Hot Desk, Dedicated Desk, Private Office, Meeting Room, Event Space, Virtual Office
2. **Create Amenities**: Settings → Amenity
   - WiFi, Printing, Coffee, Projector, etc.
3. **Create Branches**: ERPNext → Branch
4. **Create Spaces**: Spaces → Co-working Space
   - Assign type, branch, floor, capacity, pricing

### Space Status

| Status | Meaning | Changed By |
|--------|---------|------------|
| Available | Open for booking | System (on check-out/cancel) |
| Occupied | Currently in use | System (on check-in) |
| Reserved | Reserved but not checked in | Manual |
| Maintenance | Temporarily unavailable | Manual |

### Floor Plan

Access via: **ARKSpace > Floor Plan**

The floor plan shows all spaces with color-coded status. Admins can quick-book directly from the floor plan.

---

## Membership Management

### Creating Plans

1. Navigate to **Membership Plan**
2. Fill in: name, type, pricing, benefits (hours, credits, guests)
3. Check **Is Active** to make available

### Membership Lifecycle

```
Draft → (Submit) → Active → (Expiry) → Expired
                         ↘ (Cancel) → Cancelled
                         ↘ (Suspend) → Suspended
                         ↘ (Auto-Renew) → Active (new period)
```

### Auto-Renewal

Memberships with `Auto Renew = Yes` are automatically renewed daily when they reach their end date. The task:
1. Creates a new billing period
2. Updates start/end dates
3. Creates a new Sales Invoice (if ERPNext billing enabled)
4. Publishes `membership_renewed` real-time event

---

## Scheduled Tasks

### Viewing Task Status

```bash
bench --site {site} show-pending-jobs
bench --site {site} doctor
```

### Manual Task Execution

```bash
# Run specific task
bench --site {site} execute arkspace.tasks.check_membership_expiry
bench --site {site} execute arkspace.tasks.auto_renew_memberships
bench --site {site} execute arkspace.tasks.send_membership_expiry_reminders
bench --site {site} execute arkspace.tasks.generate_daily_occupancy_snapshot
bench --site {site} execute arkspace.tasks.mark_no_show_bookings
bench --site {site} execute arkspace.tasks.auto_checkout_expired_bookings
```

### Task Schedule

| Task | Schedule | Description |
|------|----------|-------------|
| Check Membership Expiry | Daily | Marks expired memberships |
| Auto-Renew Memberships | Daily | Renews eligible memberships |
| Send Expiry Reminders | Daily | Emails at 7d and 1d before |
| Daily Occupancy Snapshot | Daily | Records occupancy stats |
| Mark No-Show | Hourly | 2-hour grace period |
| Auto-Checkout Expired | Hourly | Frees spaces |
| Regenerate Documentation | 2 AM | Updates auto-docs |

---

## Backup & Maintenance

### Database Backup

```bash
bench --site {site} backup
# With files:
bench --site {site} backup --with-files
```

### Restore

```bash
bench --site {site} restore /path/to/backup.sql.gz
```

### Clear Caches

```bash
bench --site {site} clear-cache
bench --site {site} clear-website-cache
```

### Rebuild

```bash
bench build --app arkspace --force
bench --site {site} migrate
```

---

## Monitoring

### Error Logs

```bash
# View recent errors
bench --site {site} console
>>> frappe.get_all("Error Log", limit=10, fields=["name", "method", "error"], order_by="creation desc")
```

### Scheduler Health

```bash
bench --site {site} doctor
```

### Redis Status

```bash
redis-cli -h redis-cache ping
redis-cli -h redis-queue ping
```

### App Version

```python
>>> import arkspace
>>> arkspace.__version__
'6.0.0'
```

---

*See also: [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | [TECHNICAL_IMPLEMENTATION.md](TECHNICAL_IMPLEMENTATION.md)*
