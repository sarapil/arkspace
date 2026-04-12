# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, nowdate


class UserTrainingProgress(Document):
	def validate(self):
		self._set_completion()

	def after_insert(self):
		self._update_session_count()

	def on_trash(self):
		self._update_session_count()

	def _set_completion(self):
		if self.status == "Completed" and not self.completion_date:
			self.completion_date = getdate(nowdate())
		if self.status == "Completed" and self.progress_percent < 100:
			self.progress_percent = 100

	def _update_session_count(self):
		if self.training_session:
			session = frappe.get_doc("Training Session", self.training_session)
			session.registered_count = frappe.db.count(
				"User Training Progress",
				{"training_session": self.training_session},
			)
			session.db_set("registered_count", session.registered_count)


@frappe.whitelist()
def enroll_user(user, training_module, training_session=None):
	"""Enroll a user in a training module / session.

	Args:
		user: User email
		training_module: Training Module name
		training_session: Optional Training Session name

	Returns:
		dict with the new User Training Progress record
	"""
	frappe.only_for(["ARKSpace User", "ARKSpace Manager", "System Manager"])

	# Check if already enrolled
	existing = frappe.db.exists(
		"User Training Progress",
		{"user": user, "training_module": training_module, "training_session": training_session or ""},
	)
	if existing:
		frappe.throw(_("User {0} is already enrolled in {1}").format(user, training_module))

	# Check capacity
	if training_session:
		session = frappe.get_doc("Training Session", training_session)
		if session.max_participants and session.registered_count >= session.max_participants:
			frappe.throw(_("Session {0} is full ({1}/{2})").format(
				training_session, session.registered_count, session.max_participants
			))

	progress = frappe.new_doc("User Training Progress")
	progress.user = user
	progress.training_module = training_module
	progress.training_session = training_session
	progress.status = "Enrolled"
	progress.enrollment_date = getdate(nowdate())
	progress.flags.ignore_permissions = True
	progress.insert()

	return progress.as_dict()


@frappe.whitelist()
def update_progress(name, status=None, progress_percent=None, score=None, badge=None):
	"""Update a User Training Progress record.

	Args:
		name: User Training Progress name
		status: New status
		progress_percent: New progress %
		score: New score
		badge: Badge to award

	Returns:
		updated dict
	"""
	frappe.has_permission("User Training Progress", "write", throw=True)
	frappe.only_for(["ARKSpace Manager", "System Manager"])

	doc = frappe.get_doc("User Training Progress", name)

	if status:
		doc.status = status
	if progress_percent is not None:
		doc.progress_percent = progress_percent
	if score is not None:
		doc.score = score
	if badge:
		doc.badge = badge
		doc.badge_awarded_on = getdate(nowdate())

	doc.flags.ignore_permissions = True
	doc.save()

	return doc.as_dict()


@frappe.whitelist()
def get_user_progress(user, training_module=None):
	"""Get all training progress records for a user.

	Args:
		user: User email
		training_module: Optional filter

	Returns:
		list of progress records
	"""
	frappe.only_for(["ARKSpace User", "ARKSpace Manager", "System Manager"])

	filters = {"user": user}
	if training_module:
		filters["training_module"] = training_module

	return frappe.get_all(
		"User Training Progress",
		filters=filters,
		fields=[
			"name", "user", "training_module", "training_session",
			"status", "progress_percent", "score",
			"enrollment_date", "completion_date",
			"badge", "badge_awarded_on", "rating",
		],
		order_by="enrollment_date desc",
	)
