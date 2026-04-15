# Buy Mode — Purchase Property Evaluation

<!-- Read modes/_shared.md and modes/_profile.md before executing this mode.
     Load country_config from config/country/{country}.yml. -->

---

## Overview

Full evaluation of a purchase listing. Two phases:
- **Phase 1** — Quick filter: price, size, and any country-specific criteria
- **Phase 2** — Full evaluation: extraction, price/loan analysis, commute, building risks, scoring, report

Buy mode extends rent mode with loan calculations, market reference sale prices, and buyer_type-specific modules.

---

## Section 1: Input Handling

### URL input
1. `agent-browser open {url}`
2. `agent-browser snapshot -i`
3. **Verify active:** listing title + price + contact section present. If only nav/footer → output the inactive listing message from `country_config.report_labels.inactive_listing` and stop.
4. **NEVER** use WebSearch or WebFetch alone for liveness checks.

### Pasted text
Proceed directly to Phase 1 using the provided content.

---

## Section 2: Phase 1 Quick Filter

Read `config/profile.yml`. If any check fails → `Skipped: {reason} ({actual} vs limit {limit})`, no full report.

Standard checks:

| Check | Profile field | Fail condition |
|-------|---------------|----------------|
| Price | `budget.buy_max` | Total price > buy_max |
| Size | `property.size_min` | Size < size_min (using area unit from `country_config.market.area_unit`) |

Additional checks — apply if the profile field exists:
- `property.floor_min`: Floor < floor_min
- `property.age_max`: Age > age_max
- `property.ber_min`: Energy rating below minimum

Also check `modes/_profile.md` deal_breakers. If any match → Skip.

If all pass → output the Phase 1 pass message from `country_config.report_labels.phase1_pass`.

---

## Section 3: Data Extraction

Extract data fields from the listing page. Use `country_config.listing_fields` for field names and local labels. Standard fields to extract:

| Field key | Notes |
|-----------|-------|
| `title` | Full listing title |
| `address` | Area + road/street + floor/unit |
| `floor` / `total_floors` | Floor / total floors |
| `size` | Size in the country's area unit (note any breakdown: main area, shared area, etc.) |
| `layout` | Layout (bedrooms, bathrooms, etc.) |
| `total_price` | Total purchase price (in country's currency) |
| `parking` | Parking included? Separate price? |
| `management_fee` | Monthly management/service charge |
| `building_age` | Building age or year built |
| `building_type` | Property type (from `country_config.property_types`) |
| `elevator` | Yes/No |
| `land_ownership` | Land/property ownership type (if applicable in this country) |
| `owner_or_agent` | Owner or agent |
| `listing_date` | Listing date |
| `days_on_market` | Days on market (if available) |
| `platform` | Portal name |

Not all fields exist in every country. Extract what is available.

---

## Section 4: Price Analysis

1. **Price per area unit:** Total price / size (using `country_config.market.price_per_area_label`)
2. **Market comparison:** Use the market reference source from `country_config.market_reference.price_register` for the same area, comparable type, within the lookback period. Get median price per area unit.
3. **Premium/discount:** `(listing per unit - median per unit) / median per unit * 100%`
4. **Negotiation room:** If listing >5% above median → estimate negotiation room

Present as a table using labels from config:

| Item | Value |
|------|-------|
| Total price | {price} |
| Size | {size} {area_unit_symbol} |
| Price per area unit | {per_unit}/{area_unit_symbol} |
| Area median per unit (recent) | {median}/{area_unit_symbol} |
| vs Market | +/-{pct}% |
| Negotiation room | {note} |

Example: if country is Taiwan, the table shows values in TWD per 坪. If Ireland, values in EUR per sqm.

---

## Section 5: Building Risk Assessment

Check `country_config.building_risks` for any applicable risk flags based on the building's year built. For each matching risk:
- Add the flag (using `flag_local` or `flag_en` from config, matching the report language) to the red flags list
- Use the severity from config
- Note the `viewing_action` for the viewing questions section

Example: if country is Taiwan and year built is 1983, this triggers the radiation steel risk (severity: high) and the pre-1999 seismic risk (severity: medium). If country is Ireland and BER is G, this triggers an energy efficiency risk.

---

## Section 6: Loan Trial Calculation

Calculate for all applicable mortgage scenarios from `country_config.mortgage.scenarios`. Show monthly payment and total interest over the loan term.

**Formula (universal):** Monthly payment = P * [r(1+r)^n] / [(1+r)^n - 1]
where P = loan principal, r = annual rate / 12, n = term_years * 12

For each scenario in `country_config.mortgage.scenarios`:
- Check eligibility: if the scenario has an `eligibility` condition, verify against the user's profile (e.g., check `country_config.government_schemes[].profile_field`)
- Calculate: down payment = total price * down_payment percentage
- Calculate: loan = total price * (1 - down_payment percentage)
- If `max_loan` is defined, cap the loan at that amount
- Calculate monthly payment and total interest

Present as a table:

| Scenario | Rate | Down payment | Monthly payment | Total interest ({term} years) |
|----------|------|--------------|-----------------|-------------------------------|
| {scenario name from config} | {rate}% | {amount} | {monthly} | {total interest} |

Mark eligible government scheme rows with a star or highlight. Flag any row where monthly payment > `budget.monthly_payment_max`.

If `buyer_type = first_time`: add note confirming/questioning eligibility for government schemes based on profile.

Example: if country is Taiwan, the table shows rows for "青安貸款 20%", "青安貸款 30%", "一般貸款 20%", "一般貸款 30%". If Ireland, it shows "FTB Fixed 10%", "FTB Variable 10%", "Standard Fixed 20%", etc.

---

## Section 7: Commute Calculation

Same structure as rent.md. From `user.commute_origin` to listing address. Estimate travel time using transport systems from `country_config.transport.systems`. Compare to `user.commute_max_minutes`.

Present as a table:

| Transport mode | Estimated time | Notes |
|----------------|----------------|-------|
| {system from config} | X minutes | Nearest station/stop: {name} |

---

## Section 8: Scoring

Score each dimension 0–5. Apply **BUY weights** from `country_config.scoring.dimensions`.

| Dimension (from config) | Key factors |
|-------------------------|-------------|
| price_reasonableness | Price per unit vs market median, monthly payment vs max, government scheme affordability, days on market |
| space_layout | Size, layout efficiency, floor, natural light, storage, parking |
| location_amenities | Transport access vs max walk time, lifestyle priorities, neighborhood trajectory |
| property_condition | Building type, age, elevator, parking, management, legal status, ownership type |
| risk_upside | Building risks from config, legal flags, days on market; if upgrader: capital gains tax estimate |

**Upgrader supplement** (if `buyer_type = upgrader`):
- Apply the capital gains tax rules from `country_config.taxes.capital_gains`:
  - Calculate holding years = current year - purchase_year
  - Look up the applicable tax rate from the country config's holding period brackets
  - If the country config defines a self-occupied rate, check eligibility
  - Estimated tax = (estimated gain) * rate
  - If purchase price unknown: use the `default_gain_assumption` from config
- Include in red flags and factor into risk/upside score

**Final score:** weighted sum using buy weights from config.

**Score interpretation:** Use thresholds and labels from `country_config.scoring.interpretation`.

---

## Section 9: Report Generation

### 9a: Determine report number
Read `reports/` filenames. Find highest `{###}`. New = max + 1, zero-padded. Start at `001` if empty.

### 9b: Build filename
`{###}-{area}-{road-slug}-{YYYY-MM-DD}.md` (see _shared.md for slugification rules)

### 9c: Write report to `reports/{filename}`

Use section headers and table headers from `country_config.report_labels`. Use dimension names from `country_config.scoring.dimensions`.

```markdown
# {###} | {area} {road} {floor/unit}

| Field | Value |
|-------|-------|
| Type | {type label from country_config.report_labels.type_labels.buy} |
| Score | {score}/5 — {interpretation label} |
| URL | {url} |
| Price | {price} | Size | {size} | Layout | {layout} |
| Age | {age} | Floor | {floor}/{total} | Portal | {portal} |

**URL:** {url}
**Score:** {score}/5
**Type:** buy
**Status:** Evaluated
**Verification:** confirmed

## {price_analysis section label}

{price table}
{price prose}

## {loan_calculation section label}

{loan table}
{loan prose: recommendation based on buyer_type; note if any scenario exceeds monthly_payment_max}

## {commute section label}

{commute table}
{commute prose}

## {dimension_scores section label}

| {dimension header} | {score header} | {key_factors header} |
|--------------------|----------------|----------------------|
| {dimension 1 name} | {d1}/5 | {factors} |
| {dimension 2 name} | {d2}/5 | {factors} |
| {dimension 3 name} | {d3}/5 | {factors} |
| {dimension 4 name} | {d4}/5 | {factors} |
| {dimension 5 name} | {d5}/5 | {factors} |
| **{overall label}** | **{total}/5** | |

{prose: recommendation rationale}

## {red_flags section label}

| # | Issue | Risk level |
|---|-------|------------|
| 1 | {issue} | {level from config} |

{prose: explanation of significant risks}

## {viewing_questions section label}

| # | Question | Category |
|---|----------|----------|
| 1 | {question} | {category from config} |
```

---

## Section 10: TSV Output

Write `batch/tracker-additions/{num}-{slug}.tsv`:
```
{num}\t{YYYY-MM-DD}\t{portal}\t{address}\t{type_label}\t{price}\t{size}{area_unit_symbol}\t{score}/5\tEvaluated\t[{num}](reports/{report_filename})\t{one-line note}
```

Use labels and symbols from `country_config.market`.

---

## Section 11: Merge Tracker

Run: `node merge-tracker.mjs`
