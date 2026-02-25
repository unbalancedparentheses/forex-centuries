#!/usr/bin/env python3
"""
update_sources.py — Refresh programmatically-available source data.

Usage:
    python scripts/update_sources.py --fred   # requires FRED_API_KEY env var
    python scripts/update_sources.py --imf    # no auth needed
    python scripts/update_sources.py --gold   # no auth needed
    python scripts/update_sources.py --all    # all of the above
"""

import argparse
import csv
import io
import json
import os
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / "data" / "sources"

# FRED series ID -> (filename, column_header)
FRED_SERIES = {
    "DEXUSAL": "fred_aud_usd.csv",
    "DEXBZUS": "fred_brl_usd.csv",
    "DEXCAUS": "fred_cad_usd.csv",
    "DEXSZUS": "fred_chf_usd.csv",
    "DEXCHUS": "fred_cny_usd.csv",
    "DEXDNUS": "fred_dkk_usd.csv",
    "DEXUSEU": "fred_eur_usd.csv",
    "DEXUSUK": "fred_gbp_usd.csv",
    "DEXHKUS": "fred_hkd_usd.csv",
    "DEXINUS": "fred_inr_usd.csv",
    "DEXJPUS": "fred_jpy_usd.csv",
    "DEXKOUS": "fred_krw_usd.csv",
    "DEXSLUS": "fred_lkr_usd.csv",
    "DEXMXUS": "fred_mxn_usd.csv",
    "DEXMAUS": "fred_myr_usd.csv",
    "DEXNOUS": "fred_nok_usd.csv",
    "DEXUSNZ": "fred_nzd_usd.csv",
    "DEXSDUS": "fred_sek_usd.csv",
    "DEXSIUS": "fred_sgd_usd.csv",
    "DEXTHUS": "fred_thb_usd.csv",
    "DEXTAUS": "fred_twd_usd.csv",
    "DEXVZUS": "fred_vef_usd.csv",
    "DEXSFUS": "fred_zar_usd.csv",
    "DTWEXBGS": "fred_usd_broad_index.csv",
    "DTWEXM": "fred_usd_major_index.csv",
}


def fetch_url(url):
    """Download URL content as string."""
    req = urllib.request.Request(url, headers={"User-Agent": "forex-centuries/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read().decode("utf-8")


def write_atomic(path, content):
    """Write content to file atomically via temp file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(content)
        os.replace(tmp, path)
    except Exception:
        os.unlink(tmp)
        raise


def validate_csv(content, expected_columns=None, min_rows=1):
    """Basic CSV validation: non-empty, has expected columns."""
    reader = csv.reader(io.StringIO(content))
    header = next(reader, None)
    if header is None:
        raise ValueError("Empty CSV (no header)")
    if expected_columns:
        for col in expected_columns:
            if col not in header:
                raise ValueError(f"Missing expected column: {col}")
    rows = sum(1 for _ in reader)
    if rows < min_rows:
        raise ValueError(f"Only {rows} data rows (expected >= {min_rows})")
    return rows


def update_fred():
    """Update all 25 FRED daily CSV files."""
    api_key = os.environ.get("FRED_API_KEY")
    if not api_key:
        print("ERROR: FRED_API_KEY environment variable not set.")
        print("Get a free key at https://fred.stlouisfed.org/docs/api/api_key.html")
        sys.exit(1)

    dest_dir = SOURCES / "fred" / "daily"
    print(f"Updating {len(FRED_SERIES)} FRED series...")

    for series_id, filename in sorted(FRED_SERIES.items()):
        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id={series_id}&file_type=json&api_key={api_key}"
        )
        try:
            raw = fetch_url(url)
            data = json.loads(raw)
            observations = data.get("observations", [])
            if not observations:
                print(f"  SKIP {series_id}: no observations returned")
                continue

            # Build CSV content matching existing format
            lines = [f"observation_date,{series_id}"]
            for obs in observations:
                lines.append(f"{obs['date']},{obs['value']}")

            content = "\n".join(lines) + "\n"
            rows = len(observations)
            write_atomic(dest_dir / filename, content)
            print(f"  {filename}: {rows:,} observations")

        except urllib.error.URLError as e:
            print(f"  ERROR {series_id}: {e.reason}")
        except Exception as e:
            # Sanitize: str(e) may contain the API key in the URL
            msg = str(e)
            if api_key in msg:
                msg = msg.replace(api_key, "***")
            print(f"  ERROR {series_id}: {msg}")

    print("FRED update complete.")


def update_imf():
    """Update IMF exchange rates from codeforIATI GitHub."""
    url = "https://raw.githubusercontent.com/codeforIATI/imf-exchangerates/main/imf_exchangerates.csv"
    dest = SOURCES / "imf" / "imf_exchange_rates.csv"

    print("Updating IMF exchange rates...")
    content = fetch_url(url)
    rows = validate_csv(content, expected_columns=["Date", "Rate", "Currency"], min_rows=100)
    write_atomic(dest, content)
    print(f"  imf_exchange_rates.csv: {rows:,} rows")
    print("IMF update complete.")


def update_gold():
    """Update gold price CSVs."""
    print("Updating gold prices...")

    # DataHub monthly gold
    url = "https://raw.githubusercontent.com/datasets/gold-prices/main/data/monthly.csv"
    dest = SOURCES / "gold" / "gold_monthly_usd.csv"
    content = fetch_url(url)
    rows = validate_csv(content, expected_columns=["Date", "Price"], min_rows=100)
    write_atomic(dest, content)
    print(f"  gold_monthly_usd.csv: {rows:,} rows")

    print("Gold update complete.")


def main():
    parser = argparse.ArgumentParser(description="Update forex-centuries source data")
    parser.add_argument("--fred", action="store_true", help="Update FRED daily series (requires FRED_API_KEY)")
    parser.add_argument("--imf", action="store_true", help="Update IMF exchange rates")
    parser.add_argument("--gold", action="store_true", help="Update gold prices")
    parser.add_argument("--all", action="store_true", help="Update all sources")
    args = parser.parse_args()

    if not any([args.fred, args.imf, args.gold, args.all]):
        parser.print_help()
        sys.exit(1)

    if args.fred or args.all:
        update_fred()
    if args.imf or args.all:
        update_imf()
    if args.gold or args.all:
        update_gold()

    print("\nDone.")


if __name__ == "__main__":
    main()
