/**
 * ARK Onboarding — جولة تعريفية تفاعلية
 *
 * Interactive storyboard wizard that teaches new users how ARKSpace works.
 * Each step includes mini-graphs and live data to make learning immersive.
 *
 * Pattern: "Interactive Tutorial" — Storyboard + mini-GraphEngines.
 *
 * Runs as a desk page AND can be triggered via floatingWindow from help system.
 * Includes role-based filtering and Previous/Next buttons at top + bottom.
 */

frappe.pages["ark-onboarding"].on_page_load = async function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("ARK Onboarding — جولة تعريفية"),
		single_column: true,
	});

	await frappe.require("frappe_visual.bundle.js");

	const $body = $(page.body);
	$body.html('<div id="ark-onboard-container" style="max-width:900px;margin:0 auto;padding:20px"></div>');

	const container = document.getElementById("ark-onboard-container");

	// Fetch summary data for the wizard
	const data = await frappe.xcall("arkspace.arkspace_core.visual_api.get_onboarding_data");

	// Determine user role for filtering
	const roles = (frappe.user_roles || []);
	const isAdmin = roles.includes("System Manager") || roles.includes("ARKSpace Admin");
	const isManager = roles.includes("ARKSpace Manager");
	const isFrontDesk = roles.includes("ARKSpace Front Desk");
	const isOps = roles.includes("ARKSpace Operations");
	const isMember = roles.includes("ARKSpace Member");

	// Build role-aware label
	let roleLabel = __("Member");
	if (isAdmin) roleLabel = __("Admin");
	else if (isManager) roleLabel = __("Manager");
	else if (isFrontDesk) roleLabel = __("Front Desk");
	else if (isOps) roleLabel = __("Operations");

	frappe.visual.Storyboard.create(container, [
		// ── Step 0: Welcome ──
		{
			title: __("مرحباً بك في أرك سبيس! 🚀"),
			content: (el) => {
				el.innerHTML = `
					<div style="text-align:center;padding:20px">
						<div style="font-size:72px;margin-bottom:16px">🏢</div>
						<h3 style="margin-bottom:12px">${__("Welcome to ARKSpace")}</h3>
						<p style="color:var(--text-muted);font-size:15px;max-width:500px;margin:0 auto">
							${__("ARKSpace is a complete co-working space management system. This guided tour will show you how everything connects together.")}
						</p>
						<div style="margin-top:12px;padding:8px 16px;background:rgba(27,54,93,0.06);border-radius:20px;display:inline-block;font-size:12px;color:#1B365D">
							🎭 ${__("Your role")}: <strong>${roleLabel}</strong>
						</div>
						<div style="display:flex;justify-content:center;gap:20px;margin-top:24px;flex-wrap:wrap">
							<div style="text-align:center">
								<div style="font-size:28px;font-weight:700;color:#6366f1">${data.total_spaces}</div>
								<div style="font-size:12px;color:var(--text-muted)">${__("Spaces")}</div>
							</div>
							<div style="text-align:center">
								<div style="font-size:28px;font-weight:700;color:#10b981">${data.total_members}</div>
								<div style="font-size:12px;color:var(--text-muted)">${__("Active Members")}</div>
							</div>
							<div style="text-align:center">
								<div style="font-size:28px;font-weight:700;color:#8b5cf6">${data.total_branches}</div>
								<div style="font-size:12px;color:var(--text-muted)">${__("Branches")}</div>
							</div>
							<div style="text-align:center">
								<div style="font-size:28px;font-weight:700;color:#f59e0b">${data.total_plans}</div>
								<div style="font-size:12px;color:var(--text-muted)">${__("Plans")}</div>
							</div>
						</div>
					</div>
				`;
			},
		},

		// ── Step 1: Choose what to learn (role-filtered choices) ──
		{
			title: __("ماذا تريد أن تتعلم؟"),
			content: `
				<div style="text-align:center;padding:10px">
					<p style="color:var(--text-muted);margin-bottom:16px">
						${__("Choose a topic to explore. Each path includes visual explanations.")}
					</p>
				</div>
			`,
			choices: [
				{ label: __("🏢 Spaces & Bookings"), value: "spaces", color: "#6366f1", goTo: 2 },
				{ label: __("🎫 Memberships"), value: "memberships", color: "#10b981", goTo: 3 },
				...(isAdmin || isManager ? [{ label: __("📊 Analytics & Reports"), value: "analytics", color: "#f59e0b", goTo: 4 }] : []),
				{ label: __("👥 Community"), value: "community", color: "#8b5cf6", goTo: 5 },
			],
		},

		// ── Step 2: Spaces & Bookings ──
		{
			title: __("🏢 المساحات والحجوزات"),
			content: (el) => {
				el.innerHTML = `
					<div style="padding:10px">
						<p style="margin-bottom:16px">${__("Here's how the booking flow works:")}</p>
						<div id="onb-booking-graph" style="height:250px;border:1px solid var(--border-color);
							border-radius:var(--border-radius-lg);margin-bottom:16px"></div>
						<div style="display:flex;gap:12px;flex-wrap:wrap">
							<div style="flex:1;min-width:200px;padding:12px;
								border-radius:var(--border-radius-lg);
								background:rgba(99,102,241,0.1)">
								<strong>${__("Space Types")}</strong>
								<p style="font-size:13px;color:var(--text-muted);margin-top:4px">
									${(data.space_types || []).join(" · ") || __("Hot Desk, Private Office, Meeting Room…")}
								</p>
							</div>
							<div style="flex:1;min-width:200px;padding:12px;
								border-radius:var(--border-radius-lg);
								background:rgba(16,185,129,0.1)">
								<strong>${__("Booking Types")}</strong>
								<p style="font-size:13px;color:var(--text-muted);margin-top:4px">
									${__("Hourly · Daily · Monthly")}
								</p>
							</div>
						</div>
					</div>
				`;

				// Mini graph showing booking workflow
				setTimeout(() => {
					const miniC = document.getElementById("onb-booking-graph");
					if (miniC) {
						new frappe.visual.GraphEngine({
							container: miniC,
							nodes: [
								{ id: "s1", label: __("Browse Spaces"), type: "module" },
								{ id: "s2", label: __("Create Booking"), type: "action" },
								{ id: "s3", label: __("Pending"), type: "warning" },
								{ id: "s4", label: __("Confirmed"), type: "master" },
								{ id: "s5", label: __("Check In"), type: "active" },
								{ id: "s6", label: __("Check Out"), type: "settings" },
							],
							edges: [
								{ source: "s1", target: "s2", type: "flow", animated: true },
								{ source: "s2", target: "s3", type: "flow", animated: true },
								{ source: "s3", target: "s4", type: "flow", animated: true },
								{ source: "s4", target: "s5", type: "flow", animated: true },
								{ source: "s5", target: "s6", type: "flow", animated: true },
							],
							layout: "elk-layered",
							layoutOptions: { "elk.direction": "RIGHT" },
							animate: true,
							antLines: true,
							minimap: false,
							contextMenu: false,
						});
					}
				}, 300);
			},
		},

		// ── Step 3: Memberships ──
		{
			title: __("🎫 العضويات"),
			content: (el) => {
				el.innerHTML = `
					<div style="padding:10px">
						<p style="margin-bottom:16px">${__("Membership lifecycle: from plan selection to renewal.")}</p>
						<div id="onb-membership-graph" style="height:250px;border:1px solid var(--border-color);
							border-radius:var(--border-radius-lg);margin-bottom:16px"></div>
						<div style="padding:12px;border-radius:var(--border-radius-lg);
							background:rgba(16,185,129,0.1)">
							<strong>${__("Available Plans")}</strong>
							<div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:8px">
								${(data.plans || []).map(p => `
									<div style="padding:6px 12px;
										border-radius:var(--border-radius);
										background:var(--fg-color);border:1px solid var(--border-color);
										font-size:12px">
										<strong>${p.plan_name || p.name}</strong>
										<div style="color:var(--text-muted)">${p.plan_type || ""}</div>
									</div>
								`).join("")}
							</div>
						</div>
					</div>
				`;

				setTimeout(() => {
					const miniC = document.getElementById("onb-membership-graph");
					if (miniC) {
						new frappe.visual.GraphEngine({
							container: miniC,
							nodes: [
								{ id: "m1", label: __("Choose Plan"), type: "module" },
								{ id: "m2", label: __("Register"), type: "action" },
								{ id: "m3", label: __("Active"), type: "active" },
								{ id: "m4", label: __("Renew"), type: "master" },
								{ id: "m5", label: __("Expired"), type: "error" },
								{ id: "m6", label: __("Upgrade"), type: "action" },
							],
							edges: [
								{ source: "m1", target: "m2", type: "flow", animated: true },
								{ source: "m2", target: "m3", type: "flow", animated: true },
								{ source: "m3", target: "m4", type: "flow" },
								{ source: "m4", target: "m3", type: "flow", animated: true, label: __("renewed") },
								{ source: "m3", target: "m5", type: "flow", label: __("expired") },
								{ source: "m3", target: "m6", type: "link" },
								{ source: "m6", target: "m3", type: "flow", animated: true, label: __("upgraded") },
							],
							layout: "elk-layered",
							animate: true,
							antLines: true,
							minimap: false,
							contextMenu: false,
						});
					}
				}, 300);
			},
		},

		// ── Step 4: Analytics ──
		{
			title: __("📊 التحليلات والتقارير"),
			content: (el) => {
				el.innerHTML = `
					<div style="padding:10px">
						<p style="margin-bottom:16px">${__("ARKSpace provides comprehensive analytics across all operations:")}</p>
						<div id="onb-analytics-graph" style="height:250px;border:1px solid var(--border-color);
							border-radius:var(--border-radius-lg);margin-bottom:16px"></div>
						<div style="display:flex;gap:12px;flex-wrap:wrap">
							<div style="flex:1;min-width:150px;padding:10px;text-align:center;
								border-radius:var(--border-radius-lg);
								background:rgba(245,158,11,0.1)">
								<div style="font-size:24px">📈</div>
								<div style="font-size:13px;font-weight:600">${__("Revenue Trends")}</div>
							</div>
							<div style="flex:1;min-width:150px;padding:10px;text-align:center;
								border-radius:var(--border-radius-lg);
								background:rgba(99,102,241,0.1)">
								<div style="font-size:24px">🗺️</div>
								<div style="font-size:13px;font-weight:600">${__("Occupancy Heatmap")}</div>
							</div>
							<div style="flex:1;min-width:150px;padding:10px;text-align:center;
								border-radius:var(--border-radius-lg);
								background:rgba(16,185,129,0.1)">
								<div style="font-size:24px">🔮</div>
								<div style="font-size:13px;font-weight:600">${__("Revenue Forecast")}</div>
							</div>
						</div>
					</div>
				`;

				setTimeout(() => {
					const miniC = document.getElementById("onb-analytics-graph");
					if (miniC) {
						new frappe.visual.GraphEngine({
							container: miniC,
							nodes: [
								{ id: "a0", label: "ARKSpace", type: "server" },
								{ id: "a1", label: __("Occupancy"), type: "dashboard" },
								{ id: "a2", label: __("Revenue"), type: "master" },
								{ id: "a3", label: __("Members"), type: "user" },
								{ id: "a4", label: __("Bookings"), type: "transaction" },
								{ id: "a5", label: __("Forecast"), type: "action" },
							],
							edges: [
								{ source: "a0", target: "a1", type: "data-flow", animated: true },
								{ source: "a0", target: "a2", type: "data-flow", animated: true },
								{ source: "a0", target: "a3", type: "data-flow", animated: true },
								{ source: "a0", target: "a4", type: "data-flow", animated: true },
								{ source: "a2", target: "a5", type: "flow", animated: true },
							],
							layout: "elk-radial",
							animate: true,
							antLines: true,
							minimap: false,
							contextMenu: false,
						});
					}
				}, 300);
			},
		},

		// ── Step 5: Community ──
		{
			title: __("👥 المجتمع والتواصل"),
			content: (el) => {
				el.innerHTML = `
					<div style="padding:10px">
						<p style="margin-bottom:16px">${__("Build connections, share knowledge, and attend events:")}</p>
						<div id="onb-community-graph" style="height:250px;border:1px solid var(--border-color);
							border-radius:var(--border-radius-lg);margin-bottom:16px"></div>
						<div style="display:flex;gap:12px;flex-wrap:wrap">
							<div style="flex:1;min-width:150px;padding:10px;text-align:center;
								border-radius:var(--border-radius-lg);
								background:rgba(139,92,246,0.1)">
								<div style="font-size:24px">💬</div>
								<div style="font-size:13px;font-weight:600">${__("Community Board")}</div>
							</div>
							<div style="flex:1;min-width:150px;padding:10px;text-align:center;
								border-radius:var(--border-radius-lg);
								background:rgba(236,72,153,0.1)">
								<div style="font-size:24px">🤝</div>
								<div style="font-size:13px;font-weight:600">${__("Networking")}</div>
							</div>
							<div style="flex:1;min-width:150px;padding:10px;text-align:center;
								border-radius:var(--border-radius-lg);
								background:rgba(245,158,11,0.1)">
								<div style="font-size:24px">🎉</div>
								<div style="font-size:13px;font-weight:600">${__("Events")}</div>
							</div>
						</div>
					</div>
				`;

				setTimeout(() => {
					const miniC = document.getElementById("onb-community-graph");
					if (miniC) {
						new frappe.visual.GraphEngine({
							container: miniC,
							nodes: [
								{ id: "c1", label: "Alice", type: "user" },
								{ id: "c2", label: "Bob", type: "user" },
								{ id: "c3", label: "Carol", type: "user" },
								{ id: "c4", label: __("Hackathon"), type: "meeting" },
								{ id: "c5", label: __("Discussion"), type: "whatsapp" },
							],
							edges: [
								{ source: "c1", target: "c2", type: "link" },
								{ source: "c2", target: "c3", type: "link" },
								{ source: "c1", target: "c3", type: "link" },
								{ source: "c1", target: "c4", type: "flow", label: __("organizes") },
								{ source: "c2", target: "c4", type: "reference", label: __("attends") },
								{ source: "c3", target: "c5", type: "reference", label: __("posted") },
							],
							layout: "fcose",
							animate: true,
							minimap: false,
							contextMenu: false,
						});
					}
				}, 300);
			},
		},

		// ── Step 6: Where to go ──
		{
			title: __("🎯 ابدأ الآن!"),
			content: `
				<div style="text-align:center;padding:20px">
					<div style="font-size:64px;margin-bottom:16px">🎉</div>
					<h3>${__("You're all set!")}</h3>
					<p style="color:var(--text-muted);max-width:450px;margin:12px auto">
						${__("Here are the visual tools available to you:")}
					</p>
					<div style="display:flex;flex-direction:column;gap:10px;max-width:400px;margin:20px auto;text-align:start">
						<a href="/app/ark-command" class="btn btn-default btn-sm" style="text-align:start">
							🧭 ${__("Command Center")} — ${__("مركز القيادة")}
						</a>
						<a href="/app/ark-explorer" class="btn btn-default btn-sm" style="text-align:start">
							🔍 ${__("Explorer")} — ${__("المستكشف")}
						</a>
						<a href="/app/ark-command" class="btn btn-default btn-sm" style="text-align:start">
							📊 ${__("Bookings & CRM")} — ${__("الحجوزات والعملاء")}
						</a>
						<a href="/app/ark-community" class="btn btn-default btn-sm" style="text-align:start">
							👥 ${__("Community Network")} — ${__("شبكة المجتمع")}
						</a>
						<a href="/app/ark-live" class="btn btn-default btn-sm" style="text-align:start">
							🗺️ ${__("Live Floor Plan")} — ${__("المخطط التفاعلي")}
						</a>
					</div>
				</div>
			`,
		},
	], {
		onComplete: () => {
			frappe.show_alert({
				message: __("Welcome aboard! 🎉 مرحباً بك!"),
				indicator: "green",
			});
			frappe.set_route("ark-command");
		},
		showProgress: true,
	});
};
