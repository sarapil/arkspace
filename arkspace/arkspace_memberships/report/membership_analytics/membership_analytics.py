# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

"""تحليلات العضويات — Membership Analytics Report
Breakdown of memberships by plan, status, cycle with churn and growth metrics.
"""

import frappe
from frappe import _
from frappe.utils import getdate, nowdate, add_months, flt


def execute(filters=None):
	filters = filters or {}
	view = filters.get("view", "By Plan")

	if view == "By Plan":
		return plan_view(filters)
	elif view == "By Status":
		return status_view(filters)
	elif view == "By Period":
		return period_view(filters)
	else:
		return plan_view(filters)


def plan_view(filters):
	columns = [
		{"fieldname": "plan", "label": _("Membership Plan"), "fieldtype": "Link", "options": "Membership Plan", "width": 200},
		{"fieldname": "plan_type", "label": _("Type"), "fieldtype": "Data", "width": 130},
		{"fieldname": "active", "label": _("Active"), "fieldtype": "Int", "width": 90},
		{"fieldname": "expired", "label": _("Expired"), "fieldtype": "Int", "width": 90},
		{"fieldname": "cancelled", "label": _("Cancelled"), "fieldtype": "Int", "width": 100},
		{"fieldname": "total", "label": _("Total"), "fieldtype": "Int", "width": 80},
		{"fieldname": "total_revenue", "label": _("Revenue"), "fieldtype": "Currency", "width": 150},
		{"fieldname": "avg_revenue", "label": _("Avg Revenue"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "retention_rate", "label": _("Retention %"), "fieldtype": "Percent", "width": 110},
	]

	data = frappe.db.sql("""
		SELECT
			m.membership_plan as plan,
			mp.plan_type,
			SUM(CASE WHEN m.status = 'Active' THEN 1 ELSE 0 END) as active,
			SUM(CASE WHEN m.status = 'Expired' THEN 1 ELSE 0 END) as expired,
			SUM(CASE WHEN m.status = 'Cancelled' THEN 1 ELSE 0 END) as cancelled,
			COUNT(*) as total,
			COALESCE(SUM(m.net_amount), 0) as total_revenue,
			COALESCE(AVG(m.net_amount), 0) as avg_revenue
		FROM `tabMembership` m
		LEFT JOIN `tabMembership Plan` mp ON m.membership_plan = mp.name
		WHERE m.docstatus = 1
		GROUP BY m.membership_plan, mp.plan_type
		ORDER BY total DESC
	""", as_dict=True)

	for row in data:
		non_cancelled = row.total - row.cancelled
		row["retention_rate"] = round((row.active / non_cancelled * 100) if non_cancelled else 0, 1)

	chart = {
		"data": {
			"labels": [d["plan"] for d in data],
			"datasets": [
				{"name": _("Active"), "values": [d["active"] for d in data]},
				{"name": _("Expired"), "values": [d["expired"] for d in data]},
				{"name": _("Cancelled"), "values": [d["cancelled"] for d in data]},
			],
		},
		"type": "bar",
		"colors": ["#10B981", "#6B7280", "#EF4444"],
		"barOptions": {"stacked": 1},
	}

	total_active = sum(d["active"] for d in data)
	total_rev = sum(d["total_revenue"] for d in data)
	summary = [
		{"value": total_active, "indicator": "green", "label": _("Active Memberships"), "datatype": "Int"},
		{"value": total_rev, "indicator": "blue", "label": _("Total Revenue"), "datatype": "Currency"},
	]

	return columns, data, None, chart, summary


def status_view(filters):
	columns = [
		{"fieldname": "status", "label": _("Status"), "fieldtype": "Data", "width": 150},
		{"fieldname": "count", "label": _("Count"), "fieldtype": "Int", "width": 100},
		{"fieldname": "revenue", "label": _("Revenue"), "fieldtype": "Currency", "width": 150},
		{"fieldname": "percentage", "label": _("% of Total"), "fieldtype": "Percent", "width": 110},
	]

	data = frappe.db.sql("""
		SELECT
			status,
			COUNT(*) as count,
			COALESCE(SUM(net_amount), 0) as revenue
		FROM `tabMembership`
		WHERE docstatus = 1
		GROUP BY status
		ORDER BY count DESC
	""", as_dict=True)

	total = sum(d["count"] for d in data) or 1
	for row in data:
		row["percentage"] = round(row["count"] / total * 100, 1)

	chart = {
		"data": {
			"labels": [d["status"] for d in data],
			"datasets": [{"name": _("Count"), "values": [d["count"] for d in data]}],
		},
		"type": "donut",
		"colors": ["#10B981", "#6B7280", "#EF4444", "#F59E0B", "#8B5CF6"],
	}

	return columns, data, None, chart, []


def period_view(filters):
	from_date = getdate(filters.get("from_date") or add_months(nowdate(), -12))
	to_date = getdate(filters.get("to_date") or nowdate())

	columns = [
		{"fieldname": "period", "label": _("Month"), "fieldtype": "Data", "width": 120},
		{"fieldname": "new", "label": _("New"), "fieldtype": "Int", "width": 80},
		{"fieldname": "renewed", "label": _("Renewed"), "fieldtype": "Int", "width": 90},
		{"fieldname": "expired", "label": _("Expired"), "fieldtype": "Int", "width": 90},
		{"fieldname": "cancelled", "label": _("Cancelled"), "fieldtype": "Int", "width": 100},
		{"fieldname": "net_growth", "label": _("Net Growth"), "fieldtype": "Int", "width": 100},
		{"fieldname": "revenue", "label": _("Revenue"), "fieldtype": "Currency", "width": 130},
	]

	new_data = frappe.db.sql("""
		SELECT
			DATE_FORMAT(start_date, '%%Y-%%m') as period,
			COUNT(*) as new_count,
			COALESCE(SUM(net_amount), 0) as revenue
		FROM `tabMembership`
		WHERE docstatus = 1
			AND start_date >= %(from_date)s
			AND start_date <= %(to_date)s
		GROUP BY period
		ORDER BY period ASC
	""", {"from_date": from_date, "to_date": to_date}, as_dict=True)

	expired_data = frappe.db.sql("""
		SELECT
			DATE_FORMAT(end_date, '%%Y-%%m') as period,
			SUM(CASE WHEN status = 'Expired' THEN 1 ELSE 0 END) as expired,
			SUM(CASE WHEN status = 'Cancelled' THEN 1 ELSE 0 END) as cancelled
		FROM `tabMembership`
		WHERE docstatus = 1
			AND end_date >= %(from_date)s
			AND end_date <= %(to_date)s
		GROUP BY period
	""", {"from_date": from_date, "to_date": to_date}, as_dict=True)

	new_map = {d.period: d for d in new_data}
	exp_map = {d.period: d for d in expired_data}
	all_periods = sorted(set(list(new_map.keys()) + list(exp_map.keys())))

	data = []
	for period in all_periods:
		n = new_map.get(period, frappe._dict())
		e = exp_map.get(period, frappe._dict())
		new_count = n.get("new_count", 0)
		expired = e.get("expired", 0)
		cancelled = e.get("cancelled", 0)
		data.append({
			"period": period,
			"new": new_count,
			"renewed": 0,  # TODO: track renewals separately
			"expired": expired,
			"cancelled": cancelled,
			"net_growth": new_count - expired - cancelled,
			"revenue": n.get("revenue", 0),
		})

	chart = {
		"data": {
			"labels": [d["period"] for d in data],
			"datasets": [
				{"name": _("New"), "values": [d["new"] for d in data]},
				{"name": _("Expired"), "values": [-d["expired"] for d in data]},
				{"name": _("Net Growth"), "values": [d["net_growth"] for d in data]},
			],
		},
		"type": "bar",
		"colors": ["#10B981", "#EF4444", "#2563EB"],
	}

	return columns, data, None, chart, []
