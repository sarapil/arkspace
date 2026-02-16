# Copyright (c) 2026, ARKSpace Team and contributors
# For license information, please see license.txt

"""ARKSpace Integrations — API Endpoints
واجهة برمجة التكاملات
"""

import frappe
from frappe import _


@frappe.whitelist()
def get_unpaid_invoices(member=None):
	"""Proxy to billing.get_unpaid_invoices."""
	from arkspace.arkspace_integrations.billing import get_unpaid_invoices as _get
	return _get(member)


@frappe.whitelist()
def get_integration_status():
	"""Return which integrations are available on this site."""
	installed = frappe.get_installed_apps()
	return {
		"erpnext": "erpnext" in installed,
		"hrms": "hrms" in installed,
		"payments": "payments" in installed,
	}
