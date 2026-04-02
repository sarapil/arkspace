# Copyright (c) 2026, ARKSpace Team and contributors
# For license information, please see license.txt

"""ARKSpace Dynamic Pricing Engine
محرك التسعير الديناميكي

Evaluates Pricing Rules against a booking context and returns the
adjusted rate. Supports percentage, fixed, multiplier, and override
adjustments with stacking, caps, and minimum-rate floors.
"""

import frappe
from frappe import _
from frappe.utils import flt, get_datetime, getdate

# ═══════════════════════════════════════════════════════════════════════════
# Public API
# ═══════════════════════════════════════════════════════════════════════════


def calculate_dynamic_rate(context):
	"""Calculate the final rate after applying all matching pricing rules.

	Args:
		context (dict):
			base_rate (float): Original rate from Co-working Space
			booking_type (str): Hourly / Daily / Monthly
			start_datetime (datetime): Booking start
			end_datetime (datetime): Booking end
			duration_hours (float): Booking duration in hours
			space (str): Co-working Space name
			space_type (str): Space Type name
			member (str): Customer name (optional)
			membership_plan (str): Active plan name (optional)
			member_tier (str): Member tier level (optional)

	Returns:
		dict with:
			final_rate (float): Adjusted rate
			base_rate (float): Original rate
			adjustments (list): Applied rules with details
			total_adjustment_pct (float): Net percentage change
	"""
	base_rate = flt(context.get("base_rate", 0))
	if base_rate <= 0:
		return {
			"final_rate": base_rate,
			"base_rate": base_rate,
			"adjustments": [],
			"total_adjustment_pct": 0,
		}

	rules = _get_matching_rules(context)

	if not rules:
		return {
			"final_rate": base_rate,
			"base_rate": base_rate,
			"adjustments": [],
			"total_adjustment_pct": 0,
		}

	final_rate = base_rate
	adjustments = []
	override_applied = False

	for rule in rules:
		if override_applied and rule.adjustment_type != "Override Rate":
			continue

		adj = _apply_rule(rule, base_rate, final_rate)
		if adj is None:
			continue

		if rule.adjustment_type == "Override Rate":
			final_rate = adj["new_rate"]
			override_applied = True
		else:
			final_rate = adj["new_rate"]

		adjustments.append(adj)

	# Apply minimum rate floor
	global_min = 0
	for rule in rules:
		if flt(rule.min_rate) > 0:
			global_min = max(global_min, flt(rule.min_rate))

	if global_min > 0 and final_rate < global_min:
		final_rate = global_min
		adjustments.append({
			"rule_name": _("Minimum Rate Floor"),
			"rule_type": "Floor",
			"adjustment": f"min {global_min}",
			"old_rate": final_rate,
			"new_rate": global_min,
		})

	pct_change = (
		((final_rate - base_rate) / base_rate * 100)
		if base_rate else 0
	)

	return {
		"final_rate": flt(final_rate, 2),
		"base_rate": flt(base_rate, 2),
		"adjustments": adjustments,
		"total_adjustment_pct": flt(pct_change, 2),
	}


@frappe.whitelist()
def get_dynamic_rate(
	space, booking_type, start_datetime, end_datetime,
	duration_hours=None, member=None,
):
	"""API endpoint: Get the dynamic rate for a booking scenario.

	Used by the Space Booking form to preview adjusted pricing.
	"""
	space_doc = frappe.get_cached_doc("Co-working Space", space)

	rate_map = {
		"Hourly": flt(space_doc.hourly_rate),
		"Daily": flt(space_doc.daily_rate),
		"Monthly": flt(space_doc.monthly_rate),
	}
	base_rate = rate_map.get(booking_type, 0)

	# Resolve member tier from active membership
	member_tier = ""
	membership_plan = ""
	if member:
		active_mem = frappe.db.get_value(
			"Membership",
			{"member": member, "status": "Active", "docstatus": 1},
			["membership_plan", "plan_type"],
			as_dict=True,
		)
		if active_mem:
			membership_plan = active_mem.membership_plan
			# Tier could be derived from plan_type or a custom field
			member_tier = _resolve_member_tier(member)

	context = {
		"base_rate": base_rate,
		"booking_type": booking_type,
		"start_datetime": get_datetime(start_datetime),
		"end_datetime": get_datetime(end_datetime),
		"duration_hours": flt(duration_hours),
		"space": space,
		"space_type": space_doc.space_type,
		"member": member,
		"membership_plan": membership_plan,
		"member_tier": member_tier,
	}

	return calculate_dynamic_rate(context)


# ═══════════════════════════════════════════════════════════════════════════
# Rule matching & evaluation
# ═══════════════════════════════════════════════════════════════════════════


def _get_matching_rules(context):
	"""Fetch and filter all active Pricing Rules that match the context."""
	rules = frappe.get_all(
		"Pricing Rule",
		filters={"enabled": 1},
		fields=["*"],
		order_by="priority asc, creation asc",
	)

	matched = []
	for rule in rules:
		if not _is_valid(rule):
			continue
		if not _matches_scope(rule, context):
			continue
		if not _matches_condition(rule, context):
			continue
		matched.append(rule)

	# Handle stacking: non-stackable rules take precedence by priority
	return _resolve_stacking(matched)


def _is_valid(rule):
	"""Check validity window."""
	now = frappe.utils.now_datetime()
	if rule.valid_from and get_datetime(rule.valid_from) > now:
		return False
	if rule.valid_to and get_datetime(rule.valid_to) < now:
		return False
	return True


def _matches_scope(rule, ctx):
	"""Check if rule's scope (space, type, booking type) matches."""
	# Space scope
	if not rule.apply_to_all_spaces:
		if rule.specific_space and rule.specific_space != ctx.get("space"):
			return False
		if rule.space_type and rule.space_type != ctx.get("space_type"):
			return False

	# Booking type scope
	if not rule.apply_to_all_booking_types:
		if rule.booking_type and rule.booking_type != ctx.get("booking_type"):
			return False

	# Membership plan scope
	if rule.membership_plan:
		if rule.membership_plan != ctx.get("membership_plan"):
			return False

	return True


def _matches_condition(rule, ctx):
	"""Evaluate the rule's condition against the booking context."""
	ctype = rule.condition_type

	if ctype == "Always":
		return True

	if ctype == "Time Range":
		return _check_time_range(rule, ctx)

	if ctype == "Day of Week":
		return _check_day_of_week(rule, ctx)

	if ctype == "Date Range":
		return _check_date_range(rule, ctx)

	if ctype == "Booking Duration":
		return _check_duration(rule, ctx)

	if ctype == "Member Tier":
		return _check_member_tier(rule, ctx)

	return False


def _check_time_range(rule, ctx):
	"""Check if booking falls within the rule's time window."""
	start = ctx.get("start_datetime")
	if not start:
		return False

	booking_time = start.time() if hasattr(start, "time") else start
	from datetime import time as dt_time

	try:
		parts_start = str(rule.time_start).split(":")
		parts_end = str(rule.time_end).split(":")
		t_start = dt_time(int(parts_start[0]), int(parts_start[1]))
		t_end = dt_time(int(parts_end[0]), int(parts_end[1]))
	except (ValueError, IndexError):
		return False

	if t_start <= t_end:
		return t_start <= booking_time <= t_end
	else:
		# Overnight range (e.g., 22:00 - 06:00)
		return booking_time >= t_start or booking_time <= t_end


def _check_day_of_week(rule, ctx):
	"""Check if booking date matches the rule's day."""
	start = ctx.get("start_datetime")
	if not start:
		return False

	days = [
		"Monday", "Tuesday", "Wednesday",
		"Thursday", "Friday", "Saturday", "Sunday",
	]
	booking_day = days[start.weekday()] if hasattr(start, "weekday") else ""
	return booking_day == rule.day_of_week


def _check_date_range(rule, ctx):
	"""Check if booking date falls within a date range."""
	start = ctx.get("start_datetime")
	if not start:
		return False

	booking_date = getdate(start)
	date_start = getdate(rule.date_start) if rule.date_start else None
	date_end = getdate(rule.date_end) if rule.date_end else None

	if date_start and booking_date < date_start:
		return False
	if date_end and booking_date > date_end:
		return False
	return True


def _check_duration(rule, ctx):
	"""Check if booking duration matches min/max hours."""
	duration = flt(ctx.get("duration_hours", 0))
	if rule.min_hours and duration < flt(rule.min_hours):
		return False
	if rule.max_hours and duration > flt(rule.max_hours):
		return False
	return True


def _check_member_tier(rule, ctx):
	"""Check if member's tier matches."""
	return ctx.get("member_tier") == rule.member_tier


# ═══════════════════════════════════════════════════════════════════════════
# Adjustment calculation
# ═══════════════════════════════════════════════════════════════════════════


def _apply_rule(rule, base_rate, current_rate):
	"""Calculate the adjusted rate from a single rule.

	Returns dict with rule details and new_rate, or None if no change.
	"""
	old_rate = current_rate
	new_rate = current_rate

	if rule.adjustment_type == "Percentage":
		change = flt(current_rate) * flt(rule.adjustment_value) / 100
		# Apply cap
		if flt(rule.max_adjustment_amount) > 0:
			if abs(change) > flt(rule.max_adjustment_amount):
				change = (
					flt(rule.max_adjustment_amount)
					if change > 0
					else -flt(rule.max_adjustment_amount)
				)
		new_rate = flt(current_rate) + change

	elif rule.adjustment_type == "Fixed Amount":
		new_rate = flt(current_rate) + flt(rule.adjustment_value)

	elif rule.adjustment_type == "Multiplier":
		new_rate = flt(current_rate) * flt(rule.adjustment_value)

	elif rule.adjustment_type == "Override Rate":
		new_rate = flt(rule.adjustment_value)

	# Ensure rate doesn't go negative
	new_rate = max(0, new_rate)

	if flt(new_rate, 2) == flt(old_rate, 2):
		return None

	return {
		"rule_name": rule.rule_name,
		"rule_type": rule.rule_type,
		"adjustment_type": rule.adjustment_type,
		"adjustment_value": rule.adjustment_value,
		"old_rate": flt(old_rate, 2),
		"new_rate": flt(new_rate, 2),
		"change": flt(new_rate - old_rate, 2),
		"change_pct": flt(
			(new_rate - old_rate) / old_rate * 100 if old_rate else 0, 2
		),
	}


def _resolve_stacking(rules):
	"""Resolve rule stacking — non-stackable rules in the same priority
	group pick the best (highest discount or lowest surcharge).
	Stackable rules all apply.
	"""
	if not rules:
		return []

	result = []
	seen_groups = {}

	for rule in rules:
		if rule.stackable:
			result.append(rule)
		else:
			key = (rule.priority, rule.stacking_group or rule.name)
			if key not in seen_groups:
				seen_groups[key] = rule
				result.append(rule)

	return result


def _resolve_member_tier(member):
	"""Resolve a member's tier from their active membership plan type.

	Simple mapping — can be customized per deployment.
	"""
	plan_type = frappe.db.get_value(
		"Membership",
		{"member": member, "status": "Active", "docstatus": 1},
		"plan_type",
	)

	tier_map = {
		"Hot Desk": "Bronze",
		"Dedicated Desk": "Silver",
		"Private Office": "Gold",
		"Meeting Room": "Silver",
		"Event Space": "Gold",
		"Virtual Office": "Bronze",
	}

	return tier_map.get(plan_type, "")
