# Workspace Lead

A Workspace Lead tracks a potential customer through the sales pipeline from initial contact to conversion.

## Pipeline

```
New → Contacted → Tour Scheduled → Negotiating → Converted
                                               ↘ Lost
```

## Key Fields

- **Lead Name**: Full name of the prospect
- **Email / Phone**: Contact information
- **Source**: Website, Walk-in, Referral, Social Media, Event, Partner
- **Status**: Current pipeline position
- **Interested Plan**: Membership plan of interest
- **Budget**: Prospect's budget range
- **Team Size**: Number of desks needed

## Actions

- **Schedule Tour**: Creates a Workspace Tour and updates status
- **Convert to Customer**: Creates ERPNext Customer record, marks as Converted

## Tips

- Update status as you progress through the pipeline
- Schedule tours early — they significantly improve conversion
- After conversion, create a Membership for the new customer
