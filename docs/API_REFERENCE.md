# ARKSpace API Reference

> **Version:** 6.0.0 | **Updated:** 2026-03-21  
> Base URL: `/api/method/arkspace.api.<endpoint>` or `/api/method/arkspace.<module>.api.<endpoint>`

## Table of Contents

- [Health & Dashboard](#health--dashboard)
- [Spaces API](#spaces-api)
- [Memberships API](#memberships-api)
- [Training API](#training-api)
- [Integrations API](#integrations-api)
- [CRM Controller Methods](#crm-controller-methods)
- [Contract Controller Methods](#contract-controller-methods)
- [Real-time Events](#real-time-events)

---

## Health & Dashboard

### `ping`

Health-check endpoint.

```
GET /api/method/arkspace.api.ping
Auth: None (allow_guest=True)
```

**Response:**
```json
{"app": "arkspace", "version": "6.0.0", "status": "ok"}
```

### `get_dashboard_stats`

High-level KPIs for the ARKSpace dashboard.

```
GET /api/method/arkspace.api.get_dashboard_stats
Auth: Required
```

**Response:**
```json
{
  "total_spaces": 50,
  "occupied": 32,
  "available": 18,
  "bookings_today": 15,
  "active_members": 28
}
```

---

## Spaces API

Module: `arkspace.arkspace_spaces.api`

### `get_available_spaces`

Query available spaces for a given time range.

```
GET /api/method/arkspace.api.get_available_spaces
Auth: Required
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `space_type` | string | No | Filter by Space Type name |
| `branch` | string | No | Filter by Branch name |
| `booking_type` | string | No | `Hourly`, `Daily`, or `Monthly` |
| `start` | datetime | No | Start of availability window |
| `end` | datetime | No | End of availability window |

**Response:** List of available `Co-working Space` records.

### `create_booking`

Create and submit a space booking.

```
POST /api/method/arkspace.api.create_booking
Auth: Required
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `space` | string | Yes | Co-working Space name |
| `member` | string | Yes | Customer name |
| `booking_type` | string | Yes | `Hourly`, `Daily`, or `Monthly` |
| `start_datetime` | datetime | Yes | Booking start |
| `end_datetime` | datetime | Yes | Booking end |
| `amenities` | list | No | List of amenity names |

**Response:** Created `Space Booking` document.

### `check_in`

Check in to a confirmed booking. Publishes `space_status_changed` realtime event.

```
POST /api/method/arkspace.api.check_in
Auth: Required
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `booking` | string | Yes | Space Booking name |

**Validations:**
- Booking must be submitted (docstatus = 1)
- Status must be `Confirmed`

### `check_out`

Check out from a booking. Publishes `space_status_changed` realtime event.

```
POST /api/method/arkspace.api.check_out
Auth: Required
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `booking` | string | Yes | Space Booking name |

**Validations:**
- Booking must be submitted
- Status must be `Checked In`

---

## Memberships API

Module: `arkspace.arkspace_memberships.api`

### `get_membership_plans`

Retrieve available membership plans.

```
GET /api/method/arkspace.api.get_membership_plans
Auth: Required
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `plan_type` | string | No | Filter by plan type |
| `is_active` | bool | No | Filter active/inactive (default: active) |

### `create_membership`

Create and submit a new membership.

```
POST /api/method/arkspace.api.create_membership
Auth: Required
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `member` | string | Yes | Customer name |
| `plan` | string | Yes | Membership Plan name |
| `billing_cycle` | string | Yes | `Monthly`, `Quarterly`, or `Yearly` |
| `start_date` | date | Yes | Start date |
| `auto_renew` | bool | No | Enable auto-renewal |

### `get_active_memberships`

List active memberships, optionally filtered by member.

```
GET /api/method/arkspace.api.get_active_memberships
Auth: Required
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `member` | string | No | Customer name to filter |

### `get_wallet_balance`

Get credit wallet balance for a member.

```
GET /api/method/arkspace.api.get_wallet_balance
Auth: Required
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `member` | string | Yes | Customer name |

**Response:**
```json
{
  "total_credits": 100,
  "used_credits": 35,
  "available_credits": 65
}
```

### `get_member_dashboard`

Comprehensive member overview.

```
GET /api/method/arkspace.api.get_member_dashboard
Auth: Required
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `member` | string | Yes | Customer name |

**Response:** Object with `memberships`, `upcoming_bookings`, `recent_bookings`, `wallet`, and `stats`.

---

## Training API

Module: `arkspace.arkspace_training.api`

### `get_training_catalog`

Published training modules.

```
GET /api/method/arkspace.api.get_training_catalog
Auth: Required
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `category` | string | No | Technical/Business/Creative/Wellness/Community/Onboarding |
| `level` | string | No | Beginner/Intermediate/Advanced |

### `get_upcoming_sessions`

Upcoming scheduled training sessions.

```
GET /api/method/arkspace.api.get_upcoming_sessions
Auth: Required
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `training_module` | string | No | Filter by module |
| `branch` | string | No | Filter by branch |
| `limit` | int | No | Max results |

### `get_available_badges`

All active training badges.

```
GET /api/method/arkspace.api.get_available_badges
Auth: Required
```

### `get_user_badges`

Badges earned by a specific user.

```
GET /api/method/arkspace.api.get_user_badges
Auth: Required
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user` | string | Yes | User email |

### `enroll_user`

Enroll a user in a training module.

```
POST /api/method/arkspace.api.enroll_user
Auth: Required
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user` | string | Yes | User email |
| `training_module` | string | Yes | Training Module name |
| `training_session` | string | No | Specific session |

**Validations:** Checks session capacity before enrollment.

### `update_progress`

Update training progress and auto-award badges.

```
POST /api/method/arkspace.api.update_progress
Auth: Required
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `progress_name` | string | Yes | User Training Progress name |
| `status` | string | No | New status |
| `completion_percentage` | float | No | 0–100 |

### `get_user_progress`

All progress records for a user.

```
GET /api/method/arkspace.api.get_user_progress
Auth: Required
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user` | string | Yes | User email |

---

## Integrations API

Module: `arkspace.arkspace_integrations.api`

### `get_integration_status`

Reports which integration apps are installed.

```
GET /api/method/arkspace.api.get_integration_status
Auth: Required
```

**Response:**
```json
{
  "erpnext": true,
  "hrms": false,
  "payments": true
}
```

### `get_unpaid_invoices`

Outstanding invoices for a member.

```
GET /api/method/arkspace.api.get_unpaid_invoices
Auth: Required
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `member` | string | Yes | Customer name |

---

## CRM Controller Methods

These are whitelisted methods on DocType controllers, callable via `/api/method/frappe.client.call`.

### `Workspace Lead.convert_to_customer`

Creates a Customer from a lead and marks the lead as Converted.

```python
frappe.call({
    method: "convert_to_customer",
    doc: lead_doc
})
```

### `Workspace Lead.schedule_tour`

Creates a Workspace Tour linked to the lead.

```python
frappe.call({
    method: "schedule_tour",
    doc: lead_doc,
    args: {
        "scheduled_date": "2026-04-01",
        "scheduled_time": "10:00"
    }
})
```

### `Workspace Tour.complete_tour`

Marks tour as completed and propagates status to the lead.

```python
frappe.call({
    method: "complete_tour",
    doc: tour_doc,
    args: {
        "outcome": "Interested",
        "rating": 4
    }
})
```

---

## Contract Controller Methods

### `Member Contract.render_contract_terms`

Renders Jinja contract terms from the selected template with full context (member details, space, plan, dates, financials).

```python
frappe.call({
    method: "render_contract_terms",
    doc: contract_doc
})
```

---

## Real-time Events

ARKSpace publishes the following events via `frappe.publish_realtime()`:

| Event | Triggered By | Data |
|-------|-------------|------|
| `space_status_changed` | `check_in`, `check_out` | `{space, status, booking}` |
| `occupancy_snapshot` | `generate_daily_occupancy_snapshot` | `{total, occupied, available, date}` |
| `membership_renewed` | `auto_renew_memberships` | `{membership, member, new_end_date}` |

### Client-side Listening

```javascript
frappe.realtime.on("space_status_changed", function(data) {
    console.log(`Space ${data.space} is now ${data.status}`);
    // Refresh floor plan, list views, etc.
});
```

---

*See also: [FEATURES_EN.md](FEATURES_EN.md) | [DOCTYPES_REFERENCE.md](DOCTYPES_REFERENCE.md) | [TECHNICAL_IMPLEMENTATION.md](TECHNICAL_IMPLEMENTATION.md)*
