// Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
// Developer Website: https://arkan.it.com
// License: MIT
// For license information, please see license.txt

/**
 * ARK Scheduler
 * =============================================
 *
 * A resource-timeline Kanban board:
 *   • Tabs   = Space Types (Meeting Rooms, Hot Desks, …)
 *   • Cols   = Individual spaces of that type
 *   • Y-axis = 24-hour day in 1-hour rows
 *   • Cards  = Bookings placed on the grid
 *
 * Operations:
 *   • Drag card horizontally → move to another space
 *   • Drag card vertically   → change time
 *   • Resize bottom edge     → extend / shorten
 *   • Click empty slot       → quick book
 *   • Right-click card       → context menu (check-in, split, swap, cancel…)
 *   • Right-click empty      → block / quick-book
 */

frappe.pages["ark-scheduler"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("ARK Scheduler"),
		single_column: true,
	});

	const PAGE_CSS = "/assets/arkspace/arkspace_core/page/ark_scheduler/ark_scheduler.css";
	if (!document.querySelector(`link[href="${PAGE_CSS}"]`)) {
		const link = document.createElement("link");
		link.rel = "stylesheet";
		link.href = PAGE_CSS;
		document.head.appendChild(link);
	}

	new ArkScheduler(page);
};

class ArkScheduler {
	constructor(page) {
		this.page = page;
		this.$container = $(page.body);
		this.date = frappe.datetime.get_today();
		this.spaceTypes = [];
		this.activeType = null;
		this.data = null; // schedule data from API
		this.dragState = null;
		this.resizeState = null;
		this.selectionState = null; // for click-drag quick-book

		this.init();
	}

	async init() {
		this.$container.html(`<div class="ark-sched"></div>`);
		this.$root = this.$container.find(".ark-sched");

		this.buildToolbar();
		await this.loadSpaceTypes();
		if (this.spaceTypes.length) {
			this.activeType = this.spaceTypes[0].name;
			this.renderTabs();
			await this.loadSchedule();
		} else {
			this.renderEmpty(__("No space types defined"), __("Create Space Types first to use the scheduler."));
		}

		// Global event: close context menu on click elsewhere
		$(document).on("click.ark-sched", () => this.closeContextMenu());

		// Realtime
		frappe.realtime.on("booking_update", () => this.loadSchedule());

		// Auto-update current-time line every 60s
		this._timerInterval = setInterval(() => this.updateNowLine(), 60000);
	}

	destroy() {
		$(document).off("click.ark-sched");
		if (this._timerInterval) clearInterval(this._timerInterval);
	}

	// ═══════════════════════════════════════════
	//  TOOLBAR
	// ═══════════════════════════════════════════

	buildToolbar() {
		this.$toolbar = $(`
			<div class="ark-sched-toolbar">
				<span class="sched-title">📅 ${__("Resource Scheduler")}</span>
				<div class="sched-date-nav">
					<button class="btn-sched sched-prev">◀</button>
					<button class="btn-sched sched-today">${__("Today")}</button>
					<span class="sched-date-label"></span>
					<button class="btn-sched sched-next">▶</button>
				</div>
				<div class="sched-actions">
					<button class="btn-sched sched-bh-toggle" title="${__("Business Hours Only")}">🕐</button>
					<button class="btn-sched sched-refresh" title="${__("Refresh")}">🔄</button>
					<button class="btn-sched sched-find-free" title="${__("Find Free Space")}">🔍</button>
				</div>
			</div>
		`).appendTo(this.$root);

		this.$toolbar.find(".sched-prev").on("click", () => this.changeDate(-1));
		this.$toolbar.find(".sched-next").on("click", () => this.changeDate(1));
		this.$toolbar.find(".sched-today").on("click", () => {
			this.date = frappe.datetime.get_today();
			this.loadSchedule();
		});
		this.$toolbar.find(".sched-refresh").on("click", () => this.loadSchedule());
		this.$toolbar.find(".sched-bh-toggle").on("click", (e) => {
			$(e.currentTarget).toggleClass("active");
			this.loadSchedule();
		});
		this.$toolbar.find(".sched-find-free").on("click", () => this.showFindFreeDialog());

		this.updateDateLabel();
	}

	updateDateLabel() {
		const d = new Date(this.date + "T00:00:00");
		const opts = { weekday: "long", year: "numeric", month: "long", day: "numeric" };
		const locale = frappe.boot.lang === "ar" ? "ar-SA" : "en-US";
		this.$toolbar.find(".sched-date-label").text(d.toLocaleDateString(locale, opts));
	}

	changeDate(delta) {
		const d = new Date(this.date + "T00:00:00");
		d.setDate(d.getDate() + delta);
		this.date = d.toISOString().split("T")[0];
		this.updateDateLabel();
		this.loadSchedule();
	}

	// ═══════════════════════════════════════════
	//  TABS
	// ═══════════════════════════════════════════

	async loadSpaceTypes() {
		const r = await frappe.call({
			method: "arkspace.arkspace_core.schedule_api.get_space_types",
		});
		this.spaceTypes = r.message || [];
	}

	renderTabs() {
		if (this.$tabs) this.$tabs.remove();
		this.$tabs = $(`<div class="ark-sched-tabs"></div>`).appendTo(this.$root);

		for (const st of this.spaceTypes) {
			const isActive = st.name === this.activeType;
			const $tab = $(`
				<div class="ark-sched-tab ${isActive ? "active" : ""}" data-type="${st.name}">
					<span>${st.icon || "📍"}</span>
					<span>${st.type_name}</span>
					<span class="tab-badge">${st.space_count}</span>
				</div>
			`);
			$tab.on("click", () => {
				this.activeType = st.name;
				this.$tabs.find(".ark-sched-tab").removeClass("active");
				$tab.addClass("active");
				this.loadSchedule();
			});
			this.$tabs.append($tab);
		}
	}

	// ═══════════════════════════════════════════
	//  DATA LOADING
	// ═══════════════════════════════════════════

	async loadSchedule() {
		if (!this.activeType) return;

		this.updateDateLabel();

		const bhOnly = this.$toolbar.find(".sched-bh-toggle").hasClass("active") ? 1 : 0;

		frappe.dom.freeze(__("Loading schedule…"));

		try {
			const r = await frappe.call({
				method: "arkspace.arkspace_core.schedule_api.get_schedule_data",
				args: {
					space_type: this.activeType,
					date: this.date,
					business_hours_only: bhOnly,
				},
			});
			this.data = r.message;
			this.renderGrid();
		} catch (e) {
			frappe.msgprint({ title: __("Error"), message: e.message || __("Failed to load schedule"), indicator: "red" });
		} finally {
			frappe.dom.unfreeze();
		}
	}

	// ═══════════════════════════════════════════
	//  GRID RENDERING
	// ═══════════════════════════════════════════

	renderGrid() {
		if (this.$gridWrapper) this.$gridWrapper.remove();
		if (this.$statsBar) this.$statsBar.remove();

		const d = this.data;
		if (!d || !d.spaces.length) {
			this.renderEmpty(__("No spaces found"), __("No spaces of this type exist. Create some first."));
			return;
		}

		const spaces = d.spaces;
		const hours = d.hours;
		const hourStart = hours.start;
		const hourEnd = hours.end;
		const totalHours = hourEnd - hourStart;
		const colCount = spaces.length;

		// Grid wrapper
		this.$gridWrapper = $(`<div class="ark-sched-grid-wrapper"></div>`).appendTo(this.$root);

		const $grid = $(`<div class="ark-sched-grid"></div>`).appendTo(this.$gridWrapper);
		$grid.css({
			"grid-template-columns": `var(--sched-time-w) repeat(${colCount}, minmax(var(--sched-col-w), 1fr))`,
			"grid-template-rows": `var(--sched-header-h) repeat(${totalHours}, var(--sched-hour-h))`,
		});

		// Corner cell (top-left)
		$grid.append(`
			<div class="ark-sched-col-header" style="position:sticky;left:0;z-index:5;grid-row:1;grid-column:1">
				<span style="font-size:11px;color:var(--sched-muted)">${__("Time")}</span>
			</div>
		`);

		// Column headers (space names)
		spaces.forEach((sp, idx) => {
			const statusColor = this._statusColor(sp.status);
			$grid.append(`
				<div class="ark-sched-col-header" style="grid-row:1;grid-column:${idx + 2}"
					 data-space="${sp.name}" title="${sp.space_name} — ${sp.status}">
					<div class="col-name">
						<span class="col-status" style="background:${statusColor}"></span>
						${frappe.utils.escape_html(sp.space_name)}
					</div>
					<div class="col-meta">
						${sp.floor ? __("Floor") + " " + sp.floor : ""}
						${sp.capacity ? " · 👤 " + sp.capacity : ""}
					</div>
				</div>
			`);
		});

		// Time labels + grid cells
		for (let h = hourStart; h < hourEnd; h++) {
			const row = h - hourStart + 2; // +2 because row 1 is header

			// Time label
			const label = (h < 10 ? "0" : "") + h + ":00";
			$grid.append(`
				<div class="ark-sched-time-label" style="grid-row:${row};grid-column:1">${label}</div>
			`);

			// Cells per space
			spaces.forEach((sp, idx) => {
				const $cell = $(`
					<div class="ark-sched-cell"
						 style="grid-row:${row};grid-column:${idx + 2}"
						 data-space="${sp.name}" data-hour="${h}" data-col="${idx}">
					</div>
				`);

				// Click → quick book start
				$cell.on("mousedown", (e) => {
					if (e.button !== 0) return;
					if ($(e.target).closest(".ark-sched-card").length) return;
					this.startSelection(sp.name, idx, h, e);
				});

				// Right-click on empty → context
				$cell.on("contextmenu", (e) => {
					if ($(e.target).closest(".ark-sched-card").length) return;
					e.preventDefault();
					this.showEmptyContextMenu(e, sp.name, h);
				});

				$grid.append($cell);
			});
		}

		this.$grid = $grid;

		// Place booking cards
		const allCards = [...(d.bookings || []), ...(d.day_passes || [])];
		for (const card of allCards) {
			this.placeCard(card, spaces, hourStart, hourEnd);
		}

		// Now-line
		this.updateNowLine();

		// Stats bar
		this.renderStatsBar(d, allCards);

		// Scroll to current hour
		this.scrollToNow(hourStart);
	}

	placeCard(card, spaces, hourStart, hourEnd) {
		const spIdx = spaces.findIndex((s) => s.name === card.space);
		if (spIdx < 0) return;

		const startH = Math.max(card.start_hour, hourStart);
		const endH = Math.min(card.end_hour || startH + 1, hourEnd);
		if (endH <= startH) return;

		const hourH = 60; // matches --sched-hour-h
		const headerH = 56; // matches --sched-header-h
		const top = headerH + (startH - hourStart) * hourH;
		const height = Math.max((endH - startH) * hourH - 2, 20);

		const statusLabel = __(card.status);
		const timeLabel = this._fmtHour(card.start_hour) + " – " + this._fmtHour(card.end_hour);
		const typeIcon = card.type === "day_pass" ? "🎟️" : "";

		const colLeft = this._colLeft(spIdx, spaces.length);

		const $card = $(`
			<div class="ark-sched-card"
				 data-id="${card.id}" data-type="${card.type}" data-space="${card.space}"
				 data-start="${card.start_hour}" data-end="${card.end_hour}"
				 style="top:${top}px;height:${height}px;background:${card.color};${colLeft}">
				<div class="card-member">${typeIcon}${frappe.utils.escape_html(card.member_name || card.member || "")}</div>
				<div class="card-time">${timeLabel}</div>
				${height > 40 ? `<div class="card-status">${statusLabel}</div>` : ""}
				<div class="card-resize-handle"></div>
			</div>
		`);

		// Drag start
		$card.on("mousedown", (e) => {
			if ($(e.target).hasClass("card-resize-handle")) {
				this.startResize(card, $card, e);
			} else if (e.button === 0) {
				this.startDrag(card, $card, spaces, hourStart, e);
			}
		});

		// Right-click → card context menu
		$card.on("contextmenu", (e) => {
			e.preventDefault();
			e.stopPropagation();
			this.showCardContextMenu(e, card);
		});

		// Double-click → open doctype
		$card.on("dblclick", () => {
			frappe.set_route("Form", card.doctype, card.id);
		});

		// Tooltip
		$card.attr("title",
			`${card.member_name}\n${timeLabel}\n${statusLabel}\n${card.id}`
		);

		this.$grid.append($card);
	}

	// ═══════════════════════════════════════════
	//  DRAG & DROP
	// ═══════════════════════════════════════════

	startDrag(card, $card, spaces, hourStart, e) {
		if (card.type === "day_pass") return; // can't drag day passes (yet)
		if (["Checked Out", "Cancelled", "No Show"].includes(card.status)) return;

		e.preventDefault();
		const startX = e.clientX;
		const startY = e.clientY;
		let moved = false;

		const origTop = parseFloat($card.css("top"));
		const origCard = { ...card };

		$card.addClass("dragging");

		const onMove = (ev) => {
			const dx = ev.clientX - startX;
			const dy = ev.clientY - startY;

			if (!moved && Math.abs(dx) + Math.abs(dy) < 8) return;
			moved = true;

			// Vertical: snap to half-hour (30px increments)
			const hourH = 60;
			const snapY = Math.round(dy / (hourH / 2)) * (hourH / 2);
			$card.css("top", origTop + snapY + "px");

			// Horizontal: highlight target column
			this.highlightDropTarget(ev, spaces);
		};

		const onUp = (ev) => {
			$(document).off("mousemove.sched-drag mouseup.sched-drag");
			$card.removeClass("dragging");
			this.clearHighlights();

			if (!moved) return;

			// Determine target space + time
			const target = this.getDropTarget(ev, spaces, hourStart);
			if (!target) return;

			const newSpace = target.space;
			const hourDelta = target.hourDelta;
			const newStartHour = origCard.start_hour + hourDelta;
			const newEndHour = origCard.end_hour + hourDelta;

			if (newSpace === origCard.space && hourDelta === 0) return;

			// Build new times
			const newStart = this._hourToDatetime(this.date, newStartHour);
			const newEnd = this._hourToDatetime(this.date, newEndHour);

			this.moveBooking(card.id, newSpace, newStart, newEnd);
		};

		$(document).on("mousemove.sched-drag", onMove);
		$(document).on("mouseup.sched-drag", onUp);
	}

	highlightDropTarget(ev, spaces) {
		this.clearHighlights();
		const $cell = $(document.elementFromPoint(ev.clientX, ev.clientY)).closest(".ark-sched-cell");
		if ($cell.length) {
			$cell.addClass("sched-drop-target");
		}
	}

	clearHighlights() {
		this.$grid.find(".sched-drop-target, .sched-drop-invalid, .sched-highlight").removeClass("sched-drop-target sched-drop-invalid sched-highlight");
	}

	getDropTarget(ev, spaces, hourStart) {
		const $cell = $(document.elementFromPoint(ev.clientX, ev.clientY)).closest(".ark-sched-cell");
		if (!$cell.length) return null;

		const space = $cell.data("space");
		const hour = parseFloat($cell.data("hour"));

		// Calculate hour delta (snap to 0.5)
		const origCard = this.dragState;
		const hourH = 60;
		const rect = this.$gridWrapper[0].getBoundingClientRect();
		const scrollTop = this.$gridWrapper[0].scrollTop;
		const mouseY = ev.clientY - rect.top + scrollTop;
		const headerH = 56;
		const rawHour = hourStart + (mouseY - headerH) / hourH;
		const snappedHour = Math.round(rawHour * 2) / 2;

		return { space, hour, hourDelta: hour - (this.data.hours.start) };
	}

	// ═══════════════════════════════════════════
	//  RESIZE
	// ═══════════════════════════════════════════

	startResize(card, $card, e) {
		if (card.type === "day_pass") return;
		if (["Checked Out", "Cancelled", "No Show"].includes(card.status)) return;

		e.preventDefault();
		e.stopPropagation();

		const startY = e.clientY;
		const origHeight = parseFloat($card.css("height"));
		const hourH = 60;

		const onMove = (ev) => {
			const dy = ev.clientY - startY;
			const newHeight = Math.max(hourH / 2, origHeight + dy);
			// Snap to half-hour
			const snapped = Math.round(newHeight / (hourH / 2)) * (hourH / 2);
			$card.css("height", snapped + "px");
		};

		const onUp = () => {
			$(document).off("mousemove.sched-resize mouseup.sched-resize");

			const newHeight = parseFloat($card.css("height"));
			const hoursDelta = (newHeight - origHeight) / hourH;
			const newEndHour = card.end_hour + hoursDelta;

			if (Math.abs(hoursDelta) < 0.1) return;

			const newEnd = this._hourToDatetime(this.date, newEndHour);
			this.extendBooking(card.id, newEnd);
		};

		$(document).on("mousemove.sched-resize", onMove);
		$(document).on("mouseup.sched-resize", onUp);
	}

	// ═══════════════════════════════════════════
	//  CLICK-DRAG SELECTION (Quick Book)
	// ═══════════════════════════════════════════

	startSelection(space, colIdx, startHour, e) {
		e.preventDefault();
		this.selectionState = { space, colIdx, startHour, endHour: startHour + 1 };

		const $overlay = $(`<div class="ark-sched-quickbook">+ ${__("New Booking")}</div>`);
		this._updateOverlay($overlay, startHour, startHour + 1);

		const colCell = this.$grid.find(`.ark-sched-cell[data-space="${space}"][data-hour="${startHour}"]`);
		if (colCell.length) {
			// Place overlay in grid at same column position
			this.$grid.append($overlay);
			this._positionOverlay($overlay, startHour, startHour + 1);
		}

		const hourH = 60;

		const onMove = (ev) => {
			const rect = this.$gridWrapper[0].getBoundingClientRect();
			const scrollTop = this.$gridWrapper[0].scrollTop;
			const mouseY = ev.clientY - rect.top + scrollTop;
			const headerH = 56;
			const rawHour = this.data.hours.start + (mouseY - headerH) / hourH;
			const endH = Math.max(startHour + 0.5, Math.round(rawHour * 2) / 2);

			this.selectionState.endHour = endH;
			this._positionOverlay($overlay, startHour, endH);
		};

		const onUp = () => {
			$(document).off("mousemove.sched-sel mouseup.sched-sel");
			$overlay.remove();

			const { endHour } = this.selectionState;
			if (endHour - startHour >= 0.5) {
				this.showQuickBookDialog(space, startHour, endHour);
			}
			this.selectionState = null;
		};

		$(document).on("mousemove.sched-sel", onMove);
		$(document).on("mouseup.sched-sel", onUp);
	}

	_positionOverlay($el, startH, endH) {
		const hourH = 60;
		const headerH = 56;
		const hs = this.data.hours.start;
		const top = headerH + (startH - hs) * hourH;
		const height = (endH - startH) * hourH;
		$el.css({ top: top + "px", height: height + "px" });
	}

	_updateOverlay($el, startH, endH) {
		$el.text(`+ ${this._fmtHour(startH)} – ${this._fmtHour(endH)}`);
	}

	// ═══════════════════════════════════════════
	//  CONTEXT MENUS
	// ═══════════════════════════════════════════

	showCardContextMenu(e, card) {
		this.closeContextMenu();

		const items = [];

		if (card.status === "Confirmed") {
			items.push({ icon: "✅", label: __("Check In"), action: () => this.checkinBooking(card.id) });
		}
		if (card.status === "Checked In") {
			items.push({ icon: "🚪", label: __("Check Out"), action: () => this.checkoutBooking(card.id) });
		}

		items.push({ icon: "✏️", label: __("Open Booking"), action: () => frappe.set_route("Form", card.doctype, card.id) });

		if (!["Checked Out", "Cancelled", "No Show"].includes(card.status) && card.type !== "day_pass") {
			items.push({ sep: true });
			items.push({ icon: "↔️", label: __("Move to Another Space"), action: () => this.showMoveDialog(card) });
			items.push({ icon: "✂️", label: __("Split Booking"), action: () => this.showSplitDialog(card) });
			items.push({ icon: "🔄", label: __("Swap with Another"), action: () => this.showSwapDialog(card) });
			items.push({ icon: "⏱️", label: __("Extend / Shorten"), action: () => this.showExtendDialog(card) });
			items.push({ sep: true });
			items.push({ icon: "❌", label: __("Cancel Booking"), action: () => this.cancelBooking(card), cls: "ctx-danger" });
		}

		this._renderContextMenu(e, items);
	}

	showEmptyContextMenu(e, space, hour) {
		this.closeContextMenu();

		const items = [
			{ icon: "➕", label: __("Quick Book"), action: () => this.showQuickBookDialog(space, hour, hour + 1) },
			{ icon: "🚫", label: __("Block Slot"), action: () => this.showBlockDialog(space, hour) },
			{ sep: true },
			{ icon: "🔍", label: __("Find Free Spaces"), action: () => this.showFindFreeDialog(hour) },
		];

		this._renderContextMenu(e, items);
	}

	_renderContextMenu(e, items) {
		const $menu = $(`<div class="ark-sched-ctx"></div>`);

		for (const item of items) {
			if (item.sep) {
				$menu.append(`<div class="ctx-sep"></div>`);
			} else {
				const $item = $(`
					<div class="ctx-item ${item.cls || ""}">
						<span>${item.icon}</span>
						<span>${item.label}</span>
					</div>
				`);
				$item.on("click", (ev) => {
					ev.stopPropagation();
					this.closeContextMenu();
					item.action();
				});
				$menu.append($item);
			}
		}

		$menu.css({ left: e.clientX + "px", top: e.clientY + "px" });
		$("body").append($menu);

		// Adjust if off-screen
		const rect = $menu[0].getBoundingClientRect();
		if (rect.right > window.innerWidth) $menu.css("left", (e.clientX - rect.width) + "px");
		if (rect.bottom > window.innerHeight) $menu.css("top", (e.clientY - rect.height) + "px");
	}

	closeContextMenu() {
		$(".ark-sched-ctx").remove();
	}

	// ═══════════════════════════════════════════
	//  API ACTIONS
	// ═══════════════════════════════════════════

	async moveBooking(bookingId, newSpace, newStart, newEnd) {
		try {
			await frappe.call({
				method: "arkspace.arkspace_core.schedule_api.move_booking",
				args: { booking: bookingId, new_space: newSpace, new_start_time: newStart, new_end_time: newEnd },
				freeze: true,
				freeze_message: __("Moving booking…"),
			});
			frappe.show_alert({ message: __("Booking moved successfully"), indicator: "green" });
			this.loadSchedule();
		} catch (e) {
			frappe.show_alert({ message: e.message || __("Move failed"), indicator: "red" });
			this.loadSchedule();
		}
	}

	async extendBooking(bookingId, newEnd) {
		try {
			await frappe.call({
				method: "arkspace.arkspace_core.schedule_api.extend_booking",
				args: { booking: bookingId, new_end_time: newEnd },
				freeze: true,
				freeze_message: __("Updating booking…"),
			});
			frappe.show_alert({ message: __("Booking updated"), indicator: "green" });
			this.loadSchedule();
		} catch (e) {
			frappe.show_alert({ message: e.message || __("Update failed"), indicator: "red" });
			this.loadSchedule();
		}
	}

	async checkinBooking(bookingId) {
		try {
			await frappe.call({
				method: "arkspace.arkspace_core.schedule_api.checkin_booking",
				args: { booking: bookingId },
			});
			frappe.show_alert({ message: __("Checked in!"), indicator: "green" });
			this.loadSchedule();
		} catch (e) {
			frappe.show_alert({ message: e.message || __("Check-in failed"), indicator: "red" });
		}
	}

	async checkoutBooking(bookingId) {
		try {
			await frappe.call({
				method: "arkspace.arkspace_core.schedule_api.checkout_booking",
				args: { booking: bookingId },
			});
			frappe.show_alert({ message: __("Checked out!"), indicator: "green" });
			this.loadSchedule();
		} catch (e) {
			frappe.show_alert({ message: e.message || __("Check-out failed"), indicator: "red" });
		}
	}

	async cancelBooking(card) {
		frappe.confirm(
			__("Cancel booking {0}?", [card.id]),
			async () => {
				try {
					await frappe.call({
						method: "frappe.client.cancel",
						args: { doctype: "Space Booking", name: card.id },
					});
					frappe.show_alert({ message: __("Booking cancelled"), indicator: "orange" });
					this.loadSchedule();
				} catch (e) {
					frappe.show_alert({ message: e.message || __("Cancellation failed"), indicator: "red" });
				}
			}
		);
	}

	// ═══════════════════════════════════════════
	//  DIALOGS
	// ═══════════════════════════════════════════

	showQuickBookDialog(space, startHour, endHour) {
		const startTime = this._hourToDatetime(this.date, startHour);
		const endTime = this._hourToDatetime(this.date, endHour);

		const d = new frappe.ui.Dialog({
			title: __("Quick Book"),
			fields: [
				{ fieldtype: "Link", fieldname: "member", label: __("Member / Customer"), options: "Customer", reqd: 1 },
				{ fieldtype: "Column Break" },
				{ fieldtype: "Select", fieldname: "booking_type", label: __("Booking Type"), options: "Hourly\nDaily\nMonthly", default: "Hourly" },
				{ fieldtype: "Section Break" },
				{ fieldtype: "Datetime", fieldname: "start_time", label: __("Start"), default: startTime, reqd: 1 },
				{ fieldtype: "Column Break" },
				{ fieldtype: "Datetime", fieldname: "end_time", label: __("End"), default: endTime, reqd: 1 },
			],
			primary_action_label: __("Book"),
			primary_action: async (vals) => {
				try {
					await frappe.call({
						method: "arkspace.arkspace_core.schedule_api.quick_book",
						args: {
							space: space,
							start_time: vals.start_time,
							end_time: vals.end_time,
							member: vals.member,
							booking_type: vals.booking_type,
						},
						freeze: true,
					});
					d.hide();
					frappe.show_alert({ message: __("Booking created!"), indicator: "green" });
					this.loadSchedule();
				} catch (e) {
					frappe.show_alert({ message: e.message || __("Failed"), indicator: "red" });
				}
			},
		});
		d.show();
	}

	showMoveDialog(card) {
		const d = new frappe.ui.Dialog({
			title: __("Move Booking"),
			fields: [
				{
					fieldtype: "HTML",
					fieldname: "info_html",
					options: `<div style="padding:8px 0;color:var(--text-muted);font-size:13px">
						${__("Current space")}: <strong>${card.space_name || card.space}</strong><br>
						${__("Time")}: ${this._fmtHour(card.start_hour)} – ${this._fmtHour(card.end_hour)}
					</div>`,
				},
				{ fieldtype: "Link", fieldname: "new_space", label: __("New Space"), options: "Co-working Space", reqd: 1,
					get_query: () => ({
						filters: { space_type: this.activeType, status: ["!=", "Maintenance"] }
					})
				},
				{ fieldtype: "Section Break", label: __("Adjust Time (optional)") },
				{ fieldtype: "Datetime", fieldname: "new_start", label: __("New Start"), default: card.start_time },
				{ fieldtype: "Column Break" },
				{ fieldtype: "Datetime", fieldname: "new_end", label: __("New End"), default: card.end_time },
			],
			primary_action_label: __("Move"),
			primary_action: async (vals) => {
				await this.moveBooking(card.id, vals.new_space, vals.new_start, vals.new_end);
				d.hide();
			},
		});
		d.show();
	}

	showSplitDialog(card) {
		const midHour = (card.start_hour + card.end_hour) / 2;
		const splitDefault = this._hourToDatetime(this.date, Math.round(midHour * 2) / 2);

		const d = new frappe.ui.Dialog({
			title: __("Split Booking"),
			fields: [
				{
					fieldtype: "HTML",
					fieldname: "info_html",
					options: `<div style="padding:8px 0;color:var(--text-muted);font-size:13px">
						<strong>${card.member_name}</strong> · ${this._fmtHour(card.start_hour)} – ${this._fmtHour(card.end_hour)}<br>
						${__("Part 1 stays in")} <strong>${card.space_name || card.space}</strong>.
						${__("Part 2 moves to the space you choose.")}
					</div>`,
				},
				{ fieldtype: "Datetime", fieldname: "split_time", label: __("Split At"), default: splitDefault, reqd: 1 },
				{ fieldtype: "Link", fieldname: "second_space", label: __("Second Space"), options: "Co-working Space", reqd: 1,
					get_query: () => ({
						filters: { space_type: this.activeType, status: ["!=", "Maintenance"] }
					})
				},
			],
			primary_action_label: __("Split"),
			primary_action: async (vals) => {
				try {
					await frappe.call({
						method: "arkspace.arkspace_core.schedule_api.split_booking",
						args: { booking: card.id, split_time: vals.split_time, second_space: vals.second_space },
						freeze: true,
					});
					d.hide();
					frappe.show_alert({ message: __("Booking split successfully"), indicator: "green" });
					this.loadSchedule();
				} catch (e) {
					frappe.show_alert({ message: e.message || __("Split failed"), indicator: "red" });
				}
			},
		});
		d.show();
	}

	showSwapDialog(card) {
		const d = new frappe.ui.Dialog({
			title: __("Swap Bookings"),
			fields: [
				{
					fieldtype: "HTML",
					fieldname: "info_html",
					options: `<div style="padding:8px 0;color:var(--text-muted);font-size:13px">
						${__("Swap")} <strong>${card.member_name}</strong> (${card.space_name || card.space})
						${__("with another booking.")}
					</div>`,
				},
				{ fieldtype: "Link", fieldname: "other_booking", label: __("Other Booking"), options: "Space Booking", reqd: 1,
					get_query: () => ({
						filters: {
							docstatus: 1,
							status: ["not in", ["Cancelled", "No Show", "Checked Out"]],
							name: ["!=", card.id],
						}
					})
				},
			],
			primary_action_label: __("Swap"),
			primary_action: async (vals) => {
				try {
					await frappe.call({
						method: "arkspace.arkspace_core.schedule_api.swap_bookings",
						args: { booking_a: card.id, booking_b: vals.other_booking },
						freeze: true,
					});
					d.hide();
					frappe.show_alert({ message: __("Bookings swapped"), indicator: "green" });
					this.loadSchedule();
				} catch (e) {
					frappe.show_alert({ message: e.message || __("Swap failed"), indicator: "red" });
				}
			},
		});
		d.show();
	}

	showExtendDialog(card) {
		const d = new frappe.ui.Dialog({
			title: __("Extend / Shorten"),
			fields: [
				{
					fieldtype: "HTML",
					fieldname: "info_html",
					options: `<div style="padding:8px 0;color:var(--text-muted);font-size:13px">
						<strong>${card.member_name}</strong><br>
						${__("Current")}: ${this._fmtHour(card.start_hour)} – ${this._fmtHour(card.end_hour)}
					</div>`,
				},
				{ fieldtype: "Datetime", fieldname: "new_end", label: __("New End Time"), default: card.end_time, reqd: 1 },
			],
			primary_action_label: __("Update"),
			primary_action: async (vals) => {
				await this.extendBooking(card.id, vals.new_end);
				d.hide();
			},
		});
		d.show();
	}

	showBlockDialog(space, hour) {
		const startTime = this._hourToDatetime(this.date, hour);
		const endTime = this._hourToDatetime(this.date, hour + 1);

		const d = new frappe.ui.Dialog({
			title: __("Block Slot"),
			fields: [
				{ fieldtype: "Select", fieldname: "reason", label: __("Reason"), options: "Maintenance\nCleaning\nReserved\nOther", default: "Maintenance" },
				{ fieldtype: "Section Break" },
				{ fieldtype: "Datetime", fieldname: "start_time", label: __("From"), default: startTime, reqd: 1 },
				{ fieldtype: "Column Break" },
				{ fieldtype: "Datetime", fieldname: "end_time", label: __("To"), default: endTime, reqd: 1 },
			],
			primary_action_label: __("Block"),
			primary_action: async (vals) => {
				try {
					await frappe.call({
						method: "arkspace.arkspace_core.schedule_api.block_slot",
						args: { space, start_time: vals.start_time, end_time: vals.end_time, reason: vals.reason },
						freeze: true,
					});
					d.hide();
					frappe.show_alert({ message: __("Slot blocked"), indicator: "orange" });
					this.loadSchedule();
				} catch (e) {
					frappe.show_alert({ message: e.message || __("Failed"), indicator: "red" });
				}
			},
		});
		d.show();
	}

	showFindFreeDialog(hour) {
		const h = hour || new Date().getHours();
		const startTime = this._hourToDatetime(this.date, h);
		const endTime = this._hourToDatetime(this.date, h + 1);

		const d = new frappe.ui.Dialog({
			title: __("Find Free Spaces"),
			fields: [
				{ fieldtype: "Link", fieldname: "space_type", label: __("Space Type"), options: "Space Type",
					default: this.activeType, reqd: 1 },
				{ fieldtype: "Section Break" },
				{ fieldtype: "Datetime", fieldname: "start_time", label: __("From"), default: startTime, reqd: 1 },
				{ fieldtype: "Column Break" },
				{ fieldtype: "Datetime", fieldname: "end_time", label: __("To"), default: endTime, reqd: 1 },
				{ fieldtype: "Section Break" },
				{ fieldtype: "HTML", fieldname: "results_html" },
			],
			primary_action_label: __("Search"),
			primary_action: async (vals) => {
				const r = await frappe.call({
					method: "arkspace.arkspace_core.schedule_api.get_available_spaces",
					args: { space_type: vals.space_type, start_time: vals.start_time, end_time: vals.end_time },
				});

				const spaces = r.message || [];
				let html = "";
				if (!spaces.length) {
					html = `<div style="padding:16px;text-align:center;color:var(--text-muted)">
						😔 ${__("No free spaces found for this time slot.")}
					</div>`;
				} else {
					html = `<div style="padding:8px 0">
						<strong>${spaces.length} ${__("free spaces found")}:</strong>
						<div style="display:grid;gap:8px;margin-top:8px">
					`;
					for (const sp of spaces) {
						html += `<div style="padding:8px 12px;background:rgba(16,185,129,0.08);border-radius:6px;
							border:1px solid rgba(16,185,129,0.2);display:flex;align-items:center;justify-content:space-between">
							<div>
								<strong>${frappe.utils.escape_html(sp.space_name)}</strong>
								<span style="color:var(--text-muted);font-size:11px;margin-left:8px">
									${sp.floor ? __("Floor") + " " + sp.floor : ""}  · 👤 ${sp.capacity}
								</span>
							</div>
							<button class="btn btn-xs btn-primary sched-book-free"
								data-space="${sp.name}" style="background:var(--as-navy,#1B365D)">
								${__("Book")}
							</button>
						</div>`;
					}
					html += `</div></div>`;
				}

				d.fields_dict.results_html.$wrapper.html(html);

				// Book buttons
				d.$wrapper.find(".sched-book-free").on("click", (ev) => {
					const sp = $(ev.currentTarget).data("space");
					d.hide();
					this.showQuickBookDialog(sp, h, h + 1);
				});
			},
		});
		d.show();
	}

	// ═══════════════════════════════════════════
	//  NOW LINE
	// ═══════════════════════════════════════════

	updateNowLine() {
		if (!this.data || !this.$grid) return;

		this.$grid.find(".ark-sched-now-line").remove();

		const today = frappe.datetime.get_today();
		if (this.date !== today) return;

		const now = new Date();
		const hourNow = now.getHours() + now.getMinutes() / 60;
		const hs = this.data.hours.start;
		const he = this.data.hours.end;

		if (hourNow < hs || hourNow > he) return;

		const hourH = 60;
		const headerH = 56;
		const top = headerH + (hourNow - hs) * hourH;

		this.$grid.append(`<div class="ark-sched-now-line" style="top:${top}px"></div>`);
	}

	scrollToNow(hourStart) {
		const now = new Date();
		const hourNow = now.getHours();
		const targetHour = Math.max(hourNow - 2, hourStart);
		const hourH = 60;
		const scrollTo = (targetHour - hourStart) * hourH;
		this.$gridWrapper[0].scrollTop = scrollTo;
	}

	// ═══════════════════════════════════════════
	//  STATS BAR
	// ═══════════════════════════════════════════

	renderStatsBar(data, allCards) {
		const spaces = data.spaces;
		const bookings = allCards.filter((c) => c.type === "booking");
		const dayPasses = allCards.filter((c) => c.type === "day_pass");
		const checkedIn = bookings.filter((c) => c.status === "Checked In").length;
		const confirmed = bookings.filter((c) => c.status === "Confirmed").length;
		const pending = bookings.filter((c) => c.status === "Pending").length;
		const available = spaces.filter((s) => s.status === "Available").length;
		const occupied = spaces.filter((s) => s.status === "Occupied").length;
		const maintenance = spaces.filter((s) => s.status === "Maintenance").length;

		this.$statsBar = $(`
			<div class="ark-sched-stats">
				<div class="stat-item"><span class="stat-dot" style="background:#10b981"></span> ${available} ${__("Available")}</div>
				<div class="stat-item"><span class="stat-dot" style="background:#f59e0b"></span> ${occupied} ${__("Occupied")}</div>
				<div class="stat-item"><span class="stat-dot" style="background:#ef4444"></span> ${maintenance} ${__("Maintenance")}</div>
				<span style="color:var(--border-color)">|</span>
				<div class="stat-item">📅 ${bookings.length} ${__("Bookings")}</div>
				<div class="stat-item">✅ ${checkedIn} ${__("Checked In")}</div>
				<div class="stat-item">📋 ${confirmed} ${__("Confirmed")}</div>
				<div class="stat-item">⏳ ${pending} ${__("Pending")}</div>
				${dayPasses.length ? `<div class="stat-item">🎟️ ${dayPasses.length} ${__("Day Passes")}</div>` : ""}
			</div>
		`).appendTo(this.$root);
	}

	// ═══════════════════════════════════════════
	//  EMPTY STATE
	// ═══════════════════════════════════════════

	renderEmpty(title, subtitle) {
		if (this.$gridWrapper) this.$gridWrapper.remove();
		if (this.$statsBar) this.$statsBar.remove();
		if (this.$emptyState) this.$emptyState.remove();

		this.$emptyState = $(`
			<div class="ark-sched-empty">
				<div class="empty-icon">📅</div>
				<div class="empty-title">${title}</div>
				<div>${subtitle}</div>
			</div>
		`).appendTo(this.$root);
	}

	// ═══════════════════════════════════════════
	//  UTILITIES
	// ═══════════════════════════════════════════

	_statusColor(status) {
		const map = {
			"Available": "#10b981", "Occupied": "#f59e0b",
			"Maintenance": "#ef4444", "Reserved": "#8b5cf6",
		};
		return map[status] || "#6b7280";
	}

	_fmtHour(h) {
		const hours = Math.floor(h);
		const mins = Math.round((h - hours) * 60);
		return (hours < 10 ? "0" : "") + hours + ":" + (mins < 10 ? "0" : "") + mins;
	}

	_hourToDatetime(date, hour) {
		const h = Math.floor(Math.max(0, Math.min(23, hour)));
		const m = Math.round((hour - h) * 60);
		return date + " " + (h < 10 ? "0" : "") + h + ":" + (m < 10 ? "0" : "") + m + ":00";
	}

	_colLeft(colIdx, totalCols) {
		// CSS grid handles positioning, but for absolute-positioned cards we compute left
		const timeW = 60; // --sched-time-w
		const colW = 180; // --sched-col-w
		const left = timeW + colIdx * colW + 4;
		const width = colW - 8;
		return `left:${left}px;width:${width}px;`;
	}
}
