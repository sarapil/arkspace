# ARKSpace — Security Documentation

> **Version:** 6.0.0 | **Updated:** 2026-03-21

---

## Table of Contents

1. [Security Architecture](#security-architecture)
2. [Authentication & Authorization](#authentication--authorization)
3. [Role-Based Access Control](#role-based-access-control)
4. [Row-Level Security](#row-level-security)
5. [API Security](#api-security)
6. [Data Protection](#data-protection)
7. [Input Validation](#input-validation)
8. [Dependency Security](#dependency-security)
9. [Deployment Security](#deployment-security)
10. [Vulnerability Reporting](#vulnerability-reporting)

---

## Security Architecture

ARKSpace inherits the robust security foundation of the Frappe Framework and adds application-specific security layers:

```
┌─────────────────────────────────────────────┐
│              Frappe Framework                │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐ │
│  │  CSRF     │  │  Session  │  │  Password  │ │
│  │  Token    │  │  Mgmt     │  │  Hashing   │ │
│  └──────────┘  └──────────┘  └───────────┘ │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐ │
│  │  Rate     │  │  Input    │  │  SQL       │ │
│  │  Limiting │  │  Sanitize │  │  Injection │ │
│  └──────────┘  └──────────┘  └───────────┘ │
├─────────────────────────────────────────────┤
│              ARKSpace Layer                  │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐ │
│  │  7 Custom │  │  Row-Level│  │  Permission│ │
│  │  Roles    │  │  Security │  │  Queries   │ │
│  └──────────┘  └──────────┘  └───────────┘ │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐ │
│  │  Workflow  │  │  Audit    │  │  @whitelist│ │
│  │  Guards    │  │  Trail    │  │  Auth      │ │
│  └──────────┘  └──────────┘  └───────────┘ │
└─────────────────────────────────────────────┘
```

---

## Authentication & Authorization

### Authentication (Frappe Core)

ARKSpace relies on Frappe's built-in authentication:

- **Session-based auth** with secure HTTP-only cookies
- **API key/secret** for programmatic access
- **OAuth 2.0** for third-party integrations
- **Two-Factor Authentication (2FA)** support
- **Password policy** enforcement (min length, complexity)
- **Login attempt throttling** (configurable lockout)

### Authorization (ARKSpace Layer)

All 36 API endpoints use `@frappe.whitelist()` which:

1. Requires authenticated session (no anonymous access)
2. Validates CSRF token on non-GET requests
3. Enforces DocType-level permissions before data access

```python
# Every API endpoint pattern
@frappe.whitelist()
def sensitive_action(param):
    # Permission check
    frappe.has_permission("DocType", "write", throw=True)
    # or role check
    frappe.only_for(["ARKSpace Admin", "ARKSpace Manager"])
```

---

## Role-Based Access Control

### Custom Roles

ARKSpace defines 7 roles with specific permission matrices:

| Role | Scope | Access Level |
|------|-------|-------------|
| **ARKSpace Admin** | Full system | Create, Read, Update, Delete, Submit, Cancel, Amend |
| **ARKSpace Manager** | Operations | Create, Read, Update, Submit |
| **ARKSpace Sales** | CRM pipeline | Create, Read on Leads/Tours; Read on Spaces |
| **ARKSpace Operations** | Day-to-day | Create, Read, Update on Bookings/Spaces |
| **ARKSpace Front Desk** | Check-in/out | Read, Update on Bookings; Read on Spaces |
| **ARKSpace Member** | Self-service | Read own records only |
| **ARKSpace Viewer** | Read-only | Read all non-sensitive records |

### Permission Matrix (Key DocTypes)

| DocType | Admin | Manager | Sales | Operations | Front Desk | Member |
|---------|-------|---------|-------|------------|------------|--------|
| Space Booking | CRUDS | CRUS | R | CRU | RU | R* |
| Membership | CRUDS | CRUS | R | R | R | R* |
| Workspace Lead | CRUD | CRUD | CRUD | R | — | — |
| Member Contract | CRUDS | CRU | R | R | — | R* |
| Credit Wallet | CRUD | CR | R | R | R | R* |

*R\* = Own records only (row-level security)*

---

## Row-Level Security

ARKSpace implements row-level security for member-facing DocTypes via `permissions.py`:

### Protected DocTypes

```python
# hooks.py
has_permission = {
    "Space Booking": "arkspace.permissions.has_booking_permission",
    "Membership": "arkspace.permissions.has_membership_permission",
    "Member Credit Wallet": "arkspace.permissions.has_wallet_permission",
}

permission_query_conditions = {
    "Space Booking": "arkspace.permissions.booking_query_conditions",
    "Membership": "arkspace.permissions.membership_query_conditions",
    "Member Credit Wallet": "arkspace.permissions.wallet_query_conditions",
}
```

### How It Works

1. **Permission check** (`has_*_permission`): Called on every document access. Members can only access their own records; staff can access records based on their role.

2. **Query conditions** (`*_query_conditions`): Injected into every `frappe.get_list()` and `frappe.get_all()` call to filter results at the database level. Members only see their own data in list views.

```python
# Example: arkspace/permissions.py
def booking_query_conditions(user):
    if "ARKSpace Admin" in frappe.get_roles(user):
        return ""  # No restriction
    if "ARKSpace Member" in frappe.get_roles(user):
        customer = get_customer_for_user(user)
        return f"`tabSpace Booking`.customer = '{customer}'"
    return ""
```

---

## API Security

### Endpoint Protection

All API endpoints follow this security pattern:

```python
@frappe.whitelist()  # Requires authentication + CSRF
def api_function(param):
    # 1. Role/permission check
    frappe.has_permission("DocType", ptype, throw=True)

    # 2. Input validation
    frappe.validate_value(param, "field", valid_values)

    # 3. Business logic with safe ORM
    result = frappe.get_doc("DocType", name)  # ORM prevents SQL injection

    # 4. Return sanitized data
    return result.as_dict()
```

### No Guest Access

ARKSpace does not expose any `allow_guest=True` endpoints. All API access requires authentication.

### Portal Security

The member portal (`/arkspace_portal/`) uses Frappe's web request authentication and applies the same row-level security to ensure members only see their own data.

---

## Data Protection

### Sensitive Data Handling

| Data Type | Storage | Protection |
|-----------|---------|------------|
| Member personal info | DocType fields | Role-based access |
| Legal documents (ID, passport) | File attachments | Frappe file permissions |
| Contract content | Text fields | Submission lock (immutable after submit) |
| Payment records | Submittable DocType | Cannot edit after submit |
| Credit transactions | Wallet entries | Audit trail, no deletion |
| API credentials | Settings DocType | Admin-only access |

### Audit Trail

- All DocType changes are tracked in Frappe's version history
- Submittable DocTypes (Space Booking, Membership, Contract, Payment Receipt, Training Session) become immutable after submission
- Credit Wallet transactions maintain a complete ledger with no deletion

### Data Retention

- All data follows Frappe's standard retention policies
- Legal documents support expiry tracking for compliance
- Deleted records follow Frappe's soft-delete with trash retention period

---

## Input Validation

### Server-Side Validation

```python
# DocType field validation (JSON schema)
{
    "fieldname": "email",
    "fieldtype": "Data",
    "options": "Email",      # Built-in email validation
    "reqd": 1                # Required field
}

# Controller validation
def validate(self):
    if self.end_datetime <= self.start_datetime:
        frappe.throw(_("End time must be after start time"))
```

### Client-Side Validation

```javascript
frappe.ui.form.on("Space Booking", {
    validate(frm) {
        if (!frm.doc.space) {
            frappe.throw(__("Please select a space"));
            return false;
        }
    }
});
```

### ORM-Based Data Access

ARKSpace exclusively uses Frappe's ORM for database operations, which provides automatic:
- SQL injection prevention (parameterized queries)
- XSS prevention (HTML sanitization on output)
- Type validation based on DocType field definitions

---

## Dependency Security

### Python Dependencies

```toml
# pyproject.toml — minimal dependencies
[project]
dependencies = ["frappe", "erpnext"]
```

ARKSpace has only 2 Python dependencies — both are established, actively maintained projects.

### Frontend Dependencies

ARKSpace uses Frappe's built-in frontend stack and does not introduce additional npm packages.

### Supply Chain

- No third-party PyPI packages beyond Frappe/ERPNext
- No third-party npm packages
- CI pipeline includes lint checks (`ruff`) on every PR

---

## Deployment Security

### Recommended Configuration

```python
# site_config.json (production)
{
    "developer_mode": 0,           # MUST be disabled
    "disable_website_cache": 0,    # Enable caching
    "allow_cors": "https://your-domain.com",  # Restrict CORS
    "force_https": 1,              # Enforce HTTPS
}
```

### Production Checklist

- [ ] `developer_mode` set to `0`
- [ ] HTTPS enforced with valid SSL certificate
- [ ] Database credentials rotated from defaults
- [ ] Redis password configured
- [ ] File permissions restricted (`chmod 640` on config files)
- [ ] Regular backups configured
- [ ] Frappe framework kept up to date
- [ ] Monitoring and alerting enabled

---

## Vulnerability Reporting

### Responsible Disclosure

If you discover a security vulnerability in ARKSpace, please report it responsibly:

1. **Email:** security@arkspace.io
2. **Subject:** `[SECURITY] Brief description`
3. **Include:**
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact assessment
   - Suggested fix (if any)

### Response Timeline

| Phase | Timeline |
|-------|----------|
| Acknowledgment | Within 48 hours |
| Initial assessment | Within 1 week |
| Fix development | Within 2 weeks (critical) / 4 weeks (other) |
| Public disclosure | After fix is released |

### Scope

**In scope:**
- ARKSpace application code (Python, JavaScript)
- ARKSpace API endpoints
- Permission and access control logic
- Data handling and storage

**Out of scope:**
- Frappe Framework core vulnerabilities (report to [frappe.io](https://frappe.io))
- ERPNext core vulnerabilities (report to ERPNext team)
- Infrastructure/hosting issues (report to your hosting provider)

---

*See also: [ARCHITECTURE.md](ARCHITECTURE.md) | [ADMIN_GUIDE.md](ADMIN_GUIDE.md)*
