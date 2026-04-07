// Copyright (c) 2026, Arkan Lab — License: MIT
frappe.listview_settings["Membership"] = {
	add_fields: ["status", "membership_plan", "rate", "start_date", "end_date"],
	get_indicator(doc) {
		let status_color = "grey";
		let label = __(doc.status || "Draft");

		if (doc.status === "Active" && doc.end_date) {
			const days_left = frappe.datetime.get_diff(doc.end_date, frappe.datetime.get_today());
			if (days_left < 0) {
				status_color = "red";
				label = __("Expired");
			} else if (days_left <= 7) {
				status_color = "red";
				label = __("Expiring Soon");
			} else if (days_left <= 30) {
				status_color = "orange";
				label = __("Expires in {0} days", [days_left]);
			} else {
				status_color = "green";
				label = __("Active");
			}
		} else {
			const map = {
				Draft: "orange",
				Active: "green",
				Expired: "darkgrey",
				Cancelled: "red",
				Suspended: "yellow",
			};
			status_color = map[doc.status] || "grey";
		}

		return [label, status_color, `status,=,${doc.status}`];
	},
	formatters: {
		rate(val) {
			return val ? format_currency(val) : "";
		},
	},
};
