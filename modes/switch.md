# Switch Mode — Upgrade Planner

<!-- For upgrader buyer_type only. Read modes/_shared.md first.
     Load country_config from config/country/{country}.yml.
     This is a planning mode — no property report or tracker entry is written. -->

---

## Overview

Helps an upgrader (existing homeowner planning to sell and buy) analyze the financial mechanics of their move: net proceeds from selling, gap analysis for the new purchase, and strategy comparison (sell first / buy first / simultaneous). No report file is written.

---

## Section 1: Input Validation

Read from `config/profile.yml`:
- `search.buyer_type` — must be `upgrader`
- `current_property.estimated_value` — estimated current market value
- `current_property.loan_remaining` — outstanding mortgage balance
- `current_property.purchase_year` — year originally purchased
- `current_property.selling_strategy` — `sell_first` | `buy_first` | `simultaneous`
- `budget.buy_max` — target new property price ceiling
- `budget.monthly_payment_max` — max monthly payment for new mortgage

**If `buyer_type` is not `upgrader`:**
Output: "This mode is for upgraders (buyer_type: upgrader). For general purchase analysis use buy mode, for first-time buyer planning use afford mode." and stop.

**If any `current_property` field is null:**
Ask the user to provide the missing value(s) before proceeding.

---

## Section 2: Track A — Selling the Current Property

### 2a: Capital Gains / Transaction Tax Estimate

Apply the capital gains tax rules from `country_config.taxes.capital_gains`:
- Calculate holding years = current year - `current_property.purchase_year`
- Look up the applicable tax rate from the country config's holding period brackets (match based on `max_years`)
- If the country config defines a `self_occupied` rate, mention the conditions under which it may apply
- Estimated gain = `estimated_value * default_gain_assumption` from config (conservative assumption if purchase price unknown)
- Estimated tax = gain * rate

If the country does not define capital gains tax in config (e.g., `capital_gains` is null), skip this section and note that capital gains tax does not apply or should be verified with a local advisor.

### 2b: Net Proceeds Table

Use the transaction cost estimate from `country_config.taxes.transaction_costs.estimate_pct`. List the breakdown items from `country_config.taxes.transaction_costs.breakdown`.

| Item | Amount |
|------|--------|
| Estimated sale price | {estimated_value} |
| Outstanding mortgage | -{loan_remaining} |
| Transaction costs (est. {pct}%: {breakdown items from config}) | -{cost} |
| Capital gains tax (est.) | -{tax} |
| **Net Proceeds** | **{net}** |

Prose: Explain key assumptions (gain estimate percentage, transaction cost percentage). Recommend consulting a local property professional for precise figures. Reference the specific professionals or roles from the country config's transaction cost breakdown if available.

---

## Section 3: Track B — Buying the New Property

### 3a: Down Payment Requirement

For each relevant down payment scenario using `budget.buy_max`:

| Scenario | Target price | Down payment needed | Net proceeds (available) | Gap |
|----------|-------------|--------------------|--------------------------|----|
| {pct}% down | {buy_max} | {buy_max * pct} | {net} | {gap or "No gap"} |

Gap = required down payment - net proceeds (if positive, shows shortfall; if negative, shows surplus)

### 3b: Remaining Loan Estimate

For the scenario where net proceeds cover the down payment, use a standard mortgage rate from `country_config.mortgage.scenarios` (pick the standard/non-subsidized scenario):
- Remaining loan = target price - down payment (from proceeds)
- Monthly payment at the scenario's rate over the term
- Compare to `budget.monthly_payment_max`

| Loan amount | Monthly payment est. | Monthly max | Affordable? |
|-------------|---------------------|-------------|-------------|
| {loan} | {monthly} | {max} | Yes / Warning |

---

## Section 4: Strategy Comparison

| Strategy | Pros | Cons | Financial risk | Recommended when |
|----------|------|------|---------------|------------------|
| **Sell first** | Funds confirmed, no bridging pressure; stronger negotiating position | Need interim housing, hard to compete in hot market; psychological pressure | Low | Tight finances, high uncertainty |
| **Buy first** | One move, seamless transition; can take time choosing | Short-term double mortgage pressure; need extra liquidity | High | Strong finances, confident existing property will sell |
| **Simultaneous** | No interim period; shortest timeline | Coordination difficulty; limited negotiating flexibility | Medium | Stable market, experienced agents |

**For your situation** row: Based on the user's net proceeds, gap analysis, and `current_property.selling_strategy` preference, which strategy fits best? Add a tailored row with specific analysis based on the numbers.

---

## Section 5: Recommendation

Prose:
1. **Net proceeds summary:** Is the estimated net sufficient for the target down payment?
2. **Strategy recommendation:** Given the numbers, which strategy minimizes risk? Align with or challenge the user's stated `selling_strategy` preference if numbers suggest otherwise.
3. **Key risks to flag:**
   - If holding period is short: high tax rate from `country_config.taxes.capital_gains` makes selling now costly — state the specific rate
   - If gap is large: bridge financing or price range adjustment needed
   - If monthly payment > monthly_payment_max: budget adjustment needed
4. **Suggested next steps:** When ready to evaluate specific properties, use `buy` mode. Use `scan` to search target areas.

**Output only** — no report file, no TSV, no tracker entry.
