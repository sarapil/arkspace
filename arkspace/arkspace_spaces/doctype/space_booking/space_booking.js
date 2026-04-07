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

		// Visual booking dashboard
		if (!frm.is_new()) {
			render_as_booking_visual(frm);
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

function render_as_booking_visual(frm) {
	const sc = {
		Pending: "var(--orange-500)", Confirmed: "var(--blue-500)", "Checked In": "var(--green-500)",
		"Checked Out": "var(--text-muted)", Cancelled: "var(--red-500)", "No Show": "var(--red-500)",
	};
	const color = sc[frm.doc.status] || "var(--text-muted)";

	const wrapper = frm.dashboard.add_section("", __("Booking Summary"));
	$(wrapper).html(`
		<div class="as-booking-visual fv-fx-page-enter" style="padding:12px 0;">
			<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:10px;">
				<div class="fv-fx-glass fv-fx-hover-lift" style="padding:14px;border-radius:10px;text-align:center;">
					<div style="font-size:22px;font-weight:700;color:${color};">${__(frm.doc.status || "—")}</div>
					<div style="font-size:11px;color:var(--text-muted);">${__("Status")}</div>
				</div>
				<div class="fv-fx-glass fv-fx-hover-lift" style="padding:14px;border-radius:10px;text-align:center;">
					<div style="font-size:16px;font-weight:600;">${frappe.utils.escape_html(frm.doc.space || "—")}</div>
					<div style="font-size:11px;color:var(--text-muted);">${__("Space")}</div>
				</div>
				<div class="fv-fx-glass fv-fx-hover-lift" style="padding:14px;border-radius:10px;text-align:center;">
					<div style="font-size:16px;font-weight:600;">${__(frm.doc.booking_type || "—")}</div>
					<div style="font-size:11px;color:var(--text-muted);">${__("Type")}</div>
				</div>
				<div class="fv-fx-glass fv-fx-hover-lift" style="padding:14px;border-radius:10px;text-align:center;">
					<div style="font-size:22px;font-weight:700;color:var(--green-500);">${format_currency(frm.doc.rate || 0)}</div>
					<div style="font-size:11px;color:var(--text-muted);">${__("Rate")}</div>
				</div>
			</div>
		</div>
	`);
}
