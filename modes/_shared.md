# Shared Knowledge Base — ie-house-ops

<!-- Injected into every evaluation. Do NOT put user-specific data here.
     User customization goes in modes/_profile.md and config/profile.yml. -->

## Scoring Dimensions

Scoring is 0–5. Five dimensions, weights vary by transaction type:

| Dimension | Rent weight | Buy weight |
|-----------|-------------|------------|
| Price Reasonableness | 30% | 35% |
| Space & Layout | 20% | 20% |
| Location & Amenities | 25% | 20% |
| Property Condition | 15% | 15% |
| Risk / Upside | 10% | 10% |

Final score = weighted average of 5 dimension scores × 5.

### buyer_type Adjustments

- **renter**: Standard rent weights. No mortgage calculation needed. Check if property is in a Rent Pressure Zone (RPZ) — if so, note the 2%/year rent increase cap.
- **first_time_buyer**: In Price Reasonableness, add Central Bank 4× gross annual income mortgage cap. Calculate max borrowing = gross_annual_income × 4. Check Help to Buy (HTB) eligibility (new builds only, max refund €30,000). Check First Home Scheme (FHS) eligibility (shared equity up to 30%, new builds only). Require 10% deposit.
- **mover**: In Risk / Upside, add CGT estimate if selling an investment property (33% rate, PPR exemption for principal residence). Central Bank 3.5× income rule applies, 20% deposit required.

---

## Ireland Market Knowledge

### Building & Property Risk Flags

- **Pre-1970s**: potential asbestos in insulation, floor tiles, roofing — flag for survey
- **Pre-2000s**: built before BER requirement era — likely poor energy efficiency, may lack BER cert
- **Pyrite issues**: certain estates in North Dublin, Meath, Offaly, Kildare — check IS 398 pyrite assessment; Pyrite Resolution Board may apply
- **Mica/defective blocks**: primarily Donegal and Mayo — check for MICA Redress Scheme eligibility
- **Planning permission**: check for unauthorised extensions or conversions — request compliance certificate or commencement notice from vendor/agent
- **Listed/protected structures**: restrictions on modifications — check NIAH (National Inventory of Architectural Heritage)

### BER (Building Energy Rating)

Ratings from A1 (best) to G (worst). All properties for sale or rent must have a BER cert (with some exemptions for protected structures).

| BER Band | Indicative annual energy cost (3-bed semi) | Notes |
|----------|----------------------------------------------|-------|
| A1–A3 | €500–€900 | Near zero energy; new builds post-2019 |
| B1–B3 | €900–€1,500 | Well insulated; recent builds or deep retrofit |
| C1–C3 | €1,500–€2,200 | Average modern standard |
| D1–D2 | €2,200–€3,000 | Older homes, some upgrades |
| E1–E2 | €3,000–€3,800 | Poor insulation, single glazing likely |
| F–G | €3,800+ | Very poor; major retrofit needed |

A poor BER is a negotiation lever (cost to upgrade) and ongoing cost risk.

### Central Bank Mortgage Rules

| Buyer type | Loan-to-Income (LTI) | Loan-to-Value (LTV) / Deposit |
|------------|----------------------|-------------------------------|
| First-time buyer | Max 4× gross annual income | 90% LTV (10% deposit) |
| Second/subsequent buyer | Max 3.5× gross annual income | 80% LTV (20% deposit) |

- Variable rates: approximately 3.5–4.5% (verify current market rates)
- Fixed rates: approximately 3.0–4.0% for 3–10 year terms
- Mortgage term: typically up to 35 years (most lenders), borrower must be under 70 at maturity
- Lenders may grant exceptions to LTI/LTV limits for a small percentage of lending each year

### Help to Buy (HTB)

- Eligibility: first-time buyer, new build or self-build only
- Tax refund of income tax and DIRT paid over previous 4 years
- Maximum refund: €30,000 or 10% of purchase price (whichever is lower)
- Must take out a mortgage of at least 70% of purchase price
- Property price cap: €500,000
- Apply via Revenue's myAccount before drawdown

### First Home Scheme (FHS)

- Eligibility: first-time buyer, new build only
- State takes shared equity stake of up to 30% of market value (up to 20% standard + 10% if in HTB shortfall)
- No rent charged on the equity share for first 5 years; small charge from year 6
- Regional price caps apply (e.g., €475,000 in Dublin)
- Can buy out equity share at any time at current market value

### Stamp Duty

- 1% on properties up to €1,000,000
- 2% on the amount exceeding €1,000,000
- Higher rate of 6% for bulk purchases (10+ residential in 12 months)

### Local Property Tax (LPT)

- Annual tax based on property valuation bands
- Self-assessed; Revenue sets midpoint rates per band
- Typical range: €90–€600+ per year depending on value and local authority adjustment
- Councils can vary the rate by ±15%

### Property Price Register (PPR)

- Government register of all residential property sales (propertypriceregister.ie)
- Use 6-month lookback window as standard comparison period
- Shows: address, sale date, price paid, whether new/second-hand, VAT-exclusive price
- Essential for assessing if asking price is reasonable vs. comparable recent sales

### Capital Gains Tax (CGT)

- Rate: 33%
- Principal Private Residence (PPR) exemption: no CGT on sale of your own home
- Partial exemption if property was rented out for part of ownership
- Annual exemption: first €1,270 of gains per person is exempt

### Rent Pressure Zones (RPZ)

- Rent increases capped at 2% per year (or CPI if lower)
- Applies to most urban areas and many towns
- Landlord must register with RTB; tenants have rights under Residential Tenancies Act
- Check RTB rent register for comparable rents in the area

### Standard Market Metrics

- **€/m²** (price per square metre): key value metric for both rent and purchase
- **Rent yield %**: (annual rent / purchase price) × 100 — useful for investment context
- **Dublin market reference**: Dublin 2/4/6 are premium; Dublin 1/7/8 are mid-range; outer suburbs and commuter belt are more affordable
- 1 square metre = 10.764 square feet (Irish listings sometimes use sq ft)

---

## Report Format Conventions

- **Key data** → use tables
- **Reasoning and interpretation** → use prose
- Never mix: don't put narrative in tables, don't put numbers in prose when a table fits
- Required report sections (in order): Header Table, Price Analysis, Mortgage Calculation (buy only), Commute Analysis, Scoring Breakdown, Red Flags, Viewing Questions

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
- `{area}`: lowercase Dublin postal district (e.g., `d2`, `d4`, `d6w`) or town/suburb name (e.g., `ranelagh`, `stillorgan`, `blackrock`, `cork-city`)
- `{road-slug}`: road name lowercased, hyphenated (e.g., `leeson-st`, `merrion-rd`, `grafton-st`); if ambiguous → `road-{4-char-hex}`
- `{YYYY-MM-DD}`: evaluation date

Examples:
- `001-d4-merrion-rd-2026-04-11.md`
- `042-ranelagh-chelmsford-rd-2026-04-11.md`
- `003-cork-city-road-3a7f-2026-04-11.md`

**Listing liveness verification:** ALWAYS use `playwright-cli` (`playwright-cli goto {url}` + `playwright-cli snapshot`). NEVER use WebSearch or WebFetch alone to determine if a listing is active. Expired signals: "This property is no longer available", "ad has expired", content < 300 chars with only nav/footer, redirect to search results page.

**Platform access methods:**
- Daft.ie: SPA → `playwright-cli` required
- MyHome.ie: SPA → `playwright-cli` required
- Property.ie: Standard HTML → `playwright-cli` preferred for consistency
- SherryFitzGerald.ie: SPA → `playwright-cli` required
- Lisney.com: SPA → `playwright-cli` required
- PPR (propertypriceregister.ie): Government site → reference data only, never populates pipeline

---

## Address Normalization Rules

Five rules for cross-platform deduplication:

1. "Road" / "Rd" / "Rd." → "Rd"
2. "Street" / "St" / "St." → "St"
3. "Avenue" / "Ave" / "Ave." → "Ave"
4. Dublin postal codes: "Dublin 2" / "D2" / "D02" → "D2"
5. Spaces normalized, case-insensitive comparison

---

## Phase 1 Quick Filter Criteria

Apply before full evaluation. Check against profile values:

- price > budget ceiling → skip
- size < property.size_min (m²) → skip
- BER worse than ber_min (if set) → skip
- Any item in narrative.deal_breakers found in listing → skip

Output: `qualified` (proceed to Phase 2) or `skip` (state reason, do not write report)

---

## TSV Format Reminder

11 tab-separated columns for `batch/tracker-additions/{num}-{slug}.tsv`:

1. num (3-digit zero-padded)
2. date (YYYY-MM-DD)
3. portal
4. address (area + road)
5. type (rent or buy)
6. price (€2,500/mo or €450,000)
7. size (85m²)
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
