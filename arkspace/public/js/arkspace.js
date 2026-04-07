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
