// Copyright (c) 2026, ARKSpace Team and contributors
// For license information, please see license.txt

frappe.ui.form.on("Co-working Space", {
	refresh(frm) {
		// Status indicator
		if (frm.doc.status === "Available") {
			frm.page.set_indicator(__("Available"), "green");
		} else if (frm.doc.status === "Occupied") {
			frm.page.set_indicator(__("Occupied"), "blue");
		} else if (frm.doc.status === "Maintenance") {
			frm.page.set_indicator(__("Maintenance"), "orange");
		} else if (frm.doc.status === "Reserved") {
			frm.page.set_indicator(__("Reserved"), "purple");
		}

		if (!frm.is_new() && frm.doc.status === "Available") {
			frm.add_custom_button(
				__("Create Booking"),
				function () {
					frappe.new_doc("Space Booking", {
						space: frm.doc.name,
					});
				},
				__("Actions")
			);
		}
	},
});
