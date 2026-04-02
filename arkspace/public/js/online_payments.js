/**
 * ARKSpace Online Payments — Client-side Integration
 * أرك سبيس — بوابة الدفع الإلكتروني
 *
 * Adds "Pay Online" buttons to Space Booking and Membership forms,
 * and provides utilities for payment flow management.
 */

frappe.provide("arkspace.payments");

// ═══════════════════════════════════════════════════════════════════════════
// Payment Status Indicator
// ═══════════════════════════════════════════════════════════════════════════

arkspace.payments.STATUS_COLORS = {
	Initiated: "blue",
	Pending: "orange",
	Completed: "green",
	Failed: "red",
	Cancelled: "grey",
	Refunded: "purple",
	"Partially Refunded": "purple",
	Expired: "grey",
};

arkspace.payments.STATUS_ICONS = {
	Initiated: "fa-solid fa-hourglass-start",
	Pending: "fa-solid fa-spinner fa-spin",
	Completed: "fa-solid fa-circle-check",
	Failed: "fa-solid fa-circle-xmark",
	Cancelled: "fa-solid fa-ban",
	Refunded: "fa-solid fa-rotate-left",
	"Partially Refunded": "fa-solid fa-rotate-left",
	Expired: "fa-solid fa-clock",
};


// ═══════════════════════════════════════════════════════════════════════════
// Core Payment Functions
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Initiate an online payment for a document.
 * Opens a new tab/window with the gateway checkout page.
 */
arkspace.payments.pay_online = function (doctype, docname, opts) {
	opts = opts || {};

	frappe.call({
		method: "arkspace.arkspace_integrations.api.get_checkout_url",
		args: {
			reference_doctype: doctype,
			reference_name: docname,
		},
		freeze: true,
		freeze_message: __("Preparing payment link..."),
		callback: function (r) {
			if (r.message && r.message.checkout_url) {
				// Open checkout in new tab
				window.open(r.message.checkout_url, "_blank");

				frappe.show_alert(
					{
						message: __("Payment window opened. Complete the payment in the new tab."),
						indicator: "blue",
					},
					10
				);

				// Start polling for completion
				if (opts.on_complete) {
					arkspace.payments._poll_status(
						r.message.payment_name,
						opts.on_complete,
						opts.on_fail
					);
				}
			} else {
				frappe.msgprint(
					__("Could not generate payment link. Please try again.")
				);
			}
		},
		error: function () {
			frappe.msgprint(
				__("Failed to initiate payment. Please check your payment gateway configuration.")
			);
		},
	});
};

/**
 * Check payment status for a document and display it.
 */
arkspace.payments.check_status = function (doctype, docname, callback) {
	frappe.call({
		method: "arkspace.arkspace_integrations.api.get_payment_status",
		args: {
			reference_doctype: doctype,
			reference_name: docname,
		},
		callback: function (r) {
			if (callback) callback(r.message);
		},
	});
};

/**
 * Verify a specific payment with the gateway.
 */
arkspace.payments.verify = function (payment_name, callback) {
	frappe.call({
		method: "arkspace.arkspace_integrations.api.verify_payment",
		args: { payment_name: payment_name },
		freeze: true,
		freeze_message: __("Verifying payment with gateway..."),
		callback: function (r) {
			if (r.message) {
				const status = r.message.status;
				const color = arkspace.payments.STATUS_COLORS[status] || "grey";
				frappe.show_alert(
					{
						message: __("Payment status: {0}", [status]),
						indicator: color,
					},
					5
				);
			}
			if (callback) callback(r.message);
		},
	});
};

/**
 * Request a refund for a payment.
 */
arkspace.payments.refund = function (payment_name, amount, reason) {
	frappe.confirm(
		__("Are you sure you want to refund this payment?"),
		function () {
			frappe.call({
				method: "arkspace.arkspace_integrations.api.refund_payment",
				args: {
					payment_name: payment_name,
					amount: amount || null,
					reason: reason || null,
				},
				freeze: true,
				freeze_message: __("Processing refund..."),
				callback: function (r) {
					if (r.message) {
						frappe.show_alert(
							{
								message: __("Refund processed: {0}", [r.message.status]),
								indicator: "green",
							},
							5
						);
						cur_frm && cur_frm.reload_doc();
					}
				},
			});
		}
	);
};


// ═══════════════════════════════════════════════════════════════════════════
// Internal: Poll payment status
// ═══════════════════════════════════════════════════════════════════════════

arkspace.payments._poll_status = function (payment_name, on_complete, on_fail, attempt) {
	attempt = attempt || 0;
	const MAX_ATTEMPTS = 60; // 5 min at 5s intervals
	const INTERVAL = 5000;

	if (attempt >= MAX_ATTEMPTS) return;

	setTimeout(function () {
		frappe.call({
			method: "arkspace.arkspace_integrations.api.verify_payment",
			args: { payment_name: payment_name },
			callback: function (r) {
				if (!r.message) return;

				if (r.message.status === "Completed") {
					frappe.show_alert(
						{
							message: __("Payment completed successfully!"),
							indicator: "green",
						},
						8
					);
					if (on_complete) on_complete(r.message);
					cur_frm && cur_frm.reload_doc();
				} else if (r.message.status === "Failed") {
					frappe.show_alert(
						{
							message: __("Payment failed. Please try again."),
							indicator: "red",
						},
						8
					);
					if (on_fail) on_fail(r.message);
				} else if (["Initiated", "Pending"].includes(r.message.status)) {
					// Still waiting — poll again
					arkspace.payments._poll_status(
						payment_name,
						on_complete,
						on_fail,
						attempt + 1
					);
				}
			},
		});
	}, INTERVAL);
};


// ═══════════════════════════════════════════════════════════════════════════
// Payment Status HTML renderer (for form sidebars)
// ═══════════════════════════════════════════════════════════════════════════

arkspace.payments.render_status_html = function (payments) {
	if (!payments || !payments.length) {
		return '<div class="text-muted">' + __("No online payments") + "</div>";
	}

	let html = '<div class="arkspace-payment-list">';
	payments.forEach(function (p) {
		const color = arkspace.payments.STATUS_COLORS[p.status] || "grey";
		const icon = arkspace.payments.STATUS_ICONS[p.status] || "fa-solid fa-circle";
		html += `
			<div class="payment-item mb-2 p-2 border rounded">
				<div class="d-flex justify-content-between align-items-center">
					<span>
						<i class="${icon}" style="color: var(--${color}-500)"></i>
						<a href="/desk/online-payment/${p.name}">${p.name}</a>
					</span>
					<span class="indicator-pill ${color}">${p.status}</span>
				</div>
				<div class="text-muted small mt-1">
					${p.gateway} · ${format_currency(p.amount, p.currency)}
				</div>
			</div>
		`;
	});
	html += "</div>";
	return html;
};


// ═══════════════════════════════════════════════════════════════════════════
// Form Script: Space Booking — "Pay Online" button
// ═══════════════════════════════════════════════════════════════════════════

frappe.ui.form.on("Space Booking", {
	refresh: function (frm) {
		if (frm.doc.docstatus !== 1) return;
		if (["Cancelled", "No Show"].includes(frm.doc.status)) return;

		arkspace.payments.check_status("Space Booking", frm.doc.name, function (data) {
			if (!data) return;

			// Show payment status in sidebar
			if (data.payments && data.payments.length) {
				frm.dashboard.add_section(
					arkspace.payments.render_status_html(data.payments),
					__("Online Payments")
				);
			}

			// Only show Pay Online if no completed payment exists
			if (data.latest_status === "Completed") return;

			frm.add_custom_button(
				__("Pay Online"),
				function () {
					arkspace.payments.pay_online("Space Booking", frm.doc.name, {
						on_complete: function () {
							frm.reload_doc();
						},
					});
				},
				__("Actions")
			);
			frm.change_custom_button_type(__("Pay Online"), __("Actions"), "primary");
		});
	},
});


// ═══════════════════════════════════════════════════════════════════════════
// Form Script: Membership — "Pay Online" button
// ═══════════════════════════════════════════════════════════════════════════

frappe.ui.form.on("Membership", {
	refresh: function (frm) {
		if (frm.doc.docstatus !== 1) return;
		if (frm.doc.status === "Cancelled") return;

		arkspace.payments.check_status("Membership", frm.doc.name, function (data) {
			if (!data) return;

			// Show payment status in sidebar
			if (data.payments && data.payments.length) {
				frm.dashboard.add_section(
					arkspace.payments.render_status_html(data.payments),
					__("Online Payments")
				);
			}

			if (data.latest_status === "Completed") return;

			frm.add_custom_button(
				__("Pay Online"),
				function () {
					arkspace.payments.pay_online("Membership", frm.doc.name, {
						on_complete: function () {
							frm.reload_doc();
						},
					});
				},
				__("Actions")
			);
			frm.change_custom_button_type(__("Pay Online"), __("Actions"), "primary");
		});
	},
});


// ═══════════════════════════════════════════════════════════════════════════
// Form Script: Online Payment — verify & refund actions
// ═══════════════════════════════════════════════════════════════════════════

frappe.ui.form.on("Online Payment", {
	refresh: function (frm) {
		// Verify button for pending payments
		if (["Initiated", "Pending"].includes(frm.doc.status)) {
			frm.add_custom_button(__("Verify with Gateway"), function () {
				arkspace.payments.verify(frm.doc.name, function () {
					frm.reload_doc();
				});
			});
		}

		// Refund button for completed payments
		if (frm.doc.status === "Completed") {
			frm.add_custom_button(
				__("Refund"),
				function () {
					frappe.prompt(
						[
							{
								fieldname: "amount",
								fieldtype: "Currency",
								label: __("Refund Amount"),
								default: frm.doc.amount,
								reqd: 1,
							},
							{
								fieldname: "reason",
								fieldtype: "Small Text",
								label: __("Reason"),
							},
						],
						function (values) {
							arkspace.payments.refund(
								frm.doc.name,
								values.amount,
								values.reason
							);
						},
						__("Refund Payment")
					);
				},
				__("Actions")
			);
		}

		// Color the status indicator
		const color = arkspace.payments.STATUS_COLORS[frm.doc.status];
		if (color) {
			frm.page.set_indicator(frm.doc.status, color);
		}
	},
});


// ═══════════════════════════════════════════════════════════════════════════
// Real-time event listener — payment completion notification
// ═══════════════════════════════════════════════════════════════════════════

frappe.realtime.on("online_payment_completed", function (data) {
	frappe.show_alert(
		{
			message: __("Payment {0} completed!", [data.payment]),
			indicator: "green",
		},
		10
	);

	// Reload current form if it's the related document
	if (
		cur_frm &&
		cur_frm.doc.name === data.reference
	) {
		cur_frm.reload_doc();
	}
});
