"""ARKSpace Floor Plan — API
عرض مخطط الطابق — واجهة برمجة التطبيقات
"""

import frappe
from frappe import _


@frappe.whitelist()
def get_floor_plan_data(branch=None, floor=None):
	"""Return all spaces grouped by floor for the floor plan view.

	Args:
		branch: Optional filter by branch
		floor: Optional filter by floor

	Returns:
		dict with floors list, each containing spaces with status
	"""
	frappe.only_for(["ARKSpace User", "ARKSpace Manager", "System Manager"])

	filters = {}
	if branch:
		filters["branch"] = branch
	if floor:
		filters["floor"] = floor

	spaces = frappe.get_all(
		"Co-working Space",
		filters=filters,
		fields=[
			"name", "space_name", "space_type", "branch", "floor",
			"space_number", "capacity", "area_sqm", "status",
			"current_member", "hourly_rate", "daily_rate", "monthly_rate",
			"main_image",
		],
		order_by="floor asc, space_number asc, space_name asc",
	)

	# Group by floor
	floor_map = {}
	for s in spaces:
		fl = s.floor or _("Unassigned")
		if fl not in floor_map:
			floor_map[fl] = []

		# Get current booking info if occupied
		if s.status == "Occupied":
			booking = frappe.db.get_value(
				"Space Booking",
				{
					"space": s.name,
					"docstatus": 1,
					"status": "Checked In",
				},
				["name", "member", "start_datetime", "end_datetime"],
				as_dict=True,
			)
			s["current_booking"] = booking
			if booking:
				s["member_name"] = frappe.db.get_value(
					"Customer", booking.member, "customer_name"
				)

		# Get space type icon
		s["type_icon"] = _get_type_icon(s.space_type)
		floor_map[fl].append(s)

	# Build result
	floors = []
	for fl_name in sorted(floor_map.keys()):
		floor_spaces = floor_map[fl_name]
		floors.append({
			"floor": fl_name,
			"spaces": floor_spaces,
			"total": len(floor_spaces),
			"available": sum(1 for s in floor_spaces if s.status == "Available"),
			"occupied": sum(1 for s in floor_spaces if s.status == "Occupied"),
			"reserved": sum(1 for s in floor_spaces if s.status == "Reserved"),
			"maintenance": sum(1 for s in floor_spaces if s.status == "Maintenance"),
		})

	# Get summary
	branches = frappe.get_all("Branch", pluck="name", order_by="name asc")
	all_floors = list(set(
		frappe.get_all("Co-working Space", filters=filters if branch else {},
			pluck="floor", distinct=True)
	))
	all_floors = [f for f in all_floors if f] + ([_("Unassigned")] if any(not f for f in all_floors) else [])

	return {
		"floors": floors,
		"branches": branches,
		"available_floors": sorted(all_floors),
		"summary": {
			"total": len(spaces),
			"available": sum(1 for s in spaces if s.status == "Available"),
			"occupied": sum(1 for s in spaces if s.status == "Occupied"),
			"reserved": sum(1 for s in spaces if s.status == "Reserved"),
			"maintenance": sum(1 for s in spaces if s.status == "Maintenance"),
		},
	}


def _get_type_icon(space_type):
	"""Map space type to icon."""
	icons = {
		"Hot Desk": "fa-solid fa-laptop",
		"Dedicated Desk": "fa-solid fa-desktop",
		"Private Office": "fa-solid fa-door-closed",
		"Meeting Room": "fa-solid fa-users",
		"Event Space": "fa-solid fa-calendar-star",
		"Training Room": "fa-solid fa-chalkboard-teacher",
		"Phone Booth": "fa-solid fa-phone",
		"Lounge": "fa-solid fa-couch",
	}
	return icons.get(space_type, "fa-solid fa-cube")
