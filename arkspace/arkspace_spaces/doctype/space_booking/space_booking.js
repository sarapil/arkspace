// Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
// Developer Website: https://arkan.it.com
// License: MIT
// For license information, please see license.txt

frappe.ui.form.on("Space Booking", {
	refresh(frm) {
		// Status indicator
		const colors = {
			Pending: "orange",
			Confirmed: "blue",
			"Checked In": "green",
			"Checked Out": "darkgrey",
			Cancelled: "red",
			"No Show": "red",
		};
		if (frm.doc.status) {
			frm.page.set_indicator(__(frm.doc.status), colors[frm.doc.status] || "grey");
		}

		if (frm.doc.docstatus === 1) {
			if (frm.doc.status === "Confirmed") {
				frm.add_custom_button(__("Check In"), function () {
					frappe.call({
						method: "arkspace.api.check_in",
						args: { booking: frm.doc.name },
						callback: function () {
							frm.reload_doc();
						},
					});
				}, __("Actions"));
			}

			if (frm.doc.status === "Checked In") {
				frm.add_custom_button(__("Check Out"), function () {
					frappe.call({
						method: "arkspace.api.check_out",
						args: { booking: frm.doc.name },
						callback: function () {
							frm.reload_doc();
						},
					});
				}, __("Actions"));
			}
		}
	},

	space(frm) {
		if (frm.doc.space && frm.doc.booking_type) {
			frappe.db.get_doc("Co-working Space", frm.doc.space).then((space) => {
				const rate_map = {
					Hourly: space.hourly_rate,
					Daily: space.daily_rate,
					Monthly: space.monthly_rate,
				};
				frm.set_value("rate", rate_map[frm.doc.booking_type] || 0);
			});
		}
	},

	booking_type(frm) {
		frm.trigger("space");
	},
});
