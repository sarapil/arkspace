// Copyright (c) 2026, ARKSpace Team and contributors
// For license information, please see license.txt

frappe.ui.form.on("Workspace Tour", {
	refresh(frm) {
		const colors = {
			Scheduled: "blue",
			Completed: "green",
			"No Show": "red",
			Rescheduled: "orange",
			Cancelled: "darkgrey",
		};
		if (frm.doc.status) {
			frm.page.set_indicator(__(frm.doc.status), colors[frm.doc.status] || "grey");
		}

		if (!frm.is_new() && frm.doc.status === "Scheduled") {
			frm.add_custom_button(__("Complete Tour"), function () {
				let d = new frappe.ui.Dialog({
					title: __("Complete Tour"),
					fields: [
						{
							fieldname: "interest_level",
							fieldtype: "Rating",
							label: __("Interest Level"),
						},
						{
							fieldname: "outcome",
							fieldtype: "Select",
							label: __("Outcome"),
							options: "\nInterested\nNeed Follow Up\nNot Interested\nConverted",
							reqd: 1,
						},
						{
							fieldname: "feedback",
							fieldtype: "Text Editor",
							label: __("Feedback"),
						},
					],
					primary_action_label: __("Complete"),
					primary_action(values) {
						frm.call("mark_completed", values).then(() => {
							frm.reload_doc();
							d.hide();
						});
					},
				});
				d.show();
			}, __("Actions"));

			frm.add_custom_button(__("No Show"), function () {
				frm.set_value("status", "No Show");
				frm.save();
			}, __("Actions"));
		}
	},
});
