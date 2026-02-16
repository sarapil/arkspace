// Copyright (c) 2026, ARKSpace Team and contributors
// For license information, please see license.txt

frappe.ui.form.on("Membership", {
	refresh(frm) {
		const colors = {
			Draft: "orange",
			Active: "green",
			Expired: "darkgrey",
			Cancelled: "red",
			Suspended: "yellow",
		};
		if (frm.doc.status) {
			frm.page.set_indicator(__(frm.doc.status), colors[frm.doc.status] || "grey");
		}

		if (frm.doc.docstatus === 1 && frm.doc.status === "Active") {
			frm.add_custom_button(__("Suspend"), function () {
				frappe.confirm(__("Are you sure you want to suspend this membership?"), function () {
					frm.set_value("status", "Suspended");
					frm.save();
				});
			}, __("Actions"));

			if (frm.doc.credit_wallet) {
				frm.add_custom_button(__("View Wallet"), function () {
					frappe.set_route("Form", "Member Credit Wallet", frm.doc.credit_wallet);
				});
			}
		}
	},

	membership_plan(frm) {
		if (frm.doc.membership_plan) {
			frappe.db.get_doc("Membership Plan", frm.doc.membership_plan).then((plan) => {
				const rate_map = {
					Monthly: plan.monthly_price,
					Quarterly: plan.quarterly_price || plan.monthly_price * 3,
					Yearly: plan.yearly_price || plan.monthly_price * 12,
				};
				frm.set_value("rate", rate_map[frm.doc.billing_cycle] || plan.monthly_price);
				frm.set_value("plan_type", plan.plan_type);
			});
		}
	},

	billing_cycle(frm) {
		frm.trigger("membership_plan");
	},
});
