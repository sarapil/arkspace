// Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
// Developer Website: https://arkan.it.com
// License: MIT
// For license information, please see license.txt

/**
 * ARK Community Network — شبكة المجتمع
 *
 * Social graph: members as nodes, accepted connections as edges,
 * community events as meeting nodes, popular posts as content nodes.
 * The graph reveals the social fabric of the coworking space.
 *
 * Pattern: "Live Monitor" — fcose layout + real-time events.
 */

frappe.pages["ark-community"].on_page_load = async function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("ARK Community — شبكة المجتمع"),
		single_column: true,
	});

	// ── Filters ──
	page.branch_field = page.add_field({
		fieldtype: "Link",
		fieldname: "branch",
		label: __("Branch — الفرع"),
		options: "ARKSpace Branch",
		change: () => community.refresh(),
	});

	page.set_primary_action(__("Refresh"), () => community.refresh(), "refresh");

	page.add_inner_button(__("Feed"), () => {
		if (arkspace?.community?.open_feed) {
			arkspace.community.open_feed();
		} else {
			frappe.set_route("community");
		}
	});
	page.add_inner_button(__("Events"), () => frappe.set_route("List", "Community Event"));
	page.add_inner_button(__("Directory"), () => frappe.set_route("directory"));

	const community = new ArkCommunityNetwork(page);
	await community.init();
	community.refresh();

	// Real-time
	frappe.realtime.on("new_networking_request", () => community.refresh());
	frappe.realtime.on("networking_request_accepted", () => community.refresh());
	frappe.realtime.on("new_community_post", () => community.refresh());
};


class ArkCommunityNetwork {
	constructor(page) {
		this.page = page;
		this.engine = null;
	}

	async init() {
		await frappe.require("frappe_visual.bundle.js");

		// Register custom node types for community
		frappe.visual.ColorSystem.registerNodeType("member", {
			palette: "emerald", icon: "👤", shape: "ellipse", width: 55, height: 55,
		});
		frappe.visual.ColorSystem.registerNodeType("event-node", {
			palette: "violet", icon: "🎉", shape: "roundrectangle", width: 65, height: 50,
		});
		frappe.visual.ColorSystem.registerNodeType("post-node", {
			palette: "amber", icon: "💬", shape: "roundrectangle", width: 55, height: 45,
		});
		frappe.visual.ColorSystem.registerNodeType("popular-post", {
			palette: "rose", icon: "🔥", shape: "diamond", width: 60, height: 60,
		});

		const $body = $(this.page.body);
		$body.html(`
			<div class="ark-community-wrapper" style="padding:0 15px">
				<div id="ark-comm-stats"
					style="display:flex;gap:12px;margin-bottom:12px;flex-wrap:wrap"></div>
				<div id="ark-comm-toolbar"
					style="display:flex;gap:8px;align-items:center;
					margin-bottom:8px;flex-wrap:wrap"></div>
				<div id="ark-comm-graph"
					style="height:calc(100vh - 300px);min-height:450px;
					border:1px solid var(--border-color);
					border-radius:var(--border-radius-lg);
					background:var(--fg-color)"></div>
				<div id="ark-comm-legend"
					style="margin-top:8px;display:flex;gap:16px;flex-wrap:wrap;
					font-size:12px;color:var(--text-muted)">
					<span>👤 ${__("Member")}</span>
					<span>🔗 ${__("Connection")}</span>
					<span>🎉 ${__("Event")}</span>
					<span>💬 ${__("Post")}</span>
					<span>🔥 ${__("Popular (10+ likes)")}</span>
				</div>
			</div>
		`);

		this.statsEl = document.getElementById("ark-comm-stats");
		this.toolbarEl = document.getElementById("ark-comm-toolbar");
		this.graphEl = document.getElementById("ark-comm-graph");
	}

	async refresh() {
		const branch = this.page.branch_field?.get_value() || undefined;

		const data = await frappe.xcall(
			"arkspace.arkspace_core.visual_api.get_community_graph",
			{ branch, limit: 80 },
		);

		this.renderStats(data);
		this.renderGraph(data);
	}

	renderStats(data) {
		const members = data.nodes.filter(n => n.type === "user").length;
		const connections = data.edges.filter(e => e.label === __("connected")).length;
		const events = data.nodes.filter(n => n.type === "meeting").length;
		const posts = data.nodes.filter(n =>
			n.type === "whatsapp" || n.doctype === "Community Post"
		).length;

		const cards = [
			{ label: __("Members"), value: members, icon: "👥", color: "#10b981" },
			{ label: __("Connections"), value: connections, icon: "🔗", color: "#6366f1" },
			{ label: __("Events"), value: events, icon: "🎉", color: "#8b5cf6" },
			{ label: __("Posts"), value: posts, icon: "💬", color: "#f59e0b" },
		];

		this.statsEl.innerHTML = cards.map(c => `
			<div style="flex:1;min-width:120px;padding:12px 16px;
				border-radius:var(--border-radius-lg);
				background:var(--fg-color);border:1px solid var(--border-color);
				text-align:center">
				<div style="font-size:14px">${c.icon}</div>
				<div style="font-size:20px;font-weight:700;color:${c.color}">${c.value}</div>
				<div style="font-size:11px;color:var(--text-muted)">${c.label}</div>
			</div>
		`).join("");
	}

	renderGraph(data) {
		if (this.engine) {
			try { this.engine.destroy(); } catch (_e) { /* ok */ }
		}
		this.toolbarEl.innerHTML = "";

		if (!data.nodes.length) {
			this.graphEl.innerHTML = `
				<div style="display:flex;align-items:center;justify-content:center;
					height:100%;color:var(--text-muted);font-size:18px">
					<div style="text-align:center">
						<div style="font-size:64px;margin-bottom:16px">🌱</div>
						<div>${__("No community data yet")}</div>
						<div style="font-size:13px;margin-top:8px">
							${__("Members will appear here when they connect with each other")}
						</div>
					</div>
				</div>
			`;
			return;
		}

		// Mark popular posts (10+ likes) with special type
		data.nodes.forEach(n => {
			if (n.doctype === "Community Post" && n.meta?.likes >= 10) {
				n.type = "popular-post";
			}
		});

		this.engine = new frappe.visual.GraphEngine({
			container: this.graphEl,
			nodes: data.nodes,
			edges: data.edges,
			layout: "fcose",
			minimap: true,
			contextMenu: true,
			expandCollapse: false,
			animate: true,
			antLines: false,
			pulseNodes: false,
			onNodeClick: (nodeData) => this.onNodeClick(nodeData),
			onNodeDblClick: (nodeData) => {
				if (nodeData.doctype && nodeData.docname) {
					frappe.set_route("Form", nodeData.doctype, nodeData.docname);
				}
			},
		});

		frappe.visual.LayoutManager.createToolbar(this.toolbarEl, this.engine);
		frappe.visual.LayoutManager.createSearchBar(this.toolbarEl, this.engine);
	}

	async onNodeClick(nodeData) {
		if (!nodeData.doctype || !nodeData.docname) return;

		let html;
		if (nodeData.doctype === "User") {
			html = await this.buildMemberCard(nodeData.docname);
		} else {
			html = await frappe.xcall(
				"arkspace.arkspace_core.visual_api.get_entity_detail",
				{ doctype: nodeData.doctype, docname: nodeData.docname },
			);
		}

		new frappe.visual.FloatingWindow({
			title: nodeData.label || nodeData.docname,
			color: nodeData.borderColor || "#10b981",
			content: html,
			width: 360,
			height: 300,
			icon: nodeData.doctype === "User" ? "👤" : "📋",
			minimizable: true,
			closable: true,
			resizable: true,
		});
	}

	async buildMemberCard(user) {
		const info = await frappe.xcall(
			"arkspace.arkspace_community.community.get_member_profile",
			{ user },
		);

		if (!info) return `<div style="padding:20px;text-align:center">${__("No profile data")}</div>`;

		const rows = [
			[__("Email"), user],
			[__("Posts"), String(info.post_count || 0)],
			[__("Connections"), String(info.connection_count || 0)],
		];
		if (info.skills?.length) {
			rows.push([__("Skills"), info.skills.map(s => s.skill_name).join(", ")]);
		}

		const rowsHtml = rows.map(([k, v]) =>
			`<div style="display:flex;justify-content:space-between;padding:4px 0;
				border-bottom:1px solid var(--border-color)">
				<span style="color:var(--text-muted)">${k}</span>
				<strong>${v}</strong>
			</div>`
		).join("");

		return `
			<div style="padding:12px">
				<div style="font-size:32px;text-align:center;margin-bottom:8px">👤</div>
				<div style="text-align:center;font-weight:700;font-size:15px;
					color:#10b981;margin-bottom:12px">
					${info.full_name || user}
				</div>
				${rowsHtml}
				<div style="margin-top:12px;text-align:center">
					<button class="btn btn-xs btn-primary"
						onclick="frappe.set_route('ark-explorer',
						{doctype:'Customer',name:'${info.customer || ""}'})">
						${__("Explore Relationships")}
					</button>
				</div>
			</div>
		`;
	}
}
