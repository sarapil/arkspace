// Copyright (c) 2026, ARKSpace Team and contributors
// For license information, please see license.txt

frappe.ui.form.on("Member Credit Wallet", {
	refresh(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__("Add Credits"), function () {
				let d = new frappe.ui.Dialog({
					title: __("Add Credits"),
					fields: [
						{
							fieldname: "credits",
							fieldtype: "Float",
							label: __("Credits"),
							reqd: 1,
						},
						{
							fieldname: "description",
							fieldtype: "Small Text",
							label: __("Description"),
						},
					],
					primary_action_label: __("Add"),
					primary_action(values) {
						frappe.call({
							method: "add_credits",
							doc: frm.doc,
							args: {
								credits: values.credits,
								description: values.description,
							},
							callback: function () {
								frm.reload_doc();
							},
						});
						d.hide();
					},
				});
				d.show();
			});
		}
	},
});
