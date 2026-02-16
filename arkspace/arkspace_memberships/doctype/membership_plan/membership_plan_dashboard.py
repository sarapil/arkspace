from frappe import _


def get_data():
	return {
		"fieldname": "membership_plan",
		"transactions": [
			{
				"label": _("Memberships"),
				"items": ["Membership"],
			},
		],
	}
