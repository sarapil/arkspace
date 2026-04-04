// Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
// Developer Website: https://arkan.it.com
// License: MIT
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
