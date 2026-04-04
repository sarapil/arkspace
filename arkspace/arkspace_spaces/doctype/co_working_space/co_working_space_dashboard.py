# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

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
