# ARKSpace Analysis Report

**Generated**: 2026-03-21  
**Analyzer**: AI Documentation Assistant  
**App Version**: 6.0.0

---

## Application Overview

| Property | Value |
|----------|-------|
| App Name | arkspace |
| Display Title | ARKSpace |
| Version | 6.0.0 |
| Frappe Version | v16 (v15 compatible) |
| Required Apps | erpnext |
| Publisher | ARKSpace Team |
| License | MIT |
| Python | ≥3.12 |
| Total Modules | 9 |
| Total DocTypes | 25 (18 standalone + 7 child) |
| Total Pages | 2 (Floor Plan, ARK Live) |
| Total Reports | 3 (Revenue Summary, Space Occupancy, Membership Analytics) |
| API Endpoints | 36 |
| Custom Roles | 7 |
| Workflows | 3 |
| Scheduled Tasks | 7 (4 daily + 2 hourly + 1 cron) |
| Notifications | 4 |
| Print Formats | 3 |
| Translation Coverage | 100% (706 unique entries) |

---

## Module Summary

| Module | DocTypes | APIs | Reports | Pages | Purpose |
|--------|----------|------|---------|-------|---------|
| arkspace_core | 1 | 2 | 1 | — | Settings, shared utilities, revenue report |
| arkspace_spaces | 5 | 9 | 1 | 2 | Spaces, bookings, amenities, floor plans |
| arkspace_memberships | 4 | 5 | 1 | — | Plans, subscriptions, credit wallets |
| arkspace_crm | 2 | 3 | — | — | Leads, tours, conversion pipeline |
| arkspace_contracts | 5 | 1 | — | — | Templates, legal docs, contracts, receipts |
| arkspace_training | 4 | 7 | — | — | Modules, sessions, badges, progress |
| arkspace_integrations | 0 | 3 | — | — | ERPNext billing bridge |
| arkspace_documentation | 4 | 2 | — | — | Auto-generated documentation |
| arkspace_design | 1 | 0 | — | — | Colors, icons, RTL theming |

---

## DocTypes Summary

### Standalone DocTypes (18)

| DocType | Module | Submittable | Has Workflow | Child Tables |
|---------|--------|-------------|--------------|--------------|
| ARKSpace Settings | Core | No (Single) | No | — |
| Co-working Space | Spaces | No | No | Space Amenity, Space Image |
| Space Type | Spaces | No | No | — |
| Amenity | Spaces | No | No | — |
| Space Booking | Spaces | Yes | Yes | — |
| Membership Plan | Memberships | No | No | — |
| Membership | Memberships | Yes | Yes | — |
| Member Credit Wallet | Memberships | No | No | Credit Transaction |
| Workspace Lead | CRM | No | Yes | — |
| Workspace Tour | CRM | No | No | — |
| Contract Template | Contracts | No | No | — |
| Legal Document | Contracts | No | No | — |
| Member Contract | Contracts | Yes | No | Contract Legal Document |
| Payment Receipt | Contracts | No | No | — |
| Training Module | Training | No | No | — |
| Training Session | Training | No | No | — |
| Training Badge | Training | No | No | — |
| User Training Progress | Training | No | No | — |
| Documentation Entry | Documentation | No | No | Doc. Prerequisite, Doc. Relation, Doc. Code Example |
| Design Configuration | Design | No (Single) | No | — |

### Child Tables (7)

| Child DocType | Parent DocType |
|---------------|----------------|
| Space Amenity | Co-working Space |
| Space Image | Co-working Space |
| Credit Transaction | Member Credit Wallet |
| Contract Legal Document | Member Contract |
| Documentation Prerequisite | Documentation Entry |
| Documentation Relation | Documentation Entry |
| Documentation Code Example | Documentation Entry |

---

## API Endpoints (36)

| Module | Endpoint | Auth | Method |
|--------|----------|------|--------|
| Core | `arkspace.api.test_ping` | Guest | GET |
| Core | `arkspace.api.get_app_info` | User | GET |
| Spaces | `arkspace.arkspace_spaces.api.get_available_spaces` | User | GET |
| Spaces | `arkspace.arkspace_spaces.api.check_in` | User | POST |
| Spaces | `arkspace.arkspace_spaces.api.check_out` | User | POST |
| Spaces | `arkspace.arkspace_spaces.api.cancel_booking` | User | POST |
| Spaces | `arkspace.arkspace_spaces.floor_plan.get_floor_plan_data` | User | GET |
| Spaces | `arkspace.arkspace_spaces.ark_live.get_ark_live_data` | User | GET |
| Spaces | `arkspace.arkspace_spaces.ark_live.quick_book` | User | POST |
| Spaces | `arkspace.arkspace_spaces.bulk_operations.bulk_check_in` | User | POST |
| Spaces | `arkspace.arkspace_spaces.bulk_operations.bulk_check_out` | User | POST |
| Spaces | `arkspace.arkspace_spaces.bulk_operations.bulk_cancel` | User | POST |
| Spaces | `arkspace.arkspace_spaces.bulk_operations.bulk_no_show` | User | POST |
| Memberships | `arkspace.arkspace_memberships.api.get_membership_details` | User | GET |
| Memberships | `arkspace.arkspace_memberships.api.activate_membership` | User | POST |
| Memberships | `arkspace.arkspace_memberships.api.suspend_membership` | User | POST |
| Memberships | `arkspace.arkspace_memberships.api.add_credits` | User | POST |
| Memberships | `arkspace.arkspace_memberships.api.deduct_credits` | User | POST |
| CRM | `workspace_lead.convert_to_customer` | User | POST |
| CRM | `workspace_lead.schedule_tour` | User | POST |
| CRM | `workspace_tour.complete_tour` | User | POST |
| Contracts | `member_contract.populate_from_template` | User | POST |
| Training | `arkspace.arkspace_training.api.enroll_user` | User | POST |
| Training | `arkspace.arkspace_training.api.get_training_catalog` | User | GET |
| Training | `arkspace.arkspace_training.api.get_user_progress` | User | GET |
| Training | `arkspace.arkspace_training.api.get_available_sessions` | User | GET |
| Training | `user_training_progress.update_progress` | User | POST |
| Training | `user_training_progress.complete_module` | User | POST |
| Training | `user_training_progress.award_badge` | User | POST |
| Integrations | `arkspace.arkspace_integrations.api.get_customer_invoices` | User | GET |
| Integrations | `arkspace.arkspace_integrations.api.get_customer_payments` | User | GET |
| Integrations | `arkspace.arkspace_integrations.billing.create_booking_invoice` | User | POST |
| Documentation | `arkspace.arkspace_documentation.auto_generator.regenerate_documentation` | User | POST |
| Documentation | `arkspace.arkspace_documentation.auto_generator.generate_single_doc` | User | POST |
| Setup | `arkspace.setup_wizard.setup_arkspace_complete` | User | POST |

---

## Existing Documentation Inventory

| File | Location | Lines | Status | Action |
|------|----------|-------|--------|--------|
| README.md | root | 100 | ✅ Good | Enhance with marketplace badges |
| README_AR.md | root | 75 | ✅ Good | Keep as-is |
| CHANGELOG.md | root | 93 | ✅ Good | Keep as-is |
| CONTRIBUTING.md | root | 276 | ✅ Good | Keep as-is |
| LICENSE | root | 21 | ✅ Good | Keep as-is |
| ADMIN_GUIDE.md | docs/ | 300 | ✅ Good | Copy to docs/en/, create docs/ar/ |
| AI_CONTEXT.md | docs/ | 158 | ✅ Good | Keep, expand slightly |
| API_REFERENCE.md | docs/ | 445 | ✅ Good | Rename → API_DOCS.md |
| CODE_REVIEW.md | docs/ | 145 | ✅ Good | Keep as-is |
| DEV_SESSION_SUMMARY.md | docs/ | 104 | ✅ Good | Rename → SESSION_LOG.md |
| DOCTYPES_REFERENCE.md | docs/ | 577 | ✅ Good | Keep as-is |
| FEATURES_AR.md | docs/ | 185 | ✅ Good | Copy to docs/ar/ |
| FEATURES_EN.md | docs/ | 241 | ✅ Good | Copy to docs/en/ |
| INTEGRATIONS.md | docs/ | 263 | ✅ Good | Keep as-is |
| PAGES_REFERENCE.md | docs/ | 221 | ✅ Good | Keep as-is |
| QUALITY_ASSURANCE.md | docs/ | 290 | ✅ Good | Keep as-is |
| ROADMAP.md | docs/ | 150 | ✅ Good | Keep as-is |
| TECHNICAL_IMPLEMENTATION.md | docs/ | 500 | ✅ Good | Alias → TECHNICAL_SPECS |
| TROUBLESHOOTING.md | docs/ | 366 | ✅ Good | Keep as-is |
| USER_GUIDE.md | docs/ | 281 | ✅ Good | Copy to docs/en/, create docs/ar/ |

---

## Translation Status

| Metric | Value |
|--------|-------|
| ar.csv entries | 706 unique |
| en.csv entries | 706 unique |
| Code coverage | 100% (284/284 `_()`/`__()` strings) |
| Arabic in source | Comments/docstrings only (intentional) |
| Bilingual select options | Contracts module (by design) |

---

## Files to Create

| Priority | File | Purpose |
|----------|------|---------|
| P0 | docs/AI_PROMPT.md | AI assistant master instructions |
| P0 | docs/CONTEXT.md | Full application context |
| P0 | docs/ARCHITECTURE.md | System architecture |
| P0 | docs/DEVELOPER_GUIDE.md | Developer onboarding |
| P1 | docs/SALES_PITCH.md | Sales & marketing content |
| P1 | docs/MARKETPLACE_LISTING.md | Frappe Marketplace submission |
| P1 | docs/SECURITY.md | Security documentation |
| P1 | docs/TECHNICAL_SPECS.md | Technical specifications |
| P1 | docs/SESSION_LOG.md | Development session history |
| P2 | docs/ar/README.md | Arabic documentation index |
| P2 | docs/ar/USER_GUIDE.md | Arabic user guide |
| P2 | docs/ar/ADMIN_GUIDE.md | Arabic admin guide |
| P2 | docs/ar/FEATURES.md | Arabic features |
| P2 | docs/en/README.md | English documentation index |
| P2 | docs/en/USER_GUIDE.md | English user guide |
| P2 | docs/en/ADMIN_GUIDE.md | English admin guide |
| P2 | docs/en/FEATURES.md | English features |
| P2 | arkspace/help/{ar,en}/ | In-app help files |
| P3 | marketplace/listing.json | Marketplace metadata |
| P3 | SECURITY.md (root) | Security policy |
| P3 | .github/ISSUE_TEMPLATE/documentation.md | Doc issue template |
| P3 | .github/workflows/release.yml | Release workflow |
| P3 | .github/workflows/docs.yml | Docs workflow |

---

## Recommendations

1. **Enhance README.md** with marketplace badges, screenshots section, and cleaner structure
2. **Create bilingual docs/{ar,en}/** directories for user-facing documentation
3. **Add AI_PROMPT.md** as master instructions for AI assistants working on the codebase
4. **Add CONTEXT.md** as comprehensive application context document
5. **Add marketplace/** directory with listing metadata for Frappe Marketplace publication
6. **Add in-app help** system under `arkspace/help/` for contextual user assistance
7. **Add release.yml** GitHub workflow for automated release creation
8. **Create SECURITY.md** for vulnerability reporting process

---

*Generated by AI Documentation Assistant — Phase 1 Discovery*
