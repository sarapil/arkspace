// Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
// Developer Website: https://arkan.it.com
// License: MIT
// For license information, please see license.txt

/**
 * ARKSpace — Portal JavaScript
 * تفاعل بوابة الأعضاء
 *
 * Provides interactive features for the member portal:
 * - Quick booking modal
 * - Credit wallet display
 * - Booking cancellation
 * - Real-time status updates
 */

document.addEventListener("DOMContentLoaded", function () {
	// Only run on ARKSpace portal pages
	if (!document.querySelector(".arkspace-portal")) return;

	ArkPortal.init();
});

const ArkPortal = {
	init() {
		this.setupBookingActions();
		this.setupCreditAnimation();
		this.setupBookButton();
		this.setupAutoRefresh();
	},

	/**
	 * Wire up cancel buttons on upcoming bookings
	 */
	setupBookingActions() {
		document.querySelectorAll("[data-booking-cancel]").forEach((btn) => {
			btn.addEventListener("click", function (e) {
				e.preventDefault();
				const bookingName = this.getAttribute("data-booking-cancel");
				ArkPortal.cancelBooking(bookingName);
			});
		});
	},

	/**
	 * Animate credit counter on load
	 */
	setupCreditAnimation() {
		const creditEl = document.querySelector(".ark-kpi-card.gold .kpi-value");
		if (!creditEl) return;

		const target = parseInt(creditEl.textContent) || 0;
		if (target <= 0) return;

		let current = 0;
		const step = Math.max(1, Math.ceil(target / 30));
		const interval = setInterval(() => {
			current = Math.min(current + step, target);
			creditEl.textContent = current;
			if (current >= target) clearInterval(interval);
		}, 30);
	},

	/**
	 * Quick Book button — opens space selector modal
	 */
	setupBookButton() {
		const bookBtn = document.querySelector('a[href="/arkspace_portal/book"]');
		if (!bookBtn) return;

		bookBtn.addEventListener("click", function (e) {
			e.preventDefault();
			ArkPortal.showBookingDialog();
		});
	},

	/**
	 * Auto-refresh portal every 60s for real-time updates
	 */
	setupAutoRefresh() {
		setInterval(() => {
			ArkPortal.refreshStats();
		}, 60000);
	},

	/**
	 * Cancel a booking with confirmation
	 */
	cancelBooking(bookingName) {
		frappe.confirm(
			__("Are you sure you want to cancel this booking?"),
			function () {
				frappe.call({
					method: "frappe.client.cancel",
					args: { doctype: "Space Booking", name: bookingName },
					callback: function () {
						frappe.show_alert({
							message: __("Booking cancelled successfully"),
							indicator: "green",
						});
						setTimeout(() => location.reload(), 1000);
					},
					error: function () {
						frappe.show_alert({
							message: __("Failed to cancel booking"),
							indicator: "red",
						});
					},
				});
			}
		);
	},

	/**
	 * Show booking dialog with available spaces
	 */
	showBookingDialog() {
		frappe.call({
			method: "arkspace.arkspace_spaces.api.get_available_spaces",
			callback: function (r) {
				const spaces = r.message || [];
				if (!spaces.length) {
					frappe.msgprint(__("No spaces available at the moment."));
					return;
				}

				const spaceOptions = spaces.map(
					(s) => `${s.name} — ${s.space_name} (${s.space_type})`
				);

				const d = new frappe.ui.Dialog({
					title: __("Book a Space"),
					fields: [
						{
							fieldtype: "Select",
							fieldname: "space",
							label: __("Space"),
							options: spaceOptions.join("\n"),
							reqd: 1,
						},
						{
							fieldtype: "Select",
							fieldname: "booking_type",
							label: __("Booking Type"),
							options: "Hourly\nDaily\nMonthly",
							default: "Hourly",
							reqd: 1,
						},
						{
							fieldtype: "Datetime",
							fieldname: "start_datetime",
							label: __("Start"),
							reqd: 1,
							default: frappe.datetime.now_datetime(),
						},
						{
							fieldtype: "Datetime",
							fieldname: "end_datetime",
							label: __("End"),
							reqd: 1,
						},
						{
							fieldtype: "Small Text",
							fieldname: "notes",
							label: __("Notes"),
						},
					],
					primary_action_label: __("Book Now"),
					primary_action: function (values) {
						const spaceName = values.space.split(" — ")[0];
						frappe.call({
							method: "arkspace.arkspace_spaces.api.create_booking",
							args: {
								space: spaceName,
								booking_type: values.booking_type,
								start_datetime: values.start_datetime,
								end_datetime: values.end_datetime,
							},
							callback: function (r) {
								d.hide();
								frappe.show_alert({
									message: __(
										"Booking created: {0}",
										[r.message.name]
									),
									indicator: "green",
								});
								setTimeout(() => location.reload(), 1500);
							},
							error: function () {
								frappe.show_alert({
									message: __("Booking failed. Please check availability."),
									indicator: "red",
								});
							},
						});
					},
				});
				d.show();
			},
		});
	},

	/**
	 * Refresh dashboard stats without full page reload
	 */
	refreshStats() {
		frappe.call({
			method: "arkspace.api.get_dashboard_stats",
			callback: function (r) {
				if (!r.message) return;
				const stats = r.message;
				// Update KPI cards if they exist
				const cards = document.querySelectorAll(".ark-kpi-card");
				if (cards.length >= 3) {
					const values = cards[0].querySelector(".kpi-value");
					if (values) values.textContent = stats.active_members || 0;
				}
			},
		});
	},
};
