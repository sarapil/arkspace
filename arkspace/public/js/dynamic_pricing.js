// Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
// Developer Website: https://arkan.it.com
// License: MIT
// For license information, please see license.txt

/**
 * ARKSpace Dynamic Pricing — Client-side Preview
 *
 * Shows real-time pricing adjustments on the Space Booking form.
 */

frappe.provide("arkspace.pricing");

/**
 * Fetch and display the dynamic rate for the current booking form.
 */
arkspace.pricing.preview_rate = function (frm) {
	if (!frm.doc.space || !frm.doc.start_datetime || !frm.doc.end_datetime) {
		return;
	}

	frappe.call({
		method: "arkspace.arkspace_spaces.pricing_engine.get_dynamic_rate",
		args: {
			space: frm.doc.space,
			booking_type: frm.doc.booking_type || "Hourly",
			start_datetime: frm.doc.start_datetime,
			end_datetime: frm.doc.end_datetime,
			duration_hours: frm.doc.duration_hours || 0,
			member: frm.doc.member || null,
		},
		callback: function (r) {
			if (!r.message) return;

			const data = r.message;
			if (!data.adjustments || !data.adjustments.length) {
				// No dynamic pricing — clear any previous indicator
				frm.dashboard.clear_headline();
				return;
			}

			// Update rate field
			frm.set_value("rate", data.final_rate);

			// Build adjustment summary
			let lines = [];
			data.adjustments.forEach(function (adj) {
				const arrow = adj.change > 0 ? "↑" : "↓";
				const color = adj.change > 0 ? "red" : "green";
				lines.push(
					`<span style="color:var(--${color}-600)">${arrow} ${adj.rule_name}: ${adj.change_pct > 0 ? "+" : ""}${adj.change_pct}%</span>`
				);
			});

			const headline =
				`<span class="indicator-pill yellow">` +
				__("Dynamic Pricing") +
				`</span> ` +
				__("Base: {0} → Final: {1}", [
					format_currency(data.base_rate, frm.doc.currency),
					format_currency(data.final_rate, frm.doc.currency),
				]) +
				` <small>(${lines.join(", ")})</small>`;

			frm.dashboard.set_headline(headline);
		},
	});
};


// ═══════════════════════════════════════════════════════════════════════════
// Form Script: Space Booking — Dynamic Pricing Preview
// ═══════════════════════════════════════════════════════════════════════════

frappe.ui.form.on("Space Booking", {
	space: function (frm) {
		arkspace.pricing.preview_rate(frm);
	},
	booking_type: function (frm) {
		arkspace.pricing.preview_rate(frm);
	},
	start_datetime: function (frm) {
		arkspace.pricing.preview_rate(frm);
	},
	end_datetime: function (frm) {
		arkspace.pricing.preview_rate(frm);
	},
	member: function (frm) {
		arkspace.pricing.preview_rate(frm);
	},
});
