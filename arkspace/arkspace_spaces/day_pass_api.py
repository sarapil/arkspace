# Copyright (c) 2026, ARKSpace Team and contributors
# For license information, please see license.txt

"""Day Pass — Public API Endpoints
تصريح اليوم — واجهة برمجة التطبيقات

Provides endpoints for creating walk-in day passes, checking in/out,
converting to memberships, and QR scan check-in.
"""

import frappe
from frappe import _
from frappe.utils import getdate, nowdate

# ═══════════════════════════════════════════════════════════════════════════
# Walk-in / Quick Create
# ═══════════════════════════════════════════════════════════════════════════


@frappe.whitelist()
def create_day_pass(
    guest_name,
    pass_type="Full Day",
    guest_email=None,
    guest_phone=None,
    guest_company=None,
    guest_type="Walk-in",
    space=None,
    rate=None,
    payment_method="Cash",
    pass_date=None,
    start_time=None,
    end_time=None,
    is_trial=0,
    trial_plan=None,
    notes=None,
):
    """Create and optionally submit a Day Pass.

    Args:
        guest_name: Required — name of the guest
        pass_type: Full Day / Half Day / Hourly / Evening / Weekend
        guest_email: Optional email
        guest_phone: Optional phone
        guest_company: Optional company name
        guest_type: Walk-in / Online / Referred / Trial / Corporate / Event Attendee
        space: Link to Co-working Space
        rate: Override rate (auto-calculated if not given)
        payment_method: Cash / Card / Online / Wallet / Free
        pass_date: Date (defaults to today)
        start_time: HH:MM start time
        end_time: HH:MM end time
        is_trial: 1/0 — mark as trial pass
        trial_plan: Membership Plan for trial
        notes: Additional notes

    Returns:
        dict with day_pass name and details
    """
    # Auto-set rate from settings if not provided
    if not rate:
        rate = _get_default_rate(pass_type, space)

    doc = frappe.get_doc({
        "doctype": "Day Pass",
        "guest_name": guest_name,
        "guest_email": guest_email,
        "guest_phone": guest_phone,
        "guest_company": guest_company,
        "guest_type": guest_type,
        "pass_type": pass_type,
        "pass_date": pass_date or nowdate(),
        "start_time": start_time,
        "end_time": end_time,
        "space": space,
        "rate": rate,
        "payment_method": payment_method,
        "is_trial": int(is_trial),
        "trial_plan": trial_plan,
        "notes": notes,
    })
    doc.insert(ignore_permissions=True)
    doc.submit()

    return {
        "day_pass": doc.name,
        "guest_name": doc.guest_name,
        "status": doc.status,
        "net_amount": doc.net_amount,
        "qr_code": doc.qr_code,
    }


@frappe.whitelist()
def get_day_pass(name):
    """Get full details of a Day Pass.

    Args:
        name: Day Pass name (e.g. DP-2026-00001)

    Returns:
        dict with day pass details
    """
    doc = frappe.get_doc("Day Pass", name)
    doc.check_permission("read")

    return {
        "name": doc.name,
        "guest_name": doc.guest_name,
        "guest_email": doc.guest_email,
        "guest_phone": doc.guest_phone,
        "guest_type": doc.guest_type,
        "pass_type": doc.pass_type,
        "pass_date": str(doc.pass_date),
        "start_time": str(doc.start_time) if doc.start_time else None,
        "end_time": str(doc.end_time) if doc.end_time else None,
        "duration_hours": doc.duration_hours,
        "space": doc.space,
        "rate": doc.rate,
        "discount_percent": doc.discount_percent,
        "net_amount": doc.net_amount,
        "payment_method": doc.payment_method,
        "status": doc.status,
        "checked_in_at": str(doc.checked_in_at) if doc.checked_in_at else None,
        "checked_out_at": str(doc.checked_out_at) if doc.checked_out_at else None,
        "qr_code": doc.qr_code,
        "is_trial": doc.is_trial,
        "converted_to_membership": doc.converted_to_membership,
        "membership": doc.membership,
    }


# ═══════════════════════════════════════════════════════════════════════════
# Check-in / Check-out
# ═══════════════════════════════════════════════════════════════════════════


@frappe.whitelist()
def day_pass_check_in(name):
    """Check in a Day Pass guest.

    Args:
        name: Day Pass name

    Returns:
        dict with updated status
    """
    doc = frappe.get_doc("Day Pass", name)
    doc.check_in()
    return {"day_pass": doc.name, "status": doc.status, "checked_in_at": str(doc.checked_in_at)}


@frappe.whitelist()
def day_pass_check_out(name):
    """Check out a Day Pass guest.

    Args:
        name: Day Pass name

    Returns:
        dict with updated status
    """
    doc = frappe.get_doc("Day Pass", name)
    doc.check_out()
    return {
        "day_pass": doc.name,
        "status": doc.status,
        "checked_out_at": str(doc.checked_out_at),
        "duration_hours": doc.duration_hours,
    }


# ═══════════════════════════════════════════════════════════════════════════
# Conversion
# ═══════════════════════════════════════════════════════════════════════════


@frappe.whitelist()
def convert_day_pass_to_membership(name, plan, billing_cycle="Monthly"):
    """Convert a Day Pass to a full Membership.

    The day-pass amount is applied as credit toward the first invoice.

    Args:
        name: Day Pass name
        plan: Membership Plan name
        billing_cycle: Monthly / Quarterly / Yearly

    Returns:
        dict with membership name and credit applied
    """
    doc = frappe.get_doc("Day Pass", name)
    membership_name = doc.convert_to_membership(plan, billing_cycle)

    return {
        "day_pass": doc.name,
        "membership": membership_name,
        "credit_applied": doc.membership_credit_applied,
    }


# ═══════════════════════════════════════════════════════════════════════════
# QR Scan Check-in
# ═══════════════════════════════════════════════════════════════════════════


@frappe.whitelist(allow_guest=True)
def scan_day_pass(pass_name=None, token=None):
    """Process a QR code scan for day pass check-in.

    Returns mobile-friendly HTML page with result.

    Args:
        pass_name: Day Pass name
        token: QR authentication token
    """
    if not pass_name or not token:
        return _scan_response(False, _("Invalid QR code — missing parameters"))

    if not frappe.db.exists("Day Pass", pass_name):
        return _scan_response(
            False, _("Day Pass {0} not found").format(pass_name)
        )

    doc = frappe.get_doc("Day Pass", pass_name)

    # Validate token
    if token != doc.get("qr_token"):
        return _scan_response(False, _("Invalid QR code — authentication failed"))

    # Check if already checked in
    if doc.status == "Checked In":
        return _scan_response(
            True,
            _("Already checked in at {0}").format(
                frappe.utils.format_datetime(doc.checked_in_at)
            ),
            doc=doc,
            already=True,
        )

    if doc.status not in ("Active",):
        return _scan_response(
            False,
            _("Day pass status is {0} — cannot check in").format(doc.status),
        )

    # Validate date
    if getdate(doc.pass_date) != getdate(nowdate()):
        return _scan_response(False, _("This day pass is not valid today"))

    # Perform check-in
    frappe.set_user("Administrator")
    doc.check_in()
    frappe.db.commit()

    return _scan_response(True, _("Successfully checked in!"), doc=doc)


# ═══════════════════════════════════════════════════════════════════════════
# Listing & Stats
# ═══════════════════════════════════════════════════════════════════════════


@frappe.whitelist()
def get_todays_day_passes():
    """Get all day passes for today.

    Returns:
        list of day pass summary dicts
    """
    passes = frappe.get_all(
        "Day Pass",
        filters={
            "pass_date": nowdate(),
            "docstatus": ["!=", 2],
        },
        fields=[
            "name", "guest_name", "guest_type", "pass_type",
            "status", "space", "checked_in_at", "checked_out_at",
            "net_amount", "payment_method", "is_trial",
        ],
        order_by="creation desc",
    )
    return passes


@frappe.whitelist()
def get_day_pass_stats():
    """Return day-pass KPIs for today.

    Returns:
        dict with total, checked_in, checked_out, revenue, trials
    """
    today = nowdate()

    total = frappe.db.count("Day Pass", {
        "pass_date": today, "docstatus": 1,
    })
    checked_in = frappe.db.count("Day Pass", {
        "pass_date": today, "docstatus": 1, "status": "Checked In",
    })
    checked_out = frappe.db.count("Day Pass", {
        "pass_date": today, "docstatus": 1, "status": "Checked Out",
    })
    trials = frappe.db.count("Day Pass", {
        "pass_date": today, "docstatus": 1, "is_trial": 1,
    })

    revenue = frappe.db.sql(
        """
        SELECT COALESCE(SUM(net_amount), 0) FROM `tabDay Pass`
        WHERE pass_date = %s AND docstatus = 1
        AND status NOT IN ('Cancelled', 'Expired')
        """,
        today,
    )[0][0] or 0

    return {
        "total": total,
        "checked_in": checked_in,
        "checked_out": checked_out,
        "trials": trials,
        "revenue": revenue,
    }


@frappe.whitelist()
def get_available_trial_plans():
    """Return Membership Plans that have trials enabled.

    Returns:
        list of plan dicts with trial info
    """
    plans = frappe.get_all(
        "Membership Plan",
        filters={"enable_trial": 1},
        fields=[
            "name", "plan_name", "plan_type",
            "trial_days", "trial_price",
            "monthly_price",
        ],
        order_by="plan_name asc",
    )
    return plans


# ═══════════════════════════════════════════════════════════════════════════
# Private Helpers
# ═══════════════════════════════════════════════════════════════════════════


def _get_default_rate(pass_type, space=None):
    """Get the default rate for a pass type from settings or space."""
    settings = frappe.get_cached_doc("ARKSpace Settings")

    if space:
        space_doc = frappe.get_cached_doc("Co-working Space", space)
        if pass_type in ("Full Day", "Weekend"):
            return space_doc.daily_rate or 0
        if pass_type in ("Half Day", "Evening"):
            return (space_doc.daily_rate or 0) / 2
        if pass_type == "Hourly":
            return space_doc.hourly_rate or 0

    # Fallback to settings
    return settings.get("default_day_pass_rate") or 0


def _scan_response(success, message, doc=None, already=False):
    """Return a mobile-friendly HTML page for QR scan result."""
    color = "#10b981" if success else "#ef4444"
    icon = "✓" if success else "✗"
    if already:
        color = "#f59e0b"
        icon = "ℹ"

    details_html = ""
    if doc:
        details_html = f"""
        <div class="booking-details">
            <p><strong>{_("Day Pass")}:</strong> {doc.name}</p>
            <p><strong>{_("Guest")}:</strong> {doc.guest_name}</p>
            <p><strong>{_("Space")}:</strong> {doc.space or "—"}</p>
            <p><strong>{_("Type")}:</strong> {doc.pass_type}</p>
            <p><strong>{_("Date")}:</strong> {doc.pass_date}</p>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html lang="ar" dir="auto">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ARKSpace Day Pass</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont,
                'Segoe UI', Roboto, sans-serif;
            background: #f8fafc;
            display: flex; justify-content: center;
            align-items: center; min-height: 100vh; padding: 20px;
        }}
        .card {{
            background: white; border-radius: 16px; padding: 40px;
            max-width: 400px; width: 100%; text-align: center;
            box-shadow: 0 4px 24px rgba(0,0,0,0.08);
        }}
        .icon {{
            width: 80px; height: 80px; border-radius: 50%;
            background: {color}; color: white; font-size: 40px;
            display: flex; align-items: center;
            justify-content: center; margin: 0 auto 20px;
        }}
        .message {{
            font-size: 20px; font-weight: 600;
            color: #1e293b; margin-bottom: 16px;
        }}
        .booking-details {{
            background: #f1f5f9; border-radius: 8px;
            padding: 16px; text-align: left; margin-top: 16px;
        }}
        .booking-details p {{ margin: 8px 0; font-size: 14px; color: #475569; }}
        .logo {{ margin-top: 24px; font-size: 12px; color: #94a3b8; }}
    </style>
</head>
<body>
    <div class="card">
        <div class="icon">{icon}</div>
        <div class="message">{message}</div>
        {details_html}
        <div class="logo">ARKSpace — Day Pass</div>
    </div>
</body>
</html>"""

    frappe.respond_as_web_page(
        title="ARKSpace Day Pass",
        html=html,
        http_status_code=200 if success else 400,
        fullpage=True,
    )
