// Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
// Developer Website: https://arkan.it.com
// License: MIT
// For license information, please see license.txt

/**
 * ARK Command Center
 *
 * Unified command screen with 3 tabs:
 *   1. Overview  — KPI dashboard + interactive space/booking graph
 *   2. Bookings  — Booking pipeline (Pending → Checked Out) flow graph
 *   3. CRM       — Lead pipeline (New → Converted) flow graph
 *
 * Consolidates the former ark-command + ark-flow pages into one.
 * Uses frappe_visual GraphEngine, VisualDashboard, FloatingWindow.
 */

frappe.pages["ark-command"].on_page_load = async function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("ARK Command Center"),
		single_column: true,
	});

	page.set_indicator("Live", "green");

	// ── Branch filter ──
	page.branch_field = page.add_field({
		fieldtype: "Link",
		fieldname: "branch",
		label: __("Branch"),
		options: "ARKSpace Branch",
		change: () => cmd.refresh(),
	});

	// ── Date filter (for Bookings tab) ──
	page.date_field = page.add_field({
		fieldtype: "Date",
		fieldname: "date",
		label: __("Date"),
		default: frappe.datetime.get_today(),
		change: () => { if (cmd.activeTab !== "overview") cmd.refresh(); },
	});

	page.set_primary_action(__("Refresh"), () => cmd.refresh(), "refresh");

	page.add_inner_button(__("Explorer"), () => frappe.set_route("ark-explorer"));
	page.add_inner_button(__("Live Plan"), () => frappe.set_route("ark-live"));
	page.add_inner_button(__("Community"), () => frappe.set_route("ark-community"));

	const cmd = new ArkCommandCenter(page);
	await cmd.init();
	cmd.refresh();

	setInterval(() => cmd.refresh(), 45000);
	frappe.realtime.on("space_status_changed", () => cmd.refresh());
	frappe.realtime.on("booking_created", () => cmd.refresh());
	frappe.realtime.on("booking_status_changed", () => cmd.refresh());
};

class ArkCommandCenter {
	constructor(page) {
		this.page = page;
		this.engine = null;
		this.activeTab = "overview"; // overview | bookings | crm
	}

	/* ─── Initialise layout ─── */
	async init() {
		await frappe.require("frappe_visual.bundle.js");

		const $body = $(this.page.body);
		$body.html(`
			<div class="ark-cmd" style="padding:0 15px">
				<!-- Tab bar -->
				<div class="ark-cmd-tabs" style="display:flex;gap:0;margin-bottom:16px;
					border-bottom:2px solid var(--border-color)">
					<button class="ark-tab active" data-tab="overview"
						style="padding:10px 24px;font-weight:600;border:none;
						background:none;cursor:pointer;border-bottom:2px solid transparent;
						margin-bottom:-2px;color:var(--text-color);font-size:13px">
						📊 ${__("Overview")}
					</button>
					<button class="ark-tab" data-tab="bookings"
						style="padding:10px 24px;font-weight:600;border:none;
						background:none;cursor:pointer;border-bottom:2px solid transparent;
						margin-bottom:-2px;color:var(--text-muted);font-size:13px">
						📅 ${__("Bookings")}
					</button>
					<button class="ark-tab" data-tab="crm"
						style="padding:10px 24px;font-weight:600;border:none;
						background:none;cursor:pointer;border-bottom:2px solid transparent;
						margin-bottom:-2px;color:var(--text-muted);font-size:13px">
						🎯 ${__("CRM")}
					</button>
				</div>

				<!-- Dashboard / summary row -->
				<div id="ark-cmd-dashboard" style="margin-bottom:12px"></div>

				<!-- Toolbar -->
				<div id="ark-cmd-toolbar" style="display:flex;gap:8px;align-items:center;
					margin-bottom:8px;flex-wrap:wrap"></div>

				<!-- Graph -->
				<div id="ark-cmd-graph" style="height:calc(100vh - 360px);min-height:400px;
					border:1px solid var(--border-color);border-radius:var(--border-radius-lg);
					background:var(--fg-color)"></div>
			</div>
		`);

		this.dashboardEl = document.getElementById("ark-cmd-dashboard");
		this.toolbarEl = document.getElementById("ark-cmd-toolbar");
		this.graphEl = document.getElementById("ark-cmd-graph");

		// Tab switching
		$body.find(".ark-tab").on("click", (e) => {
			const tab = $(e.currentTarget).data("tab");
			if (tab === this.activeTab) return;
			this.activeTab = tab;
			$body.find(".ark-tab").css({
				color: "var(--text-muted)", borderBottomColor: "transparent",
			}).removeClass("active");
			$(e.currentTarget).css({
				color: "var(--text-color)", borderBottomColor: "var(--primary)",
			}).addClass("active");
			this.refresh();
		});
	}

	/* ─── Refresh active tab ─── */
	async refresh() {
		const branch = this.page.branch_field?.get_value() || undefined;

		if (this.activeTab === "overview") {
			await this._refreshOverview(branch);
		} else if (this.activeTab === "bookings") {
			await this._refreshBookings(branch);
		} else {
			await this._refreshCRM(branch);
		}
	}

	/* ─── Tab 1: Overview ─── */
	async _refreshOverview(branch) {
		const [kpis, graph] = await Promise.all([
			frappe.xcall("arkspace.arkspace_core.visual_api.get_command_center_kpis", { branch }),
			frappe.xcall("arkspace.arkspace_core.visual_api.get_command_center_graph", { branch }),
		]);
		this._renderDashboard(kpis);
		this._renderGraph(graph, "elk-layered", { expandCollapse: true, antLines: true });
	}

	/* ─── Tab 2: Bookings Flow ─── */
	async _refreshBookings(branch) {
		const date = this.page.date_field?.get_value() || frappe.datetime.get_today();
		const data = await frappe.xcall(
			"arkspace.arkspace_core.visual_api.get_booking_flow", { branch, date },
		);
		this._renderFlowSummary(data.counts || {}, data.total || 0, "bookings");
		this._renderGraph(data, "elk-layered", {
			layoutOptions: { "elk.direction": "RIGHT" },
			antLines: true, pulseNodes: true,
		});
	}

	/* ─── Tab 3: CRM Pipeline ─── */
	async _refreshCRM(branch) {
		const data = await frappe.xcall(
			"arkspace.arkspace_core.visual_api.get_crm_pipeline", { branch },
		);
		this._renderFlowSummary(data.counts || {}, 0, "crm");
		this._renderGraph(data, "elk-layered", {
			layoutOptions: { "elk.direction": "RIGHT" },
			antLines: true, pulseNodes: true,
		});
	}

	/* ─── Renderers ─── */
	_renderDashboard(kpis) {
		if (!kpis?.length) return;
		frappe.visual.VisualDashboard.create(this.dashboardEl, kpis);
	}

	_renderFlowSummary(counts, total, mode) {
		const stages = mode === "crm"
			? ["New", "Contacted", "Tour Scheduled", "Negotiating", "Converted", "Lost"]
			: ["Pending", "Confirmed", "Checked In", "Checked Out", "Cancelled", "No Show"];

		const colors = {
			Pending: "#f59e0b", Confirmed: "#10b981", "Checked In": "#22c55e",
			"Checked Out": "#6b7280", Cancelled: "#ef4444", "No Show": "#9ca3af",
			New: "#f97316", Contacted: "#10b981", "Tour Scheduled": "#8b5cf6",
			Negotiating: "#f59e0b", Converted: "#22c55e", Lost: "#6b7280",
		};

		const totalVal = total || Object.values(counts).reduce((a, b) => a + b, 0);

		this.dashboardEl.innerHTML = `<div style="display:flex;gap:10px;flex-wrap:wrap">`
			+ stages.map(s => `
				<div style="flex:1;min-width:90px;padding:10px 12px;border-radius:var(--border-radius-lg);
					background:var(--fg-color);border:1px solid var(--border-color);text-align:center">
					<div style="font-size:20px;font-weight:700;color:${colors[s] || "#6b7280"}">${counts[s] || 0}</div>
					<div style="font-size:11px;color:var(--text-muted)">${__(s)}</div>
				</div>
			`).join("")
			+ `<div style="flex:1;min-width:90px;padding:10px 12px;border-radius:var(--border-radius-lg);
				background:var(--primary);color:white;text-align:center">
				<div style="font-size:20px;font-weight:700">${totalVal}</div>
				<div style="font-size:11px;opacity:0.8">${__("Total")}</div>
			</div></div>`;
	}

	_renderGraph(data, layout, opts = {}) {
		if (!data) return;
		if (this.engine) {
			try { this.engine.destroy(); } catch (_e) { /* ok */ }
		}
		this.toolbarEl.innerHTML = "";

		this.engine = new frappe.visual.GraphEngine({
			container: this.graphEl,
			nodes: data.nodes,
			edges: data.edges,
			layout: layout,
			layoutOptions: opts.layoutOptions || {},
			minimap: true,
			contextMenu: true,
			expandCollapse: opts.expandCollapse || false,
			animate: true,
			antLines: opts.antLines || false,
			pulseNodes: opts.pulseNodes || false,
			onNodeClick: (nd) => this._onNodeClick(nd),
			onNodeDblClick: (nd) => {
				if (nd.doctype && nd.docname) frappe.set_route("Form", nd.doctype, nd.docname);
			},
		});

		frappe.visual.LayoutManager.createToolbar(this.toolbarEl, this.engine);
		frappe.visual.LayoutManager.createSearchBar(this.toolbarEl, this.engine);
	}

	async _onNodeClick(nodeData) {
		if (!nodeData.doctype || !nodeData.docname) return;
		if (nodeData.meta?.is_stage) return;

		const html = await frappe.xcall(
			"arkspace.arkspace_core.visual_api.get_entity_detail",
			{ doctype: nodeData.doctype, docname: nodeData.docname },
		);

		const icons = {
			"Co-working Space": "🏢", "Space Booking": "📅", Customer: "👤",
			Membership: "🎫", "ARKSpace Branch": "🏛️", "Day Pass": "🎟️",
			"Visitor Log": "🚶", "Workspace Lead": "🎯",
		};

		new frappe.visual.FloatingWindow({
			title: nodeData.label || nodeData.docname,
			color: nodeData.borderColor || "#6366f1",
			content: html,
			width: 360, height: 320,
			icon: icons[nodeData.doctype] || "📋",
			minimizable: true, closable: true, resizable: true,
		});
	}
}
