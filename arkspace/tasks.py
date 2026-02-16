# Copyright (c) 2026, ARKSpace Team and contributors
# For license information, please see license.txt

"""ARKSpace — Scheduled Background Tasks
المهام المجدولة في الخلفية

Wired via hooks.py scheduler_events.
"""

import frappe
from frappe import _
from frappe.utils import add_days, getdate, now_datetime, nowdate


def check_membership_expiry():
	"""يومياً — التحقق من انتهاء العضويات
	Daily: Mark memberships as Expired when end_date has passed.
	"""
	today = getdate(nowdate())

	expired = frappe.get_all(
		"Membership",
		filters={
			"docstatus": 1,
			"status": "Active",
			"end_date": ["<", today],
		},
		pluck="name",
	)

	for name in expired:
		try:
			frappe.db.set_value("Membership", name, "status", "Expired")
			frappe.logger("arkspace").info(f"Membership {name} marked as Expired")
		except Exception:
			frappe.log_error(f"Error expiring membership {name}")

	if expired:
		frappe.db.commit()
		frappe.logger("arkspace").info(f"Expired {len(expired)} membership(s)")


def auto_renew_memberships():
	"""يومياً — تجديد العضويات التلقائي
	Daily: Auto-renew memberships that have auto_renew=1 and expire today.
	"""
	today = getdate(nowdate())

	to_renew = frappe.get_all(
		"Membership",
		filters={
			"docstatus": 1,
			"status": "Active",
			"auto_renew": 1,
			"end_date": today,
		},
		fields=["name", "member", "membership_plan", "billing_cycle", "discount_percent",
				"assigned_space", "branch", "end_date"],
	)

	for mem in to_renew:
		try:
			new_membership = frappe.get_doc({
				"doctype": "Membership",
				"member": mem.member,
				"membership_plan": mem.membership_plan,
				"billing_cycle": mem.billing_cycle,
				"start_date": add_days(mem.end_date, 1),
				"discount_percent": mem.discount_percent,
				"assigned_space": mem.assigned_space,
				"branch": mem.branch,
				"auto_renew": 1,
			})
			new_membership.insert(ignore_permissions=True)
			new_membership.submit()

			frappe.logger("arkspace").info(
				f"Auto-renewed membership {mem.name} → {new_membership.name}"
			)

			# Notify the member
			frappe.publish_realtime(
				"membership_renewed",
				{"old": mem.name, "new": new_membership.name, "member": mem.member},
			)
		except Exception:
			frappe.log_error(f"Error auto-renewing membership {mem.name}")

	if to_renew:
		frappe.db.commit()


def mark_no_show_bookings():
	"""كل ساعة — تحديد حالة عدم الحضور
	Hourly: Mark Confirmed bookings as No Show if start_datetime passed > 2 hours ago.
	"""
	now = now_datetime()

	no_shows = frappe.get_all(
		"Space Booking",
		filters={
			"docstatus": 1,
			"status": "Confirmed",
			"start_datetime": ["<", frappe.utils.add_to_date(now, hours=-2)],
		},
		pluck="name",
	)

	for name in no_shows:
		try:
			frappe.db.set_value("Space Booking", name, "status", "No Show")
			frappe.logger("arkspace").info(f"Booking {name} marked as No Show")
		except Exception:
			frappe.log_error(f"Error marking no-show for booking {name}")

	if no_shows:
		frappe.db.commit()
		frappe.logger("arkspace").info(f"Marked {len(no_shows)} booking(s) as No Show")


def auto_checkout_expired_bookings():
	"""كل ساعة — تسجيل خروج تلقائي
	Hourly: Auto check-out bookings where end_datetime has passed.
	"""
	now = now_datetime()

	overdue = frappe.get_all(
		"Space Booking",
		filters={
			"docstatus": 1,
			"status": "Checked In",
			"end_datetime": ["<", now],
		},
		fields=["name", "space", "member"],
	)

	for bk in overdue:
		try:
			frappe.db.set_value("Space Booking", bk.name, {
				"status": "Checked Out",
				"checked_out_at": now,
			})

			# Free the space
			frappe.db.set_value("Co-working Space", bk.space, {
				"status": "Available",
				"current_member": None,
			})

			frappe.publish_realtime("space_status_changed", {
				"space": bk.space,
				"status": "Available",
				"booking": bk.name,
				"auto_checkout": True,
			})

			frappe.logger("arkspace").info(f"Auto checked-out booking {bk.name}")
		except Exception:
			frappe.log_error(f"Error auto-checking-out booking {bk.name}")

	if overdue:
		frappe.db.commit()


def send_membership_expiry_reminders():
	"""يومياً — إرسال تذكيرات انتهاء العضوية
	Daily: Send reminders for memberships expiring in 7 days or 1 day.
	"""
	today = getdate(nowdate())

	for days_before in [7, 1]:
		target_date = add_days(today, days_before)
		expiring = frappe.get_all(
			"Membership",
			filters={
				"docstatus": 1,
				"status": "Active",
				"end_date": target_date,
			},
			fields=["name", "member", "member_name", "membership_plan", "end_date", "auto_renew"],
		)

		for mem in expiring:
			try:
				subject = _("Membership Expiry Reminder — {0} days").format(days_before)
				message = _(
					"Dear {0},<br><br>"
					"Your membership <b>{1}</b> (Plan: {2}) will expire on <b>{3}</b>.<br>"
					"{4}<br><br>"
					"Thank you,<br>ARKSpace Team"
				).format(
					mem.member_name or mem.member,
					mem.name,
					mem.membership_plan,
					mem.end_date,
					_("It will be auto-renewed.") if mem.auto_renew else _(
						"Please renew your membership to continue enjoying our services."
					),
				)

				# Get member's email from Customer
				email = frappe.db.get_value("Customer", mem.member, "email_id")
				if email:
					frappe.sendmail(
						recipients=[email],
						subject=subject,
						message=message,
						reference_doctype="Membership",
						reference_name=mem.name,
					)
			except Exception:
				frappe.log_error(f"Error sending expiry reminder for {mem.name}")


def generate_daily_occupancy_snapshot():
	"""يومياً — لقطة يومية للإشغال
	Daily: Record occupancy stats for historical reporting.
	"""
	today = getdate(nowdate())

	total = frappe.db.count("Co-working Space") or 0
	occupied = frappe.db.count("Co-working Space", {"status": "Occupied"}) or 0
	reserved = frappe.db.count("Co-working Space", {"status": "Reserved"}) or 0
	maintenance = frappe.db.count("Co-working Space", {"status": "Maintenance"}) or 0
	available = frappe.db.count("Co-working Space", {"status": "Available"}) or 0

	active_bookings = frappe.db.count("Space Booking", {
		"docstatus": 1,
		"status": ["in", ["Confirmed", "Checked In"]],
		"start_datetime": ["<=", now_datetime()],
		"end_datetime": [">=", now_datetime()],
	}) or 0

	active_memberships = frappe.db.count("Membership", {
		"docstatus": 1,
		"status": "Active",
	}) or 0

	# Store as a Comment on ARKSpace Settings for simplicity
	# (In production, this would be a dedicated Occupancy Snapshot doctype)
	snapshot = {
		"date": str(today),
		"total_spaces": total,
		"occupied": occupied,
		"reserved": reserved,
		"maintenance": maintenance,
		"available": available,
		"occupancy_rate": round((occupied / total * 100) if total else 0, 1),
		"active_bookings": active_bookings,
		"active_memberships": active_memberships,
	}

	frappe.logger("arkspace").info(f"Daily occupancy snapshot: {snapshot}")

	# Publish for any connected dashboards
	frappe.publish_realtime("occupancy_snapshot", snapshot)
