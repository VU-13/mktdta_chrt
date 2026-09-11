# EV/EBITDA sector multiples pipeline

Weekly (Wednesday) pull of small/mid-cap public-market EV/EBITDA multiples by
sector, blended EU/US per sector's configured weight, with a per-sector
illiquidity discount applied and a manual slot for BVB data.

## Setup (one time)

1. Create a new GitHub repository and push these files to it (`main` branch).
   A **public** repo is simplest, since it lets WordPress fetch `history.csv`
   directly via its raw URL with no authentication. If the data should stay
   private, keep the repo private and instead have WordPress pull the file
   through a small server-side proxy that holds a GitHub token — ask if you
   want that variant.
2. In the repo settings, confirm **Actions** are enabled (they are by default).
3. That's it — no API keys needed. The workflow in
   `.github/workflows/weekly-update.yml` runs automatically every Wednesday
   at 06:00 UTC, and you can also trigger it manually from the repo's
   **Actions** tab (`Run workflow`) any time you want a fresh pull.

## Weekly manual step: BVB

Before or after the automated run, edit `bvb_manual.csv` on GitHub (web UI,
no git needed) and add one row per sector you have a BVB figure for, e.g.:

```
date,sector,multiple
2026-09-16,telecom,7.8
```

Use the current Wednesday's date and one of the sector keys from
`config.py` (`saas`, `it_services`, `manufacturing`, `healthcare_services`,
`logistics`, `ecommerce`, `telecom`). The script folds this in as an
additional equal-weight observation alongside that sector's blended EU/US
figure, before the discount is applied.

If you add the row **before** that Wednesday's Action runs, it gets picked
up automatically. If you add it **after**, just re-run the workflow manually
(Actions tab → Run workflow) once you've saved the row.

## Adjusting sectors, companies, weights, or discounts

Everything is in `config.py` — no need to touch `fetch_multiples.py`. Each
sector has its own `discount` (starting at 25%), its own `weights` (EU/US
split), and its own company lists per region.

The comp basket is a first draft built from general market knowledge, not
verified against live data — the first run's logs will print `[skip]` or
`[error]` for any ticker yfinance can't resolve or that has no EV/EBITDA
populated (delisted, acquired, renamed, thin data). Prune or replace those
as they show up.

## Connecting to WordPress

Point a chart plugin (e.g. **Visualizer — Charts & Maps**) at the raw CSV
URL for the time series:

```
https://raw.githubusercontent.com/<your-username>/<your-repo>/main/history.csv
```

For the "3-month average" callout on the page, either:
- read the `three_month_avg` field per sector from `latest.json` at the same
  raw-URL pattern and display it via a small custom shortcode, or
- add a second chart/table sourced from the same `history.csv`, filtered or
  aggregated by the plugin itself if it supports that.

## Files

- `config.py` — sectors, companies, region weights, discounts (edit this)
- `fetch_multiples.py` — the pipeline (rarely needs edits)
- `bvb_manual.csv` — your weekly manual BVB entries
- `history.csv` — full time series (generated/appended weekly — point WP here)
- `latest.json` — current snapshot per sector incl. 3-month average (generated)
- `.github/workflows/weekly-update.yml` — the Wednesday schedule
