# Pipeline Mode — Batch Pipeline Processor

<!-- Read modes/_shared.md first.
     Load country_config from config/country/{country}.yml. -->

**Execution recommendation:** Run this mode as a background subagent (`Agent` tool with `run_in_background: true`) to protect the main conversation context. Processing multiple listings generates substantial output.

---

## Overview

Processes all unchecked (`- [ ]`) entries in `data/pipeline.md`. For each entry: applies Phase 1 quick filter, routes qualified listings to full evaluation (rent or buy mode), and marks entries as done.

---

## Step 1: Read Pipeline

1. Read `data/pipeline.md`
2. Find all lines matching: `- [ ] {url} | {portal} | {area} | {type} | {price} | {size} | {layout}`
3. If no unchecked entries → output "Pipeline is empty. No pending listings to process." and stop
4. Log count: "Found {N} pending listings to evaluate."

---

## Step 2: Process Each Entry

For each `- [ ]` entry, in order:

### 2a: Parse entry fields

| Field | From entry |
|-------|-----------|
| URL | First field |
| Portal | Second field |
| Area | Third field |
| Type | Fourth field: detect rent vs buy |
| Price | Fifth field |
| Size | Sixth field (parse number, area unit from `country_config.market.area_unit`) |
| Layout | Seventh field |

### 2b: Apply Phase 1 Quick Filter

Check against `config/profile.yml`. For rent listings check `budget.rent_max`, for buy listings check `budget.buy_max`.

| Check | Rule |
|-------|------|
| Price | Parsed price > budget ceiling → skip |
| Size | Parsed size < `property.size_min` → skip |
| Floor | If floor visible in entry or URL → check vs `property.floor_min` (if defined) |
| Age | Usually not available at this stage — skip this check |

Check `modes/_profile.md` deal_breakers against the title/address fields.

**If any check fails:**
- Mark entry in pipeline.md: `- [x] SKIP: {reason} — {url}`
- Write a minimal TSV to `batch/tracker-additions/{num}-{slug}.tsv` with status `Skip`
- Continue to next entry

### 2c: Full Evaluation (if qualified)

**Note:** Full evaluation generates significant output. Consider whether to:
- Evaluate all entries in sequence (simpler but can be very long)
- Or ask the user how many to evaluate in one run if there are >5 entries

**For rent listings:**
- Follow all steps in `modes/rent.md` Phase 2 (Sections 3–9)
- Write the full report to `reports/`
- Write TSV to `batch/tracker-additions/`

**For buy listings:**
- Follow all steps in `modes/buy.md` Phase 2 (Sections 3–11)
- Write the full report to `reports/`
- Write TSV to `batch/tracker-additions/`

**Note on verification:** In batch mode, set `**Verification:** unconfirmed (batch mode)` in the report header because liveness checks are not always reliable for queued entries that may have aged.

### 2d: Mark entry as done

After evaluation (qualified or skip):
- Replace `- [ ]` with `- [x]` for that line in `data/pipeline.md`

---

## Step 3: Post-Processing

After all entries are processed:

1. **Run merge-tracker:**
   ```
   node merge-tracker.mjs
   ```
   This merges all newly written TSV files into `data/tracker.md`.

2. **Output summary table:**

```
Pipeline Complete — YYYY-MM-DD
===============================
Total processed: N listings
  Full evaluation: N (reports generated)
  Quick filter skip: N (SKIP)

Added to tracker:
  + {###} | {area} | {price} | {score}/5 | {status} | [Report](reports/{filename})
  ...

Skipped:
  - {url} — {reason}
  ...
```

**IMPORTANT — Human Review Output:**
After the summary table, always output a dedicated review section. For each qualified listing (score >= moderate threshold from `country_config.scoring.interpretation`), output the full report content inline — do NOT use file links. The user reads everything in the conversation, not in files.

Format:

```
## Human Review

| Priority | Property | Size | Price | Summary | Score | Listing |
|----------|----------|------|-------|---------|-------|---------|
| ** | {area} {address} | {size} | {price} | {one-line summary} | {score}/5 | [Link]({listing_url}) |
| *  | {area} {address} | {size} | {price} | {one-line summary} | {score}/5 | [Link]({listing_url}) |
...

---

### ** {###} {area} {address}
[Link]({listing_url})

{full report content — all sections}

---

### * {###} {area} {address}
[Link]({listing_url})

{full report content}

---
...
```

Priority rules (using thresholds from `country_config.scoring.interpretation`):
- ** = score >= excellent threshold (recommended for viewing)
- *  = score >= moderate threshold (worth considering)
- Omit listings scored below moderate threshold from this section entirely

---

## Notes

- **Order matters:** Process entries in the order they appear in pipeline.md (top to bottom).
- **Report numbering:** Each evaluation must check `reports/` for the current highest ### before writing, since earlier entries in the same batch will have incremented the counter.
- **Partial runs:** If the user interrupts mid-batch, already-checked entries (`- [x]`) will not be re-processed on the next run.
- **Error handling:** If a listing URL is unreachable or returns an error, mark it `- [x] ERROR: {reason}` and continue.
