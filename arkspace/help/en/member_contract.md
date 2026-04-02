# Member Contract

A Member Contract is a legal agreement between the space operator and a member, generated from customizable templates.

## Workflow

```
Draft → Active → Expired
            ↘ Terminated
            ↘ Cancelled
```

## Key Fields

- **Customer**: The contracting member
- **Contract Type**: Membership, Booking, Office Rental, Event Space, Virtual Office
- **Contract Template**: Jinja template for auto-populating terms
- **Start/End Date**: Contract validity period
- **Contract Value**: Total contract amount
- **Legal Documents**: Attached member documents (ID, passport, etc.)
- **Member Signature**: Digital signature field
- **Witness / Company Signatory**: Additional signatories

## Template Rendering

Click **Render Terms** to auto-populate the contract body from a template. Templates support:
- Member details (name, email, phone)
- Space information (name, type, floor)
- Plan data (pricing, benefits)
- Dates and financials

Templates support Arabic, English, and Bilingual formats.

## Tips

- Always attach required Legal Documents before submitting
- Submitted contracts are immutable for legal compliance
- Use Print Format for professional output
