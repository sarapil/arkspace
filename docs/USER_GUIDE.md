# ARKSpace User Guide — دليل المستخدم

> **Version:** 6.0.0 | **Updated:** 2026-03-21  
> For co-working space members, front desk staff, and sales teams.

## Table of Contents

- [Getting Started](#getting-started)
- [Booking a Space](#booking-a-space)
- [Check-in & Check-out](#check-in--check-out)
- [Memberships](#memberships)
- [Member Portal](#member-portal)
- [CRM & Sales](#crm--sales)
- [Contracts](#contracts)
- [Training](#training)

---

## Getting Started

### First Login

1. Open your browser and navigate to your ARKSpace URL
2. Log in with your email and password
3. You'll see the **ARKSpace Workspace** with dashboard cards

### Navigation

- **Desk**: The main application interface at `/desk/arkspace`
- **Floor Plan**: Visual space overview at `/desk/arkspace/floor-plan`
- **Member Portal**: Self-service portal at `/member-portal` (for members)

---

## Booking a Space

### From the Desk

1. Navigate to **Spaces > Space Booking > + New**
2. Select the **Space** (you can search by name or type)
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

### Viewing Bookings

- **All Bookings**: Spaces > Space Booking
- **Today's Bookings**: Filter by today's date
- **My Bookings**: Filtered automatically for Members

---

## Check-in & Check-out

### Individual Check-in

1. Open the Space Booking
2. Click the **Check In** button (appears for Confirmed bookings)
3. The space status changes to **Occupied**
4. The Floor Plan updates in real-time

### Individual Check-out

1. Open the Space Booking
2. Click the **Check Out** button
3. The space returns to **Available**

### Bulk Operations (Front Desk / Operations)

1. Go to **Spaces > Space Booking** list view
2. Select multiple bookings using checkboxes
3. Use the **Actions** menu:
   - **Bulk Check In**: Check in all selected
   - **Bulk Check Out**: Check out all selected
   - **Bulk Cancel**: Cancel all selected
   - **Bulk No Show**: Mark all as No Show

---

## Memberships

### Viewing Plans

Navigate to **Memberships > Membership Plan** to see available plans.

Each plan shows:
- Plan type (Hot Desk, Private Office, etc.)
- Monthly/Quarterly/Yearly pricing
- Included benefits (hours, credits, guests, meeting rooms)

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

Each member has a credit wallet that tracks:
- **Total Credits**: All-time credits received
- **Used Credits**: Credits consumed
- **Available Credits**: Current balance

Credits are added when a membership is activated and deducted when used for bookings.

---

## Member Portal

### Accessing the Portal

Navigate to `/member-portal` after logging in.

### Portal Dashboard

| Section | Description |
|---------|-------------|
| **Active Memberships** | Your current membership cards |
| **Upcoming Bookings** | Future reservations |
| **Recent Bookings** | Booking history |
| **Stats** | Total bookings, total spent |

### Booking from Portal

1. Click **Book a Space** / **حجز مساحة**
2. Select space type and dates
3. Choose an available space
4. Confirm booking
5. See confirmation message

### Cancelling a Booking

1. Find the booking in **Upcoming Bookings**
2. Click **Cancel** / **إلغاء**
3. Confirm the cancellation

---

## CRM & Sales

### Managing Leads (Sales Team)

#### Creating a Lead

1. Navigate to **CRM > Workspace Lead > + New**
2. Fill in: Name, Email, Phone
3. Select **Source**: Website, Walk-in, Referral, Social Media, Event, Partner
4. Set initial **Status**: New
5. Optionally set interested plan, budget, team size
6. **Save**

#### Lead Pipeline

```
New → Contacted → Tour Scheduled → Negotiating → Converted → Lost
```

Update the status as you progress through the pipeline.

#### Scheduling a Tour

1. Open the lead
2. Click **Schedule Tour** / **جدولة جولة**
3. Set date, time, and duration
4. A Workspace Tour is created
5. Lead status automatically changes to **Tour Scheduled**

#### Completing a Tour

1. Open the Workspace Tour
2. Click **Complete Tour** / **إتمام الجولة**
3. Set rating (1–5 stars)
4. Set outcome: Interested / Need Follow Up / Not Interested / Converted
5. Status propagates back to the lead

#### Converting to Customer

1. Open the lead (must be in a convertible status)
2. Click **Convert to Customer** / **تحويل لعميل**
3. A Customer record is created
4. Lead status changes to **Converted**
5. You can now create a Membership for the customer

---

## Contracts

### Creating a Contract

1. Navigate to **Contracts > Member Contract > + New**
2. Fill in:
   - **Member** (Customer)
   - **Contract Type** (Membership, Booking, Office Rental, etc.)
   - **Contract Template** (optional — auto-fills terms)
   - **Start/End dates**
   - **Contract Value**
3. Attach **Legal Documents** (ID, passport, etc.)
4. Click **Render Terms** to populate Jinja template
5. Get **Member Signature** (digital)
6. **Save** and **Submit**

### Legal Documents

1. Navigate to **Contracts > Legal Document > + New**
2. Select member and document type (National ID, Passport, etc.)
3. Upload front and back images
4. Set issue/expiry dates
5. Status: Valid / Expired / Pending / Rejected

### Payment Receipts

1. Navigate to **Contracts > Payment Receipt > + New**
2. Select receipt type, date, member
3. Link to contract/membership/booking
4. Set amount and payment method
5. **Submit** to finalize

---

## Training

### Browsing Training

1. Navigate to **Training > Training Module** for the catalog
2. Filter by category (Technical, Business, Creative, etc.) and level
3. View module details: syllabus, prerequisites, instructor

### Enrolling in Training

1. Find an upcoming **Training Session**
2. Click **Enroll** / **التسجيل**
3. Your progress is tracked in **User Training Progress**

### Tracking Progress

1. Navigate to **Training > User Training Progress**
2. See your enrolled modules with status and completion %
3. Status: Enrolled → In Progress → Completed

### Earning Badges

Badges are awarded automatically when you complete training:

| Level | Achievement |
|-------|-------------|
| 🥉 Bronze | Basic completion |
| 🥈 Silver | Intermediate achievement |
| 🥇 Gold | Advanced mastery |
| 💎 Platinum | Exceptional performance |

Badge categories: Completion, Streak, Mastery, Community, Special

---

## Tips & Shortcuts

| Action | Shortcut |
|--------|----------|
| New Booking | `Ctrl+Shift+B` from ARKSpace workspace |
| Search | `Ctrl+K` for global search |
| Floor Plan | Click ARKSpace > Floor Plan |
| Language Switch | User Settings > Language |

---

*See also: [ADMIN_GUIDE.md](ADMIN_GUIDE.md) | [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | [FEATURES_AR.md](FEATURES_AR.md)*
