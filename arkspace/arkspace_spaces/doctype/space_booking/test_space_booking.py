# Copyright (c) 2026, ARKSpace Team and Contributors
# See license.txt

import frappe
from arkspace.tests.compat import ARKSpaceTestCase
from frappe.utils import now_datetime, add_to_date, flt


class TestSpaceBooking(ARKSpaceTestCase):
	"""Test cases for Space Booking DocType."""

	def setUp(self):
		"""Create test prerequisites."""
		self.space = self._get_or_create_space()
		self.customer = self._get_or_create_customer()

	def _get_or_create_space(self):
		spaces = frappe.get_all("Co-working Space", filters={"status": "Available"}, limit=1)
		if spaces:
			return frappe.get_doc("Co-working Space", spaces[0].name)

		# Create prerequisites
		if not frappe.db.exists("Space Type", "Test Desk"):
			frappe.get_doc({"doctype": "Space Type", "type_name": "Test Desk"}).insert()
		if not frappe.db.exists("Branch", "Test Branch"):
			frappe.get_doc({"doctype": "Branch", "branch": "Test Branch"}).insert()

		return frappe.get_doc({
			"doctype": "Co-working Space",
			"space_name": "Test Space for Booking",
			"space_type": "Test Desk",
			"branch": "Test Branch",
			"capacity": 10,
			"hourly_rate": 50,
			"daily_rate": 300,
			"monthly_rate": 5000,
		}).insert()

	def _get_or_create_customer(self):
		if frappe.db.exists("Customer", "Test Booking Customer"):
			return frappe.get_doc("Customer", "Test Booking Customer")
		return frappe.get_doc({
			"doctype": "Customer",
			"customer_name": "Test Booking Customer",
			"customer_type": "Individual",
		}).insert()

	def _make_booking(self, **kwargs):
		start = add_to_date(now_datetime(), days=1)
		end = add_to_date(start, hours=3)
		defaults = {
			"doctype": "Space Booking",
			"space": self.space.name,
			"member": self.customer.name,
			"booking_type": "Hourly",
			"start_datetime": start,
			"end_datetime": end,
			"rate": self.space.hourly_rate or 50,
		}
		defaults.update(kwargs)
		return frappe.get_doc(defaults)

	def test_create_booking(self):
		"""Test basic booking creation."""
		booking = self._make_booking()
		booking.insert()
		self.assertTrue(booking.name)
		self.assertTrue(booking.name.startswith("BK-"))
		self.assertEqual(booking.status, "Pending")

	def test_duration_calculation(self):
		"""Test automatic duration calculation."""
		start = add_to_date(now_datetime(), days=2)
		end = add_to_date(start, hours=4)
		booking = self._make_booking(start_datetime=start, end_datetime=end)
		booking.insert()
		self.assertAlmostEqual(flt(booking.duration_hours, 1), 4.0, places=1)

	def test_amount_calculation_hourly(self):
		"""Test hourly billing calculation."""
		start = add_to_date(now_datetime(), days=3)
		end = add_to_date(start, hours=2)
		booking = self._make_booking(
			start_datetime=start,
			end_datetime=end,
			booking_type="Hourly",
			rate=100,
		)
		booking.insert()
		self.assertEqual(flt(booking.total_amount, 2), 200.0)

	def test_discount_calculation(self):
		"""Test discount applied correctly."""
		start = add_to_date(now_datetime(), days=4)
		end = add_to_date(start, hours=2)
		booking = self._make_booking(
			start_datetime=start,
			end_datetime=end,
			rate=100,
			discount_percent=10,
		)
		booking.insert()
		# total = 200, discount 10% => net = 180
		self.assertEqual(flt(booking.net_amount, 2), 180.0)

	def test_submit_changes_status(self):
		"""Test that submitting sets status to Confirmed."""
		booking = self._make_booking(
			start_datetime=add_to_date(now_datetime(), days=5),
			end_datetime=add_to_date(now_datetime(), days=5, hours=2),
		)
		booking.insert()
		booking.submit()
		self.assertEqual(booking.status, "Confirmed")

	def test_cancel_changes_status(self):
		"""Test that cancelling sets status to Cancelled."""
		booking = self._make_booking(
			start_datetime=add_to_date(now_datetime(), days=6),
			end_datetime=add_to_date(now_datetime(), days=6, hours=2),
		)
		booking.insert()
		booking.submit()
		booking.cancel()
		self.assertEqual(booking.status, "Cancelled")

	def test_invalid_time_range(self):
		"""Test that end before start is rejected."""
		start = add_to_date(now_datetime(), days=7)
		end = add_to_date(start, hours=-1)
		booking = self._make_booking(start_datetime=start, end_datetime=end)
		self.assertRaises(frappe.ValidationError, booking.insert)

	def test_overlapping_booking_check(self):
		"""Test that overlapping bookings on same space are caught."""
		start = add_to_date(now_datetime(), days=10)

		b1 = self._make_booking(
			start_datetime=start,
			end_datetime=add_to_date(start, hours=3),
		)
		b1.insert()
		b1.submit()

		b2 = self._make_booking(
			start_datetime=add_to_date(start, hours=1),
			end_datetime=add_to_date(start, hours=4),
		)
		self.assertRaises(frappe.ValidationError, b2.insert)

	def test_daily_booking_type(self):
		"""Test daily booking type calculation."""
		start = add_to_date(now_datetime(), days=15)
		end = add_to_date(start, days=1)
		booking = self._make_booking(
			start_datetime=start,
			end_datetime=end,
			booking_type="Daily",
			rate=300,
		)
		booking.insert()
		self.assertGreater(flt(booking.total_amount), 0)
