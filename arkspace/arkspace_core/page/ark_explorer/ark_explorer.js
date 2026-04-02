/**
 * ARK Explorer — المستكشف المركزي
 *
 * Radial relationship explorer: pick any entity (space, member, branch,
 * booking, membership) and see ALL its relationships radiate outward.
 * Double-click any node to re-center the exploration on it.
 *
 * Pattern: "Central Explorer" — elk-radial layout, depth-expandable.
 */

frappe.pages["ark-explorer"].on_page_load = async function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("ARK Explorer — المستكشف"),
		single_column: true,
	});

	// ── Entity selection fields ──
	page.doctype_field = page.add_field({
		fieldtype: "Select",
		fieldname: "explore_doctype",
		label: __("Entity Type — نوع الكيان"),
		options: [
			"Co-working Space", "Customer", "Membership", "Space Booking",
			"ARKSpace Branch", "Day Pass", "Membership Plan", "Workspace Lead",
			"Workspace Tour", "Member Contract", "Community Event",
		].join("\n"),
		default: "Co-working Space",
		change: () => {
			page.entity_field.df.options = page.doctype_field.get_value();
			page.entity_field.set_value("");
			page.entity_field.refresh();
		},
	});

	page.entity_field = page.add_field({
		fieldtype: "Link",
		fieldname: "explore_entity",
		label: __("Entity — الكيان"),
		options: "Co-working Space",
		change: () => {
			const dt = page.doctype_field.get_value();
			const dn = page.entity_field.get_value();
			if (dt && dn) explorer.explore(dt, dn);
		},
	});

	page.depth_field = page.add_field({
		fieldtype: "Select",
		fieldname: "depth",
		label: __("Depth — العمق"),
		options: "1\n2\n3",
		default: "1",
	});

	page.set_primary_action(__("Explore"), () => {
		const dt = page.doctype_field.get_value();
		const dn = page.entity_field.get_value();
		if (dt && dn) explorer.explore(dt, dn);
		else frappe.show_alert({ message: __("Select an entity to explore"), indicator: "orange" });
	}, "search");

	const explorer = new ArkExplorer(page);
	await explorer.init();

	// Check route params: /app/ark-explorer?doctype=X&name=Y
	const params = frappe.utils.get_url_params();
	if (params.doctype && params.name) {
		page.doctype_field.set_value(params.doctype);
		setTimeout(() => {
			page.entity_field.df.options = params.doctype;
			page.entity_field.set_value(params.name);
			page.entity_field.refresh();
		}, 300);
	}
};


class ArkExplorer {
	constructor(page) {
		this.page = page;
		this.engine = null;
		this.history = [];
	}

	async init() {
		await frappe.require("frappe_visual.bundle.js");

		const $body = $(this.page.body);
		$body.html(`
			<div class="ark-explorer-wrapper" style="padding:0 15px">
				<div id="ark-exp-breadcrumb"
					style="margin-bottom:8px;display:flex;gap:6px;flex-wrap:wrap;
					font-size:12px;color:var(--text-muted)"></div>
				<div id="ark-exp-toolbar"
					style="display:flex;gap:8px;align-items:center;
					margin-bottom:8px;flex-wrap:wrap"></div>
				<div id="ark-exp-graph"
					style="height:calc(100vh - 280px);min-height:450px;
					border:1px solid var(--border-color);
					border-radius:var(--border-radius-lg);
					background:var(--fg-color)"></div>
			</div>
		`);

		this.graphEl = document.getElementById("ark-exp-graph");
		this.toolbarEl = document.getElementById("ark-exp-toolbar");
		this.breadcrumbEl = document.getElementById("ark-exp-breadcrumb");

		// Placeholder message
		this.graphEl.innerHTML = `
			<div style="display:flex;align-items:center;justify-content:center;
				height:100%;color:var(--text-muted);font-size:18px">
				<div style="text-align:center">
					<div style="font-size:64px;margin-bottom:16px">🔍</div>
					<div>${__("Select an entity and click Explore")}</div>
					<div style="font-size:13px;margin-top:8px">
						${__("اختر كياناً واضغط استكشاف")}
					</div>
				</div>
			</div>
		`;
	}

	async explore(doctype, docname) {
		const depth = this.page.depth_field?.get_value() || 1;

		frappe.show_alert({ message: __("Loading exploration…"), indicator: "blue" });

		const data = await frappe.xcall(
			"arkspace.arkspace_core.visual_api.get_space_explorer",
			{ doctype, docname, depth },
		);

		if (!data || !data.nodes.length) {
			frappe.show_alert({ message: __("No relationships found"), indicator: "orange" });
			return;
		}

		// Update breadcrumb history
		this.history.push({ doctype, docname });
		if (this.history.length > 10) this.history.shift();
		this.renderBreadcrumb();

		this.renderGraph(data, doctype, docname);
	}

	renderBreadcrumb() {
		this.breadcrumbEl.innerHTML = this.history.map((h, i) => {
			const sep = i > 0 ? '<span style="margin:0 2px">→</span>' : "";
			return `${sep}<a href="#" class="ark-exp-bc-link"
				data-dt="${h.doctype}" data-dn="${h.docname}"
				style="color:var(--text-color)">${h.docname}</a>`;
		}).join("");

		this.breadcrumbEl.querySelectorAll(".ark-exp-bc-link").forEach(link => {
			link.addEventListener("click", (e) => {
				e.preventDefault();
				this.explore(link.dataset.dt, link.dataset.dn);
			});
		});
	}

	renderGraph(data, centerDoctype, centerDocname) {
		if (this.engine) {
			try { this.engine.destroy(); } catch (_e) { /* ok */ }
		}
		this.toolbarEl.innerHTML = "";

		// Mark center node
		const centerId = `n-${centerDoctype.replace(/ /g, "_")}-${centerDocname.replace(/ /g, "_")}`;
		data.nodes.forEach(n => {
			if (n.id === centerId) {
				n.width = 80;
				n.height = 80;
				n.classes = "fv-pulse";
			}
		});

		this.engine = new frappe.visual.GraphEngine({
			container: this.graphEl,
			nodes: data.nodes,
			edges: data.edges,
			layout: "elk-radial",
			minimap: true,
			contextMenu: true,
			expandCollapse: false,
			animate: true,
			antLines: false,
			pulseNodes: true,
			onNodeClick: (nodeData) => this.onNodeClick(nodeData),
			onNodeDblClick: (nodeData) => this.onNodeDblClick(nodeData),
		});

		frappe.visual.LayoutManager.createToolbar(this.toolbarEl, this.engine);
		frappe.visual.LayoutManager.createSearchBar(this.toolbarEl, this.engine);
	}

	async onNodeClick(nodeData) {
		if (!nodeData.doctype || !nodeData.docname) return;

		const html = await frappe.xcall(
			"arkspace.arkspace_core.visual_api.get_entity_detail",
			{ doctype: nodeData.doctype, docname: nodeData.docname },
		);

		new frappe.visual.FloatingWindow({
			title: nodeData.label || nodeData.docname,
			color: nodeData.borderColor || "#8b5cf6",
			content: html,
			width: 360,
			height: 320,
			icon: "🔍",
			minimizable: true,
			closable: true,
			resizable: true,
		});
	}

	onNodeDblClick(nodeData) {
		// Re-center exploration on double-clicked node
		if (nodeData.doctype && nodeData.docname) {
			this.page.doctype_field.set_value(nodeData.doctype);
			setTimeout(() => {
				this.page.entity_field.df.options = nodeData.doctype;
				this.page.entity_field.set_value(nodeData.docname);
				this.explore(nodeData.doctype, nodeData.docname);
			}, 100);
		}
	}
}
