# Afford Mode — Affordability Calculator (Ireland)

<!-- For first_time buyers primarily. Read modes/_shared.md first. -->
<!-- This is a planning mode — no property report or tracker entry is written. -->

---

## Overview

Calculates how much home a buyer in Ireland can actually afford, given their income and savings, applying Central Bank of Ireland lending rules. Produces a mortgage plan table and area reality check. No report file is written.

---

## Section 1: Input Validation

Read from `config/profile.yml`:
- `finance.annual_income` — gross annual income (EUR)
- `finance.savings` — available for deposit (EUR)
- `search.buyer_type` — `first_time` or `upgrader`
- `property.size_min` — minimum target size (m²)
- `regions[].areas` — target areas/neighbourhoods
- `budget.buy_max` — user's stated ceiling (for comparison)

If any required field is `null` or missing, ask the user to provide it before proceeding.

Note: This mode is most relevant for `buyer_type: first_time`. It can be used by any buyer type, but the HTB and FHS sections only apply to first-time buyers purchasing new builds.

---

## Section 2: Max Affordable Price Calculation

**Central Bank of Ireland lending rules:**
- First-time buyer (FTB): max mortgage = 4x gross annual income, min deposit = 10%
- Non-FTB (mover): max mortgage = 3.5x gross annual income, min deposit = 20%

**Bank affordability rule of thumb:** Monthly payment <= 35% of net monthly income.

**Max monthly payment:** `(annual_income x 0.70 / 12) x 0.35` (approximate net after tax, then 35% of net)

**Mortgage rates:**
- Fixed rate: 3.2% per year
- Variable rate: 3.8% per year
- Term: 30 years (360 months)

**Mortgage formula (monthly payment -> max principal):**
P = payment x [(1+r)^n - 1] / [r(1+r)^n]
where r = annual_rate / 12, n = 360

**For each scenario:**
1. Calculate max mortgage from Central Bank income multiple:
   - FTB: max_mortgage = annual_income x 4
   - Non-FTB: max_mortgage = annual_income x 3.5
2. Calculate max mortgage from monthly payment affordability (using formula above)
3. Binding constraint = lower of (income multiple) and (affordability calculation)
4. FTB: max total price = binding mortgage / 0.90 (since deposit = 10%)
   Non-FTB: max total price = binding mortgage / 0.80 (since deposit = 20%)
5. Required deposit = total_price x deposit_percentage
6. Check: if required deposit > savings → constrained by savings:
   - Actual deposit = savings
   - Actual max mortgage = min(savings / deposit_pct x (1 - deposit_pct), binding mortgage)
   - Actual max total price = savings + actual max mortgage
7. Total interest over 30 years = (monthly_payment x 360) - actual mortgage

**Help to Buy (HTB) adjustment** (FTB + new build only):
- HTB refund = min(EUR 30,000, 10% of purchase price up to EUR 500,000)
- Effective deposit = savings + HTB refund
- Recalculate max price with boosted deposit

**First Home Scheme (FHS) adjustment** (FTB + new build only):
- Shared equity up to 30% of purchase price (max EUR 500,000 property)
- Effective mortgage = price - deposit - FHS equity
- Recalculate monthly payment with reduced mortgage

---

## Section 3: Mortgage Plan Table

| Scenario | Rate | Max property price | Deposit needed | Monthly payment | 30-year total interest | Notes |
|----------|------|-------------------|----------------|-----------------|----------------------|-------|
| FTB Fixed 10% | 3.2% | {max_price} | {deposit} | {monthly} | {interest} | {note} |
| FTB Variable 10% | 3.8% | {max_price} | {deposit} | {monthly} | {interest} | {note} |
| FTB Fixed + HTB (new build) | 3.2% | {max_price} | {deposit - HTB} | {monthly} | {interest} | {note} |
| FTB Fixed + FHS (new build) | 3.2% | {max_price} | {deposit} | {reduced monthly} | {interest} | FHS equity: EUR {equity} |
| Non-FTB Fixed 20% | 3.2% | {max_price} | {deposit} | {monthly} | {interest} | {note} |
| Non-FTB Variable 20% | 3.8% | {max_price} | {deposit} | {monthly} | {interest} | {note} |

Show only rows relevant to the user's `buyer_type`:
- `first_time`: show FTB rows (including HTB and FHS if applicable)
- `upgrader`: show Non-FTB rows only

Notes column:
- Mark "Deposit shortfall" with a Warning if required deposit > savings
- Mark "Exceeds Central Bank limit" with a Warning if loan exceeds income multiple

Also show: User's stated `budget.buy_max` vs the calculated max — if budget > what's affordable, call it out explicitly: "Your target price of EUR {buy_max} exceeds what your current finances can support (EUR {max_price}). Consider adjusting your target or increasing your deposit savings."

---

## Section 4: Area Price Reality Check

For each area in `profile.regions`:
1. Fetch PPR (Property Price Register) median EUR/m² for that area (last 6 months) using WebSearch
2. Calculate: max affordable m² = best affordable total price / median EUR/m²
3. Check vs `property.size_min`

| Area | Median EUR/m² (last 6 months) | Affordable m² at budget | Meets minimum (>= {size_min} m²) |
|------|------------------------------|------------------------|----------------------------------|
| {area} | EUR {median}/m² | {sqm} m² | Yes / Insufficient |

Sort by "Meets minimum" (Yes first) then by affordable m² descending.

---

## Section 5: Recommendation

Prose summary:

1. **Achievable scenarios:** Which mortgage scenarios are realistic given savings and income? (highlight the best one)
2. **HTB / FHS impact:** If FTB, how much do HTB and FHS improve affordability? Are new builds in the target areas available within budget?
3. **Area fit:** Which areas fall within budget for the target size?
4. **Overall assessment:** e.g., "With your current income and savings, purchasing a {size_min}+ m² property in {area} is the most feasible option, with the FTB Fixed + HTB scenario offering the best terms."
5. **If budget is unrealistic:** Say so directly: "Your target price exceeds what is affordable under all scenarios. Consider adjusting your target price, increasing your deposit savings, or exploring the First Home Scheme for new builds."
6. **Key Central Bank considerations:** Remind user that banks may lend below the max multiple depending on individual circumstances (employment type, existing debts, etc.)
7. **Next step:** Suggest using `buy` mode to evaluate specific listings, or `scan` to find options in feasible areas.

**Output only** — no report file, no TSV, no tracker entry. This is a planning consultation.
