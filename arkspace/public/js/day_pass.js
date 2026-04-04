// Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
// Developer Website: https://arkan.it.com
// License: MIT
// For license information, please see license.txt

/**
 * ARKSpace Day Pass — Frontend
 * تصريح اليوم — واجهة المستخدم
 *
 * Form buttons for check-in/out, convert to membership,
 * QR preview, walk-in quick create, and day-pass dashboard stats.
 */

arkspace = window.arkspace || {};
arkspace.day_pass = {};

// ─────────────────────────────────────────────────────────────────────────
// Day Pass Form Script
// ─────────────────────────────────────────────────────────────────────────

frappe.ui.form.on("Day Pass", {
	refresh(frm) {
		arkspace.day_pass.setup_buttons(frm);
		arkspace.day_pass.show_qr_preview(frm);
		arkspace.day_pass.show_stats_banner(frm);
	},
});

/**
 * Add contextual action buttons based on status.
 */
arkspace.day_pass.setup_buttons = function (frm) {
	if (frm.doc.docstatus !== 1) return;

	const status = frm.doc.status;

	// Check In button
	if (status === "Active") {
		frm.add_custom_button(__("Check In"), () => {
			frappe.call({
				method: "arkspace.arkspace_spaces.day_pass_api.day_pass_check_in",
				args: { name: frm.doc.name },
				freeze: true,
				freeze_message: __("Checking in..."),
				callback(r) {
					if (r.message) {
						frappe.show_alert({
							message: __("Checked in successfully"),
							indicator: "green",
						});
						frm.reload_doc();
					}
				},
			});
		}).addClass("btn-primary-dark");
	}

	// Check Out button
	if (status === "Checked In") {
		frm.add_custom_button(__("Check Out"), () => {
			frappe.call({
				method: "arkspace.arkspace_spaces.day_pass_api.day_pass_check_out",
				args: { name: frm.doc.name },
				freeze: true,
				freeze_message: __("Checking out..."),
				callback(r) {
					if (r.message) {
						frappe.show_alert({
							message: __(
								"Checked out — Duration: {0}h",
								[r.message.duration_hours]
							),
							indicator: "blue",
						});
						frm.reload_doc();
					}
				},
			});
		}).addClass("btn-warning");
	}

	// Convert to Membership
	if (
		["Active", "Checked In", "Checked Out"].includes(status) &&
		!frm.doc.converted_to_membership
	) {
		frm.add_custom_button(
			__("Convert to Membership"),
			() => arkspace.day_pass.convert_dialog(frm),
			__("Actions")
		);
	}

	// Regenerate QR
	if (["Active", "Checked In"].includes(status)) {
		frm.add_custom_button(
			__("Regenerate QR"),
			() => {
				frappe.call({
					method: "arkspace.arkspace_spaces.day_pass_api.create_day_pass",
					// trigger QR regeneration via the controller
				});
				// Simpler: just reload after regenerating via direct doc method
				frm.call("_generate_qr").then(() => frm.reload_doc());
			},
			__("Actions")
		);

		frm.add_custom_button(
			__("Print QR"),
			() => arkspace.day_pass.print_qr(frm),
			__("Actions")
		);
	}
};

/**
 * Show QR code preview on the form.
 */
arkspace.day_pass.show_qr_preview = function (frm) {
	if (!frm.doc.qr_code || frm.doc.docstatus !== 1) return;

	const $wrapper = $(frm.fields_dict.qr_code?.wrapper);
	if (!$wrapper.length) return;

	$wrapper.find(".qr-preview").remove();
	$wrapper.append(`
		<div class="qr-preview"
			 style="text-align:center; padding:15px; margin-top:10px;
					background:#fff; border:1px solid #e2e8f0;
					border-radius:8px;">
			<img src="${frm.doc.qr_code}"
				 alt="QR Code"
				 style="max-width:180px; height:auto; image-rendering:pixelated;" />
			<div style="margin-top:8px; font-size:12px; color:#64748b;">
				${__("Scan for check-in")}
			</div>
		</div>
	`);
};

/**
 * Show today's day pass stats as a banner.
 */
arkspace.day_pass.show_stats_banner = function (frm) {
	if (!frm.is_new()) return;

	frappe.call({
		method: "arkspace.arkspace_spaces.day_pass_api.get_day_pass_stats",
		callback(r) {
			if (r.message) {
				const s = r.message;
				frm.dashboard.add_comment(
					__(
						"Today: {0} passes, {1} checked in, {2} checked out, Revenue: {3}",
						[s.total, s.checked_in, s.checked_out, s.revenue]
					),
					"blue",
					true
				);
			}
		},
	});
};

/**
 * Dialog for converting Day Pass to Membership.
 */
arkspace.day_pass.convert_dialog = function (frm) {
	const d = new frappe.ui.Dialog({
		title: __("Convert to Membership"),
		fields: [
			{
				fieldname: "plan",
				fieldtype: "Link",
				label: __("Membership Plan"),
				options: "Membership Plan",
				reqd: 1,
			},
			{
				fieldname: "billing_cycle",
				fieldtype: "Select",
				label: __("Billing Cycle"),
				options: "Monthly\nQuarterly\nYearly",
				default: "Monthly",
			},
			{
				fieldname: "credit_note",
				fieldtype: "HTML",
				options: `<p class="text-muted">
					${__(
						"The day pass amount ({0}) will be applied as credit.",
						[frm.doc.net_amount]
					)}
				</p>`,
			},
		],
		primary_action_label: __("Convert"),
		primary_action(values) {
			frappe.call({
				method: "arkspace.arkspace_spaces.day_pass_api.convert_day_pass_to_membership",
				args: {
					name: frm.doc.name,
					plan: values.plan,
					billing_cycle: values.billing_cycle,
				},
				freeze: true,
				freeze_message: __("Converting to membership..."),
				callback(r) {
					if (r.message) {
						d.hide();
						frappe.show_alert({
							message: __(
								"Membership {0} created! Credit: {1}",
								[r.message.membership, r.message.credit_applied]
							),
							indicator: "green",
						});
						frm.reload_doc();
					}
				},
			});
		},
	});
	d.show();
};

/**
 * Open a print-friendly QR page.
 */
arkspace.day_pass.print_qr = function (frm) {
	const doc = frm.doc;
	const win = window.open("", "_blank");
	win.document.write(`
		<!DOCTYPE html>
		<html>
		<head>
			<title>${__("Day Pass QR")} — ${doc.name}</title>
			<style>
				* { margin: 0; padding: 0; box-sizing: border-box; }
				body {
					font-family: -apple-system, BlinkMacSystemFont,
						'Segoe UI', Roboto, sans-serif;
					display: flex; justify-content: center; padding: 40px;
				}
				.card {
					text-align: center; max-width: 350px; padding: 30px;
					border: 2px solid #1B365D; border-radius: 12px;
				}
				.card h2 { color: #1B365D; margin-bottom: 8px; font-size: 18px; }
				.card .sub { color: #64748b; margin-bottom: 20px; font-size: 13px; }
				.card img { max-width: 220px; height: auto; image-rendering: pixelated; }
				.details { margin-top: 20px; text-align: left; font-size: 13px; color: #334155; }
				.details p { margin: 4px 0; }
				.footer { margin-top: 16px; font-size: 11px; color: #94a3b8; }
				@media print { body { padding: 0; } .card { border: 1px solid #ccc; } }
			</style>
		</head>
		<body>
			<div class="card">
				<h2>ARKSpace Day Pass</h2>
				<div class="sub">${__("Scan for check-in")}</div>
				<img src="${doc.qr_code}" />
				<div class="details">
					<p><strong>${__("Pass")}:</strong> ${doc.name}</p>
					<p><strong>${__("Guest")}:</strong> ${doc.guest_name}</p>
					<p><strong>${__("Type")}:</strong> ${doc.pass_type}</p>
					<p><strong>${__("Date")}:</strong> ${doc.pass_date}</p>
					<p><strong>${__("Space")}:</strong> ${doc.space || "—"}</p>
				</div>
				<div class="footer">${__("Powered by ARKSpace")}</div>
			</div>
			<script>window.print();</script>
		</body>
		</html>
	`);
	win.document.close();
};

// ─────────────────────────────────────────────────────────────────────────
// List View: Quick Walk-in + Bulk Actions
// ─────────────────────────────────────────────────────────────────────────

frappe.listview_settings["Day Pass"] =
	frappe.listview_settings["Day Pass"] || {};

Object.assign(frappe.listview_settings["Day Pass"], {
	get_indicator(doc) {
		const map = {
			Draft: [__("Draft"), "grey", "status,=,Draft"],
			Active: [__("Active"), "blue", "status,=,Active"],
			"Checked In": [__("Checked In"), "green", "status,=,Checked In"],
			"Checked Out": [__("Checked Out"), "darkgrey", "status,=,Checked Out"],
			Expired: [__("Expired"), "orange", "status,=,Expired"],
			Cancelled: [__("Cancelled"), "red", "status,=,Cancelled"],
		};
		return map[doc.status] || [doc.status, "grey"];
	},

	onload(listview) {
		listview.page.add_inner_button(__("Quick Walk-in"), () => {
			arkspace.day_pass.quick_walkin_dialog(listview);
		});
	},
});

/**
 * Quick Walk-in Dialog from list view.
 */
arkspace.day_pass.quick_walkin_dialog = function (listview) {
	const d = new frappe.ui.Dialog({
		title: __("Quick Walk-in Day Pass"),
		fields: [
			{
				fieldname: "guest_name",
				fieldtype: "Data",
				label: __("Guest Name"),
				reqd: 1,
			},
			{ fieldtype: "Column Break" },
			{
				fieldname: "guest_phone",
				fieldtype: "Data",
				label: __("Phone"),
				options: "Phone",
			},
			{ fieldtype: "Section Break" },
			{
				fieldname: "pass_type",
				fieldtype: "Select",
				label: __("Pass Type"),
				options: "Full Day\nHalf Day\nHourly\nEvening\nWeekend",
				default: "Full Day",
			},
			{ fieldtype: "Column Break" },
			{
				fieldname: "space",
				fieldtype: "Link",
				label: __("Space"),
				options: "Co-working Space",
				get_query: () => ({
					filters: { status: ["in", ["Available", "Reserved"]] },
				}),
			},
			{ fieldtype: "Section Break" },
			{
				fieldname: "payment_method",
				fieldtype: "Select",
				label: __("Payment"),
				options: "Cash\nCard\nOnline\nWallet\nFree",
				default: "Cash",
			},
			{ fieldtype: "Column Break" },
			{
				fieldname: "guest_email",
				fieldtype: "Data",
				label: __("Email"),
				options: "Email",
			},
		],
		primary_action_label: __("Create & Check In"),
		primary_action(values) {
			frappe.call({
				method: "arkspace.arkspace_spaces.day_pass_api.create_day_pass",
				args: values,
				freeze: true,
				freeze_message: __("Creating day pass..."),
				callback(r) {
					if (r.message) {
						d.hide();
						frappe.show_alert({
							message: __(
								"Day Pass {0} created for {1}",
								[r.message.day_pass, r.message.guest_name]
							),
							indicator: "green",
						});
						listview.refresh();
					}
				},
			});
		},
	});
	d.show();
};

// ─────────────────────────────────────────────────────────────────────────
// Real-time Events
// ─────────────────────────────────────────────────────────────────────────

frappe.realtime.on("day_pass_checked_in", function (data) {
	if (!data) return;
	frappe.show_alert({
		message: __("{0} checked in (Day Pass)", [data.guest_name || data.day_pass]),
		indicator: "green",
	});
	if (
		cur_frm &&
		cur_frm.doctype === "Day Pass" &&
		cur_frm.docname === data.day_pass
	) {
		cur_frm.reload_doc();
	}
});

frappe.realtime.on("day_pass_checked_out", function (data) {
	if (!data) return;
	frappe.show_alert({
		message: __("{0} checked out (Day Pass)", [data.guest_name || data.day_pass]),
		indicator: "blue",
	});
	if (
		cur_frm &&
		cur_frm.doctype === "Day Pass" &&
		cur_frm.docname === data.day_pass
	) {
		cur_frm.reload_doc();
	}
});
