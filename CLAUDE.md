# ie-house-ops — AI House Hunting Pipeline for Ireland

## What is ie-house-ops

ie-house-ops is an AI-powered real estate search pipeline built on Claude Code, designed for house hunters in Ireland. It automates listing discovery, evaluation, and tracking across the full search lifecycle — from scanning portals like Daft.ie, MyHome.ie, and Property.ie, through structured evaluation against your budget and lifestyle criteria, to managing a tracker of every property you've considered. It supports three buyer personas (renter, first-time buyer, mover), handles both rental and purchase markets, and produces structured reports so you can make informed decisions without drowning in listings.

---

## First-Session Checks

On every session start, run these checks **silently** (no output to the user unless action is needed):

1. Does `config/profile.yml` exist?
2. Does `portals.yml` exist?
3. Does `data/tracker.md` exist?
4. Does `data/pipeline.md` exist?
5. Does `modes/_profile.md` exist?
6. Is `playwright-cli` installed? Run `which playwright-cli` silently.

**If `modes/_profile.md` is missing** → silently copy from `modes/_profile.template.md`. This is the user's customization file and will never be overwritten by system updates.

**If any of the five main files are missing** → enter Onboarding mode (see next section). Do NOT run evaluations, scans, or any other mode until the basics are in place.

**If `playwright-cli` is not found** → warn the user immediately (this is NOT silent):
> Warning: `playwright-cli` is not installed. Scanning and listing verification features require it to function. Please run:
> ```bash
> npm install -g @playwright/cli@latest
> playwright-cli install --skills
> ```
> Restart Claude Code after installation. Without it, running `scan` or pasting a URL will produce unreliable scraping results, and subsequent evaluations may be based on stale or incorrect data.

---

## Onboarding Flow

Guide the user through these 7 steps in order. Do not skip ahead.

### Step 1: Search Mode

Ask:
> "Are you looking to **rent**, **buy**, or **both**?"

- Set `search.mode` to `rent`, `buy`, or `both`
- Set `buyer_type`:
  - Renting → `renter`
  - Buying, no existing property → `first_time_buyer`
  - Buying, already own a home → `mover`

### Step 2: Region + Budget

Ask:
> "Which counties or areas are you targeting? (e.g., Dublin 2, Dublin 4, Dun Laoghaire, Ranelagh, Cork City) And what's your budget?
> - For rent: monthly ceiling in EUR
> - For buy: max purchase price in EUR, and your max monthly mortgage payment in EUR"

Fill in:
- `regions[].county` and `regions[].areas`
- `budget.rent_max` (if renting) or `budget.buy_max` + `budget.monthly_payment_max` (if buying)

### Step 3: Commute Origin

Ask:
> "Where do you commute to? (Work address, school, or major landmark — used to filter by commute time.) What's the maximum commute you'd accept in minutes?"

Fill in:
- `user.commute_origin`
- `user.commute_max_minutes`

### Step 4a: First-Time Buyer Supplement (only if `buyer_type = first_time_buyer`)

Ask:
> "Since you're a first-time buyer, I need a few details to help with affordability and government scheme eligibility:
> - Gross annual salary (EUR)
> - Savings available for deposit (EUR)
> - Are you eligible for Help to Buy (HTB)? (new build only, tax refund up to EUR 30,000)
> - Are you interested in the First Home Scheme (FHS)? (shared equity up to 30%, new build, FTB only)"

Fill in `finance` block:
- `annual_income`, `savings`, `htb_eligible`, `fhs_interested`

Note: Central Bank rules for FTBs allow max 4x gross annual income, with 10% deposit required.

### Step 4b: Mover Supplement (only if `buyer_type = mover`)

Ask:
> "Since you're moving, I need a few details about your current property to help with timing and tax calculations:
> - Estimated current market value (EUR)
> - Outstanding mortgage balance (EUR)
> - Year you purchased it
> - Strategy: sell first, buy first, or simultaneous?"

Fill in `current_property` block:
- `estimated_value`, `loan_remaining`, `purchase_year`, `selling_strategy`

Note: Central Bank rules for second/subsequent buyers allow max 3.5x gross annual income, with 20% deposit required. Capital Gains Tax (CGT) at 33% applies on gains, but Principal Private Residence (PPR) relief exempts your own home.

### Step 5: Create Config Files

Using the answers from Steps 1–4, auto-create the following:

- **`config/profile.yml`** — copy from `config/profile.example.yml`, fill in user's answers
- **`data/tracker.md`** — create with header:
  ```markdown
  # Property Tracker

  | # | Date | Portal | Address | Type | Price | Size | Score | Status | Report | Notes |
  |---|------|--------|---------|------|-------|------|-------|--------|--------|-------|
  ```
- **`data/scan-history.tsv`** — create empty file (header only):
  ```
  url	first_seen	last_seen	status
  ```
- **`data/pipeline.md`** — create with header:
  ```markdown
  # Pipeline Inbox

  Paste listing URLs here, one per line. Claude will process them in order.

  ## Pending
  ```

### Step 6: Copy Portals Config

Auto-copy `portals.example.yml` → `portals.yml`. Tell the user:
> "I've copied the default portals configuration. You can customize which sites and search parameters to use by editing `portals.yml`, or just ask me."

### Step 7: Ready

Confirm setup is complete and offer an immediate scan:
> "You're all set! Here's what you can do now:
> - Paste a listing URL to evaluate it
> - Say 'scan' to search your target areas for new listings
> - Say 'pipeline' to process any pending URLs
> - Say 'tracker' to see your search summary
>
> Want me to scan for listings in your target areas right now?"

---

## Main Files

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Entry point — routing brain Claude reads every session |
| `config/profile.yml` | User preferences: budget, regions, commute, property criteria |
| `portals.yml` | Portal URLs, search queries, and scraping config |
| `data/pipeline.md` | Inbox of pending listing URLs to process |
| `data/tracker.md` | Master tracker of all evaluated properties |
| `data/scan-history.tsv` | Dedup log for scanner (url, first_seen, last_seen, status) |
| `reports/` | Individual evaluation reports (one per listing) |
| `modes/` | Mode files: rent.md, buy.md, afford.md, switch.md, compare.md, visit.md, scan.md, pipeline.md, _shared.md, _profile.md |

---

## Mode Routing

| If the user... | Mode |
|----------------|------|
| Pastes a URL | Auto-pipeline: detect rent vs buy → Phase 1 quick filter → Phase 2 full eval |
| Asks to evaluate a rental | `modes/rent.md` |
| Asks to evaluate a purchase | `modes/buy.md` |
| Wants an affordability calculation | `modes/afford.md` |
| Is planning a move (sell + buy) | `modes/switch.md` |
| Wants to compare two or more listings | `modes/compare.md` |
| Is preparing for a property viewing | `modes/visit.md` |
| Wants to scan portals for new listings | `modes/scan.md` |
| Asks about tracker / search status | Show `data/tracker.md` summary |
| Wants to process pending pipeline URLs | `modes/pipeline.md` |

**When `search.mode: both`:** Detect listing type from page content:
- Contains "per month" or "pcm" or monthly rent (without asking price) → treat as **rent** → use `modes/rent.md`
- Contains asking price without monthly rent → treat as **buy** → use `modes/buy.md`
- Ambiguous → ask user before proceeding

---

## Auto-Pipeline Logic

When the user pastes a URL, execute this sequence:

### 1. Verify Listing is Active

Use `playwright-cli` (via Bash tool):
```bash
playwright-cli goto {url}
playwright-cli snapshot
```

Interpretation:
- Only footer/navbar present, no listing content → listing **closed** → report "Listing no longer available" and stop
- Title + description + price + contact/apply section present → listing **active** → continue

**NEVER** rely on WebSearch or WebFetch alone to verify if a listing is active. Always use `playwright-cli`. If `playwright-cli` is not installed, stop and remind the user to install it before proceeding.

### 2. Detect Rent vs Buy

From page content:
- Monthly rent figure ("per month" / "pcm") + deposit → **rent**
- Asking price without monthly rent → **buy**
- Ambiguous → ask user

### 3. Phase 1 Quick Filter

Check these criteria against `config/profile.yml`. If any fail, mark **skip** and note the reason:

| Criterion | Profile field | Fail condition |
|-----------|---------------|----------------|
| Price | `budget.rent_max` / `budget.buy_max` | Listing price > budget ceiling |
| Size | `property.size_min` | Listed m² < minimum |
| Bedrooms | `property.bedrooms_min` | Bedrooms < minimum |
| BER rating | `property.ber_max` | BER worse than maximum (e.g., listing is F, limit is D) |

### 4. Phase 2: Full Evaluation

If the listing passes Phase 1:
- Rent listing → load and follow `modes/rent.md`
- Buy listing → load and follow `modes/buy.md`

After evaluation:
- Write evaluation report to `reports/` (see Report Conventions)
- Write TSV entry to `batch/tracker-additions/`
- Run `node merge-tracker.mjs`

### 5. Skip Handling

If Phase 1 disqualifies the listing:
- Output a one-line summary: "Skipped: [reason] ([value] vs limit [limit])"
- Do NOT write a full evaluation report
- Optionally write a minimal TSV entry with status `Skip`

---

## Report Conventions

### Naming

```
{###}-{area}-{road-slug}-{YYYY-MM-DD}.md
```

- `{###}`: sequential 3-digit zero-padded integer (max existing report number + 1)
- `{area}`: area name lowercase (e.g., `d2`, `d4`, `ranelagh`, `stillorgan`, `cork-city`, `dun-laoghaire`)
- `{road-slug}`: road/street name lowercase hyphenated (e.g., `merrion-sq`, `baggot-st`, `grafton-st`); if ambiguous or unresolvable, use `road-{4-char-hex}` (e.g., `road-3a7f`)
- `{YYYY-MM-DD}`: evaluation date

Examples:
- `001-d2-merrion-sq-2025-04-08.md`
- `042-ranelagh-chelmsford-rd-2025-04-08.md`
- `015-cork-city-road-3a7f-2025-04-08.md`

### Required Report Header

Every report must include these fields at the top:

```markdown
**URL:** {listing url}
**Score:** {X.X}/5
**Type:** rent | buy
**Status:** {canonical status}
**Verification:** confirmed | unconfirmed (batch mode)
```

### Location

All reports go in `reports/`. Output files (PDFs, etc.) go in `output/` (gitignored).

### After Writing Report

1. Write TSV to `batch/tracker-additions/{num}-{slug}.tsv`
2. Run `node merge-tracker.mjs`

---

## Pipeline Integrity Rules

1. **NEVER write new entries directly to `data/tracker.md`.** Always write a TSV file to `batch/tracker-additions/{num}-{slug}.tsv` and run `node merge-tracker.mjs` to merge. This prevents duplicates and maintains consistent formatting.

2. **Direct edits to `data/tracker.md` are allowed** for updating the `status` or `notes` columns of existing entries. Do not add new rows manually.

3. **`verify-pipeline.mjs`** — run to validate:
   - All reports in `reports/` have a matching tracker entry
   - No unmerged TSV files remain in `batch/tracker-additions/`
   - All statuses are canonical (per `templates/states.yml`)

4. **`dedup-tracker.mjs`** — removes duplicate tracker entries by normalized address. Run if duplicates are suspected.

5. **`merge-tracker.mjs`** — reads all TSV files from `batch/tracker-additions/`, appends rows to `data/tracker.md`, then archives processed TSVs to `batch/tracker-additions/processed/`.

### TSV Format

One file per evaluation: `batch/tracker-additions/{num}-{slug}.tsv`

Single line, tab-separated, 11 columns matching tracker.md headers:

```
{num}\t{date}\t{platform}\t{address}\t{type}\t{price}\t{size}\t{score}/5\t{status}\t{report-link}\t{notes}
```

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

Rules:
- No markdown bold in status field
- No dates in status field (use the date column)
- No extra text in status field (use the notes column)

---

## Ireland Market Reference

### Mortgage Rules (Central Bank of Ireland)
- **First-time buyers (FTB):** max 4x gross annual income, 10% deposit required
- **Second/subsequent buyers:** max 3.5x gross annual income, 20% deposit required
- **Typical rates:** Variable ~3.5-4.5%, Fixed ~3.0-4.0%

### Taxes and Costs
- **Stamp duty:** 1% on first EUR 1M, 2% above EUR 1M (residential)
- **Local Property Tax (LPT):** Annual tax based on property value
- **Capital Gains Tax (CGT):** 33% on gains; Principal Private Residence (PPR) exemption for your own home
- **Solicitor fees:** Typically EUR 2,000-4,000 for conveyancing
- **Surveyor:** Pre-purchase structural survey typically EUR 300-600

### Government Schemes (Buyers)
- **Help to Buy (HTB):** FTB of new builds only, tax refund up to EUR 30,000 (10% of price, max EUR 500k property)
- **First Home Scheme (FHS):** Government shared equity up to 30% for new builds, FTB only

### Rental Market
- **Rent Pressure Zones (RPZ):** Limits rent increases to max 2% per year in designated areas
- **RTB (Residential Tenancies Board):** Regulates all private residential tenancies
- **HAP (Housing Assistance Payment):** Government rental support scheme
- **Standard deposit:** 1 month's rent

### Key Resources
- **Property Price Register (PPR):** propertypriceregister.ie — Ireland's transaction price database
- **BER (Building Energy Rating):** A1 (best) to G (worst) — critical for energy costs
- **PSRA:** Property Services Regulatory Authority — licenses estate agents/auctioneers

### Portals
- **Daft.ie** — dominant portal for both rent and buy
- **MyHome.ie** — strong buy listings, Irish Times affiliated
- **Property.ie** — additional buy listings
- **SherryFitzGerald.ie** — major estate agent chain
- **Lisney.com** — established Dublin-focused agent

### Transport (Dublin)
- **Luas:** Light rail (Green Line / Red Line)
- **DART:** Suburban rail along the coast
- **Dublin Bus / Bus Connects:** City and suburban bus network
- **Bus Eireann:** Regional/intercity bus
- **Irish Rail:** National rail network

---

## Data Contract

### User Layer (NEVER auto-overwritten)

These files contain your personal data. System updates will never touch them:

- `config/profile.yml`
- `modes/_profile.md`
- `data/*` (tracker, pipeline, scan history)
- `reports/*`
- `output/*`

### System Layer (auto-updatable)

These files are part of the system and may be updated:

- `modes/_shared.md` and all mode files except `modes/_profile.md`
- `CLAUDE.md`
- `*.mjs` scripts
- `templates/*`

### The Rule

**When the user asks to customize anything** (regions, budget, deal-breakers, lifestyle priorities, commute limits), ALWAYS write to `config/profile.yml` or `modes/_profile.md`. NEVER edit `modes/_shared.md` for user-specific content. This ensures system updates don't overwrite their customizations.

---

## Ethical Use

**This system is for quality-focused house hunting, not volume browsing.**

- **NEVER submit, sign, or send a contract, offer, or application without the user reviewing and explicitly approving it first.** Fill forms, draft cover letters, prepare offer summaries — but always STOP before any final action. The user makes the final call.

- **Strongly discourage low-fit properties.** If a score is below **3.5/5**, explicitly recommend against pursuing. The user's time (and the landlord's/agent's time) is valuable. Only proceed if the user has a specific reason to override.

- **Quality over quantity.** Five well-matched properties are worth more than fifty random ones. Guide the user toward fewer, better-targeted evaluations.
