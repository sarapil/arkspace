# Copyright (c) 2026, ARKSpace Team and contributors
# For license information, please see license.txt

"""Visitor Log — سجل الزوار

Tracks visitors to the co-working space with check-in/out,
host notification, badge generation, and pre-registration.
"""

import frappe
from frappe import _
from frappe.utils import now_datetime


class VisitorLog(frappe.model.document.Document):
	def validate(self):
		self._validate_times()

	def before_insert(self):
		if frappe.session.user != "Administrator" and not self.preregistered_by:
			self.preregistered_by = frappe.session.user

	def after_insert(self):
		self._notify_host()

	def _validate_times(self):
		"""Validate expected arrival is before departure."""
		if self.expected_arrival and self.expected_departure:
			if self.expected_arrival >= self.expected_departure:
				frappe.throw(
					_("Expected departure must be after expected arrival")
				)

	def check_in(self):
		"""تسجيل دخول الزائر — Mark visitor as checked in."""
		if self.status == "Checked In":
			frappe.throw(_("Visitor is already checked in"))
		if self.status in ("Checked Out", "Cancelled"):
			frappe.throw(
				_("Cannot check in a visitor with status {0}").format(self.status)
			)

		self.db_set({
			"status": "Checked In",
			"checked_in_at": now_datetime(),
		})

		# Notify host of arrival
		self._notify_host_arrival()

		frappe.publish_realtime(
			"visitor_checked_in",
			{
				"visitor": self.name,
				"visitor_name": self.visitor_name,
				"host": self.host,
				"space": self.visiting_space,
			},
		)

	def check_out(self):
		"""تسجيل خروج الزائر — Mark visitor as checked out."""
		if self.status != "Checked In":
			frappe.throw(_("Visitor must be checked in before checking out"))

		self.db_set({
			"status": "Checked Out",
			"checked_out_at": now_datetime(),
		})

		frappe.publish_realtime(
			"visitor_checked_out",
			{
				"visitor": self.name,
				"visitor_name": self.visitor_name,
			},
		)

	def _notify_host(self):
		"""Send notification to host about pre-registered visitor."""
		if not self.host:
			return

		host_email = frappe.db.get_value("Customer", self.host, "email_id")
		if not host_email:
			return

		try:
			frappe.sendmail(
				recipients=[host_email],
				subject=_("Visitor Pre-registered: {0}").format(self.visitor_name),
				message=_(
					"A visitor has been registered to meet you."
					"<br><br>"
					"<b>Visitor:</b> {0}<br>"
					"<b>Company:</b> {1}<br>"
					"<b>Purpose:</b> {2}<br>"
					"<b>Expected:</b> {3}"
				).format(
					self.visitor_name,
					self.visitor_company or "-",
					self.purpose,
					frappe.utils.format_datetime(self.expected_arrival)
					if self.expected_arrival else "-",
				),
				reference_doctype="Visitor Log",
				reference_name=self.name,
			)
		except Exception:
			frappe.log_error(
				title=_("Visitor notification error"),
				message=f"Failed to notify host for {self.name}",
			)

	def _notify_host_arrival(self):
		"""Notify host when visitor actually arrives."""
		if not self.host:
			return

		host_email = frappe.db.get_value("Customer", self.host, "email_id")
		if not host_email:
			return

		# Also try to find user linked to customer for realtime notification
		host_user = frappe.db.get_value(
			"Dynamic Link",
			{
				"parenttype": "Contact",
				"link_doctype": "Customer",
				"link_name": self.host,
			},
			"parent",
		)
		if host_user:
			contact_user = frappe.db.get_value("Contact", host_user, "user")
			if contact_user:
				frappe.publish_realtime(
					"visitor_arrived",
					{
						"visitor": self.name,
						"visitor_name": self.visitor_name,
						"message": _("Your visitor {0} has arrived").format(
							self.visitor_name
						),
					},
					user=contact_user,
				)

		try:
			frappe.sendmail(
				recipients=[host_email],
				subject=_("Your visitor {0} has arrived").format(self.visitor_name),
				message=_(
					"Your visitor <b>{0}</b> has checked in and is waiting for you."
				).format(self.visitor_name),
				reference_doctype="Visitor Log",
				reference_name=self.name,
			)
		except Exception:
			frappe.log_error(
				title=_("Visitor arrival notification error"),
				message=f"Failed to notify host arrival for {self.name}",
			)
