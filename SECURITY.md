# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 6.x     | ✅ Active  |
| 5.x     | ⚠️ Security fixes only |
| < 5.0   | ❌ End of life |

## Reporting a Vulnerability

If you discover a security vulnerability in ARKSpace, please report it responsibly.

### How to Report

1. **Email:** security@arkspace.io
2. **Subject:** `[SECURITY] Brief description of the vulnerability`
3. **Include:**
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact assessment
   - Suggested fix (if any)

### What to Expect

| Phase | Timeline |
|-------|----------|
| Acknowledgment | Within 48 hours |
| Initial assessment | Within 1 week |
| Fix for critical issues | Within 2 weeks |
| Fix for other issues | Within 4 weeks |
| Public disclosure | After fix is released |

### Please Do NOT

- Open a public GitHub issue for security vulnerabilities
- Share vulnerability details publicly before a fix is released
- Access or modify other users' data during testing

### Scope

**In scope:**
- ARKSpace application code (Python, JavaScript)
- ARKSpace API endpoints and permission logic
- Data handling, access control, and storage

**Out of scope:**
- Frappe Framework core (report to [frappe.io](https://frappe.io))
- ERPNext core (report to the ERPNext team)
- Infrastructure/hosting issues (report to your hosting provider)

## Security Documentation

For detailed security architecture, see [docs/SECURITY.md](docs/SECURITY.md).

## Thank You

We appreciate responsible disclosure and will credit reporters (with permission) in our security advisories.
