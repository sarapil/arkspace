# ARKSpace Quality Assurance

> **Version:** 6.0.0 | **Updated:** 2026-03-21

## Table of Contents

- [Test Environment Setup](#test-environment-setup)
- [Running Tests](#running-tests)
- [Test Categories](#test-categories)
- [Writing Tests](#writing-tests)
- [Manual Testing Checklist](#manual-testing-checklist)
- [Performance Testing](#performance-testing)
- [Bilingual Testing](#bilingual-testing)

---

## Test Environment Setup

### Prerequisites

```bash
# Ensure bench is set up with a test site
bench new-site test.local --db-root-password root --admin-password admin
bench --site test.local install-app erpnext
bench --site test.local install-app arkspace
```

### Compatibility

Tests use `ARKSpaceTestCase` from `arkspace.tests.compat` which auto-selects the correct base class for Frappe v15 or v16.

```python
from arkspace.tests.compat import ARKSpaceTestCase

class TestMyFeature(ARKSpaceTestCase):
    pass
```

---

## Running Tests

### All Tests

```bash
cd frappe-bench/sites
../env/bin/python -m pytest ../apps/arkspace/ -x -v
```

### By Module

```bash
# Spaces module
../env/bin/python -m pytest ../apps/arkspace/arkspace/arkspace_spaces/ -x -v

# Memberships module
../env/bin/python -m pytest ../apps/arkspace/arkspace/arkspace_memberships/ -x -v

# CRM module
../env/bin/python -m pytest ../apps/arkspace/arkspace/arkspace_crm/ -x -v

# Contracts module
../env/bin/python -m pytest ../apps/arkspace/arkspace/arkspace_contracts/ -x -v

# Training module
../env/bin/python -m pytest ../apps/arkspace/arkspace/arkspace_training/ -x -v
```

### By File

```bash
../env/bin/python -m pytest ../apps/arkspace/arkspace/arkspace_spaces/doctype/space_booking/test_space_booking.py -x -v
```

### With Coverage

```bash
../env/bin/python -m pytest ../apps/arkspace/ --cov=arkspace --cov-report=html -x -v
```

### Using Bench

```bash
bench --site test.local run-tests --app arkspace --failfast
```

---

## Test Categories

### Unit Tests

Test individual functions and methods in isolation.

| Module | Test File | Coverage |
|--------|-----------|----------|
| Spaces | `test_space_booking.py` | Booking lifecycle, validation, overlap |
| Spaces | `test_coworking_space.py` | Space CRUD, status transitions |
| Memberships | `test_membership.py` | Lifecycle, auto-renew, credits |
| Memberships | `test_credit_wallet.py` | Credit/debit, balance calculations |
| CRM | `test_workspace_lead.py` | Pipeline, conversion |
| CRM | `test_workspace_tour.py` | Scheduling, completion |
| Contracts | `test_member_contract.py` | Contract lifecycle, rendering |
| Training | `test_training_session.py` | Enrollment, progress, badges |

### Integration Tests

Test interactions between modules.

| Test | Coverage |
|------|----------|
| Booking → Billing | Booking submit creates Sales Invoice |
| Membership → Wallet | Membership submit allocates credits |
| Lead → Customer → Membership | Full conversion flow |
| Training → Badge | Completion awards badge |

### API Tests

Test all whitelisted endpoints.

```python
class TestSpacesAPI(ARKSpaceTestCase):
    def test_get_available_spaces(self):
        result = frappe.call(
            "arkspace.arkspace_spaces.api.get_available_spaces",
            space_type="Hot Desk"
        )
        self.assertIsInstance(result, list)

    def test_create_booking(self):
        result = frappe.call(
            "arkspace.arkspace_spaces.api.create_booking",
            space=self.space.name,
            member=self.customer.name,
            booking_type="Hourly",
            start_datetime="2026-04-01 10:00:00",
            end_datetime="2026-04-01 12:00:00"
        )
        self.assertEqual(result.status, "Confirmed")
```

---

## Writing Tests

### Test Fixtures

```python
def make_test_space(space_type="Hot Desk", branch="Main Branch"):
    """Create a test Co-working Space."""
    return frappe.get_doc({
        "doctype": "Co-working Space",
        "space_name": f"Test Space {frappe.generate_hash(length=6)}",
        "space_type": space_type,
        "branch": branch,
        "capacity": 1,
        "hourly_rate": 50,
        "daily_rate": 300,
        "monthly_rate": 5000,
        "status": "Available"
    }).insert()

def make_test_customer():
    """Create a test Customer."""
    return frappe.get_doc({
        "doctype": "Customer",
        "customer_name": f"Test Customer {frappe.generate_hash(length=6)}",
        "customer_type": "Individual"
    }).insert()
```

### Test Lifecycle Pattern

```python
class TestSpaceBooking(ARKSpaceTestCase):
    def setUp(self):
        self.space = make_test_space()
        self.customer = make_test_customer()

    def test_booking_lifecycle(self):
        # Create
        booking = create_booking(
            self.space.name, self.customer.name,
            "Hourly", "2026-04-01 10:00", "2026-04-01 12:00"
        )
        self.assertEqual(booking.status, "Confirmed")

        # Check in
        check_in(booking.name)
        booking.reload()
        self.assertEqual(booking.status, "Checked In")

        # Check out
        check_out(booking.name)
        booking.reload()
        self.assertEqual(booking.status, "Checked Out")

    def test_double_booking_prevented(self):
        create_booking(self.space.name, self.customer.name,
                      "Hourly", "2026-04-01 10:00", "2026-04-01 12:00")
        with self.assertRaises(frappe.ValidationError):
            create_booking(self.space.name, self.customer.name,
                          "Hourly", "2026-04-01 11:00", "2026-04-01 13:00")

    def tearDown(self):
        frappe.db.rollback()
```

---

## Manual Testing Checklist

### Space Booking Flow

- [ ] Create Space Type
- [ ] Create Amenity
- [ ] Create Co-working Space
- [ ] Open Floor Plan page — verify space appears
- [ ] Create booking from Floor Plan quick-book
- [ ] Submit booking — verify status "Confirmed"
- [ ] Check In — verify space status "Occupied"
- [ ] Check Out — verify space status "Available"
- [ ] Verify Sales Invoice created (if ERPNext billing enabled)
- [ ] Test cancel booking
- [ ] Test bulk check-in from list view

### Membership Flow

- [ ] Create Membership Plan
- [ ] Create Customer
- [ ] Create Membership → Submit
- [ ] Verify Credit Wallet created
- [ ] Verify credits allocated
- [ ] Verify Sales Invoice created
- [ ] Wait for expiry (or manually set date) → verify expiry task runs
- [ ] Test auto-renew

### CRM Flow

- [ ] Create Workspace Lead
- [ ] Schedule Tour → verify lead status changes
- [ ] Complete Tour → verify outcome recorded
- [ ] Convert to Customer → verify Customer created
- [ ] Verify lead status "Converted"

### Bilingual Testing

- [ ] Switch language to Arabic
- [ ] Verify all form labels appear in Arabic
- [ ] Verify all status values show Arabic
- [ ] Verify RTL layout is correct
- [ ] Verify Floor Plan page in Arabic
- [ ] Verify Member Portal in Arabic
- [ ] Verify Print Formats in Arabic
- [ ] Verify email notifications in Arabic

---

## Performance Testing

### Key Metrics

| Operation | Target | Measurement |
|-----------|--------|-------------|
| Floor Plan load | < 2s | With 100 spaces |
| Available spaces query | < 500ms | With 500 spaces |
| Dashboard stats | < 1s | With 10,000 bookings |
| Member dashboard | < 1s | Per member |
| Booking creation | < 500ms | Including validation |

### Load Testing

```bash
# Use bench's built-in profiling
bench --site test.local --profile execute arkspace.api.get_dashboard_stats
```

---

## CI Pipeline

The GitHub Actions CI workflow (`ci.yml`) runs:

1. **Lint** — `ruff check` and `ruff format --check`
2. **Tests** — Full test suite with MariaDB + Redis
3. **Translations** — Checks ar.csv exists and scans for hardcoded Arabic

---

*See also: [CODE_REVIEW.md](CODE_REVIEW.md) | [TROUBLESHOOTING.md](TROUBLESHOOTING.md)*
