# Compare Mode — Multi-Listing Comparison

<!-- Read modes/_shared.md first. -->
<!-- No new report file is written — this compares existing evaluated reports. -->

---

## Overview

Side-by-side comparison of 2 or more evaluated properties. Reads existing reports, normalises prices to per-m², ranks by score, and produces a decision recommendation.

---

## Section 1: Input

Accepted input formats:
- **Specific reports:** "compare 001, 003, 007" → compare those three reports
- **All Evaluated:** "compare all Evaluated" → find all tracker entries with status `Evaluated`, load those reports

### Resolve report files

For each report number:
1. Search `reports/` for a file starting with `{###}-` (zero-padded)
2. If not found → "Report {###} not found — please check the report number." and skip that entry
3. If fewer than 2 valid reports → "At least 2 reports are required for comparison." and stop

---

## Section 2: Data Extraction

For each report file, extract:

| Field | Where to find it |
|-------|-----------------|
| Report # | Filename prefix |
| Type | rent / buy (from report Type header) |
| Address | From report header table |
| Price / Rent | From report header table |
| Size (m²) | From report header table |
| EUR/m² | Calculate: total price / m² (buy) or monthly rent / m² (rent) |
| Overall Score | From scoring table (Overall row) |
| Value for Money | From scoring table |
| Space & Layout | From scoring table |
| Local Amenities | From scoring table |
| Property Condition | From scoring table |
| Risk / Potential | From scoring table |
| Commute Time | From commute assessment table (first row, estimated minutes) |
| Key Concerns | Top 1-2 items from concerns list |
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
| Price / Rent | {price} | | |
| Size | {size} m² | | |
| **EUR/m²** | {per_sqm} | | |
| Commute Time | {mins} mins | | |
| **Overall Score** | **{total}/5** | | |
| Value for Money | {d1}/5 | | |
| Space & Layout | {d2}/5 | | |
| Local Amenities | {d3}/5 | | |
| Property Condition | {d4}/5 | | |
| Risk / Potential | {d5}/5 | | |
| Key Concerns | {issue} | | |
```

Bold the best value in each row (e.g., highest score, lowest EUR/m², shortest commute).

---

## Section 4: Ranking

Sort listings by Overall Score descending. Present as a ranked list:

```
1. Report 003 — Dublin 2, Pembroke Rd — 4.3/5
2. Report 007 — Ranelagh, Chelmsford Rd — 3.9/5
3. Report 001 — Drumcondra, Iona Rd — 3.5/5
```

---

## Section 5: Verdict Table

Per listing: biggest advantage, biggest concern, recommended action.

| Report | Biggest Advantage | Biggest Concern | Recommended Action |
|--------|-------------------|-----------------|-------------------|
| 001 | {e.g., lowest EUR/m²} | {e.g., longest commute} | View / Skip / Already viewed |
| 003 | {e.g., highest overall score} | {e.g., older building} | View / Skip / Already viewed |
| 007 | {e.g., shortest commute} | {e.g., small size} | View / Skip / Already viewed |

Recommended action logic:
- Score >= 4.0 → Priority viewing
- Score 3.5–3.9 → Backup option
- Score < 3.5 → Recommend skip
- Status already `Visited` or beyond → note current status

---

## Section 6: Decision Recommendation

Prose recommendation:

**If you can only visit one:** "If you can only view one property, prioritise Report {###} — {reason based on scores and user priorities from _profile.md}."

**Trade-off analysis:** For the top 2: "Report {A} scores higher on {dimension}, but Report {B} has the edge on {dimension}. If {X} matters more to you, go with {A}; if {Y} is the priority, choose {B}."

**Skip confirmation:** If any listing scored < 3.5: "Report {###} scored below 3.5 — recommend removing from consideration. You can update its tracker status to Skip."

**Output only** — no new report file, no TSV, no tracker changes (tracker status updates require explicit user instruction).
