from frappe import _


def get_data():
	return {
		"heatmap": True,
		"heatmap_message": _("Activity based on bookings"),
		"fieldname": "space",
		"transactions": [
			{
				"label": _("Bookings"),
				"items": ["Space Booking"],
			},
		],
	}
