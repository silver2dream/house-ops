# Shared Knowledge Base — house-ops

<!-- Injected into every evaluation. Do NOT put user-specific data here.
     User customization goes in modes/_profile.md and config/profile.yml.
     Country-specific data comes from config/country/{code}.yml (loaded as country_config). -->

## Country Config Loading

Before any evaluation, load:
1. `config/profile.yml` → get `country` field
2. `config/country/{country}.yml` → this is `country_config`

All country-specific values (currency, area units, tax rules, scoring labels, building risks, government schemes, etc.) come from `country_config`. Never hard-code them.

---

## Scoring Dimensions

Scoring is 0–5. Five dimensions, weights vary by transaction type.

Read dimension names, labels, and weights from `country_config.scoring.dimensions`. Each dimension has:
- `key`: internal identifier
- `name_local`: label in the local language (used in reports)
- `name_en`: English label
- `rent_weight`: percentage weight for rental evaluations
- `buy_weight`: percentage weight for purchase evaluations

Standard dimensions (keys are universal, labels come from config):
1. `price_reasonableness` — How does the price compare to market and budget?
2. `space_layout` — Size, layout efficiency, floor, light, storage
3. `location_amenities` — Transport access, lifestyle priorities
4. `property_condition` — Building type, age, facilities, management
5. `risk_upside` — Red flags, days on market, growth potential

Final score = weighted average of 5 dimension scores.

Example: if country is Taiwan, report headers use "價格合理性", "空間與格局", etc. If country is Ireland, they use "Price Reasonableness", "Space & Layout", etc.

### buyer_type Adjustments

Read buyer types from `country_config.mortgage.buyer_types`. Standard adjustments:

- **renter**: Standard rent weights. No loan calculation needed.
- **first_time**: In the price reasonableness dimension, add a trial loan calculation for any government schemes the buyer is eligible for (from `country_config.government_schemes`). Flag eligibility status from profile.
- **upgrader**: In the risk/upside dimension, add a capital gains tax estimate using the rules from `country_config.taxes.capital_gains` based on `current_property.purchase_year`.

---

## Market Knowledge

All market knowledge comes from `country_config`. Do NOT hard-code any country-specific facts.

### Building Risks

Refer to `country_config.building_risks` for any building-age-related risk flags. Each entry defines:
- `condition`: when to trigger (e.g., year built range)
- `severity`: high / medium / low
- `flag_local` / `flag_en`: warning text
- `viewing_action`: what to check during a viewing

### Tax Rules

Refer to `country_config.taxes` for:
- Capital gains tax rates and holding period brackets
- Transaction cost estimates
- Stamp duty (if applicable)
- Property tax details

### Government Schemes

Refer to `country_config.government_schemes` for subsidized loans, grants, or tax credits available to buyers. Each scheme defines eligibility criteria and a profile field to check.

### Market Reference Data

Refer to `country_config.market_reference` for:
- Price register / comparison data source (name, URL, lookback period)
- Key pricing metrics (rent per area unit, purchase price per area unit)
- Reference area classifications (premium vs mid-range districts)

---

## Report Format Conventions

- **Key data** → use tables
- **Reasoning and interpretation** → use prose
- Never mix: don't put narrative in tables, don't put numbers in prose when a table fits
- Required report sections (in order): header table, then sections from `country_config.report_labels.sections` — typically: price analysis, loan calculation (buy only), commute estimate, dimension scores, red flags, viewing questions

Use `country_config.report_labels` for all section headers, table headers, risk level labels, and question category labels. Reports should use the local language labels from the config.

**Required header fields** (every report must include these at the top):
```
**URL:** {listing url}
**Score:** {X.X}/5
**Type:** rent | buy
**Status:** {canonical status}
**Verification:** confirmed | unconfirmed (batch mode)
```

**Report filename convention:** `{###}-{area}-{road-slug}-{YYYY-MM-DD}.md`
- `{###}`: sequential 3-digit zero-padded integer (max existing report number + 1)
- `{area}`: area/district romanized or slugified from the address
- `{road-slug}`: road name slugified, hyphenated; if ambiguous → `road-{4-char-hex-of-address-hash}`
- `{YYYY-MM-DD}`: evaluation date

**Listing liveness verification:** ALWAYS use `agent-browser` (`agent-browser open` + `agent-browser snapshot`). NEVER use WebSearch or WebFetch alone to determine if a listing is active. Expired signals: URL error parameters, "no longer available" / inactive text in content (check `country_config.report_labels.inactive_listing` for localized text), content < 300 chars with only nav/footer.

**Platform access methods:**
Refer to `country_config.portals` for each portal's access method. Most real estate portals are SPAs requiring `agent-browser`. Market reference data sources (e.g., price registers) are reference-only and never populate the pipeline.

---

## Address Normalization Rules

Refer to `country_config.address_normalization.rules` for the country-specific normalization rules used for cross-platform deduplication. Each rule defines a transformation (e.g., character substitution, suffix normalization, space removal).

---

## Phase 1 Quick Filter Criteria

Apply before full evaluation. Check against profile values:

- price > budget ceiling → skip
- size < property.size_min (using the country's area unit from `country_config.market.area_unit`) → skip
- Additional country-specific checks: apply any profile fields that exist (e.g., `property.floor_min`, `property.age_max`, `property.ber_min`)
- Any item in `narrative.deal_breakers` found in listing → skip

Output: `qualified` (proceed to Phase 2) or `skip` (state reason, do not write report)

---

## TSV Format Reminder

11 tab-separated columns for `batch/tracker-additions/{num}-{slug}.tsv`:

1. num (3-digit zero-padded)
2. date (YYYY-MM-DD)
3. portal
4. address (area + road + floor/unit)
5. type (use `country_config.report_labels.type_labels` for the local label, e.g., "rent"/"buy" or localized equivalent)
6. price (formatted with currency from config)
7. size (with area unit symbol from config)
8. score (X.X/5)
9. status (canonical from states.yml)
10. report (markdown link)
11. notes (one line)

After writing TSV → always run `node merge-tracker.mjs`

---

## Canonical Statuses

Source of truth: `templates/states.yml`

| Status | When to use |
|--------|-------------|
| `Scanned` | Found by scanner, not yet evaluated |
| `Evaluated` | Report complete, pending decision |
| `Skip` | Low score or doesn't meet criteria |
| `Visit` | Viewing scheduled |
| `Visited` | Viewed, pending decision |
| `Pass` | Rejected after viewing |
| `Offer` | Offer submitted |
| `Negotiating` | Price negotiation in progress |
| `Signed` | Contract signed |
| `Done` | Move-in complete / title transferred |
| `Expired` | Listing taken down |

Rules: no bold, no dates, no extra text in status field — use the notes column for those.
