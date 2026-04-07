# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

"""ARKSpace — Smart Analytics Engine

Provides occupancy heatmaps, revenue trends, forecasting, member analytics,
space utilization, booking patterns, and period-over-period comparisons.
"""

import frappe  # noqa: I001
from frappe import _
from frappe.utils import (
    add_days,
    cint,
    flt,
    get_first_day,
    getdate,
    nowdate,
)


# ──────────────────────── Daily Snapshot ────────────────────────────────

def capture_daily_snapshot():
    """Capture daily analytics for each branch + overall.

    Called by scheduler (daily). Creates Analytics Snapshot docs.
    """
    today = getdate(nowdate())

    # Get all active branches
    branches = frappe.get_all("Branch", pluck="name")
    branch_list = branches + [None]  # None = all-branches aggregate

    for branch in branch_list:
        try:
            _create_snapshot(today, branch)
        except Exception:
            frappe.log_error(
                title=f"Analytics Snapshot Error ({branch or 'ALL'})",
                message=frappe.get_traceback(),
            )

    frappe.db.commit()
    frappe.logger("arkspace").info(
        f"Analytics snapshots captured for {today}: {len(branch_list)} branch(es)"
    )


def _create_snapshot(snapshot_date, branch=None):
    """Create a single Analytics Snapshot for a date + branch."""
    # Skip if already captured
    if frappe.db.exists("Analytics Snapshot", {
        "snapshot_date": snapshot_date,
        "branch": branch or "",
        "period_type": "Daily",
    }):
        return

    bf = {"branch": branch} if branch else {}  # branch filter dict

    # ── Spaces ──
    total_spaces = frappe.db.count("Co-working Space", bf) or 0
    occupied = frappe.db.count("Co-working Space", {**bf, "status": "Occupied"}) or 0
    available = frappe.db.count("Co-working Space", {**bf, "status": "Available"}) or 0
    maintenance = frappe.db.count("Co-working Space", {**bf, "status": "Maintenance"}) or 0
    reserved = frappe.db.count("Co-working Space", {**bf, "status": "Reserved"}) or 0
    occupancy_rate = round((occupied / total_spaces * 100) if total_spaces else 0, 1)

    # ── Bookings ──
    day_start = f"{snapshot_date} 00:00:00"
    day_end = f"{snapshot_date} 23:59:59"

    booking_filters = {
        "docstatus": 1,
        "start_datetime": ["between", [day_start, day_end]],
    }
    if branch:
        booking_filters["space"] = [
            "in",
            frappe.get_all("Co-working Space", {"branch": branch}, pluck="name") or ["__none__"],
        ]

    total_bookings = frappe.db.count("Space Booking", booking_filters) or 0
    new_bookings = frappe.db.count("Space Booking", {
        **booking_filters, "creation": ["between", [day_start, day_end]],
    }) or 0
    cancelled = frappe.db.count("Space Booking", {
        **booking_filters, "status": "Cancelled",
    }) or 0
    no_shows = frappe.db.count("Space Booking", {
        **booking_filters, "status": "No Show",
    }) or 0
    checked_in = frappe.db.count("Space Booking", {
        **booking_filters, "status": ["in", ["Checked In", "Checked Out"]],
    }) or 0

    # Avg booking duration
    avg_dur_result = frappe.db.sql("""
        SELECT AVG(TIMESTAMPDIFF(MINUTE, start_datetime, end_datetime)) / 60
        FROM `tabSpace Booking`
        WHERE docstatus = 1
          AND start_datetime BETWEEN %s AND %s
          AND status NOT IN ('Cancelled', 'No Show')
    """, (day_start, day_end))
    avg_duration = flt(avg_dur_result[0][0], 1) if avg_dur_result and avg_dur_result[0][0] else 0

    # ── Members ──
    active_members = frappe.db.count("Membership", {
        "docstatus": 1,
        "status": "Active",
        **({"branch": branch} if branch else {}),
    }) or 0

    new_members = frappe.db.count("Membership", {
        "docstatus": 1,
        "creation": ["between", [day_start, day_end]],
        **({"branch": branch} if branch else {}),
    }) or 0

    churned = frappe.db.count("Membership", {
        "docstatus": 1,
        "status": "Expired",
        "end_date": snapshot_date,
        **({"branch": branch} if branch else {}),
    }) or 0

    prev_active = active_members + churned
    retention = round(((prev_active - churned) / prev_active * 100) if prev_active else 100, 1)

    # ── Revenue (from Sales Invoice) ──
    revenue_data = _get_revenue_for_date(snapshot_date, branch)

    # ── Day Passes & Visitors ──
    dp_count = frappe.db.count("Day Pass", {
        "docstatus": 1,
        "pass_date": snapshot_date,
        **({"branch": branch} if branch else {}),
    }) or 0

    vis_count = frappe.db.count("Visitor Log", {
        "visit_date": snapshot_date,
        **({"branch": branch} if branch else {}),
    }) or 0

    trial_conv = frappe.db.count("Day Pass", {
        "docstatus": 1,
        "pass_date": snapshot_date,
        "converted_to_membership": ["!=", ""],
        **({"branch": branch} if branch else {}),
    }) or 0

    # ── Patterns ──
    peak = _get_peak_hour(snapshot_date, branch)
    popular_st = _get_popular_space_type(snapshot_date, branch)
    popular_bt = _get_popular_booking_type(snapshot_date, branch)

    # ── Create Snapshot ──
    snap = frappe.get_doc({
        "doctype": "Analytics Snapshot",
        "snapshot_date": snapshot_date,
        "branch": branch or "",
        "period_type": "Daily",
        "total_spaces": total_spaces,
        "occupied_spaces": occupied,
        "available_spaces": available,
        "maintenance_spaces": maintenance,
        "reserved_spaces": reserved,
        "occupancy_rate": occupancy_rate,
        "total_bookings": total_bookings,
        "new_bookings": new_bookings,
        "cancelled_bookings": cancelled,
        "no_shows": no_shows,
        "checked_in_count": checked_in,
        "avg_booking_duration": avg_duration,
        "active_members": active_members,
        "new_members": new_members,
        "churned_members": churned,
        "retention_rate": retention,
        "total_revenue": revenue_data.get("total", 0),
        "booking_revenue": revenue_data.get("booking", 0),
        "membership_revenue": revenue_data.get("membership", 0),
        "day_pass_revenue": revenue_data.get("day_pass", 0),
        "other_revenue": revenue_data.get("other", 0),
        "avg_revenue_per_booking": (
            flt(revenue_data.get("booking", 0) / total_bookings, 2)
            if total_bookings else 0
        ),
        "day_pass_count": dp_count,
        "visitor_count": vis_count,
        "trial_conversions": trial_conv,
        "peak_hour": peak,
        "popular_space_type": popular_st,
        "popular_booking_type": popular_bt,
    })
    snap.flags.ignore_permissions = True
    snap.insert()

    # Publish for connected dashboards
    frappe.publish_realtime("analytics_snapshot_created", {
        "date": str(snapshot_date),
        "branch": branch or "ALL",
        "occupancy_rate": occupancy_rate,
        "total_revenue": revenue_data.get("total", 0),
    })


# ──────────────────────── API Endpoints ────────────────────────────────

@frappe.whitelist()
def get_occupancy_heatmap(branch=None, from_date=None, to_date=None):
    """Return hourly occupancy by day-of-week (7×24 matrix).

    Each cell = average number of active bookings at that hour on that weekday.
    """
    frappe.only_for(["ARKSpace User", "ARKSpace Manager", "System Manager"])

    from_date = getdate(from_date or add_days(nowdate(), -30))
    to_date = getdate(to_date or nowdate())

    branch_condition = ""
    params = [from_date, to_date]
    if branch:
        space_names = frappe.get_all(
            "Co-working Space", {"branch": branch}, pluck="name",
        )
        if not space_names:
            return {"heatmap": [[0] * 24 for _ in range(7)], "max_value": 0}
        branch_condition = f"AND sb.space IN ({','.join(['%s'] * len(space_names))})"
        params.extend(space_names)

    # Get bookings with their time ranges
    rows = frappe.db.sql(f"""
        SELECT
            DAYOFWEEK(sb.start_datetime) AS dow,
            HOUR(sb.start_datetime) AS start_hour,
            HOUR(sb.end_datetime) AS end_hour,
            DATE(sb.start_datetime) AS booking_date
        FROM `tabSpace Booking` sb
        WHERE sb.docstatus = 1
          AND sb.start_datetime >= %s
          AND sb.start_datetime <= %s
          AND sb.status NOT IN ('Cancelled', 'No Show')
          {branch_condition}
    """, params, as_dict=True)

    # Build heatmap: weekday (0=Sun) × hour (0-23)
    heatmap = [[0] * 24 for _ in range(7)]
    date_counts = {}

    for r in rows:
        dow = cint(r.dow) - 1  # MySQL DAYOFWEEK: 1=Sun → 0-indexed
        start_h = cint(r.start_hour)
        end_h = max(cint(r.end_hour), start_h + 1)
        date_key = str(r.booking_date)

        for h in range(start_h, min(end_h, 24)):
            heatmap[dow][h] += 1

        date_counts.setdefault(dow, set()).add(date_key)

    # Average by number of unique dates per weekday
    for dow in range(7):
        num_dates = len(date_counts.get(dow, set())) or 1
        for h in range(24):
            heatmap[dow][h] = round(heatmap[dow][h] / num_dates, 1)

    max_val = max(max(row) for row in heatmap) if any(any(r) for r in heatmap) else 0

    return {
        "heatmap": heatmap,
        "max_value": max_val,
        "days": [_("Sun"), _("Mon"), _("Tue"), _("Wed"), _("Thu"), _("Fri"), _("Sat")],
        "from_date": str(from_date),
        "to_date": str(to_date),
    }


@frappe.whitelist()
def get_revenue_trends(branch=None, period="monthly", from_date=None, to_date=None):
    """Return revenue data points grouped by period.

    Args:
        period: 'daily', 'weekly', or 'monthly'
    """
    frappe.only_for(["ARKSpace User", "ARKSpace Manager", "System Manager"])

    if period not in ("daily", "weekly", "monthly"):
        period = "monthly"

    from_date = getdate(from_date or add_days(nowdate(), -90))
    to_date = getdate(to_date or nowdate())

    if period == "daily":
        group_expr = "DATE(posting_date)"
        label_expr = "DATE_FORMAT(posting_date, '%%Y-%%m-%%d')"
    elif period == "weekly":
        group_expr = "YEARWEEK(posting_date, 1)"
        label_expr = "DATE_FORMAT(MIN(posting_date), '%%Y-W%%v')"
    else:  # monthly
        group_expr = "DATE_FORMAT(posting_date, '%%Y-%%m')"
        label_expr = "DATE_FORMAT(posting_date, '%%Y-%%m')"

    branch_join = ""
    params = [from_date, to_date]
    if branch:
        branch_join = """
            AND (si.arkspace_booking IN (
                SELECT sb.name FROM `tabSpace Booking` sb
                JOIN `tabCo-working Space` cs ON sb.space = cs.name
                WHERE cs.branch = %s
            ) OR 1=1)
        """
        params.append(branch)

    rows = frappe.db.sql(f"""
        SELECT
            {label_expr} AS period_label,
            SUM(si.grand_total) AS total_revenue,
            SUM(CASE WHEN si.arkspace_booking IS NOT NULL AND si.arkspace_booking != ''
                     THEN si.grand_total ELSE 0 END) AS booking_rev,
            SUM(CASE WHEN si.remarks LIKE '%%Membership%%'
                     THEN si.grand_total ELSE 0 END) AS membership_rev,
            SUM(CASE WHEN si.remarks LIKE '%%Day Pass%%'
                     THEN si.grand_total ELSE 0 END) AS day_pass_rev,
            COUNT(*) AS invoice_count
        FROM `tabSales Invoice` si
        WHERE si.docstatus = 1
          AND si.posting_date BETWEEN %s AND %s
          AND (si.remarks LIKE '%%ARKSpace%%' OR si.remarks LIKE '%%Space Booking%%'
               OR si.remarks LIKE '%%Membership%%' OR si.remarks LIKE '%%Day Pass%%'
               OR si.arkspace_booking IS NOT NULL)
          {branch_join}
        GROUP BY {group_expr}
        ORDER BY {group_expr}
    """, params, as_dict=True)

    return {
        "labels": [r.period_label for r in rows],
        "total_revenue": [flt(r.total_revenue, 2) for r in rows],
        "booking_revenue": [flt(r.booking_rev, 2) for r in rows],
        "membership_revenue": [flt(r.membership_rev, 2) for r in rows],
        "day_pass_revenue": [flt(r.day_pass_rev, 2) for r in rows],
        "invoice_count": [cint(r.invoice_count) for r in rows],
        "period": period,
    }


@frappe.whitelist()
def get_revenue_forecast(branch=None, months_ahead=3):
    """Simple linear regression forecast based on monthly revenue history.

    Uses last 12 months of Analytics Snapshot data to project future revenue.
    """
    frappe.only_for(["ARKSpace User", "ARKSpace Manager", "System Manager"])

    months_ahead = cint(months_ahead) or 3
    from_date = add_days(get_first_day(nowdate()), -365)

    filters = {
        "snapshot_date": [">=", from_date],
        "period_type": "Daily",
    }
    if branch:
        filters["branch"] = branch

    snapshots = frappe.get_all("Analytics Snapshot", filters=filters, fields=[
        "snapshot_date", "total_revenue",
    ], order_by="snapshot_date asc")

    if len(snapshots) < 14:
        return {"forecast": [], "message": _("Not enough data for forecasting (need 14+ days)")}

    # Aggregate to monthly
    monthly = {}
    for s in snapshots:
        key = str(s.snapshot_date)[:7]  # YYYY-MM
        monthly.setdefault(key, 0)
        monthly[key] += flt(s.total_revenue)

    months = sorted(monthly.keys())
    values = [monthly[m] for m in months]

    if len(values) < 3:
        return {"forecast": [], "message": _("Need at least 3 months of data")}

    # Linear regression: y = mx + b
    n = len(values)
    x_vals = list(range(n))
    x_mean = sum(x_vals) / n
    y_mean = sum(values) / n

    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_vals, values))
    denominator = sum((x - x_mean) ** 2 for x in x_vals)

    if denominator == 0:
        slope = 0
    else:
        slope = numerator / denominator
    intercept = y_mean - slope * x_mean

    # Generate forecast
    forecast = []
    last_month_date = getdate(f"{months[-1]}-01")
    for i in range(1, months_ahead + 1):
        forecast_x = n + i - 1
        predicted = max(0, slope * forecast_x + intercept)
        forecast_date = add_days(get_first_day(last_month_date), 30 * i)
        forecast.append({
            "month": str(forecast_date)[:7],
            "predicted_revenue": round(predicted, 2),
            "confidence": max(0, round(100 - (i * 10), 1)),  # Decreasing confidence
        })

    return {
        "historical": [{"month": m, "revenue": round(v, 2)} for m, v in zip(months, values)],
        "forecast": forecast,
        "trend": "up" if slope > 0 else "down" if slope < 0 else "flat",
        "monthly_growth": round(slope, 2),
    }


@frappe.whitelist()
def get_member_analytics(branch=None, from_date=None, to_date=None):
    """Member growth, churn, retention, and composition analytics."""
    frappe.only_for(["ARKSpace User", "ARKSpace Manager", "System Manager"])

    from_date = getdate(from_date or add_days(nowdate(), -90))
    to_date = getdate(to_date or nowdate())

    bf = {"branch": branch} if branch else {}

    # Current state
    active = frappe.db.count("Membership", {"docstatus": 1, "status": "Active", **bf}) or 0
    total_ever = frappe.db.count("Membership", {"docstatus": 1, **bf}) or 0
    expired = frappe.db.count("Membership", {"docstatus": 1, "status": "Expired", **bf}) or 0

    # Growth over period
    growth_params = [from_date, to_date]
    branch_filter = ""
    if branch:
        branch_filter = "AND branch = %s"
        growth_params.append(branch)

    growth_data = frappe.db.sql("""
        SELECT DATE_FORMAT(creation, '%%Y-%%m') AS month,
               COUNT(*) AS new_members
        FROM `tabMembership`
        WHERE docstatus = 1 AND creation BETWEEN %s AND %s
          {branch_filter}
        GROUP BY DATE_FORMAT(creation, '%%Y-%%m')
        ORDER BY month
    """.format(branch_filter=branch_filter), growth_params, as_dict=True)

    # Churn over period
    churn_params = [from_date, to_date]
    if branch:
        churn_params.append(branch)

    churn_data = frappe.db.sql("""
        SELECT DATE_FORMAT(end_date, '%%Y-%%m') AS month,
               COUNT(*) AS churned
        FROM `tabMembership`
        WHERE docstatus = 1 AND status = 'Expired'
          AND end_date BETWEEN %s AND %s
          {branch_filter}
        GROUP BY DATE_FORMAT(end_date, '%%Y-%%m')
        ORDER BY month
    """.format(branch_filter=branch_filter), churn_params, as_dict=True)

    # Plan distribution
    plan_params = [branch] if branch else []
    plan_dist = frappe.db.sql("""
        SELECT membership_plan, COUNT(*) AS count
        FROM `tabMembership`
        WHERE docstatus = 1 AND status = 'Active'
          {branch_filter}
        GROUP BY membership_plan
        ORDER BY count DESC
    """.format(branch_filter=branch_filter), plan_params, as_dict=True)

    # Billing cycle distribution
    cycle_params = [branch] if branch else []
    cycle_dist = frappe.db.sql("""
        SELECT billing_cycle, COUNT(*) AS count
        FROM `tabMembership`
        WHERE docstatus = 1 AND status = 'Active'
          {branch_filter}
        GROUP BY billing_cycle
        ORDER BY count DESC
    """.format(branch_filter=branch_filter), cycle_params, as_dict=True)

    retention_rate = round(((total_ever - expired) / total_ever * 100) if total_ever else 100, 1)

    return {
        "active_members": active,
        "total_ever": total_ever,
        "expired": expired,
        "retention_rate": retention_rate,
        "growth": [{"month": r.month, "new_members": r.new_members} for r in growth_data],
        "churn": [{"month": r.month, "churned": r.churned} for r in churn_data],
        "plan_distribution": [{"plan": r.membership_plan, "count": r.count} for r in plan_dist],
        "cycle_distribution": [{"cycle": r.billing_cycle, "count": r.count} for r in cycle_dist],
    }


@frappe.whitelist()
def get_space_utilization(branch=None, from_date=None, to_date=None):
    """Per-space utilization stats over a period."""
    frappe.only_for(["ARKSpace User", "ARKSpace Manager", "System Manager"])

    from_date = getdate(from_date or add_days(nowdate(), -30))
    to_date = getdate(to_date or nowdate())

    bf = ""
    params = [from_date, to_date]
    if branch:
        bf = "AND cs.branch = %s"
        params.append(branch)

    rows = frappe.db.sql(f"""
        SELECT
            cs.name AS space,
            cs.space_name,
            cs.space_type,
            cs.branch,
            cs.capacity,
            COUNT(sb.name) AS total_bookings,
            SUM(CASE WHEN sb.status = 'Checked In' THEN 1
                     WHEN sb.status = 'Checked Out' THEN 1 ELSE 0 END) AS actual_uses,
            AVG(TIMESTAMPDIFF(MINUTE, sb.start_datetime, sb.end_datetime)) / 60 AS avg_hours,
            SUM(sb.total_amount) AS total_revenue,
            COUNT(DISTINCT DATE(sb.start_datetime)) AS active_days
        FROM `tabCo-working Space` cs
        LEFT JOIN `tabSpace Booking` sb
            ON sb.space = cs.name
            AND sb.docstatus = 1
            AND sb.start_datetime BETWEEN %s AND %s
            AND sb.status NOT IN ('Cancelled')
        WHERE 1=1 {bf}
        GROUP BY cs.name
        ORDER BY total_bookings DESC
    """, params, as_dict=True)

    total_days = max((getdate(to_date) - getdate(from_date)).days, 1)

    for r in rows:
        r["avg_hours"] = flt(r.get("avg_hours"), 1)
        r["total_revenue"] = flt(r.get("total_revenue"), 2)
        r["utilization_rate"] = round(
            (cint(r.get("active_days")) / total_days * 100), 1,
        )

    return {
        "spaces": rows,
        "total_spaces": len(rows),
        "from_date": str(from_date),
        "to_date": str(to_date),
    }


@frappe.whitelist()
def get_dashboard_kpis(branch=None):
    """Real-time KPI summary for dashboard cards."""
    frappe.only_for(["ARKSpace User", "ARKSpace Manager", "System Manager"])

    today = getdate(nowdate())
    bf = {"branch": branch} if branch else {}

    total_spaces = frappe.db.count("Co-working Space", bf) or 0
    occupied = frappe.db.count("Co-working Space", {**bf, "status": "Occupied"}) or 0
    available = frappe.db.count("Co-working Space", {**bf, "status": "Available"}) or 0

    # Today's bookings
    day_start = f"{today} 00:00:00"
    day_end = f"{today} 23:59:59"

    todays_bookings = frappe.db.sql("""
        SELECT COUNT(*) FROM `tabSpace Booking`
        WHERE docstatus = 1
          AND start_datetime BETWEEN %s AND %s
          AND status NOT IN ('Cancelled', 'No Show')
    """, (day_start, day_end))[0][0] or 0

    checked_in = frappe.db.count("Space Booking", {
        "docstatus": 1, "status": "Checked In",
    }) or 0

    active_members = frappe.db.count("Membership", {
        "docstatus": 1, "status": "Active", **bf,
    }) or 0

    # This month revenue
    month_start = get_first_day(today)
    month_revenue = frappe.db.sql("""
        SELECT COALESCE(SUM(grand_total), 0)
        FROM `tabSales Invoice`
        WHERE docstatus = 1
          AND posting_date BETWEEN %s AND %s
          AND (remarks LIKE '%%ARKSpace%%' OR remarks LIKE '%%Space Booking%%'
               OR remarks LIKE '%%Membership%%' OR remarks LIKE '%%Day Pass%%'
               OR arkspace_booking IS NOT NULL)
    """, (month_start, today))[0][0] or 0

    # Day passes today
    day_passes_today = frappe.db.count("Day Pass", {
        "docstatus": 1, "pass_date": today, **bf,
    }) or 0

    # Visitors today
    visitors_today = frappe.db.count("Visitor Log", {
        "visit_date": today, **bf,
    }) or 0

    # Week over week booking change
    last_week_start = add_days(today, -13)
    last_week_end = add_days(today, -7)
    this_week_start = add_days(today, -6)

    this_week_bookings = frappe.db.sql("""
        SELECT COUNT(*) FROM `tabSpace Booking`
        WHERE docstatus = 1
          AND start_datetime >= %s AND start_datetime <= %s
          AND status NOT IN ('Cancelled')
    """, (this_week_start, day_end))[0][0] or 0

    last_week_bookings = frappe.db.sql("""
        SELECT COUNT(*) FROM `tabSpace Booking`
        WHERE docstatus = 1
          AND start_datetime >= %s AND start_datetime <= %s
          AND status NOT IN ('Cancelled')
    """, (last_week_start, last_week_end))[0][0] or 0

    wow_change = (
        round(((this_week_bookings - last_week_bookings) / last_week_bookings * 100), 1)
        if last_week_bookings else 0
    )

    return {
        "total_spaces": total_spaces,
        "occupied": occupied,
        "available": available,
        "occupancy_rate": round((occupied / total_spaces * 100) if total_spaces else 0, 1),
        "todays_bookings": todays_bookings,
        "checked_in": checked_in,
        "active_members": active_members,
        "month_revenue": flt(month_revenue, 2),
        "day_passes_today": day_passes_today,
        "visitors_today": visitors_today,
        "wow_booking_change": wow_change,
    }


@frappe.whitelist()
def get_booking_patterns(branch=None, from_date=None, to_date=None):
    """Booking patterns: peak hours, popular spaces, duration distribution."""
    frappe.only_for(["ARKSpace User", "ARKSpace Manager", "System Manager"])

    from_date = getdate(from_date or add_days(nowdate(), -30))
    to_date = getdate(to_date or nowdate())

    bf = ""
    params = [from_date, to_date]
    if branch:
        bf = """AND sb.space IN (
            SELECT name FROM `tabCo-working Space` WHERE branch = %s
        )"""
        params.append(branch)

    # Hourly distribution
    hourly = frappe.db.sql(f"""
        SELECT HOUR(start_datetime) AS hour, COUNT(*) AS count
        FROM `tabSpace Booking` sb
        WHERE docstatus = 1
          AND DATE(start_datetime) BETWEEN %s AND %s
          AND status NOT IN ('Cancelled')
          {bf}
        GROUP BY HOUR(start_datetime)
        ORDER BY hour
    """, params, as_dict=True)

    # Day-of-week distribution
    daily = frappe.db.sql(f"""
        SELECT DAYOFWEEK(start_datetime) AS dow, COUNT(*) AS count
        FROM `tabSpace Booking` sb
        WHERE docstatus = 1
          AND DATE(start_datetime) BETWEEN %s AND %s
          AND status NOT IN ('Cancelled')
          {bf}
        GROUP BY DAYOFWEEK(start_datetime)
        ORDER BY dow
    """, params, as_dict=True)

    # Booking type distribution
    types = frappe.db.sql(f"""
        SELECT booking_type, COUNT(*) AS count
        FROM `tabSpace Booking` sb
        WHERE docstatus = 1
          AND DATE(start_datetime) BETWEEN %s AND %s
          AND status NOT IN ('Cancelled')
          {bf}
        GROUP BY booking_type
        ORDER BY count DESC
    """, params, as_dict=True)

    # Top spaces
    top_spaces = frappe.db.sql(f"""
        SELECT sb.space, cs.space_name, COUNT(*) AS bookings
        FROM `tabSpace Booking` sb
        JOIN `tabCo-working Space` cs ON sb.space = cs.name
        WHERE sb.docstatus = 1
          AND DATE(sb.start_datetime) BETWEEN %s AND %s
          AND sb.status NOT IN ('Cancelled')
          {bf}
        GROUP BY sb.space
        ORDER BY bookings DESC
        LIMIT 10
    """, params, as_dict=True)

    day_names = [_("Sun"), _("Mon"), _("Tue"), _("Wed"), _("Thu"), _("Fri"), _("Sat")]
    hourly_data = [0] * 24
    for r in hourly:
        hourly_data[cint(r.hour)] = cint(r.count)

    daily_data = [0] * 7
    for r in daily:
        daily_data[cint(r.dow) - 1] = cint(r.count)

    return {
        "hourly": {"labels": [f"{h}:00" for h in range(24)], "values": hourly_data},
        "daily": {"labels": day_names, "values": daily_data},
        "booking_types": [{"type": r.booking_type, "count": r.count} for r in types],
        "top_spaces": [{"space": r.space, "name": r.space_name, "bookings": r.bookings}
                       for r in top_spaces],
    }


@frappe.whitelist()
def get_comparison_report(
    period1_start, period1_end, period2_start, period2_end, branch=None,
):
    """Compare two periods side-by-side."""
    frappe.only_for(["ARKSpace User", "ARKSpace Manager", "System Manager"])

    def _period_stats(start, end):
        start = getdate(start)
        end = getdate(end)
        bf = {"branch": branch} if branch else {}

        bookings = frappe.db.sql("""
            SELECT COUNT(*) FROM `tabSpace Booking`
            WHERE docstatus = 1
              AND DATE(start_datetime) BETWEEN %s AND %s
              AND status NOT IN ('Cancelled')
        """, (start, end))[0][0] or 0

        revenue = frappe.db.sql("""
            SELECT COALESCE(SUM(grand_total), 0)
            FROM `tabSales Invoice`
            WHERE docstatus = 1 AND posting_date BETWEEN %s AND %s
              AND (remarks LIKE '%%ARKSpace%%' OR remarks LIKE '%%Membership%%'
                   OR remarks LIKE '%%Day Pass%%' OR arkspace_booking IS NOT NULL)
        """, (start, end))[0][0] or 0

        new_members = frappe.db.count("Membership", {
            "docstatus": 1,
            "creation": ["between", [f"{start} 00:00:00", f"{end} 23:59:59"]],
            **bf,
        }) or 0

        day_passes = frappe.db.count("Day Pass", {
            "docstatus": 1,
            "pass_date": ["between", [start, end]],
            **bf,
        }) or 0

        visitors = frappe.db.count("Visitor Log", {
            "visit_date": ["between", [start, end]],
            **bf,
        }) or 0

        return {
            "bookings": bookings,
            "revenue": flt(revenue, 2),
            "new_members": new_members,
            "day_passes": day_passes,
            "visitors": visitors,
        }

    p1 = _period_stats(period1_start, period1_end)
    p2 = _period_stats(period2_start, period2_end)

    # Calculate changes
    changes = {}
    for key in p1:
        old_val = p1[key]
        new_val = p2[key]
        if old_val:
            changes[key] = round(((new_val - old_val) / old_val * 100), 1)
        else:
            changes[key] = 100 if new_val else 0

    return {
        "period1": {"start": str(period1_start), "end": str(period1_end), **p1},
        "period2": {"start": str(period2_start), "end": str(period2_end), **p2},
        "changes": changes,
    }


# ──────────────────────── Helpers ──────────────────────────────────────

def _get_revenue_for_date(date, branch=None):
    """Get revenue breakdown for a specific date."""
    try:
        row = frappe.db.sql("""
            SELECT
                COALESCE(SUM(grand_total), 0) AS total,
                COALESCE(SUM(CASE WHEN arkspace_booking IS NOT NULL
                    AND arkspace_booking != '' THEN grand_total ELSE 0 END), 0) AS booking,
                COALESCE(SUM(CASE WHEN remarks LIKE '%%Membership%%'
                    THEN grand_total ELSE 0 END), 0) AS membership,
                COALESCE(SUM(CASE WHEN remarks LIKE '%%Day Pass%%'
                    THEN grand_total ELSE 0 END), 0) AS day_pass
            FROM `tabSales Invoice`
            WHERE docstatus = 1 AND posting_date = %s
              AND (remarks LIKE '%%ARKSpace%%' OR remarks LIKE '%%Membership%%'
                   OR remarks LIKE '%%Day Pass%%' OR remarks LIKE '%%Space Booking%%'
                   OR arkspace_booking IS NOT NULL)
        """, (date,), as_dict=True)

        if row:
            r = row[0]
            other = flt(r.total) - flt(r.booking) - flt(r.membership) - flt(r.day_pass)
            return {
                "total": flt(r.total, 2),
                "booking": flt(r.booking, 2),
                "membership": flt(r.membership, 2),
                "day_pass": flt(r.day_pass, 2),
                "other": flt(max(0, other), 2),
            }
    except Exception:
        pass

    return {"total": 0, "booking": 0, "membership": 0, "day_pass": 0, "other": 0}


def _get_peak_hour(date, branch=None):
    """Get the busiest hour of the day."""
    row = frappe.db.sql("""
        SELECT HOUR(start_datetime) AS h, COUNT(*) AS c
        FROM `tabSpace Booking`
        WHERE docstatus = 1 AND DATE(start_datetime) = %s
          AND status NOT IN ('Cancelled', 'No Show')
        GROUP BY HOUR(start_datetime)
        ORDER BY c DESC
        LIMIT 1
    """, (date,), as_dict=True)
    return cint(row[0].h) if row else 0


def _get_popular_space_type(date, branch=None):
    """Get most popular space type for the day."""
    row = frappe.db.sql("""
        SELECT cs.space_type, COUNT(*) AS c
        FROM `tabSpace Booking` sb
        JOIN `tabCo-working Space` cs ON sb.space = cs.name
        WHERE sb.docstatus = 1 AND DATE(sb.start_datetime) = %s
          AND sb.status NOT IN ('Cancelled', 'No Show')
        GROUP BY cs.space_type
        ORDER BY c DESC
        LIMIT 1
    """, (date,), as_dict=True)
    return row[0].space_type if row else ""


def _get_popular_booking_type(date, branch=None):
    """Get most popular booking type for the day."""
    row = frappe.db.sql("""
        SELECT booking_type, COUNT(*) AS c
        FROM `tabSpace Booking`
        WHERE docstatus = 1 AND DATE(start_datetime) = %s
          AND status NOT IN ('Cancelled', 'No Show')
        GROUP BY booking_type
        ORDER BY c DESC
        LIMIT 1
    """, (date,), as_dict=True)
    return row[0].booking_type if row else ""
