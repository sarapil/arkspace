# ARKSpace DocTypes Reference

> **Version:** 6.0.0 | **Updated:** 2026-03-21  
> Total: 25 DocTypes (18 standalone + 7 child tables)

## Table of Contents

- [ARKSpace Core](#arkspace-core)
- [ARKSpace Spaces](#arkspace-spaces)
- [ARKSpace Memberships](#arkspace-memberships)
- [ARKSpace CRM](#arkspace-crm)
- [ARKSpace Contracts](#arkspace-contracts)
- [ARKSpace Training](#arkspace-training)
- [ARKSpace Design](#arkspace-design)
- [ARKSpace Documentation](#arkspace-documentation)
- [Relationships Diagram](#relationships-diagram)

---

## ARKSpace Core

### ARKSpace Settings

| Property | Value |
|----------|-------|
| Module | ARKSpace Core |
| Type | Single DocType |
| Submittable | No |

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `company` | Link → Company | ✅ | Linked ERPNext company |
| `default_currency` | Link → Currency | | Default currency |
| `primary_language` | Select | | Primary UI language |
| `secondary_language` | Select | | Secondary language |
| `timezone` | Select | | Timezone |
| `date_format` | Select | | Date display format |
| `booking_prefix` | Data | | Booking naming prefix (default: BK) |
| `membership_prefix` | Data | | Membership naming prefix (default: MEM) |
| `invoice_prefix` | Data | | Invoice prefix |
| `lead_prefix` | Data | | Lead naming prefix (default: WL) |
| `enable_voip` | Check | | Enable VoIP integration |
| `enable_arkamor` | Check | | Enable ARKAMOR IoT |
| `enable_arkanoor` | Check | | Enable ARKANOOR Marketplace |
| `enable_ai` | Check | | Enable AI features |
| `arkanoor_api_key` | Password | | ARKANOOR API key |
| `freepbx_host` | Data | | FreePBX host address |
| `freepbx_api_key` | Password | | FreePBX API key |
| `openai_api_key` | Password | | OpenAI API key |

---

## ARKSpace Spaces

### Space Type

| Property | Value |
|----------|-------|
| Module | ARKSpace Spaces |
| Autoname | `field:type_name` |
| Submittable | No |

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type_name` | Data | ✅ | English name |
| `type_name_ar` | Data | | Arabic name |
| `icon` | Data | | Icon identifier |
| `color` | Color | | Category color |
| `default_capacity` | Int | | Default capacity |
| `hourly_booking` | Check | | Allow hourly bookings |
| `daily_booking` | Check | | Allow daily bookings |
| `monthly_booking` | Check | | Allow monthly bookings |

### Amenity

| Property | Value |
|----------|-------|
| Module | ARKSpace Spaces |
| Autoname | `field:amenity_name` |
| Submittable | No |

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `amenity_name` | Data | ✅ | English name |
| `amenity_name_ar` | Data | | Arabic name |
| `icon` | Data | | Icon identifier |
| `color` | Color | | Display color |
| `hourly_price` | Currency | | Hourly add-on price |
| `daily_price` | Currency | | Daily add-on price |
| `monthly_price` | Currency | | Monthly add-on price |
| `is_complimentary` | Check | | Free with membership |

### Co-working Space

| Property | Value |
|----------|-------|
| Module | ARKSpace Spaces |
| Autoname | `field:space_name` |
| Submittable | No |

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `space_name` | Data | ✅ | English name |
| `space_name_ar` | Data | | Arabic name |
| `space_type` | Link → Space Type | ✅ | Category |
| `branch` | Link → Branch | ✅ | Location |
| `floor` | Data | | Floor number/name |
| `space_number` | Data | | Unit number |
| `capacity` | Int | ✅ | Max occupants |
| `area_sqm` | Float | | Area in square meters |
| `hourly_rate` | Currency | | Rate per hour |
| `daily_rate` | Currency | | Rate per day |
| `monthly_rate` | Currency | | Rate per month |
| `status` | Select | | Available / Occupied / Maintenance / Reserved |
| `current_member` | Link → Customer | | Currently assigned member |
| `amenities` | Table → Space Amenity | | Available amenities |
| `main_image` | Attach Image | | Primary photo |
| `gallery` | Table → Space Image | | Photo gallery |

**Controller:** `validate_capacity()`, `validate_pricing()`

### Space Booking

| Property | Value |
|----------|-------|
| Module | ARKSpace Spaces |
| Autoname | `naming_series:BK-.YYYY.-.#####` |
| Submittable | ✅ Yes |

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `space` | Link → Co-working Space | ✅ | Booked space |
| `member` | Link → Customer | ✅ | Booking customer |
| `booking_type` | Select | ✅ | Hourly / Daily / Monthly |
| `start_datetime` | Datetime | ✅ | Start time |
| `end_datetime` | Datetime | ✅ | End time |
| `duration_hours` | Float | | Calculated duration |
| `add_on_amenities` | Table → Space Amenity | | Extra amenities |
| `rate` | Currency | ✅ | Booking rate |
| `total_amount` | Currency | | Calculated total |
| `discount_percent` | Percent | | Discount |
| `net_amount` | Currency | | After discount |
| `status` | Select | | Pending / Confirmed / Checked In / Checked Out / Cancelled / No Show |
| `checked_in_at` | Datetime | | Check-in timestamp |
| `checked_out_at` | Datetime | | Check-out timestamp |
| `sales_invoice` | Link → Sales Invoice | | Generated invoice |

**Controller:** validate dates/pricing/overlap; on_submit → Confirmed; on_cancel → Cancelled, free space

### Space Amenity (Child Table)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `amenity` | Link → Amenity | ✅ | Selected amenity |
| `qty` | Int | | Quantity |
| `rate` | Currency | | Unit rate |
| `amount` | Currency | | Line total |
| `notes` | Small Text | | Notes |

### Space Image (Child Table)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `image` | Attach Image | ✅ | Image file |
| `caption` | Data | | Caption text |

---

## ARKSpace Memberships

### Membership Plan

| Property | Value |
|----------|-------|
| Module | ARKSpace Memberships |
| Autoname | `field:plan_name` |
| Submittable | No |

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `plan_name` | Data | ✅ | Plan name |
| `plan_name_ar` | Data | | Arabic name |
| `plan_type` | Select | ✅ | Hot Desk / Dedicated Desk / Private Office / Meeting Room / Event Space / Virtual Office |
| `space_type` | Link → Space Type | | Default space type |
| `is_active` | Check | | Active flag |
| `price` | Currency | ✅ | Base price |
| `setup_fee` | Currency | | One-time setup fee |
| `included_hours` | Int | | Monthly included hours |
| `included_credits` | Int | | Monthly credits |
| `max_guests` | Int | | Guest allowance |
| `meeting_room_hours` | Int | | Meeting room hours |
| `printing_pages` | Int | | Printing allowance |
| `storage_gb` | Float | | Storage allocation |
| `description` | Text Editor | | English description |
| `description_ar` | Text Editor | | Arabic description |

**Controller:** `validate_pricing()`

### Membership

| Property | Value |
|----------|-------|
| Module | ARKSpace Memberships |
| Autoname | `naming_series:MEM-.YYYY.-.#####` |
| Submittable | ✅ Yes |

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `member` | Link → Customer | ✅ | Member |
| `membership_plan` | Link → Membership Plan | ✅ | Selected plan |
| `billing_cycle` | Select | ✅ | Monthly / Quarterly / Yearly |
| `start_date` | Date | ✅ | Period start |
| `end_date` | Date | ✅ | Period end |
| `auto_renew` | Check | | Auto-renewal flag |
| `status` | Select | | Draft / Active / Expired / Cancelled / Suspended |
| `rate` | Currency | ✅ | Period rate |
| `assigned_space` | Link → Co-working Space | | Dedicated space |
| `credit_wallet` | Link → Member Credit Wallet | | Linked wallet |

**Controller:** validate dates/plan; on_submit → Active, create wallet, apply credits; on_cancel → Cancelled

### Member Credit Wallet

| Property | Value |
|----------|-------|
| Module | ARKSpace Memberships |
| Autoname | `field:member` |
| Submittable | No |

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `member` | Link → Customer | ✅ | Owner (unique) |
| `total_credits` | Float | | All-time credits |
| `used_credits` | Float | | Consumed credits |
| `available_credits` | Float | | Current balance |
| `transactions` | Table → Credit Transaction | | Transaction history |

### Credit Transaction (Child Table)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `transaction_type` | Select | ✅ | Credit / Debit / Expired / Refund |
| `credits` | Float | ✅ | Amount |
| `description` | Small Text | | Description |
| `reference_doctype` | Link → DocType | | Source type |
| `reference_name` | Dynamic Link | | Source document |
| `transaction_date` | Date | | Transaction date |

---

## ARKSpace CRM

### Workspace Lead

| Property | Value |
|----------|-------|
| Module | ARKSpace CRM |
| Autoname | `naming_series:WL-.YYYY.-.#####` |
| Submittable | No |

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `lead_name` | Data | ✅ | Contact name |
| `email` | Data | | Email address |
| `phone` | Data | | Phone number |
| `source` | Select | | Website / Walk-in / Referral / Social Media / Event / Partner / Other |
| `status` | Select | | New / Contacted / Tour Scheduled / Negotiating / Converted / Lost |
| `interested_plan` | Link → Membership Plan | | Interested plan |
| `interested_space_type` | Link → Space Type | | Preferred space type |
| `expected_start_date` | Date | | Expected start |
| `budget_monthly` | Currency | | Monthly budget |
| `team_size` | Int | | Team size |
| `next_follow_up` | Date | | Follow-up date |
| `converted_customer` | Link → Customer | | Converted customer |
| `converted_membership` | Link → Membership | | Resulting membership |

**Whitelisted:** `convert_to_customer()`, `schedule_tour()`

### Workspace Tour

| Property | Value |
|----------|-------|
| Module | ARKSpace CRM |
| Autoname | `naming_series:WT-.YYYY.-.#####` |
| Submittable | No |

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `lead` | Link → Workspace Lead | ✅ | Linked lead |
| `scheduled_date` | Date | ✅ | Tour date |
| `scheduled_time` | Time | ✅ | Tour time |
| `duration_minutes` | Int | | Duration |
| `status` | Select | | Scheduled / Completed / No Show / Rescheduled / Cancelled |
| `rating` | Rating | | 1–5 star rating |
| `outcome` | Select | | Interested / Need Follow Up / Not Interested / Converted |
| `follow_up_date` | Date | | Follow-up date |
| `converted_membership` | Link → Membership | | Converted membership |

**Whitelisted:** `complete_tour()`

---

## ARKSpace Contracts

### Contract Template

| Property | Value |
|----------|-------|
| Module | ARKSpace Contracts |
| Autoname | `field:template_name` |
| Submittable | No |

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `template_name` | Data | ✅ | Template name |
| `language` | Select | ✅ | Arabic / English / Bilingual |
| `contract_type` | Select | ✅ | Membership / Booking / Office Rental / Event Space / Virtual Office / Other |
| `is_active` | Check | | Active flag |
| `contract_terms_en` | Text Editor | | English Jinja terms |
| `contract_terms_ar` | Text Editor | | Arabic Jinja terms |
| `available_placeholders` | Small Text | | Placeholder reference |

### Legal Document

| Property | Value |
|----------|-------|
| Module | ARKSpace Contracts |
| Submittable | No |

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `member` | Link → Customer | ✅ | Document owner |
| `document_type` | Select | ✅ | National ID / Passport / Commercial Register / Tax Card / etc. (10 bilingual types) |
| `document_number` | Data | | ID number |
| `issue_date` | Date | | Issue date |
| `expiry_date` | Date | | Expiry date |
| `issuing_authority` | Data | | Issuing authority |
| `status` | Select | | Valid / Expired / Pending / Rejected |
| `document_file` | Attach | | Front image |
| `document_file_back` | Attach | | Back image |

### Member Contract

| Property | Value |
|----------|-------|
| Module | ARKSpace Contracts |
| Autoname | `naming_series:MC-.YYYY.-.#####` |
| Submittable | ✅ Yes |

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `contract_title` | Data | ✅ | Contract title |
| `contract_type` | Select | ✅ | Type of contract |
| `contract_template` | Link → Contract Template | | Template for terms |
| `status` | Select | | Draft / Active / Expired / Terminated / Cancelled |
| `member` | Link → Customer | ✅ | Contract party |
| `space` | Link → Co-working Space | | Linked space |
| `membership` | Link → Membership | | Linked membership |
| `start_date` | Date | ✅ | Contract start |
| `end_date` | Date | ✅ | Contract end |
| `contract_value` | Currency | ✅ | Total value |
| `legal_documents` | Table → Contract Legal Document | | Attached legal docs |
| `member_signature` | Signature | | Digital signature |
| `company_signatory` | Data | | Company signer |
| `witness_name` | Data | | Witness |

**Whitelisted:** `render_contract_terms()`

### Payment Receipt

| Property | Value |
|----------|-------|
| Module | ARKSpace Contracts |
| Autoname | `naming_series:PR-.YYYY.-.#####` |
| Submittable | ✅ Yes |

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `receipt_type` | Select | ✅ | 6 bilingual receipt types |
| `receipt_date` | Date | ✅ | Date of receipt |
| `member` | Link → Customer | ✅ | Paying member |
| `member_contract` | Link → Member Contract | | Linked contract |
| `membership` | Link → Membership | | Linked membership |
| `space_booking` | Link → Space Booking | | Linked booking |
| `amount` | Currency | ✅ | Payment amount |
| `payment_method` | Select | | Cash / Bank Transfer / Credit Card / Check / Online Payment / Wallet |
| `reference_number` | Data | | Payment reference |

### Contract Legal Document (Child Table)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `legal_document` | Link → Legal Document | ✅ | Linked document |
| `document_type` | Data | | Auto-populated type |
| `document_number` | Data | | Auto-populated number |
| `expiry_date` | Date | | Auto-populated expiry |
| `status` | Data | | Auto-populated status |

---

## ARKSpace Training

### Training Module

| Property | Value |
|----------|-------|
| Module | ARKSpace Training |
| Autoname | `field:module_name` |
| Submittable | No |

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `module_name` | Data | ✅ | Module title |
| `category` | Select | ✅ | Technical / Business / Creative / Wellness / Community / Onboarding |
| `level` | Select | | Beginner / Intermediate / Advanced |
| `status` | Select | | Draft / Published / Archived |
| `instructor` | Link → User | | Lead instructor |
| `syllabus` | Text Editor | | Course content |
| `image` | Attach Image | | Module image |
| `total_sessions` | Int | | Session count |
| `total_enrollments` | Int | | Enrollment count |

### Training Session

| Property | Value |
|----------|-------|
| Module | ARKSpace Training |
| Autoname | `naming_series:TS-.YYYY.-.#####` |
| Submittable | ✅ Yes |

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | Data | ✅ | Session title |
| `training_module` | Link → Training Module | ✅ | Parent module |
| `status` | Select | | Scheduled / In Progress / Completed / Cancelled |
| `session_date` | Date | ✅ | Date |
| `start_time` | Time | ✅ | Start time |
| `end_time` | Time | ✅ | End time |
| `venue` | Data | | Physical venue |
| `space` | Link → Co-working Space | | Linked space |
| `instructor` | Link → User | | Session instructor |
| `is_online` | Check | | Online session |
| `meeting_url` | Data | | Meeting link |
| `is_free` | Check | | Free session |
| `fee_amount` | Currency | | Fee if not free |

### Training Badge

| Property | Value |
|----------|-------|
| Module | ARKSpace Training |
| Autoname | `field:badge_name` |
| Submittable | No |

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `badge_name` | Data | ✅ | Badge name |
| `badge_code` | Data | | Unique code |
| `category` | Select | ✅ | Completion / Streak / Mastery / Community / Special |
| `level` | Select | | Bronze / Silver / Gold / Platinum |
| `points` | Int | | Point value |
| `criteria` | Small Text | | Earning criteria |
| `icon` | Data | | Icon |
| `image` | Attach Image | | Badge image |
| `is_active` | Check | | Active flag |

### User Training Progress

| Property | Value |
|----------|-------|
| Module | ARKSpace Training |
| Autoname | `naming_series:UTP-.YYYY.-.#####` |
| Submittable | No |

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `user` | Link → User | ✅ | Trainee |
| `member` | Link → Customer | | Linked customer |
| `training_module` | Link → Training Module | ✅ | Module |
| `training_session` | Link → Training Session | | Specific session |
| `status` | Select | | Enrolled / In Progress / Completed / Dropped |
| `completion_percentage` | Percent | | Progress |
| `enrolled_date` | Date | ✅ | Enrollment date |
| `completed_date` | Date | | Completion date |
| `badge_earned` | Link → Training Badge | | Awarded badge |
| `rating` | Rating | | User rating |

---

## ARKSpace Design

### Design Configuration

| Property | Value |
|----------|-------|
| Module | ARKSpace Design |
| Type | Single DocType |
| Submittable | No |

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `primary_color` | Color | | Primary color (#1B365D) |
| `secondary_color` | Color | | Secondary color |
| `accent_color` | Color | | Accent color (#C4A962) |
| `success_color` | Color | | Success color |
| `danger_color` | Color | | Danger color |
| `button_border_radius` | Data | | Border radius |
| `button_font_weight` | Data | | Font weight |
| `link_color` | Color | | Link color |
| `icon_library` | Select | | Font Awesome 6 / Material Icons / Custom |
| `enable_rtl` | Check | | RTL mode |
| `arabic_font` | Data | | Arabic font family |
| `english_font` | Data | | English font family |

---

## ARKSpace Documentation

### Documentation Entry

| Property | Value |
|----------|-------|
| Module | ARKSpace Documentation |
| Submittable | No |

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | Data | ✅ | English title |
| `title_ar` | Data | | Arabic title |
| `doc_type` | Select | ✅ | Module / DocType / API / Workflow / Tutorial / FAQ |
| `module_name` | Link → Module Def | | Related module |
| `related_doctype` | Link → DocType | | Related doctype |
| `summary` | Small Text | | English summary |
| `summary_ar` | Small Text | | Arabic summary |
| `content` | Markdown Editor | | English content |
| `content_ar` | Markdown Editor | | Arabic content |
| `code_examples` | Table → Documentation Code Example | | Code snippets |
| `related_docs` | Table → Documentation Relation | | Related entries |
| `prerequisites` | Table → Documentation Prerequisite | | Prerequisites |
| `auto_generated` | Check | | Auto-generated flag |

---

## Relationships Diagram

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│  Customer    │─────→│  Membership  │─────→│  Membership │
│             │      │              │      │  Plan       │
└─────┬───────┘      └──────────────┘      └─────────────┘
      │
      ├─────→ Space Booking ─────→ Co-working Space ─────→ Space Type
      │                                    │
      ├─────→ Member Contract              ├─→ Space Amenity[] → Amenity
      │           │                        └─→ Space Image[]
      ├─────→ Member Credit Wallet
      │           └─→ Credit Transaction[]
      ├─────→ Legal Document[]
      │
      └─────→ Payment Receipt

┌──────────────┐      ┌───────────────┐
│ Workspace    │─────→│ Workspace     │──── converts to ──→ Customer
│ Lead         │      │ Tour          │
└──────────────┘      └───────────────┘

┌──────────────┐      ┌───────────────┐      ┌──────────────┐
│ Training     │─────→│ Training      │      │ Training     │
│ Module       │      │ Session       │      │ Badge        │
└──────┬───────┘      └───────────────┘      └──────────────┘
       │                                            │
       └──────→ User Training Progress ─────────────┘
```

---

*See also: [API_REFERENCE.md](API_REFERENCE.md) | [FEATURES_EN.md](FEATURES_EN.md) | [TECHNICAL_IMPLEMENTATION.md](TECHNICAL_IMPLEMENTATION.md)*
