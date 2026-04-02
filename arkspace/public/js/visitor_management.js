/**
 * ARKSpace Visitor Management Frontend
 * إدارة الزوار — Visitor check-in/out, badge printing, real-time updates
 */

// Namespace
arkspace = window.arkspace || {};
arkspace.visitors = {};

// ─────────────────────────────────────────────────────────────────────────
// Visitor Log — Form Script
// ─────────────────────────────────────────────────────────────────────────

frappe.ui.form.on("Visitor Log", {
	refresh(frm) {
		arkspace.visitors.setup_buttons(frm);
	},
});

/**
 * Add action buttons based on visitor status.
 */
arkspace.visitors.setup_buttons = function (frm) {
	if (frm.is_new()) return;

	const status = frm.doc.status;

	// Check-in button
	if (status === "Expected") {
		if (frm.doc.approval_status === "Rejected") return;

		frm.add_custom_button(__("Check In"), () => {
			frappe.call({
				method: "arkspace.arkspace_spaces.visitor_management.visitor_check_in",
				args: { visitor_name: frm.doc.name },
				freeze: true,
				freeze_message: __("Checking in visitor..."),
				callback(r) {
					if (r.message) {
						frappe.show_alert({
							message: __(
								"{0} checked in — Badge #{1}",
								[frm.doc.visitor_name, r.message.badge_number]
							),
							indicator: "green",
						});
						frm.reload_doc();
					}
				},
			});
		}, __("Actions"));
		frm.change_custom_button_type(__("Check In"), __("Actions"), "primary");
	}

	// Check-out button
	if (status === "Checked In") {
		frm.add_custom_button(__("Check Out"), () => {
			frappe.call({
				method: "arkspace.arkspace_spaces.visitor_management.visitor_check_out",
				args: { visitor_name: frm.doc.name },
				freeze: true,
				callback(r) {
					if (r.message) {
						frappe.show_alert({
							message: __("{0} checked out", [frm.doc.visitor_name]),
							indicator: "green",
						});
						frm.reload_doc();
					}
				},
			});
		}, __("Actions"));
		frm.change_custom_button_type(__("Check Out"), __("Actions"), "danger");
	}

	// Print Badge button (checked in only)
	if (status === "Checked In" || status === "Expected") {
		frm.add_custom_button(__("Print Badge"), () => {
			arkspace.visitors.print_badge(frm);
		}, __("Actions"));
	}

	// Approve / Reject (for pre-registered pending visitors)
	if (frm.doc.preregistered && frm.doc.approval_status === "Pending") {
		frm.add_custom_button(__("Approve"), () => {
			frappe.call({
				method: "arkspace.arkspace_spaces.visitor_management.approve_visitor",
				args: { visitor_name: frm.doc.name },
				callback() {
					frappe.show_alert({
						message: __("Visitor approved"),
						indicator: "green",
					});
					frm.reload_doc();
				},
			});
		}, __("Approval"));
		frm.change_custom_button_type(__("Approve"), __("Approval"), "primary");

		frm.add_custom_button(__("Reject"), () => {
			frappe.prompt(
				{ fieldtype: "Small Text", label: __("Reason"), fieldname: "reason" },
				(values) => {
					frappe.call({
						method: "arkspace.arkspace_spaces.visitor_management.reject_visitor",
						args: {
							visitor_name: frm.doc.name,
							reason: values.reason,
						},
						callback() {
							frappe.show_alert({
								message: __("Visitor rejected"),
								indicator: "red",
							});
							frm.reload_doc();
						},
					});
				},
				__("Reject Visitor")
			);
		}, __("Approval"));
	}

	// Quick Walk-in button at top
	if (frm.is_new()) {
		frm.set_intro(__("Fill in visitor details and save, or use Quick Walk-in for immediate check-in."));
	}
};

/**
 * Print a visitor badge.
 */
arkspace.visitors.print_badge = function (frm) {
	frappe.call({
		method: "arkspace.arkspace_spaces.visitor_management.get_visitor_badge_html",
		args: { visitor_name: frm.doc.name },
		callback(r) {
			if (r.message) {
				const win = window.open("", "_blank");
				win.document.write(r.message);
				win.document.close();
			}
		},
	});
};

/**
 * Quick walk-in dialog — accessible from list view.
 */
arkspace.visitors.quick_walk_in = function () {
	const d = new frappe.ui.Dialog({
		title: __("Quick Walk-in"),
		fields: [
			{
				fieldtype: "Data",
				fieldname: "visitor_name",
				label: __("Visitor Name"),
				reqd: 1,
			},
			{
				fieldtype: "Data",
				fieldname: "visitor_phone",
				label: __("Phone"),
			},
			{
				fieldtype: "Data",
				fieldname: "visitor_company",
				label: __("Company"),
			},
			{ fieldtype: "Column Break" },
			{
				fieldtype: "Select",
				fieldname: "purpose",
				label: __("Purpose"),
				options: "Meeting\nInterview\nDelivery\nMaintenance\nTour\nEvent\nOther",
				default: "Meeting",
				reqd: 1,
			},
			{
				fieldtype: "Link",
				fieldname: "host",
				label: __("Host (Member)"),
				options: "Customer",
			},
			{
				fieldtype: "Link",
				fieldname: "visiting_space",
				label: __("Space"),
				options: "Co-working Space",
			},
			{ fieldtype: "Section Break", label: __("ID Verification") },
			{
				fieldtype: "Select",
				fieldname: "id_type",
				label: __("ID Type"),
				options: "\nNational ID\nPassport\nIqama\nDriving License\nOther",
			},
			{
				fieldtype: "Data",
				fieldname: "id_number",
				label: __("ID Number"),
			},
		],
		primary_action_label: __("Check In Now"),
		primary_action(values) {
			frappe.call({
				method: "arkspace.arkspace_spaces.visitor_management.walk_in_visitor",
				args: values,
				freeze: true,
				freeze_message: __("Registering and checking in visitor..."),
				callback(r) {
					d.hide();
					if (r.message) {
						frappe.show_alert({
							message: __(
								"{0} checked in — Badge #{1}",
								[r.message.visitor_name, r.message.badge_number]
							),
							indicator: "green",
						});
						// Open the visitor log
						frappe.set_route("Form", "Visitor Log", r.message.visitor);
					}
				},
			});
		},
	});
	d.show();
};

// ─────────────────────────────────────────────────────────────────────────
// List View
// ─────────────────────────────────────────────────────────────────────────

frappe.listview_settings["Visitor Log"] =
	frappe.listview_settings["Visitor Log"] || {};

const _original_visitor_onload =
	frappe.listview_settings["Visitor Log"].onload;

frappe.listview_settings["Visitor Log"].onload = function (listview) {
	if (_original_visitor_onload) _original_visitor_onload(listview);

	// Quick Walk-in button
	listview.page.add_inner_button(__("Quick Walk-in"), () => {
		arkspace.visitors.quick_walk_in();
	});

	// Today's Visitors button
	listview.page.add_inner_button(__("Today's Visitors"), () => {
		frappe.set_route("List", "Visitor Log", {
			creation: [
				">=",
				frappe.datetime.get_today() + " 00:00:00",
			],
		});
	});
};

frappe.listview_settings["Visitor Log"].get_indicator = function (doc) {
	const map = {
		"Expected": [__("Expected"), "orange", "status,=,Expected"],
		"Checked In": [__("Checked In"), "blue", "status,=,Checked In"],
		"Checked Out": [__("Checked Out"), "green", "status,=,Checked Out"],
		"Cancelled": [__("Cancelled"), "red", "status,=,Cancelled"],
		"No Show": [__("No Show"), "grey", "status,=,No Show"],
	};
	return map[doc.status] || [doc.status, "grey"];
};

// ─────────────────────────────────────────────────────────────────────────
// Real-time events
// ─────────────────────────────────────────────────────────────────────────

frappe.realtime.on("visitor_checked_in", function (data) {
	if (!data) return;
	frappe.show_alert({
		message: __("{0} has arrived", [data.visitor_name]),
		indicator: "blue",
	});
});

frappe.realtime.on("visitor_checked_out", function (data) {
	if (!data) return;
	frappe.show_alert({
		message: __("{0} has left", [data.visitor_name]),
		indicator: "green",
	});
});

frappe.realtime.on("visitor_arrived", function (data) {
	if (!data) return;
	frappe.show_alert({
		message: data.message,
		indicator: "blue",
	}, 10);
});
