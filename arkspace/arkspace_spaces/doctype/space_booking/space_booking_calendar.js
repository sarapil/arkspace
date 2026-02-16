frappe.views.calendar["Space Booking"] = {
	field_map: {
		start: "start_datetime",
		end: "end_datetime",
		id: "name",
		allDay: 0,
		title: "space",
		status: "status",
		color: "color",
	},

	style_map: {
		Pending: "warning",
		Confirmed: "info",
		"Checked In": "success",
		"Checked Out": "inverse",
		Completed: "success",
		Cancelled: "danger",
		"No Show": "danger",
	},

	order_by: "start_datetime asc",

	gantt: {
		field_map: {
			start: "start_datetime",
			end: "end_datetime",
			id: "name",
			title: "space",
			progress: 0,
		},
	},

	filters: [
		{
			fieldtype: "Link",
			fieldname: "space",
			options: "Co-working Space",
			label: __("Space"),
		},
		{
			fieldtype: "Select",
			fieldname: "status",
			options: "\nPending\nConfirmed\nChecked In\nChecked Out\nCompleted\nCancelled\nNo Show",
			label: __("Status"),
		},
		{
			fieldtype: "Link",
			fieldname: "member",
			options: "Customer",
			label: __("Member"),
		},
	],

	get_events_method: "frappe.client.get_list",

	get_css_class: function (data) {
		if (data.status === "Cancelled" || data.status === "No Show") {
			return "danger";
		} else if (data.status === "Checked In") {
			return "success";
		} else if (data.status === "Confirmed") {
			return "info";
		} else if (data.status === "Pending") {
			return "warning";
		}
		return "default";
	},
};
