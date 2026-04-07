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
