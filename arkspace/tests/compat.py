# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

"""ARKSpace — Test Compatibility Layer

Provides a single import for test base class that works on both
Frappe v15 (FrappeTestCase) and v16+ (IntegrationTestCase).
"""

try:
    # Frappe v16+
    from frappe.tests import IntegrationTestCase as ARKSpaceTestCase
except ImportError:
    # Frappe v15
    from frappe.tests.utils import FrappeTestCase as ARKSpaceTestCase

__all__ = ["ARKSpaceTestCase"]
