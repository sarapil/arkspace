# ARKSpace Code Review

> **Version:** 6.0.0 | **Reviewed:** 2026-03-21

## Review Scope

Full code audit of the ARKSpace Frappe application covering security, performance, code quality, and best practices.

## Review Checklist

### Security ✅

| Check | Status | Notes |
|-------|--------|-------|
| SQL injection vulnerabilities | ✅ Pass | Uses `frappe.db` ORM, parameterized queries |
| Permission checks on all APIs | ✅ Pass | `@frappe.whitelist()` on all endpoints; `has_permission` hooks |
| Error handling present | ✅ Pass | `frappe.throw()` with translatable messages |
| No hardcoded secrets | ✅ Pass | API keys stored in Password fields in Settings |
| XSS prevention | ✅ Pass | Frappe's built-in sanitization |
| CSRF protection | ✅ Pass | Frappe framework handles CSRF tokens |
| Row-level permissions | ✅ Pass | `permissions.py` restricts Member role to own records |

### Performance

| Check | Status | Notes |
|-------|--------|-------|
| No N+1 query patterns | ⚠️ Warning | `get_member_dashboard` could benefit from SQL joins vs multiple queries |
| Efficient list queries | ✅ Pass | Uses `frappe.get_all` with field selection |
| Index usage | ✅ Pass | Key fields have indexes (status, dates, foreign keys) |
| Bulk operation efficiency | ✅ Pass | Bulk check-in/out uses batch processing |
| Cron job performance | ⚠️ Warning | `regenerate_documentation` scans all DocTypes — could be slow with many custom apps |

### Code Quality

| Check | Status | Notes |
|-------|--------|-------|
| Functions under 50 lines | ✅ Pass | Most functions are concise |
| Meaningful variable names | ✅ Pass | Clear, descriptive names |
| Docstrings present | ✅ Pass | All API functions documented |
| Consistent code style | ✅ Pass | Ruff linting configured |
| DRY principle | ✅ Pass | Shared utils, re-exported APIs |
| Error messages translated | ✅ Pass | All errors use `_()` wrapper |

### Bilingual Support

| Check | Status | Notes |
|-------|--------|-------|
| All strings translatable | ✅ Pass | `_()` used consistently |
| Arabic translations complete | ✅ Pass | 272 entries in ar.csv |
| RTL layout tested | ⚠️ Warning | Some edge cases in floor plan page |
| Bilingual Select options | ✅ Pass | "English / العربي" format |
| `_ar` suffix fields | ✅ Pass | All major DocTypes have bilingual fields |

---

## Findings

### Critical — None 🟢

No critical security or functionality issues found.

### High Priority — 2 Items

#### H1: Dashboard API N+1 Queries

**File:** `arkspace/arkspace_memberships/api.py` → `get_member_dashboard()`

**Issue:** Multiple separate DB queries for memberships, bookings, wallet, and stats.

**Recommendation:** Combine into fewer queries using SQL joins or `frappe.get_all` with proper filters.

```python
# Current: 4+ separate queries
memberships = frappe.get_all("Membership", filters={"member": member, "status": "Active"})
bookings = frappe.get_all("Space Booking", filters={"member": member})
wallet = frappe.get_doc("Member Credit Wallet", member)

# Recommended: Use SQL for combined stats
stats = frappe.db.sql("""
    SELECT
        (SELECT COUNT(*) FROM `tabMembership` WHERE member=%s AND status='Active') as active_memberships,
        (SELECT COUNT(*) FROM `tabSpace Booking` WHERE member=%s AND docstatus=1) as total_bookings
""", (member, member), as_dict=True)[0]
```

#### H2: Documentation Generator Performance

**File:** `arkspace/arkspace_documentation/auto_generator.py`

**Issue:** Nightly cron scans all DocTypes and modules, which could become slow.

**Recommendation:** Add incremental generation — only regenerate docs for DocTypes modified since last run.

### Medium Priority — 3 Items

#### M1: Missing Input Validation on Tour Rating

**File:** `arkspace/arkspace_crm/doctype/workspace_tour/workspace_tour.py`

**Recommendation:** Validate rating is between 1–5 in `validate()`.

#### M2: Credit Wallet Race Condition

**File:** `arkspace/arkspace_memberships/doctype/member_credit_wallet/member_credit_wallet.py`

**Issue:** Concurrent debit operations could lead to negative balance.

**Recommendation:** Use `frappe.db.sql` with `FOR UPDATE` lock when debiting.

#### M3: Floor Plan Page Performance

**File:** `arkspace/arkspace_spaces/floor_plan.py`

**Issue:** Loads all spaces on initial page load.

**Recommendation:** Add pagination or lazy loading for large installations.

### Low Priority — 2 Items

#### L1: Unused `ARKSpace Viewer` Role

The Viewer role is defined but not assigned any permissions. Consider implementing or removing.

#### L2: Setup Wizard Hardcoded Defaults

**File:** `arkspace/setup_wizard.py`

Some default values (currency, timezone) are hardcoded. Consider making them configurable.

---

## Summary

| Severity | Count | Status |
|----------|-------|--------|
| Critical | 0 | 🟢 All clear |
| High | 2 | 🟡 Needs attention |
| Medium | 3 | 🟡 Recommended fixes |
| Low | 2 | ⚪ Optional |

**Overall Assessment:** The codebase is well-structured, follows Frappe conventions, and has good security practices. The main areas for improvement are query optimization and edge case handling.

---

*See also: [QUALITY_ASSURANCE.md](QUALITY_ASSURANCE.md) | [TECHNICAL_IMPLEMENTATION.md](TECHNICAL_IMPLEMENTATION.md)*
