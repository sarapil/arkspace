frappe.pages["arkspace-3d-map"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("3D Space Map"),
		single_column: true,
	});
	wrapper.arkspace_map = new ARKSpace3DMap(page);
};

frappe.pages["arkspace-3d-map"].on_page_show = function (wrapper) {
	if (wrapper.arkspace_map) {
		const space = frappe.get_route()[1];
		if (space) wrapper.arkspace_map.load_space(space);
		wrapper.arkspace_map.resume();
	}
};

frappe.pages["arkspace-3d-map"].on_page_hide = function (wrapper) {
	if (wrapper.arkspace_map) wrapper.arkspace_map.pause();
};

class ARKSpace3DMap {
	constructor(page) {
		this.page = page;
		this.current_space = null;
		this.engine = null;
		this.auto_refresh = null;
		this.setup_controls();
		this.render_layout();
	}

	setup_controls() {
		this.page.add_field({
			fieldname: "space",
			label: __("Space"),
			fieldtype: "Link",
			options: "AS Space",
			change: () => {
				const val = this.page.fields_dict.space.get_value();
				if (val) this.load_space(val);
			},
		});

		this.page.add_field({
			fieldname: "floor",
			label: __("Floor"),
			fieldtype: "Select",
			options: [__("All Floors")],
			change: () => this.filter_floor(),
		});

		this.page.add_inner_button(__("Screenshot"), () => this.screenshot(), __("Export"));
		this.page.add_inner_button(__("Fullscreen"), () => this.toggle_fullscreen());

		this.page.add_action_item(__("Toggle Auto-Refresh"), () => this.toggle_auto_refresh());

		// XR integration — VR space tour + AR desk planning
		frappe.base_base?.xr_mixin?.attach(this, {
			get_engine: () => this.engine,
			get_spatial_data: () => this.getXRPanels(),
			vr_options: { startPosition: [0, 1.7, 6] },
		});
	}

	getXRPanels() {
		if (!this.current_space) return [];
		const total = this.page.main.find(".total-desks").text();
		const avail = this.page.main.find(".available-desks").text();
		return [
			{ content: `<h3>${this.current_space}</h3><p>${__("Desks")}: ${total} | ${__("Available")}: ${avail}</p>`, position: [0, 2.5, -4], billboard: true },
		];
	}

	render_layout() {
		const container = this.page.main.find("#arkspace-3d-map-container");
		container.html(`
			<div class="arkspace-map-wrapper" style="display:flex; gap:12px; min-height:calc(100vh - 160px);">
				<div class="map-main" style="flex:1; display:flex; flex-direction:column; gap:12px;">
					<div class="zone-stats" style="display:grid; grid-template-columns:repeat(auto-fit,minmax(140px,1fr)); gap:8px;">
						<div class="stat-card fv-fx-glass fv-fx-hover-lift" style="padding:12px; border-radius:8px; text-align:center;">
							<div class="stat-label" style="font-size:11px; color:var(--text-muted);">${__("Total Desks")}</div>
							<div class="stat-value total-desks" style="font-size:24px; font-weight:700;">0</div>
						</div>
						<div class="stat-card fv-fx-glass fv-fx-hover-lift" style="padding:12px; border-radius:8px; text-align:center;">
							<div class="stat-label" style="font-size:11px; color:var(--text-muted);">${__("Occupied")}</div>
							<div class="stat-value occupied-desks" style="font-size:24px; font-weight:700; color:var(--red-500);">0</div>
						</div>
						<div class="stat-card fv-fx-glass fv-fx-hover-lift" style="padding:12px; border-radius:8px; text-align:center;">
							<div class="stat-label" style="font-size:11px; color:var(--text-muted);">${__("Available")}</div>
							<div class="stat-value available-desks" style="font-size:24px; font-weight:700; color:var(--green-500);">0</div>
						</div>
						<div class="stat-card fv-fx-glass fv-fx-hover-lift" style="padding:12px; border-radius:8px; text-align:center;">
							<div class="stat-label" style="font-size:11px; color:var(--text-muted);">${__("Occupancy")}</div>
							<div class="stat-value occupancy-rate" style="font-size:24px; font-weight:700;">0%</div>
						</div>
					</div>
					<div class="viewport-3d fv-fx-glass" style="flex:1; min-height:500px; border-radius:8px; position:relative; overflow:hidden;">
						<div class="viewport-placeholder" style="display:flex; align-items:center; justify-content:center; height:100%; color:var(--text-muted);">
							<div style="text-align:center;">
								<div style="font-size:48px; margin-bottom:12px;">🏢</div>
								<div>${__("Select a space to view 3D map")}</div>
							</div>
						</div>
					</div>
					<div class="zone-legend" style="display:flex; gap:16px; flex-wrap:wrap; padding:8px;">
						<span style="display:flex; align-items:center; gap:4px;">
							<span style="width:12px; height:12px; border-radius:50%; background:var(--green-500);"></span>
							${__("Available")}
						</span>
						<span style="display:flex; align-items:center; gap:4px;">
							<span style="width:12px; height:12px; border-radius:50%; background:var(--red-500);"></span>
							${__("Occupied")}
						</span>
						<span style="display:flex; align-items:center; gap:4px;">
							<span style="width:12px; height:12px; border-radius:50%; background:var(--blue-500);"></span>
							${__("Reserved")}
						</span>
						<span style="display:flex; align-items:center; gap:4px;">
							<span style="width:12px; height:12px; border-radius:50%; background:var(--yellow-500);"></span>
							${__("Meeting Room")}
						</span>
						<span style="display:flex; align-items:center; gap:4px;">
							<span style="width:12px; height:12px; border-radius:50%; background:var(--orange-500);"></span>
							${__("Maintenance")}
						</span>
					</div>
				</div>
				<div class="map-sidebar fv-fx-glass" style="width:280px; border-radius:8px; padding:16px; overflow-y:auto; max-height:calc(100vh - 160px);">
					<h6 style="margin-bottom:12px;">${__("Zone Filter")}</h6>
					<div class="zone-filters" style="display:flex; flex-direction:column; gap:6px; margin-bottom:16px;">
						<label style="display:flex; align-items:center; gap:6px; cursor:pointer;">
							<input type="checkbox" data-zone="hot-desk" checked> ${__("Hot Desks")}
						</label>
						<label style="display:flex; align-items:center; gap:6px; cursor:pointer;">
							<input type="checkbox" data-zone="dedicated" checked> ${__("Dedicated Desks")}
						</label>
						<label style="display:flex; align-items:center; gap:6px; cursor:pointer;">
							<input type="checkbox" data-zone="private-office" checked> ${__("Private Offices")}
						</label>
						<label style="display:flex; align-items:center; gap:6px; cursor:pointer;">
							<input type="checkbox" data-zone="meeting-room" checked> ${__("Meeting Rooms")}
						</label>
						<label style="display:flex; align-items:center; gap:6px; cursor:pointer;">
							<input type="checkbox" data-zone="event-space" checked> ${__("Event Spaces")}
						</label>
					</div>
					<hr>
					<h6 style="margin:12px 0;">${__("Desk Detail")}</h6>
					<div class="desk-detail" style="color:var(--text-muted); font-size:12px;">
						${__("Click a desk on the map")}
					</div>
					<hr>
					<h6 style="margin:12px 0;">${__("Upcoming Bookings")}</h6>
					<div class="upcoming-bookings" style="font-size:12px; color:var(--text-muted);">
						${__("No bookings today")}
					</div>
				</div>
			</div>
		`);

		container.find(".zone-filters input").on("change", () => this.apply_zone_filters());
	}

	async load_space(space_name) {
		this.current_space = space_name;
		frappe.dom.freeze(__("Loading space map..."));

		try {
			const space = await frappe.xcall(
				"frappe.client.get",
				{ doctype: "AS Space", name: space_name }
			);

			const desks = await frappe.xcall(
				"frappe.client.get_list",
				{
					doctype: "AS Desk",
					filters: { space: space_name },
					fields: ["name", "desk_name", "desk_type", "status", "floor", "zone",
						"member", "member_name", "x_pos", "y_pos"],
					limit_page_length: 0,
				}
			);

			this.update_stats(desks);
			this.update_floors(desks);
			await this.render_3d_map(space, desks);
			this.load_upcoming_bookings(space_name);
		} catch (e) {
			frappe.msgprint({ title: __("Error"), indicator: "red", message: e.message || __("Failed to load space") });
		} finally {
			frappe.dom.unfreeze();
		}
	}

	update_stats(desks) {
		const container = this.page.main.find("#arkspace-3d-map-container");
		const total = desks.length;
		const occupied = desks.filter((d) => d.status === "Occupied").length;
		const available = desks.filter((d) => d.status === "Available").length;
		const rate = total > 0 ? Math.round((occupied / total) * 100) : 0;

		container.find(".total-desks").text(total);
		container.find(".occupied-desks").text(occupied);
		container.find(".available-desks").text(available);
		container.find(".occupancy-rate").text(rate + "%");
	}

	update_floors(desks) {
		const floors = [...new Set(desks.map((d) => d.floor).filter(Boolean))].sort();
		const field = this.page.fields_dict.floor;
		const options = [__("All Floors"), ...floors];
		field.df.options = options;
		field.refresh();
	}

	async render_3d_map(space, desks) {
		const viewport = this.page.main.find(".viewport-3d");
		viewport.find(".viewport-placeholder").remove();

		try {
			await frappe.require("fv_3d.bundle.js");

			if (!this.engine) {
				this.engine = await frappe.visual.three.engine({
					container: viewport[0],
					background: 0xf8f9fa,
					controls: "orbit",
					grid: true,
					ambient_light: 0.6,
				});
			}

			this.engine.clearScene();

			const overlay = await frappe.visual.three.coworkingOverlay({
				engine: this.engine,
			});

			const status_map = {};
			desks.forEach((d) => { status_map[d.name] = d.status; });

			overlay.setDeskStatuses(status_map);
			overlay.showZones(true);
			overlay.showCapacity(true);

			desks.forEach((desk) => {
				const x = (desk.x_pos || Math.random() * 20 - 10);
				const z = (desk.y_pos || Math.random() * 20 - 10);

				this.engine.addBox({
					id: desk.name,
					position: [x, 0.4, z],
					size: desk.desk_type === "Private Office" ? [2.5, 0.8, 2.5] : [1.2, 0.8, 0.8],
					color: this.get_desk_color(desk),
					metadata: desk,
				});
			});

			this.engine.onSelect((obj) => {
				if (obj && obj.userData) this.show_desk_detail(obj.userData);
			});

			this.engine.fitAll();
		} catch (e) {
			viewport.html(`<div style="padding:40px; text-align:center; color:var(--text-muted);">
				<p>${__("3D engine not available. Install frappe_visual for full 3D support.")}</p>
				<p style="font-size:12px;">${e.message || ""}</p>
			</div>`);
		}
	}

	get_desk_color(desk) {
		const colors = {
			Available: 0x22c55e,
			Occupied: 0xef4444,
			Reserved: 0x3b82f6,
			Maintenance: 0xf97316,
		};
		if (desk.desk_type === "Meeting Room") return 0xeab308;
		return colors[desk.status] || 0x94a3b8;
	}

	show_desk_detail(desk) {
		const detail = this.page.main.find(".desk-detail");
		const status_color = { Available: "green", Occupied: "red", Reserved: "blue", Maintenance: "orange" };
		detail.html(`
			<div style="display:flex; flex-direction:column; gap:8px;">
				<div style="font-weight:600; font-size:14px;">${frappe.utils.escape_html(desk.desk_name || desk.name)}</div>
				<div><span class="indicator-pill ${status_color[desk.status] || "gray"}">${__(desk.status)}</span></div>
				<div><strong>${__("Type")}:</strong> ${__(desk.desk_type || "Hot Desk")}</div>
				<div><strong>${__("Zone")}:</strong> ${__(desk.zone || "-")}</div>
				<div><strong>${__("Floor")}:</strong> ${desk.floor || "-"}</div>
				${desk.member_name ? `<div><strong>${__("Member")}:</strong> ${frappe.utils.escape_html(desk.member_name)}</div>` : ""}
				<div style="margin-top:8px; display:flex; gap:6px;">
					${desk.status === "Available" ? `<button class="btn btn-primary btn-xs btn-book">${__("Book")}</button>` : ""}
					<button class="btn btn-default btn-xs btn-open">${__("Open")}</button>
				</div>
			</div>
		`);

		detail.find(".btn-book").on("click", () => {
			frappe.new_doc("AS Booking", { desk: desk.name, space: this.current_space });
		});
		detail.find(".btn-open").on("click", () => {
			frappe.set_route("Form", "AS Desk", desk.name);
		});
	}

	async load_upcoming_bookings(space_name) {
		try {
			const bookings = await frappe.xcall(
				"frappe.client.get_list",
				{
					doctype: "AS Booking",
					filters: {
						space: space_name,
						booking_date: [">=", frappe.datetime.get_today()],
						status: ["in", ["Confirmed", "Pending"]],
					},
					fields: ["name", "member_name", "desk", "booking_date", "status"],
					order_by: "booking_date asc",
					limit_page_length: 10,
				}
			);

			const el = this.page.main.find(".upcoming-bookings");
			if (!bookings.length) {
				el.html(`<span style="color:var(--text-muted);">${__("No upcoming bookings")}</span>`);
				return;
			}
			el.html(bookings.map((b) => `
				<div style="padding:6px 0; border-bottom:1px solid var(--border-color); cursor:pointer;"
					 data-name="${frappe.utils.escape_html(b.name)}">
					<div style="font-weight:500;">${frappe.utils.escape_html(b.member_name || b.name)}</div>
					<div style="font-size:11px; color:var(--text-muted);">
						${frappe.datetime.str_to_user(b.booking_date)} · ${__(b.status)}
					</div>
				</div>
			`).join(""));

			el.find("[data-name]").on("click", function () {
				frappe.set_route("Form", "AS Booking", $(this).data("name"));
			});
		} catch {
			// bookings fetch optional
		}
	}

	filter_floor() {
		if (!this.engine) return;
		const floor = this.page.fields_dict.floor.get_value();
		if (floor === __("All Floors")) {
			this.engine.showAll();
		} else {
			this.engine.filterByMetadata("floor", floor);
		}
	}

	apply_zone_filters() {
		if (!this.engine) return;
		const checked = [];
		this.page.main.find(".zone-filters input:checked").each(function () {
			checked.push($(this).data("zone"));
		});
		this.engine.filterByMetadata("desk_type", checked, "include");
	}

	toggle_auto_refresh() {
		if (this.auto_refresh) {
			clearInterval(this.auto_refresh);
			this.auto_refresh = null;
			frappe.show_alert({ message: __("Auto-refresh OFF"), indicator: "gray" });
		} else {
			this.auto_refresh = setInterval(() => {
				if (this.current_space) this.load_space(this.current_space);
			}, 30000);
			frappe.show_alert({ message: __("Auto-refresh ON (30s)"), indicator: "green" });
		}
	}

	screenshot() {
		if (this.engine) this.engine.screenshot(`arkspace_${this.current_space || "map"}.png`);
	}

	toggle_fullscreen() {
		const el = this.page.main.find(".viewport-3d")[0];
		if (!document.fullscreenElement) {
			el.requestFullscreen?.();
		} else {
			document.exitFullscreen?.();
		}
	}

	resume() {
		if (this.engine) this.engine.resume?.();
	}

	pause() {
		if (this.auto_refresh) {
			clearInterval(this.auto_refresh);
			this.auto_refresh = null;
		}
		if (this.engine) this.engine.pause?.();
	}
}
