/**
 * ARKSpace Contextual Help — نظام المساعدة السياقية
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

	// ── Topic help content per DocType ──
	const HELP_TOPICS = {
		"Co-working Space": {
			title: __("Spaces — المساحات"),
			icon: "🏢",
			slides: [
				{ title: __("What is a Space?"), body: __("A co-working space is a bookable resource — desks, rooms, studios, or any physical area.") },
				{ title: __("Space Types"), body: __("Organize spaces by type: Hot Desk, Private Office, Meeting Room, Event Hall, Studio, etc.") },
				{ title: __("Capacity & Pricing"), body: __("Set capacity, hourly/daily/monthly rates, and dynamic pricing rules.") },
				{ title: __("Floor Plan"), body: __("Link spaces to floor zones for the Live Floor Plan view.") },
			],
		},
		"Space Booking": {
			title: __("Bookings — الحجوزات"),
			icon: "📅",
			slides: [
				{ title: __("Creating a Booking"), body: __("Select space, date/time range, and member. Pricing is auto-calculated.") },
				{ title: __("Booking Lifecycle"), body: __("Draft → Submitted → Confirmed → Checked In → Checked Out → Invoiced") },
				{ title: __("QR Check-in"), body: __("Each confirmed booking generates a QR code for self-service check-in.") },
				{ title: __("Cancellation"), body: __("Cancel before check-in. Refund policies apply per space type.") },
			],
		},
		"Membership": {
			title: __("Memberships — العضويات"),
			icon: "🎫",
			slides: [
				{ title: __("Plans & Tiers"), body: __("Create membership plans with different access levels, amenities, and pricing.") },
				{ title: __("Membership Lifecycle"), body: __("New → Active → Expiring → Expired. Auto-renewal and manual renewal supported.") },
				{ title: __("Benefits"), body: __("Each plan includes benefits: booking credits, locker access, event invites, etc.") },
			],
		},
		"Day Pass": {
			title: __("Day Pass — تصاريح اليوم"),
			icon: "🎟️",
			slides: [
				{ title: __("Quick Access"), body: __("Day passes provide single-day access without a full membership.") },
				{ title: __("Check-in"), body: __("Issue at front desk or online. QR code generated for entry.") },
				{ title: __("Auto-Expiry"), body: __("Passes expire at end of business day automatically.") },
			],
		},
		"Workspace Lead": {
			title: __("CRM — إدارة العملاء"),
			icon: "🎯",
			slides: [
				{ title: __("Lead Pipeline"), body: __("Track prospective members from inquiry to tour to conversion.") },
				{ title: __("Tour Scheduling"), body: __("Schedule and track space tours for leads.") },
				{ title: __("Conversion"), body: __("Convert leads to members or booking customers.") },
			],
		},
		"Community Event": {
			title: __("Events — الفعاليات"),
			icon: "🎉",
			slides: [
				{ title: __("Event Management"), body: __("Create events with capacity limits, RSVP, and space allocation.") },
				{ title: __("Member Events"), body: __("Events can be open to all or restricted to membership tiers.") },
			],
		},
		"Space Type": {
			title: __("Space Types — أنواع المساحات"),
			icon: "🏷️",
			slides: [
				{ title: __("What are Space Types?"), body: __("Space Types categorize your physical resources — Hot Desk, Private Office, Meeting Room, Event Hall, Studio, etc.") },
				{ title: __("Pricing by Type"), body: __("Each type can have its own default pricing structure: hourly, daily, or monthly rates.") },
			],
		},
		"Pricing Rule": {
			title: __("Pricing Rules — قواعد التسعير"),
			icon: "💰",
			slides: [
				{ title: __("Dynamic Pricing"), body: __("Create rules that adjust pricing based on peak hours, membership tier, duration, or advance booking.") },
				{ title: __("Rule Priority"), body: __("Rules are evaluated by priority. The first matching rule determines the final price.") },
			],
		},
		"Visitor Log": {
			title: __("Visitors — الزوار"),
			icon: "🚪",
			slides: [
				{ title: __("Visitor Management"), body: __("Pre-register visitors, track walk-ins, and generate entry badges with QR codes.") },
				{ title: __("Host Notification"), body: __("When a visitor checks in, the host member is automatically notified.") },
			],
		},
		"Workspace Tour": {
			title: __("Tours — الجولات"),
			icon: "🗺️",
			slides: [
				{ title: __("Tour Scheduling"), body: __("Schedule guided tours for prospective members. Track attendance and follow-up.") },
				{ title: __("Lead Conversion"), body: __("Convert tour visitors into members or booking customers directly from the tour record.") },
			],
		},
		"Community Post": {
			title: __("Community Board — لوحة المجتمع"),
			icon: "💬",
			slides: [
				{ title: __("Community Posts"), body: __("Members can share knowledge, ask questions, and post announcements on the community board.") },
				{ title: __("Engagement"), body: __("Posts support likes, pinning, and comment threads to foster engagement.") },
			],
		},
		"Networking Request": {
			title: __("Networking — التواصل"),
			icon: "🤝",
			slides: [
				{ title: __("Connect with Members"), body: __("Send networking requests to other members based on skills and interests.") },
				{ title: __("Accept or Decline"), body: __("Recipients can accept or decline requests. Accepted connections appear in your network.") },
			],
		},
		"Training Session": {
			title: __("Training — التدريب"),
			icon: "🎓",
			slides: [
				{ title: __("Training Sessions"), body: __("Create and manage training sessions for member skill development.") },
				{ title: __("Progress Tracking"), body: __("Track attendance and completion status for each participant.") },
			],
		},
		"Member Contract": {
			title: __("Contracts — العقود"),
			icon: "📄",
			slides: [
				{ title: __("Contract Management"), body: __("Create and manage contracts for memberships, space rentals, and services.") },
				{ title: __("Legal Documents"), body: __("Attach legal documents and templates to contracts for compliance tracking.") },
			],
		},
		"Analytics Snapshot": {
			title: __("Analytics — التحليلات"),
			icon: "📊",
			slides: [
				{ title: __("Daily Snapshots"), body: __("Automatic daily captures of occupancy, revenue, and membership metrics.") },
				{ title: __("Trend Analysis"), body: __("Compare snapshots over time to identify trends and optimize operations.") },
			],
		},
		"ARKSpace Settings": {
			title: __("Settings — الإعدادات"),
			icon: "⚙️",
			slides: [
				{ title: __("App Configuration"), body: __("Configure payment gateways, notification preferences, QR settings, and branch defaults.") },
				{ title: __("Integration Setup"), body: __("Connect ERPNext billing, WhatsApp notifications, and CAPS security from one place.") },
			],
		},
		"ARKSpace Branch": {
			title: __("Branches — الفروع"),
			icon: "🏢",
			slides: [
				{ title: __("Multi-Branch Management"), body: __("Manage multiple locations with independent settings but centralized reporting.") },
				{ title: __("Branch Transfers"), body: __("Transfer members and bookings between branches seamlessly.") },
			],
		},
		"Online Payment": {
			title: __("Online Payments — الدفع الإلكتروني"),
			icon: "💳",
			slides: [
				{ title: __("Payment Gateways"), body: __("Accept payments via Stripe, Tap, or other gateways configured in ARKSpace Settings.") },
				{ title: __("Payment Reconciliation"), body: __("Webhook-based automatic reconciliation keeps your invoices and payments in sync.") },
			],
		},
		"Space Amenity": {
			title: __("Space Amenities — مرافق المساحة"),
			icon: "🛋️",
			slides: [
				{ title: __("What are Space Amenities?"), body: __("Amenities are the features available in a space — WiFi, projector, whiteboard, coffee machine, etc.") },
				{ title: __("Link to Spaces"), body: __("Assign amenities to spaces so members can filter bookings by required facilities.") },
			],
		},
		"Space Image": {
			title: __("Space Images — صور المساحة"),
			icon: "🖼️",
			slides: [
				{ title: __("Gallery Images"), body: __("Upload multiple images for each space to showcase in the portal and booking screen.") },
				{ title: __("Primary Image"), body: __("Mark one image as the primary thumbnail that appears in listings and cards.") },
			],
		},
		"Membership Plan": {
			title: __("Membership Plans — خطط العضوية"),
			icon: "📋",
			slides: [
				{ title: __("Plan Setup"), body: __("Define membership tiers with different access levels, credit allowances, and amenity bundles.") },
				{ title: __("Plan Pricing"), body: __("Set monthly, quarterly, or annual pricing. Link to ERPNext Item for invoicing.") },
				{ title: __("Plan Benefits"), body: __("Specify included booking hours, locker access, event invites, and printing credits per plan.") },
			],
		},
		"Credit Transaction": {
			title: __("Credit Transactions — معاملات الرصيد"),
			icon: "💱",
			slides: [
				{ title: __("Credit Flow"), body: __("Each booking, day pass, or amenity usage deducts credits. Top-ups and plan renewals add credits.") },
				{ title: __("Transaction Log"), body: __("Every credit movement is logged with type, amount, reference document, and timestamp.") },
			],
		},
		"Member Credit Wallet": {
			title: __("Credit Wallet — محفظة الرصيد"),
			icon: "👛",
			slides: [
				{ title: __("Wallet Balance"), body: __("Each member has a credit wallet showing current balance, total earned, and total spent.") },
				{ title: __("Top-up Methods"), body: __("Credits can be added via online payment, manual adjustment, or membership plan allocation.") },
			],
		},
		"Member Skill": {
			title: __("Member Skills — مهارات العضو"),
			icon: "🧠",
			slides: [
				{ title: __("Skill Profiles"), body: __("Members can list their skills and expertise for the community directory and networking.") },
				{ title: __("Skill Matching"), body: __("Skills appear in the member directory, enabling networking requests based on complementary expertise.") },
			],
		},
		"Contract Template": {
			title: __("Contract Templates — قوالب العقود"),
			icon: "📑",
			slides: [
				{ title: __("Reusable Templates"), body: __("Create contract templates with standard terms for memberships, space rental, and services.") },
				{ title: __("Template Variables"), body: __("Use Jinja variables for member name, dates, pricing, and space details — auto-filled at contract creation.") },
			],
		},
		"Contract Legal Document": {
			title: __("Legal Documents — المستندات القانونية للعقود"),
			icon: "⚖️",
			slides: [
				{ title: __("Attached Legals"), body: __("Link legal documents (NDAs, terms of service, waivers) to specific contracts.") },
				{ title: __("Compliance Tracking"), body: __("Track which legal documents each member has acknowledged and signed.") },
			],
		},
		"Legal Document": {
			title: __("Legal Documents — المستندات القانونية"),
			icon: "📜",
			slides: [
				{ title: __("Master Legal Library"), body: __("Maintain a library of legal documents — terms of service, NDAs, waivers, and policies.") },
				{ title: __("Version Control"), body: __("Track document versions to ensure members always agree to the latest terms.") },
			],
		},
		"Training Module": {
			title: __("Training Modules — وحدات التدريب"),
			icon: "📚",
			slides: [
				{ title: __("Module Structure"), body: __("Organize training content into modules — each module contains sessions, resources, and assessments.") },
				{ title: __("Prerequisites"), body: __("Set module prerequisites so members progress through a structured learning path.") },
			],
		},
		"Training Badge": {
			title: __("Training Badges — شارات التدريب"),
			icon: "🏅",
			slides: [
				{ title: __("Achievement Badges"), body: __("Award badges upon completing training modules or achieving milestones.") },
				{ title: __("Badge Display"), body: __("Badges appear on member profiles in the directory and community pages.") },
			],
		},
		"Design Configuration": {
			title: __("Design Config — إعدادات التصميم"),
			icon: "🎨",
			slides: [
				{ title: __("Portal Appearance"), body: __("Customize colors, logo, and layout for the member-facing portal.") },
				{ title: __("Brand Consistency"), body: __("Configure brand colors and assets that apply across all ARKSpace pages.") },
			],
		},
		"Documentation Entry": {
			title: __("Documentation — التوثيق"),
			icon: "📝",
			slides: [
				{ title: __("Knowledge Base"), body: __("Create internal documentation for space policies, procedures, and member guidelines.") },
				{ title: __("Rich Content"), body: __("Entries support Markdown, images, and code examples for technical documentation.") },
			],
		},
		"Payment Receipt": {
			title: __("Payment Receipts — إيصالات الدفع"),
			icon: "🧾",
			slides: [
				{ title: __("Receipt Generation"), body: __("Auto-generated receipts for every payment — linked to invoices and credit transactions.") },
				{ title: __("Print Formats"), body: __("Multiple print formats available: bilingual (AR/EN), Arabic-only, and English-only.") },
			],
		},
		"User Training Progress": {
			title: __("Training Progress — تقدم التدريب"),
			icon: "📈",
			slides: [
				{ title: __("Progress Tracking"), body: __("Track each member's progress through training modules and sessions.") },
				{ title: __("Completion Status"), body: __("View completion percentage, time spent, and badges earned per member.") },
			],
		},
		"Amenity": {
			title: __("Amenities — المرافق"),
			icon: "✨",
			slides: [
				{ title: __("Amenity Catalog"), body: __("Define all available amenities — WiFi, projector, printer, coffee, parking, lockers, etc.") },
				{ title: __("Link to Spaces"), body: __("Amenities are linked to spaces via Space Amenity child entries, enabling filter-by-amenity bookings.") },
			],
		},
		"Documentation Code Example": {
			title: __("Code Examples — أمثلة البرمجة"),
			icon: "💻",
			slides: [
				{ title: __("Code Snippets"), body: __("Attach code examples to documentation entries for API usage, integrations, and automation recipes.") },
			],
		},
		"Documentation Prerequisite": {
			title: __("Prerequisites — المتطلبات المسبقة"),
			icon: "🔗",
			slides: [
				{ title: __("Reading Order"), body: __("Define which documentation entries must be read before this one, creating a structured learning path.") },
			],
		},
		"Documentation Relation": {
			title: __("Related Docs — مستندات ذات صلة"),
			icon: "🔀",
			slides: [
				{ title: __("Cross-references"), body: __("Link related documentation entries to help readers discover connected topics and guides.") },
			],
		},
	};

	// ── Default help for unknown DocTypes ──
	const DEFAULT_HELP = {
		title: __("ARKSpace Help — مساعدة أرك سبيس"),
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
