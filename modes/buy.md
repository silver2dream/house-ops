# Buy Mode — Purchase Property Evaluation (Ireland)

<!-- Read modes/_shared.md and modes/_profile.md before executing this mode. -->

---

## Overview

Full evaluation of a purchase listing in Ireland. Two phases:
- **Phase 1** — Quick filter: price, size, BER
- **Phase 2** — Full evaluation: extraction, price/loan analysis, commute, building risks, scoring, report

Buy mode extends rent mode with mortgage calculations, PPR (Property Price Register) sale price comparisons, and buyer_type-specific modules (FTB vs non-FTB).

---

## Section 1: Input Handling

### URL input
1. `playwright-cli goto {url}` to navigate to the URL
2. `playwright-cli snapshot` to read the page
3. **Verify active:** listing title + price + contact section present. If only nav/footer → "This listing is no longer available." and stop.
4. **NEVER** use WebSearch or WebFetch alone for liveness checks. Always use `playwright-cli`.

### Pasted text
Proceed directly to Phase 1 using the provided content.

---

## Section 2: Phase 1 Quick Filter

Read `config/profile.yml`. If any fail → `Skipped: {reason} ({actual} vs limit {limit})`, no full report.

| Check | Profile field | Fail condition |
|-------|---------------|----------------|
| Price | `budget.buy_max` | Asking price > buy_max (EUR) |
| Size | `property.size_min` | m² < size_min |
| BER | `property.ber_min` | BER rating worse than ber_min (if set) |

Also check `modes/_profile.md` deal_breakers. If any match → Skip.

If all pass → `Phase 1 passed — proceeding to full evaluation.`

---

## Section 3: Data Extraction

| Field | Notes |
|-------|-------|
| Title | Full listing title |
| Address | Area + street + Eircode if available |
| BER | Rating (A1-G), BER number if available |
| Size | m² |
| Bedrooms/Bathrooms | e.g., 3 bed, 2 bath |
| Asking price | EUR |
| Property type | Detached / Semi-detached / Terraced / Apartment / Duplex / Bungalow / End-of-terrace |
| New build or second-hand | New / Second-hand |
| Parking | Yes / No / On-street |
| Management fees | If apartment (per year) |
| Management company | Name if apartment |
| Planning history | Any noted extensions, conversions |
| Floor area breakdown | If available |
| Estate agent | Agent name (PSRA licensed) |
| Days on market | If available |
| Platform | Portal name (e.g., Daft.ie, MyHome.ie, PropertyPal) |

---

## Section 4: Price Analysis

1. **Price per m²:** `asking price / m²`
2. **Market comparison:** Use PPR (propertypriceregister.ie) data for same area, comparable type, last 6 months. Get median EUR/m².
3. **Premium/discount:** `(listing EUR/m² - median EUR/m²) / median EUR/m² x 100%`
4. **Stamp duty:** 1% on first EUR 1,000,000 + 2% on balance above EUR 1,000,000
5. **Negotiation room:** If listing >5% above median → estimate negotiation room

| Item | Value |
|------|-------|
| Asking price | EUR {price} |
| Size | {size} m² |
| Price per m² | EUR {per_sqm}/m² |
| Area median EUR/m² (PPR, last 6 months) | EUR {median}/m² |
| Relative to market | +/-{pct}% |
| Stamp duty | EUR {stamp_duty} |
| Negotiation room estimate | {note} |

---

## Section 5: Building Risk Assessment

Assess the following Ireland-specific property risks:

| Risk factor | Condition | Flag |
|-------------|-----------|------|
| Asbestos | Pre-1970s build | Warning: Pre-1970s property — asbestos risk in insulation, floor tiles, roof materials. Recommend asbestos survey before purchase. (Add to red flags, level Medium) |
| Pyrite | Certain areas of North Dublin, parts of Leinster (Meath, Offaly, Carlow) | Warning: Property in known pyrite-affected area. Check if pyrite remediation has been done. Request IS 398-1:2013 classification. (Add to red flags, level High) |
| Mica/defective blocks | Donegal, Mayo, Clare, Sligo, Limerick | Warning: Property in area affected by defective concrete blocks (mica/pyrite). Check if property is part of the Defective Concrete Blocks Grant Scheme. (Add to red flags, level High) |
| No BER certificate | BER not listed or expired | Warning: No valid BER certificate. Legally required for sale. Seller must provide before closing. (Add to red flags, level Medium) |
| Unauthorised extensions | Visible extensions not matching planning records | Warning: Potential unauthorised development. Request planning search from local authority. May affect mortgage approval. (Add to red flags, level High) |
| Septic tank | Rural properties | Note: Verify septic tank registration and compliance with EPA standards. (Add to red flags, level Low) |

---

## Section 6: Mortgage Calculation

Calculate for all applicable scenarios. Show monthly payment and total interest over the mortgage term.

**Formula:** Monthly payment = P x [r(1+r)^n] / [(1+r)^n - 1]
where P = loan principal, r = annual rate / 12, n = number of monthly payments

Default term: 30 years (360 months) unless otherwise specified.

**Central Bank of Ireland rules:**
- First-time buyer (FTB): max 4x gross annual income, 10% deposit
- Non-FTB (mover/second-time): max 3.5x gross annual income, 20% deposit

Scenarios:

| Scenario | Rate | Deposit | Loan | Monthly payment | 30-year total interest |
|----------|------|---------|------|-----------------|----------------------|
| FTB Fixed 10% | 3.2% | {price x 10%} | {price x 90%} | {calc} | {calc} |
| FTB Variable 10% | 3.8% | {price x 10%} | {price x 90%} | {calc} | {calc} |
| Non-FTB Fixed 20% | 3.2% | {price x 20%} | {price x 80%} | {calc} | {calc} |
| Non-FTB Variable 20% | 3.8% | {price x 20%} | {price x 80%} | {calc} | {calc} |

Show only the rows relevant to the user's `buyer_type`:
- `first_time`: show FTB rows only
- `upgrader`: show Non-FTB rows only
- If unclear: show all rows

**Help to Buy (HTB):** If `buyer_type = first_time` AND property is a new build:
- Add HTB row: deposit reduced by up to EUR 30,000 (10% of purchase price up to EUR 500,000)
- Show adjusted deposit and loan amounts

| Scenario | Rate | Deposit (after HTB) | Loan | Monthly payment | 30-year total interest |
|----------|------|---------------------|------|-----------------|----------------------|
| FTB Fixed + HTB | 3.2% | {deposit - HTB} | {price - adjusted deposit} | {calc} | {calc} |

**First Home Scheme (FHS):** If `buyer_type = first_time` AND new build AND price <= EUR 500,000:
- Note: Shared equity of up to 30% available, reducing the mortgage required
- Show FHS row with reduced mortgage amount

Flag any row where monthly payment > `budget.monthly_payment_max` with a Warning.

Also check: does the required loan exceed the Central Bank income multiple?
- FTB: loan > 4 x `finance.annual_income` → flag as Warning: "Loan exceeds Central Bank lending limit of 4x income"
- Non-FTB: loan > 3.5 x `finance.annual_income` → flag as Warning: "Loan exceeds Central Bank lending limit of 3.5x income"

---

## Section 7: Commute Calculation

Same as rent.md. From listing address to `user.commute_origin`. Estimate public transport (Luas, DART, Dublin Bus, Irish Rail) + walking time. Note driving time. Compare to `user.commute_max_minutes`.

| Transport mode | Estimated time | Notes |
|---------------|----------------|-------|
| Luas | X min | Nearest stop: {stop}, {line} line |
| DART | X min | Nearest station: {station} |
| Bus | X min | Route(s): {route} |
| Driving | X min | Approximate, traffic-dependent |

---

## Section 8: Scoring

Score each dimension 0-5. Apply BUY weights.

| Dimension | Weight | Key factors |
|-----------|--------|-------------|
| Price reasonableness | 35% | EUR/m² vs market median (PPR), monthly payment vs monthly_payment_max; if FTB: HTB/FHS eligibility; days on market; stamp duty impact |
| Space and layout | 20% | Size, bedroom/bathroom count, natural light, storage, garden/outdoor space, parking |
| Location and amenities | 20% | Public transport proximity, lifestyle priorities, school catchment, neighbourhood trajectory, local services |
| Property condition | 15% | BER rating, property type, age, condition, management company (if apt), legal status, planning compliance |
| Risk / potential | 10% | Building risks (asbestos/pyrite/mica), BER issues, planning concerns, days on market; if upgrader: CGT implications |

**Upgrader supplement** (if `buyer_type = upgrader`):
- Calculate CGT assessment for current property:
  - If selling PPR (principal private residence): CGT exempt — no tax on gain
  - If selling investment property: 33% CGT on gain
  - Note: must have occupied as PPR for entire ownership period for full exemption; partial exemption available for partial occupation
- Include in red flags and factor into Risk / potential score

**Final score:** `(D1 x 0.35 + D2 x 0.20 + D3 x 0.20 + D4 x 0.15 + D5 x 0.10)`

**Score interpretation:**
- >= 4.0: **Recommended for viewing**
- 3.5-3.9: **Worth considering**
- < 3.5: **Recommend skipping**

---

## Section 9: Report Generation

### 9a: Determine report number
Read `reports/` filenames. Find highest `{###}`. New = max + 1, zero-padded. Start at `001` if empty.

### 9b: Build filename
`{###}-{area}-{road-slug}-{YYYY-MM-DD}.md`
- `{area}`: area/neighbourhood name, lowercase, hyphenated (e.g., `rathmines`, `drumcondra`, `dun-laoghaire`, `sandyford`, `lucan`, `maynooth`, `blackrock`, `dalkey`)
- `{road-slug}`: road/street name, lowercase, hyphenated (e.g., `ormond-quay`, `merrion-rd`, `griffith-ave`). If ambiguous → `road-{4-char-hex-of-address-hash}`

### 9c: Write report to `reports/{filename}`

```markdown
# {###} | {area} {road}

| Field | Value |
|-------|-------|
| Type | Purchase |
| Score | {score}/5 — {interpretation} |
| URL | {url} |
| Asking price | EUR {price} | Size | {size} m² | Layout | {bedrooms} bed, {bathrooms} bath |
| BER | {ber} | Property type | {type} | Platform | {portal} |

**URL:** {url}
**Score:** {score}/5
**Type:** buy
**Status:** Evaluated
**Verification:** confirmed

## Price Analysis

{price table}
{price prose}

## Mortgage Calculation

{mortgage table}
{mortgage prose: recommendation based on buyer_type; note if any scenario exceeds monthly_payment_max or Central Bank limits; note HTB/FHS eligibility}

## Commute Estimate

{commute table}
{commute prose}

## Dimension Scores

| Dimension | Score | Key factors |
|-----------|-------|-------------|
| Price reasonableness | {d1}/5 | {factors} |
| Space and layout | {d2}/5 | {factors} |
| Location and amenities | {d3}/5 | {factors} |
| Property condition | {d4}/5 | {factors} |
| Risk / potential | {d5}/5 | {factors} |
| **Overall** | **{total}/5** | |

{prose: recommendation rationale}

## Red Flags

| # | Issue | Risk level |
|---|-------|------------|
| 1 | {issue} | High/Medium/Low |

{prose: explanation of significant risks}

## Viewing Questions

| # | Question | Category |
|---|----------|----------|
| 1 | {question} | Structure/Utilities/Environment/Legal/Title |
```

---

## Section 10: TSV Output

Write `batch/tracker-additions/{num}-{slug}.tsv`:
```
{num}\t{YYYY-MM-DD}\t{portal}\t{address}\tBuy\tEUR {price}\t{size} m²\t{score}/5\tEvaluated\t[{num}](reports/{report_filename})\t{one-line note}
```

---

## Section 11: Merge Tracker

Run: `node merge-tracker.mjs`
