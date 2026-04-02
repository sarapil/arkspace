# ARKSpace User Guide

> **Version:** 6.0.0 | **Language:** English  
> For co-working space members, front desk staff, and sales teams.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Booking a Space](#booking-a-space)
3. [Check-in & Check-out](#check-in--check-out)
4. [Memberships](#memberships)
5. [Member Portal](#member-portal)
6. [CRM & Sales](#crm--sales)
7. [Contracts](#contracts)
8. [Training](#training)
9. [Tips & Shortcuts](#tips--shortcuts)

---

## Getting Started

### First Login

1. Open your browser and navigate to your ARKSpace URL
2. Log in with your email and password
3. You'll see the **ARKSpace Workspace** with dashboard cards

### Navigation

| Area | URL | Purpose |
|------|-----|---------|
| Desk | `/desk/arkspace` | Main application interface |
| Floor Plan | `/desk/arkspace/floor-plan` | Visual space overview |
| ARK Live | `/desk/arkspace/ark-live` | Real-time space monitor |
| Member Portal | `/member-portal` | Self-service for members |

---

## Booking a Space

### From the Desk

1. Navigate to **Spaces > Space Booking > + New**
2. Select the **Space** (search by name or type)
3. Select the **Member** (Customer)
4. Choose **Booking Type**: Hourly, Daily, or Monthly
5. Set **Start** and **End** date/time
6. Add any **Add-on Amenities** if needed
7. Click **Save** then **Submit**
8. Status changes to **Confirmed** ✅

### From the Floor Plan

1. Navigate to **ARKSpace > Floor Plan**
2. Green spaces are available — click one
3. Fill in the Quick Book dialog
4. Click **Book** — done!

### Booking Statuses

```
Pending → Confirmed → Checked In → Checked Out
                   ↘ Cancelled
                   ↘ No Show
```

---

## Check-in & Check-out

### Individual Check-in

1. Open the Space Booking
2. Click the **Check In** button (appears for Confirmed bookings)
3. The space status changes to **Occupied**
4. The Floor Plan and ARK Live update in real-time

### Individual Check-out

1. Open the Space Booking
2. Click the **Check Out** button
3. The space returns to **Available**

### Bulk Operations (Front Desk / Operations)

1. Go to **Spaces > Space Booking** list view
2. Select multiple bookings using checkboxes
3. Use the **Actions** menu:
   - **Bulk Check In** — Check in all selected
   - **Bulk Check Out** — Check out all selected
   - **Bulk Cancel** — Cancel all selected
   - **Bulk No Show** — Mark all as No Show

### Automatic Actions

- **No-show detection**: Bookings not checked in within 2 hours are auto-marked (hourly task)
- **Auto check-out**: Overdue bookings are auto-checked out (hourly task)

---

## Memberships

### Viewing Plans

Navigate to **Memberships > Membership Plan** to see available plans.

Each plan includes:
- Plan type (Hot Desk, Dedicated Desk, Private Office, etc.)
- Monthly/Quarterly/Yearly pricing
- Included benefits (hours, credits, guests, meeting rooms, printing, storage)

### Creating a Membership

1. Navigate to **Memberships > Membership > + New**
2. Select **Member** (Customer)
3. Select **Membership Plan**
4. Choose **Billing Cycle** (Monthly/Quarterly/Yearly)
5. Set **Start Date**
6. Toggle **Auto Renew** if desired
7. **Save** and **Submit**
8. A **Credit Wallet** is automatically created

### Credit Wallet

Each member has a credit wallet:

| Field | Description |
|-------|-------------|
| Total Credits | All-time credits received |
| Used Credits | Credits consumed |
| Available Credits | Current balance |

Credits are added on membership activation and deducted on usage.

### Automatic Processes

- **Expiry check**: Daily task marks expired memberships
- **Auto-renewal**: Daily task renews eligible memberships
- **Reminders**: Email notifications at 7 days and 1 day before expiry

---

## Member Portal

### Accessing the Portal

Navigate to `/member-portal` after logging in.

### Dashboard Sections

| Section | What You See |
|---------|-------------|
| Active Memberships | Current membership cards |
| Upcoming Bookings | Future reservations |
| Recent Bookings | Booking history |
| Stats | Total bookings, total spent |

### Self-Service Actions

- **Book a Space** — Select type, dates, and confirm
- **View Bookings** — See upcoming and past bookings
- **Cancel a Booking** — Cancel from upcoming bookings list
- **View Membership** — Check plan details and credit balance

---

## CRM & Sales

### Lead Management

#### Creating a Lead

1. Navigate to **CRM > Workspace Lead > + New**
2. Fill in: Name, Email, Phone
3. Select **Source**: Website, Walk-in, Referral, Social Media, Event, Partner
4. Optionally set interested plan, budget, team size
5. **Save**

#### Lead Pipeline

```
New → Contacted → Tour Scheduled → Negotiating → Converted
                                                ↘ Lost
```

#### Scheduling a Tour

1. Open the lead record
2. Click **Schedule Tour**
3. Set date, time, and duration
4. A Workspace Tour is created automatically
5. Lead status changes to **Tour Scheduled**

#### Converting to Customer

1. Open the lead (must be in a convertible status)
2. Click **Convert to Customer**
3. A Customer record is created in ERPNext
4. Lead status changes to **Converted**
5. Create a Membership for the new customer

---

## Contracts

### Creating a Contract

1. Navigate to **Contracts > Member Contract > + New**
2. Fill in: Member, Contract Type, Template, Dates, Value
3. Click **Render Terms** to populate from template
4. Attach Legal Documents (ID, passport, etc.)
5. Collect Member Signature
6. **Save** and **Submit**

### Legal Documents

Supported types: National ID, Passport, Commercial Register, Tax Card, and more.

1. Navigate to **Contracts > Legal Document > + New**
2. Upload front/back images, set issue/expiry dates
3. Status: Valid / Expired / Pending / Rejected

### Payment Receipts

1. Navigate to **Contracts > Payment Receipt > + New**
2. Link to contract/membership/booking
3. Set amount and payment method (Cash, Bank Transfer, Credit Card, etc.)
4. **Submit** to finalize

---

## Training

### Browsing the Catalog

1. Navigate to **Training > Training Module**
2. Filter by category (Technical, Business, Creative, Wellness, Community, Onboarding)
3. Filter by level (Beginner, Intermediate, Advanced)

### Enrolling in a Session

1. Find an upcoming **Training Session**
2. Click **Enroll**
3. Progress tracked in **User Training Progress**

### Earning Badges

Badges are awarded automatically:

| Level | Achievement |
|-------|-------------|
| 🥉 Bronze | Basic completion |
| 🥈 Silver | Intermediate achievement |
| 🥇 Gold | Advanced mastery |
| 💎 Platinum | Exceptional performance |

---

## Tips & Shortcuts

| Action | How |
|--------|-----|
| New Booking | Spaces > Space Booking > + New |
| Global Search | `Ctrl+K` |
| Floor Plan | ARKSpace sidebar > Floor Plan |
| Language Switch | User Settings > Language |
| Quick Book | Click available space on Floor Plan |

---

*See also: [Admin Guide](ADMIN_GUIDE.md) | [Features](FEATURES.md) | [Arabic version](../ar/USER_GUIDE.md)*
