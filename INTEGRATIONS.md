# 🔗 ARKSpace — Integrations Guide

> **Domain:** Coworking Space Management
> **Prefix:** ARK

---

## Integration Map

```
ARKSpace
  ├── ERPNext
  ├── HRMS
  ├── CAPS
  ├── frappe_visual
  ├── Payment Gateways
```

---

## ERPNext

### Connection Type
- **Direction:** Bidirectional
- **Protocol:** Python API / REST
- **Authentication:** Frappe session / API key

### Data Flow
| Source | Target | Trigger | Data |
|--------|--------|---------|------|
| ARKSpace | ERPNext | On submit | Document data |
| ERPNext | ARKSpace | On change | Updated data |

### Configuration
```python
# In ARK Settings or site_config.json
# erpnext_enabled = 1
```

---

## HRMS

### Connection Type
- **Direction:** Bidirectional
- **Protocol:** Python API / REST
- **Authentication:** Frappe session / API key

### Data Flow
| Source | Target | Trigger | Data |
|--------|--------|---------|------|
| ARKSpace | HRMS | On submit | Document data |
| HRMS | ARKSpace | On change | Updated data |

### Configuration
```python
# In ARK Settings or site_config.json
# hrms_enabled = 1
```

---

## CAPS

### Connection Type
- **Direction:** Bidirectional
- **Protocol:** Python API / REST
- **Authentication:** Frappe session / API key

### Data Flow
| Source | Target | Trigger | Data |
|--------|--------|---------|------|
| ARKSpace | CAPS | On submit | Document data |
| CAPS | ARKSpace | On change | Updated data |

### Configuration
```python
# In ARK Settings or site_config.json
# caps_enabled = 1
```

---

## frappe_visual

### Connection Type
- **Direction:** Bidirectional
- **Protocol:** Python API / REST
- **Authentication:** Frappe session / API key

### Data Flow
| Source | Target | Trigger | Data |
|--------|--------|---------|------|
| ARKSpace | frappe_visual | On submit | Document data |
| frappe_visual | ARKSpace | On change | Updated data |

### Configuration
```python
# In ARK Settings or site_config.json
# frappe_visual_enabled = 1
```

---

## Payment Gateways

### Connection Type
- **Direction:** Bidirectional
- **Protocol:** Python API / REST
- **Authentication:** Frappe session / API key

### Data Flow
| Source | Target | Trigger | Data |
|--------|--------|---------|------|
| ARKSpace | Payment Gateways | On submit | Document data |
| Payment Gateways | ARKSpace | On change | Updated data |

### Configuration
```python
# In ARK Settings or site_config.json
# payment_gateways_enabled = 1
```

---

## API Endpoints

All integration APIs use the standard response format from `arkspace.api.response`:

```python
from arkspace.api.response import success, error

@frappe.whitelist()
def sync_data():
    return success(data={}, message="Sync completed")
```

---

*Part of ARKSpace by Arkan Lab*
