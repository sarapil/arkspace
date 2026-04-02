## Description / الوصف

<!-- What does this PR do? Brief summary of changes -->

## Related Issue / المسألة المرتبطة

Closes #

## Type of Change / نوع التغيير

- [ ] 🐛 Bug fix (non-breaking change that fixes an issue)
- [ ] ✨ New feature (non-breaking change that adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to change)
- [ ] 📝 Documentation update
- [ ] 🌐 Translation update
- [ ] 🎨 Design / UI change
- [ ] ♻️ Refactor (no functional changes)
- [ ] 🧪 Tests

## Module(s) Affected / الوحدات المتأثرة

- [ ] arkspace_core
- [ ] arkspace_spaces
- [ ] arkspace_memberships
- [ ] arkspace_crm
- [ ] arkspace_contracts
- [ ] arkspace_training
- [ ] arkspace_integrations
- [ ] arkspace_documentation
- [ ] arkspace_design

## Checklist / قائمة المراجعة

### Code Quality
- [ ] Code follows project conventions
- [ ] Functions are under 50 lines
- [ ] Meaningful variable names used
- [ ] Docstrings added for new functions
- [ ] No hardcoded secrets or credentials

### Bilingual / ثنائي اللغة
- [ ] All new strings wrapped in `_()` or `__()`
- [ ] Arabic translations added to `translations/ar.csv`
- [ ] RTL layout tested (if UI changes)
- [ ] Works in both Arabic and English

### Security
- [ ] Permission checks on all new APIs (`frappe.has_permission()`)
- [ ] No SQL injection vulnerabilities
- [ ] `@frappe.whitelist()` on all exposed methods

### Documentation
- [ ] `docs/FEATURES_EN.md` updated (if new features)
- [ ] `docs/FEATURES_AR.md` updated (if new features)
- [ ] `docs/API_REFERENCE.md` updated (if API changes)
- [ ] `docs/DOCTYPES_REFERENCE.md` updated (if schema changes)
- [ ] `CHANGELOG.md` updated

### Testing
- [ ] Tests added for new functionality
- [ ] All existing tests pass
- [ ] Manual testing completed

## Screenshots / لقطات الشاشة

<!-- If UI changes, add before/after screenshots -->

## Testing Instructions / تعليمات الاختبار

<!-- How should reviewers test this? -->

```bash
# Run tests
cd frappe-bench/sites && ../env/bin/python -m pytest ../apps/arkspace/ -x -v
```
