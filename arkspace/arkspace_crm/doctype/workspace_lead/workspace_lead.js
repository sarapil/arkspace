// Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
// Developer Website: https://arkan.it.com
// License: MIT
// For license information, please see license.txt

frappe.ui.form.on("Workspace Lead", {
	refresh(frm) {
		const colors = {
			New: "blue",
			Contacted: "orange",
			"Tour Scheduled": "purple",
			Negotiating: "yellow",
			Converted: "green",
			Lost: "red",
		};
		if (frm.doc.status) {
			frm.page.set_indicator(__(frm.doc.status), colors[frm.doc.status] || "grey");
		}

		if (!frm.is_new() && frm.doc.status !== "Converted" && frm.doc.status !== "Lost") {
			frm.add_custom_button(__("Schedule Tour"), function () {
				frm.call("schedule_tour").then(() => frm.reload_doc());
			}, __("Actions"));

			frm.add_custom_button(__("Convert to Customer"), function () {
				frappe.confirm(
					__("Convert {0} to a Customer?", [frm.doc.lead_name]),
					function () {
						frm.call("convert_to_customer").then(() => frm.reload_doc());
					}
				);
			}, __("Actions"));
		}
	},
});
