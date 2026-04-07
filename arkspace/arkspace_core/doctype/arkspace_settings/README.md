# ARKSpace Settings

> Auto-generated documentation

## Overview

No description provided.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| company | Link | Company |
| default_currency | Link | Default Currency |
| fiscal_year_start | Select | Fiscal Year Start |
| primary_language | Link | Primary Language |
| secondary_language | Link | Secondary Language |
| timezone | Select | Timezone |
| date_format | Select | Date Format |
| booking_prefix | Data | Booking Prefix |
| membership_prefix | Data | Membership Prefix |
| invoice_prefix | Data | Invoice Prefix |
| lead_prefix | Data | Lead Prefix |
| enable_voip | Check | Enable VoIP |
| enable_arkamor | Check | Enable ARKAMOR IoT |
| enable_arkanoor | Check | Enable ARKANOOR Hub |
| enable_ai | Check | Enable AI Features |
| enable_online_payments | Check | Enable Online Payments / تفعيل الدفع الإلكتروني |
| default_payment_gateway | Select | Default Gateway / البوابة الافتراضية |
| payment_success_message | Small Text | Payment Success Message / رسالة نجاح الدفع |
| auto_reconcile_payments | Check | Auto-Reconcile Payments / مطابقة المدفوعات تلقائياً |
| payment_link_expiry_hours | Int | Payment Link Expiry (hours) / انتهاء رابط الدفع (ساعات) |
| stripe_publishable_key | Data | Stripe Publishable Key |
| stripe_secret_key | Password | Stripe Secret Key |
| stripe_webhook_secret | Password | Stripe Webhook Secret |
| tap_publishable_key | Data | Tap Publishable Key |
| tap_secret_key | Password | Tap Secret Key |
| tap_webhook_secret | Password | Tap Webhook Secret |
| enable_day_pass | Check | Enable Day Pass / تفعيل تصريح اليوم |
| default_day_pass_rate | Currency | Default Day Pass Rate / سعر التصريح الافتراضي |
| day_pass_auto_expire | Check | Auto-Expire Day Passes / انتهاء التصاريح تلقائياً |
| max_trial_days | Int | Max Trial Days / أقصى أيام التجربة |
| enable_analytics | Check | Enable Analytics / تفعيل التحليلات |
| analytics_retention_days | Int | Retention Days / أيام الاحتفاظ بالبيانات |
| auto_capture_snapshots | Check | Auto-Capture Snapshots / التقاط تلقائي للقطات |
| enable_multi_location | Check | Enable Multi-Location / تفعيل تعدد الفروع |
| default_branch | Link | Default Branch / الفرع الافتراضي |
| allow_cross_location_booking | Check | Allow Cross-Location Booking / السماح بالحجز بين الفروع |
| enable_community | Check | Enable Community / تفعيل المجتمع |
| allow_anonymous_posts | Check | Allow Anonymous Posts / السماح بالمنشورات المجهولة |
| enable_member_directory | Check | Enable Member Directory / تفعيل دليل الأعضاء |
| enable_events | Check | Enable Events / تفعيل الفعاليات |
| arkanoor_api_key | Password | ARKANOOR API Key |
| freepbx_host | Data | FreePBX Host |
| freepbx_api_key | Password | FreePBX API Key |
| openai_api_key | Password | OpenAI API Key |
| license_key | Password | License Key |
| license_status | Data | License Status |
| license_tier | Select | Current Tier |
| license_source | Data | License Source |


## Usage

```python
# Create
doc = frappe.new_doc("ARKSpace Settings")
doc.insert()

# Query
records = frappe.get_all("ARKSpace Settings")
```

## Related DocTypes

_Add related DocTypes here_

---
*Last updated: 2026-04-07 15:35:19.255960*
