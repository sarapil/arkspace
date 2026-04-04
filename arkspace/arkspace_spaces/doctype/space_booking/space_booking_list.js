// Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
// Developer Website: https://arkan.it.com
// License: MIT
// For license information, please see license.txt

frappe.listview_settings["Space Booking"] = {
	add_fields: ["status", "space", "member", "start_datetime", "end_datetime", "net_amount"],

	get_indicator: function (doc) {
		const colors = {
			Pending: [__("Pending"), "orange", "status,=,Pending"],
			Confirmed: [__("Confirmed"), "blue", "status,=,Confirmed"],
			"Checked In": [__("Checked In"), "green", "status,=,Checked In"],
			"Checked Out": [__("Checked Out"), "darkgrey", "status,=,Checked Out"],
			Completed: [__("Completed"), "green", "status,=,Completed"],
			Cancelled: [__("Cancelled"), "red", "status,=,Cancelled"],
			"No Show": [__("No Show"), "red", "status,=,No Show"],
		};
		return colors[doc.status] || [__(doc.status), "grey", `status,=,${doc.status}`];
	},

	formatters: {
		start_datetime: function (value) {
			if (value) {
				return frappe.datetime.str_to_user(value);
			}
			return "";
		},
		net_amount: function (value) {
			if (value) {
				return format_currency(value);
			}
			return "";
		},
	},

	onload: function (listview) {
		// Bulk Check In
		listview.page.add_action_item(__("Bulk Check In"), function () {
			const names = listview.get_checked_items(true);
			if (!names.length) {
				frappe.throw(__("Please select bookings first"));
				return;
			}
			frappe.confirm(
				__("Check in {0} booking(s)?", [names.length]),
				function () {
					frappe.call({
						method: "arkspace.arkspace_spaces.bulk_operations.bulk_check_in",
						args: { bookings: names },
						callback: function (r) {
							_show_bulk_result(r.message, __("Check In"));
							listview.refresh();
						},
					});
				}
			);
		});

		// Bulk Check Out
		listview.page.add_action_item(__("Bulk Check Out"), function () {
			const names = listview.get_checked_items(true);
			if (!names.length) {
				frappe.throw(__("Please select bookings first"));
				return;
			}
			frappe.confirm(
				__("Check out {0} booking(s)?", [names.length]),
				function () {
					frappe.call({
						method: "arkspace.arkspace_spaces.bulk_operations.bulk_check_out",
						args: { bookings: names },
						callback: function (r) {
							_show_bulk_result(r.message, __("Check Out"));
							listview.refresh();
						},
					});
				}
			);
		});

		// Bulk Cancel
		listview.page.add_action_item(__("Bulk Cancel"), function () {
			const names = listview.get_checked_items(true);
			if (!names.length) {
				frappe.throw(__("Please select bookings first"));
				return;
			}
			frappe.confirm(
				__("Cancel {0} booking(s)? This cannot be undone.", [names.length]),
				function () {
					frappe.call({
						method: "arkspace.arkspace_spaces.bulk_operations.bulk_cancel",
						args: { bookings: names },
						callback: function (r) {
							_show_bulk_result(r.message, __("Cancel"));
							listview.refresh();
						},
					});
				}
			);
		});

		// Bulk No Show
		listview.page.add_action_item(__("Bulk No Show"), function () {
			const names = listview.get_checked_items(true);
			if (!names.length) {
				frappe.throw(__("Please select bookings first"));
				return;
			}
			frappe.confirm(
				__("Mark {0} booking(s) as No Show?", [names.length]),
				function () {
					frappe.call({
						method: "arkspace.arkspace_spaces.bulk_operations.bulk_mark_no_show",
						args: { bookings: names },
						callback: function (r) {
							_show_bulk_result(r.message, __("No Show"));
							listview.refresh();
						},
					});
				}
			);
		});
	},
};

function _show_bulk_result(result, action) {
	const s = result.success.length;
	const f = result.failed.length;
	let msg = __("{0}: {1} succeeded", [action, s]);
	if (f > 0) {
		msg += __(", {0} failed", [f]);
		const errors = result.failed
			.map((e) => `<li>${e.booking}: ${e.error}</li>`)
			.join("");
		msg += `<ul class="mt-2" style="font-size:12px;">${errors}</ul>`;
	}
	frappe.msgprint({
		title: __("Bulk {0} Result", [action]),
		message: msg,
		indicator: f > 0 ? "orange" : "green",
	});
}
