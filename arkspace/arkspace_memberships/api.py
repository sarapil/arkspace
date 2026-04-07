# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

"""ARKSpace Memberships — Public API
"""

import frappe
from frappe import _
from frappe.utils import add_months, flt, getdate, nowdate

@frappe.whitelist()
def get_active_memberships(member=None):
	"""Return active memberships, optionally filtered by member (Customer).

	Args:
		member: Customer name (optional)

	Returns:
		list of active membership dicts
	"""
	frappe.only_for(["System Manager", "ARK Admin", "ARK User"])
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
	frappe.only_for(["System Manager", "ARK Admin", "ARK User"])
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
def create_membership(
	member, membership_plan, billing_cycle="Monthly",
	start_date=None, discount_percent=0, assigned_space=None, branch=None,
):
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
	frappe.only_for(["System Manager", "ARK Admin", "ARK User"])
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
	frappe.only_for(["System Manager", "ARK Admin", "ARK User"])
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
	"""Comprehensive member dashboard data.

	Args:
		member: Customer name

	Returns:
		dict with memberships, bookings, wallet, stats
	"""
	frappe.only_for(["System Manager", "ARK Admin", "ARK User"])
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

# ═══════════════════════════════════════════════════════════════════════════
# Self-Service Portal APIs
# ═══════════════════════════════════════════════════════════════════════════

@frappe.whitelist()
def renew_membership(membership_name, billing_cycle=None):
	"""Renew an existing membership.

	Creates a new Membership as a continuation of the current one.

	Args:
		membership_name: existing Membership name
		billing_cycle: Monthly/Quarterly/Yearly (keeps current if not provided)

	Returns:
		dict with new membership details
	"""
	frappe.only_for(["System Manager", "ARK Admin", "ARK User"])
	old = frappe.get_doc("Membership", membership_name)

	# Validate ownership
	_validate_member_access(old.member)

	if old.docstatus != 1:
		frappe.throw(_("Only submitted memberships can be renewed"))

	cycle = billing_cycle or old.billing_cycle
	start = old.end_date if getdate(old.end_date) >= getdate(nowdate()) else getdate(nowdate())

	new_membership = frappe.get_doc({
		"doctype": "Membership",
		"member": old.member,
		"membership_plan": old.membership_plan,
		"billing_cycle": cycle,
		"start_date": start,
		"assigned_space": old.assigned_space,
		"branch": old.branch,
		"auto_renew": old.auto_renew,
	})
	new_membership.insert()
	new_membership.submit()

	return {
		"membership": new_membership.name,
		"status": new_membership.status,
		"start_date": str(new_membership.start_date),
		"end_date": str(new_membership.end_date),
		"net_amount": new_membership.net_amount,
		"billing_cycle": new_membership.billing_cycle,
	}

@frappe.whitelist()
def upgrade_membership(membership_name, new_plan, billing_cycle=None):
	"""Upgrade or change membership plan.

	Cancels the current membership and creates a new one with the new plan.

	Args:
		membership_name: current Membership name
		new_plan: new Membership Plan name
		billing_cycle: optional new billing cycle

	Returns:
		dict with new membership details
	"""
	frappe.only_for(["System Manager", "ARK Admin", "ARK User"])
	old = frappe.get_doc("Membership", membership_name)

	_validate_member_access(old.member)

	if old.docstatus != 1 or old.status != "Active":
		frappe.throw(_("Only active memberships can be upgraded"))

	if old.membership_plan == new_plan and not billing_cycle:
		frappe.throw(_("Please select a different plan or billing cycle"))

	# Calculate prorated credit for remaining days
	today = getdate(nowdate())
	end = getdate(old.end_date)
	if end > today:
		total_days = (end - getdate(old.start_date)).days or 1
		remaining_days = (end - today).days
		prorated_credit = flt(old.net_amount * remaining_days / total_days, 2)
	else:
		prorated_credit = 0

	# Cancel old membership
	old.cancel()

	# Create new membership starting today
	cycle = billing_cycle or old.billing_cycle
	new_membership = frappe.get_doc({
		"doctype": "Membership",
		"member": old.member,
		"membership_plan": new_plan,
		"billing_cycle": cycle,
		"start_date": nowdate(),
		"assigned_space": old.assigned_space,
		"branch": old.branch,
		"auto_renew": old.auto_renew,
	})
	new_membership.insert()
	new_membership.submit()

	return {
		"membership": new_membership.name,
		"previous": old.name,
		"prorated_credit": prorated_credit,
		"status": new_membership.status,
		"plan": new_plan,
		"start_date": str(new_membership.start_date),
		"end_date": str(new_membership.end_date),
		"net_amount": new_membership.net_amount,
	}

@frappe.whitelist()
def get_renewal_options(membership_name):
	"""Get renewal options for a membership.

	Returns pricing for different billing cycles based on current plan.
	"""
	frappe.only_for(["System Manager", "ARK Admin", "ARK User"])
	mem = frappe.get_doc("Membership", membership_name)
	_validate_member_access(mem.member)

	plan = frappe.get_doc("Membership Plan", mem.membership_plan)

	options = []
	cycles = {
		"Monthly": plan.monthly_price,
		"Quarterly": plan.quarterly_price or flt(plan.monthly_price * 3 * 0.9, 2),
		"Yearly": plan.yearly_price or flt(plan.monthly_price * 12 * 0.8, 2),
	}

	for cycle, price in cycles.items():
		if price:
			options.append({
				"billing_cycle": cycle,
				"price": price,
				"currency": plan.currency or frappe.defaults.get_default("currency"),
				"is_current": cycle == mem.billing_cycle,
			})

	return {
		"membership": mem.name,
		"current_plan": mem.membership_plan,
		"current_cycle": mem.billing_cycle,
		"end_date": str(mem.end_date),
		"options": options,
	}

@frappe.whitelist(allow_guest=True)
def register_member(full_name, email, phone=None, plan=None,
                    billing_cycle="Monthly", company_name=None):
	"""Self-service member registration.

	Creates a User + Customer + optional Membership.

	Args:
		full_name: member full name
		email: email address (becomes the login)
		phone: phone number
		plan: Membership Plan name (optional — create membership if provided)
		billing_cycle: Monthly/Quarterly/Yearly
		company_name: company name (optional)

	Returns:
		dict with registration details
	"""
	# Check if user already exists
	if frappe.db.exists("User", email):
		frappe.throw(_("An account with this email already exists. Please login."))

	# Create User
	user = frappe.get_doc({
		"doctype": "User",
		"email": email,
		"first_name": full_name.split(" ")[0],
		"last_name": " ".join(full_name.split(" ")[1:]) if " " in full_name else "",
		"user_type": "Website User",
		"send_welcome_email": 1,
	})
	user.insert(ignore_permissions=True)

	# Create Customer
	customer = frappe.get_doc({
		"doctype": "Customer",
		"customer_name": full_name,
		"customer_type": "Individual" if not company_name else "Company",
		"customer_group": frappe.db.get_single_value("Selling Settings", "customer_group")
			or "All Customer Groups",
		"territory": frappe.db.get_single_value("Selling Settings", "territory")
			or "All Territories",
		"email_id": email,
		"mobile_no": phone,
	})
	customer.insert(ignore_permissions=True)

	# Link User to Customer via Contact
	contact = frappe.get_doc({
		"doctype": "Contact",
		"first_name": full_name.split(" ")[0],
		"last_name": " ".join(full_name.split(" ")[1:]) if " " in full_name else "",
		"user": email,
		"email_ids": [{"email_id": email, "is_primary": 1}],
		"links": [{"link_doctype": "Customer", "link_name": customer.name}],
	})
	if phone:
		contact.append("phone_nos", {"phone": phone, "is_primary_phone": 1})
	contact.insert(ignore_permissions=True)

	result = {
		"user": user.name,
		"customer": customer.name,
		"contact": contact.name,
	}

	# Create membership if plan specified
	if plan and frappe.db.exists("Membership Plan", plan):
		membership = frappe.get_doc({
			"doctype": "Membership",
			"member": customer.name,
			"membership_plan": plan,
			"billing_cycle": billing_cycle,
			"start_date": nowdate(),
		})
		membership.insert(ignore_permissions=True)
		membership.submit()
		result["membership"] = membership.name
		result["membership_status"] = membership.status

	frappe.db.commit()

	return result

@frappe.whitelist()
def get_payment_history(member=None, limit=20):
	"""Get payment history for a member.

	Returns invoices and online payments.
	"""
	frappe.only_for(["System Manager", "ARK Admin", "ARK User"])
	if not member:
		member = _get_current_member()

	_validate_member_access(member)

	# Sales Invoices
	invoices = frappe.get_all(
		"Sales Invoice",
		filters={
			"customer": member,
			"docstatus": ["!=", 2],
		},
		fields=[
			"name", "posting_date", "grand_total", "outstanding_amount",
			"currency", "status", "due_date",
		],
		order_by="posting_date desc",
		limit=limit,
	)

	# Online Payments
	online_payments = frappe.get_all(
		"Online Payment",
		filters={
			"member": member,
		},
		fields=[
			"name", "initiated_at", "amount", "currency", "gateway",
			"status", "payment_method_type", "card_last_four",
		],
		order_by="initiated_at desc",
		limit=limit,
	)

	# Payment summary
	total_paid = frappe.db.sql("""
		SELECT COALESCE(SUM(grand_total - outstanding_amount), 0)
		FROM `tabSales Invoice`
		WHERE customer=%s AND docstatus=1
	""", member)[0][0]

	total_outstanding = frappe.db.sql("""
		SELECT COALESCE(SUM(outstanding_amount), 0)
		FROM `tabSales Invoice`
		WHERE customer=%s AND docstatus=1 AND outstanding_amount > 0
	""", member)[0][0]

	return {
		"member": member,
		"invoices": invoices,
		"online_payments": online_payments,
		"summary": {
			"total_paid": flt(total_paid, 2),
			"total_outstanding": flt(total_outstanding, 2),
			"invoice_count": len(invoices),
		},
	}

@frappe.whitelist()
def toggle_auto_renew(membership_name, auto_renew):
	"""Toggle auto-renewal for a membership."""
	frappe.only_for(["System Manager", "ARK Admin", "ARK User"])
	mem = frappe.get_doc("Membership", membership_name)
	_validate_member_access(mem.member)

	mem.db_set("auto_renew", 1 if int(auto_renew) else 0)
	return {"membership": mem.name, "auto_renew": mem.auto_renew}

# ═══════════════════════════════════════════════════════════════════════════
# Internal Helpers
# ═══════════════════════════════════════════════════════════════════════════

def _validate_member_access(member):
	"""Ensure the current user has access to this member's data."""
	if frappe.session.user == "Administrator":
		return
	if "System Manager" in frappe.get_roles():
		return
	if "ARKSpace Admin" in frappe.get_roles():
		return

	current_member = _get_current_member()
	if current_member != member:
		frappe.throw(_("You do not have permission to access this data"), frappe.PermissionError)

def _get_current_member():
	"""Find Customer linked to current user."""
	contacts = frappe.get_all("Contact", filters={"user": frappe.session.user}, pluck="name")
	if contacts:
		customer = frappe.db.get_value(
			"Dynamic Link",
			{"parenttype": "Contact", "link_doctype": "Customer", "parent": ["in", contacts]},
			"link_name",
		)
		if customer:
			return customer

	return frappe.db.get_value("Customer", {"email_id": frappe.session.user}, "name")
