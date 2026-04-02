# ARKSpace Pages Reference

> **Version:** 6.0.0 | **Updated:** 2026-03-21

## Table of Contents

- [Desk Pages](#desk-pages)
- [Portal Pages](#portal-pages)
- [Report Pages](#report-pages)

---

## Desk Pages

### Floor Plan — مخطط الطابق

| Property | Value |
|----------|-------|
| Module | ARKSpace Spaces |
| Route | `/desk/arkspace/floor-plan` |
| Backend | `arkspace/arkspace_spaces/floor_plan.py` |
| Frontend | `arkspace/arkspace_spaces/page/floor_plan/` |

#### Features

- **Interactive Grid**: Visual representation of all Co-working Spaces with color-coded status:
  - 🟢 Green = Available
  - 🔴 Red = Occupied
  - 🟡 Yellow = Reserved
  - ⚫ Gray = Maintenance
- **Quick Book Modal**: Click any available space to open a booking dialog
- **Live Stats Bar**: Total spaces, available count, occupied count
- **Floor Filter**: Dropdown to filter by floor (All Floors by default)
- **Live Mode**: Auto-refreshes via Socket.IO `space_status_changed` events
- **Bilingual**: All labels translated, supports RTL layout

#### API Calls

```python
# Backend function
arkspace.arkspace_spaces.floor_plan.get_floor_plan_data(branch=None, floor=None)
```

#### Permissions

All ARKSpace roles can view the floor plan. Only Admin/Manager/Operations/Front Desk can quick-book.

---

### ARKSpace Workspace

| Property | Value |
|----------|-------|
| Module | ARKSpace Core |
| Route | `/desk/arkspace` |
| Type | Frappe v16 Workspace |

#### Layout

- **Shortcuts**: Quick access to frequently used DocTypes
  - New Booking
  - New Membership
  - Floor Plan
  - New Lead
- **Number Cards**: 
  - Total Spaces
  - Active Members
  - Today's Bookings
  - Monthly Revenue
- **Dashboard Charts**:
  - Monthly Bookings (Bar)
  - Revenue Trend (Line)
  - Membership Distribution (Pie)
  - Space Utilization (Bar)
  - Lead Pipeline (Funnel)
- **Quick Lists**: Recent bookings, active memberships

---

## Portal Pages

### Member Portal — بوابة الأعضاء

| Property | Value |
|----------|-------|
| Route | `/member-portal` |
| Backend | `arkspace/www/member-portal.py` |
| Frontend | `arkspace/www/member-portal.html` |
| CSS | `arkspace/public/css/arkspace_portal.css` |
| JS | `arkspace/public/js/arkspace_portal.js` |

#### Features

- **Dashboard**: Welcome message, key stats (active memberships, total bookings, total spent)
- **Active Memberships**: Cards showing current memberships with plan, dates, status
- **Upcoming Bookings**: List of future bookings with check-in/cancel actions
- **Recent Bookings**: History of past bookings
- **Book a Space**: Browse available spaces and create bookings
- **No Membership State**: Friendly message with contact instructions

#### Authentication

Requires login. Uses `frappe.session.user` to identify the member via Contact → Customer link.

#### Bilingual Support

All portal strings are in `translations/ar.csv`. The portal detects the user's language preference.

```python
# Portal access check
@frappe.whitelist()
def get_portal_context():
    if frappe.session.user == "Guest":
        frappe.throw(_("Please login to access the member portal"))
    # ... resolve customer from user
```

---

### Member Portal — Book a Space

| Property | Value |
|----------|-------|
| Route | `/member-portal/book` |
| Parent | Member Portal |

#### Features

- Space type filter
- Date/time picker
- Available spaces grid
- Booking confirmation dialog
- Success/failure messages (bilingual)

---

## Report Pages

### Revenue Summary — ملخص الإيرادات

| Property | Value |
|----------|-------|
| Module | ARKSpace Core |
| Type | Script Report |
| Route | `/desk/query-report/Revenue Summary` |

#### Columns

| Column | Type | Description |
|--------|------|-------------|
| Month | Data | Reporting month |
| Booking Revenue | Currency | Revenue from bookings |
| Membership Revenue | Currency | Revenue from memberships |
| Total Revenue | Currency | Combined total |
| Growth % | Percent | Month-over-month growth |

---

### Space Occupancy — إشغال المساحات

| Property | Value |
|----------|-------|
| Module | ARKSpace Core |
| Type | Script Report |
| Route | `/desk/query-report/Space Occupancy` |

#### Columns

| Column | Type | Description |
|--------|------|-------------|
| Space | Link | Co-working Space |
| Space Type | Data | Category |
| Branch | Data | Location |
| Total Hours | Float | Hours booked |
| Occupancy % | Percent | Utilization rate |
| Revenue | Currency | Generated revenue |

---

### Membership Analytics — تحليلات العضوية

| Property | Value |
|----------|-------|
| Module | ARKSpace Core |
| Type | Script Report |
| Route | `/desk/query-report/Membership Analytics` |

#### Columns

| Column | Type | Description |
|--------|------|-------------|
| Plan | Link | Membership Plan |
| Active | Int | Active memberships |
| Expired | Int | Expired this period |
| New | Int | New this period |
| Revenue | Currency | Plan revenue |
| Retention % | Percent | Renewal rate |

---

## Setup Wizard Pages

### Stage 1: Welcome — مرحباً

Configure basic settings: workspace name, currency, timezone.

### Stage 2: Branches — الفروع

Add up to 3 branch locations.

### Stage 3: Space Types — أنواع المساحات

Select which space types to offer (6 checkboxes).

### Stage 4: First Plan — خطة العضوية الأولى

Create the first membership plan with name, type, and price.

---

*See also: [FEATURES_EN.md](FEATURES_EN.md) | [USER_GUIDE.md](USER_GUIDE.md)*
