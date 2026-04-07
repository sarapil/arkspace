// Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
// License: GPL-3.0

/**
 * ARKSpace 3D Coworking Layout
 * ==============================
 * Integrates frappe_visual's 3D framework with ARKSpace coworking management.
 * Provides interactive 3D space visualization with desk availability,
 * zone-based occupancy tracking, and click-to-book functionality.
 *
 * Lazy-loaded — NOT included in app_include_js.
 *
 * Usage:
 *   await frappe.arkspace.layout3D.create("#container", { space: "SPACE-001" });
 */

frappe.provide("frappe.arkspace.layout3D");

frappe.arkspace.layout3D = {
	_loaded: false,

	async load() {
		if (this._loaded) return;
		await frappe.visual.load3D();
		this._loaded = true;
	},

	/**
	 * Create a 3D coworking space layout viewer.
	 * @param {string|Element} container — CSS selector or DOM element
	 * @param {Object} opts — { space, zone, modelUrl, date }
	 */
	async create(container, opts = {}) {
		await this.load();

		const el = typeof container === "string" ? document.querySelector(container) : container;
		if (!el) return;

		const { ThreeEngine, CoworkingOverlay } = frappe.visual.three;

		const engine = new ThreeEngine(el, {
			background: opts.background || "#f1f5f9",
			shadows: true,
			antialias: true,
		});
		engine.init();

		// Apply coworking overlay
		const overlay = new CoworkingOverlay(engine, {
			statusColors: {
				available: 0x22c55e,
				occupied: 0xef4444,
				reserved: 0x3b82f6,
				maintenance: 0x6b7280,
			},
		});

		// Load space model if provided
		if (opts.modelUrl) {
			const { ModelLoader } = frappe.visual.three;
			const loader = new ModelLoader(engine);
			try {
				const model = await loader.load(opts.modelUrl);
				engine.scene.add(model);
			} catch (e) {
				console.error("Failed to load space model:", e);
			}
		}

		// Load desk/seat data
		if (opts.space) {
			try {
				const filters = { parent_space: opts.space };
				if (opts.zone) filters.zone = opts.zone;

				const desks = await frappe.call({
					method: "frappe.client.get_list",
					args: {
						doctype: "AS Desk",
						filters,
						fields: ["name", "desk_number", "zone", "status",
							"desk_type", "mesh_name", "current_member"],
						limit_page_length: 0,
					},
				});

				if (desks.message) {
					const units = desks.message.map(d => ({
						id: d.name,
						meshName: d.mesh_name || d.desk_number,
						zone: d.zone || "default",
						status: (d.status || "available").toLowerCase(),
						label: `${d.desk_number} — ${__(d.desk_type || "Hot Desk")}`,
						metadata: {
							member: d.current_member,
							type: d.desk_type,
						},
					}));
					overlay.registerDesks(units);
				}
			} catch (e) {
				console.warn("Could not load AS Desk data:", e);
			}
		}

		// Click handler — show desk details / initiate booking
		overlay.onDeskClick = (deskData) => {
			if (!deskData) return;

			if (deskData.status === "available") {
				frappe.confirm(
					__("Book desk {0}?", [deskData.label]),
					() => frappe.new_doc("AS Booking", { desk: deskData.id }),
				);
			} else {
				frappe.set_route("Form", "AS Desk", deskData.id);
			}
		};

		return { engine, overlay };
	},

	/**
	 * Create a dashboard with 3D layout + occupancy stats.
	 */
	async createDashboard(container, opts = {}) {
		const el = typeof container === "string" ? document.querySelector(container) : container;
		if (!el) return;

		el.innerHTML = `
			<div class="as-layout-dashboard fv-fx-page-enter" style="display:flex;gap:16px;height:500px;">
				<div class="as-layout-viewer" style="flex:3;border-radius:12px;overflow:hidden;border:1px solid var(--border-color);"></div>
				<div class="as-layout-stats fv-fx-glass" style="flex:1;padding:16px;border-radius:12px;overflow-y:auto;">
					<h4>${__("Space Occupancy")}</h4>
					<div class="as-stats-content"></div>
				</div>
			</div>
		`;

		const viewerEl = el.querySelector(".as-layout-viewer");
		const statsEl = el.querySelector(".as-stats-content");

		const result = await this.create(viewerEl, opts);
		if (!result) return;

		const summary = result.overlay.getOccupancyStats();
		const statusLabels = {
			available: { label: __("Available"), color: "#22c55e" },
			occupied: { label: __("Occupied"), color: "#ef4444" },
			reserved: { label: __("Reserved"), color: "#3b82f6" },
			maintenance: { label: __("Maintenance"), color: "#6b7280" },
		};

		let statsHTML = `
			<div style="margin-bottom:12px;">
				<div class="text-muted">${__("Total Desks")}</div>
				<div style="font-size:2em;font-weight:bold;color:var(--primary);">${summary.total}</div>
			</div>
			<div style="margin-bottom:12px;">
				<div class="text-muted">${__("Utilization")}</div>
				<div style="font-size:1.5em;font-weight:bold;">${summary.utilizationRate}%</div>
			</div>
			<hr>
		`;

		for (const [status, info] of Object.entries(statusLabels)) {
			const count = summary.byStatus?.[status] || 0;
			statsHTML += `
				<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
					<span style="display:flex;align-items:center;gap:6px;">
						<span style="width:10px;height:10px;border-radius:50%;background:${info.color};display:inline-block;"></span>
						${info.label}
					</span>
					<strong>${count}</strong>
				</div>
			`;
		}

		// Zone breakdown
		if (summary.zones && Object.keys(summary.zones).length > 1) {
			statsHTML += `<hr><h5>${__("By Zone")}</h5>`;
			for (const [zone, zoneData] of Object.entries(summary.zones)) {
				statsHTML += `
					<div style="margin-bottom:6px;">
						<div style="display:flex;justify-content:space-between;">
							<span>${zone}</span>
							<span>${zoneData.occupied}/${zoneData.total}</span>
						</div>
						<div style="height:4px;background:var(--bg-light-gray);border-radius:2px;margin-top:2px;">
							<div style="height:100%;width:${zoneData.rate}%;background:var(--primary);border-radius:2px;"></div>
						</div>
					</div>
				`;
			}
		}

		statsEl.innerHTML = statsHTML;
		return result;
	},
};
