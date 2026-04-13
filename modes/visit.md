# Visit Mode — Visit Preparation and Post-Visit Recording

<!-- Read modes/_shared.md and the relevant report before executing this mode. -->

---

## Overview

Two sub-modes:
1. **Pre-visit:** Generate a visit checklist + negotiation strategy from an existing evaluation report
2. **Post-visit:** Record findings and update tracker status

---

## Sub-mode 1: Pre-Visit Preparation

### Input

User provides a report number (e.g., "prepare visit for 001" or "visit checklist 003").

1. Search `reports/` for a file starting with `{###}-`
2. If not found → "Report {###} not found — please check the report number." and stop
3. Read the report file fully — especially the concerns list and viewing questions sections

---

### Section A: Universal Checklist

Items to check at every viewing regardless of listing type:

| # | Item | What to check |
|---|------|--------------|
| 1 | Dampness/moisture | Walls, ceilings, around windows — very common in Ireland. Look for stains, bubbling paint, musty smell. Check behind furniture if possible. |
| 2 | Phone signal | Test in all rooms — basements and ground floors of older buildings can be dead zones. |
| 3 | Natural light | Open all curtains/blinds, check each room. Note which direction rooms face (south-facing is best). |
| 4 | Noise | Stand quietly and listen: neighbours, traffic, proximity to pubs/late-night venues, flight path (near Dublin Airport). |
| 5 | BER cert | Ask to see the certificate. Check that the rating matches what was listed. Note the BER number for verification. |
| 6 | Heating system | Gas/oil/heat pump/electric storage? Age of boiler? When was it last serviced? Is there a service history? |
| 7 | Plumbing | Run all taps simultaneously, flush all toilets. Check water pressure. Look under sinks for leaks. |
| 8 | Windows | Double or triple glazed? Any condensation between panes? Do they all open and close properly? Draughts? |
| 9 | Broadband | Check actual speed on your phone. Is fibre available? Check comreg.ie/broadband-map for coverage. |
| 10 | Parking | On-street? Dedicated space? Disc parking zone? Permit required? How busy is the street in the evening? |
| 11 | Garden/outdoor space | North or south facing? Condition of boundary walls/fences? Drainage issues? Overlooked by neighbours? |
| 12 | Management company (if apartment) | Annual fees? Sinking fund balance? Any recent or upcoming special levies? Minutes of last AGM available? |

---

### Section B: Property-Specific Checklist

Derived from the report's concerns list. For each concern in the report:

| # | Source Concern | What to do at viewing |
|---|---------------|----------------------|
| 1 | {concern from report} | {specific inspection instruction} |

Conversion rules:
- Pyrite risk → "Ask about pyrite testing. Check if the property is in a known affected area. Request IS 398 categorisation report. Look for cracking in internal walls and external render."
- Mica risk → "Check if the property is in Donegal/Mayo affected areas. Request mica testing results (IS 465). Look for cracking patterns in blockwork."
- Pre-1970s building → "Asbestos risk. Has an asbestos survey been done? Do not disturb any suspect materials. Check soffits, boiler flues, artex ceilings."
- No BER → "Why is there no BER? A BER cert is legally required for sale/rental. Do not proceed without one."
- Unauthorised extension → "Check planning permission history on the local council's planning portal. Request commencement notice and compliance certificate."
- Dampness indicators → "Focus inspection on: basement/lower ground, gable walls, around chimneys, bathroom ceiling. Ask when the roof was last repaired."
- Old wiring → "Check fuse board — is it a modern consumer unit with RCD protection? Ask when the electrics were last certified."
- Flat roof sections → "Flat roofs have a limited lifespan (15-20 years). Ask when it was last felted/repaired. Check for ponding water signs."

---

### Section C: Negotiation Strategy

Read the report's price analysis section for price vs market data.

| Item | Amount | Notes |
|------|--------|-------|
| Asking price | {listing price} | Current listing |
| PPR median (area) | {median} | Last 12 months, similar properties in area |
| Suggested first offer | {suggested offer} | Typically 5-10% below asking, informed by PPR data |
| Walk-away ceiling | {walk-away} | Asking price or budget limit, whichever is lower |
| Leverage points | {leverage points} | e.g., time on market, issues found, BER rating |

**Suggested first offer logic:**
- If listing is at or below PPR median: offer PPR median directly (fair value)
- If listing is up to 10% above PPR median: offer 5% below asking price
- If listing is >10% above PPR median: offer at PPR median and negotiate up
- Never exceed `budget.rent_max` (rent) or `budget.buy_max` (buy)

**Negotiation notes:** List any leverage points from the report (days on market, flagged issues that require repair, poor BER rating, no management company sinking fund, etc.) that justify a lower offer. In the Irish market, offers are typically 0-10% below asking price depending on demand in the area.

---

### Section D: Logistics Reminder

- **Bring:** Photo ID, phone (for photos/video), a friend or family member if possible
- **Visit during daylight** — check natural light, see the neighbourhood properly
- **Bring a measuring tape** for key rooms (listed m² may include common areas in apartments)
- **Check:** Bin collection day and provider, flooding history at floodinfo.ie, local amenities (shops, schools, GP, pharmacy)
- **If buying:** Arrange a chartered surveyor/structural engineer for a second visit before going sale-agreed. Budget EUR 300-500 for a structural survey.
- **If renting:** Photograph everything before signing — this protects your deposit. Check if the property is in an RPZ (Rent Pressure Zone).

---

## Sub-mode 2: Post-Visit Record

### Trigger

User has completed the viewing and wants to record findings.

### Present template for user to fill in:

```markdown
## Post-Visit Record — Report {###}

**Date visited:** {YYYY-MM-DD}
**Overall impression (1–5):** 

**Checklist notes:**
- [ ] Dampness/moisture: 
- [ ] Phone signal: 
- [ ] Natural light: 
- [ ] Noise: 
- [ ] BER cert: 
- [ ] Heating system: 
- [ ] Plumbing: 
- [ ] Windows: 
- [ ] Broadband: 
- [ ] Parking: 
- [ ] Property-specific item 1: 
- [ ] Property-specific item 2: 

**Negotiation notes:**
- Offered: 
- Counter: 
- Status: 

**Deal-breakers found:** (none / list them)

**Decision:** proceed / pass

**Notes:** 
```

### After user fills record:

1. **Update tracker.md directly** (status + notes column, direct edit allowed per CLAUDE.md):
   - Find the row with matching report number
   - Status: `Visit` → `Visited`
   - Append visit summary to notes column (e.g., "Viewed 2026-04-10, impression 4/5, no damp issues")

2. **If decision = pass:**
   - Update status to `Pass`
   - Note the reason in notes column

3. **If decision = proceed:**
   - Suggest next steps: make an offer → update status to `Offer`, or schedule another visit
   - If buying: strongly recommend arranging a structural survey before going sale-agreed
   - Can use `compare` mode to re-evaluate against other candidates before deciding
