// Copyright (c) 2026, ARKSpace Team and contributors
// For license information, please see license.txt

frappe.ui.form.on("Membership Plan", {
	refresh(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__("View Memberships"), function () {
				frappe.set_route("List", "Membership", {
					membership_plan: frm.doc.name,
				});
			});
		}
	},
});
