# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

"""ARKSpace QR Code Check-in Engine

Generates unique QR codes for Space Bookings and provides
scan-to-check-in functionality without additional hardware.
"""

import hashlib
import io
import json

import frappe
from frappe import _
from frappe.utils import (
	get_datetime,
	get_url,
	now_datetime,
	nowdate,
)
from frappe.utils.file_manager import save_file

# ═══════════════════════════════════════════════════════════════════════════
# QR Code Generation
# ═══════════════════════════════════════════════════════════════════════════

def generate_booking_qr(booking_name, force=False):
	"""Generate a QR code image for a Space Booking.

	The QR encodes a signed check-in URL that can be scanned at the door.

	Args:
		booking_name: Space Booking name
		force: Re-generate even if QR already exists

	Returns:
		dict with qr_url (file URL) and checkin_url
	"""
	booking = frappe.get_doc("Space Booking", booking_name)

	# Skip if already has QR and not forcing
	if not force and booking.get("qr_code"):
		return {
			"qr_url": booking.qr_code,
			"checkin_url": _build_checkin_url(booking_name),
		}

	# Generate signed token
	token = _generate_token(booking_name)

	# Build the check-in URL
	checkin_url = _build_checkin_url(booking_name, token)

	# Generate QR image
	qr_data = json.dumps({
		"type": "arkspace_checkin",
		"booking": booking_name,
		"url": checkin_url,
	})

	img_bytes = _create_qr_image(qr_data)

	# Save as file attachment
	filename = f"qr-{booking_name}.png"
	file_doc = save_file(
		filename,
		img_bytes,
		"Space Booking",
		booking_name,
		is_private=0,
	)

	# Store QR URL and token on the booking
	booking.db_set({
		"qr_code": file_doc.file_url,
		"qr_token": token,
	}, update_modified=False)

	return {
		"qr_url": file_doc.file_url,
		"checkin_url": checkin_url,
	}

def _create_qr_image(data, size=10, border=2):
	"""Create a QR code PNG image from data string.

	Uses the segno library (lightweight, pure Python) if available,
	otherwise falls back to the qrcode library.
	"""
	try:
		import segno
		qr = segno.make(data, error="h")
		buf = io.BytesIO()
		qr.save(buf, kind="png", scale=size, border=border)
		return buf.getvalue()
	except ImportError:
		pass

	try:
		import qrcode
		qr = qrcode.QRCode(
			version=None,
			error_correction=qrcode.constants.ERROR_CORRECT_H,
			box_size=size,
			border=border,
		)
		qr.add_data(data)
		qr.make(fit=True)
		img = qr.make_image(fill_color="black", back_color="white")
		buf = io.BytesIO()
		img.save(buf, format="PNG")
		return buf.getvalue()
	except ImportError:
		frappe.throw(
			_(
				"QR code generation requires 'segno' or 'qrcode' package. "
				"Install with: pip install segno"
			)
		)

def _generate_token(booking_name):
	"""Generate a signed HMAC token for the booking."""
	secret = frappe.utils.password.get_encryption_key()
	payload = f"{booking_name}:{frappe.conf.db_name}"
	return hashlib.sha256(
		f"{secret}:{payload}".encode()
	).hexdigest()[:32]

def _build_checkin_url(booking_name, token=None):
	"""Build the check-in URL for a booking."""
	if not token:
		token = frappe.db.get_value(
			"Space Booking", booking_name, "qr_token"
		)
	return get_url(
		f"/api/method/arkspace.arkspace_spaces.qr_checkin"
		f".scan_checkin?booking={booking_name}&token={token}"
	)

# ═══════════════════════════════════════════════════════════════════════════
# QR Scan & Check-in API
# ═══════════════════════════════════════════════════════════════════════════

@frappe.whitelist(allow_guest=True)
def scan_checkin(booking=None, token=None):
	"""Process a QR code scan for check-in.

	This endpoint is called when someone scans the QR code.
	It validates the token, checks timing, and performs check-in.

	Returns HTML page with result (mobile-friendly).
	"""
	if not booking or not token:
		return _checkin_response(
			success=False,
			message=_("Invalid QR code — missing parameters"),
		)

	# Validate booking exists
	if not frappe.db.exists("Space Booking", booking):
		return _checkin_response(
			success=False,
			message=_("Booking {0} not found").format(booking),
		)

	doc = frappe.get_doc("Space Booking", booking)

	# Validate token
	expected_token = _generate_token(booking)
	if token != expected_token and token != doc.get("qr_token"):
		return _checkin_response(
			success=False,
			message=_("Invalid QR code — authentication failed"),
		)

	# Check booking status
	if doc.status == "Checked In":
		return _checkin_response(
			success=True,
			message=_("Already checked in at {0}").format(
				frappe.utils.format_datetime(doc.checked_in_at)
			),
			booking=doc,
			already=True,
		)

	if doc.status == "Cancelled":
		return _checkin_response(
			success=False,
			message=_("This booking has been cancelled"),
		)

	if doc.status not in ("Confirmed", "Pending"):
		return _checkin_response(
			success=False,
			message=_("Booking status is {0} — cannot check in").format(
				doc.status
			),
		)

	# Validate timing (allow 30 min early)
	now = now_datetime()
	start = get_datetime(doc.start_datetime)
	from frappe.utils import add_to_date
	early_window = add_to_date(start, minutes=-30)

	if now < early_window:
		return _checkin_response(
			success=False,
			message=_(
				"Too early to check in. Your booking starts at {0}"
			).format(frappe.utils.format_datetime(doc.start_datetime)),
		)

	end = get_datetime(doc.end_datetime)
	if now > end:
		return _checkin_response(
			success=False,
			message=_("This booking has already ended"),
		)

	# Perform check-in
	frappe.set_user("Administrator")
	doc.db_set({
		"status": "Checked In",
		"checked_in_at": now,
	})

	# Update space status
	if doc.space:
		frappe.db.set_value("Co-working Space", doc.space, {
			"status": "Occupied",
			"current_member": doc.member,
		})

	frappe.db.commit()

	# Notify via realtime
	frappe.publish_realtime(
		"booking_checked_in",
		{
			"booking": doc.name,
			"member": doc.member,
			"space": doc.space,
			"checked_in_at": str(now),
		},
	)

	return _checkin_response(
		success=True,
		message=_("Successfully checked in!"),
		booking=doc,
	)

@frappe.whitelist()
def generate_qr(booking_name):
	"""API endpoint to generate/regenerate QR code for a booking."""
	frappe.only_for(["ARKSpace Manager", "System Manager"])

	return generate_booking_qr(booking_name, force=True)

@frappe.whitelist()
def bulk_generate_qr():
	"""Generate QR codes for all confirmed bookings today that lack one."""
	frappe.only_for(["ARKSpace Manager", "System Manager"])

	today = nowdate()
	bookings = frappe.get_all(
		"Space Booking",
		filters={
			"docstatus": 1,
			"status": ["in", ["Confirmed", "Pending"]],
			"start_datetime": ["between", [f"{today} 00:00:00", f"{today} 23:59:59"]],
			"qr_code": ["is", "not set"],
		},
		pluck="name",
	)

	generated = []
	for name in bookings:
		try:
			result = generate_booking_qr(name)
			generated.append({"booking": name, "qr_url": result["qr_url"]})
		except Exception:
			frappe.log_error(
				title=_("QR Generation Error"),
				message=f"Failed to generate QR for {name}",
			)

	return {
		"generated": len(generated),
		"bookings": generated,
	}

# ═══════════════════════════════════════════════════════════════════════════
# Check-in Response (Mobile-friendly HTML)
# ═══════════════════════════════════════════════════════════════════════════

def _checkin_response(success, message, booking=None, already=False):
	"""Return a mobile-friendly HTML page for QR scan result."""
	color = "#10b981" if success else "#ef4444"
	icon = "✓" if success else "✗"
	if already:
		color = "#f59e0b"
		icon = "ℹ"

	booking_html = ""
	if booking:
		booking_html = f"""
		<div class="booking-details">
			<p><strong>{_("Booking")}:</strong> {booking.name}</p>
			<p><strong>{_("Space")}:</strong> {booking.space}</p>
			<p><strong>{_("Member")}:</strong>
				{booking.member_name or booking.member}</p>
			<p><strong>{_("Time")}:</strong>
				{frappe.utils.format_datetime(booking.start_datetime)}
				— {frappe.utils.format_datetime(booking.end_datetime)}</p>
		</div>
		"""

	html = f"""<!DOCTYPE html>
<html lang="ar" dir="auto">
<head>
	<meta charset="utf-8">
	<meta name="viewport"
		content="width=device-width, initial-scale=1.0">
	<title>ARKSpace Check-in</title>
	<style>
		* {{ margin: 0; padding: 0; box-sizing: border-box; }}
		body {{
			font-family: -apple-system, BlinkMacSystemFont,
				'Segoe UI', Roboto, sans-serif;
			background: #f8fafc;
			display: flex;
			justify-content: center;
			align-items: center;
			min-height: 100vh;
			padding: 20px;
		}}
		.card {{
			background: white;
			border-radius: 16px;
			padding: 40px;
			max-width: 400px;
			width: 100%;
			text-align: center;
			box-shadow: 0 4px 24px rgba(0,0,0,0.08);
		}}
		.icon {{
			width: 80px;
			height: 80px;
			border-radius: 50%;
			background: {color};
			color: white;
			font-size: 40px;
			display: flex;
			align-items: center;
			justify-content: center;
			margin: 0 auto 20px;
		}}
		.message {{
			font-size: 20px;
			font-weight: 600;
			color: #1e293b;
			margin-bottom: 16px;
		}}
		.booking-details {{
			background: #f1f5f9;
			border-radius: 8px;
			padding: 16px;
			text-align: left;
			margin-top: 16px;
		}}
		.booking-details p {{
			margin: 8px 0;
			font-size: 14px;
			color: #475569;
		}}
		.logo {{
			margin-top: 24px;
			font-size: 12px;
			color: #94a3b8;
		}}
	</style>
</head>
<body>
	<div class="card">
		<div class="icon">{icon}</div>
		<div class="message">{message}</div>
		{booking_html}
		<div class="logo">ARKSpace</div>
	</div>
</body>
</html>"""

	frappe.respond_as_web_page(
		title="ARKSpace Check-in",
		html=html,
		http_status_code=200 if success else 400,
		fullpage=True,
	)
