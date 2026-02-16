// Copyright (c) 2026, ARKSpace Team and contributors
// For license information, please see license.txt

frappe.ui.form.on("Member Contract", {
    refresh: function(frm) {
        // Populate from template button
        if (frm.doc.contract_template && frm.doc.docstatus === 0) {
            frm.add_custom_button(__("Populate from Template"), function() {
                frappe.confirm(
                    __("This will overwrite current contract terms. Continue?"),
                    function() {
                        frm.call("populate_from_template").then(() => {
                            frm.dirty();
                            frm.refresh_fields();
                            frappe.show_alert({
                                message: __("Terms populated from template"),
                                indicator: "green"
                            });
                        });
                    }
                );
            }, __("Actions"));
        }

        // Print buttons
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(__("Print Arabic Contract"), function() {
                frappe.set_route("print", "Member Contract", frm.doc.name, {
                    print_format: "Member Contract AR"
                });
            }, __("Print"));

            frm.add_custom_button(__("Print English Contract"), function() {
                frappe.set_route("print", "Member Contract", frm.doc.name, {
                    print_format: "Member Contract EN"
                });
            }, __("Print"));

            frm.add_custom_button(__("Print Bilingual"), function() {
                frappe.set_route("print", "Member Contract", frm.doc.name, {
                    print_format: "Member Contract Bilingual"
                });
            }, __("Print"));
        }

        // Status indicator colors
        if (frm.doc.status) {
            let color = {
                "Draft / مسودة": "orange",
                "Active / ساري": "green",
                "Expired / منتهي": "red",
                "Terminated / منهي": "darkgrey",
                "Cancelled / ملغي": "red"
            }[frm.doc.status] || "blue";
            frm.page.set_indicator(frm.doc.status, color);
        }
    },

    member: function(frm) {
        // Auto-fetch legal documents for this member
        if (frm.doc.member) {
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Legal Document",
                    filters: { member: frm.doc.member },
                    fields: ["name", "document_type", "document_number", "expiry_date", "status"],
                    limit_page_length: 20
                },
                callback: function(r) {
                    if (r.message && r.message.length) {
                        frm.clear_table("legal_documents");
                        r.message.forEach(function(doc) {
                            let row = frm.add_child("legal_documents");
                            row.legal_document = doc.name;
                            row.document_type = doc.document_type;
                            row.document_number = doc.document_number;
                            row.expiry_date = doc.expiry_date;
                            row.status = doc.status;
                        });
                        frm.refresh_field("legal_documents");
                        frappe.show_alert({
                            message: __("{0} legal document(s) found", [r.message.length]),
                            indicator: "blue"
                        });
                    }
                }
            });
        }
    },

    membership: function(frm) {
        // Auto-fill from membership
        if (frm.doc.membership) {
            frappe.db.get_doc("Membership", frm.doc.membership).then(doc => {
                frm.set_value("start_date", doc.start_date);
                frm.set_value("end_date", doc.end_date);
                frm.set_value("rate", doc.rate);
                frm.set_value("discount_percent", doc.discount_percent);
                frm.set_value("auto_renew", doc.auto_renew);
                if (doc.assigned_space) {
                    frm.set_value("space", doc.assigned_space);
                }
                if (doc.branch) {
                    frm.set_value("branch", doc.branch);
                }
            });
        }
    },

    rate: function(frm) {
        calculate_net(frm);
    },

    discount_percent: function(frm) {
        calculate_net(frm);
    }
});

function calculate_net(frm) {
    let rate = flt(frm.doc.rate);
    let discount = flt(frm.doc.discount_percent);
    frm.set_value("net_amount", rate * (1 - discount / 100));
}
