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
| arkanoor_api_key | Password | ARKANOOR API Key |
| freepbx_host | Data | FreePBX Host |
| freepbx_api_key | Password | FreePBX API Key |
| openai_api_key | Password | OpenAI API Key |


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
*Last updated: 2026-02-09 20:26:49.544269*
