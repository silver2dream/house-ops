# house-ops

AI-powered house hunting pipeline built on Claude Code. Automates listing discovery, evaluation, and tracking across the full search lifecycle — from scanning property portals, through structured evaluation against your budget and lifestyle criteria, to managing a tracker of every property you've considered.

Forked from [kylinfish/tw-house-ops](https://github.com/kylinfish/tw-house-ops) (Taiwan version). This fork adds multi-country support and several improvements.

Supports three user types: **Renter**, **First-Time Buyer**, **Mover/Upgrader**.

---

## Branches

| Branch | Country | Portals | Currency |
|--------|---------|---------|----------|
| `main` | Taiwan | 591, Rakuya, Sinyi, Yungching, Ethouse, JJHouse | TWD |
| `ireland` | Ireland | Daft.ie, MyHome.ie, Property.ie, SherryFitzGerald, Lisney | EUR |

## What's Improved Over Upstream

### Browser Automation
- **`agent-browser` → `playwright-cli`** migration — 4x fewer tokens per session, snapshots saved to disk instead of flooding context window, Microsoft-backed with active maintenance
- **Daft.ie API integration** (`daft-scan.py`) — bypasses Cloudflare CAPTCHA entirely by calling the internal API directly, returns complete data (BER ratings, floor area, GPS coordinates, price history) without browser automation

### Pipeline Enhancements
- **PDF report generation** via `md-to-pdf` — evaluation reports exported to `output/` for offline review
- **API-first scanning** — direct API calls where available (e.g., Daft.ie gateway API) for faster, more reliable data extraction vs. browser scraping

### Ireland Branch (`ireland`)
- Full adaptation for the Irish property market: EUR/m², BER ratings, Central Bank mortgage rules (4x FTB / 3.5x mover), Help to Buy, First Home Scheme, Stamp Duty, CGT, RPZ, RTB
- Irish portals: Daft.ie, MyHome.ie, Property.ie, SherryFitzGerald, Lisney
- Dublin transport: Luas, DART, Dublin Bus, Irish Rail
- Property risk flags: pyrite, mica, asbestos, unauthorised extensions
- Property Price Register (PPR) as market comparison source

---

## Features

- **Scan** property portals for listings matching your criteria
- **Evaluate** each property: market price comparison, commute calculation, five-dimension scoring
- **Track** every property in a structured Markdown table
- **Calculate** affordability and financial planning
- **Prepare** viewing checklists and negotiation strategies from evaluation reports
- **Export** reports as PDF

---

## Prerequisites

Scanning and listing verification depend on `playwright-cli`:

```bash
npm install -g @playwright/cli@latest
playwright-cli install --skills
```

For the Ireland branch, also install the Daft.ie scanner:

```bash
pip install daftlistings requests
```

---

## Quick Start

1. Install prerequisites (see above)
2. Clone this repo and open it in Claude Code
3. Claude will detect missing config files and start the onboarding flow (7 steps, ~5 minutes)
4. Once set up, paste any listing URL to evaluate — or type `scan` to search your target areas

---

## Usage

| Input | Action |
|-------|--------|
| Paste a listing URL | Auto-detect rent / buy → evaluate → generate report |
| `scan` | Scan target area portals for new listings |
| `pipeline` | Batch-process all pending URLs in `data/pipeline.md` |
| `compare 001, 003` | Side-by-side comparison of two evaluated properties |
| `prepare visit for 001` | Generate viewing checklist and negotiation strategy |
| `affordability` | Calculate maximum affordable purchase price |
| `upgrade plan` / `move plan` | Sell + buy timing, tax implications, equity gap analysis |
| `tracker` | Show summary of all tracked properties |

---

## Scoring

Properties are scored across five dimensions, each rated 0–5:

| Dimension | Rent Weight | Buy Weight |
|-----------|-------------|------------|
| Price Reasonableness | 30% | 35% |
| Space & Layout | 20% | 20% |
| Location & Amenities | 25% | 20% |
| Property Condition | 15% | 15% |
| Risk & Potential | 10% | 10% |

Score interpretation: ≥4.0 → Recommend viewing | 3.5–3.9 → Worth considering | <3.5 → Recommend skipping

---

## Tracker Statuses

`Scanned` → `Evaluated` → `Visit` → `Visited` → `Offer` → `Negotiating` → `Signed` → `Done`

Also: `Skip` (filtered out), `Pass` (rejected after viewing), `Expired` (listing removed)

---

## Data Contract

**User layer** (never auto-overwritten): `config/profile.yml`, `modes/_profile.md`, `data/*`, `reports/*`, `output/*`

**System layer** (may update with releases): all mode files, `CLAUDE.md`, `*.mjs` scripts, `templates/*`

---

## Scripts

```bash
node merge-tracker.mjs           # Merge pending TSV files into tracker.md
node verify-pipeline.mjs         # Validate pipeline integrity
node dedup-tracker.mjs           # Remove duplicate tracker entries
python daft-scan.py --help       # Daft.ie API scanner (Ireland branch)
```

---

## Acknowledgements

- Original project: [kylinfish/tw-house-ops](https://github.com/kylinfish/tw-house-ops) — the Taiwan house hunting pipeline this fork is based on
- Inspired by: [santifer/career-ops](https://github.com/santifer/career-ops) — the ops-style approach to life decisions

---

## Principles

This system is designed for quality-focused house hunting, not volume browsing. Claude will never submit an offer, sign a contract, or send an application on your behalf without your explicit approval. Properties scoring below 3.5/5 will be flagged as not worth pursuing.

---

## Support This Project

If this tool has been helpful in your property search:

[![Sponsor](https://img.shields.io/badge/Sponsor-silver2dream-ea4aaa?logo=github-sponsors)](https://github.com/sponsors/silver2dream)

Also consider supporting the original author: [kylinfish on Ko-fi](https://ko-fi.com/kylinwin)
