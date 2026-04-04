// Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
// Developer Website: https://arkan.it.com
// License: MIT
// For license information, please see license.txt

/**
 * ARKSpace About — عن أرك سبيس
 *
 * Full app showcase storyboard for admins, executives, and decision makers.
 * 10 slides: Overview, Modules, ERD, Workflows, Stakeholders, Industry,
 * Integrations, Security, Reports, Getting Started.
 *
 * Uses frappe_visual: Storyboard, appMap, erd, dependencyGraph, GraphEngine.
 */

frappe.pages["arkspace-about"].on_page_load = async function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("About ARKSpace — عن أرك سبيس"),
		single_column: true,
	});

	await frappe.require("frappe_visual.bundle.js");

	const PRIMARY = "#1B365D";
	const GOLD = "#C4A962";
	const ACCENT = "#2563EB";

	// ── Fetch live stats ──
	let stats = { spaces: 0, members: 0, bookings: 0, memberships: 0 };
	try {
		stats = await frappe.xcall(
			"arkspace.arkspace_core.visual_api.get_onboarding_data",
		);
	} catch (_e) { /* use defaults */ }

	// ── Build slides ──
	const slides = [
		/* ── 1. App Overview ── */
		{
			title: __("ARKSpace — Enterprise Co-Working Management"),
			content: `
				<div style="text-align:center;padding:20px 0">
					<img src="/assets/arkspace/images/arkspace-splash.svg"
						 style="width:180px;height:180px;margin-bottom:20px" alt="ARKSpace Logo"/>
					<h2 style="color:${PRIMARY};margin-bottom:12px;font-weight:800">
						${__("Smart Co-Working Space Management")}
					</h2>
					<p style="font-size:16px;color:var(--text-muted);max-width:600px;margin:0 auto 24px">
						${__("End-to-end platform for managing shared workspaces — from booking and membership to billing, community, and marketplace. Built on ERPNext for seamless financial integration.")}
					</p>
					<div style="display:flex;gap:16px;justify-content:center;flex-wrap:wrap;margin-top:20px">
						${_statCard("🏢", stats.spaces || 0, __("Spaces"))}
						${_statCard("👥", stats.members || 0, __("Members"))}
						${_statCard("📅", stats.bookings || 0, __("Bookings"))}
						${_statCard("🎫", stats.memberships || 0, __("Memberships"))}
					</div>
					<div style="margin-top:28px;display:flex;gap:10px;justify-content:center;flex-wrap:wrap">
						<span class="badge" style="background:${PRIMARY};color:white;padding:6px 14px;border-radius:20px;font-size:12px">ERPNext Integration</span>
						<span class="badge" style="background:${GOLD};color:${PRIMARY};padding:6px 14px;border-radius:20px;font-size:12px">ARKANOOR Marketplace</span>
						<span class="badge" style="background:${ACCENT};color:white;padding:6px 14px;border-radius:20px;font-size:12px">Multi-Branch</span>
						<span class="badge" style="background:#10B981;color:white;padding:6px 14px;border-radius:20px;font-size:12px">QR Check-in</span>
					</div>
					<div style="margin-top:20px;padding:16px;background:rgba(27,54,93,0.04);border-radius:12px;border:1px solid var(--border-color)">
						<p style="font-size:14px;color:${PRIMARY};font-weight:700;margin-bottom:8px;text-align:center">
							${__('حيوي وعصري — إدارة مساحتك بالكامل من نظام واحد')}
						</p>
						<div style="display:flex;gap:10px;justify-content:center;flex-wrap:wrap">
							<span class="badge" style="background:rgba(27,54,93,0.08);color:${PRIMARY};padding:5px 12px;border-radius:16px;font-size:11px">👤 ${__('مالك مساحة مشتركة')}</span>
							<span class="badge" style="background:rgba(27,54,93,0.08);color:${PRIMARY};padding:5px 12px;border-radius:16px;font-size:11px">⚙️ ${__('مدير عمليات')}</span>
							<span class="badge" style="background:rgba(27,54,93,0.08);color:${PRIMARY};padding:5px 12px;border-radius:16px;font-size:11px">🏠 ${__('عضو/مستأجر')}</span>
							<span class="badge" style="background:rgba(27,54,93,0.08);color:${PRIMARY};padding:5px 12px;border-radius:16px;font-size:11px">💰 ${__('محاسب')}</span>
						</div>
					</div>
				</div>`,
		},

		/* ── 2. Module Map ── */
		{
			title: __("Module Map — خريطة الوحدات"),
			content: `<div id="about-module-map" style="height:500px"></div>`,
			onEnter: (el) => {
				const target = el.querySelector("#about-module-map");
				if (!target || target.dataset.loaded) return;
				target.dataset.loaded = "1";
				frappe.visual.appMap(target, "arkspace", {
					layout: "elk-layered",
					animate: true,
				});
			},
		},

		/* ── 3. Entity Relationships ── */
		{
			title: __("Entity Relationships — علاقات البيانات"),
			content: `<div id="about-erd" style="height:500px"></div>`,
			onEnter: (el) => {
				const target = el.querySelector("#about-erd");
				if (!target || target.dataset.loaded) return;
				target.dataset.loaded = "1";

				const nodes = [
					{ id: "space", label: "Co-working Space", type: "primary" },
					{ id: "booking", label: "Space Booking", type: "success" },
					{ id: "member", label: "Membership", type: "info" },
					{ id: "plan", label: "Membership Plan", type: "info" },
					{ id: "daypass", label: "Day Pass", type: "warning" },
					{ id: "visitor", label: "Visitor Log", type: "default" },
					{ id: "event", label: "Community Event", type: "success" },
					{ id: "lead", label: "Workspace Lead", type: "warning" },
					{ id: "branch", label: "Branch", type: "primary" },
					{ id: "invoice", label: "Sales Invoice", type: "danger" },
					{ id: "contract", label: "Space Contract", type: "default" },
				];
				const edges = [
					{ source: "branch", target: "space" },
					{ source: "space", target: "booking" },
					{ source: "member", target: "booking" },
					{ source: "plan", target: "member" },
					{ source: "member", target: "contract" },
					{ source: "space", target: "daypass" },
					{ source: "lead", target: "visitor" },
					{ source: "lead", target: "member" },
					{ source: "event", target: "space" },
					{ source: "booking", target: "invoice" },
					{ source: "contract", target: "invoice" },
				];

				new frappe.visual.GraphEngine({
					container: target,
					nodes,
					edges,
					layout: "elk-layered",
					layoutOptions: { "elk.direction": "DOWN" },
					animate: true,
					minimap: true,
				});
			},
		},

		/* ── 4. Workflows ── */
		{
			title: __("Workflows — سير العمل"),
			content: `
				<p style="text-align:center;color:var(--text-muted);margin-bottom:16px">
					${__("Key business workflows in ARKSpace")}
				</p>
				<div id="about-workflows" style="height:460px"></div>`,
			onEnter: (el) => {
				const container = el.querySelector("#about-workflows");
				if (!container || container.dataset.loaded) return;
				container.dataset.loaded = "1";

				const nodes = [
					{ id: "lead", label: __("Workspace Lead"), type: "info", doctype: "Workspace Lead" },
					{ id: "tour", label: __("Tour / Visit"), type: "info", doctype: "Visitor Log" },
					{ id: "booking", label: __("Space Booking"), type: "success", doctype: "Space Booking" },
					{ id: "checkin", label: __("Check In"), type: "success" },
					{ id: "checkout", label: __("Check Out"), type: "default" },
					{ id: "invoice", label: __("Invoice"), type: "warning" },
					{ id: "member", label: __("Membership"), type: "primary", doctype: "Membership" },
					{ id: "renewal", label: __("Renewal"), type: "primary" },
					{ id: "daypass", label: __("Day Pass"), type: "info", doctype: "Day Pass" },
					{ id: "event", label: __("Community Event"), type: "default", doctype: "Community Event" },
					{ id: "marketplace", label: __("Marketplace"), type: "warning" },
				];
				const edges = [
					{ source: "lead", target: "tour" },
					{ source: "tour", target: "booking" },
					{ source: "booking", target: "checkin" },
					{ source: "checkin", target: "checkout" },
					{ source: "checkout", target: "invoice" },
					{ source: "lead", target: "member" },
					{ source: "member", target: "renewal" },
					{ source: "member", target: "booking" },
					{ source: "daypass", target: "checkin" },
					{ source: "member", target: "event" },
					{ source: "member", target: "marketplace" },
				];

				new frappe.visual.GraphEngine({
					container,
					nodes,
					edges,
					layout: "elk-layered",
					layoutOptions: { "elk.direction": "RIGHT" },
					animate: true,
					antLines: true,
					minimap: true,
					onNodeDblClick: (nd) => {
						if (nd.doctype) frappe.set_route("List", nd.doctype);
					},
				});
			},
		},

		/* ── 5. Stakeholder Perspectives ── */
		{
			title: __("Stakeholders — أصحاب المصلحة"),
			content: `
				<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px;padding:8px">
					${_roleCard("🛡️", __("Admin"), __("ARKSpace Admin"), [
						__("Full system configuration"),
						__("Branch management"),
						__("Pricing rules & contracts"),
						__("Analytics & reports"),
						__("User & role management"),
					])}
					${_roleCard("📋", __("Manager"), __("ARKSpace Manager"), [
						__("Branch operations oversight"),
						__("Booking approvals"),
						__("Revenue tracking"),
						__("Staff scheduling"),
						__("CRM pipeline management"),
					])}
					${_roleCard("🖥️", __("Front Desk"), __("ARKSpace Front Desk"), [
						__("Member check-in/check-out"),
						__("Day pass issuance"),
						__("Visitor management"),
						__("Quick booking"),
						__("Space status monitoring"),
					])}
					${_roleCard("⚙️", __("Operations"), __("ARKSpace Operations"), [
						__("Space maintenance"),
						__("Event coordination"),
						__("Community management"),
						__("Floor plan monitoring"),
					])}
					${_roleCard("👤", __("Member"), __("ARKSpace Member"), [
						__("Self-service booking"),
						__("Membership dashboard"),
						__("Community events"),
						__("Marketplace access"),
						__("QR code check-in"),
					])}
				</div>`,
		},

		/* ── 6. Industry Use-Cases ── */
		{
			title: __("Industry Use-Cases — حالات الاستخدام"),
			content: `
				<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px;padding:8px">
					${_useCaseCard("🏢", __("Traditional Co-Working"), __("Shared desks, private offices, meeting rooms. Hourly/daily/monthly booking with membership tiers and community events."))}
					${_useCaseCard("🎓", __("University / Training Centers"), __("Classroom booking, study halls, lab scheduling. Day pass for visitors, membership for enrolled students."))}
					${_useCaseCard("🏥", __("Medical Clinics"), __("Exam room scheduling, specialist time-slots. Patient check-in via QR, billing integration with insurance."))}
					${_useCaseCard("💼", __("Business Incubators"), __("Startup desks, mentoring rooms, pitch halls. Milestone-based memberships, investor events, CRM pipeline for startups."))}
					${_useCaseCard("🏋️", __("Fitness & Wellness"), __("Studio bookings, class scheduling, personal training rooms. Membership + day-pass model with automated renewals."))}
					${_useCaseCard("🛒", __("ARKANOOR Marketplace"), __("Multi-vendor marketplace for co-working services, supplies, equipment rental. Cross-branch inventory and fulfillment."))}
				</div>`,
		},

		/* ── 7. Integrations ── */
		{
			title: __("Integrations — التكاملات"),
			content: `
				<div id="about-integrations" style="height:420px"></div>`,
			onEnter: (el) => {
				const container = el.querySelector("#about-integrations");
				if (!container || container.dataset.loaded) return;
				container.dataset.loaded = "1";

				const nodes = [
					{ id: "arkspace", label: "ARKSpace", type: "primary", borderColor: PRIMARY },
					{ id: "erpnext", label: "ERPNext", type: "warning" },
					{ id: "hrms", label: "HRMS", type: "success" },
					{ id: "caps", label: "CAPS", type: "info" },
					{ id: "arrowz", label: "Arrowz VoIP", type: "default" },
					{ id: "payments", label: "Payments", type: "warning" },
					{ id: "whatsapp", label: "WhatsApp", type: "success" },
					{ id: "qr", label: "QR System", type: "info" },
				];
				const edges = [
					{ source: "arkspace", target: "erpnext", label: __("Billing & Invoicing") },
					{ source: "arkspace", target: "hrms", label: __("Employee ↔ Member") },
					{ source: "arkspace", target: "caps", label: __("Permissions") },
					{ source: "arkspace", target: "arrowz", label: __("Notifications") },
					{ source: "arkspace", target: "payments", label: __("Online Pay") },
					{ source: "arkspace", target: "whatsapp", label: __("Messaging") },
					{ source: "arkspace", target: "qr", label: __("Check-in") },
				];

				new frappe.visual.GraphEngine({
					container,
					nodes,
					edges,
					layout: "elk-radial",
					animate: true,
					pulseNodes: true,
					minimap: true,
				});
			},
		},

		/* ── 8. Security & CAPS ── */
		{
			title: __("Security & Permissions — الأمان والصلاحيات"),
			content: `
				<div style="padding:8px">
					<p style="text-align:center;color:var(--text-muted);margin-bottom:20px">
						${__("ARKSpace uses CAPS (Capability-Based Access Control) for fine-grained security.")}
					</p>
					<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px">
						${_secCard("🔐", "33", __("Capabilities"), __("Module, Action, Field, Report"))}
						${_secCard("📦", "5", __("Bundles"), __("Admin, Manager, Front Desk, Ops, Member"))}
						${_secCard("🔒", "8", __("Field Restrictions"), __("Cost, revenue, pricing masked per role"))}
						${_secCard("⚡", "6", __("Action Controls"), __("Approve, cancel, check-in gated"))}
					</div>
					<div id="about-security-graph" style="height:320px;margin-top:16px"></div>
				</div>`,
			onEnter: (el) => {
				const container = el.querySelector("#about-security-graph");
				if (!container || container.dataset.loaded) return;
				container.dataset.loaded = "1";

				const nodes = [
					{ id: "admin", label: __("Admin"), type: "danger" },
					{ id: "manager", label: __("Manager"), type: "warning" },
					{ id: "frontdesk", label: __("Front Desk"), type: "success" },
					{ id: "ops", label: __("Operations"), type: "info" },
					{ id: "member", label: __("Member"), type: "default" },
					{ id: "b_admin", label: __("Full Admin Bundle"), type: "primary" },
					{ id: "b_mgr", label: __("Manager Bundle"), type: "primary" },
					{ id: "b_fd", label: __("Front Desk Bundle"), type: "primary" },
					{ id: "b_ops", label: __("Operations Bundle"), type: "primary" },
					{ id: "b_mem", label: __("Member Bundle"), type: "primary" },
				];
				const edges = [
					{ source: "admin", target: "b_admin" },
					{ source: "manager", target: "b_mgr" },
					{ source: "frontdesk", target: "b_fd" },
					{ source: "ops", target: "b_ops" },
					{ source: "member", target: "b_mem" },
				];

				new frappe.visual.GraphEngine({
					container,
					nodes,
					edges,
					layout: "elk-layered",
					layoutOptions: { "elk.direction": "RIGHT" },
					animate: true,
				});
			},
		},

		/* ── 9. Reports & Analytics ── */
		{
			title: __("Reports & Analytics — التقارير والتحليلات"),
			content: `
				<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px;padding:8px">
					${_reportCard("📊", __("Revenue Summary"), __("Daily/weekly/monthly revenue breakdown by branch, space type, and payment method."))}
					${_reportCard("📈", __("Occupancy Report"), __("Real-time and historical occupancy rates with heatmaps per branch and floor."))}
					${_reportCard("👥", __("Member Activity"), __("Check-in frequency, booking patterns, membership utilization per member."))}
					${_reportCard("📅", __("Booking Analytics"), __("Peak hours, cancellation rates, no-show tracking, average booking duration."))}
					${_reportCard("🗺️", __("Live Floor Plan"), __("Real-time 2D floor plan with SVG overlay showing space status and occupancy."))}
					${_reportCard("🎯", __("CRM Pipeline"), __("Lead conversion funnel, tour scheduling, follow-up tracking."))}
				</div>`,
		},

		/* ── 10. Competitive Comparison ── */
		{
			title: __("Why ARKSpace? — لماذا أرك سبيس؟"),
			content: `
				<div style="padding:8px">
					<p style="text-align:center;color:var(--text-muted);margin-bottom:16px">
						${__("See how ARKSpace compares to the leading co-working management platforms.")}
					</p>
					<div style="overflow-x:auto">
						<table style="width:100%;border-collapse:collapse;font-size:12px">
						<thead><tr style="background:rgba(27,54,93,0.06)">
							<th style="text-align:start;padding:8px;border-bottom:2px solid ${PRIMARY}">${__("Feature")}</th>
							<th style="text-align:center;padding:8px;border-bottom:2px solid ${PRIMARY};color:${PRIMARY};font-weight:800">ARKSpace</th>
							<th style="text-align:center;padding:8px;border-bottom:2px solid var(--border-color)">Nexudus</th>
							<th style="text-align:center;padding:8px;border-bottom:2px solid var(--border-color)">OfficeRnD</th>
							<th style="text-align:center;padding:8px;border-bottom:2px solid var(--border-color)">Cobot</th>
							<th style="text-align:center;padding:8px;border-bottom:2px solid var(--border-color)">Optix</th>
						</tr></thead>
						<tbody>
						${[
							[__("Smart Booking (Hourly/Daily/Monthly)"),"Y","Y","Y","Y","Y"],
							[__("Tiered Memberships & Auto-Renewal"),"Y","Y","Y","Y","Y"],
							[__("QR Code Self Check-in"),"Y","P","Y","P","Y"],
							[__("Interactive 2D Floor Plan"),"Y","Y","P","N","P"],
							[__("Built-in CRM & Lead Pipeline"),"Y","P","P","N","N"],
							[__("Community Board & Networking"),"Y","Y","P","Y","Y"],
							[__("Multi-Vendor Marketplace"),"Y","N","N","N","N"],
							[__("Full ERP Integration (ERPNext)"),"Y","N","N","N","N"],
							[__("CAPS Field-Level Security"),"Y","N","N","N","N"],
							[__("Day Pass System"),"Y","Y","Y","Y","Y"],
							[__("Event Management & RSVP"),"Y","Y","P","Y","P"],
							[__("WhatsApp Notifications"),"Y","N","N","N","N"],
							[__("Multi-Branch Centralized"),"Y","Y","Y","P","Y"],
							[__("Revenue Forecasting & Analytics"),"Y","P","P","N","P"],
							[__("Arabic + RTL Support"),"Y","N","N","N","N"],
							[__("Open Source"),"Y","N","N","N","N"],
							[__("Cost"),"FREE","$225+/mo","$599+/mo","€99+/mo","$99+/mo"],
						].map(r => _compareRow(r)).join("")}
						</tbody></table>
					</div>
					<p style="margin-top:16px;font-size:13px;text-align:center;color:var(--text-muted)">
						${__("ARKSpace delivers enterprise-grade co-working management with full ERPNext integration — at zero licensing cost, fully open source.")}
					</p>
				</div>`,
		},

		/* ── 11. Getting Started ── */
		{
			title: __("Getting Started — ابدأ الآن"),
			content: `
				<div style="text-align:center;padding:20px 0">
					<h3 style="color:${PRIMARY};margin-bottom:16px">${__("Ready to explore ARKSpace?")}</h3>
					<p style="color:var(--text-muted);max-width:500px;margin:0 auto 28px">
						${__("Follow the onboarding wizard to learn how ARKSpace works, or jump directly to any section.")}
					</p>
					<div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap">
						<a href="/app/ark-onboarding" class="btn btn-primary btn-md" style="background:${PRIMARY}">
							🎓 ${__("Start Onboarding")}
						</a>
						<a href="/app/ark-command" class="btn btn-default btn-md">
							📊 ${__("Command Center")}
						</a>
						<a href="/app/ark-live" class="btn btn-default btn-md">
							🗺️ ${__("Live Floor Plan")}
						</a>
						<a href="/app/ark-explorer" class="btn btn-default btn-md">
							🔍 ${__("Explorer")}
						</a>
					</div>
					<hr style="margin:24px 0;border-color:var(--border-color)"/>
					<div style="display:flex;gap:16px;justify-content:center;flex-wrap:wrap;font-size:13px;color:var(--text-muted)">
						<span>📧 dev@arkspace.io</span>
						<span>🏢 Arkan Lab</span>
						<span>🔗 moatazarkan6-lab</span>
					</div>
				</div>`,
		},
	];

	// ── Render Storyboard ──
	const $body = $(page.body);
	$body.html('<div id="arkspace-about-storyboard" style="padding:0 15px"></div>');

	frappe.visual.storyboard(
		document.getElementById("arkspace-about-storyboard"),
		slides,
		{ showProgress: true, allowSkip: true }
	);
};

/* ── Helper HTML builders (scoped) ── */

var _statCard, _roleCard, _useCaseCard, _secCard, _reportCard, _compareRow;
(function () {

var _Y = '<span style="color:#10B981;font-weight:700">✓</span>';
var _N = '<span style="color:#EF4444;font-weight:700">✗</span>';
var _P = '<span style="color:#F59E0B;font-weight:700">~</span>';
_compareRow = function (r) {
	return '<tr>' + r.map(function (c, i) {
		var val = c;
		if (c === 'Y') val = _Y;
		else if (c === 'N') val = _N;
		else if (c === 'P') val = _P;
		else if (c === 'FREE') val = '<strong style="color:#10B981">Free</strong>';
		else if (typeof c === 'string' && c.indexOf('$') === 0) val = '<span style="color:#EF4444">' + c + '</span>';
		else if (typeof c === 'string' && c.indexOf('€') === 0) val = '<span style="color:#EF4444">' + c + '</span>';
		return '<td style="padding:6px 8px;border-bottom:1px solid var(--border-color);' + (i > 0 ? 'text-align:center;' : '') + '">' + val + '</td>';
	}).join('') + '</tr>';
};

_statCard = function (icon, value, label) {
	return `<div style="text-align:center;padding:16px 20px;background:var(--fg-color);
		border:1px solid var(--border-color);border-radius:12px;min-width:100px">
		<div style="font-size:24px;margin-bottom:4px">${icon}</div>
		<div style="font-size:28px;font-weight:800;color:#1B365D">${value}</div>
		<div style="font-size:12px;color:var(--text-muted)">${label}</div>
	</div>`;
}

_roleCard = function (icon, title, role, capabilities) {
	return `<div style="padding:16px;background:var(--fg-color);border:1px solid var(--border-color);
		border-radius:12px;border-left:4px solid #1B365D">
		<div style="font-size:20px;margin-bottom:6px">${icon} <strong>${title}</strong></div>
		<div style="font-size:11px;color:var(--text-muted);margin-bottom:10px">${role}</div>
		<ul style="margin:0;padding-left:18px;font-size:13px;color:var(--text-color)">
			${capabilities.map(c => `<li style="margin-bottom:4px">${c}</li>`).join("")}
		</ul>
	</div>`;
}

_useCaseCard = function (icon, title, description) {
	return `<div style="padding:16px;background:var(--fg-color);border:1px solid var(--border-color);
		border-radius:12px">
		<div style="font-size:28px;margin-bottom:8px">${icon}</div>
		<h4 style="margin:0 0 8px;color:#1B365D">${title}</h4>
		<p style="margin:0;font-size:13px;color:var(--text-muted);line-height:1.5">${description}</p>
	</div>`;
}

_secCard = function (icon, count, title, desc) {
	return `<div style="text-align:center;padding:14px;background:var(--fg-color);
		border:1px solid var(--border-color);border-radius:10px">
		<div style="font-size:22px">${icon}</div>
		<div style="font-size:24px;font-weight:800;color:#1B365D">${count}</div>
		<div style="font-size:13px;font-weight:600">${title}</div>
		<div style="font-size:11px;color:var(--text-muted)">${desc}</div>
	</div>`;
}

_reportCard = function (icon, title, desc) {
	return `<div style="padding:14px;background:var(--fg-color);border:1px solid var(--border-color);
		border-radius:12px">
		<div style="font-size:22px;margin-bottom:6px">${icon}</div>
		<h4 style="margin:0 0 6px;color:#1B365D;font-size:14px">${title}</h4>
		<p style="margin:0;font-size:12px;color:var(--text-muted);line-height:1.5">${desc}</p>
	</div>`;
};

})(); // end helpers IIFE
