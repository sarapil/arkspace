# ARKSpace Troubleshooting

> **Version:** 6.0.0 | **Updated:** 2026-03-21

## Table of Contents

- [Installation Issues](#installation-issues)
- [JavaScript / CSS Issues](#javascript--css-issues)
- [Database Issues](#database-issues)
- [Permission Issues](#permission-issues)
- [Booking Issues](#booking-issues)
- [Membership Issues](#membership-issues)
- [Integration Issues](#integration-issues)
- [Portal Issues](#portal-issues)
- [Real-time Issues](#real-time-issues)
- [Translation Issues](#translation-issues)

---

## Installation Issues

### App installation fails with dependency error

**Error:** `arkspace requires erpnext`

**Solution:**
```bash
bench get-app --branch version-16 erpnext
bench --site {site} install-app erpnext
bench --site {site} install-app arkspace
```

### Setup wizard not appearing

**Cause:** Setup wizard stage JS not loaded.

**Solution:**
```bash
bench build --app arkspace
bench --site {site} clear-cache
# Refresh browser with Ctrl+Shift+R
```

### Roles not created after install

**Solution:**
```bash
bench --site {site} migrate
# Or manually trigger:
bench --site {site} execute arkspace.install.after_install
```

---

## JavaScript / CSS Issues

### Styles not applying / JS not loading

```bash
# Clear all caches and rebuild
bench --site {site} clear-cache
bench build --app arkspace
```

### Design system CSS variables not working

**Cause:** `design-system.css` not loaded.

**Check:** Verify in browser DevTools → Network tab that `/assets/arkspace/css/design-system.css` is loaded.

**Solution:** Ensure `hooks.py` has `app_include_css` entries. Run `bench build --app arkspace`.

### Floor Plan page blank

**Cause:** JS bundle error or no spaces created.

**Solution:**
1. Check browser console for errors
2. Ensure at least one Co-working Space exists
3. Run `bench build --app arkspace`

---

## Database Issues

### Migration errors

```bash
bench --site {site} migrate
# If schema conflicts:
bench --site {site} migrate --rebuild-website
```

### DocType not found

**Error:** `DocType 'Co-working Space' not found`

**Solution:**
```bash
bench --site {site} migrate
bench --site {site} clear-cache
```

### Check database connection

```bash
bench --site {site} mariadb
# In MariaDB:
SHOW TABLES LIKE 'tabCo-working Space';
SELECT COUNT(*) FROM `tabCo-working Space`;
```

---

## Permission Issues

### "Not permitted" error

**Diagnosis:**
```python
# In bench console
bench --site {site} console
>>> frappe.get_roles("user@example.com")
>>> frappe.has_permission("Space Booking", "read", user="user@example.com")
```

**Common causes:**
1. User missing ARKSpace role
2. Member trying to access another member's records
3. Row-level permission blocking access

**Solution:**
```python
# Assign role
bench --site {site} execute frappe.client.add_to_roles \
    --args '["user@example.com", "ARKSpace Member"]'
```

### Member can't see bookings

**Cause:** No Customer linked to user, or Customer doesn't match booking.

**Check:**
```python
# In bench console
>>> customer = frappe.db.get_value("Contact", {"user": "user@example.com"}, "name")
>>> frappe.db.get_value("Dynamic Link", {"parent": customer, "link_doctype": "Customer"}, "link_name")
```

---

## Booking Issues

### "Space already booked" error

**Cause:** Overlapping booking exists.

**Diagnosis:**
```python
frappe.get_all("Space Booking",
    filters={
        "space": "SpaceName",
        "docstatus": 1,
        "status": ["not in", ["Cancelled", "No Show"]],
        "start_datetime": ["<=", end_time],
        "end_datetime": [">=", start_time]
    })
```

### Check-in fails

**Possible causes:**
1. Booking not submitted (`docstatus != 1`)
2. Status is not "Confirmed" (e.g., already "Checked In" or "Cancelled")

**Fix:** Ensure the booking is submitted and in "Confirmed" status.

### No-show not triggered

**Cause:** Hourly cron not running.

**Check:**
```bash
bench --site {site} execute arkspace.tasks.mark_no_show_bookings
```

---

## Membership Issues

### Credit wallet not created

**Cause:** Membership not submitted, or billing hook error.

**Manual fix:**
```python
bench --site {site} console
>>> from arkspace.arkspace_memberships.api import create_membership
>>> # Or manually create wallet:
>>> frappe.get_doc({"doctype": "Member Credit Wallet", "member": "CustomerName"}).insert()
```

### Auto-renew not working

**Diagnosis:**
1. Check membership has `auto_renew = 1`
2. Check `end_date` is today
3. Check scheduler is running

```bash
bench --site {site} execute arkspace.tasks.auto_renew_memberships
```

### Expiry reminders not sent

**Check:**
1. Email setup is correct (`bench --site {site} console → frappe.sendmail`)
2. Notification "Membership Expiry Reminder" exists and is enabled
3. Members have email addresses

---

## Integration Issues

### Sales Invoice not created on booking submit

**Diagnosis:**
1. Check ERPNext is installed: `bench --site {site} list-apps`
2. Check doc_events in hooks.py
3. Check for errors in error log

```python
bench --site {site} console
>>> from arkspace.arkspace_integrations.api import get_integration_status
>>> get_integration_status()
```

### Employee not linked to Customer

**Cause:** Employee doesn't have matching email/phone.

**Solution:** Ensure Employee has the same email as the Customer's primary contact.

---

## Portal Issues

### "Please login to access the member portal"

**Cause:** User is not logged in or session expired.

**Solution:** Log in at `/login` first.

### Portal shows "No membership found"

**Cause:** No Customer linked to the logged-in user.

**Solution:**
1. Create a Contact with the user's email
2. Link the Contact to a Customer via Dynamic Link
3. Ensure Customer has an active Membership

### Booking from portal fails

**Cause:** Insufficient permissions or no available spaces.

**Check:** Browser console for API error details.

---

## Real-time Issues

### Floor plan not updating in real-time

**Diagnosis:**
1. Check Socket.IO is running:
   ```bash
   ps aux | grep socketio
   ```
2. Check browser console for WebSocket connection
3. Verify `frappe.publish_realtime` is called in check-in/out functions

**Solution:**
```bash
# Restart bench (includes socketio)
bench start
```

### Events not reaching client

**Check:**
```javascript
// In browser console
frappe.realtime.on("space_status_changed", function(data) {
    console.log("Received:", data);
});
```

---

## Translation Issues

### Arabic text not showing

**Diagnosis:**
1. Check user's language is set to Arabic
2. Check `translations/ar.csv` contains the string
3. Clear cache after updating translations

```bash
bench --site {site} clear-cache
```

### Import translations

```bash
bench --site {site} import-translations arkspace /path/to/ar.csv
```

### Export untranslated strings

```bash
bench --site {site} get-untranslated arkspace -l ar
```

### Hardcoded Arabic in source

```bash
# Find hardcoded Arabic in Python/JS
grep -rn '[؀-ۿ]' arkspace/ --include="*.py" --include="*.js" --exclude-dir=translations
```

---

## General Debugging

### Enable developer mode

```python
# In site_config.json
{"developer_mode": 1}
```

### Check error logs

```bash
bench --site {site} console
>>> frappe.get_all("Error Log", limit=5, fields=["name", "error", "creation"])
```

### Clear all caches

```bash
bench --site {site} clear-cache
bench --site {site} clear-website-cache
```

### Rebuild search index

```bash
bench --site {site} build-search-index
```

---

*See also: [ADMIN_GUIDE.md](ADMIN_GUIDE.md) | [QUALITY_ASSURANCE.md](QUALITY_ASSURANCE.md)*
