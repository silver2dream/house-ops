# Compare Mode — Multi-Listing Comparison

<!-- Read modes/_shared.md first.
     Load country_config from config/country/{country}.yml.
     No new report file is written — this compares existing evaluated reports. -->

---

## Overview

Side-by-side comparison of 2 or more evaluated properties. Reads existing reports, normalizes prices to per-area-unit (using `country_config.market.area_unit`), ranks by score, and produces a decision recommendation.

---

## Section 1: Input

Accepted input formats:
- **Specific reports:** "compare 001, 003, 007" → compare those three reports
- **All Evaluated:** "compare all Evaluated" → find all tracker entries with status `Evaluated`, load those reports

### Resolve report files

For each report number:
1. Search `reports/` for a file starting with `{###}-` (zero-padded)
2. If not found → "Report {###} not found. Please verify the report number." and skip that entry
3. If fewer than 2 valid reports → "At least 2 reports are needed for comparison." and stop

---

## Section 2: Data Extraction

For each report file, extract:

| Field | Where to find it |
|-------|-----------------|
| Report # | Filename prefix |
| Type | rent / buy (from report Type header) |
| Address | From report header table |
| Price | Total price or monthly rent from report |
| Size | From report header table |
| Price per unit | Calculate: price / size (using area unit from `country_config.market.area_unit_symbol`) |
| Overall score | From dimension scores table (overall row) |
| Dimension 1–5 scores | From dimension scores table (use dimension keys from `country_config.scoring.dimensions`) |
| Commute time | From commute table (first row, estimated minutes) |
| Top red flags | Top 1-2 items from red flags section |
| Status | From tracker.md |

If a field can't be extracted, mark it as `—`.

---

## Section 3: Comparison Table

All listings as columns, all dimensions as rows. Highlight the best value in each row.

```markdown
## Property Comparison

| Field | 001 | 003 | 007 |
|-------|-----|-----|-----|
| Address | {address} | {address} | {address} |
| Type | rent/buy | | |
| Price | {price} | | |
| Size | {size} {area_unit} | | |
| **Price per unit** | {per_unit} | | |
| Commute | {mins} min | | |
| **Overall score** | **{total}/5** | | |
| {dimension 1 name} | {d1}/5 | | |
| {dimension 2 name} | {d2}/5 | | |
| {dimension 3 name} | {d3}/5 | | |
| {dimension 4 name} | {d4}/5 | | |
| {dimension 5 name} | {d5}/5 | | |
| Top red flags | {issue} | | |
```

Use dimension names from `country_config.scoring.dimensions` (local or English depending on report language). Bold the best value in each row (e.g., highest score, lowest price per unit, shortest commute).

---

## Section 4: Ranking

Sort listings by overall score descending. Present as a ranked list:

```
1st — Report 003 — {area} {road} — 4.3/5
2nd — Report 007 — {area} {road} — 3.9/5
3rd — Report 001 — {area} {road} — 3.5/5
```

---

## Section 5: Verdict Table

Per listing: biggest advantage, biggest concern, recommended action.

| Report | Biggest advantage | Biggest concern | Recommended action |
|--------|-------------------|-----------------|-------------------|
| 001 | {e.g., lowest price per unit} | {e.g., longest commute} | View / Skip / Already viewed |
| 003 | {e.g., highest overall score} | {e.g., older building} | View / Skip / Already viewed |
| 007 | {e.g., shortest commute} | {e.g., smallest size} | View / Skip / Already viewed |

Recommended action logic (using thresholds from `country_config.scoring.interpretation`):
- Score >= excellent threshold → Priority viewing
- Score >= moderate threshold → Optional viewing
- Score < moderate threshold → Recommend skipping
- Status already `Visited` or beyond → note current status

---

## Section 6: Decision Recommendation

Prose recommendation:

**If you can only visit one:** "If you can only visit one property, prioritize Report {###} — {reason based on scores and user priorities from _profile.md}."

**Trade-off analysis:** For the top 2: "Report {A} scores better on {dimension}, but Report {B} has the advantage on {dimension}. If you prioritize {X}, choose {A}; if you prioritize {Y}, choose {B}."

**Skip confirmation:** If any listing scored below the moderate threshold: "Report {###} scored below the recommended threshold. Consider updating its status to Skip in the tracker."

**Output only** — no new report file, no TSV, no tracker changes (tracker status updates require explicit user instruction).
