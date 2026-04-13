# Rent Mode — Rental Property Evaluation (Ireland)

<!-- Read modes/_shared.md and modes/_profile.md before executing this mode. -->

---

## Overview

Full evaluation of a rental listing in Ireland. Two phases:
- **Phase 1** — Quick filter (seconds): price, size, BER
- **Phase 2** — Full evaluation: data extraction, price analysis, commute, scoring, report

---

## Section 1: Input Handling

### URL input (most common)
1. `playwright-cli goto {url}` to navigate to the URL
2. `playwright-cli snapshot` to read the page
3. **Verify listing is active:**
   - Active: listing title + description + price + contact/apply section all present
   - Inactive: only nav and footer visible, no listing content → output "This listing is no longer available." and stop
4. **NEVER** use WebSearch or WebFetch alone to verify listing status. Always use `playwright-cli`.

### Pasted text input
Proceed directly to Phase 1 using the provided content.

---

## Section 2: Phase 1 Quick Filter

Read `config/profile.yml`. Check each criterion. If **any** fails:
- Output: `Skipped: {reason} ({actual value} vs limit {limit value})`
- Do NOT write a full report
- Optionally write a minimal TSV with status `Skip`
- Stop

| Check | Profile field | Fail condition |
|-------|---------------|----------------|
| Price | `budget.rent_max` | Monthly rent > rent_max (EUR) |
| Size | `property.size_min` | Listed m² < size_min |
| BER | `property.ber_min` | BER rating worse than ber_min (if set) |

Also check `modes/_profile.md` deal_breakers: if any match the listing → Skip with reason.

If all pass: output `Phase 1 passed — proceeding to full evaluation.` and proceed to Phase 2.

---

## Section 3: Data Extraction

Extract from the listing page:

| Field | Notes |
|-------|-------|
| Title | Full listing title |
| Address | Area + street + Eircode if available |
| BER | Rating (A1–G) |
| Size | m² |
| Bedrooms/Bathrooms | e.g., 2 bed, 1 bath |
| Monthly rent | EUR |
| Deposit | Months or amount |
| Management fees | If apartment (per month or per year) |
| Furnished | Furnished / Unfurnished / Part-furnished |
| Available from | Date |
| Lease term | Minimum term |
| Type | Apartment / House / Studio / Duplex |
| Parking | Yes / No |
| Listed by | Agent / Landlord |
| Platform | Portal name (e.g., Daft.ie, MyHome.ie, Rent.ie) |

---

## Section 4: Price Analysis

1. **Rent per m²:** `monthly rent / m²`
2. **Market comparison:** Use Daft Rental Report or RTB Rent Index data for the same area/county. Target: comparable size and type.
3. **RPZ check:** Is this property in a Rent Pressure Zone? If yes, note that rent increases are capped at 2% per year (or general CPI-linked cap).
4. **Premium/discount:** `(listing rent/m² - median rent/m²) / median rent/m² x 100%`
5. **Total monthly cost:** `rent + management fees + bins estimate (~EUR 25-40/month) + utilities estimate (~EUR 150-250/month)`
6. **Deposit calculation:** `deposit / monthly rent` = number of months
7. **Negotiation room:** If listing is >10% above median → note estimated negotiation room

Present as a table:

| Item | Value |
|------|-------|
| Monthly rent | EUR {price}/month |
| Management fees | EUR {fee}/month |
| Estimated bins + utilities | EUR {estimate}/month |
| Total monthly cost | EUR {total}/month |
| Rent per m² | EUR {per_sqm}/month |
| Area median rent per m² | EUR {median}/month |
| Relative to market | +/-{pct}% |
| Deposit | EUR {deposit} ({months} months) |
| RPZ status | Yes/No — {implications} |
| Negotiation room estimate | {negotiation_note} |

---

## Section 5: Commute Calculation

- **From:** listing address
- **To:** `config/profile.yml → user.commute_origin`
- **Method:** Estimate via public transport (Luas, DART, Dublin Bus, Irish Rail as applicable); note walking time from property to nearest stop/station + from destination station to workplace. Also note driving time if relevant.
- **Compare:** Total commute time vs `user.commute_max_minutes`

| Transport mode | Estimated time | Notes |
|---------------|----------------|-------|
| Luas | X min | Nearest stop: {stop}, {line} line |
| DART | X min | Nearest station: {station} |
| Bus | X min | Route(s): {route} |
| Driving | X min | Approximate, traffic-dependent |

Prose: Is the commute within the acceptable limit? If borderline, note it.

---

## Section 6: Scoring

Score each dimension 0-5 (0=very poor, 5=excellent). Apply rent weights. Sum = final score.

| Dimension | Weight | Key factors |
|-----------|--------|-------------|
| Price reasonableness | 30% | Rent vs budget ceiling, rent vs market median, total monthly cost, deposit reasonableness, RPZ status |
| Space and layout | 20% | Size vs size_min, number of bedrooms/bathrooms, furnished status, natural light, storage |
| Location and amenities | 25% | Public transport proximity, lifestyle priorities (shops/schools/hospitals from profile), walkability |
| Property condition | 15% | BER rating, property type, furnishing quality, parking, landlord vs agent, listing freshness |
| Risk / potential | 10% | Number and severity of flags, days on market, any deal_breakers, neighbourhood trajectory |

**Final score:** `(D1 x 0.30 + D2 x 0.20 + D3 x 0.25 + D4 x 0.15 + D5 x 0.10) / 1.0`

**Score interpretation:**
- >= 4.0: **Recommended for viewing** — strong match, prioritize
- 3.5-3.9: **Worth considering** — worth viewing with caveats
- < 3.5: **Recommend skipping** — strongly discourage pursuing; only proceed if user has specific reason

---

## Section 7: Report Generation

### 7a: Determine report number

Read filenames in `reports/`. Find the highest `{###}` prefix. New report number = max + 1, zero-padded to 3 digits. If no reports exist, start at `001`.

### 7b: Build filename

`{###}-{area}-{road-slug}-{YYYY-MM-DD}.md`
- `{area}`: area/neighbourhood name, lowercase, hyphenated (e.g., `rathmines`, `drumcondra`, `dun-laoghaire`, `sandyford`, `grand-canal-dock`, `phibsborough`, `stoneybatter`, `smithfield`, `clontarf`, `ranelagh`)
- `{road-slug}`: road/street name, lowercase, hyphenated (e.g., `harold-cross-rd`, `pearse-st`, `baggot-st`). If ambiguous → `road-{4-char-hex-of-address-hash}`
- `{YYYY-MM-DD}`: today's date

### 7c: Write report to `reports/{filename}`

```markdown
# {###} | {area} {road}

| Field | Value |
|-------|-------|
| Type | Rental |
| Score | {score}/5 — {interpretation} |
| URL | {url} |
| Monthly rent | EUR {rent} | Size | {size} m² | Layout | {bedrooms} bed, {bathrooms} bath |
| Listed | {listing_date} | Platform | {portal} |

**URL:** {url}
**Score:** {score}/5
**Type:** rent
**Status:** Evaluated
**Verification:** confirmed

## Price Analysis

{price analysis table}

{price analysis prose: interpretation, RPZ implications, and negotiation context}

## Commute Estimate

{commute table}

{commute prose: assessment vs commute_max_minutes}

## Dimension Scores

| Dimension | Score | Key factors |
|-----------|-------|-------------|
| Price reasonableness | {d1}/5 | {key factors} |
| Space and layout | {d2}/5 | {key factors} |
| Location and amenities | {d3}/5 | {key factors} |
| Property condition | {d4}/5 | {key factors} |
| Risk / potential | {d5}/5 | {key factors} |
| **Overall** | **{total}/5** | |

{dimension prose: overall recommendation rationale, key trade-offs}

## Red Flags

| # | Issue | Risk level |
|---|-------|------------|
| 1 | {issue} | High/Medium/Low |

{prose: explanation of the most significant risks; if none, write "No significant red flags identified."}

## Viewing Questions

| # | Question | Category |
|---|----------|----------|
| 1 | {question} | Structure/Utilities/Environment/Legal |
```

All sections are required. If a section has no content (e.g., no red flags), write a brief "None." rather than omitting it.

---

## Section 8: TSV Output

Write `batch/tracker-additions/{num}-{slug}.tsv` where `{slug}` matches the report filename minus date.

Single line, 11 tab-separated columns:
```
{num}\t{YYYY-MM-DD}\t{portal}\t{address}\tRent\tEUR {price}/month\t{size} m²\t{score}/5\tEvaluated\t[{num}](reports/{report_filename})\t{one-line note}
```

---

## Section 9: Merge Tracker

Run: `node merge-tracker.mjs`

This appends the TSV row to `data/tracker.md` and archives the TSV to `batch/tracker-additions/processed/`.
