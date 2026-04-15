# Scan Mode — Portal Scanner

<!-- Read modes/_shared.md before executing this mode.
     Load country_config from config/country/{country}.yml. -->

**Execution recommendation:** Run this mode as a background subagent (`Agent` tool with `run_in_background: true`) to protect the main conversation context. Scanning multiple portals can take significant time.

---

## Overview

Three-level scanning strategy:
- **Level 1 — playwright-cli direct** (primary): Navigate each tracked portal's search results
- **Level 2 — Market reference API** (reference only): Used during evaluation, NOT here — never populates pipeline.md. Refer to `country_config.market_reference.price_register` for what this source is.
- **Level 3 — WebSearch** (broad discovery): site: queries to find listings outside tracked portals

---

## Step 1: Read Configuration

1. Read `config/profile.yml`:
   - `country` → load `config/country/{country}.yml`
   - Target regions from profile
   - `budget.rent_max` → rental ceiling
   - `budget.buy_max` → purchase ceiling
   - `property.size_min` → minimum size
   - `search.mode` → `rent` | `buy` | `both`

2. Read `portals.yml`:
   - `tracked_portals[]` where `enabled: true`
   - `title_filter.property_types.include` and `.exclude`
   - `title_filter.price.rent_max`, `.buy_max`, `.size_min`
   - `search_queries[]` for Level 3

3. Filter portals by `search.mode`:
   - `rent` → only portals with `type: rent`
   - `buy` → only portals with `type: buy`
   - `both` → all enabled portals

---

## Step 2: Level 1 — playwright-cli Direct Scan (Primary)

**Prerequisite:** `playwright-cli` must be installed (`npm install -g @playwright/cli@latest`). If not found, stop and remind the user before proceeding.

For each enabled portal matching the search mode:

### If portal has `url_template`:

Substitute values from profile into the URL template. Use region codes from `country_config.regions.region_codes` if the template requires them. Substitute budget and size values from the profile.

Then:
```bash
playwright-cli goto {constructed_url}
playwright-cli snapshot
```

### If portal has `base_url`:

```bash
playwright-cli goto {base_url}
playwright-cli snapshot
```

Then interact with the site's search filters to apply area/price/size criteria:
```bash
# Fill filter fields and submit search
playwright-cli fill {filter_input} "{value}"
playwright-cli click {search_button}
playwright-cli snapshot
playwright-cli snapshot
```

### Extraction (both methods):

From the search results page, extract each listing:
- `title`: listing title text
- `url`: full listing URL (absolute)
- `address`: street address or area + road
- `price`: price string (formatted in country's currency)
- `size`: size in country's area unit
- `layout`: bedroom/bathroom layout
- `portal`: the portal name from portals.yml

### Pagination:

If results show a "next page" control (look for standard pagination elements — the text varies by language and portal):
```bash
playwright-cli click "getByText('{next_page_text}')"
playwright-cli snapshot
playwright-cli snapshot
```

Continue extracting until:
- No more pages, or
- All results are below the size_min threshold (stop early)

---

## Step 3: Level 3 — WebSearch Discovery (Secondary)

For each `search_queries[]` entry in portals.yml (where `enabled: true`):

1. Substitute template values into `query` from the profile (target areas, budget values)

2. Run WebSearch with the substituted query

3. For each result URL: **verify liveness with `playwright-cli`** before considering it:
   ```bash
   playwright-cli goto {url}
   playwright-cli snapshot
   ```
   Check for expired signals:
   - URL contains error parameters
   - Page content contains "no longer available" or equivalent (check `country_config.report_labels.inactive_listing` for localized text)
   - Content is < 300 characters (only nav/footer, no listing body)

   Only proceed if listing appears active.

---

## Step 4: Phase 1 Quick Filter

Apply to every extracted listing (both Level 1 and Level 3). Check against `portals.yml title_filter` (these are loose scanner ceilings, not the precise profile values):

| Check | Rule | Result |
|-------|------|--------|
| Property type | Title contains an excluded type (from `country_config.property_types.exclude` or portals.yml filter) | `skipped_title` |
| Price | Price > title_filter price ceiling | `skipped_title` |
| Size | Size < title_filter size_min | `skipped_title` |
| Passes all | — | `qualified` |

---

## Step 5: Deduplication

For each `qualified` listing, check against `data/scan-history.tsv`:

**Layer 1 — URL exact match:**
- If the listing URL already exists with status `added` → `skipped_dup`

**Layer 2 — Normalized address match:**
- Normalize the listing's address using the rules from `country_config.address_normalization.rules`
- If the normalized address matches any existing entry → `skipped_dup`

If neither match → listing is new, proceed to Step 6.

---

## Step 6: Add to Pipeline

For each new qualified listing:

**Append to `data/pipeline.md`:**
```
- [ ] {url} | {portal} | {area} | {type} | {price} | {size} | {layout}
```
Where `{type}` = rent or buy label (use short labels), `{area}` = the listing's area/district.

**Append to `data/scan-history.tsv`** (9 tab-separated columns):
```
{url}\t{first_seen}\t{portal}\t{title}\t{address}\t{normalized_address}\t{price}\t{size}\tAdded
```
- `first_seen`: today's date (YYYY-MM-DD)
- `normalized_address`: apply the normalization rules from `country_config.address_normalization.rules`

---

## Step 7: Update scan-history.tsv for Skipped Entries

For `skipped_title` and `skipped_dup` listings, also append to `data/scan-history.tsv` with the appropriate status so future scans don't re-process them:
- Title filter fail → status: `skipped_title`
- Duplicate → status: `skipped_dup`
- Expired listing detected → status: `skipped_expired`
- Added to pipeline → status: `added`

---

## Step 8: Scan Summary Output

After completing all portals and updates, output exactly this format:

```
Portal Scan — YYYY-MM-DD
========================
Portals scanned: N
Listings found: N total
Quick filter passed: N qualified
Duplicates skipped: N skipped_dup
Title filter failed: N skipped_title
Expired skipped: N skipped_expired
Added to pipeline.md: N

  + {area} | {portal} | {price} | {size} | {layout}
  + {area} | {portal} | {price} | {size} | {layout}
  ...

→ Run pipeline mode to start evaluating new listings.
```

List each newly added listing with a `+` prefix. If nothing was added, say "→ No new listings found in this scan."

---

## Notes

- **Level 2 (market reference) is evaluation-only.** It provides price comparison data during rent.md / buy.md evaluation — it never populates pipeline.md.
- **Do not verify liveness for Level 1 results** — freshly scraped search pages are assumed live. Liveness verification is only needed for Level 3 (WebSearch cached results).
- **If a portal's page fails to load** (JS error, CAPTCHA, etc.): skip that portal, note it in the summary, continue with others.
- **If `playwright-cli` is not installed**: do not attempt any Level 1 or Level 3 liveness verification. Stop immediately and remind the user: `npm install -g @playwright/cli@latest`.
