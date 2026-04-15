# Rent Mode — Rental Property Evaluation

<!-- Read modes/_shared.md and modes/_profile.md before executing this mode.
     Load country_config from config/country/{country}.yml. -->

---

## Overview

Full evaluation of a rental listing. Two phases:
- **Phase 1** — Quick filter (seconds): price, size, and any country-specific criteria
- **Phase 2** — Full evaluation: data extraction, price analysis, commute, scoring, report

---

## Section 1: Input Handling

### URL input (most common)
1. `agent-browser open {url}`
2. `agent-browser snapshot -i`
3. **Verify listing is active:**
   - Active: listing title + description + price + contact/apply section all present
   - Inactive: only nav and footer visible, no listing content → output the inactive listing message from `country_config.report_labels.inactive_listing` and stop
4. **NEVER** use WebSearch or WebFetch alone to verify listing status. Always use `agent-browser`.

### Pasted text input
Proceed directly to Phase 1 using the provided content.

---

## Section 2: Phase 1 Quick Filter

Read `config/profile.yml`. Check each applicable criterion. If **any** fails:
- Output: `Skipped: {reason} ({actual value} vs limit {limit value})`
- Do NOT write a full report
- Optionally write a minimal TSV with status `Skip`
- Stop

Standard checks:

| Check | Profile field | Fail condition |
|-------|---------------|----------------|
| Price | `budget.rent_max` | Monthly rent > rent_max |
| Size | `property.size_min` | Listed size < size_min (using area unit from `country_config.market.area_unit`) |

Additional checks — apply if the profile field exists:
- `property.floor_min`: Floor number < floor_min
- `property.age_max`: Building age > age_max
- `property.ber_min`: Energy rating below minimum (if country uses BER/EPC ratings)

Also check `modes/_profile.md` deal_breakers: if any match the listing → Skip with reason.

If all pass: output the Phase 1 pass message from `country_config.report_labels.phase1_pass` and proceed to Phase 2.

---

## Section 3: Data Extraction

Extract data fields from the listing page. Use `country_config.listing_fields` for the field names and local labels. Standard fields to extract:

| Field key | Notes |
|-----------|-------|
| `title` | Full listing title |
| `address` | Area + road/street + floor/unit |
| `floor` / `total_floors` | Floor number / total floors |
| `size` | Size in the country's area unit |
| `layout` | Layout (e.g., bedrooms, bathrooms) |
| `monthly_rent` | Monthly rent (in country's currency) |
| `deposit` | Deposit (months or amount) |
| `management_fee` | Monthly management/service charge (0 if none) |
| `facilities` | Key facilities (elevator, parking, appliances, etc.) |
| `building_type` | Property type (from `country_config.property_types`) |
| `building_age` | Building age or year built (if applicable) |
| `owner_or_agent` | Owner-listed or via agent |
| `listing_date` | Listing date |
| `platform` | Portal name |

Not all fields exist in every country. Extract what is available on the page.

---

## Section 4: Price Analysis

1. **Rent per area unit:** Monthly rent / size (using `country_config.market.area_unit_symbol` and `country_config.market.price_per_area_label`)
2. **Market comparison:** Use the market reference source from `country_config.market_reference.price_register` to find rental median for the same area. Target: comparable size and type, within the lookback period from config.
3. **Premium/discount:** `(listing rent per unit - median rent per unit) / median rent per unit * 100%`
4. **Total monthly cost:** Rent + management fee + any other recurring charges
5. **Deposit analysis:** Deposit / monthly rent = number of months (compare to `country_config.rental_market.deposit_norm`)
6. **Negotiation room:** If listing is >10% above median → note estimated negotiation room

Present as a table using labels from `country_config.report_labels.table_headers`:

| Item | Value |
|------|-------|
| Monthly rent | {price}/{period label from config} |
| Management fee | {fee}/{period label} |
| Total monthly cost | {total}/{period label} |
| Rent per area unit | {per_unit}/{period label} |
| Area median per unit | {median}/{period label} |
| vs Market | +/-{pct}% |
| Deposit | {deposit} ({months} months) |
| Negotiation room | {note} |

Example: if country is Taiwan, the table shows "月租", "管理費", values in TWD and per 坪. If country is Ireland, it shows "Monthly rent", "Service charge", values in EUR and per sqm.

---

## Section 5: Commute Calculation

- **From:** `config/profile.yml → user.commute_origin`
- **To:** listing address
- **Method:** Estimate using transport systems from `country_config.transport.systems`. For each transport system defined, estimate travel time (e.g., nearest station + walking time). Note alternative options if relevant.
- **Compare:** Total commute time vs `user.commute_max_minutes`

Present as a table:

| Transport mode | Estimated time | Notes |
|----------------|----------------|-------|
| {system name from config} | X minutes | Nearest station/stop: {name} |

Prose: Is the commute within the acceptable limit? If borderline, note it.

---

## Section 6: Scoring

Score each dimension 0–5 (0=very poor, 5=excellent). Apply **rent weights** from `country_config.scoring.dimensions`.

For each dimension, use the key factors relevant to renting:

| Dimension (from config) | Key factors |
|-------------------------|-------------|
| price_reasonableness | Rent vs budget ceiling, rent vs market median, total monthly cost, deposit reasonableness |
| space_layout | Size vs size_min, layout efficiency, floor number, natural light, storage |
| location_amenities | Transport access vs max walk time, lifestyle priorities from profile |
| property_condition | Building type, age, elevator, appliances, owner vs agent, listing freshness |
| risk_upside | Number and severity of red flags, days on market, deal_breakers, neighborhood trajectory |

**Final score:** weighted sum using rent weights from config.

**Score interpretation:** Use thresholds and labels from `country_config.scoring.interpretation`:
- Score >= excellent threshold → excellent label (e.g., "Recommended for viewing")
- Score >= moderate threshold → moderate label (e.g., "Worth considering with caveats")
- Below moderate threshold → poor label (e.g., "Recommend skipping")

---

## Section 7: Report Generation

### 7a: Determine report number

Read filenames in `reports/`. Find the highest `{###}` prefix. New report number = max + 1, zero-padded to 3 digits. If no reports exist, start at `001`.

### 7b: Build filename

`{###}-{area}-{road-slug}-{YYYY-MM-DD}.md`
- `{area}`: slugify the area/district from the address
- `{road-slug}`: slugify the road/street name, hyphenated. If ambiguous → `road-{4-char-hex-of-address-hash}`
- `{YYYY-MM-DD}`: today's date

### 7c: Write report to `reports/{filename}`

Use section headers from `country_config.report_labels.sections` (local language labels). Use table headers from `country_config.report_labels.table_headers`. Use dimension names from `country_config.scoring.dimensions`.

The report structure:

```markdown
# {###} | {area} {road} {floor/unit}

| Field | Value |
|-------|-------|
| Type | {type label from country_config.report_labels.type_labels.rent} |
| Score | {score}/5 — {interpretation label} |
| URL | {url} |
| Rent | {rent} | Size | {size} | Layout | {layout} |
| Listed | {listing_date} | Portal | {portal} |

**URL:** {url}
**Score:** {score}/5
**Type:** rent
**Status:** Evaluated
**Verification:** confirmed

## {price_analysis section label from config}

{price analysis table}
{price analysis prose}

## {commute section label from config}

{commute table}
{commute prose}

## {dimension_scores section label from config}

| {dimension header} | {score header} | {key_factors header} |
|--------------------|----------------|----------------------|
| {dimension 1 name} | {d1}/5 | {factors} |
| {dimension 2 name} | {d2}/5 | {factors} |
| {dimension 3 name} | {d3}/5 | {factors} |
| {dimension 4 name} | {d4}/5 | {factors} |
| {dimension 5 name} | {d5}/5 | {factors} |
| **{overall label}** | **{total}/5** | |

{prose: overall recommendation rationale, key trade-offs}

## {red_flags section label from config}

| # | Issue | Risk level |
|---|-------|------------|
| 1 | {issue} | {level from config risk_levels} |

{prose: explanation of the most significant risks; if none, write a brief "None identified."}

## {viewing_questions section label from config}

| # | Question | Category |
|---|----------|----------|
| 1 | {question} | {category from config question_categories} |
```

All sections are required. If a section has no content (e.g., no red flags), write a brief note rather than omitting it.

---

## Section 8: TSV Output

Write `batch/tracker-additions/{num}-{slug}.tsv` where `{slug}` matches the report filename minus date.

Single line, 11 tab-separated columns:
```
{num}\t{YYYY-MM-DD}\t{portal}\t{address}\t{type_label}\t{price}{rent_period_label}\t{size}{area_unit_symbol}\t{score}/5\tEvaluated\t[{num}](reports/{report_filename})\t{one-line note}
```

Use labels and symbols from `country_config.market` for type, currency, area units, and period labels.

---

## Section 9: Merge Tracker

Run: `node merge-tracker.mjs`

This appends the TSV row to `data/tracker.md` and archives the TSV to `batch/tracker-additions/processed/`.
