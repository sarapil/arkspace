# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

# Portal context for member directory page

import frappe


def get_context(context):
    context.no_cache = 1
    context.title = "Member Directory"

    if frappe.session.user == "Guest":
        frappe.throw("Please log in to view the directory", frappe.PermissionError)

    # Get active members with their info
    members = frappe.db.sql("""
        SELECT DISTINCT m.member, m.member_name, m.membership_plan, m.branch,
               u.full_name, u.user_image, u.bio
        FROM `tabMembership` m
        LEFT JOIN `tabUser` u ON m.member = u.name
        WHERE m.docstatus = 1 AND m.status = 'Active'
        ORDER BY u.full_name
        LIMIT 100
    """, as_dict=True)

    context.members = members
    context.branches = frappe.get_all("Branch", pluck="name")
    context.total_members = len(members)
