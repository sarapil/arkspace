# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

"""ARKSpace Setup Wizard
Adds ARKSpace-specific steps to the Frappe setup wizard.
"""

import frappe
from frappe import _


def get_setup_stages(args=None):
	"""Return setup wizard stages for hooks.py setup_wizard_stages."""
	return [
		{
			"status": _("Configuring ARKSpace"),
			"fail_msg": _("Failed to configure ARKSpace"),
			"tasks": [
				{
					"fn": setup_arkspace_config,
					"args": args,
					"fail_msg": _("Failed to configure ARKSpace"),
				}
			],
		}
	]


def get_setup_slides():
	"""Return setup wizard slides for hooks.py setup_wizard_requires."""
	return [
		{
			"slide_name": "arkspace_welcome",
			"slide_title": _("Welcome to ARKSpace"),
			"slide_desc": _("Configure your co-working space management system."),
			"slide_icon": "fa-solid fa-cubes",
			"slide_order": 30,
			"fields": [
				{
					"fieldtype": "Data",
					"fieldname": "workspace_name",
					"label": _("Workspace Name"),
					"description": _("The name of your co-working space brand"),
					"reqd": 1,
					"default": "ARKSpace",
				},
				{
					"fieldtype": "Select",
					"fieldname": "default_currency",
					"label": _("Default Currency"),
					"options": "AED\nSAR\nEGP\nUSD\nEUR\nGBP",
					"default": "AED",
					"reqd": 1,
				},
				{
					"fieldtype": "Select",
					"fieldname": "timezone",
					"label": _("Timezone"),
					"options": "Asia/Dubai\nAsia/Riyadh\nAfrica/Cairo\nEurope/Istanbul\nAmerica/New_York\nEurope/London",
					"default": "Asia/Dubai",
					"reqd": 1,
				},
			],
		},
		{
			"slide_name": "arkspace_branches",
			"slide_title": _("Branches"),
			"slide_desc": _("Add your co-working space locations. You can add more later."),
			"slide_icon": "fa-solid fa-map-marker-alt",
			"slide_order": 31,
			"fields": [
				{
					"fieldtype": "Data",
					"fieldname": "branch_1",
					"label": _("Main Branch"),
					"reqd": 1,
					"default": _("Main Branch"),
				},
				{
					"fieldtype": "Data",
					"fieldname": "branch_2",
					"label": _("Branch 2 (Optional)"),
				},
				{
					"fieldtype": "Data",
					"fieldname": "branch_3",
					"label": _("Branch 3 (Optional)"),
				},
			],
		},
		{
			"slide_name": "arkspace_spaces",
			"slide_title": _("Space Types"),
			"slide_desc": _("Select the types of spaces you offer."),
			"slide_icon": "fa-solid fa-th-large",
			"slide_order": 32,
			"fields": [
				{
					"fieldtype": "Check",
					"fieldname": "type_hot_desk",
					"label": _("Hot Desk"),
					"default": 1,
				},
				{
					"fieldtype": "Check",
					"fieldname": "type_dedicated_desk",
					"label": _("Dedicated Desk"),
					"default": 1,
				},
				{
					"fieldtype": "Check",
					"fieldname": "type_private_office",
					"label": _("Private Office"),
					"default": 1,
				},
				{
					"fieldtype": "Check",
					"fieldname": "type_meeting_room",
					"label": _("Meeting Room"),
					"default": 1,
				},
				{
					"fieldtype": "Check",
					"fieldname": "type_event_space",
					"label": _("Event Space"),
				},
				{
					"fieldtype": "Check",
					"fieldname": "type_virtual_office",
					"label": _("Virtual Office"),
				},
			],
		},
		{
			"slide_name": "arkspace_plan",
			"slide_title": _("First Membership Plan"),
			"slide_desc": _("Create your first membership plan to get started."),
			"slide_icon": "fa-solid fa-id-card",
			"slide_order": 33,
			"fields": [
				{
					"fieldtype": "Data",
					"fieldname": "plan_name",
					"label": _("Plan Name"),
					"default": _("Basic Hot Desk"),
					"reqd": 1,
				},
				{
					"fieldtype": "Select",
					"fieldname": "plan_type",
					"label": _("Plan Type"),
					"options": "Hot Desk\nDedicated Desk\nPrivate Office\nMeeting Room\nEvent Space\nVirtual Office",
					"default": "Hot Desk",
					"reqd": 1,
				},
				{
					"fieldtype": "Currency",
					"fieldname": "monthly_price",
					"label": _("Monthly Price"),
					"reqd": 1,
					"default": 1000,
				},
				{
					"fieldtype": "Int",
					"fieldname": "included_credits",
					"label": _("Included Credits"),
					"default": 20,
				},
			],
		},
	]


@frappe.whitelist()
def setup_arkspace_config(args):
	"""Process setup wizard data and create initial configuration.

	Called by the setup wizard framework with collected slide data.
	"""
	if not args:
		return

	if isinstance(args, str):
		import json
		args = json.loads(args)

	# 1. Update ARKSpace Settings
	_update_settings(args)

	# 2. Create Branches
	_create_branches(args)

	# 3. Create Space Types
	_create_space_types(args)

	# 4. Create First Membership Plan
	_create_first_plan(args)


def _update_settings(args):
	"""Update ARKSpace Settings with wizard values."""
	settings = frappe.get_single("ARKSpace Settings")

	company = args.get("company_name")
	if company and frappe.db.exists("Company", company):
		settings.company = company

	if args.get("default_currency"):
		settings.default_currency = args["default_currency"]
	if args.get("timezone"):
		settings.timezone = args["timezone"]

	# Skip save if mandatory company is still missing (will be set on first use)
	if not settings.company:
		return

	settings.save(ignore_permissions=True)


def _create_branches(args):
	"""Create branches from wizard input."""
	for key in ["branch_1", "branch_2", "branch_3"]:
		name = args.get(key)
		if name and not frappe.db.exists("Branch", name):
			frappe.get_doc({
				"doctype": "Branch",
				"branch": name,
			}).insert(ignore_permissions=True)


def _create_space_types(args):
	"""Create selected space types."""
	type_map = {
		"type_hot_desk": "Hot Desk",
		"type_dedicated_desk": "Dedicated Desk",
		"type_private_office": "Private Office",
		"type_meeting_room": "Meeting Room",
		"type_event_space": "Event Space",
		"type_virtual_office": "Virtual Office",
	}
	for field, type_name in type_map.items():
		if args.get(field) and not frappe.db.exists("Space Type", type_name):
			frappe.get_doc({
				"doctype": "Space Type",
				"type_name": type_name,
			}).insert(ignore_permissions=True)


def _create_first_plan(args):
	"""Create the first membership plan."""
	plan_name = args.get("plan_name")
	if not plan_name or frappe.db.exists("Membership Plan", {"plan_name": plan_name}):
		return

	frappe.get_doc({
		"doctype": "Membership Plan",
		"plan_name": plan_name,
		"plan_type": args.get("plan_type", "Hot Desk"),
		"monthly_price": args.get("monthly_price", 1000),
		"included_credits": args.get("included_credits", 20),
		"is_active": 1,
	}).insert(ignore_permissions=True)
