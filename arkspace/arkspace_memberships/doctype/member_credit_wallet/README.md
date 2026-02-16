# Member Credit Wallet

> Auto-generated documentation

## Overview

No description provided.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| member | Link | Member |
| member_name | Data | Member Name |
| total_credits | Float | Total Credits |
| used_credits | Float | Used Credits |
| available_credits | Float | Available Credits |
| transactions | Table | Transactions |


## Usage

```python
# Create
doc = frappe.new_doc("Member Credit Wallet")
doc.insert()

# Query
records = frappe.get_all("Member Credit Wallet")
```

## Related DocTypes

_Add related DocTypes here_

---
*Last updated: 2026-02-09 20:26:53.574133*
