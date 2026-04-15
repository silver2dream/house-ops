# Afford Mode — Affordability Calculator

<!-- For first_time buyers primarily. Read modes/_shared.md first.
     Load country_config from config/country/{country}.yml.
     This is a planning mode — no property report or tracker entry is written. -->

---

## Overview

Calculates how much home a first_time buyer can actually afford, given their income and savings. Produces a loan plan table and area reality check. No report file is written.

---

## Section 1: Input Validation

Read from `config/profile.yml`. The required fields depend on the country's affordability model (from `country_config.mortgage.affordability`):

- If `income_period` is `monthly`: read `finance.monthly_income`
- If `income_period` is `annual`: read `finance.gross_annual_income`
- `finance.savings` — available for down payment
- `property.size_min` — minimum target size (in country's area unit)
- Target regions from profile
- `budget.buy_max` — user's stated ceiling (for comparison)

Also check `country_config.government_schemes` for any scheme eligibility fields in the profile (e.g., `finance.youth_loan_eligible`, `finance.htb_eligible`).

If any required field is `null` or missing, ask the user to provide it before proceeding.

Note: This mode is most relevant for `buyer_type: first_time`. It can be used by any buyer type, but government scheme sections only apply when the user meets eligibility criteria.

---

## Section 2: Max Affordable Price Calculation

**Affordability rule:** Read from `country_config.mortgage.affordability`:
- If `payment_ceiling_pct` is defined: Max monthly payment = income * (payment_ceiling_pct / 100)
- If `income_multiple` is defined: Max purchase price = gross annual income * income_multiple

Adjust income to monthly if needed (annual / 12).

**Loan formula (monthly payment to max principal):**
P = payment * [(1+r)^n - 1] / [r(1+r)^n]
where r = annual_rate / 12, n = term_years * 12

**For each scenario in `country_config.mortgage.scenarios`:**
1. Check eligibility (skip scenarios the user doesn't qualify for)
2. Calculate max loan P from max monthly payment (using scenario's rate and term)
3. If `max_loan` is defined in the scenario, cap P at that value
4. Unconstrained max total price = P / (1 - down_payment_pct)
5. Required down payment = total_price * down_payment_pct
6. Check: if required down payment > savings → constrained by savings:
   - Actual down payment = savings
   - Actual max loan = min(savings / down_pct * (1 - down_pct), P from income rule)
   - Actual max total price = savings + actual max loan
7. Total interest over loan term = (monthly_payment * n) - actual max loan

---

## Section 3: Loan Plan Table

Present all applicable scenarios:

| Scenario | Rate | Max price | Down payment | Monthly payment | Total interest | Notes |
|----------|------|-----------|--------------|-----------------|----------------|-------|
| {name from config} | {rate}% | {max_price} | {down} | {monthly} | {interest} | {note} |

Mark government scheme rows with a star. Mark rows where required down payment exceeds savings with a warning.

Also show: User's stated `budget.buy_max` vs the calculated max — if budget exceeds what's affordable, call it out explicitly: "Your target price of {buy_max} exceeds your current financial capacity ({max_price}). Consider adjusting your target or increasing your down payment savings."

Example: if country is Taiwan, the table shows "青安貸款 20%", "一般貸款 30%", etc. in TWD. If Ireland, it shows "FTB Fixed 10%", "Standard Variable 20%", etc. in EUR.

---

## Section 4: Area Price Reality Check

For each target area/district in the profile:
1. Fetch median price per area unit from the market reference source (`country_config.market_reference.price_register`) for that area, within the lookback period
2. Calculate: max affordable size = best affordable total price / median price per unit
3. Check vs `property.size_min`

Present as a table:

| Area | Median price per unit (recent) | Affordable size | Meets minimum ({size_min} {unit})? |
|------|-------------------------------|-----------------|-------------------------------------|
| {area} | {median}/{unit} | {size} | Yes / No |

Sort by affordability (feasible areas first), then by affordable size descending.

---

## Section 5: Recommendation

Prose summary:

1. **Achievable scenarios:** Which loan scenarios are realistic given savings? Highlight the best one.
2. **Area fit:** Which areas fall within budget for the target size?
3. **Overall assessment:** Which area + scenario combination is most feasible? State it directly.
4. **If budget is unrealistic:** Say so directly: "Your target price exceeds your financial capacity under all scenarios. Consider adjusting your target price or increasing your down payment savings."
5. **Next step:** Suggest using `buy` mode to evaluate specific listings, or `scan` to find options in feasible areas.

**Output only** — no report file, no TSV, no tracker entry. This is a planning consultation.
