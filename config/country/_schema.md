# Country Configuration Schema

Each country is defined by a single YAML file at `config/country/{code}.yml`.

To add a new country, create a new file following this schema and also create:
- `config/profile.{code}.example.yml` — user profile template
- `portals.{code}.example.yml` — portal configuration

## Required Top-Level Sections

| Section | Purpose |
|---------|---------|
| `meta` | Country code, name (local + English), language |
| `market` | Currency, area units, conversion factors |
| `regions` | How regions are structured (city>district, county>area, etc.) |
| `property_types` | Available property types with local + English names |
| `mortgage` | Loan scenarios, affordability rules, buyer types |
| `government_schemes` | Housing assistance programs |
| `taxes` | Capital gains, stamp duty, property tax, transaction costs |
| `building_risks` | Country-specific property risk flags with severity and viewing actions |
| `transport` | Public transport systems for commute calculation |
| `address_normalization` | Rules for deduplication across portals |
| `market_reference` | Price comparison data sources (registers, APIs, indices) |
| `portals` | Listing portal details (name, URL, type, access method) |
| `rental_market` | Deposit norms, tenant protections, regulations |
| `scoring` | Dimension labels (local + English), weights, interpretation thresholds |
| `report_labels` | Section headers and table labels (local + English) |
| `listing_fields` | Data extraction field labels (local + English) |
| `onboarding` | User-facing prompts for the setup flow |
| `listing_detection` | Text signals to distinguish rent vs buy listings |
| `visit_checklist` | Viewing inspection items with local + English labels |

## Bilingual Labels

Every user-facing string should have both `local` and `en` variants:
```yaml
name_local: "價格合理性"
name_en: "Price Reasonableness"
```

The mode files use `name_local` for reports in the user's language and `name_en` for internal logic.

## Existing Countries

- `tw.yml` — Taiwan (TWD, 坪, 591/Sinyi/etc.)
- `ie.yml` — Ireland (EUR, m², Daft.ie/MyHome.ie/etc.)
- `th.yml` — Thailand (THB, m²/wah, DDproperty/Hipflat/etc.)
