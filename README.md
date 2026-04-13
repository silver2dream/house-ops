# ie-house-ops

AI house hunting pipeline for Ireland, built on Claude Code. Automates listing discovery, evaluation, and tracking across the full search lifecycle for both rental and purchase markets.

Supports three user types: **Renter**, **First-Time Buyer (FTB)**, **Mover** (upgrader/trader-up).

> Inspired by [santifer/career-ops](https://github.com/santifer/career-ops) — same ops-style approach, applied to house hunting in Ireland.

![Property Tracker](demo-images/tracker-demo.png)

---

## Features

- **Scan** Daft.ie, MyHome.ie, Property.ie, SherryFitzGerald.ie, and Lisney.com for listings matching your criteria
- **Evaluate** each property: compare against Property Price Register data, commute calculation, five-dimension scoring
- **Track** every property you've considered in a structured Markdown table
- **Calculate** affordability (FTB: Central Bank limits, HTB, First Home Scheme) and move planning (mover: sell + buy timing, CGT, equity release)
- **Prepare** viewing checklists and negotiation strategies from evaluation reports

---

## Prerequisites

Scanning (`scan`) and listing verification depend on `playwright-cli` — **you must install it before use**:

```bash
npm install -g @playwright/cli@latest
playwright-cli install --skills
```

Confirm installation:

```bash
playwright-cli --version
```

> Without `playwright-cli`, running `scan` or pasting a URL means Claude cannot scrape live page content, and subsequent evaluations will be unreliable. Claude Code checks for this automatically on every session start.

---

## Quick Start

1. Install `playwright-cli` (see above)
2. Clone this repo and open it in Claude Code
3. Claude will detect missing config files and start the onboarding flow (7 steps, about 5 minutes)
4. Once set up, paste any listing URL to evaluate it — or type `scan` to search your target areas

---

## Usage

| Input | Action |
|-------|--------|
| Paste a listing URL | Auto-detect rent / buy → evaluate → generate report |
| `scan` | Scan target area portals for new listings |
| `pipeline` | Batch-process all pending URLs in `data/pipeline.md` |
| `compare 001, 003` | Side-by-side comparison of two evaluated properties |
| `prepare visit for 001` | Generate viewing checklist and negotiation strategy for report 001 |
| `affordability` | Calculate maximum affordable purchase price (FTB: Central Bank 4x rule, deposit, HTB/FHS) |
| `move plan` | Move planning: sell current + buy new — timing, CGT, equity gap analysis (mover) |
| `tracker` | Show summary of all tracked properties |

---

## Demo

### Pipeline Batch Evaluation Output

After a batch run, Claude outputs a summary table with top recommendations and links to each listing for manual review.

![Pipeline Processing Summary](demo-images/pipeline-summary-demo.png)

### Property Evaluation Report

Each property gets a full report: price analysis (with Property Price Register comparison), commute calculation, five-dimension score, red flags, and viewing question list.

![Report Details 1](demo-images/report-details-1.png)

![Report Details 2](demo-images/report-details-2.png)

![Report Details 3](demo-images/report-details-3.png)

---

## Directory Structure

```
ie-house-ops/
├── CLAUDE.md                    # Entry point: mode routing, onboarding, data contract
├── config/
│   ├── profile.yml              # Personal settings (never overwritten by system updates)
│   └── profile.example.yml      # Settings template
├── portals.yml                  # Portal URLs and scanning config
├── modes/
│   ├── _shared.md               # Scoring dimensions, Ireland market knowledge
│   ├── _profile.md              # Personal context (injected into every evaluation)
│   ├── _profile.template.md     # Initial template for _profile.md
│   ├── scan.md                  # Portal scanner
│   ├── rent.md                  # Rental evaluation
│   ├── buy.md                   # Purchase evaluation
│   ├── afford.md                # Affordability calculator
│   ├── switch.md                # Move planning (sell + buy)
│   ├── compare.md               # Multi-property comparison
│   ├── visit.md                 # Viewing checklist and post-visit notes
│   └── pipeline.md              # Batch evaluation processor
├── data/
│   ├── pipeline.md              # Pending URL inbox
│   ├── tracker.md               # Master property tracker
│   └── scan-history.tsv         # Dedup log (gitignored)
├── reports/                     # Individual evaluation reports
├── batch/tracker-additions/     # Pending TSV files for merge
├── templates/states.yml         # Canonical tracker statuses
├── merge-tracker.mjs            # Merge TSV files into tracker.md
├── verify-pipeline.mjs          # Validate pipeline integrity
└── dedup-tracker.mjs            # Remove duplicate tracker entries
```

---

## Scoring

Properties are scored across five dimensions, each rated 0-5:

| Dimension | Rent Weight | Buy Weight |
|-----------|-------------|------------|
| Price fairness | 30% | 35% |
| Space and layout | 20% | 20% |
| Location and amenities | 25% | 20% |
| Property condition | 15% | 15% |
| Risk and potential | 10% | 10% |

Score interpretation: >=4.0 → recommend viewing | 3.5-3.9 → proceed with reservations | <3.5 → recommend skipping

---

## Tracker Statuses

`Scanned` → `Evaluated` → `Visit` → `Visited` → `Offer` → `Negotiating` → `Signed` → `Done`

Also: `Skip` (filtered out), `Pass` (rejected after viewing), `Expired` (listing removed)

---

## Ireland Market Context

### Key Portals
- **Daft.ie** — dominant portal (rent and buy)
- **MyHome.ie** — strong for sales, Irish Times affiliated
- **Property.ie** — additional sales listings
- **SherryFitzGerald.ie** / **Lisney.com** — major estate agent sites

### Mortgage Rules (Central Bank of Ireland)
- FTB: max 4x gross annual income, 10% deposit
- Second/subsequent buyer: max 3.5x gross annual income, 20% deposit

### Government Schemes
- **Help to Buy (HTB):** FTB, new builds only, up to EUR 30,000
- **First Home Scheme (FHS):** Shared equity up to 30%, FTB, new builds only

### Important References
- **Property Price Register:** propertypriceregister.ie (transaction history)
- **BER Rating:** A1 (best) to G (worst) — affects energy costs significantly
- **RTB:** Residential Tenancies Board (rental regulations)
- **PSRA:** Property Services Regulatory Authority (agent licensing)

---

## Data Contract

**User layer** (never auto-overwritten): `config/profile.yml`, `modes/_profile.md`, `data/*`, `reports/*`

**System layer** (may update with releases): all mode files, `CLAUDE.md`, `*.mjs` scripts, `templates/*`

---

## Scripts

```bash
node merge-tracker.mjs           # Merge pending TSV files into tracker.md
node verify-pipeline.mjs         # Validate pipeline integrity
node dedup-tracker.mjs           # Remove duplicate tracker entries
node --test tests/**/*.test.mjs  # Run all tests
```

---

## Principles

This system is designed for quality-focused house hunting, not volume browsing. Claude will never submit an offer, sign a contract, or send an application on your behalf without your explicit approval. Properties scoring below 3.5/5 will be flagged as not worth pursuing.

---

## Support This Project

If this tool has been helpful in your property search, feel free to buy me a coffee.

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/kylinwin)
