# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

"""ARKSpace Visitor Management API

Provides endpoints for visitor pre-registration, check-in/out,
badge generation, and visitor analytics.
"""

import hashlib

import frappe
from frappe import _
from frappe.utils import now_datetime, nowdate

@frappe.whitelist()
def preregister_visitor(
	visitor_name, purpose="Meeting", host=None,
	visitor_email=None, visitor_phone=None, visitor_company=None,
	expected_arrival=None, expected_departure=None,
	visiting_space=None, visiting_branch=None, notes=None,
):
    frappe.only_for(["AS User", "AS Manager", "System Manager"])
def preregister_visitor(
	visitor_name, purpose="Meeting", host=None,
	visitor_email=None, visitor_phone=None, visitor_company=None,
	expected_arrival=None, expected_departure=None,
	visiting_space=None, visiting_branch=None, notes=None,
):
	"""Pre-register an expected visitor.

	Args:
		visitor_name: Visitor full name
		purpose: Meeting/Interview/Delivery/Maintenance/Tour/Event/Other
		host: Customer name of the member hosting
		And other optional details

	Returns:
		dict with visitor log details
	"""
	frappe.has_permission("AS Visitor Log", "create", throw=True)
	frappe.only_for(["System Manager", "ARK Admin", "ARK User"])
	visitor = frappe.get_doc({
		"doctype": "Visitor Log",
		"visitor_name": visitor_name,
		"visitor_email": visitor_email,
		"visitor_phone": visitor_phone,
		"visitor_company": visitor_company,
		"purpose": purpose,
		"host": host,
		"visiting_space": visiting_space,
		"visiting_branch": visiting_branch,
		"expected_arrival": expected_arrival,
		"expected_departure": expected_departure,
		"notes": notes,
		"preregistered": 1,
		"preregistered_by": frappe.session.user,
		"status": "Expected",
		"approval_status": "Approved",
		"approved_by": frappe.session.user,
	})
	visitor.insert()

	# Generate QR token for visitor pass
	_generate_visitor_token(visitor)

	return {
		"visitor": visitor.name,
		"visitor_name": visitor.visitor_name,
		"status": visitor.status,
		"expected_arrival": str(visitor.expected_arrival) if visitor.expected_arrival else None,
		"qr_token": visitor.qr_token,
	}

@frappe.whitelist()
def walk_in_visitor(
	visitor_name, purpose="Meeting", host=None,
	visitor_email=None, visitor_phone=None, visitor_company=None,
	id_type=None, id_number=None, visiting_space=None,
):
	"""Register a walk-in visitor and immediately check in.

	For front desk use when a visitor arrives without pre-registration.
	"""
	frappe.only_for(["System Manager", "ARK Admin", "ARK User"])
	visitor = frappe.get_doc({
		"doctype": "Visitor Log",
		"visitor_name": visitor_name,
		"visitor_email": visitor_email,
		"visitor_phone": visitor_phone,
		"visitor_company": visitor_company,
		"purpose": purpose,
		"host": host,
		"id_type": id_type,
		"id_number": id_number,
		"visiting_space": visiting_space,
		"status": "Expected",
		"approval_status": "Approved",
		"approved_by": frappe.session.user,
	})
	visitor.insert()

	# Immediately check in
	visitor.check_in()

	# Generate badge
	badge_no = _assign_badge(visitor.name)

	return {
		"visitor": visitor.name,
		"visitor_name": visitor.visitor_name,
		"status": "Checked In",
		"checked_in_at": str(visitor.checked_in_at),
		"badge_number": badge_no,
	}

@frappe.whitelist()
def visitor_check_in(visitor_name):
	"""Check in a pre-registered visitor."""
	frappe.only_for(["System Manager", "ARK Admin", "ARK User"])
	visitor = frappe.get_doc("Visitor Log", visitor_name)
	visitor.check_in()

	badge_no = _assign_badge(visitor_name)

	return {
		"visitor": visitor.name,
		"status": "Checked In",
		"checked_in_at": str(now_datetime()),
		"badge_number": badge_no,
	}

@frappe.whitelist()
def visitor_check_out(visitor_name):
	"""Check out a visitor."""
	frappe.only_for(["System Manager", "ARK Admin", "ARK User"])
	visitor = frappe.get_doc("Visitor Log", visitor_name)
	visitor.check_out()

	# Release badge
	if visitor.badge_number:
		visitor.db_set("badge_number", None)

	return {
		"visitor": visitor.name,
		"status": "Checked Out",
		"checked_out_at": str(now_datetime()),
	}

@frappe.whitelist()
def get_todays_visitors(status=None, branch=None):
	"""Get all visitors expected or checked-in today."""
	frappe.only_for(["System Manager", "ARK Admin", "ARK User"])
	today = nowdate()

	filters = {
		"creation": [">=", f"{today} 00:00:00"],
	}
	if status:
		filters["status"] = status
	if branch:
		filters["visiting_branch"] = branch

	return frappe.get_all(
		"Visitor Log",
		filters=filters,
		fields=[
			"name", "visitor_name", "visitor_company", "visitor_phone",
			"purpose", "host", "host_name", "visiting_space",
			"status", "checked_in_at", "checked_out_at",
			"badge_number", "expected_arrival", "preregistered",
		],
		order_by="creation desc",
	)

@frappe.whitelist()
def get_active_visitors():
	"""Get currently checked-in visitors."""
	frappe.only_for(["System Manager", "ARK Admin", "ARK User"])
	return frappe.get_all(
		"Visitor Log",
		filters={"status": "Checked In"},
		fields=[
			"name", "visitor_name", "visitor_company", "visitor_phone",
			"purpose", "host", "host_name", "visiting_space",
			"checked_in_at", "badge_number",
		],
		order_by="checked_in_at desc",
	)

@frappe.whitelist()
def approve_visitor(visitor_name):
	"""Approve a pre-registered visitor."""
	frappe.only_for(["System Manager", "ARK Admin", "ARK User"])
	visitor = frappe.get_doc("Visitor Log", visitor_name)
	if visitor.approval_status == "Approved":
		frappe.throw(_("Visitor is already approved"))

	visitor.db_set({
		"approval_status": "Approved",
		"approved_by": frappe.session.user,
	})

	return {"visitor": visitor.name, "approval_status": "Approved"}

@frappe.whitelist()
def reject_visitor(visitor_name, reason=None):
	"""Reject a visitor pre-registration."""
	frappe.only_for(["System Manager", "ARK Admin", "ARK User"])
	visitor = frappe.get_doc("Visitor Log", visitor_name)
	visitor.db_set({
		"approval_status": "Rejected",
		"status": "Cancelled",
	})

	if reason:
		visitor.add_comment("Info", _("Rejected: {0}").format(reason))

	return {"visitor": visitor.name, "approval_status": "Rejected"}

@frappe.whitelist()
def get_visitor_badge_html(visitor_name):
	"""Generate printable badge HTML for a visitor."""
	frappe.only_for(["System Manager", "ARK Admin", "ARK User"])
	v = frappe.get_doc("Visitor Log", visitor_name)

	html = f"""<!DOCTYPE html>
<html>
<head>
	<meta charset="utf-8">
	<title>Visitor Badge — {v.visitor_name}</title>
	<style>
		* {{ margin: 0; padding: 0; box-sizing: border-box; }}
		body {{ font-family: -apple-system, sans-serif; }}
		.badge {{
			width: 3.5in; height: 2.2in;
			border: 2px solid #1B365D;
			border-radius: 12px;
			padding: 16px;
			margin: 20px auto;
			position: relative;
		}}
		.badge-header {{
			display: flex;
			justify-content: space-between;
			align-items: center;
			margin-bottom: 10px;
		}}
		.badge-logo {{ font-weight: 800; color: #1B365D; font-size: 14px; }}
		.badge-type {{
			background: #C4A962; color: #1B365D;
			padding: 2px 8px; border-radius: 4px;
			font-size: 11px; font-weight: 700;
			text-transform: uppercase;
		}}
		.badge-name {{ font-size: 20px; font-weight: 700; color: #1B365D; }}
		.badge-company {{ font-size: 12px; color: #6B7280; }}
		.badge-details {{
			margin-top: 8px;
			font-size: 11px; color: #374151;
		}}
		.badge-details span {{ display: block; margin: 2px 0; }}
		.badge-number {{
			position: absolute; bottom: 10px; right: 16px;
			font-size: 24px; font-weight: 800; color: #C4A962;
		}}
		@media print {{
			body {{ margin: 0; }}
			.badge {{ margin: 0; border-width: 1px; }}
		}}
	</style>
</head>
<body>
	<div class="badge">
		<div class="badge-header">
			<span class="badge-logo">ARKSpace</span>
			<span class="badge-type">{_("VISITOR")}</span>
		</div>
		<div class="badge-name">{v.visitor_name}</div>
		<div class="badge-company">{v.visitor_company or ""}</div>
		<div class="badge-details">
			<span><b>{_("Host")}:</b> {v.host_name or v.host or "-"}</span>
			<span><b>{_("Purpose")}:</b> {v.purpose}</span>
			<span><b>{_("Date")}:</b> {frappe.utils.formatdate(frappe.utils.nowdate())}</span>
		</div>
		<div class="badge-number">{v.badge_number or ""}</div>
	</div>
	<script>window.print();</script>
</body>
</html>"""

	v.db_set("badge_printed", 1)
	return html

@frappe.whitelist()
def get_visitor_stats(days=30):
	"""Visitor analytics."""
	frappe.only_for(["System Manager", "ARK Admin", "ARK User"])
	from frappe.utils import add_days

	cutoff = add_days(nowdate(), -days)

	total = frappe.db.count("Visitor Log", {"creation": [">=", cutoff]}) or 0
	checked_in = frappe.db.count("Visitor Log", {"status": "Checked In"}) or 0
	today_count = frappe.db.count(
		"Visitor Log",
		{"creation": [">=", f"{nowdate()} 00:00:00"]},
	) or 0

	# Purpose breakdown
	purposes = frappe.db.sql("""
		SELECT purpose, COUNT(*) as count
		FROM `tabVisitor Log`
		WHERE creation >= %s
		GROUP BY purpose
		ORDER BY count DESC
	""", cutoff, as_dict=True)

	return {
		"total_visitors": total,
		"currently_in": checked_in,
		"today": today_count,
		"by_purpose": purposes,
		"period_days": days,
	}

# ═══════════════════════════════════════════════════════════════════════════
# Internal Helpers
# ═══════════════════════════════════════════════════════════════════════════

def _generate_visitor_token(visitor):
	"""Generate a QR token for visitor pass."""
	secret = frappe.utils.password.get_encryption_key()
	payload = f"visitor:{visitor.name}:{frappe.conf.db_name}"
	token = hashlib.sha256(f"{secret}:{payload}".encode()).hexdigest()[:24]
	visitor.db_set("qr_token", token, update_modified=False)
	return token

def _assign_badge(visitor_name):
	"""Auto-assign the next available badge number."""
	# Find the highest badge number currently in use
	in_use = frappe.get_all(
		"Visitor Log",
		filters={
			"status": "Checked In",
			"badge_number": ["is", "set"],
		},
		pluck="badge_number",
	)

	used_numbers = set()
	for b in in_use:
		try:
			used_numbers.add(int(b))
		except (ValueError, TypeError):
			pass

	# Find next available number (1-999)
	badge_no = 1
	while badge_no in used_numbers and badge_no < 1000:
		badge_no += 1

	badge_str = str(badge_no).zfill(3)
	frappe.db.set_value("Visitor Log", visitor_name, "badge_number", badge_str)
	return badge_str
