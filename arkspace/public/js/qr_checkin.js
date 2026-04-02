/**
 * ARKSpace QR Check-in Frontend
 * تسجيل الدخول بـ QR — QR Code Check-in UI
 *
 * Adds QR generation, preview, print, and bulk-generate functionality
 * to Space Booking forms and list views.
 */

// Namespace
arkspace = window.arkspace || {};
arkspace.qr = {};

// ─────────────────────────────────────────────────────────────────────────
// Space Booking — Form Script
// ─────────────────────────────────────────────────────────────────────────

frappe.ui.form.on("Space Booking", {
	refresh(frm) {
		arkspace.qr.setup_booking_buttons(frm);
		arkspace.qr.show_qr_preview(frm);
	},
});

/**
 * Add QR-related buttons to the Space Booking form.
 */
arkspace.qr.setup_booking_buttons = function (frm) {
	if (!frm.doc.docstatus || frm.doc.docstatus !== 1) return;
	if (["Cancelled", "No Show"].includes(frm.doc.status)) return;

	// Generate / Regenerate QR button
	const label = frm.doc.qr_code
		? __("Regenerate QR Code")
		: __("Generate QR Code");

	frm.add_custom_button(
		label,
		() => arkspace.qr.generate(frm),
		__("QR Check-in")
	);

	// Print QR button (only if QR exists)
	if (frm.doc.qr_code) {
		frm.add_custom_button(
			__("Print QR Code"),
			() => arkspace.qr.print_qr(frm),
			__("QR Check-in")
		);

		frm.add_custom_button(
			__("Download QR Code"),
			() => arkspace.qr.download_qr(frm),
			__("QR Check-in")
		);
	}
};

/**
 * Generate QR code for the current booking.
 */
arkspace.qr.generate = function (frm) {
	frappe.call({
		method: "arkspace.arkspace_spaces.qr_checkin.generate_qr",
		args: { booking_name: frm.doc.name },
		freeze: true,
		freeze_message: __("Generating QR Code..."),
		callback(r) {
			if (r.message) {
				frappe.show_alert({
					message: __("QR Code generated successfully"),
					indicator: "green",
				});
				frm.reload_doc();
			}
		},
	});
};

/**
 * Show QR code image preview on the form.
 */
arkspace.qr.show_qr_preview = function (frm) {
	if (!frm.doc.qr_code || frm.doc.docstatus !== 1) return;

	// Remove old preview
	frm.fields_dict.qr_code &&
		$(frm.fields_dict.qr_code.wrapper).find(".qr-preview").remove();

	if (!frm.fields_dict.qr_code) return;

	const $wrapper = $(frm.fields_dict.qr_code.wrapper);
	const preview_html = `
		<div class="qr-preview"
			 style="text-align:center; padding:15px; margin-top:10px;
					background:#fff; border:1px solid #e2e8f0;
					border-radius:8px;">
			<img src="${frm.doc.qr_code}"
				 alt="QR Code"
				 style="max-width:200px; height:auto; image-rendering:pixelated;" />
			<div style="margin-top:8px; font-size:12px; color:#64748b;">
				${__("Scan to check in")}
			</div>
		</div>
	`;
	$wrapper.append(preview_html);
};

/**
 * Open a print-friendly page with the QR code.
 */
arkspace.qr.print_qr = function (frm) {
	const booking = frm.doc;
	const win = window.open("", "_blank");
	win.document.write(`
		<!DOCTYPE html>
		<html>
		<head>
			<title>${__("QR Check-in")} — ${booking.name}</title>
			<style>
				* { margin: 0; padding: 0; box-sizing: border-box; }
				body {
					font-family: -apple-system, BlinkMacSystemFont,
						'Segoe UI', Roboto, sans-serif;
					display: flex;
					justify-content: center;
					padding: 40px;
				}
				.print-card {
					text-align: center;
					max-width: 350px;
					padding: 30px;
					border: 2px solid #1B365D;
					border-radius: 12px;
				}
				.print-card h2 {
					color: #1B365D;
					margin-bottom: 8px;
					font-size: 18px;
				}
				.print-card .sub {
					color: #64748b;
					margin-bottom: 20px;
					font-size: 13px;
				}
				.print-card img {
					max-width: 250px;
					height: auto;
					image-rendering: pixelated;
				}
				.details {
					margin-top: 20px;
					text-align: left;
					font-size: 13px;
					color: #334155;
				}
				.details p { margin: 4px 0; }
				.footer {
					margin-top: 16px;
					font-size: 11px;
					color: #94a3b8;
				}
				@media print {
					body { padding: 0; }
					.print-card { border: 1px solid #ccc; }
				}
			</style>
		</head>
		<body>
			<div class="print-card">
				<h2>ARKSpace Check-in</h2>
				<div class="sub">${__("Scan to check in")}</div>
				<img src="${booking.qr_code}" />
				<div class="details">
					<p><strong>${__("Booking")}:</strong> ${booking.name}</p>
					<p><strong>${__("Space")}:</strong> ${booking.space || ""}</p>
					<p><strong>${__("Member")}:</strong> ${booking.member_name || booking.member}</p>
					<p><strong>${__("Time")}:</strong>
						${frappe.datetime.str_to_user(booking.start_datetime)}
						— ${frappe.datetime.str_to_user(booking.end_datetime)}
					</p>
				</div>
				<div class="footer">${__("Powered by ARKSpace")}</div>
			</div>
			<script>window.print();</script>
		</body>
		</html>
	`);
	win.document.close();
};

/**
 * Download QR code image.
 */
arkspace.qr.download_qr = function (frm) {
	if (!frm.doc.qr_code) return;
	const a = document.createElement("a");
	a.href = frm.doc.qr_code;
	a.download = `qr-${frm.doc.name}.png`;
	document.body.appendChild(a);
	a.click();
	document.body.removeChild(a);
};

// ─────────────────────────────────────────────────────────────────────────
// List View: Bulk Generate QR
// ─────────────────────────────────────────────────────────────────────────

frappe.listview_settings["Space Booking"] =
	frappe.listview_settings["Space Booking"] || {};

const _original_onload =
	frappe.listview_settings["Space Booking"].onload;

frappe.listview_settings["Space Booking"].onload = function (listview) {
	if (_original_onload) _original_onload(listview);

	listview.page.add_inner_button(__("Bulk Generate QR"), () => {
		frappe.call({
			method: "arkspace.arkspace_spaces.qr_checkin.bulk_generate_qr",
			freeze: true,
			freeze_message: __("Generating QR codes for today's bookings..."),
			callback(r) {
				if (r.message) {
					frappe.show_alert({
						message: __(
							"{0} QR codes generated", [r.message.generated]
						),
						indicator: "green",
					});
					listview.refresh();
				}
			},
		});
	});
};

// ─────────────────────────────────────────────────────────────────────────
// Real-time: booking_checked_in event
// ─────────────────────────────────────────────────────────────────────────

frappe.realtime.on("booking_checked_in", function (data) {
	if (!data) return;

	frappe.show_alert({
		message: __("{0} checked in to {1}", [
			data.member || data.booking,
			data.space || "",
		]),
		indicator: "green",
	});

	// Refresh form if currently viewing this booking
	if (
		cur_frm &&
		cur_frm.doctype === "Space Booking" &&
		cur_frm.docname === data.booking
	) {
		cur_frm.reload_doc();
	}
});
