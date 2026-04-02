# ARKSpace Integrations

> **Version:** 6.0.0 | **Updated:** 2026-03-21  
> External system integrations and their configuration.

## Table of Contents

- [ERPNext Integration](#erpnext-integration)
- [Email Integration](#email-integration)
- [Real-time (Socket.IO)](#real-time-socketio)
- [Future Integrations](#future-integrations)

---

## ERPNext Integration

ARKSpace depends on ERPNext and leverages its core DocTypes for billing, customer management, and employee linking.

### Architecture

```
┌──────────────┐           ┌──────────────────┐
│   ARKSpace   │           │     ERPNext      │
│              │           │                  │
│ Space Booking│──submit──→│ Sales Invoice    │
│ Membership   │──submit──→│ Sales Invoice    │
│ (Customer)   │←──────────│ Customer         │
│ (Employee)   │←──linked──│ Employee         │
│              │           │ (Branch)         │
│              │           │ (Company)        │
└──────────────┘           └──────────────────┘
```

### Billing Bridge

**Module:** `arkspace.arkspace_integrations.billing`

#### Booking → Invoice

When a Space Booking is submitted:

```python
# Triggered via doc_events in hooks.py
def on_booking_submit(doc, method):
    """Create Sales Invoice from booking."""
    # Creates invoice with:
    # - Customer = booking.member
    # - Item = "Space Booking" service item
    # - Qty = duration
    # - Rate = booking.rate
    # - Linked back to booking.sales_invoice
```

When a Space Booking is cancelled:

```python
def on_booking_cancel(doc, method):
    """Cancel related Sales Invoice."""
    # Cancels the linked Sales Invoice
```

#### Membership → Invoice

When a Membership is submitted:

```python
def on_membership_submit(doc, method):
    """Create Sales Invoice from membership."""
    # Creates invoice with:
    # - Customer = membership.member
    # - Item = "Membership" service item
    # - Rate = membership.rate
```

#### Employee → Customer Linking

```python
def link_employee_to_customer(doc, method):
    """Auto-link Employee to Customer record."""
    # Triggered on Employee insert/update
    # Matches via email address
    # Enables member portal access for employees
```

### Configuration

1. Ensure **Company** is set in ARKSpace Settings
2. Create service items in ERPNext:
   - "Space Booking" (or custom name)
   - "Membership" (or custom name)
3. Set up a default income account

### Checking Integration Status

```python
# API endpoint
GET /api/method/arkspace.api.get_integration_status

# Response:
{
  "erpnext": true,
  "hrms": false,
  "payments": true
}
```

---

## Email Integration

ARKSpace uses Frappe's built-in email system for notifications.

### Notifications (4)

| Notification | Trigger | Recipients |
|-------------|---------|------------|
| Booking Confirmation | Booking submitted | Member |
| Membership Welcome | Membership activated | Member |
| Membership Expiry Reminder | 7d and 1d before expiry | Member |
| Booking Cancelled | Booking cancelled | Member |

### Configuration

1. Ensure email account is set up in Frappe
2. Notifications are auto-created during `bench migrate` via `setup.py`
3. Verify in **Notification** list that ARKSpace notifications are enabled

### Custom Email Templates

Notifications use Frappe's Jinja template system. You can customize:
- Subject line
- Email body (HTML)
- Recipient logic

---

## Real-time (Socket.IO)

ARKSpace publishes real-time events for live UI updates.

### Events

| Event | Source | Data | Used By |
|-------|--------|------|---------|
| `space_status_changed` | `check_in()`, `check_out()` | `{space, status, booking}` | Floor Plan page |
| `occupancy_snapshot` | Daily cron task | `{total, occupied, available, date}` | Dashboard |
| `membership_renewed` | Auto-renew task | `{membership, member, new_end_date}` | Member notifications |

### Server-side Publishing

```python
frappe.publish_realtime("space_status_changed", {
    "space": doc.space,
    "status": "Occupied",
    "booking": doc.name
}, user=frappe.session.user)
```

### Client-side Listening

```javascript
frappe.realtime.on("space_status_changed", function(data) {
    // Update floor plan UI
    update_space_status(data.space, data.status);
});
```

### Configuration

Socket.IO runs on port 9000 as part of `bench start`. No additional configuration needed.

---

## Future Integrations

### VoIP (FreePBX) — Planned

| Setting | Description |
|---------|-------------|
| `freepbx_host` | FreePBX server address |
| `freepbx_api_key` | API authentication |

**Planned features:**
- Click-to-call from lead/contact records
- Call logging
- VoIP extension management

### ARKANOOR Marketplace — Planned

| Setting | Description |
|---------|-------------|
| `arkanoor_api_key` | Marketplace API key |

**Planned features:**
- List available spaces on marketplace
- Accept external bookings
- Partner management

### ARKAMOR IoT — Planned

**Planned features:**
- Room occupancy sensors
- Temperature/humidity monitoring
- Automated lighting control
- Access control integration

### AI Features (OpenAI) — Planned

| Setting | Description |
|---------|-------------|
| `openai_api_key` | OpenAI API key |

**Planned features:**
- Smart space recommendations
- Predictive occupancy planning
- Automated lead scoring
- Content generation for contracts

---

## Integration Development Guide

### Adding a New Integration

1. Add configuration fields to `ARKSpace Settings` DocType
2. Create integration module in `arkspace/arkspace_integrations/`
3. Add doc_events in `hooks.py` if event-driven
4. Add scheduled tasks in `hooks.py` if poll-based
5. Update `get_integration_status()` API
6. Add translations for new fields
7. Update documentation

### Integration Pattern

```python
# arkspace/arkspace_integrations/my_integration.py

import frappe
from frappe import _


def is_enabled():
    """Check if integration is configured and enabled."""
    settings = frappe.get_single("ARKSpace Settings")
    return bool(settings.my_api_key)


def sync_data():
    """Synchronize data with external system."""
    if not is_enabled():
        return

    try:
        # Integration logic
        pass
    except Exception as e:
        frappe.log_error(f"My Integration Error: {e}")
        raise
```

---

*See also: [TECHNICAL_IMPLEMENTATION.md](TECHNICAL_IMPLEMENTATION.md) | [API_REFERENCE.md](API_REFERENCE.md) | [ADMIN_GUIDE.md](ADMIN_GUIDE.md)*
