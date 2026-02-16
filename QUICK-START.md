# ⚡ Quick Start — ARKSpace v5.0

## Prerequisites

- Frappe Bench with Frappe v15 installed
- ERPNext v15 (optional but recommended)
- Python 3.10+
- MariaDB 10.6+
- Redis

## Installation

```bash
# Navigate to your bench directory
cd frappe-bench

# Install the app (from local path or Git URL)
bench get-app arkspace

# Install on your site
bench --site dev.localhost install-app arkspace

# Run migrations
bench --site dev.localhost migrate

# Build frontend assets
bench build --app arkspace

# Start development server
bench start
```

## First Steps After Install

1. **Configure Settings**
   - Navigate to: `ARKSpace Settings`
   - Set your company, currency, timezone
   - Enable/disable features (VoIP, IoT, AI, ARKANOOR)

2. **Create Space Types**
   - Go to `Space Type` list
   - Create types: Hot Desk, Private Office, Meeting Room, etc.

3. **Create Amenities**
   - Go to `Amenity` list
   - Add: WiFi, Parking, Coffee, Printer, etc.

4. **Add Your First Space**
   - Go to `Co-working Space` → New
   - Select branch, type, capacity, pricing

5. **Create Membership Plans**
   - Go to `Membership Plan` list
   - Define Monthly, Quarterly, Annual, Credits plans

## Roles

| Role | Access Level |
|------|-------------|
| ARKSpace Admin | Full access to all modules |
| ARKSpace Manager | Branch management, reports |
| ARKSpace Sales | CRM, leads, tours, quotations |
| ARKSpace Operations | Spaces, bookings, maintenance |
| ARKSpace Front Desk | Check-in/out, basic bookings |
| ARKSpace Member | Self-service portal |
| ARKSpace Viewer | Read-only access |

## Development

```bash
# Watch for changes
bench watch

# Clear cache
bench --site dev.localhost clear-cache

# Run tests
bench --site dev.localhost run-tests --app arkspace
```
