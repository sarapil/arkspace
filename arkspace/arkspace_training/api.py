# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

"""ARKSpace Training — API Endpoints
"""

import frappe
from frappe import _


@frappe.whitelist()
def get_training_catalog(category=None, level=None):
	"""Return published training modules.

	Args:
		category: Filter by category
		level: Filter by level

	Returns:
		list of training module dicts
	"""
	frappe.only_for(["ARKSpace User", "ARKSpace Manager", "System Manager"])

	filters = {"status": "Published"}
	if category:
		filters["category"] = category
	if level:
		filters["level"] = level

	return frappe.get_all(
		"Training Module",
		filters=filters,
		fields=[
			"name", "module_name", "category", "level",
			"duration_hours", "instructor", "description",
			"image", "total_sessions", "total_enrollments",
		],
		order_by="module_name asc",
	)


@frappe.whitelist()
def get_upcoming_sessions(training_module=None, branch=None, limit=20):
	"""Return upcoming training sessions.

	Args:
		training_module: Filter by module
		branch: Filter by branch
		limit: Max results

	Returns:
		list of session dicts
	"""
	frappe.only_for(["ARKSpace User", "ARKSpace Manager", "System Manager"])

	from frappe.utils import nowdate

	filters = {
		"docstatus": 1,
		"status": "Scheduled",
		"session_date": [">=", nowdate()],
	}
	if training_module:
		filters["training_module"] = training_module
	if branch:
		filters["branch"] = branch

	return frappe.get_all(
		"Training Session",
		filters=filters,
		fields=[
			"name", "title", "training_module", "session_date",
			"start_time", "end_time", "venue", "space", "branch",
			"max_participants", "registered_count", "instructor",
			"is_online", "meeting_url", "is_free", "fee_amount",
		],
		order_by="session_date asc, start_time asc",
		limit_page_length=limit,
	)


@frappe.whitelist()
def get_available_badges():
	"""Return all active badges."""
	frappe.only_for(["ARKSpace User", "ARKSpace Manager", "System Manager"])

	return frappe.get_all(
		"Training Badge",
		filters={"is_active": 1},
		fields=[
			"name", "badge_name", "badge_code", "category",
			"level", "points", "description", "criteria",
			"icon", "image", "total_awarded",
		],
		order_by="level desc, badge_name asc",
	)


@frappe.whitelist()
def get_user_badges(user=None):
	"""Return badges earned by a user.

	Args:
		user: User email (defaults to current user)

	Returns:
		list of badge dicts with award date
	"""
	frappe.only_for(["ARKSpace User", "ARKSpace Manager", "System Manager"])

	if not user:
		user = frappe.session.user

	progress_with_badges = frappe.get_all(
		"User Training Progress",
		filters={"user": user, "badge": ["is", "set"]},
		fields=["badge", "badge_awarded_on", "training_module", "training_session"],
		order_by="badge_awarded_on desc",
	)

	badges = []
	for p in progress_with_badges:
		badge_info = frappe.get_doc("Training Badge", p.badge)
		badges.append({
			"badge_name": badge_info.badge_name,
			"badge_code": badge_info.badge_code,
			"category": badge_info.category,
			"level": badge_info.level,
			"points": badge_info.points,
			"icon": badge_info.icon,
			"image": badge_info.image,
			"awarded_on": p.badge_awarded_on,
			"training_module": p.training_module,
			"training_session": p.training_session,
		})

	return badges


# Re-export from User Training Progress
from arkspace.arkspace_training.doctype.user_training_progress.user_training_progress import (  # noqa: F401, E402
	enroll_user,
	get_user_progress,
	update_progress,
)
