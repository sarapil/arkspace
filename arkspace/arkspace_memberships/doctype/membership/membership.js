// Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
// Developer Website: https://arkan.it.com
// License: MIT
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

		// Visual membership dashboard
		if (!frm.is_new()) {
			render_as_membership_visual(frm);
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

function render_as_membership_visual(frm) {
	const sc = {
		Draft: "var(--orange-500)", Active: "var(--green-500)", Expired: "var(--text-muted)",
		Cancelled: "var(--red-500)", Suspended: "var(--yellow-500)",
	};
	const color = sc[frm.doc.status] || "var(--text-muted)";

	let days_left = null;
	if (frm.doc.end_date && frm.doc.status === "Active") {
		days_left = frappe.datetime.get_diff(frm.doc.end_date, frappe.datetime.get_today());
	}

	const wrapper = frm.dashboard.add_section("", __("Membership Overview"));
	$(wrapper).html(`
		<div class="as-membership-visual fv-fx-page-enter" style="padding:12px 0;">
			<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:10px;">
				<div class="fv-fx-glass fv-fx-hover-lift" style="padding:14px;border-radius:10px;text-align:center;">
					<div style="font-size:22px;font-weight:700;color:${color};">${__(frm.doc.status || "Draft")}</div>
					<div style="font-size:11px;color:var(--text-muted);">${__("Status")}</div>
				</div>
				<div class="fv-fx-glass fv-fx-hover-lift" style="padding:14px;border-radius:10px;text-align:center;">
					<div style="font-size:16px;font-weight:600;">${frappe.utils.escape_html(frm.doc.membership_plan || "—")}</div>
					<div style="font-size:11px;color:var(--text-muted);">${__("Plan")}</div>
				</div>
				<div class="fv-fx-glass fv-fx-hover-lift" style="padding:14px;border-radius:10px;text-align:center;">
					<div style="font-size:22px;font-weight:700;color:var(--green-500);">${format_currency(frm.doc.rate || 0)}</div>
					<div style="font-size:11px;color:var(--text-muted);">${__(frm.doc.billing_cycle || "Rate")}</div>
				</div>
				${days_left !== null ? `
				<div class="fv-fx-glass fv-fx-hover-lift" style="padding:14px;border-radius:10px;text-align:center;">
					<div style="font-size:22px;font-weight:700;color:${days_left <= 7 ? "var(--red-500)" : "var(--primary)"};">
						${days_left} ${__("days")}
					</div>
					<div style="font-size:11px;color:var(--text-muted);">${__("Remaining")}</div>
				</div>` : ""}
			</div>
		</div>
	`);
}
