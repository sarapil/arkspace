// Copyright (c) 2026, ARKSpace Team and contributors
// Multi-Location / Branch Management — إدارة الفروع المتعددة

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
