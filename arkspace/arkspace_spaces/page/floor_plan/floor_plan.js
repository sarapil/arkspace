frappe.pages["floor-plan"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Floor Plan — مخطط الطابق"),
		single_column: true,
	});

	page.set_indicator("Live", "green");

	// Filters
	page.branch_field = page.add_field({
		fieldtype: "Link",
		fieldname: "branch",
		label: __("Branch"),
		options: "Branch",
		change: () => floorPlan.refresh(),
	});

	page.floor_field = page.add_field({
		fieldtype: "Select",
		fieldname: "floor",
		label: __("Floor"),
		options: "",
		change: () => floorPlan.refresh(),
	});

	// Refresh button
	page.set_primary_action(__("Refresh"), () => floorPlan.refresh(), "refresh");

	const floorPlan = new FloorPlanView(page);
	floorPlan.refresh();

	// Auto-refresh every 30 seconds
	setInterval(() => floorPlan.refresh(), 30000);

	// Real-time updates
	frappe.realtime.on("space_status_changed", () => floorPlan.refresh());
};

class FloorPlanView {
	constructor(page) {
		this.page = page;
		this.$container = $('<div class="floor-plan-container"></div>').appendTo(
			this.page.body
		);
	}

	refresh() {
		const branch = this.page.branch_field?.get_value();
		const floor = this.page.floor_field?.get_value();

		frappe.call({
			method: "arkspace.arkspace_spaces.floor_plan.get_floor_plan_data",
			args: { branch, floor },
			callback: (r) => {
				if (r.message) {
					this.render(r.message);
					this.updateFloorOptions(r.message.available_floors);
				}
			},
		});
	}

	updateFloorOptions(floors) {
		const current = this.page.floor_field?.get_value();
		const opts = ["", ...(floors || [])];
		this.page.floor_field?.df &&
			(this.page.floor_field.df.options = opts.join("\n"));
		this.page.floor_field?.$input
			?.empty()
			.append(opts.map((f) => `<option value="${f}">${f || __("All Floors")}</option>`).join(""));
		if (current) this.page.floor_field?.set_value(current);
	}

	render(data) {
		const { floors, summary } = data;

		let html = `
			<div class="fp-summary">
				<div class="fp-stat">
					<div class="fp-stat-value">${summary.total}</div>
					<div class="fp-stat-label">${__("Total")}</div>
				</div>
				<div class="fp-stat fp-available">
					<div class="fp-stat-value">${summary.available}</div>
					<div class="fp-stat-label">${__("Available")}</div>
				</div>
				<div class="fp-stat fp-occupied">
					<div class="fp-stat-value">${summary.occupied}</div>
					<div class="fp-stat-label">${__("Occupied")}</div>
				</div>
				<div class="fp-stat fp-reserved">
					<div class="fp-stat-value">${summary.reserved}</div>
					<div class="fp-stat-label">${__("Reserved")}</div>
				</div>
				<div class="fp-stat fp-maintenance">
					<div class="fp-stat-value">${summary.maintenance}</div>
					<div class="fp-stat-label">${__("Maintenance")}</div>
				</div>
			</div>

			<div class="fp-legend">
				<span class="fp-legend-item"><span class="fp-dot available"></span> ${__("Available")}</span>
				<span class="fp-legend-item"><span class="fp-dot occupied"></span> ${__("Occupied")}</span>
				<span class="fp-legend-item"><span class="fp-dot reserved"></span> ${__("Reserved")}</span>
				<span class="fp-legend-item"><span class="fp-dot maintenance"></span> ${__("Maintenance")}</span>
			</div>
		`;

		for (const floor of floors) {
			html += `
				<div class="fp-floor">
					<div class="fp-floor-header">
						<h3>
							<i class="fa-solid fa-layer-group"></i>
							${floor.floor}
						</h3>
						<span class="fp-floor-stats">
							${floor.available} ${__("available")} / ${floor.total} ${__("total")}
						</span>
					</div>
					<div class="fp-grid">
			`;

			for (const space of floor.spaces) {
				const statusClass = space.status.toLowerCase().replace(" ", "-");
				const memberInfo = space.member_name
					? `<div class="fp-space-member">${space.member_name}</div>`
					: "";
				const capacityBadge =
					space.capacity > 1
						? `<span class="fp-capacity">${space.capacity}</span>`
						: "";

				html += `
					<div class="fp-space ${statusClass}"
						 data-space="${space.name}"
						 title="${space.space_name} — ${space.space_type} (${space.status})">
						<div class="fp-space-icon">
							<i class="${space.type_icon}"></i>
							${capacityBadge}
						</div>
						<div class="fp-space-name">${space.space_name}</div>
						<div class="fp-space-type">${space.space_type}</div>
						${memberInfo}
						<div class="fp-space-status">${__(space.status)}</div>
					</div>
				`;
			}

			html += `
					</div>
				</div>
			`;
		}

		if (!floors.length) {
			html += `
				<div class="fp-empty">
					<i class="fa-solid fa-map" style="font-size: 3rem; color: var(--ark-gold, #C4A962);"></i>
					<h3>${__("No spaces found")}</h3>
					<p>${__("Add Co-working Spaces to see them on the floor plan.")}</p>
				</div>
			`;
		}

		this.$container.html(html);

		// Bind click events
		this.$container.find(".fp-space").on("click", function () {
			const spaceName = $(this).data("space");
			frappe.set_route("Form", "Co-working Space", spaceName);
		});

		// Right-click for quick actions
		this.$container.find(".fp-space.available").on("contextmenu", function (e) {
			e.preventDefault();
			const spaceName = $(this).data("space");
			FloorPlanView.showQuickBook(spaceName);
		});
	}

	static showQuickBook(spaceName) {
		frappe.prompt(
			[
				{
					fieldtype: "Link",
					fieldname: "member",
					label: __("Member"),
					options: "Customer",
					reqd: 1,
				},
				{
					fieldtype: "Select",
					fieldname: "booking_type",
					label: __("Booking Type"),
					options: "Hourly\nDaily\nMonthly",
					default: "Hourly",
					reqd: 1,
				},
				{
					fieldtype: "Datetime",
					fieldname: "start_datetime",
					label: __("Start"),
					reqd: 1,
					default: frappe.datetime.now_datetime(),
				},
				{
					fieldtype: "Datetime",
					fieldname: "end_datetime",
					label: __("End"),
					reqd: 1,
				},
			],
			(values) => {
				frappe.call({
					method: "arkspace.arkspace_spaces.api.create_booking",
					args: {
						space: spaceName,
						member: values.member,
						booking_type: values.booking_type,
						start_datetime: values.start_datetime,
						end_datetime: values.end_datetime,
					},
					callback: (r) => {
						frappe.show_alert({
							message: __("Booking {0} created!", [r.message.booking]),
							indicator: "green",
						});
					},
				});
			},
			__("Quick Book — {0}", [spaceName]),
			__("Book")
		);
	}
}
