# Copyright (c) 2026, ARKSpace Team and contributors
# For license information, please see license.txt

"""ARKSpace Memberships — Public API
إدارة العضويات — واجهة برمجة التطبيقات
"""

import frappe
from frappe import _
from frappe.utils import nowdate, getdate, add_months, flt


@frappe.whitelist()
def get_active_memberships(member=None):
	"""Return active memberships, optionally filtered by member (Customer).

	Args:
		member: Customer name (optional)

	Returns:
		list of active membership dicts
	"""
	filters = {"docstatus": 1, "status": "Active"}
	if member:
		filters["member"] = member

	return frappe.get_all(
		"Membership",
		filters=filters,
		fields=[
			"name", "member", "member_name", "membership_plan", "plan_type",
			"billing_cycle", "start_date", "end_date", "net_amount", "status",
			"assigned_space", "branch", "auto_renew", "credit_wallet",
		],
		order_by="end_date desc",
	)


@frappe.whitelist()
def get_membership_plans(plan_type=None, is_active=True):
	"""Return available membership plans.

	Args:
		plan_type: filter by plan type
		is_active: only active plans (default True)
	"""
	filters = {}
	if is_active:
		filters["is_active"] = 1
	if plan_type:
		filters["plan_type"] = plan_type

	return frappe.get_all(
		"Membership Plan",
		filters=filters,
		fields=[
			"name", "plan_name", "plan_name_ar", "plan_type", "space_type",
			"monthly_price", "quarterly_price", "yearly_price", "currency",
			"included_hours", "included_credits", "max_guests",
			"meeting_room_hours", "printing_pages",
		],
		order_by="monthly_price asc",
	)


@frappe.whitelist()
def create_membership(member, membership_plan, billing_cycle="Monthly",
					  start_date=None, discount_percent=0, assigned_space=None, branch=None):
	"""Create and submit a new Membership.

	Args:
		member: Customer name
		membership_plan: Membership Plan name
		billing_cycle: Monthly / Quarterly / Yearly
		start_date: ISO date (defaults to today)
		discount_percent: discount percentage
		assigned_space: Co-working Space name (optional)
		branch: Branch name (optional)

	Returns:
		dict with membership details
	"""
	if not start_date:
		start_date = nowdate()

	membership = frappe.get_doc({
		"doctype": "Membership",
		"member": member,
		"membership_plan": membership_plan,
		"billing_cycle": billing_cycle,
		"start_date": start_date,
		"discount_percent": flt(discount_percent),
		"assigned_space": assigned_space,
		"branch": branch,
	})
	membership.insert()
	membership.submit()

	return {
		"membership": membership.name,
		"status": membership.status,
		"start_date": str(membership.start_date),
		"end_date": str(membership.end_date),
		"net_amount": membership.net_amount,
	}


@frappe.whitelist()
def get_wallet_balance(member):
	"""Get credit wallet balance for a member.

	Args:
		member: Customer name

	Returns:
		dict with wallet details or None
	"""
	wallet_name = frappe.db.exists("Member Credit Wallet", {"member": member})
	if not wallet_name:
		return {"member": member, "available_credits": 0, "total_credits": 0, "used_credits": 0}

	wallet = frappe.get_doc("Member Credit Wallet", wallet_name)
	return {
		"wallet": wallet.name,
		"member": member,
		"total_credits": wallet.total_credits,
		"used_credits": wallet.used_credits,
		"available_credits": wallet.available_credits,
	}


@frappe.whitelist()
def get_member_dashboard(member):
	"""ملخص لوحة تحكم العضو — Comprehensive member dashboard data.

	Args:
		member: Customer name

	Returns:
		dict with memberships, bookings, wallet, stats
	"""
	today = getdate(nowdate())

	# Active memberships
	memberships = frappe.get_all(
		"Membership",
		filters={"docstatus": 1, "member": member, "status": "Active"},
		fields=["name", "membership_plan", "plan_type", "start_date", "end_date",
				"billing_cycle", "net_amount", "assigned_space", "auto_renew"],
		order_by="end_date desc",
	)

	# Recent bookings (last 30 days)
	recent_bookings = frappe.get_all(
		"Space Booking",
		filters={
			"docstatus": 1,
			"member": member,
			"start_datetime": [">=", add_months(today, -1)],
		},
		fields=["name", "space", "booking_type", "start_datetime", "end_datetime",
				"status", "net_amount", "duration_hours"],
		order_by="start_datetime desc",
		limit=10,
	)

	# Upcoming bookings
	upcoming = frappe.get_all(
		"Space Booking",
		filters={
			"docstatus": 1,
			"member": member,
			"status": ["in", ["Confirmed", "Pending"]],
			"start_datetime": [">=", today],
		},
		fields=["name", "space", "booking_type", "start_datetime", "end_datetime", "status"],
		order_by="start_datetime asc",
		limit=5,
	)

	# Wallet
	wallet_data = get_wallet_balance(member)

	# Stats
	total_bookings = frappe.db.count("Space Booking", {
		"docstatus": 1, "member": member,
		"status": ["not in", ["Cancelled", "No Show"]],
	})
	total_spent = frappe.db.sql("""
		SELECT COALESCE(SUM(net_amount), 0) FROM `tabSpace Booking`
		WHERE docstatus=1 AND member=%s AND status NOT IN ('Cancelled', 'No Show')
	""", member)[0][0]
	total_hours = frappe.db.sql("""
		SELECT COALESCE(SUM(duration_hours), 0) FROM `tabSpace Booking`
		WHERE docstatus=1 AND member=%s AND status NOT IN ('Cancelled', 'No Show')
	""", member)[0][0]

	return {
		"member": member,
		"memberships": memberships,
		"recent_bookings": recent_bookings,
		"upcoming_bookings": upcoming,
		"wallet": wallet_data,
		"stats": {
			"total_bookings": total_bookings,
			"total_spent": flt(total_spent, 2),
			"total_hours": flt(total_hours, 1),
			"active_memberships": len(memberships),
		},
	}
