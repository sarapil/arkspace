// Copyright (c) 2026, ARKSpace Team and contributors
// For license information, please see license.txt

frappe.ui.form.on("Documentation Entry", {
	refresh(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__("Regenerate"), function () {
				frappe.call({
					method:
						"arkspace.arkspace_documentation.auto_generator.regenerate_single",
					args: { doc_name: frm.doc.name },
					callback: function () {
						frm.reload_doc();
					},
				});
			});
		}
	},
});
