# Switch Mode — Mover/Trader-Up Planner (Ireland)

<!-- For upgrader buyer_type only. Read modes/_shared.md first. -->
<!-- This is a planning mode — no property report or tracker entry is written. -->

---

## Overview

Helps a mover/trader-up (existing homeowner planning to sell and buy in Ireland) analyse the financial mechanics of their move: net proceeds from selling, gap analysis for the new purchase, and strategy comparison (sell first / buy first / simultaneous). No report file is written.

---

## Section 1: Input Validation

Read from `config/profile.yml`:
- `search.buyer_type` — must be `upgrader`
- `current_property.estimated_value` — estimated current market value (EUR)
- `current_property.loan_remaining` — outstanding mortgage balance (EUR)
- `current_property.purchase_year` — year originally purchased
- `current_property.is_ppr` — true/false (was it your principal private residence for the entire ownership period?)
- `current_property.selling_strategy` — `sell_first` | `buy_first` | `simultaneous`
- `budget.buy_max` — target new property price ceiling (EUR)
- `budget.monthly_payment_max` — max monthly payment for new mortgage (EUR)
- `finance.annual_income` — gross annual income (EUR)

**If `buyer_type` is not `upgrader`:**
Output: "This mode is for movers/trader-ups (buyer_type: upgrader). For general purchase analysis use buy mode, for first-time buyer planning use afford mode." and stop.

**If any `current_property` field is null:**
Ask the user to provide the missing value(s) before proceeding.

---

## Section 2: Track A — Selling the Current Property

### 2a: Capital Gains Tax (CGT) Assessment

Irish CGT rules for property:
- **Principal Private Residence (PPR) relief:** If the property was your main home for the entire period of ownership → full CGT exemption. No tax on the gain.
- **Partial PPR relief:** If you lived in it for part of the ownership period → proportional exemption. The last 12 months of ownership always qualify for relief regardless.
- **Non-PPR (investment property):** 33% CGT on the gain (sale price minus purchase price minus allowable costs).
- **Annual CGT exemption:** First EUR 1,270 of gains per year is exempt.

Calculation:
- If `current_property.is_ppr = true`:
  - Estimated CGT = EUR 0 (full PPR exemption)
  - Note: "As your principal private residence for the full ownership period, this sale is exempt from CGT."
- If `current_property.is_ppr = false`:
  - Estimated gain = `estimated_value - purchase_price` (if purchase price unknown, assume gain = estimated_value x 15%)
  - Allowable deductions: stamp duty paid on purchase, legal fees, cost of improvements (ask user or estimate ~5% of purchase price)
  - Taxable gain = gain - deductions - EUR 1,270 (annual exemption)
  - CGT = taxable gain x 33%

### 2b: Net Proceeds Table

| Item | Amount |
|------|--------|
| Estimated sale price | EUR {estimated_value} |
| Outstanding mortgage | -EUR {loan_remaining} |
| Estate agent fees (~1-2% + VAT at 23%) | -EUR {agent_fee} |
| Solicitor/conveyancing fees (~EUR 2,000-3,000 + VAT) | -EUR {legal_fee} |
| CGT (if applicable) | -EUR {cgt} |
| **Net proceeds** | **EUR {net}** |

Prose: Explain key assumptions. Estate agent fees in Ireland are typically 1-2% of sale price plus 23% VAT. Solicitor fees for sale are typically EUR 2,000-3,000 plus VAT and outlays. Recommend getting a formal valuation and consulting a tax adviser for precise CGT calculation. Note that if selling a non-PPR property, CGT payment deadlines apply (preliminary tax within the year of disposal).

---

## Section 3: Track B — Buying the New Property

### 3a: Central Bank Rules for Movers

Non-first-time buyer rules (stricter than FTB):
- Max mortgage: 3.5x gross annual income
- Min deposit: 20%
- No access to Help to Buy or First Home Scheme

Max mortgage from income: `annual_income x 3.5`

### 3b: Deposit Requirement and Gap Analysis

For each deposit scenario using `budget.buy_max`:

| Scenario | Target price | Deposit required (20%) | Net proceeds available | Gap / Surplus |
|----------|-------------|----------------------|----------------------|---------------|
| Standard 20% deposit | EUR {buy_max} | EUR {buy_max x 20%} | EUR {net} | EUR {gap or "No gap"} |
| Higher deposit 30% | EUR {buy_max} | EUR {buy_max x 30%} | EUR {net} | EUR {gap or "No gap"} |

Gap = required deposit - net proceeds (positive = shortfall, negative = surplus)

### 3c: New Mortgage Estimate

For the scenario where net proceeds cover the deposit:
- Mortgage required = target price - deposit (from proceeds)
- Check: does mortgage exceed 3.5x income? If yes → flag as Warning
- Monthly payment calculations:

| Loan amount | Rate | Monthly payment (30 years) | Monthly payment max | Affordable? |
|------------|------|---------------------------|--------------------|----|
| EUR {loan} | 3.2% Fixed | EUR {monthly_fixed} | EUR {max} | Yes/Warning |
| EUR {loan} | 3.8% Variable | EUR {monthly_var} | EUR {max} | Yes/Warning |

### 3d: Stamp Duty on New Purchase

- 1% on first EUR 1,000,000
- 2% on balance above EUR 1,000,000
- Total stamp duty: EUR {stamp_duty}
- Note: this must be funded in addition to the deposit

### 3e: Total Cash Needed

| Item | Amount |
|------|--------|
| Deposit (20%) | EUR {deposit} |
| Stamp duty | EUR {stamp_duty} |
| Solicitor fees (~EUR 3,000-4,000 + VAT) | EUR {legal} |
| Valuation fee (~EUR 150-300) | EUR {valuation} |
| Survey/snag list (~EUR 300-500) | EUR {survey} |
| **Total cash needed** | **EUR {total}** |
| Net proceeds from sale | -EUR {net_proceeds} |
| **Additional cash required** | **EUR {additional}** |

---

## Section 4: Strategy Comparison

| Strategy | Pros | Cons | Financial risk | Best when |
|----------|------|------|---------------|-----------|
| **Sell first** | Funds are certain, no bridging finance needed; stronger negotiating position as chain-free buyer | Need interim accommodation (rent or stay with family); risk of prices rising while searching; stressful timeline | Low | Cash-constrained; uncertain market; mortgage approval conditional on sale |
| **Buy first** | Seamless move, no interim housing; can take time finding the right property | Bridging finance may be needed (expensive, ~5-7% interest); carrying two mortgages temporarily; pressure to sell quickly | High | Substantial equity/savings; confident current property will sell quickly; strong market |
| **Simultaneous** | Single move, no interim period; shortest overall timeline | Complex coordination; chain dependencies; risk of one side falling through; limited negotiation flexibility | Medium | Stable market; experienced solicitor managing both transactions; property already sale-agreed |

**Irish market considerations:**
- Average time to sell in Ireland: 4-8 weeks in Dublin, longer outside Dublin
- Conveyancing typically takes 6-12 weeks from sale agreed to closing
- Bridging finance is available from some Irish lenders but is expensive and not widely offered
- "Sale agreed" is not legally binding until contracts are exchanged — either party can withdraw

**For your situation** row: Based on the user's net proceeds, gap analysis, and `current_property.selling_strategy` preference, which strategy fits best? Add a row:

| **Your situation** | {tailored analysis based on numbers} | {main risk} | {calculated risk level} | {recommendation} |

---

## Section 5: Recommendation

Prose:
1. **Net proceeds summary:** Are the estimated net proceeds sufficient for the target deposit plus costs?
2. **Strategy recommendation:** Given the numbers, which strategy minimises risk? Align with or challenge the user's stated `selling_strategy` preference if numbers suggest otherwise.
3. **Key risks to flag:**
   - If non-PPR and short holding period: CGT at 33% significantly reduces proceeds
   - If gap is large: bridging finance is expensive and hard to obtain in Ireland; consider reducing target price
   - If monthly payment > monthly_payment_max: budget adjustment needed
   - If mortgage exceeds 3.5x income: Central Bank limit will prevent approval without an exception (banks can grant exceptions for up to 20% of lending)
4. **Tax planning:** If selling a non-PPR property, consider timing of sale relative to tax year for CGT payment scheduling. Recommend consulting a tax adviser.
5. **Suggested next steps:** When ready to evaluate specific properties, use `buy` mode. Use `scan` to search target areas.

**Output only** — no report file, no TSV, no tracker entry.
