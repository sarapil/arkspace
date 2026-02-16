# Copyright (c) 2026, ARKSpace Team and contributors
# For license information, please see license.txt

"""تقرير إشغال المساحات — Space Occupancy Report"""

import frappe
from frappe import _
from frappe.utils import getdate, nowdate, add_days


def execute(filters=None):
	filters = filters or {}
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart(data)
	summary = get_summary(data)
	return columns, data, None, chart, summary


def get_columns():
	return [
		{"fieldname": "space", "label": _("Space"), "fieldtype": "Link", "options": "Co-working Space", "width": 200},
		{"fieldname": "space_name", "label": _("Space Name"), "fieldtype": "Data", "width": 200},
		{"fieldname": "space_type", "label": _("Type"), "fieldtype": "Link", "options": "Space Type", "width": 130},
		{"fieldname": "branch", "label": _("Branch"), "fieldtype": "Link", "options": "Branch", "width": 130},
		{"fieldname": "capacity", "label": _("Capacity"), "fieldtype": "Int", "width": 90},
		{"fieldname": "status", "label": _("Status"), "fieldtype": "Data", "width": 110},
		{"fieldname": "bookings_count", "label": _("Bookings (Period)"), "fieldtype": "Int", "width": 130},
		{"fieldname": "hours_booked", "label": _("Hours Booked"), "fieldtype": "Float", "width": 120},
		{"fieldname": "revenue", "label": _("Revenue"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "occupancy_rate", "label": _("Occupancy %"), "fieldtype": "Percent", "width": 110},
	]


def get_data(filters):
	from_date = getdate(filters.get("from_date") or add_days(nowdate(), -30))
	to_date = getdate(filters.get("to_date") or nowdate())

	spaces = frappe.get_all(
		"Co-working Space",
		filters=_get_space_filters(filters),
		fields=["name", "space_name", "space_type", "branch", "capacity", "status"],
		order_by="space_name asc",
	)

	# Calculate total available hours in the period
	total_days = (to_date - from_date).days or 1
	total_hours = total_days * 24

	data = []
	for space in spaces:
		booking_stats = frappe.db.sql("""
			SELECT
				COUNT(*) as count,
				COALESCE(SUM(duration_hours), 0) as hours,
				COALESCE(SUM(net_amount), 0) as revenue
			FROM `tabSpace Booking`
			WHERE
				docstatus = 1
				AND space = %(space)s
				AND status NOT IN ('Cancelled', 'No Show')
				AND start_datetime >= %(from_date)s
				AND end_datetime <= %(to_date)s
		""", {"space": space.name, "from_date": from_date, "to_date": to_date}, as_dict=True)[0]

		occupancy_rate = (booking_stats.hours / total_hours * 100) if total_hours else 0

		data.append({
			"space": space.name,
			"space_name": space.space_name,
			"space_type": space.space_type,
			"branch": space.branch,
			"capacity": space.capacity,
			"status": space.status,
			"bookings_count": booking_stats.count,
			"hours_booked": round(booking_stats.hours, 1),
			"revenue": booking_stats.revenue,
			"occupancy_rate": round(occupancy_rate, 1),
		})

	return data


def _get_space_filters(filters):
	f = {}
	if filters.get("space_type"):
		f["space_type"] = filters["space_type"]
	if filters.get("branch"):
		f["branch"] = filters["branch"]
	if filters.get("status"):
		f["status"] = filters["status"]
	return f


def get_chart(data):
	if not data:
		return None

	labels = [d["space_name"] for d in data[:20]]
	occupancy = [d["occupancy_rate"] for d in data[:20]]
	revenue = [d["revenue"] for d in data[:20]]

	return {
		"data": {
			"labels": labels,
			"datasets": [
				{"name": _("Occupancy %"), "values": occupancy},
				{"name": _("Revenue"), "values": revenue},
			],
		},
		"type": "bar",
		"colors": ["#2563EB", "#C4A962"],
	}


def get_summary(data):
	if not data:
		return []

	total_spaces = len(data)
	total_revenue = sum(d["revenue"] for d in data)
	avg_occupancy = sum(d["occupancy_rate"] for d in data) / total_spaces if total_spaces else 0
	total_bookings = sum(d["bookings_count"] for d in data)

	return [
		{"value": total_spaces, "indicator": "blue", "label": _("Total Spaces"), "datatype": "Int"},
		{"value": total_bookings, "indicator": "green", "label": _("Total Bookings"), "datatype": "Int"},
		{"value": total_revenue, "indicator": "green", "label": _("Total Revenue"), "datatype": "Currency"},
		{"value": round(avg_occupancy, 1), "indicator": "orange", "label": _("Avg Occupancy %"), "datatype": "Percent"},
	]
