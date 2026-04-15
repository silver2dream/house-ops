# Visit Mode — Visit Preparation and Post-Visit Recording

<!-- Read modes/_shared.md and the relevant report before executing this mode.
     Load country_config from config/country/{country}.yml. -->

---

## Overview

Two sub-modes:
1. **Pre-visit:** Generate a visit checklist + negotiation strategy from an existing evaluation report
2. **Post-visit:** Record findings and update tracker status

---

## Sub-mode 1: Pre-Visit Preparation

### Input

User provides a report number (e.g., "prepare visit for 001").

1. Search `reports/` for a file starting with `{###}-`
2. If not found → "Report {###} not found. Please verify the report number." and stop
3. Read the report file fully — especially the red flags and viewing questions sections

---

### Section A: Universal Checklist

Read the universal checklist from `country_config.visit_checklist.universal`. Present each item using its local-language label and check description:

| # | Item | What to check |
|---|------|--------------|
| 1 | {item label from config} | {check description from config} |
| 2 | {item label from config} | {check description from config} |
| ... | ... | ... |

Example: if country is Taiwan, items include "漏水痕跡" with checks for "天花板、牆面...". If Ireland, items include "Dampness" with checks for "walls, ceilings, window sills..."

---

### Section B: Property-Specific Checklist

Derived from the report's red flags section. For each red flag in the report:

| # | Source issue | What to do at viewing |
|---|-------------|----------------------|
| 1 | {red flag from report} | {specific inspection instruction} |

For building-risk-related flags, use the `viewing_action` from the matching entry in `country_config.building_risks`. For other red flags, generate appropriate inspection instructions based on the issue type.

---

### Section C: Negotiation Strategy

Read the report's price analysis section for price vs market data.

| Item | Amount | Notes |
|------|--------|-------|
| Listing price | {listing price} | Current |
| Market reference median | {median} | Recent period, same area |
| Suggested first offer | {suggested offer} | See logic below |
| Walk-away ceiling | {walk-away} | Budget max or listing price * X%, whichever is lower |
| Leverage points | {leverage points} | e.g., days on market, repair needs |

**Suggested first offer logic:**
- If listing is at or below 5% above market reference median: offer the median directly
- If listing is >5% above: offer 5% below listing price
- Never exceed `budget.rent_max` (rent) or `budget.buy_max` (buy)

**Negotiation notes:** List any leverage points from the report (days on market, flagged issues that require repair, building risks) that justify a lower offer.

---

### Section D: Logistics Reminder

Read logistics guidance from `country_config.visit_checklist.logistics`. Present as a reminder list.

If the country config does not define logistics, use this universal fallback:
- Bring: ID, camera/phone for photos
- Recommended visit time: morning or midday (check natural light; avoid staged evening lighting)
- Bring a measuring tape for key rooms
- Check: waste collection schedule, parking rules, neighbor demographics

---

## Sub-mode 2: Post-Visit Record

### Trigger

User has completed the viewing and wants to record findings.

### Present template for user to fill in:

Generate the template dynamically using the universal checklist items from `country_config.visit_checklist.universal`:

```markdown
## Post-Visit Record — Report {###}

**Date visited:** {YYYY-MM-DD}
**Overall impression (1-5):**

**Checklist notes:**
- [ ] {item 1 from config}: 
- [ ] {item 2 from config}: 
- [ ] {item 3 from config}: 
...
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
   - Append visit summary to notes column

2. **If decision = pass:**
   - Update status to `Pass`
   - Note the reason in notes column

3. **If decision = proceed:**
   - Suggest next steps: make an offer → update status to `Offer`, or schedule another visit
   - Can use `compare` mode to re-evaluate against other candidates before deciding
