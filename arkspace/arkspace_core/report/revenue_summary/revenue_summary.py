# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

"""Revenue Summary Report
Aggregates revenue from bookings and memberships by period.
"""

import frappe
from frappe import _
from frappe.utils import getdate, nowdate, add_days, add_months, flt

def execute(filters=None):
	filters = filters or {}
	columns = get_columns(filters)
	data = get_data(filters)
	chart = get_chart(data, filters)
	summary = get_summary(data)
	return columns, data, None, chart, summary

def get_columns(filters):
	group_by = filters.get("group_by", "Month")
	return [
		{"fieldname": "period", "label": _(group_by), "fieldtype": "Data", "width": 150},
		{"fieldname": "booking_revenue", "label": _("Booking Revenue"), "fieldtype": "Currency", "width": 160},
		{"fieldname": "booking_count", "label": _("Bookings"), "fieldtype": "Int", "width": 100},
		{"fieldname": "membership_revenue", "label": _("Membership Revenue"), "fieldtype": "Currency", "width": 170},
		{"fieldname": "membership_count", "label": _("Memberships"), "fieldtype": "Int", "width": 110},
		{"fieldname": "total_revenue", "label": _("Total Revenue"), "fieldtype": "Currency", "width": 160},
	]

def get_data(filters):
	from_date = getdate(filters.get("from_date") or add_months(nowdate(), -12))
	to_date = getdate(filters.get("to_date") or nowdate())
	group_by = filters.get("group_by", "Month")
	if group_by not in ("Day", "Week", "Month", "Quarter", "Year"):
		group_by = "Month"

	# Use %% to escape percent signs for PyMySQL parameterized queries
	date_format = {
		"Day": "%%Y-%%m-%%d",
		"Week": "%%Y-W%%v",
		"Month": "%%Y-%%m",
		"Quarter": "CONCAT(YEAR(start_datetime), '-Q', QUARTER(start_datetime))",
		"Year": "%%Y",
	}

	if group_by in ("Quarter",):
		period_expr = date_format[group_by]
	else:
		period_expr = f"DATE_FORMAT(start_datetime, '{date_format.get(group_by, '%%Y-%%m')}')"

	# Booking revenue
	bookings = frappe.db.sql(f"""
		SELECT
			{period_expr} as period,
			COALESCE(SUM(net_amount), 0) as revenue,
			COUNT(*) as count
		FROM `tabSpace Booking`
		WHERE docstatus = 1
			AND status NOT IN ('Cancelled', 'No Show')
			AND start_datetime >= %(from_date)s
			AND start_datetime <= %(to_date)s
		GROUP BY period
		ORDER BY period ASC
	""", {"from_date": from_date, "to_date": to_date}, as_dict=True)

	# Membership revenue — use start_date for grouping
	if group_by in ("Quarter",):
		mem_period = "CONCAT(YEAR(start_date), '-Q', QUARTER(start_date))"
	else:
		fmt = date_format.get(group_by, "%%Y-%%m")
		mem_period = f"DATE_FORMAT(start_date, '{fmt}')"

	memberships = frappe.db.sql(f"""
		SELECT
			{mem_period} as period,
			COALESCE(SUM(net_amount), 0) as revenue,
			COUNT(*) as count
		FROM `tabMembership`
		WHERE docstatus = 1
			AND status NOT IN ('Cancelled')
			AND start_date >= %(from_date)s
			AND start_date <= %(to_date)s
		GROUP BY period
		ORDER BY period ASC
	""", {"from_date": from_date, "to_date": to_date}, as_dict=True)

	# Merge into combined rows
	booking_map = {b.period: b for b in bookings}
	membership_map = {m.period: m for m in memberships}
	all_periods = sorted(set(list(booking_map.keys()) + list(membership_map.keys())))

	data = []
	for period in all_periods:
		bk = booking_map.get(period, frappe._dict())
		mem = membership_map.get(period, frappe._dict())
		br = flt(bk.get("revenue", 0))
		mr = flt(mem.get("revenue", 0))
		data.append({
			"period": period,
			"booking_revenue": br,
			"booking_count": bk.get("count", 0),
			"membership_revenue": mr,
			"membership_count": mem.get("count", 0),
			"total_revenue": br + mr,
		})

	return data

def get_chart(data, filters):
	if not data:
		return None

	labels = [d["period"] for d in data]
	return {
		"data": {
			"labels": labels,
			"datasets": [
				{"name": _("Booking Revenue"), "values": [d["booking_revenue"] for d in data]},
				{"name": _("Membership Revenue"), "values": [d["membership_revenue"] for d in data]},
			],
		},
		"type": "bar",
		"colors": ["#2563EB", "#C4A962"],
		"barOptions": {"stacked": 1},
	}

def get_summary(data):
	if not data:
		return []

	total_booking = sum(d["booking_revenue"] for d in data)
	total_membership = sum(d["membership_revenue"] for d in data)
	grand_total = total_booking + total_membership

	return [
		{"value": grand_total, "indicator": "green", "label": _("Grand Total"), "datatype": "Currency"},
		{"value": total_booking, "indicator": "blue", "label": _("Bookings"), "datatype": "Currency"},
		{"value": total_membership, "indicator": "orange", "label": _("Memberships"), "datatype": "Currency"},
	]
