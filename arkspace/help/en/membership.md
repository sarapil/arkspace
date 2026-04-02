# Membership

A Membership represents a member's subscription to a plan with included benefits and credit allocation.

## Workflow

```
Draft → Active → Expired
            ↘ Suspended
            ↘ Cancelled
```

## Key Fields

- **Customer**: The subscribing member
- **Membership Plan**: Selected plan with pricing and benefits
- **Billing Cycle**: Monthly, Quarterly, or Yearly
- **Start/End Date**: Subscription period
- **Auto Renew**: Toggle for automatic renewal
- **Status**: Current membership state

## Automatic Features

- **Credit Wallet**: Created automatically on submit with allocated credits
- **Auto-Renewal**: Daily task renews eligible memberships before expiry
- **Expiry Reminders**: Email notifications at 7 days and 1 day before expiry
- **Billing**: Sales Invoice auto-created on submit, credit note on cancel

## Member Dashboard

The Member Dashboard API provides a unified view of:
- Active memberships
- Upcoming and recent bookings
- Credit wallet balance
- Usage statistics
