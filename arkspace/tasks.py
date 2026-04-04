# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

"""ARKSpace — Scheduled Background Tasks
المهام المجدولة في الخلفية

Wired via hooks.py scheduler_events.
"""

import frappe
from frappe import _
from frappe.utils import add_days, add_to_date, getdate, now_datetime, nowdate


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


# ─────────────────── Online Payments ─────────────────────────────────────

def expire_stale_online_payments():
	"""Mark old Initiated/Pending payments as Expired.

	Runs hourly. Uses the payment_link_expiry_hours from ARKSpace Settings
	(default 24 hours).
	"""
	try:
		settings = frappe.get_cached_doc("ARKSpace Settings")
		expiry_hours = int(getattr(settings, "payment_link_expiry_hours", 24) or 24)
	except Exception:
		expiry_hours = 24

	cutoff = add_to_date(now_datetime(), hours=-expiry_hours)

	stale = frappe.get_all(
		"Online Payment",
		filters={
			"status": ["in", ["Initiated", "Pending"]],
			"initiated_at": ["<", cutoff],
		},
		pluck="name",
	)

	for name in stale:
		frappe.db.set_value("Online Payment", name, {
			"status": "Expired",
			"expires_at": now_datetime(),
		})

	if stale:
		frappe.db.commit()
		frappe.logger("arkspace").info(f"Expired {len(stale)} stale online payments")


def bulk_generate_booking_qr_codes():
	"""توليد QR لجميع حجوزات اليوم — Generate QR codes for today's bookings.

	Runs daily to ensure all confirmed bookings have QR codes
	ready for check-in.
	"""
	try:
		from arkspace.arkspace_spaces.qr_checkin import bulk_generate_qr
		result = bulk_generate_qr()
		if result and result.get("generated"):
			frappe.logger("arkspace").info(
				f"Bulk QR: generated {result['generated']} QR codes"
			)
	except Exception:
		frappe.log_error(
			title="Bulk QR Generation Error",
			message=frappe.get_traceback(),
		)


def expire_day_passes():
	"""انتهاء تصاريح الأيام السابقة — Expire past-date day passes.

	Runs daily. Marks Active day passes from previous days as Expired.
	"""
	settings = frappe.get_cached_doc("ARKSpace Settings")
	if not settings.get("day_pass_auto_expire"):
		return

	today = nowdate()
	stale = frappe.get_all(
		"Day Pass",
		filters={
			"docstatus": 1,
			"status": "Active",
			"pass_date": ["<", today],
		},
		pluck="name",
	)

	for name in stale:
		frappe.db.set_value("Day Pass", name, "status", "Expired")

	if stale:
		frappe.db.commit()
		frappe.logger("arkspace").info(f"Expired {len(stale)} day passes")


def auto_checkout_day_passes():
	"""خروج تلقائي لتصاريح اليوم — Auto-checkout checked-in day passes past end time.

	Runs hourly. If a day pass is still Checked In and the current time
	is past the end_time (or 20:00 default), auto check-out.
	"""
	from frappe.utils import get_time

	now = now_datetime()
	today = nowdate()
	current_time = now.time()
	default_end = get_time("20:00:00")

	checked_in = frappe.get_all(
		"Day Pass",
		filters={
			"docstatus": 1,
			"status": "Checked In",
			"pass_date": today,
		},
		fields=["name", "end_time"],
	)

	count = 0
	for dp in checked_in:
		end = get_time(dp.end_time) if dp.end_time else default_end
		if current_time > end:
			try:
				doc = frappe.get_doc("Day Pass", dp.name)
				doc.check_out()
				count += 1
			except Exception:
				frappe.log_error(
					title="Day Pass Auto-Checkout Error",
					message=f"Failed to auto-checkout {dp.name}",
				)

	if count:
		frappe.logger("arkspace").info(f"Auto-checked-out {count} day passes")


def capture_analytics_snapshot():
	"""يومياً — التقاط لقطة تحليلية
	Daily: Capture analytics snapshots for each branch + overall.
	"""
	try:
		from arkspace.arkspace_core.analytics_engine import capture_daily_snapshot
		capture_daily_snapshot()
	except Exception:
		frappe.log_error(
			title="Analytics Snapshot Error",
			message=frappe.get_traceback(),
		)


def update_community_event_statuses():
	"""كل ساعة — تحديث حالات الفعاليات
	Hourly: Update community event statuses based on current time.
	"""
	try:
		from arkspace.arkspace_community.community import update_event_statuses
		update_event_statuses()
	except Exception:
		frappe.log_error(
			title="Community Event Status Update Error",
			message=frappe.get_traceback(),
		)
