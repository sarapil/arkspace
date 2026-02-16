# Workspace Lead

> Auto-generated documentation

## Overview

No description provided.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| lead_name | Data | Lead Name |
| email | Data | Email |
| phone | Data | Phone |
| company_name | Data | Company |
| source | Select | Source |
| status | Select | Status |
| interested_plan | Link | Interested Plan |
| interested_space_type | Link | Interested Space Type |
| expected_start_date | Date | Expected Start |
| budget_monthly | Currency | Monthly Budget |
| team_size | Int | Team Size |
| assigned_to | Link | Assigned To |
| branch | Link | Branch |
| next_follow_up | Date | Next Follow Up |
| notes | Text Editor | Notes |
| converted_customer | Link | Converted Customer |
| converted_membership | Link | Converted Membership |


## Usage

```python
# Create
doc = frappe.new_doc("Workspace Lead")
doc.insert()

# Query
records = frappe.get_all("Workspace Lead")
```

## Related DocTypes

_Add related DocTypes here_

---
*Last updated: 2026-02-09 20:26:55.060765*
