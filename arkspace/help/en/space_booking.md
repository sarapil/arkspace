# Space Booking

A Space Booking records the reservation of a co-working space for a member.

## Workflow

```
Pending → Confirmed → Checked In → Checked Out
                   ↘ Cancelled
                   ↘ No Show
```

## Key Fields

- **Space**: The co-working space being booked
- **Customer**: The member making the booking
- **Booking Type**: Hourly, Daily, or Monthly
- **Start/End DateTime**: Booking period
- **Status**: Current booking status
- **Add-on Amenities**: Optional extra services

## Actions

- **Submit**: Confirms the booking (auto-creates Sales Invoice)
- **Check In**: Marks member as present, updates space to Occupied
- **Check Out**: Completes the booking, frees the space
- **Cancel**: Cancels the booking (creates credit note)

## Tips

- Use the **Floor Plan** page for visual booking
- **Bulk operations** available in list view for front desk efficiency
- No-shows are auto-detected after 2 hours
- Overdue bookings are auto-checked out
