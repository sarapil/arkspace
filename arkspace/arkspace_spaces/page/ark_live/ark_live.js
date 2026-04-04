// Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
// Developer Website: https://arkan.it.com
// License: MIT
// For license information, please see license.txt

/**
 * ARK Live — Interactive Space Viewer
 * عرض المساحات التفاعلي
 *
 * Unified page with 2 view modes:
 *   1. 2D Plan  — SVG overlay on floor plan PNG (original ark-live)
 *   2. Grid     — Card grid organized by floor (absorbed from floor-plan)
 *
 * Both modes share: summary bar, booking dialog, detail panel, auto-refresh.
 */

frappe.pages["ark-live"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("ARK Live — عرض المساحات التفاعلي"),
		single_column: true,
	});

	page.set_indicator("Live", "green");

	// Branch filter
	page.branch_field = page.add_field({
		fieldtype: "Link",
		fieldname: "branch",
		label: __("Branch — الفرع"),
		options: "Branch",
		change: () => arkLive.refresh(),
	});

	// Floor filter (for Grid mode)
	page.floor_field = page.add_field({
		fieldtype: "Select",
		fieldname: "floor",
		label: __("Floor — الطابق"),
		options: "",
		change: () => arkLive.refresh(),
	});

	page.set_primary_action(__("Refresh"), () => arkLive.refresh(), "refresh");
	page.set_secondary_action(__("Fullscreen"), () => arkLive.toggleFullscreen());

	const arkLive = new ArkLiveView(page);
	arkLive.refresh();

	setInterval(() => arkLive.refresh(), 30000);
	frappe.realtime.on("space_status_changed", () => arkLive.refresh());
	frappe.realtime.on("booking_created", () => arkLive.refresh());
};


/*──────────────────────────────────────────────────────────────
 * ZONE MAP — Maps floor plan image regions to Co-working Spaces
 * The floor plan image is 1015 x 802 pixels.
 * Coordinates in % for responsiveness.
 *──────────────────────────────────────────────────────────────*/
const ZONE_MAP = [
	{ id: "zone-a1", zoneLabel: "A1", points: "7.1,7.7 26.8,7.7 26.8,19.0 7.1,19.0" },
	{ id: "zone-a2", zoneLabel: "A2", points: "32.7,7.7 43.4,7.7 43.4,18.6 32.7,18.6" },
	{ id: "zone-a3", zoneLabel: "A3", points: "43.8,7.7 57.4,7.7 57.4,18.6 43.8,18.6" },
	{ id: "zone-a4", zoneLabel: "A4", points: "57.7,7.7 65.3,7.7 65.3,12.0 57.7,12.0" },
	{ id: "zone-a5", zoneLabel: "A5", points: "57.7,12.2 65.3,12.2 65.3,19.1 57.7,19.1" },
	{ id: "zone-a6", zoneLabel: "A6", points: "65.6,7.7 75.9,7.7 75.9,29.9 65.6,29.9" },
	{ id: "zone-b1", zoneLabel: "B1", points: "7.1,19.6 26.8,19.6 26.8,30.8 7.1,30.8" },
	{ id: "zone-b2", zoneLabel: "B2", points: "32.7,19.6 43.4,19.6 43.4,28.8 32.7,28.8" },
	{ id: "zone-b3", zoneLabel: "B3", points: "43.8,19.6 57.4,19.6 57.4,28.8 43.8,28.8" },
	{ id: "zone-b4", zoneLabel: "B4", points: "57.7,19.6 65.3,19.6 65.3,29.6 57.7,29.6" },
	{ id: "zone-c1", zoneLabel: "C1", points: "7.1,31.4 26.6,31.4 26.6,57.6 7.1,57.6" },
	{ id: "zone-c2", zoneLabel: "C2", points: "27.1,31.4 32.5,31.4 32.5,41.4 27.1,41.4" },
	{ id: "zone-hall", zoneLabel: "HALL", points: "69.0,37.4 93.6,37.4 93.6,93.5 69.0,93.5" },
];


class ArkLiveView {
	constructor(page) {
		this.page = page;
		this.$wrapper = $('<div class="ark-live-wrapper"></div>').appendTo(page.body);
		this.spaces = [];
		this.zoneSpaceMap = {};
		this.activeTooltip = null;
		this.viewMode = "plan"; // plan | grid
		this.gridData = null;   // cached floor-plan API response
	}

	/* ─── Refresh ─── */
	refresh() {
		const branch = this.page.branch_field?.get_value();

		if (this.viewMode === "plan") {
			frappe.call({
				method: "arkspace.arkspace_spaces.ark_live.get_live_plan_data",
				args: { branch: branch || undefined },
				callback: (r) => {
					if (r.message) {
						this.spaces = r.message.spaces;
						this._buildZoneMapping();
						this._renderPlan(r.message);
					}
				},
			});
		} else {
			const floor = this.page.floor_field?.get_value();
			frappe.call({
				method: "arkspace.arkspace_spaces.floor_plan.get_floor_plan_data",
				args: { branch, floor },
				callback: (r) => {
					if (r.message) {
						this.gridData = r.message;
						this._updateFloorOptions(r.message.available_floors);
						this._renderGrid(r.message);
					}
				},
			});
		}
	}

	/* ─── Common shell (view toggle + summary) ─── */
	_renderShell(summary) {
		const isGrid = this.viewMode === "grid";

		this.$wrapper.html(`
			<!-- View toggle -->
			<div class="ark-view-toggle" style="display:flex;gap:0;margin-bottom:12px;
				border-bottom:2px solid var(--border-color)">
				<button class="ark-vtab ${!isGrid ? 'active' : ''}" data-mode="plan"
					style="padding:8px 20px;font-weight:600;border:none;background:none;
					cursor:pointer;border-bottom:2px solid ${!isGrid ? 'var(--primary)' : 'transparent'};
					margin-bottom:-2px;color:${!isGrid ? 'var(--text-color)' : 'var(--text-muted)'};font-size:13px">
					🗺️ ${__("2D Plan — المخطط")}
				</button>
				<button class="ark-vtab ${isGrid ? 'active' : ''}" data-mode="grid"
					style="padding:8px 20px;font-weight:600;border:none;background:none;
					cursor:pointer;border-bottom:2px solid ${isGrid ? 'var(--primary)' : 'transparent'};
					margin-bottom:-2px;color:${isGrid ? 'var(--text-color)' : 'var(--text-muted)'};font-size:13px">
					📋 ${__("Grid View — عرض الشبكة")}
				</button>
			</div>

			<!-- Summary Bar -->
			<div class="ark-live-summary">
				<div class="ark-summary-card total">
					<i class="fa-solid fa-building"></i>
					<div class="ark-summary-info">
						<span class="ark-summary-value">${summary.total}</span>
						<span class="ark-summary-label">${__("Total Spaces")}</span>
					</div>
				</div>
				<div class="ark-summary-card available">
					<i class="fa-solid fa-check-circle"></i>
					<div class="ark-summary-info">
						<span class="ark-summary-value">${summary.available}</span>
						<span class="ark-summary-label">${__("Available")}</span>
					</div>
				</div>
				<div class="ark-summary-card occupied">
					<i class="fa-solid fa-user-clock"></i>
					<div class="ark-summary-info">
						<span class="ark-summary-value">${summary.occupied}</span>
						<span class="ark-summary-label">${__("Occupied")}</span>
					</div>
				</div>
				<div class="ark-summary-card maintenance">
					<i class="fa-solid fa-wrench"></i>
					<div class="ark-summary-info">
						<span class="ark-summary-value">${summary.maintenance || summary.reserved || 0}</span>
						<span class="ark-summary-label">${__("Maintenance")}</span>
					</div>
				</div>
			</div>

			<!-- Legend -->
			<div class="ark-live-legend">
				<span class="ark-legend-item"><span class="ark-dot available"></span> ${__("Available — متاح")}</span>
				<span class="ark-legend-item"><span class="ark-dot occupied"></span> ${__("Occupied — مشغول")}</span>
				<span class="ark-legend-item"><span class="ark-dot confirmed"></span> ${__("Confirmed — مؤكد")}</span>
				<span class="ark-legend-item"><span class="ark-dot membership"></span> ${__("Membership — عضوية")}</span>
				<span class="ark-legend-item"><span class="ark-dot maintenance"></span> ${__("Maintenance — صيانة")}</span>
				<span class="ark-legend-tip">
					<i class="fa-solid fa-mouse-pointer"></i>
					${__("Click on a space to view details or book")}
				</span>
			</div>

			<!-- Content area (filled by plan or grid renderer) -->
			<div id="ark-live-content"></div>

			<!-- Detail panel (shared) -->
			<div class="ark-live-detail-panel" id="ark-detail-panel">
				<div class="ark-detail-header">
					<h3 id="ark-detail-title"></h3>
					<button class="ark-detail-close" id="ark-detail-close">
						<i class="fa-solid fa-times"></i>
					</button>
				</div>
				<div class="ark-detail-body" id="ark-detail-body"></div>
			</div>
		`);

		// View toggle binding
		this.$wrapper.find(".ark-vtab").on("click", (e) => {
			const mode = $(e.currentTarget).data("mode");
			if (mode === this.viewMode) return;
			this.viewMode = mode;
			this.refresh();
		});

		// Close detail panel
		this.$wrapper.find("#ark-detail-close").on("click", () => {
			this.$wrapper.find("#ark-detail-panel").removeClass("open");
		});
	}

	/* ══════════════════════════════════════════════
	 * MODE 1:  2D Plan  (SVG overlay on PNG)
	 * ══════════════════════════════════════════════ */

	_buildZoneMapping() {
		this.zoneSpaceMap = {};
		const copy = [...this.spaces];
		ZONE_MAP.forEach((z, i) => { if (i < copy.length) this.zoneSpaceMap[z.id] = copy[i]; });
	}

	_renderPlan(data) {
		this._renderShell(data.summary);

		this.$wrapper.find("#ark-live-content").html(`
			<div class="ark-live-plan-container" id="ark-live-plan">
				<img src="/assets/arkspace/images/workspace-2d-plan.png"
					 class="ark-live-plan-img" alt="ARKSpace Floor Plan" draggable="false">
				<svg class="ark-live-svg-overlay" viewBox="0 0 100 100"
					 preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
					${this._svgZones()}
				</svg>
			</div>
		`);

		this._bindPlanEvents();
	}

	_svgZones() {
		let svg = "";
		for (const zone of ZONE_MAP) {
			const sp = this.zoneSpaceMap[zone.id];
			let cls = "unmapped";
			if (sp) {
				if (sp.status === "Maintenance") cls = "maintenance";
				else if (sp.occupancy) cls = sp.occupancy.type === "membership" ? "membership" :
					sp.occupancy.type === "confirmed" ? "confirmed" : "occupied";
				else if (sp.status === "Available") cls = "available";
				else cls = sp.status.toLowerCase().replace(" ", "-");
			}

			const pts = zone.points.split(" ").map(p => p.split(",").map(Number));
			const cx = pts.reduce((s, p) => s + p[0], 0) / pts.length;
			const cy = pts.reduce((s, p) => s + p[1], 0) / pts.length;
			const xs = pts.map(p => p[0]), ys = pts.map(p => p[1]);
			const zw = Math.max(...xs) - Math.min(...xs);
			const zh = Math.max(...ys) - Math.min(...ys);
			const fs = Math.min(zw / 6, zh / 4, 1.6);
			const subFs = fs * 0.65;

			svg += `<g class="ark-zone ${cls}" data-zone-id="${zone.id}">
				<polygon points="${zone.points}" />
				<text x="${cx}" y="${cy - fs * 0.3}" text-anchor="middle"
					  font-size="${fs}" class="ark-zone-label">${zone.zoneLabel}</text>`;

			if (sp) {
				const icon = cls === "available" ? "✓" : cls === "occupied" ? "●" :
					cls === "confirmed" ? "◉" : cls === "membership" ? "★" :
					cls === "maintenance" ? "⚠" : "?";
				svg += `<text x="${cx}" y="${cy + fs * 0.7}" text-anchor="middle"
					font-size="${subFs}" class="ark-zone-status">${icon} ${sp.space_type}</text>`;
				if (sp.occupancy?.member_name) {
					svg += `<text x="${cx}" y="${cy + fs * 1.5}" text-anchor="middle"
						font-size="${subFs * 0.85}" class="ark-zone-member">${sp.occupancy.member_name}</text>`;
				}
			}
			svg += `</g>`;
		}
		return svg;
	}

	_bindPlanEvents() {
		const self = this;

		this.$wrapper.find(".ark-zone").on("click", function (e) {
			e.stopPropagation();
			self._showSpaceDetail(self.zoneSpaceMap[$(this).data("zone-id")]);
		});

		this.$wrapper.find(".ark-zone").on("mouseenter", function (e) {
			const sp = self.zoneSpaceMap[$(this).data("zone-id")];
			if (sp) self._showTooltip(e, sp);
		}).on("mouseleave", () => self._hideTooltip());

		this.$wrapper.find(".ark-live-plan-container").on("click", (e) => {
			if (!$(e.target).closest(".ark-zone").length) {
				this.$wrapper.find("#ark-detail-panel").removeClass("open");
			}
		});
	}

	/* ══════════════════════════════════════════════
	 * MODE 2:  Grid View  (floor-organized cards)
	 * ══════════════════════════════════════════════ */

	_updateFloorOptions(floors) {
		const cur = this.page.floor_field?.get_value();
		const opts = ["", ...(floors || [])];
		if (this.page.floor_field?.df) this.page.floor_field.df.options = opts.join("\n");
		this.page.floor_field?.$input?.empty().append(
			opts.map(f => `<option value="${f}">${f || __("All Floors — كل الطوابق")}</option>`).join(""),
		);
		if (cur) this.page.floor_field?.set_value(cur);
	}

	_renderGrid(data) {
		this._renderShell(data.summary);
		const { floors } = data;

		let html = "";
		for (const floor of floors) {
			html += `
				<div class="fp-floor">
					<div class="fp-floor-header">
						<h3><i class="fa-solid fa-layer-group"></i> ${floor.floor}</h3>
						<span class="fp-floor-stats">
							${floor.available} ${__("available")} / ${floor.total} ${__("total")}
						</span>
					</div>
					<div class="fp-grid">`;

			for (const space of floor.spaces) {
				const cls = space.status.toLowerCase().replace(" ", "-");
				const memberInfo = space.member_name
					? `<div class="fp-space-member">${space.member_name}</div>` : "";
				const capBadge = space.capacity > 1
					? `<span class="fp-capacity">${space.capacity}</span>` : "";

				html += `
					<div class="fp-space ${cls}" data-space="${space.name}"
						 title="${space.space_name} — ${space.space_type} (${space.status})">
						<div class="fp-space-icon">
							<i class="${space.type_icon}"></i>${capBadge}
						</div>
						<div class="fp-space-name">${space.space_name}</div>
						<div class="fp-space-type">${space.space_type}</div>
						${memberInfo}
						<div class="fp-space-status">${__(space.status)}</div>
					</div>`;
			}
			html += `</div></div>`;
		}

		if (!floors.length) {
			html += `
				<div class="fp-empty">
					<i class="fa-solid fa-map" style="font-size:3rem;color:var(--ark-gold,#C4A962)"></i>
					<h3>${__("No spaces found")}</h3>
					<p>${__("Add Co-working Spaces to see them on the floor plan.")}</p>
				</div>`;
		}

		this.$wrapper.find("#ark-live-content").html(html);

		// Card click → open form
		this.$wrapper.find(".fp-space").on("click", function () {
			frappe.set_route("Form", "Co-working Space", $(this).data("space"));
		});

		// Right-click available → quick book
		this.$wrapper.find(".fp-space.available").on("contextmenu", function (e) {
			e.preventDefault();
			ArkLiveView.showBookingDialog($(this).data("space"));
		});
	}

	/* ══════════════════════════════════════════════
	 * Shared helpers
	 * ══════════════════════════════════════════════ */

	_showTooltip(e, space) {
		this._hideTooltip();
		const status = space.occupancy
			? (space.occupancy.type === "membership" ? __("Membership") :
			   space.occupancy.type === "confirmed" ? __("Confirmed") : __("Occupied"))
			: (space.status === "Maintenance" ? __("Maintenance") : __("Available"));

		const memberLine = space.occupancy?.member_name
			? `<div class="ark-tt-member"><i class="fa-solid fa-user"></i> ${space.occupancy.member_name}</div>` : "";
		const dateLine = space.occupancy
			? `<div class="ark-tt-dates"><i class="fa-solid fa-calendar"></i> ${space.occupancy.start} → ${space.occupancy.end}</div>` : "";

		const $tt = $(`<div class="ark-live-tooltip">
			<div class="ark-tt-title">${space.space_name}</div>
			<div class="ark-tt-type">${space.space_type} · ${__("Capacity")}: ${space.capacity}</div>
			<div class="ark-tt-status status-${status.toLowerCase()}">${status}</div>
			${memberLine}${dateLine}
		</div>`);

		$("body").append($tt);
		this.activeTooltip = $tt;
		$tt.css({ left: e.pageX + 15, top: e.pageY - 10 });

		requestAnimationFrame(() => {
			const r = $tt[0].getBoundingClientRect();
			if (r.right > window.innerWidth) $tt.css("left", e.pageX - r.width - 15);
			if (r.bottom > window.innerHeight) $tt.css("top", e.pageY - r.height - 10);
		});
	}

	_hideTooltip() {
		if (this.activeTooltip) { this.activeTooltip.remove(); this.activeTooltip = null; }
	}

	_showSpaceDetail(space) {
		if (!space) return;

		const $panel = this.$wrapper.find("#ark-detail-panel");
		this.$wrapper.find("#ark-detail-title").text(space.space_name);

		const cls = space.occupancy
			? (space.occupancy.type === "membership" ? "membership" :
			   space.occupancy.type === "confirmed" ? "confirmed" : "occupied")
			: (space.status === "Maintenance" ? "maintenance" : "available");

		const label = space.occupancy
			? (space.occupancy.type === "membership" ? __("Active Membership") :
			   space.occupancy.type === "confirmed" ? __("Confirmed Booking") : __("Currently Occupied"))
			: (space.status === "Maintenance" ? __("Under Maintenance") : __("Available for Booking"));

		let h = `
			<div class="ark-detail-status ${cls}">
				<i class="fa-solid ${cls === 'available' ? 'fa-check-circle' :
				                     cls === 'maintenance' ? 'fa-wrench' : 'fa-user-clock'}"></i>
				${label}
			</div>
			<div class="ark-detail-info">
				<div class="ark-detail-row"><span class="ark-detail-key">${__("Type")}</span><span class="ark-detail-val">${space.space_type}</span></div>
				<div class="ark-detail-row"><span class="ark-detail-key">${__("Branch")}</span><span class="ark-detail-val">${space.branch}</span></div>
				<div class="ark-detail-row"><span class="ark-detail-key">${__("Floor")}</span><span class="ark-detail-val">${space.floor || "—"}</span></div>
				<div class="ark-detail-row"><span class="ark-detail-key">${__("Capacity")}</span><span class="ark-detail-val">${space.capacity} ${__("persons")}</span></div>
				<div class="ark-detail-row"><span class="ark-detail-key">${__("Area")}</span><span class="ark-detail-val">${space.area_sqm || "—"} ${__("m²")}</span></div>`;

		if (space.hourly_rate)
			h += `<div class="ark-detail-row"><span class="ark-detail-key">${__("Hourly Rate")}</span><span class="ark-detail-val">${space.hourly_rate} ${__("EGP")}</span></div>`;
		if (space.daily_rate)
			h += `<div class="ark-detail-row"><span class="ark-detail-key">${__("Daily Rate")}</span><span class="ark-detail-val">${space.daily_rate} ${__("EGP")}</span></div>`;

		h += `</div>`;

		if (space.occupancy) {
			h += `<div class="ark-detail-section"><h4><i class="fa-solid fa-user"></i> ${__("Current Occupant")}</h4>
				<div class="ark-detail-occupant">
					<div class="ark-detail-row"><span class="ark-detail-key">${__("Member")}</span><span class="ark-detail-val">${space.occupancy.member_name}</span></div>
					<div class="ark-detail-row"><span class="ark-detail-key">${__("From")}</span><span class="ark-detail-val">${frappe.datetime.str_to_user(space.occupancy.start)}</span></div>
					<div class="ark-detail-row"><span class="ark-detail-key">${__("To")}</span><span class="ark-detail-val">${frappe.datetime.str_to_user(space.occupancy.end)}</span></div>
				</div></div>`;
		}

		if (space.upcoming_bookings?.length) {
			h += `<div class="ark-detail-section"><h4><i class="fa-solid fa-calendar-alt"></i> ${__("Upcoming Bookings")}</h4>`;
			for (const bk of space.upcoming_bookings) {
				h += `<div class="ark-detail-booking-card">
					<div class="ark-booking-member">${bk.member_name}</div>
					<div class="ark-booking-time">${frappe.datetime.str_to_user(bk.start_datetime)} — ${frappe.datetime.str_to_user(bk.end_datetime)}</div>
					<span class="ark-booking-status ${bk.status.toLowerCase()}">${__(bk.status)}</span>
				</div>`;
			}
			h += `</div>`;
		}

		h += `<div class="ark-detail-actions">`;
		if (space.status === "Available" && !space.occupancy)
			h += `<button class="btn btn-primary btn-sm ark-btn-book" data-space="${space.name}">
				<i class="fa-solid fa-calendar-plus"></i> ${__("Book Now — احجز الآن")}</button>`;
		h += `<button class="btn btn-default btn-sm ark-btn-open" data-space="${space.name}">
			<i class="fa-solid fa-external-link-alt"></i> ${__("Open Space")}</button></div>`;

		const $body = this.$wrapper.find("#ark-detail-body");
		$body.html(h);
		$panel.addClass("open");

		$body.find(".ark-btn-book").on("click", function () {
			ArkLiveView.showBookingDialog($(this).data("space"), () => $panel.removeClass("open"));
		});
		$body.find(".ark-btn-open").on("click", function () {
			frappe.set_route("Form", "Co-working Space", $(this).data("space"));
		});
	}

	static showBookingDialog(spaceName, onSuccess) {
		const now = frappe.datetime.now_datetime();
		const end = frappe.datetime.add_to_date(now, { hours: 2 });

		const dlg = new frappe.ui.Dialog({
			title: __("Book Space — حجز المساحة"),
			fields: [
				{ fieldtype: "HTML", fieldname: "space_info",
				  options: `<div class="alert alert-info mb-3"><i class="fa-solid fa-map-pin"></i> <strong>${spaceName}</strong></div>` },
				{ fieldtype: "Link", fieldname: "member", label: __("Member — العضو"),
				  options: "Customer", reqd: 1,
				  get_query: () => ({ filters: { customer_type: ["in", ["Individual", "Company"]] } }) },
				{ fieldtype: "Select", fieldname: "booking_type", label: __("Booking Type — نوع الحجز"),
				  options: "Hourly\nDaily", default: "Hourly", reqd: 1 },
				{ fieldtype: "Column Break" },
				{ fieldtype: "Datetime", fieldname: "start_datetime", label: __("Start — البداية"),
				  reqd: 1, default: now },
				{ fieldtype: "Datetime", fieldname: "end_datetime", label: __("End — النهاية"),
				  reqd: 1, default: end },
				{ fieldtype: "Section Break" },
				{ fieldtype: "Small Text", fieldname: "notes", label: __("Notes — ملاحظات") },
			],
			primary_action_label: __("Confirm Booking — تأكيد الحجز"),
			primary_action(vals) {
				frappe.call({
					method: "arkspace.arkspace_spaces.ark_live.quick_book_space",
					args: { space: spaceName, member: vals.member,
						booking_type: vals.booking_type,
						start_datetime: vals.start_datetime,
						end_datetime: vals.end_datetime, notes: vals.notes },
					callback(r) {
						if (r.message) {
							dlg.hide();
							frappe.show_alert({
								message: __("Booking {0} created for {1}!", [r.message.booking, r.message.member_name]),
								indicator: "green",
							});
							if (onSuccess) onSuccess();
						}
					},
				});
			},
		});
		dlg.show();
		dlg.$wrapper.find(".modal-dialog").css("max-width", "600px");
	}

	toggleFullscreen() {
		const el = this.$wrapper.find(".ark-live-plan-container")[0] || this.$wrapper[0];
		if (!document.fullscreenElement) el.requestFullscreen?.().catch(() => {});
		else document.exitFullscreen();
	}
}
