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
