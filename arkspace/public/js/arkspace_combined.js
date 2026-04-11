/* arkspace — Combined JS (reduces HTTP requests) */
/* Auto-generated from 11 individual files */


/* === arkspace.js === */
// Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
// Developer Website: https://arkan.it.com
// License: MIT
// For license information, please see license.txt

/**
 * ARKSpace — Main JavaScript Bundle
 * ARKSpace Main JavaScript

 */

frappe.provide("arkspace");
frappe.provide("arkspace.components");
frappe.provide("arkspace.design");
frappe.provide("arkspace.design.icons");

// ========================
// Icon registry (mirrors icons.py)
// ========================
arkspace.design.icons = {
	dashboard: "fa-solid fa-gauge-high",
	spaces: "fa-solid fa-building",
	bookings: "fa-solid fa-calendar-check",
	memberships: "fa-solid fa-id-card",
	members: "fa-solid fa-users",
	leads: "fa-solid fa-user-plus",
	sales: "fa-solid fa-chart-line",
	add: "fa-solid fa-plus",
	edit: "fa-solid fa-pen",
	delete: "fa-solid fa-trash",
	save: "fa-solid fa-floppy-disk",
	search: "fa-solid fa-magnifying-glass",
	success: "fa-solid fa-circle-check",
	warning: "fa-solid fa-triangle-exclamation",
	error: "fa-solid fa-circle-xmark",
	info: "fa-solid fa-circle-info",
	pending: "fa-solid fa-clock",
	invoice: "fa-solid fa-file-invoice-dollar",
	payment: "fa-solid fa-credit-card",
	wallet: "fa-solid fa-wallet",
	wifi: "fa-solid fa-wifi",
	parking: "fa-solid fa-square-parking",
	coffee: "fa-solid fa-mug-hot",
	temperature: "fa-solid fa-temperature-half",
	humidity: "fa-solid fa-droplet",
};

// ========================
// BUTTON COMPONENT
// ========================
arkspace.components.Button = class {
	constructor(options) {
		this.options = Object.assign(
			{
				label: "",
				variant: "primary",
				icon: null,
				size: "md",
				onClick: null,
				loading: false,
				disabled: false,
			},
			options
		);
		this.render();
	}

	render() {
		const sizeClass = { sm: "btn-sm", md: "", lg: "btn-lg" }[
			this.options.size
		];
		const iconHtml = this.options.icon
			? `<i class="${arkspace.design.icons[this.options.icon] || this.options.icon}"></i>`
			: "";

		this.$element = $(`
            <button class="btn-arkspace-${this.options.variant} ${sizeClass}"
                    ${this.options.disabled ? "disabled" : ""}>
                ${iconHtml}
                <span class="label">${this.options.label}</span>
            </button>
        `);

		if (this.options.onClick) {
			this.$element.on("click", this.options.onClick);
		}
		return this.$element;
	}

	setLoading(loading) {
		this.options.loading = loading;
		this.$element.toggleClass("loading", loading);
		this.$element.prop("disabled", loading);
	}
};

// ========================
// SHORTCUT CARD COMPONENT
// ========================
arkspace.components.ShortcutCard = class {
	constructor(options) {
		this.options = Object.assign(
			{
				label: "",
				icon: "dashboard",
				color: "blue",
				href: "#",
				count: null,
			},
			options
		);
		return this.render();
	}

	render() {
		const iconClass =
			arkspace.design.icons[this.options.icon] || "fa-solid fa-circle";
		const countHtml =
			this.options.count !== null
				? `<span class="count">${this.options.count}</span>`
				: "";

		return $(`
            <a href="${this.options.href}" class="shortcut-card">
                <div class="icon-wrapper ${this.options.color}">
                    <i class="${iconClass}"></i>
                </div>
                <span class="label">${this.options.label}</span>
                ${countHtml}
            </a>
        `);
	}
};

// ========================
// STATUS BADGE COMPONENT
// ========================
arkspace.components.StatusBadge = class {
	constructor(status, label) {
		this.status = status;
		this.label = label || this.getDefaultLabel(status);
		return this.render();
	}

	getDefaultLabel(status) {
		const labels = {
			active: __("Active"),
			pending: __("Pending"),
			cancelled: __("Cancelled"),
			draft: __("Draft"),
			completed: __("Completed"),
		};
		return labels[status] || status;
	}

	render() {
		const icons = {
			active: "fa-solid fa-circle-check",
			pending: "fa-solid fa-clock",
			cancelled: "fa-solid fa-circle-xmark",
			draft: "fa-solid fa-file",
			completed: "fa-solid fa-flag-checkered",
		};
		return $(`
            <span class="status-badge status-${this.status}">
                <i class="${icons[this.status] || "fa-solid fa-circle"}"></i>
                ${this.label}
            </span>
        `);
	}
};

// ========================
// KPI CARD COMPONENT
// ========================
arkspace.components.KPICard = class {
	constructor(options) {
		this.options = Object.assign(
			{
				title: "",
				value: "0",
				icon: "sales",
				trend: "neutral",
				trendValue: "",
				color: "blue",
			},
			options
		);
		return this.render();
	}

	render() {
		const iconClass =
			arkspace.design.icons[this.options.icon] ||
			"fa-solid fa-chart-line";
		const trendIcon = {
			up: "fa-solid fa-arrow-up",
			down: "fa-solid fa-arrow-down",
			neutral: "fa-solid fa-minus",
		}[this.options.trend];
		const trendClass = {
			up: "trend-up",
			down: "trend-down",
			neutral: "trend-neutral",
		}[this.options.trend];

		return $(`
            <div class="kpi-card kpi-${this.options.color}">
                <div class="kpi-icon">
                    <i class="${iconClass}"></i>
                </div>
                <div class="kpi-content">
                    <div class="kpi-title">${this.options.title}</div>
                    <div class="kpi-value">${this.options.value}</div>
                    ${
						this.options.trendValue
							? `<div class="kpi-trend ${trendClass}">
                            <i class="${trendIcon}"></i>
                            ${this.options.trendValue}
                        </div>`
							: ""
					}
                </div>
            </div>
        `);
	}
};


/* === arkspace_help.js === */
// Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
// Developer Website: https://arkan.it.com
// License: MIT
// For license information, please see license.txt

/**
 * ARKSpace Contextual Help
 *
 * Provides a floating-window-based help system that:
 *  - Adds ❓ button to every ARKSpace form toolbar
 *  - Opens onboarding/help inside frappe.visual.FloatingWindow
 *  - Positions on opposite side of sidebar (right in LTR, left in RTL)
 *  - Supports topic-specific micro-tutorials
 *
 * Standards compliance:
 *  ✅ floatingWindow (not standalone page)
 *  ✅ Minimize / maximize / drag
 *  ✅ Opposite side of sidebar
 *  ✅ ❓ on every form toolbar
 */

(function () {
	const PRIMARY = "#1B365D";
	const GOLD = "#C4A962";

	// ── DocTypes that belong to ARKSpace (actual DocTypes only) ──
	const ARKSPACE_DOCTYPES = [
		"Co-working Space", "Space Booking", "Space Type", "Amenity", "Space Amenity", "Space Image",
		"Membership", "Membership Plan", "Credit Transaction", "Member Credit Wallet",
		"Day Pass", "Visitor Log", "Workspace Lead", "Workspace Tour",
		"Pricing Rule", "Online Payment", "Payment Receipt",
		"Community Event", "Community Post", "Networking Request", "Member Skill",
		"Analytics Snapshot", "ARKSpace Branch", "ARKSpace Settings",
		"Training Session", "Training Module", "Training Badge", "User Training Progress",
		"Member Contract", "Contract Template", "Contract Legal Document", "Legal Document",
		"Design Configuration", "Documentation Entry",
		"Documentation Code Example", "Documentation Prerequisite", "Documentation Relation",
	];

	// Guard: skip if translation function not loaded
	if (typeof __ === "undefined") { window.__ = function(s) { return s; }; }

	// ── Topic help content per DocType ──
	const HELP_TOPICS = {
		"Co-working Space": {
			title: __("Spaces"),
			icon: "🏢",
			slides: [
				{ title: __("What is a Space?"), body: __("A co-working space is a bookable resource — desks, rooms, studios, or any physical area.") },
				{ title: __("Space Types"), body: __("Organize spaces by type: Hot Desk, Private Office, Meeting Room, Event Hall, Studio, etc.") },
				{ title: __("Capacity & Pricing"), body: __("Set capacity, hourly/daily/monthly rates, and dynamic pricing rules.") },
				{ title: __("Floor Plan"), body: __("Link spaces to floor zones for the Live Floor Plan view.") },
			],
		},
		"Space Booking": {
			title: __("Bookings"),
			icon: "📅",
			slides: [
				{ title: __("Creating a Booking"), body: __("Select space, date/time range, and member. Pricing is auto-calculated.") },
				{ title: __("Booking Lifecycle"), body: __("Draft → Submitted → Confirmed → Checked In → Checked Out → Invoiced") },
				{ title: __("QR Check-in"), body: __("Each confirmed booking generates a QR code for self-service check-in.") },
				{ title: __("Cancellation"), body: __("Cancel before check-in. Refund policies apply per space type.") },
			],
		},
		"Membership": {
			title: __("Memberships"),
			icon: "🎫",
			slides: [
				{ title: __("Plans & Tiers"), body: __("Create membership plans with different access levels, amenities, and pricing.") },
				{ title: __("Membership Lifecycle"), body: __("New → Active → Expiring → Expired. Auto-renewal and manual renewal supported.") },
				{ title: __("Benefits"), body: __("Each plan includes benefits: booking credits, locker access, event invites, etc.") },
			],
		},
		"Day Pass": {
			title: __("Day Pass"),
			icon: "🎟️",
			slides: [
				{ title: __("Quick Access"), body: __("Day passes provide single-day access without a full membership.") },
				{ title: __("Check-in"), body: __("Issue at front desk or online. QR code generated for entry.") },
				{ title: __("Auto-Expiry"), body: __("Passes expire at end of business day automatically.") },
			],
		},
		"Workspace Lead": {
			title: __("CRM"),
			icon: "🎯",
			slides: [
				{ title: __("Lead Pipeline"), body: __("Track prospective members from inquiry to tour to conversion.") },
				{ title: __("Tour Scheduling"), body: __("Schedule and track space tours for leads.") },
				{ title: __("Conversion"), body: __("Convert leads to members or booking customers.") },
			],
		},
		"Community Event": {
			title: __("Events"),
			icon: "🎉",
			slides: [
				{ title: __("Event Management"), body: __("Create events with capacity limits, RSVP, and space allocation.") },
				{ title: __("Member Events"), body: __("Events can be open to all or restricted to membership tiers.") },
			],
		},
		"Space Type": {
			title: __("Space Types"),
			icon: "🏷️",
			slides: [
				{ title: __("What are Space Types?"), body: __("Space Types categorize your physical resources — Hot Desk, Private Office, Meeting Room, Event Hall, Studio, etc.") },
				{ title: __("Pricing by Type"), body: __("Each type can have its own default pricing structure: hourly, daily, or monthly rates.") },
			],
		},
		"Pricing Rule": {
			title: __("Pricing Rules"),
			icon: "💰",
			slides: [
				{ title: __("Dynamic Pricing"), body: __("Create rules that adjust pricing based on peak hours, membership tier, duration, or advance booking.") },
				{ title: __("Rule Priority"), body: __("Rules are evaluated by priority. The first matching rule determines the final price.") },
			],
		},
		"Visitor Log": {
			title: __("Visitors"),
			icon: "🚪",
			slides: [
				{ title: __("Visitor Management"), body: __("Pre-register visitors, track walk-ins, and generate entry badges with QR codes.") },
				{ title: __("Host Notification"), body: __("When a visitor checks in, the host member is automatically notified.") },
			],
		},
		"Workspace Tour": {
			title: __("Tours"),
			icon: "🗺️",
			slides: [
				{ title: __("Tour Scheduling"), body: __("Schedule guided tours for prospective members. Track attendance and follow-up.") },
				{ title: __("Lead Conversion"), body: __("Convert tour visitors into members or booking customers directly from the tour record.") },
			],
		},
		"Community Post": {
			title: __("Community Board"),
			icon: "💬",
			slides: [
				{ title: __("Community Posts"), body: __("Members can share knowledge, ask questions, and post announcements on the community board.") },
				{ title: __("Engagement"), body: __("Posts support likes, pinning, and comment threads to foster engagement.") },
			],
		},
		"Networking Request": {
			title: __("Networking"),
			icon: "🤝",
			slides: [
				{ title: __("Connect with Members"), body: __("Send networking requests to other members based on skills and interests.") },
				{ title: __("Accept or Decline"), body: __("Recipients can accept or decline requests. Accepted connections appear in your network.") },
			],
		},
		"Training Session": {
			title: __("Training"),
			icon: "🎓",
			slides: [
				{ title: __("Training Sessions"), body: __("Create and manage training sessions for member skill development.") },
				{ title: __("Progress Tracking"), body: __("Track attendance and completion status for each participant.") },
			],
		},
		"Member Contract": {
			title: __("Contracts"),
			icon: "📄",
			slides: [
				{ title: __("Contract Management"), body: __("Create and manage contracts for memberships, space rentals, and services.") },
				{ title: __("Legal Documents"), body: __("Attach legal documents and templates to contracts for compliance tracking.") },
			],
		},
		"Analytics Snapshot": {
			title: __("Analytics"),
			icon: "📊",
			slides: [
				{ title: __("Daily Snapshots"), body: __("Automatic daily captures of occupancy, revenue, and membership metrics.") },
				{ title: __("Trend Analysis"), body: __("Compare snapshots over time to identify trends and optimize operations.") },
			],
		},
		"ARKSpace Settings": {
			title: __("Settings"),
			icon: "⚙️",
			slides: [
				{ title: __("App Configuration"), body: __("Configure payment gateways, notification preferences, QR settings, and branch defaults.") },
				{ title: __("Integration Setup"), body: __("Connect ERPNext billing, WhatsApp notifications, and CAPS security from one place.") },
			],
		},
		"ARKSpace Branch": {
			title: __("Branches"),
			icon: "🏢",
			slides: [
				{ title: __("Multi-Branch Management"), body: __("Manage multiple locations with independent settings but centralized reporting.") },
				{ title: __("Branch Transfers"), body: __("Transfer members and bookings between branches seamlessly.") },
			],
		},
		"Online Payment": {
			title: __("Online Payments"),
			icon: "💳",
			slides: [
				{ title: __("Payment Gateways"), body: __("Accept payments via Stripe, Tap, or other gateways configured in ARKSpace Settings.") },
				{ title: __("Payment Reconciliation"), body: __("Webhook-based automatic reconciliation keeps your invoices and payments in sync.") },
			],
		},
		"Space Amenity": {
			title: __("Space Amenities"),
			icon: "🛋️",
			slides: [
				{ title: __("What are Space Amenities?"), body: __("Amenities are the features available in a space — WiFi, projector, whiteboard, coffee machine, etc.") },
				{ title: __("Link to Spaces"), body: __("Assign amenities to spaces so members can filter bookings by required facilities.") },
			],
		},
		"Space Image": {
			title: __("Space Images"),
			icon: "🖼️",
			slides: [
				{ title: __("Gallery Images"), body: __("Upload multiple images for each space to showcase in the portal and booking screen.") },
				{ title: __("Primary Image"), body: __("Mark one image as the primary thumbnail that appears in listings and cards.") },
			],
		},
		"Membership Plan": {
			title: __("Membership Plans"),
			icon: "📋",
			slides: [
				{ title: __("Plan Setup"), body: __("Define membership tiers with different access levels, credit allowances, and amenity bundles.") },
				{ title: __("Plan Pricing"), body: __("Set monthly, quarterly, or annual pricing. Link to ERPNext Item for invoicing.") },
				{ title: __("Plan Benefits"), body: __("Specify included booking hours, locker access, event invites, and printing credits per plan.") },
			],
		},
		"Credit Transaction": {
			title: __("Credit Transactions"),
			icon: "💱",
			slides: [
				{ title: __("Credit Flow"), body: __("Each booking, day pass, or amenity usage deducts credits. Top-ups and plan renewals add credits.") },
				{ title: __("Transaction Log"), body: __("Every credit movement is logged with type, amount, reference document, and timestamp.") },
			],
		},
		"Member Credit Wallet": {
			title: __("Credit Wallet"),
			icon: "👛",
			slides: [
				{ title: __("Wallet Balance"), body: __("Each member has a credit wallet showing current balance, total earned, and total spent.") },
				{ title: __("Top-up Methods"), body: __("Credits can be added via online payment, manual adjustment, or membership plan allocation.") },
			],
		},
		"Member Skill": {
			title: __("Member Skills"),
			icon: "🧠",
			slides: [
				{ title: __("Skill Profiles"), body: __("Members can list their skills and expertise for the community directory and networking.") },
				{ title: __("Skill Matching"), body: __("Skills appear in the member directory, enabling networking requests based on complementary expertise.") },
			],
		},
		"Contract Template": {
			title: __("Contract Templates"),
			icon: "📑",
			slides: [
				{ title: __("Reusable Templates"), body: __("Create contract templates with standard terms for memberships, space rental, and services.") },
				{ title: __("Template Variables"), body: __("Use Jinja variables for member name, dates, pricing, and space details — auto-filled at contract creation.") },
			],
		},
		"Contract Legal Document": {
			title: __("Legal Documents"),
			icon: "⚖️",
			slides: [
				{ title: __("Attached Legals"), body: __("Link legal documents (NDAs, terms of service, waivers) to specific contracts.") },
				{ title: __("Compliance Tracking"), body: __("Track which legal documents each member has acknowledged and signed.") },
			],
		},
		"Legal Document": {
			title: __("Legal Documents"),
			icon: "📜",
			slides: [
				{ title: __("Master Legal Library"), body: __("Maintain a library of legal documents — terms of service, NDAs, waivers, and policies.") },
				{ title: __("Version Control"), body: __("Track document versions to ensure members always agree to the latest terms.") },
			],
		},
		"Training Module": {
			title: __("Training Modules"),
			icon: "📚",
			slides: [
				{ title: __("Module Structure"), body: __("Organize training content into modules — each module contains sessions, resources, and assessments.") },
				{ title: __("Prerequisites"), body: __("Set module prerequisites so members progress through a structured learning path.") },
			],
		},
		"Training Badge": {
			title: __("Training Badges"),
			icon: "🏅",
			slides: [
				{ title: __("Achievement Badges"), body: __("Award badges upon completing training modules or achieving milestones.") },
				{ title: __("Badge Display"), body: __("Badges appear on member profiles in the directory and community pages.") },
			],
		},
		"Design Configuration": {
			title: __("Design Config"),
			icon: "🎨",
			slides: [
				{ title: __("Portal Appearance"), body: __("Customize colors, logo, and layout for the member-facing portal.") },
				{ title: __("Brand Consistency"), body: __("Configure brand colors and assets that apply across all ARKSpace pages.") },
			],
		},
		"Documentation Entry": {
			title: __("Documentation"),
			icon: "📝",
			slides: [
				{ title: __("Knowledge Base"), body: __("Create internal documentation for space policies, procedures, and member guidelines.") },
				{ title: __("Rich Content"), body: __("Entries support Markdown, images, and code examples for technical documentation.") },
			],
		},
		"Payment Receipt": {
			title: __("Payment Receipts"),
			icon: "🧾",
			slides: [
				{ title: __("Receipt Generation"), body: __("Auto-generated receipts for every payment — linked to invoices and credit transactions.") },
				{ title: __("Print Formats"), body: __("Multiple print formats available: bilingual (AR/EN), Arabic-only, and English-only.") },
			],
		},
		"User Training Progress": {
			title: __("Training Progress"),
			icon: "📈",
			slides: [
				{ title: __("Progress Tracking"), body: __("Track each member's progress through training modules and sessions.") },
				{ title: __("Completion Status"), body: __("View completion percentage, time spent, and badges earned per member.") },
			],
		},
		"Amenity": {
			title: __("Amenities"),
			icon: "✨",
			slides: [
				{ title: __("Amenity Catalog"), body: __("Define all available amenities — WiFi, projector, printer, coffee, parking, lockers, etc.") },
				{ title: __("Link to Spaces"), body: __("Amenities are linked to spaces via Space Amenity child entries, enabling filter-by-amenity bookings.") },
			],
		},
		"Documentation Code Example": {
			title: __("Code Examples"),
			icon: "💻",
			slides: [
				{ title: __("Code Snippets"), body: __("Attach code examples to documentation entries for API usage, integrations, and automation recipes.") },
			],
		},
		"Documentation Prerequisite": {
			title: __("Prerequisites"),
			icon: "🔗",
			slides: [
				{ title: __("Reading Order"), body: __("Define which documentation entries must be read before this one, creating a structured learning path.") },
			],
		},
		"Documentation Relation": {
			title: __("Related Docs"),
			icon: "🔀",
			slides: [
				{ title: __("Cross-references"), body: __("Link related documentation entries to help readers discover connected topics and guides.") },
			],
		},
	};

	// ── Default help for unknown DocTypes ──
	const DEFAULT_HELP = {
		title: __("ARKSpace Help"),
		icon: "❓",
		slides: [
			{ title: __("About ARKSpace"), body: __("ARKSpace is a comprehensive co-working space management platform.") },
			{ title: __("Need more help?"), body: __("Visit the About page for a full app overview, or start the Onboarding wizard.") },
		],
	};

	// ── Open help in FloatingWindow ──
	function openHelp(doctype) {
		if (!frappe.visual || !frappe.visual.FloatingWindow) {
			frappe.msgprint(__("frappe_visual is required. Please install it first."));
			return;
		}

		const topic = HELP_TOPICS[doctype] || DEFAULT_HELP;
		const isRTL = document.documentElement.dir === "rtl" ||
			$("html").attr("lang") === "ar";

		// Build slide HTML
		let currentSlide = 0;
		const totalSlides = topic.slides.length;

		function slideHTML(idx) {
			const s = topic.slides[idx];
			return `
				<div style="padding:16px">
					<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
						<button class="btn btn-xs btn-default as-help-prev" ${idx === 0 ? 'disabled style="opacity:0.4"' : ''}>
							◀ ${__("Previous")}
						</button>
						<span style="font-size:11px;color:var(--text-muted)">${idx + 1} / ${totalSlides}</span>
						<button class="btn btn-xs btn-default as-help-next" ${idx === totalSlides - 1 ? 'disabled style="opacity:0.4"' : ''}>
							${__("Next")} ▶
						</button>
					</div>
					<h4 style="color:${PRIMARY};margin-bottom:8px">${s.title}</h4>
					<p style="font-size:13px;color:var(--text-color);line-height:1.6">${s.body}</p>
					<div style="display:flex;justify-content:space-between;align-items:center;margin-top:16px;padding-top:12px;border-top:1px solid var(--border-color)">
						<button class="btn btn-xs btn-default as-help-prev2" ${idx === 0 ? 'disabled style="opacity:0.4"' : ''}>
							◀ ${__("Previous")}
						</button>
						<span style="font-size:11px;color:var(--text-muted)">${idx + 1} / ${totalSlides}</span>
						<button class="btn btn-xs btn-default as-help-next2" ${idx === totalSlides - 1 ? 'disabled style="opacity:0.4"' : ''}>
							${__("Next")} ▶
						</button>
					</div>
				</div>
			`;
		}

		// Position: opposite side of sidebar
		const x = isRTL ? 40 : window.innerWidth - 420;
		const y = 80;

		const win = new frappe.visual.FloatingWindow({
			title: `${topic.icon} ${topic.title}`,
			color: PRIMARY,
			content: slideHTML(currentSlide),
			width: 380,
			height: 320,
			x,
			y,
			minimizable: true,
			closable: true,
			resizable: true,
			icon: topic.icon,
		});

		// Navigation handlers
		function attachNavHandlers() {
			const body = win.el.querySelector(".fv-win-body");
			if (!body) return;

			body.querySelectorAll(".as-help-prev, .as-help-prev2").forEach((btn) => {
				btn.addEventListener("click", () => {
					if (currentSlide > 0) {
						currentSlide--;
						win.setContent(slideHTML(currentSlide));
						attachNavHandlers();
					}
				});
			});

			body.querySelectorAll(".as-help-next, .as-help-next2").forEach((btn) => {
				btn.addEventListener("click", () => {
					if (currentSlide < totalSlides - 1) {
						currentSlide++;
						win.setContent(slideHTML(currentSlide));
						attachNavHandlers();
					}
				});
			});
		}

		attachNavHandlers();
	}

	// ── Open full onboarding in FloatingWindow ──
	function openOnboarding() {
		if (!frappe.visual || !frappe.visual.FloatingWindow) {
			frappe.set_route("ark-onboarding");
			return;
		}

		const isRTL = document.documentElement.dir === "rtl" ||
			$("html").attr("lang") === "ar";
		const x = isRTL ? 40 : window.innerWidth - 520;

		// Determine user role for personalized onboarding
		const roles = (frappe.user_roles || []);
		const isAdmin = roles.includes("System Manager") || roles.includes("ARKSpace Admin");
		const isManager = roles.includes("ARKSpace Manager");
		const isFrontDesk = roles.includes("ARKSpace Front Desk");
		let roleLabel = __("Member");
		if (isAdmin) roleLabel = __("Admin");
		else if (isManager) roleLabel = __("Manager");
		else if (isFrontDesk) roleLabel = __("Front Desk");

		const contentEl = document.createElement("div");
		contentEl.style.cssText = "height:100%;overflow:auto;padding:12px";
		contentEl.innerHTML = `
			<div style="text-align:center;padding:16px 0">
				<div style="font-size:48px;margin-bottom:12px">🏢</div>
				<h3 style="color:${PRIMARY}">${__("ARKSpace Onboarding")}</h3>
				<div style="margin:8px 0;padding:4px 12px;background:rgba(27,54,93,0.06);border-radius:16px;display:inline-block;font-size:11px;color:${PRIMARY}">
					🎭 ${roleLabel}
				</div>
				<p style="color:var(--text-muted);font-size:13px;margin-bottom:16px">
					${__("Choose a topic to learn about:")}
				</p>
				<div style="display:flex;flex-direction:column;gap:8px;max-width:320px;margin:0 auto">
					<button class="btn btn-default btn-sm as-onb-topic" data-topic="spaces" style="text-align:start">
						🏢 ${__("Spaces & Bookings")}
					</button>
					<button class="btn btn-default btn-sm as-onb-topic" data-topic="memberships" style="text-align:start">
						🎫 ${__("Memberships")}
					</button>
					<button class="btn btn-default btn-sm as-onb-topic" data-topic="crm" style="text-align:start">
						🎯 ${__("CRM & Leads")}
					</button>
					<button class="btn btn-default btn-sm as-onb-topic" data-topic="community" style="text-align:start">
						👥 ${__("Community & Events")}
					</button>
					${isAdmin || isManager ? `
					<button class="btn btn-default btn-sm as-onb-topic" data-topic="analytics" style="text-align:start">
						📊 ${__("Analytics & Reports")}
					</button>` : ""}
					${isAdmin ? `
					<button class="btn btn-default btn-sm as-onb-topic" data-topic="settings" style="text-align:start">
						⚙️ ${__("Settings & Configuration")}
					</button>` : ""}
					<hr style="margin:8px 0;border-color:var(--border-color)"/>
					<a href="/app/ark-onboarding" class="btn btn-primary btn-sm" style="background:${PRIMARY}">
						🎓 ${__("Full Interactive Tour")}
					</a>
					<a href="/app/arkspace-about" class="btn btn-default btn-sm">
						📖 ${__("About ARKSpace")}
					</a>
				</div>
			</div>
		`;

		const win = new frappe.visual.FloatingWindow({
			title: `🎓 ${__("ARKSpace Onboarding")}`,
			color: PRIMARY,
			content: contentEl,
			width: 400,
			height: 420,
			x,
			y: 80,
			minimizable: true,
			closable: true,
			resizable: true,
		});

		// Topic buttons
		contentEl.querySelectorAll(".as-onb-topic").forEach((btn) => {
			btn.addEventListener("click", () => {
				const topicMap = {
					spaces: "Co-working Space",
					memberships: "Membership",
					crm: "Workspace Lead",
					community: "Community Event",
					analytics: "Analytics Snapshot",
					settings: "ARKSpace Settings",
				};
				win.close();
				openHelp(topicMap[btn.dataset.topic]);
			});
		});
	}

	// ── Add ❓ button to form toolbar ──
	function addHelpButton(frm) {
		if (!ARKSPACE_DOCTYPES.includes(frm.doctype)) return;

		// Don't add duplicate
		if (frm.page.inner_toolbar.find(".as-help-btn").length) return;

		frm.page.add_inner_button("❓ " + __("Help"), () => {
			openHelp(frm.doctype);
		}).addClass("as-help-btn").css({
			"font-size": "13px",
			"margin-left": "4px",
		});
	}

	// ── Hook into all form refreshes ──
	$(document).on("form-load form-refresh", function (_e, frm) {
		if (frm) addHelpButton(frm);
	});

	// Alternative: use frappe.ui.form.on with wildcard via after_load
	if (frappe.ui && frappe.ui.form) {
		const origMakeForm = frappe.ui.form.Form.prototype.refresh;
		if (origMakeForm) {
			frappe.ui.form.Form.prototype.refresh = function (...args) {
				const result = origMakeForm.apply(this, args);
				try {
					addHelpButton(this);
				} catch (_e) { /* silent */ }
				return result;
			};
		}
	}

	// ── Expose public API ──
	if (!window.arkspace) window.arkspace = {};
	window.arkspace.help = {
		openHelp,
		openOnboarding,
		HELP_TOPICS,
	};

	// ── Add ❓ to navbar if user has ARKSpace role ──
	$(document).ready(() => {
		setTimeout(() => {
			if (!frappe.user_roles) return;
			const hasRole = frappe.user_roles.some((r) => r.startsWith("ARKSpace"));
			if (!hasRole && !frappe.user_roles.includes("System Manager")) return;

			const $helpIcon = $(`
				<li class="nav-item as-navbar-help" title="${__("ARKSpace Help")}">
					<a class="nav-link" href="#" style="font-size:16px;padding:8px 10px">❓</a>
				</li>
			`);
			$helpIcon.on("click", (e) => {
				e.preventDefault();
				openOnboarding();
			});

			// Insert before the user dropdown
			const $navbar = $(".navbar-nav:last");
			if ($navbar.length) {
				$navbar.prepend($helpIcon);
			}
		}, 2000);
	});
})();


/* === online_payments.js === */
// Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
// Developer Website: https://arkan.it.com
// License: MIT
// For license information, please see license.txt

/**
 * ARKSpace Online Payments — Client-side Integration
 *
 * Adds "Pay Online" buttons to Space Booking and Membership forms,
 * and provides utilities for payment flow management.
 */

(function() {
"use strict";
// Guard: skip if frappe core not loaded
if (typeof frappe === "undefined" || typeof frappe.provide !== "function") return;
frappe.provide("arkspace.payments");

// ═══════════════════════════════════════════════════════════════════════════
// Payment Status Indicator
// ═══════════════════════════════════════════════════════════════════════════

arkspace.payments.STATUS_COLORS = {
	Initiated: "blue",
	Pending: "orange",
	Completed: "green",
	Failed: "red",
	Cancelled: "grey",
	Refunded: "purple",
	"Partially Refunded": "purple",
	Expired: "grey",
};

arkspace.payments.STATUS_ICONS = {
	Initiated: "fa-solid fa-hourglass-start",
	Pending: "fa-solid fa-spinner fa-spin",
	Completed: "fa-solid fa-circle-check",
	Failed: "fa-solid fa-circle-xmark",
	Cancelled: "fa-solid fa-ban",
	Refunded: "fa-solid fa-rotate-left",
	"Partially Refunded": "fa-solid fa-rotate-left",
	Expired: "fa-solid fa-clock",
};


// ═══════════════════════════════════════════════════════════════════════════
// Core Payment Functions
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Initiate an online payment for a document.
 * Opens a new tab/window with the gateway checkout page.
 */
arkspace.payments.pay_online = function (doctype, docname, opts) {
	opts = opts || {};

	frappe.call({
		method: "arkspace.arkspace_integrations.api.get_checkout_url",
		args: {
			reference_doctype: doctype,
			reference_name: docname,
		},
		freeze: true,
		freeze_message: __("Preparing payment link..."),
		callback: function (r) {
			if (r.message && r.message.checkout_url) {
				// Open checkout in new tab
				window.open(r.message.checkout_url, "_blank");

				frappe.show_alert(
					{
						message: __("Payment window opened. Complete the payment in the new tab."),
						indicator: "blue",
					},
					10
				);

				// Start polling for completion
				if (opts.on_complete) {
					arkspace.payments._poll_status(
						r.message.payment_name,
						opts.on_complete,
						opts.on_fail
					);
				}
			} else {
				frappe.msgprint(
					__("Could not generate payment link. Please try again.")
				);
			}
		},
		error: function () {
			frappe.msgprint(
				__("Failed to initiate payment. Please check your payment gateway configuration.")
			);
		},
	});
};

/**
 * Check payment status for a document and display it.
 */
arkspace.payments.check_status = function (doctype, docname, callback) {
	frappe.call({
		method: "arkspace.arkspace_integrations.api.get_payment_status",
		args: {
			reference_doctype: doctype,
			reference_name: docname,
		},
		callback: function (r) {
			if (callback) callback(r.message);
		},
	});
};

/**
 * Verify a specific payment with the gateway.
 */
arkspace.payments.verify = function (payment_name, callback) {
	frappe.call({
		method: "arkspace.arkspace_integrations.api.verify_payment",
		args: { payment_name: payment_name },
		freeze: true,
		freeze_message: __("Verifying payment with gateway..."),
		callback: function (r) {
			if (r.message) {
				const status = r.message.status;
				const color = arkspace.payments.STATUS_COLORS[status] || "grey";
				frappe.show_alert(
					{
						message: __("Payment status: {0}", [status]),
						indicator: color,
					},
					5
				);
			}
			if (callback) callback(r.message);
		},
	});
};

/**
 * Request a refund for a payment.
 */
arkspace.payments.refund = function (payment_name, amount, reason) {
	frappe.confirm(
		__("Are you sure you want to refund this payment?"),
		function () {
			frappe.call({
				method: "arkspace.arkspace_integrations.api.refund_payment",
				args: {
					payment_name: payment_name,
					amount: amount || null,
					reason: reason || null,
				},
				freeze: true,
				freeze_message: __("Processing refund..."),
				callback: function (r) {
					if (r.message) {
						frappe.show_alert(
							{
								message: __("Refund processed: {0}", [r.message.status]),
								indicator: "green",
							},
							5
						);
						cur_frm && cur_frm.reload_doc();
					}
				},
			});
		}
	);
};


// ═══════════════════════════════════════════════════════════════════════════
// Internal: Poll payment status
// ═══════════════════════════════════════════════════════════════════════════

arkspace.payments._poll_status = function (payment_name, on_complete, on_fail, attempt) {
	attempt = attempt || 0;
	const MAX_ATTEMPTS = 60; // 5 min at 5s intervals
	const INTERVAL = 5000;

	if (attempt >= MAX_ATTEMPTS) return;

	setTimeout(function () {
		frappe.call({
			method: "arkspace.arkspace_integrations.api.verify_payment",
			args: { payment_name: payment_name },
			callback: function (r) {
				if (!r.message) return;

				if (r.message.status === "Completed") {
					frappe.show_alert(
						{
							message: __("Payment completed successfully!"),
							indicator: "green",
						},
						8
					);
					if (on_complete) on_complete(r.message);
					cur_frm && cur_frm.reload_doc();
				} else if (r.message.status === "Failed") {
					frappe.show_alert(
						{
							message: __("Payment failed. Please try again."),
							indicator: "red",
						},
						8
					);
					if (on_fail) on_fail(r.message);
				} else if (["Initiated", "Pending"].includes(r.message.status)) {
					// Still waiting — poll again
					arkspace.payments._poll_status(
						payment_name,
						on_complete,
						on_fail,
						attempt + 1
					);
				}
			},
		});
	}, INTERVAL);
};


// ═══════════════════════════════════════════════════════════════════════════
// Payment Status HTML renderer (for form sidebars)
// ═══════════════════════════════════════════════════════════════════════════

arkspace.payments.render_status_html = function (payments) {
	if (!payments || !payments.length) {
		return '<div class="text-muted">' + __("No online payments") + "</div>";
	}

	let html = '<div class="arkspace-payment-list">';
	payments.forEach(function (p) {
		const color = arkspace.payments.STATUS_COLORS[p.status] || "grey";
		const icon = arkspace.payments.STATUS_ICONS[p.status] || "fa-solid fa-circle";
		html += `
			<div class="payment-item mb-2 p-2 border rounded">
				<div class="d-flex justify-content-between align-items-center">
					<span>
						<i class="${icon}" style="color: var(--${color}-500)"></i>
						<a href="/desk/online-payment/${p.name}">${p.name}</a>
					</span>
					<span class="indicator-pill ${color}">${p.status}</span>
				</div>
				<div class="text-muted small mt-1">
					${p.gateway} · ${format_currency(p.amount, p.currency)}
				</div>
			</div>
		`;
	});
	html += "</div>";
	return html;
};


// ═══════════════════════════════════════════════════════════════════════════
// Form Script: Space Booking — "Pay Online" button
// ═══════════════════════════════════════════════════════════════════════════

frappe.ui.form.on("Space Booking", {
	refresh: function (frm) {
		if (frm.doc.docstatus !== 1) return;
		if (["Cancelled", "No Show"].includes(frm.doc.status)) return;

		arkspace.payments.check_status("Space Booking", frm.doc.name, function (data) {
			if (!data) return;

			// Show payment status in sidebar
			if (data.payments && data.payments.length) {
				frm.dashboard.add_section(
					arkspace.payments.render_status_html(data.payments),
					__("Online Payments")
				);
			}

			// Only show Pay Online if no completed payment exists
			if (data.latest_status === "Completed") return;

			frm.add_custom_button(
				__("Pay Online"),
				function () {
					arkspace.payments.pay_online("Space Booking", frm.doc.name, {
						on_complete: function () {
							frm.reload_doc();
						},
					});
				},
				__("Actions")
			);
			frm.change_custom_button_type(__("Pay Online"), __("Actions"), "primary");
		});
	},
});


// ═══════════════════════════════════════════════════════════════════════════
// Form Script: Membership — "Pay Online" button
// ═══════════════════════════════════════════════════════════════════════════

frappe.ui.form.on("Membership", {
	refresh: function (frm) {
		if (frm.doc.docstatus !== 1) return;
		if (frm.doc.status === "Cancelled") return;

		arkspace.payments.check_status("Membership", frm.doc.name, function (data) {
			if (!data) return;

			// Show payment status in sidebar
			if (data.payments && data.payments.length) {
				frm.dashboard.add_section(
					arkspace.payments.render_status_html(data.payments),
					__("Online Payments")
				);
			}

			if (data.latest_status === "Completed") return;

			frm.add_custom_button(
				__("Pay Online"),
				function () {
					arkspace.payments.pay_online("Membership", frm.doc.name, {
						on_complete: function () {
							frm.reload_doc();
						},
					});
				},
				__("Actions")
			);
			frm.change_custom_button_type(__("Pay Online"), __("Actions"), "primary");
		});
	},
});


// ═══════════════════════════════════════════════════════════════════════════
// Form Script: Online Payment — verify & refund actions
// ═══════════════════════════════════════════════════════════════════════════

frappe.ui.form.on("Online Payment", {
	refresh: function (frm) {
		// Verify button for pending payments
		if (["Initiated", "Pending"].includes(frm.doc.status)) {
			frm.add_custom_button(__("Verify with Gateway"), function () {
				arkspace.payments.verify(frm.doc.name, function () {
					frm.reload_doc();
				});
			});
		}

		// Refund button for completed payments
		if (frm.doc.status === "Completed") {
			frm.add_custom_button(
				__("Refund"),
				function () {
					frappe.prompt(
						[
							{
								fieldname: "amount",
								fieldtype: "Currency",
								label: __("Refund Amount"),
								default: frm.doc.amount,
								reqd: 1,
							},
							{
								fieldname: "reason",
								fieldtype: "Small Text",
								label: __("Reason"),
							},
						],
						function (values) {
							arkspace.payments.refund(
								frm.doc.name,
								values.amount,
								values.reason
							);
						},
						__("Refund Payment")
					);
				},
				__("Actions")
			);
		}

		// Color the status indicator
		const color = arkspace.payments.STATUS_COLORS[frm.doc.status];
		if (color) {
			frm.page.set_indicator(frm.doc.status, color);
		}
	},
});


// ═══════════════════════════════════════════════════════════════════════════
// Real-time event listener — payment completion notification
// ═══════════════════════════════════════════════════════════════════════════

frappe.realtime.on("online_payment_completed", function (data) {
	frappe.show_alert(
		{
			message: __("Payment {0} completed!", [data.payment]),
			indicator: "green",
		},
		10
	);

	// Reload current form if it's the related document
	if (
		cur_frm &&
		cur_frm.doc.name === data.reference
	) {
		cur_frm.reload_doc();
	}
});
})();


/* === dynamic_pricing.js === */
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


/* === qr_checkin.js === */
// Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
// Developer Website: https://arkan.it.com
// License: MIT
// For license information, please see license.txt

/**
 * ARKSpace QR Check-in Frontend
 * QR Code Check-in UI
 *
 * Adds QR generation, preview, print, and bulk-generate functionality
 * to Space Booking forms and list views.
 */

// Namespace
arkspace = window.arkspace || {};
arkspace.qr = {};

// ─────────────────────────────────────────────────────────────────────────
// Space Booking — Form Script
// ─────────────────────────────────────────────────────────────────────────

frappe.ui.form.on("Space Booking", {
	refresh(frm) {
		arkspace.qr.setup_booking_buttons(frm);
		arkspace.qr.show_qr_preview(frm);
	},
});

/**
 * Add QR-related buttons to the Space Booking form.
 */
arkspace.qr.setup_booking_buttons = function (frm) {
	if (!frm.doc.docstatus || frm.doc.docstatus !== 1) return;
	if (["Cancelled", "No Show"].includes(frm.doc.status)) return;

	// Generate / Regenerate QR button
	const label = frm.doc.qr_code
		? __("Regenerate QR Code")
		: __("Generate QR Code");

	frm.add_custom_button(
		label,
		() => arkspace.qr.generate(frm),
		__("QR Check-in")
	);

	// Print QR button (only if QR exists)
	if (frm.doc.qr_code) {
		frm.add_custom_button(
			__("Print QR Code"),
			() => arkspace.qr.print_qr(frm),
			__("QR Check-in")
		);

		frm.add_custom_button(
			__("Download QR Code"),
			() => arkspace.qr.download_qr(frm),
			__("QR Check-in")
		);
	}
};

/**
 * Generate QR code for the current booking.
 */
arkspace.qr.generate = function (frm) {
	frappe.call({
		method: "arkspace.arkspace_spaces.qr_checkin.generate_qr",
		args: { booking_name: frm.doc.name },
		freeze: true,
		freeze_message: __("Generating QR Code..."),
		callback(r) {
			if (r.message) {
				frappe.show_alert({
					message: __("QR Code generated successfully"),
					indicator: "green",
				});
				frm.reload_doc();
			}
		},
	});
};

/**
 * Show QR code image preview on the form.
 */
arkspace.qr.show_qr_preview = function (frm) {
	if (!frm.doc.qr_code || frm.doc.docstatus !== 1) return;

	// Remove old preview
	frm.fields_dict.qr_code &&
		$(frm.fields_dict.qr_code.wrapper).find(".qr-preview").remove();

	if (!frm.fields_dict.qr_code) return;

	const $wrapper = $(frm.fields_dict.qr_code.wrapper);
	const preview_html = `
		<div class="qr-preview"
			 style="text-align:center; padding:15px; margin-top:10px;
					background:#fff; border:1px solid #e2e8f0;
					border-radius:8px;">
			<img src="${frm.doc.qr_code}"
				 alt="QR Code"
				 style="max-width:200px; height:auto; image-rendering:pixelated;" />
			<div style="margin-top:8px; font-size:12px; color:#64748b;">
				${__("Scan to check in")}
			</div>
		</div>
	`;
	$wrapper.append(preview_html);
};

/**
 * Open a print-friendly page with the QR code.
 */
arkspace.qr.print_qr = function (frm) {
	const booking = frm.doc;
	const win = window.open("", "_blank");
	win.document.write(`
		<!DOCTYPE html>
		<html>
		<head>
			<title>${__("QR Check-in")} — ${booking.name}</title>
			<style>
				* { margin: 0; padding: 0; box-sizing: border-box; }
				body {
					font-family: -apple-system, BlinkMacSystemFont,
						'Segoe UI', Roboto, sans-serif;
					display: flex;
					justify-content: center;
					padding: 40px;
				}
				.print-card {
					text-align: center;
					max-width: 350px;
					padding: 30px;
					border: 2px solid #1B365D;
					border-radius: 12px;
				}
				.print-card h2 {
					color: #1B365D;
					margin-bottom: 8px;
					font-size: 18px;
				}
				.print-card .sub {
					color: #64748b;
					margin-bottom: 20px;
					font-size: 13px;
				}
				.print-card img {
					max-width: 250px;
					height: auto;
					image-rendering: pixelated;
				}
				.details {
					margin-top: 20px;
					text-align: left;
					font-size: 13px;
					color: #334155;
				}
				.details p { margin: 4px 0; }
				.footer {
					margin-top: 16px;
					font-size: 11px;
					color: #94a3b8;
				}
				@media print {
					body { padding: 0; }
					.print-card { border: 1px solid #ccc; }
				}
			</style>
		</head>
		<body>
			<div class="print-card">
				<h2>ARKSpace Check-in</h2>
				<div class="sub">${__("Scan to check in")}</div>
				<img src="${booking.qr_code}" />
				<div class="details">
					<p><strong>${__("Booking")}:</strong> ${booking.name}</p>
					<p><strong>${__("Space")}:</strong> ${booking.space || ""}</p>
					<p><strong>${__("Member")}:</strong> ${booking.member_name || booking.member}</p>
					<p><strong>${__("Time")}:</strong>
						${frappe.datetime.str_to_user(booking.start_datetime)}
						— ${frappe.datetime.str_to_user(booking.end_datetime)}
					</p>
				</div>
				<div class="footer">${__("Powered by ARKSpace")}</div>
			</div>
			<script>window.print();</script>
		</body>
		</html>
	`);
	win.document.close();
};

/**
 * Download QR code image.
 */
arkspace.qr.download_qr = function (frm) {
	if (!frm.doc.qr_code) return;
	const a = document.createElement("a");
	a.href = frm.doc.qr_code;
	a.download = `qr-${frm.doc.name}.png`;
	document.body.appendChild(a);
	a.click();
	document.body.removeChild(a);
};

// ─────────────────────────────────────────────────────────────────────────
// List View: Bulk Generate QR
// ─────────────────────────────────────────────────────────────────────────

frappe.listview_settings["Space Booking"] =
	frappe.listview_settings["Space Booking"] || {};

const _original_onload =
	frappe.listview_settings["Space Booking"].onload;

frappe.listview_settings["Space Booking"].onload = function (listview) {
	if (_original_onload) _original_onload(listview);

	listview.page.add_inner_button(__("Bulk Generate QR"), () => {
		frappe.call({
			method: "arkspace.arkspace_spaces.qr_checkin.bulk_generate_qr",
			freeze: true,
			freeze_message: __("Generating QR codes for today's bookings..."),
			callback(r) {
				if (r.message) {
					frappe.show_alert({
						message: __(
							"{0} QR codes generated", [r.message.generated]
						),
						indicator: "green",
					});
					listview.refresh();
				}
			},
		});
	});
};

// ─────────────────────────────────────────────────────────────────────────
// Real-time: booking_checked_in event
// ─────────────────────────────────────────────────────────────────────────

frappe.realtime.on("booking_checked_in", function (data) {
	if (!data) return;

	frappe.show_alert({
		message: __("{0} checked in to {1}", [
			data.member || data.booking,
			data.space || "",
		]),
		indicator: "green",
	});

	// Refresh form if currently viewing this booking
	if (
		cur_frm &&
		cur_frm.doctype === "Space Booking" &&
		cur_frm.docname === data.booking
	) {
		cur_frm.reload_doc();
	}
});


/* === visitor_management.js === */
// Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
// Developer Website: https://arkan.it.com
// License: MIT
// For license information, please see license.txt

/**
 * ARKSpace Visitor Management Frontend
 * Visitor check-in/out, badge printing, real-time updates
 */

// Namespace
arkspace = window.arkspace || {};
arkspace.visitors = {};

// ─────────────────────────────────────────────────────────────────────────
// Visitor Log — Form Script
// ─────────────────────────────────────────────────────────────────────────

frappe.ui.form.on("Visitor Log", {
	refresh(frm) {
		arkspace.visitors.setup_buttons(frm);
	},
});

/**
 * Add action buttons based on visitor status.
 */
arkspace.visitors.setup_buttons = function (frm) {
	if (frm.is_new()) return;

	const status = frm.doc.status;

	// Check-in button
	if (status === "Expected") {
		if (frm.doc.approval_status === "Rejected") return;

		frm.add_custom_button(__("Check In"), () => {
			frappe.call({
				method: "arkspace.arkspace_spaces.visitor_management.visitor_check_in",
				args: { visitor_name: frm.doc.name },
				freeze: true,
				freeze_message: __("Checking in visitor..."),
				callback(r) {
					if (r.message) {
						frappe.show_alert({
							message: __(
								"{0} checked in — Badge #{1}",
								[frm.doc.visitor_name, r.message.badge_number]
							),
							indicator: "green",
						});
						frm.reload_doc();
					}
				},
			});
		}, __("Actions"));
		frm.change_custom_button_type(__("Check In"), __("Actions"), "primary");
	}

	// Check-out button
	if (status === "Checked In") {
		frm.add_custom_button(__("Check Out"), () => {
			frappe.call({
				method: "arkspace.arkspace_spaces.visitor_management.visitor_check_out",
				args: { visitor_name: frm.doc.name },
				freeze: true,
				callback(r) {
					if (r.message) {
						frappe.show_alert({
							message: __("{0} checked out", [frm.doc.visitor_name]),
							indicator: "green",
						});
						frm.reload_doc();
					}
				},
			});
		}, __("Actions"));
		frm.change_custom_button_type(__("Check Out"), __("Actions"), "danger");
	}

	// Print Badge button (checked in only)
	if (status === "Checked In" || status === "Expected") {
		frm.add_custom_button(__("Print Badge"), () => {
			arkspace.visitors.print_badge(frm);
		}, __("Actions"));
	}

	// Approve / Reject (for pre-registered pending visitors)
	if (frm.doc.preregistered && frm.doc.approval_status === "Pending") {
		frm.add_custom_button(__("Approve"), () => {
			frappe.call({
				method: "arkspace.arkspace_spaces.visitor_management.approve_visitor",
				args: { visitor_name: frm.doc.name },
				callback() {
					frappe.show_alert({
						message: __("Visitor approved"),
						indicator: "green",
					});
					frm.reload_doc();
				},
			});
		}, __("Approval"));
		frm.change_custom_button_type(__("Approve"), __("Approval"), "primary");

		frm.add_custom_button(__("Reject"), () => {
			frappe.prompt(
				{ fieldtype: "Small Text", label: __("Reason"), fieldname: "reason" },
				(values) => {
					frappe.call({
						method: "arkspace.arkspace_spaces.visitor_management.reject_visitor",
						args: {
							visitor_name: frm.doc.name,
							reason: values.reason,
						},
						callback() {
							frappe.show_alert({
								message: __("Visitor rejected"),
								indicator: "red",
							});
							frm.reload_doc();
						},
					});
				},
				__("Reject Visitor")
			);
		}, __("Approval"));
	}

	// Quick Walk-in button at top
	if (frm.is_new()) {
		frm.set_intro(__("Fill in visitor details and save, or use Quick Walk-in for immediate check-in."));
	}
};

/**
 * Print a visitor badge.
 */
arkspace.visitors.print_badge = function (frm) {
	frappe.call({
		method: "arkspace.arkspace_spaces.visitor_management.get_visitor_badge_html",
		args: { visitor_name: frm.doc.name },
		callback(r) {
			if (r.message) {
				const win = window.open("", "_blank");
				win.document.write(r.message);
				win.document.close();
			}
		},
	});
};

/**
 * Quick walk-in dialog — accessible from list view.
 */
arkspace.visitors.quick_walk_in = function () {
	const d = new frappe.ui.Dialog({
		title: __("Quick Walk-in"),
		fields: [
			{
				fieldtype: "Data",
				fieldname: "visitor_name",
				label: __("Visitor Name"),
				reqd: 1,
			},
			{
				fieldtype: "Data",
				fieldname: "visitor_phone",
				label: __("Phone"),
			},
			{
				fieldtype: "Data",
				fieldname: "visitor_company",
				label: __("Company"),
			},
			{ fieldtype: "Column Break" },
			{
				fieldtype: "Select",
				fieldname: "purpose",
				label: __("Purpose"),
				options: "Meeting\nInterview\nDelivery\nMaintenance\nTour\nEvent\nOther",
				default: "Meeting",
				reqd: 1,
			},
			{
				fieldtype: "Link",
				fieldname: "host",
				label: __("Host (Member)"),
				options: "Customer",
			},
			{
				fieldtype: "Link",
				fieldname: "visiting_space",
				label: __("Space"),
				options: "Co-working Space",
			},
			{ fieldtype: "Section Break", label: __("ID Verification") },
			{
				fieldtype: "Select",
				fieldname: "id_type",
				label: __("ID Type"),
				options: "\nNational ID\nPassport\nIqama\nDriving License\nOther",
			},
			{
				fieldtype: "Data",
				fieldname: "id_number",
				label: __("ID Number"),
			},
		],
		primary_action_label: __("Check In Now"),
		primary_action(values) {
			frappe.call({
				method: "arkspace.arkspace_spaces.visitor_management.walk_in_visitor",
				args: values,
				freeze: true,
				freeze_message: __("Registering and checking in visitor..."),
				callback(r) {
					d.hide();
					if (r.message) {
						frappe.show_alert({
							message: __(
								"{0} checked in — Badge #{1}",
								[r.message.visitor_name, r.message.badge_number]
							),
							indicator: "green",
						});
						// Open the visitor log
						frappe.set_route("Form", "Visitor Log", r.message.visitor);
					}
				},
			});
		},
	});
	d.show();
};

// ─────────────────────────────────────────────────────────────────────────
// List View
// ─────────────────────────────────────────────────────────────────────────

frappe.listview_settings["Visitor Log"] =
	frappe.listview_settings["Visitor Log"] || {};

const _original_visitor_onload =
	frappe.listview_settings["Visitor Log"].onload;

frappe.listview_settings["Visitor Log"].onload = function (listview) {
	if (_original_visitor_onload) _original_visitor_onload(listview);

	// Quick Walk-in button
	listview.page.add_inner_button(__("Quick Walk-in"), () => {
		arkspace.visitors.quick_walk_in();
	});

	// Today's Visitors button
	listview.page.add_inner_button(__("Today's Visitors"), () => {
		frappe.set_route("List", "Visitor Log", {
			creation: [
				">=",
				frappe.datetime.get_today() + " 00:00:00",
			],
		});
	});
};

frappe.listview_settings["Visitor Log"].get_indicator = function (doc) {
	const map = {
		"Expected": [__("Expected"), "orange", "status,=,Expected"],
		"Checked In": [__("Checked In"), "blue", "status,=,Checked In"],
		"Checked Out": [__("Checked Out"), "green", "status,=,Checked Out"],
		"Cancelled": [__("Cancelled"), "red", "status,=,Cancelled"],
		"No Show": [__("No Show"), "grey", "status,=,No Show"],
	};
	return map[doc.status] || [doc.status, "grey"];
};

// ─────────────────────────────────────────────────────────────────────────
// Real-time events
// ─────────────────────────────────────────────────────────────────────────

frappe.realtime.on("visitor_checked_in", function (data) {
	if (!data) return;
	frappe.show_alert({
		message: __("{0} has arrived", [data.visitor_name]),
		indicator: "blue",
	});
});

frappe.realtime.on("visitor_checked_out", function (data) {
	if (!data) return;
	frappe.show_alert({
		message: __("{0} has left", [data.visitor_name]),
		indicator: "green",
	});
});

frappe.realtime.on("visitor_arrived", function (data) {
	if (!data) return;
	frappe.show_alert({
		message: data.message,
		indicator: "blue",
	}, 10);
});


/* === day_pass.js === */
// Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
// Developer Website: https://arkan.it.com
// License: MIT
// For license information, please see license.txt

/**
 * ARKSpace Day Pass — Frontend
 *
 * Form buttons for check-in/out, convert to membership,
 * QR preview, walk-in quick create, and day-pass dashboard stats.
 */

arkspace = window.arkspace || {};
arkspace.day_pass = {};

// ─────────────────────────────────────────────────────────────────────────
// Day Pass Form Script
// ─────────────────────────────────────────────────────────────────────────

frappe.ui.form.on("Day Pass", {
	refresh(frm) {
		arkspace.day_pass.setup_buttons(frm);
		arkspace.day_pass.show_qr_preview(frm);
		arkspace.day_pass.show_stats_banner(frm);
	},
});

/**
 * Add contextual action buttons based on status.
 */
arkspace.day_pass.setup_buttons = function (frm) {
	if (frm.doc.docstatus !== 1) return;

	const status = frm.doc.status;

	// Check In button
	if (status === "Active") {
		frm.add_custom_button(__("Check In"), () => {
			frappe.call({
				method: "arkspace.arkspace_spaces.day_pass_api.day_pass_check_in",
				args: { name: frm.doc.name },
				freeze: true,
				freeze_message: __("Checking in..."),
				callback(r) {
					if (r.message) {
						frappe.show_alert({
							message: __("Checked in successfully"),
							indicator: "green",
						});
						frm.reload_doc();
					}
				},
			});
		}).addClass("btn-primary-dark");
	}

	// Check Out button
	if (status === "Checked In") {
		frm.add_custom_button(__("Check Out"), () => {
			frappe.call({
				method: "arkspace.arkspace_spaces.day_pass_api.day_pass_check_out",
				args: { name: frm.doc.name },
				freeze: true,
				freeze_message: __("Checking out..."),
				callback(r) {
					if (r.message) {
						frappe.show_alert({
							message: __(
								"Checked out — Duration: {0}h",
								[r.message.duration_hours]
							),
							indicator: "blue",
						});
						frm.reload_doc();
					}
				},
			});
		}).addClass("btn-warning");
	}

	// Convert to Membership
	if (
		["Active", "Checked In", "Checked Out"].includes(status) &&
		!frm.doc.converted_to_membership
	) {
		frm.add_custom_button(
			__("Convert to Membership"),
			() => arkspace.day_pass.convert_dialog(frm),
			__("Actions")
		);
	}

	// Regenerate QR
	if (["Active", "Checked In"].includes(status)) {
		frm.add_custom_button(
			__("Regenerate QR"),
			() => {
				frappe.call({
					method: "arkspace.arkspace_spaces.day_pass_api.create_day_pass",
					// trigger QR regeneration via the controller
				});
				// Simpler: just reload after regenerating via direct doc method
				frm.call("_generate_qr").then(() => frm.reload_doc());
			},
			__("Actions")
		);

		frm.add_custom_button(
			__("Print QR"),
			() => arkspace.day_pass.print_qr(frm),
			__("Actions")
		);
	}
};

/**
 * Show QR code preview on the form.
 */
arkspace.day_pass.show_qr_preview = function (frm) {
	if (!frm.doc.qr_code || frm.doc.docstatus !== 1) return;

	const $wrapper = $(frm.fields_dict.qr_code?.wrapper);
	if (!$wrapper.length) return;

	$wrapper.find(".qr-preview").remove();
	$wrapper.append(`
		<div class="qr-preview"
			 style="text-align:center; padding:15px; margin-top:10px;
					background:#fff; border:1px solid #e2e8f0;
					border-radius:8px;">
			<img src="${frm.doc.qr_code}"
				 alt="QR Code"
				 style="max-width:180px; height:auto; image-rendering:pixelated;" />
			<div style="margin-top:8px; font-size:12px; color:#64748b;">
				${__("Scan for check-in")}
			</div>
		</div>
	`);
};

/**
 * Show today's day pass stats as a banner.
 */
arkspace.day_pass.show_stats_banner = function (frm) {
	if (!frm.is_new()) return;

	frappe.call({
		method: "arkspace.arkspace_spaces.day_pass_api.get_day_pass_stats",
		callback(r) {
			if (r.message) {
				const s = r.message;
				frm.dashboard.add_comment(
					__(
						"Today: {0} passes, {1} checked in, {2} checked out, Revenue: {3}",
						[s.total, s.checked_in, s.checked_out, s.revenue]
					),
					"blue",
					true
				);
			}
		},
	});
};

/**
 * Dialog for converting Day Pass to Membership.
 */
arkspace.day_pass.convert_dialog = function (frm) {
	const d = new frappe.ui.Dialog({
		title: __("Convert to Membership"),
		fields: [
			{
				fieldname: "plan",
				fieldtype: "Link",
				label: __("Membership Plan"),
				options: "Membership Plan",
				reqd: 1,
			},
			{
				fieldname: "billing_cycle",
				fieldtype: "Select",
				label: __("Billing Cycle"),
				options: "Monthly\nQuarterly\nYearly",
				default: "Monthly",
			},
			{
				fieldname: "credit_note",
				fieldtype: "HTML",
				options: `<p class="text-muted">
					${__(
						"The day pass amount ({0}) will be applied as credit.",
						[frm.doc.net_amount]
					)}
				</p>`,
			},
		],
		primary_action_label: __("Convert"),
		primary_action(values) {
			frappe.call({
				method: "arkspace.arkspace_spaces.day_pass_api.convert_day_pass_to_membership",
				args: {
					name: frm.doc.name,
					plan: values.plan,
					billing_cycle: values.billing_cycle,
				},
				freeze: true,
				freeze_message: __("Converting to membership..."),
				callback(r) {
					if (r.message) {
						d.hide();
						frappe.show_alert({
							message: __(
								"Membership {0} created! Credit: {1}",
								[r.message.membership, r.message.credit_applied]
							),
							indicator: "green",
						});
						frm.reload_doc();
					}
				},
			});
		},
	});
	d.show();
};

/**
 * Open a print-friendly QR page.
 */
arkspace.day_pass.print_qr = function (frm) {
	const doc = frm.doc;
	const win = window.open("", "_blank");
	win.document.write(`
		<!DOCTYPE html>
		<html>
		<head>
			<title>${__("Day Pass QR")} — ${doc.name}</title>
			<style>
				* { margin: 0; padding: 0; box-sizing: border-box; }
				body {
					font-family: -apple-system, BlinkMacSystemFont,
						'Segoe UI', Roboto, sans-serif;
					display: flex; justify-content: center; padding: 40px;
				}
				.card {
					text-align: center; max-width: 350px; padding: 30px;
					border: 2px solid #1B365D; border-radius: 12px;
				}
				.card h2 { color: #1B365D; margin-bottom: 8px; font-size: 18px; }
				.card .sub { color: #64748b; margin-bottom: 20px; font-size: 13px; }
				.card img { max-width: 220px; height: auto; image-rendering: pixelated; }
				.details { margin-top: 20px; text-align: left; font-size: 13px; color: #334155; }
				.details p { margin: 4px 0; }
				.footer { margin-top: 16px; font-size: 11px; color: #94a3b8; }
				@media print { body { padding: 0; } .card { border: 1px solid #ccc; } }
			</style>
		</head>
		<body>
			<div class="card">
				<h2>ARKSpace Day Pass</h2>
				<div class="sub">${__("Scan for check-in")}</div>
				<img src="${doc.qr_code}" />
				<div class="details">
					<p><strong>${__("Pass")}:</strong> ${doc.name}</p>
					<p><strong>${__("Guest")}:</strong> ${doc.guest_name}</p>
					<p><strong>${__("Type")}:</strong> ${doc.pass_type}</p>
					<p><strong>${__("Date")}:</strong> ${doc.pass_date}</p>
					<p><strong>${__("Space")}:</strong> ${doc.space || "—"}</p>
				</div>
				<div class="footer">${__("Powered by ARKSpace")}</div>
			</div>
			<script>window.print();</script>
		</body>
		</html>
	`);
	win.document.close();
};

// ─────────────────────────────────────────────────────────────────────────
// List View: Quick Walk-in + Bulk Actions
// ─────────────────────────────────────────────────────────────────────────

frappe.listview_settings["Day Pass"] =
	frappe.listview_settings["Day Pass"] || {};

Object.assign(frappe.listview_settings["Day Pass"], {
	get_indicator(doc) {
		const map = {
			Draft: [__("Draft"), "grey", "status,=,Draft"],
			Active: [__("Active"), "blue", "status,=,Active"],
			"Checked In": [__("Checked In"), "green", "status,=,Checked In"],
			"Checked Out": [__("Checked Out"), "darkgrey", "status,=,Checked Out"],
			Expired: [__("Expired"), "orange", "status,=,Expired"],
			Cancelled: [__("Cancelled"), "red", "status,=,Cancelled"],
		};
		return map[doc.status] || [doc.status, "grey"];
	},

	onload(listview) {
		listview.page.add_inner_button(__("Quick Walk-in"), () => {
			arkspace.day_pass.quick_walkin_dialog(listview);
		});
	},
});

/**
 * Quick Walk-in Dialog from list view.
 */
arkspace.day_pass.quick_walkin_dialog = function (listview) {
	const d = new frappe.ui.Dialog({
		title: __("Quick Walk-in Day Pass"),
		fields: [
			{
				fieldname: "guest_name",
				fieldtype: "Data",
				label: __("Guest Name"),
				reqd: 1,
			},
			{ fieldtype: "Column Break" },
			{
				fieldname: "guest_phone",
				fieldtype: "Data",
				label: __("Phone"),
				options: "Phone",
			},
			{ fieldtype: "Section Break" },
			{
				fieldname: "pass_type",
				fieldtype: "Select",
				label: __("Pass Type"),
				options: "Full Day\nHalf Day\nHourly\nEvening\nWeekend",
				default: "Full Day",
			},
			{ fieldtype: "Column Break" },
			{
				fieldname: "space",
				fieldtype: "Link",
				label: __("Space"),
				options: "Co-working Space",
				get_query: () => ({
					filters: { status: ["in", ["Available", "Reserved"]] },
				}),
			},
			{ fieldtype: "Section Break" },
			{
				fieldname: "payment_method",
				fieldtype: "Select",
				label: __("Payment"),
				options: "Cash\nCard\nOnline\nWallet\nFree",
				default: "Cash",
			},
			{ fieldtype: "Column Break" },
			{
				fieldname: "guest_email",
				fieldtype: "Data",
				label: __("Email"),
				options: "Email",
			},
		],
		primary_action_label: __("Create & Check In"),
		primary_action(values) {
			frappe.call({
				method: "arkspace.arkspace_spaces.day_pass_api.create_day_pass",
				args: values,
				freeze: true,
				freeze_message: __("Creating day pass..."),
				callback(r) {
					if (r.message) {
						d.hide();
						frappe.show_alert({
							message: __(
								"Day Pass {0} created for {1}",
								[r.message.day_pass, r.message.guest_name]
							),
							indicator: "green",
						});
						listview.refresh();
					}
				},
			});
		},
	});
	d.show();
};

// ─────────────────────────────────────────────────────────────────────────
// Real-time Events
// ─────────────────────────────────────────────────────────────────────────

frappe.realtime.on("day_pass_checked_in", function (data) {
	if (!data) return;
	frappe.show_alert({
		message: __("{0} checked in (Day Pass)", [data.guest_name || data.day_pass]),
		indicator: "green",
	});
	if (
		cur_frm &&
		cur_frm.doctype === "Day Pass" &&
		cur_frm.docname === data.day_pass
	) {
		cur_frm.reload_doc();
	}
});

frappe.realtime.on("day_pass_checked_out", function (data) {
	if (!data) return;
	frappe.show_alert({
		message: __("{0} checked out (Day Pass)", [data.guest_name || data.day_pass]),
		indicator: "blue",
	});
	if (
		cur_frm &&
		cur_frm.doctype === "Day Pass" &&
		cur_frm.docname === data.day_pass
	) {
		cur_frm.reload_doc();
	}
});


/* === analytics.js === */
// Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
// Developer Website: https://arkan.it.com
// License: MIT
// For license information, please see license.txt

// Analytics Dashboard
// Desk-side analytics dashboard with charts and KPIs

frappe.provide("arkspace.analytics");

// ─────────────── Analytics Dashboard Page ───────────────

arkspace.analytics.show_dashboard = function (branch) {
    const d = new frappe.ui.Dialog({
        title: __("ARKSpace Analytics Dashboard"),
        size: "extra-large",
        minimizable: true,
    });

    d.$body.html(`
        <div class="analytics-dashboard p-3">
            <div class="row mb-3">
                <div class="col-md-4">
                    <select class="form-control branch-filter">
                        <option value="">${__("All Branches")}</option>
                    </select>
                </div>
                <div class="col-md-4">
                    <select class="form-control period-filter">
                        <option value="30">${__("Last 30 Days")}</option>
                        <option value="60">${__("Last 60 Days")}</option>
                        <option value="90" selected>${__("Last 90 Days")}</option>
                        <option value="180">${__("Last 6 Months")}</option>
                        <option value="365">${__("Last Year")}</option>
                    </select>
                </div>
                <div class="col-md-4">
                    <button class="btn btn-primary btn-sm refresh-btn">
                        <i class="fa fa-refresh"></i> ${__("Refresh")}
                    </button>
                </div>
            </div>

            <!-- KPI Cards -->
            <div class="row kpi-cards mb-4"></div>

            <!-- Charts -->
            <div class="row">
                <div class="col-md-6 mb-3">
                    <div class="card"><div class="card-body">
                        <h6>${__("Revenue Trends")}</h6>
                        <div id="revenue-chart" style="height:250px"></div>
                    </div></div>
                </div>
                <div class="col-md-6 mb-3">
                    <div class="card"><div class="card-body">
                        <h6>${__("Booking Patterns by Hour")}</h6>
                        <div id="hourly-chart" style="height:250px"></div>
                    </div></div>
                </div>
            </div>
            <div class="row">
                <div class="col-md-6 mb-3">
                    <div class="card"><div class="card-body">
                        <h6>${__("Member Growth")}</h6>
                        <div id="member-chart" style="height:250px"></div>
                    </div></div>
                </div>
                <div class="col-md-6 mb-3">
                    <div class="card"><div class="card-body">
                        <h6>${__("Space Utilization")}</h6>
                        <div id="utilization-chart" style="height:250px"></div>
                    </div></div>
                </div>
            </div>
            <div class="row">
                <div class="col-md-6 mb-3">
                    <div class="card"><div class="card-body">
                        <h6>${__("Revenue Forecast")}</h6>
                        <div id="forecast-chart" style="height:250px"></div>
                    </div></div>
                </div>
                <div class="col-md-6 mb-3">
                    <div class="card"><div class="card-body">
                        <h6>${__("Occupancy Heatmap")}</h6>
                        <div id="heatmap-container" style="height:250px; overflow:auto"></div>
                    </div></div>
                </div>
            </div>
        </div>
    `);

    // Load branches
    frappe.call({
        method: "frappe.client.get_list",
        args: { doctype: "Branch", fields: ["name"], limit_page_length: 0 },
        callback(r) {
            if (r.message) {
                const sel = d.$body.find(".branch-filter");
                r.message.forEach((b) => {
                    sel.append(`<option value="${b.name}">${b.name}</option>`);
                });
                if (branch) sel.val(branch);
            }
        },
    });

    function load_all() {
        const br = d.$body.find(".branch-filter").val();
        const days = parseInt(d.$body.find(".period-filter").val());
        const from_date = frappe.datetime.add_days(frappe.datetime.nowdate(), -days);
        const to_date = frappe.datetime.nowdate();

        load_kpis(d.$body, br);
        load_revenue_chart(d.$body, br, from_date, to_date);
        load_booking_patterns(d.$body, br, from_date, to_date);
        load_member_chart(d.$body, br, from_date, to_date);
        load_utilization_chart(d.$body, br, from_date, to_date);
        load_forecast_chart(d.$body, br);
        load_heatmap(d.$body, br, from_date, to_date);
    }

    d.$body.find(".refresh-btn").on("click", load_all);
    d.$body.find(".branch-filter, .period-filter").on("change", load_all);

    d.show();
    load_all();
};

// ─────────────── KPI Cards ───────────────

function load_kpis($body, branch) {
    frappe.call({
        method: "arkspace.arkspace_core.analytics_engine.get_dashboard_kpis",
        args: { branch: branch || undefined },
        callback(r) {
            if (!r.message) return;
            const d = r.message;
            const wow = d.wow_booking_change;
            const arrow = wow >= 0 ? "↑" : "↓";
            const color = wow >= 0 ? "green" : "red";

            $body.find(".kpi-cards").html(`
                ${kpi_card(__("Occupancy"), d.occupancy_rate + "%", "blue")}
                ${kpi_card(__("Today's Bookings"), d.todays_bookings, "orange")}
                ${kpi_card(__("Checked In"), d.checked_in, "green")}
                ${kpi_card(__("Active Members"), d.active_members, "purple")}
                ${kpi_card(__("Month Revenue"), format_currency(d.month_revenue), "cyan")}
                ${kpi_card(__("Day Passes"), d.day_passes_today, "yellow")}
                ${kpi_card(__("Visitors"), d.visitors_today, "pink")}
                ${kpi_card(__("WoW Change"), `<span style="color:${color}">${arrow} ${Math.abs(wow)}%</span>`, "gray")}
            `);
        },
    });
}

function kpi_card(label, value, color) {
    return `<div class="col-md-3 col-6 mb-2">
        <div class="card" style="border-left: 3px solid var(--${color}-500, #0089ff)">
            <div class="card-body p-2">
                <small class="text-muted">${label}</small>
                <h5 class="mb-0">${value}</h5>
            </div>
        </div>
    </div>`;
}

// ─────────────── Revenue Trends Chart ───────────────

function load_revenue_chart($body, branch, from_date, to_date) {
    frappe.call({
        method: "arkspace.arkspace_core.analytics_engine.get_revenue_trends",
        args: { branch, period: "monthly", from_date, to_date },
        callback(r) {
            if (!r.message || !r.message.labels.length) return;
            const data = r.message;
            new frappe.Chart("#revenue-chart", {
                data: {
                    labels: data.labels,
                    datasets: [
                        { name: __("Bookings"), values: data.booking_revenue },
                        { name: __("Memberships"), values: data.membership_revenue },
                        { name: __("Day Passes"), values: data.day_pass_revenue },
                    ],
                },
                type: "bar",
                height: 220,
                colors: ["#4299e1", "#48bb78", "#ed8936"],
                barOptions: { stacked: 1 },
            });
        },
    });
}

// ─────────────── Booking Patterns Chart ───────────────

function load_booking_patterns($body, branch, from_date, to_date) {
    frappe.call({
        method: "arkspace.arkspace_core.analytics_engine.get_booking_patterns",
        args: { branch, from_date, to_date },
        callback(r) {
            if (!r.message) return;
            const data = r.message;
            new frappe.Chart("#hourly-chart", {
                data: {
                    labels: data.hourly.labels,
                    datasets: [{ name: __("Bookings"), values: data.hourly.values }],
                },
                type: "line",
                height: 220,
                colors: ["#4299e1"],
                lineOptions: { regionFill: 1 },
            });
        },
    });
}

// ─────────────── Member Growth Chart ───────────────

function load_member_chart($body, branch, from_date, to_date) {
    frappe.call({
        method: "arkspace.arkspace_core.analytics_engine.get_member_analytics",
        args: { branch, from_date, to_date },
        callback(r) {
            if (!r.message) return;
            const data = r.message;
            const months = data.growth.map((g) => g.month);
            const growth_vals = data.growth.map((g) => g.new_members);
            const churn_map = {};
            data.churn.forEach((c) => { churn_map[c.month] = c.churned; });
            const churn_vals = months.map((m) => -(churn_map[m] || 0));

            if (!months.length) return;
            new frappe.Chart("#member-chart", {
                data: {
                    labels: months,
                    datasets: [
                        { name: __("New Members"), values: growth_vals },
                        { name: __("Churned"), values: churn_vals },
                    ],
                },
                type: "bar",
                height: 220,
                colors: ["#48bb78", "#e53e3e"],
            });
        },
    });
}

// ─────────────── Space Utilization Chart ───────────────

function load_utilization_chart($body, branch, from_date, to_date) {
    frappe.call({
        method: "arkspace.arkspace_core.analytics_engine.get_space_utilization",
        args: { branch, from_date, to_date },
        callback(r) {
            if (!r.message || !r.message.spaces.length) return;
            const spaces = r.message.spaces.slice(0, 10);
            new frappe.Chart("#utilization-chart", {
                data: {
                    labels: spaces.map((s) => s.space_name || s.space),
                    datasets: [{
                        name: __("Utilization %"),
                        values: spaces.map((s) => s.utilization_rate),
                    }],
                },
                type: "bar",
                height: 220,
                colors: ["#667eea"],
            });
        },
    });
}

// ─────────────── Revenue Forecast Chart ───────────────

function load_forecast_chart($body, branch) {
    frappe.call({
        method: "arkspace.arkspace_core.analytics_engine.get_revenue_forecast",
        args: { branch, months_ahead: 3 },
        callback(r) {
            if (!r.message || !r.message.historical) return;
            const data = r.message;
            if (data.message) {
                $body.find("#forecast-chart").html(
                    `<p class="text-muted text-center mt-5">${data.message}</p>`
                );
                return;
            }
            const labels = data.historical.map((h) => h.month);
            const values = data.historical.map((h) => h.revenue);

            data.forecast.forEach((f) => {
                labels.push(f.month + " ⟨F⟩");
                values.push(f.predicted_revenue);
            });

            new frappe.Chart("#forecast-chart", {
                data: {
                    labels: labels,
                    datasets: [{ name: __("Revenue"), values: values }],
                    yMarkers: [{ label: __("Forecast Start"), value: values[data.historical.length - 1] || 0 }],
                },
                type: "line",
                height: 220,
                colors: ["#805ad5"],
                lineOptions: { regionFill: 1 },
            });
        },
    });
}

// ─────────────── Occupancy Heatmap ───────────────

function load_heatmap($body, branch, from_date, to_date) {
    frappe.call({
        method: "arkspace.arkspace_core.analytics_engine.get_occupancy_heatmap",
        args: { branch, from_date, to_date },
        callback(r) {
            if (!r.message) return;
            const data = r.message;
            const max_val = data.max_value || 1;
            const days = data.days;

            let html = '<table class="table table-sm table-bordered" style="font-size:11px">';
            html += '<thead><tr><th></th>';
            for (let h = 6; h <= 22; h++) {
                html += `<th class="text-center">${h}</th>`;
            }
            html += '</tr></thead><tbody>';

            for (let d = 0; d < 7; d++) {
                html += `<tr><td><strong>${days[d]}</strong></td>`;
                for (let h = 6; h <= 22; h++) {
                    const val = data.heatmap[d][h];
                    const intensity = Math.min(val / max_val, 1);
                    const bg = intensity > 0
                        ? `rgba(66, 153, 225, ${0.1 + intensity * 0.8})`
                        : "transparent";
                    const text_color = intensity > 0.5 ? "#fff" : "#333";
                    html += `<td class="text-center" style="background:${bg};color:${text_color}">${val || ""}</td>`;
                }
                html += '</tr>';
            }
            html += '</tbody></table>';
            $body.find("#heatmap-container").html(html);
        },
    });
}

// ─────────────── Analytics list view banner ───────────────

$(document).on("app_ready", function () {
    // Add analytics button to ARKSpace Settings
    if (cur_page && cur_page.page && cur_page.page.wrapper) {
        // Available via frappe.call from anywhere
    }
});

// Quick access from any page
frappe.provide("arkspace");
arkspace.open_analytics = function (branch) {
    arkspace.analytics.show_dashboard(branch);
};


/* === multi_location.js === */
// Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
// Developer Website: https://arkan.it.com
// License: MIT
// For license information, please see license.txt

// Multi-Location / Branch Management

frappe.provide("arkspace.branches");

// ─────────────── ARKSpace Branch Form ───────────────

frappe.ui.form.on("ARKSpace Branch", {
    refresh(frm) {
        if (!frm.is_new()) {
            // Recalculate capacity button
            frm.add_custom_button(__("Recalculate Capacity"), function () {
                frm.call("recalculate_capacity").then((r) => {
                    if (r.message) {
                        frappe.show_alert({
                            message: __("Capacity updated: {0} max, {1} occupied", [
                                r.message.max_capacity,
                                r.message.current_occupancy,
                            ]),
                            indicator: "green",
                        });
                        frm.reload_doc();
                    }
                });
            });

            // View Spaces button
            frm.add_custom_button(__("View Spaces"), function () {
                frappe.set_route("List", "Co-working Space", {
                    branch: frm.doc.branch || frm.doc.branch_name,
                });
            }, __("View"));

            // View Bookings button
            frm.add_custom_button(__("View Bookings"), function () {
                frappe.set_route("List", "Space Booking", {
                    space: ["in", (frm._space_names || [])],
                });
            }, __("View"));

            // View Members button
            frm.add_custom_button(__("View Members"), function () {
                frappe.set_route("List", "Membership", {
                    branch: frm.doc.branch || frm.doc.branch_name,
                    status: "Active",
                });
            }, __("View"));

            // Analytics button
            frm.add_custom_button(__("Analytics"), function () {
                if (arkspace.analytics && arkspace.analytics.show_dashboard) {
                    arkspace.analytics.show_dashboard(frm.doc.branch || frm.doc.branch_name);
                } else {
                    frappe.set_route("analytics");
                }
            }, __("View"));

            // Load branch stats summary
            load_branch_stats(frm);
        }
    },
});

function load_branch_stats(frm) {
    frappe.call({
        method: "arkspace.arkspace_core.multi_location.get_branch_stats",
        args: { branch: frm.doc.name },
        callback(r) {
            if (!r.message) return;
            const s = r.message;
            frm.dashboard.add_indicator(
                __("Spaces: {0}", [s.total_spaces]), "blue"
            );
            frm.dashboard.add_indicator(
                __("Bookings: {0}", [s.bookings.total]), "orange"
            );
            frm.dashboard.add_indicator(
                __("Members: {0}", [s.active_members]), "green"
            );
            frm.dashboard.add_indicator(
                __("Revenue: {0}", [format_currency(s.bookings.revenue)]), "purple"
            );
        },
    });
}

// ─────────────── Cross-Location Search Dialog ───────────────

arkspace.branches.cross_location_search = function () {
    const d = new frappe.ui.Dialog({
        title: __("Cross-Location Space Search"),
        fields: [
            {
                fieldname: "space_type",
                fieldtype: "Link",
                label: __("Space Type"),
                options: "Space Type",
            },
            {
                fieldname: "date",
                fieldtype: "Date",
                label: __("Date"),
                default: frappe.datetime.nowdate(),
                reqd: 1,
            },
            { fieldtype: "Column Break" },
            {
                fieldname: "start_time",
                fieldtype: "Time",
                label: __("Start Time"),
            },
            {
                fieldname: "end_time",
                fieldtype: "Time",
                label: __("End Time"),
            },
            { fieldtype: "Section Break", label: __("Results") },
            {
                fieldname: "results_html",
                fieldtype: "HTML",
            },
        ],
        size: "large",
        primary_action_label: __("Search"),
        primary_action(values) {
            frappe.call({
                method: "arkspace.arkspace_core.multi_location.cross_location_search",
                args: {
                    space_type: values.space_type,
                    date: values.date,
                    start_time: values.start_time,
                    end_time: values.end_time,
                },
                callback(r) {
                    if (!r.message || !r.message.length) {
                        d.fields_dict.results_html.$wrapper.html(
                            `<p class="text-muted text-center">${__("No available spaces found")}</p>`
                        );
                        return;
                    }

                    let html = "";
                    r.message.forEach((branch_data) => {
                        const b = branch_data.branch;
                        html += `<div class="card mb-3">
                            <div class="card-header">
                                <strong>${b.branch_name}</strong>
                                <span class="text-muted"> — ${b.city || ""}</span>
                                <span class="badge badge-primary float-right">${branch_data.count} ${__("available")}</span>
                            </div>
                            <div class="card-body p-0">
                                <table class="table table-sm mb-0">
                                    <thead><tr>
                                        <th>${__("Space")}</th>
                                        <th>${__("Type")}</th>
                                        <th>${__("Capacity")}</th>
                                        <th>${__("Rate")}</th>
                                        <th></th>
                                    </tr></thead>
                                    <tbody>`;

                        branch_data.available_spaces.forEach((s) => {
                            html += `<tr>
                                <td>${s.space_name}</td>
                                <td>${s.space_type || "-"}</td>
                                <td>${s.capacity || "-"}</td>
                                <td>${format_currency(s.hourly_rate)}/hr</td>
                                <td><a href="/app/co-working-space/${s.name}" class="btn btn-xs btn-primary">${__("Book")}</a></td>
                            </tr>`;
                        });

                        html += `</tbody></table></div></div>`;
                    });

                    d.fields_dict.results_html.$wrapper.html(html);
                },
            });
        },
    });
    d.show();
};

// ─────────────── Branch Comparison Dialog ───────────────

arkspace.branches.compare = function () {
    frappe.call({
        method: "arkspace.arkspace_core.multi_location.get_branch_comparison",
        callback(r) {
            if (!r.message || !r.message.branches.length) {
                frappe.msgprint(__("No branch data available"));
                return;
            }

            const data = r.message;
            let html = `<div class="table-responsive">
                <table class="table table-sm table-hover">
                    <thead><tr>
                        <th>${__("Branch")}</th>
                        <th>${__("Spaces")}</th>
                        <th>${__("Bookings")}</th>
                        <th>${__("Members")}</th>
                        <th>${__("Day Passes")}</th>
                        <th>${__("Revenue")}</th>
                    </tr></thead><tbody>`;

            data.branches.forEach((b) => {
                html += `<tr>
                    <td><strong>${b.branch}</strong><br><small class="text-muted">${b.city || ""}</small></td>
                    <td>${b.total_spaces}</td>
                    <td>${b.bookings.total}</td>
                    <td>${b.active_members}</td>
                    <td>${b.day_passes}</td>
                    <td>${format_currency(b.bookings.revenue)}</td>
                </tr>`;
            });

            html += "</tbody></table></div>";

            frappe.msgprint({
                title: __("Branch Comparison — {0} to {1}", [data.period.from, data.period.to]),
                message: html,
                wide: true,
            });
        },
    });
};

// ─────────────── Transfer Membership Dialog ───────────────

arkspace.branches.transfer_membership = function (membership) {
    frappe.prompt(
        {
            fieldname: "target_branch",
            fieldtype: "Link",
            label: __("Target Branch"),
            options: "ARKSpace Branch",
            reqd: 1,
        },
        function (values) {
            frappe.call({
                method: "arkspace.arkspace_core.multi_location.transfer_membership",
                args: {
                    membership: membership,
                    target_branch: values.target_branch,
                },
                callback(r) {
                    if (r.message && r.message.status === "success") {
                        frappe.show_alert({
                            message: r.message.message,
                            indicator: "green",
                        });
                        cur_frm && cur_frm.reload_doc();
                    }
                },
            });
        },
        __("Transfer Membership"),
        __("Transfer")
    );
};

// ─────────────── Add branch button to Membership form ───────────────

$(document).on("form-refresh", function (e, frm) {
    if (frm.doctype === "Membership" && !frm.is_new() && frm.doc.status === "Active") {
        frm.add_custom_button(__("Transfer Branch"), function () {
            arkspace.branches.transfer_membership(frm.doc.name);
        });
    }
});


/* === community.js === */
// Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
// Developer Website: https://arkan.it.com
// License: MIT
// For license information, please see license.txt

// Community & Networking

frappe.provide("arkspace.community");

// ─────────────── Community Post Form ───────────────

frappe.ui.form.on("Community Post", {
    refresh(frm) {
        if (!frm.is_new()) {
            // Like button
            frm.add_custom_button(
                frm._user_liked ? __("Unlike ❤️") : __("Like ♡"),
                function () {
                    frm.call("toggle_like").then((r) => {
                        if (r.message) {
                            frm._user_liked = r.message.liked;
                            frappe.show_alert({
                                message: r.message.liked ? __("Liked!") : __("Unliked"),
                                indicator: r.message.liked ? "red" : "gray",
                            });
                            frm.reload_doc();
                        }
                    });
                }
            );

            // Pin/Unpin for admins
            if (frappe.user.has_role("ARKSpace Admin") || frappe.user.has_role("System Manager")) {
                frm.add_custom_button(
                    frm.doc.is_pinned ? __("Unpin") : __("Pin"),
                    function () {
                        frm.set_value("is_pinned", frm.doc.is_pinned ? 0 : 1);
                        frm.save();
                    }
                );
            }

            // Increment views
            frm.call("increment_views");

            // Show engagement stats
            frm.dashboard.add_indicator(
                __("❤️ {0} likes", [frm.doc.likes_count]), "red"
            );
            frm.dashboard.add_indicator(
                __("💬 {0} comments", [frm.doc.comments_count]), "blue"
            );
            frm.dashboard.add_indicator(
                __("👁 {0} views", [frm.doc.views_count]), "gray"
            );
        }
    },
});

// ─────────────── Community Event Form ───────────────

frappe.ui.form.on("Community Event", {
    refresh(frm) {
        if (!frm.is_new()) {
            if (frm.doc.status !== "Cancelled" && frm.doc.status !== "Completed") {
                frm.add_custom_button(__("Register"), function () {
                    frm.call("register_attendee").then((r) => {
                        if (r.message) {
                            frappe.show_alert({
                                message: __("Registered successfully!"),
                                indicator: "green",
                            });
                            frm.reload_doc();
                        }
                    });
                });

                frm.add_custom_button(__("View Attendees"), function () {
                    frappe.call({
                        method: "arkspace.arkspace_community.community.get_event_attendees",
                        args: { event: frm.doc.name },
                        callback(r) {
                            if (!r.message || !r.message.length) {
                                frappe.msgprint(__("No attendees registered yet"));
                                return;
                            }
                            let html = '<div class="list-group">';
                            r.message.forEach((a) => {
                                const img = a.image
                                    ? `<img src="${a.image}" class="avatar avatar-small" />`
                                    : '<span class="avatar avatar-small standard-image">👤</span>';
                                html += `<div class="list-group-item d-flex align-items-center">
                                    ${img}
                                    <span class="ml-2">${a.name}</span>
                                    <small class="ml-auto text-muted">${frappe.datetime.prettyDate(a.registered_at)}</small>
                                </div>`;
                            });
                            html += "</div>";
                            frappe.msgprint({ title: __("Attendees"), message: html, wide: true });
                        },
                    });
                });
            }

            // Attendance indicator
            frm.dashboard.add_indicator(
                __("{0}/{1} attendees", [frm.doc.current_attendees, frm.doc.max_attendees]),
                frm.doc.current_attendees >= frm.doc.max_attendees ? "red" : "green"
            );
        }
    },
});

// ─────────────── Networking Request Form ───────────────

frappe.ui.form.on("Networking Request", {
    refresh(frm) {
        if (!frm.is_new() && frm.doc.status === "Pending") {
            if (frappe.session.user === frm.doc.to_member) {
                frm.add_custom_button(__("Accept"), function () {
                    frm.call("accept").then(() => {
                        frappe.show_alert({ message: __("Connection accepted!"), indicator: "green" });
                        frm.reload_doc();
                    });
                }, __("Respond"));

                frm.add_custom_button(__("Decline"), function () {
                    frm.call("decline").then(() => {
                        frappe.show_alert({ message: __("Request declined"), indicator: "orange" });
                        frm.reload_doc();
                    });
                }, __("Respond"));
            }
        }
    },
});

// ─────────────── Community Feed Dialog ───────────────

arkspace.community.open_feed = function (branch) {
    const d = new frappe.ui.Dialog({
        title: __("Community Board"),
        size: "extra-large",
        minimizable: true,
    });

    d.$body.html(`
        <div class="community-feed p-3">
            <div class="row mb-3">
                <div class="col-md-3">
                    <select class="form-control post-type-filter">
                        <option value="">${__("All Types")}</option>
                        <option value="Discussion">${__("Discussion")}</option>
                        <option value="Announcement">${__("Announcement")}</option>
                        <option value="Question">${__("Question")}</option>
                        <option value="Idea">${__("Idea")}</option>
                        <option value="Showcase">${__("Showcase")}</option>
                        <option value="Job Posting">${__("Job Posting")}</option>
                    </select>
                </div>
                <div class="col-md-6"></div>
                <div class="col-md-3">
                    <button class="btn btn-primary btn-sm new-post-btn">
                        ✏️ ${__("New Post")}
                    </button>
                </div>
            </div>
            <div class="feed-container"></div>
            <div class="text-center mt-3">
                <button class="btn btn-default btn-sm load-more-btn" style="display:none">
                    ${__("Load More")}
                </button>
            </div>
        </div>
    `);

    let current_page = 0;

    function load_feed(append) {
        if (!append) current_page = 0;
        frappe.call({
            method: "arkspace.arkspace_community.community.get_community_feed",
            args: {
                branch: branch || undefined,
                post_type: d.$body.find(".post-type-filter").val() || undefined,
                page: current_page,
            },
            callback(r) {
                if (!r.message) return;
                const data = r.message;
                let html = "";
                data.posts.forEach((p) => {
                    const pinned = p.is_pinned ? '📌 ' : '';
                    const liked_class = p.user_liked ? "text-danger" : "";
                    const type_badge = `<span class="badge badge-light">${p.post_type}</span>`;
                    html += `<div class="card mb-2">
                        <div class="card-body p-3">
                            <div class="d-flex justify-content-between">
                                <h6 class="mb-1">${pinned}${p.title} ${type_badge}</h6>
                                <small class="text-muted">${frappe.datetime.prettyDate(p.creation)}</small>
                            </div>
                            <small class="text-muted">${p.author_name || p.author}</small>
                            <p class="mt-2 mb-2" style="max-height:100px;overflow:hidden">${p.content}</p>
                            <div class="d-flex">
                                <span class="${liked_class} mr-3 like-btn" data-post="${p.name}" style="cursor:pointer">
                                    ❤️ ${p.likes_count}
                                </span>
                                <span class="mr-3">💬 ${p.comments_count}</span>
                                <span>👁 ${p.views_count}</span>
                                ${p.tags ? `<span class="ml-auto text-muted">${p.tags}</span>` : ''}
                            </div>
                        </div>
                    </div>`;
                });

                if (append) {
                    d.$body.find(".feed-container").append(html);
                } else {
                    d.$body.find(".feed-container").html(html || `<p class="text-muted text-center">${__("No posts yet")}</p>`);
                }

                d.$body.find(".load-more-btn").toggle(data.has_more);
            },
        });
    }

    d.$body.find(".post-type-filter").on("change", () => load_feed(false));
    d.$body.find(".load-more-btn").on("click", () => { current_page++; load_feed(true); });
    d.$body.find(".new-post-btn").on("click", () => frappe.new_doc("Community Post"));

    // Like handler
    d.$body.on("click", ".like-btn", function () {
        const post = $(this).data("post");
        frappe.call({
            method: "arkspace.arkspace_community.community.like_post",
            args: { post },
            callback() { load_feed(false); },
        });
    });

    d.show();
    load_feed(false);
};

// ─────────────── Realtime Events ───────────────

frappe.realtime.on("new_community_post", function (data) {
    frappe.show_alert({
        message: __("New post: {0}", [data.title]),
        indicator: "blue",
    });
});

frappe.realtime.on("new_networking_request", function (data) {
    frappe.show_alert({
        message: __("{0} wants to connect with you", [data.from_name]),
        indicator: "green",
    });
});

frappe.realtime.on("networking_request_accepted", function (data) {
    frappe.show_alert({
        message: __("Your networking request was accepted!"),
        indicator: "green",
    });
});

frappe.realtime.on("event_registration", function (data) {
    if (cur_frm && cur_frm.doctype === "Community Event" && cur_frm.doc.name === data.event) {
        cur_frm.reload_doc();
    }
});


/* === fv_integration.js === */
// Copyright (c) 2024, Arkan Lab — https://arkan.it.com
// License: MIT
// frappe_visual Integration for ARKSpace

(function() {
    "use strict";

    // App branding registration
    const APP_CONFIG = {
        name: "arkspace",
        title: "ARKSpace",
        color: "#1B365D",
        module: "ARKSpace Core",
    };

    // Initialize visual enhancements when ready
    $(document).on("app_ready", function() {
        // Register app color with visual theme system
        if (frappe.visual && frappe.visual.ThemeManager) {
            try {
                document.documentElement.style.setProperty(
                    "--arkspace-primary",
                    APP_CONFIG.color
                );
            } catch(e) {}
        }

        // Initialize bilingual tooltips for Arabic support
        if (frappe.visual && frappe.visual.bilingualTooltip) {
            // bilingualTooltip auto-initializes — just ensure it's active
        }
    });

    // Route-based visual page rendering
    $(document).on("page-change", function() {
        if (!frappe.visual || !frappe.visual.generator) return;

    // Visual Settings Page
    if (frappe.get_route_str() === 'arkspace-settings') {
        const page = frappe.container.page;
        if (page && page.main && frappe.visual.generator) {
            frappe.visual.generator.settingsPage(
                page.main[0] || page.main,
                "ARKSpace Settings"
            );
        }
    }

    // Visual Reports Hub
    if (frappe.get_route_str() === 'arkspace-reports') {
        const page = frappe.container.page;
        if (page && page.main && frappe.visual.generator) {
            frappe.visual.generator.reportsHub(
                page.main[0] || page.main,
                "ARKSpace Core"
            );
        }
    }
    });
})();

