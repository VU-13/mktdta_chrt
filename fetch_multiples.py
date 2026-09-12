#!/usr/bin/env python3
"""
Weekly EV/EBITDA sector multiples pipeline.

Run every Wednesday (via GitHub Actions — see .github/workflows/weekly-update.yml —
or any other scheduler):
    python fetch_multiples.py

What it does:
  1. Pulls EV and EBITDA for every configured ticker via yfinance (free, no API key).
  2. Excludes implausible individual readings (EV/EBITDA below 3x or above 80x —
     see MIN/MAX_PLAUSIBLE_MULTIPLE in config.py) before averaging.
  3. Averages EV/EBITDA per region (EU/US) within each sector.
  4. Blends EU/US using the sector's configured weight (auto-renormalized if one
     region has no usable data this week).
  5. Folds in a manual BVB data point for the sector, if one was added to
     bvb_manual.csv for today's date.
  6. Applies the sector's illiquidity discount.
  7. Appends one row per sector to history.csv (point your WP chart plugin at this
     file for the time series).
  8. Recomputes the trailing ~3-month average per sector and writes latest.json
     (a compact snapshot for the page).
"""

import csv
import json
import random
import sys
import time
from datetime import date, datetime, timedelta
from pathlib import Path

import yfinance as yf

from config import (
    SECTORS,
    HISTORY_FILE,
    BVB_MANUAL_FILE,
    LATEST_OUTPUT_FILE,
    ROLLING_WINDOW_DAYS,
    MIN_PLAUSIBLE_MULTIPLE,
    MAX_PLAUSIBLE_MULTIPLE,
)

TODAY = date.today().isoformat()

# Yahoo Finance (via yfinance) will intermittently 404/error perfectly valid,
# still-listed tickers when hit with a burst of requests in a row -- common
# from shared CI IPs like GitHub Actions runners. A short pause between
# requests plus a couple of retries clears up most of these false failures.
REQUEST_DELAY_SECONDS = 1.0
MAX_RETRIES = 3


def get_ev_ebitda(ticker: str):
    """Return EV/EBITDA for a ticker, or None if data is unavailable/unreliable/an outlier."""
    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            info = yf.Ticker(ticker).info
            ev = info.get("enterpriseValue")
            ebitda = info.get("ebitda")
            if not ev or not ebitda or ebitda <= 0:
                print(f"  [skip] {ticker}: missing/invalid EV or EBITDA", file=sys.stderr)
                return None
            multiple = ev / ebitda
            if multiple < MIN_PLAUSIBLE_MULTIPLE or multiple > MAX_PLAUSIBLE_MULTIPLE:
                print(
                    f"  [outlier] {ticker}: EV/EBITDA={multiple:.1f}x is outside "
                    f"[{MIN_PLAUSIBLE_MULTIPLE}, {MAX_PLAUSIBLE_MULTIPLE}], excluded from the average",
                    file=sys.stderr,
                )
                return None
            return multiple
        except Exception as exc:  # yfinance can raise all sorts of things
            last_error = exc
            if attempt < MAX_RETRIES:
                wait = REQUEST_DELAY_SECONDS * attempt * 2
                print(f"  [retry] {ticker}: attempt {attempt} failed ({exc}), retrying in {wait:.1f}s", file=sys.stderr)
                time.sleep(wait)
    print(f"  [error] {ticker}: giving up after {MAX_RETRIES} attempts ({last_error})", file=sys.stderr)
    return None


def region_average(tickers):
    """Mean EV/EBITDA across a list of tickers. Returns (mean_or_None, n_used)."""
    values = []
    for t in tickers:
        v = get_ev_ebitda(t)
        if v is not None:
            values.append(v)
        time.sleep(REQUEST_DELAY_SECONDS + random.uniform(0, 0.5))  # space out requests to avoid rate-limiting
    if not values:
        return None, 0
    return sum(values) / len(values), len(values)


def load_bvb_manual_for_today():
    """Read bvb_manual.csv and return {sector: multiple} for today's date, if present."""
    path = Path(BVB_MANUAL_FILE)
    if not path.exists():
        return {}
    result = {}
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("date") == TODAY and row.get("sector") and row.get("multiple"):
                result[row["sector"]] = float(row["multiple"])
    return result


def append_history(rows):
    path = Path(HISTORY_FILE)
    is_new = not path.exists()
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "date", "sector", "label", "eu_avg", "eu_n", "us_avg", "us_n",
                "bvb_manual", "blended_raw", "discount", "final_multiple",
            ],
        )
        if is_new:
            writer.writeheader()
        for row in rows:
            writer.writerow(row)


def compute_three_month_averages():
    path = Path(HISTORY_FILE)
    if not path.exists():
        return {}
    cutoff = date.today() - timedelta(days=ROLLING_WINDOW_DAYS)
    buckets = {}
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            row_date = datetime.strptime(row["date"], "%Y-%m-%d").date()
            if row_date >= cutoff and row["final_multiple"]:
                buckets.setdefault(row["sector"], []).append(float(row["final_multiple"]))
    return {sector: sum(v) / len(v) for sector, v in buckets.items()}


def main():
    bvb_today = load_bvb_manual_for_today()
    history_rows = []

    for sector_key, cfg in SECTORS.items():
        print(f"Processing {cfg['label']}...")
        eu_avg, eu_n = region_average(cfg["companies"].get("EU", []))
        us_avg, us_n = region_average(cfg["companies"].get("US", []))
        w_eu = cfg["weights"].get("EU", 0)
        w_us = cfg["weights"].get("US", 0)

        # Blend whichever regions actually returned data; renormalize weights
        # if one side came back empty this week rather than skipping the sector.
        parts = [(v, w) for v, w in ((eu_avg, w_eu), (us_avg, w_us)) if v is not None]
        if not parts:
            print(f"  [warn] no data at all for {sector_key} this week, skipping", file=sys.stderr)
            continue
        weight_sum = sum(w for _, w in parts) or 1
        blended_raw = sum(v * w for v, w in parts) / weight_sum

        # Fold in a manual BVB data point for this sector, if provided today,
        # as an equal-weight extra observation alongside the blended EU/US figure.
        # Subject to the same plausibility bounds as the automated readings.
        bvb_value = bvb_today.get(sector_key)
        if bvb_value is not None and not (MIN_PLAUSIBLE_MULTIPLE <= bvb_value <= MAX_PLAUSIBLE_MULTIPLE):
            print(
                f"  [outlier] BVB manual entry for {sector_key}: {bvb_value:.1f}x is outside "
                f"[{MIN_PLAUSIBLE_MULTIPLE}, {MAX_PLAUSIBLE_MULTIPLE}], excluded",
                file=sys.stderr,
            )
            bvb_value = None
        if bvb_value is not None:
            blended_raw = (blended_raw + bvb_value) / 2

        discount = cfg["discount"]
        final_multiple = round(blended_raw * (1 - discount), 1)

        history_rows.append({
            "date": TODAY,
            "sector": sector_key,
            "label": cfg["label"],
            "eu_avg": round(eu_avg, 2) if eu_avg is not None else "",
            "eu_n": eu_n,
            "us_avg": round(us_avg, 2) if us_avg is not None else "",
            "us_n": us_n,
            "bvb_manual": bvb_value if bvb_value is not None else "",
            "blended_raw": round(blended_raw, 2),
            "discount": discount,
            "final_multiple": final_multiple,
        })

    if not history_rows:
        print("Nothing to write this week.", file=sys.stderr)
        sys.exit(1)

    append_history(history_rows)
    three_month = compute_three_month_averages()

    latest = {
        row["sector"]: {
            "label": row["label"],
            "final_multiple": row["final_multiple"],
            "three_month_avg": round(three_month.get(row["sector"], row["final_multiple"]), 1),
            "last_updated": TODAY,
        }
        for row in history_rows
    }
    Path(LATEST_OUTPUT_FILE).write_text(json.dumps(latest, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Done. Wrote {len(history_rows)} rows to {HISTORY_FILE} and a snapshot to {LATEST_OUTPUT_FILE}.")


if __name__ == "__main__":
    main()
