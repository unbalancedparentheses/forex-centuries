#!/usr/bin/env python3
"""
update_sources.py — Refresh programmatically-available source data.

Usage:
    python scripts/update_sources.py --fred   # requires FRED_API_KEY env var
    python scripts/update_sources.py --imf    # no auth needed
    python scripts/update_sources.py --gold   # no auth needed
    python scripts/update_sources.py --bis    # no auth needed
    python scripts/update_sources.py --riksbank  # no auth needed (rate-limited)
    python scripts/update_sources.py --worldbank # no auth needed
    python scripts/update_sources.py --jst    # no auth needed
    python scripts/update_sources.py --pwt    # no auth needed
    python scripts/update_sources.py --measuringworth  # no auth needed
    python scripts/update_sources.py --clio   # no auth needed
    python scripts/update_sources.py --freegold  # no auth needed
    python scripts/update_sources.py --lbma   # no auth needed (gold + silver from LBMA)
    python scripts/update_sources.py --irr    # no auth needed
    python scripts/update_sources.py --boe    # no auth needed
    python scripts/update_sources.py --all    # all of the above
"""

import argparse
import csv
import io
import json
import os
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / "data" / "sources"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def fetch_url(url, timeout=120):
    """Download URL content as string."""
    req = urllib.request.Request(url, headers={"User-Agent": "forex-centuries/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8")


def fetch_bytes(url, timeout=120):
    """Download URL content as bytes."""
    req = urllib.request.Request(url, headers={"User-Agent": "forex-centuries/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def write_atomic(path, content):
    """Write text content to file atomically via temp file."""
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


def write_atomic_bytes(path, data):
    """Write binary content to file atomically via temp file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
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


def download_and_extract_zip(url, dest_dir, timeout=300):
    """Download a ZIP file and extract all contents to dest_dir."""
    data = fetch_bytes(url, timeout=timeout)
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        zf.extractall(dest_dir)
    return zf.namelist()


# ---------------------------------------------------------------------------
# FRED
# ---------------------------------------------------------------------------

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
            msg = str(e)
            if api_key in msg:
                msg = msg.replace(api_key, "***")
            print(f"  ERROR {series_id}: {msg}")

    print("FRED update complete.")


# ---------------------------------------------------------------------------
# IMF
# ---------------------------------------------------------------------------

def update_imf():
    """Update IMF exchange rates from codeforIATI GitHub."""
    url = "https://codeforiati.org/imf-exchangerates/imf_exchangerates.csv"
    dest = SOURCES / "imf" / "imf_exchange_rates.csv"

    print("Updating IMF exchange rates...")
    content = fetch_url(url)
    rows = validate_csv(content, expected_columns=["Date", "Rate", "Currency"], min_rows=100)
    write_atomic(dest, content)
    print(f"  imf_exchange_rates.csv: {rows:,} rows")
    print("IMF update complete.")


# ---------------------------------------------------------------------------
# Gold (DataHub)
# ---------------------------------------------------------------------------

def update_gold():
    """Update gold price CSVs."""
    print("Updating gold prices...")

    url = "https://raw.githubusercontent.com/datasets/gold-prices/main/data/monthly.csv"
    dest = SOURCES / "gold" / "gold_monthly_usd.csv"
    content = fetch_url(url)
    rows = validate_csv(content, expected_columns=["Date", "Price"], min_rows=100)
    write_atomic(dest, content)
    print(f"  gold_monthly_usd.csv: {rows:,} rows")

    print("Gold update complete.")


# ---------------------------------------------------------------------------
# BIS (Bank for International Settlements)
# ---------------------------------------------------------------------------

def update_bis():
    """Update BIS bilateral exchange rates and effective exchange rates."""
    print("Updating BIS datasets...")

    datasets = {
        "WS_XRU_csv_flat": ("bis/xru", "bilateral exchange rates"),
        "WS_EER_csv_flat": ("bis/eer", "effective exchange rates"),
    }

    for name, (subdir, desc) in datasets.items():
        url = f"https://data.bis.org/static/bulk/{name}.zip"
        dest_dir = SOURCES / subdir
        try:
            data = fetch_bytes(url, timeout=300)
            dest_dir.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(io.BytesIO(data)) as zf:
                members = zf.namelist()
                # Extract the CSV (skip any readme or metadata)
                csv_files = [m for m in members if m.endswith(".csv")]
                for cf in csv_files:
                    content = zf.read(cf)
                    write_atomic_bytes(dest_dir / cf, content)
                    size_mb = len(content) / (1024 * 1024)
                    print(f"  {cf}: {size_mb:.1f} MB ({desc})")
        except Exception as e:
            print(f"  ERROR {name}: {e}")

    print("BIS update complete.")


# ---------------------------------------------------------------------------
# Riksbank (Sveriges Riksbank)
# ---------------------------------------------------------------------------

# 53 series from the existing dataset
RIKSBANK_SERIES = [
    "SEKATSPMI", "SEKAUDPMI", "SEKBEFPMI", "SEKBGNPMI", "SEKBRLPMI",
    "SEKCADPMI", "SEKCHFPMI", "SEKCNYPMI", "SEKCYPPMI", "SEKCZKPMI",
    "SEKDEMPMI", "SEKDKKPMI", "SEKEEKPMI", "SEKESPPMI", "SEKETT",
    "SEKEURPMI", "SEKFIMPMI", "SEKFRFPMI", "SEKGBPPMI", "SEKGRDPMI",
    "SEKHKDPMI", "SEKHUFPMI", "SEKIDRPMI", "SEKIEPPMI", "SEKILSPMI",
    "SEKINRPMI", "SEKISKPMI", "SEKITLPMI", "SEKJPYPMI", "SEKKRWPMI",
    "SEKKWDPMI", "SEKLTLPMI", "SEKLVLPMI", "SEKMADPMI", "SEKMXNPMI",
    "SEKMYRPMI", "SEKNLGPMI", "SEKNOKPMI", "SEKNZDPMI", "SEKPHPPMI",
    "SEKPLNPMI", "SEKPTEPMI", "SEKRONPMI", "SEKRUBPMI", "SEKSARPMI",
    "SEKSGDPMI", "SEKSITPMI", "SEKSKKPMI", "SEKTHBPMI", "SEKTRLPMI",
    "SEKTRYPMI", "SEKUSDPMI", "SEKZARPMI",
]


def update_riksbank():
    """Update Riksbank exchange rates via API."""
    dest = SOURCES / "riksbank" / "riksbank_exchange_rates.csv"

    print(f"Updating {len(RIKSBANK_SERIES)} Riksbank series...")
    all_rows = []
    errors = 0

    for series_id in RIKSBANK_SERIES:
        url = (
            f"https://api.riksbank.se/swea/v1/Observations/{series_id}"
            f"/1900-01-01/{datetime.now().strftime('%Y-%m-%d')}"
        )
        try:
            raw = fetch_url(url, timeout=60)
            observations = json.loads(raw)
            for obs in observations:
                date = obs.get("date", "")[:10]
                value = obs.get("value")
                if date and value is not None:
                    all_rows.append(f"{date},{series_id},{value}")
            print(f"  {series_id}: {len(observations):,} observations")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                print(f"  SKIP {series_id}: not found (discontinued)")
            else:
                print(f"  ERROR {series_id}: HTTP {e.code}")
                errors += 1
        except Exception as e:
            print(f"  ERROR {series_id}: {e}")
            errors += 1
        # Rate limit: 5 calls/min without API key
        time.sleep(3)

    if all_rows:
        all_rows.sort()
        content = "date,series_id,value\n" + "\n".join(all_rows) + "\n"
        write_atomic(dest, content)
        print(f"  riksbank_exchange_rates.csv: {len(all_rows):,} rows total")
    else:
        print("  WARNING: no data fetched, keeping existing file")

    if errors:
        print(f"  ({errors} series had errors)")
    print("Riksbank update complete.")


# ---------------------------------------------------------------------------
# World Bank
# ---------------------------------------------------------------------------

def update_worldbank():
    """Update World Bank official exchange rates (PA.NUS.FCRF)."""
    dest = SOURCES / "worldbank" / "worldbank_exchange_rates.csv"
    year = datetime.now().year

    print("Updating World Bank exchange rates...")

    # Try the API with JSON format (more reliable than CSV download)
    page = 1
    all_rows = []
    while True:
        url = (
            f"https://api.worldbank.org/v2/country/all/indicator/PA.NUS.FCRF"
            f"?format=json&date=1960:{year}&per_page=10000&page={page}"
        )
        try:
            raw = fetch_url(url, timeout=120)
            data = json.loads(raw)
            if not isinstance(data, list) or len(data) < 2:
                break
            meta, records = data[0], data[1]
            if not records:
                break
            for rec in records:
                if rec.get("value") is not None:
                    country = rec["country"]["value"]
                    iso3 = rec["countryiso3code"]
                    date = rec["date"]
                    value = rec["value"]
                    all_rows.append((iso3, country, date, str(value)))
            pages = meta.get("pages", 1)
            if page >= pages:
                break
            page += 1
        except Exception as e:
            print(f"  ERROR fetching page {page}: {e}")
            break

    if all_rows:
        all_rows.sort(key=lambda r: (r[0], r[2]))
        lines = ["iso3,country,year,exchange_rate"]
        for iso3, country, date, value in all_rows:
            # Escape country names with commas
            if "," in country:
                country = f'"{country}"'
            lines.append(f"{iso3},{country},{date},{value}")
        content = "\n".join(lines) + "\n"
        write_atomic(dest, content)
        print(f"  worldbank_exchange_rates.csv: {len(all_rows):,} rows")
    else:
        print("  WARNING: no data fetched, keeping existing file")

    print("World Bank update complete.")


# ---------------------------------------------------------------------------
# JST (Jorda-Schularick-Taylor Macrohistory)
# ---------------------------------------------------------------------------

def update_jst():
    """Update JST Macrohistory dataset."""
    url = "https://www.macrohistory.net/app/download/9834512469/JSTdatasetR6.xlsx"
    dest = SOURCES / "jst" / "jst_macrohistory.xlsx"

    print("Updating JST Macrohistory dataset...")
    try:
        data = fetch_bytes(url, timeout=120)
        if len(data) < 100_000:
            print(f"  WARNING: file too small ({len(data)} bytes), possible error page")
            return
        write_atomic_bytes(dest, data)
        size_mb = len(data) / (1024 * 1024)
        print(f"  jst_macrohistory.xlsx: {size_mb:.1f} MB")
    except Exception as e:
        print(f"  ERROR: {e}")

    print("JST update complete.")


# ---------------------------------------------------------------------------
# Penn World Table
# ---------------------------------------------------------------------------

def update_pwt():
    """Update Penn World Table."""
    url = "https://dataverse.nl/api/access/datafile/554105"
    dest = SOURCES / "pwt" / "pwt.xlsx"

    print("Updating Penn World Table...")
    try:
        data = fetch_bytes(url, timeout=300)
        if len(data) < 100_000:
            print(f"  WARNING: file too small ({len(data)} bytes), possible error page")
            return
        write_atomic_bytes(dest, data)
        size_mb = len(data) / (1024 * 1024)
        print(f"  pwt.xlsx: {size_mb:.1f} MB")
    except Exception as e:
        print(f"  ERROR: {e}")

    print("Penn World Table update complete.")


# ---------------------------------------------------------------------------
# MeasuringWorth
# ---------------------------------------------------------------------------

MW_COUNTRIES = [
    "Argentina", "Australia", "Austria", "Belgium", "Brazil", "Canada",
    "Chile", "China", "Colombia", "Denmark", "Europe", "Finland", "France",
    "Germany", "Greece", "Hong Kong", "India", "Indonesia", "Ireland",
    "Israel", "Italy", "Japan", "Korea", "Malaysia", "Mexico", "Netherlands",
    "New Zealand", "Norway", "Peru", "Philippines", "Portugal", "Singapore",
    "South Africa", "Spain", "Sri Lanka", "Sweden", "Switzerland", "Taiwan",
    "Thailand", "United Kingdom", "Venezuela",
]


def update_measuringworth():
    """Update MeasuringWorth exchange rates and gold prices."""
    print("Updating MeasuringWorth datasets...")
    year = datetime.now().year

    # Exchange rates (41 currencies vs USD)
    country_params = "&".join(
        f"countryE[]={urllib.parse.quote(c)}" for c in MW_COUNTRIES
    )
    url = (
        f"https://www.measuringworth.com/datasets/exchangeglobal/export.php"
        f"?year_source=1791&year_result={year}&{country_params}"
    )
    dest = SOURCES / "measuringworth" / "measuringworth_exchange_rates.csv"
    try:
        content = fetch_url(url)
        rows = validate_csv(content, min_rows=50)
        write_atomic(dest, content)
        print(f"  measuringworth_exchange_rates.csv: {rows:,} rows")
    except Exception as e:
        print(f"  ERROR exchange rates: {e}")

    # Gold prices — each series has a different start year, so we fetch them
    # separately and merge on year.
    # Series: (param, start_year)
    gold_series = [
        ("British", 1257),   # British official GBP
        ("london", 1718),    # London market GBP + USD
        ("us", 1786),        # US official USD
        ("newyork", 1791),   # New York market USD
        ("goldsilver", 1687),  # Gold/silver ratio
    ]
    gold_data = {}  # year -> {col: val}
    all_columns = []
    for param, start_year in gold_series:
        series_url = (
            f"https://www.measuringworth.com/datasets/gold/export.php"
            f"?year_source={start_year}&year_result={year}&{param}=on"
        )
        try:
            raw = fetch_url(series_url)
            reader = csv.reader(io.StringIO(raw))
            # Skip preamble lines until we find the header starting with "Year"
            header = None
            for row in reader:
                if row and row[0].strip().strip('"').lower() == "year":
                    header = [c.strip().strip('"') for c in row]
                    break
            if not header or len(header) < 2:
                print(f"  SKIP gold/{param}: no valid header")
                continue
            # Use short column names based on param
            col_name = f"{param}_price"
            all_columns.append(col_name)
            for row in reader:
                if not row or not row[0].strip().strip('"').isdigit():
                    continue
                yr = row[0].strip().strip('"')
                if yr not in gold_data:
                    gold_data[yr] = {}
                if len(row) > 1 and row[1].strip().strip('"'):
                    gold_data[yr][col_name] = row[1].strip().strip('"')
            print(f"  gold/{param}: fetched ({start_year}-{year})")
        except Exception as e:
            print(f"  ERROR gold/{param}: {e}")

    if gold_data:
        dest = SOURCES / "measuringworth" / "measuringworth_gold_prices.csv"
        lines = ["year," + ",".join(all_columns)]
        for yr in sorted(gold_data.keys(), key=int):
            vals = [gold_data[yr].get(c, "") for c in all_columns]
            lines.append(f"{yr},{','.join(vals)}")
        content = "\n".join(lines) + "\n"
        write_atomic(dest, content)
        print(f"  measuringworth_gold_prices.csv: {len(gold_data):,} rows")

    print("MeasuringWorth update complete.")


# ---------------------------------------------------------------------------
# Clio Infra
# ---------------------------------------------------------------------------

CLIO_DATASETS = {
    "ExchangeRatestoUSDollar_Compact.xlsx": "clio_infra_exchange_rates_compact.xlsx",
    "ExchangeRatestoUKPound_Compact.xlsx": "clio_infra_exchange_rates_gbp_compact.xlsx",
    "Inflation_Compact.xlsx": "clio_infra_inflation_compact.xlsx",
    "GoldStandard_Compact.xlsx": "clio_infra_gold_standard_compact.xlsx",
    "TotalGrossCentralGovernmentDebtasaPercentageofGDP_Compact.xlsx": "clio_infra_govt_debt_compact.xlsx",
    "Long-TermGovernmentBondYield_Compact.xlsx": "clio_infra_bond_yield_compact.xlsx",
    "GDPperCapita_Compact.xlsx": "clio_infra_gdp_per_capita_compact.xlsx",
}


def update_clio():
    """Update Clio Infra datasets."""
    print("Updating Clio Infra datasets...")

    dest_dir = SOURCES / "clio_infra"
    for remote_name, local_name in sorted(CLIO_DATASETS.items()):
        url = f"https://clio-infra.eu/data/{remote_name}"
        try:
            data = fetch_bytes(url, timeout=60)
            if len(data) < 1000:
                print(f"  SKIP {remote_name}: too small ({len(data)} bytes)")
                continue
            write_atomic_bytes(dest_dir / local_name, data)
            size_kb = len(data) / 1024
            print(f"  {local_name}: {size_kb:.0f} KB")
        except Exception as e:
            print(f"  ERROR {remote_name}: {e}")

    print("Clio Infra update complete.")


# ---------------------------------------------------------------------------
# FreeGoldAPI
# ---------------------------------------------------------------------------

def update_freegold():
    """Update FreeGoldAPI gold prices (768 years) and gold/silver ratio."""
    print("Updating FreeGoldAPI datasets...")

    dest_dir = SOURCES / "freegold"
    files = {
        "latest.csv": ("freegold_prices.csv", ["date", "price"]),
        "gold_silver_ratio_enriched.csv": (
            "freegold_gold_silver_ratio.csv",
            ["date", "price"],
        ),
        "gold_silver_normalized.csv": (
            "freegold_silver_prices.csv",
            ["date", "price"],
        ),
    }

    for remote_name, (local_name, expected_cols) in files.items():
        url = f"https://freegoldapi.com/data/{remote_name}"
        try:
            content = fetch_url(url)
            rows = validate_csv(content, expected_columns=expected_cols, min_rows=100)
            write_atomic(dest_dir / local_name, content)
            print(f"  {local_name}: {rows:,} rows")
        except Exception as e:
            print(f"  ERROR {remote_name}: {e}")

    print("FreeGoldAPI update complete.")


# ---------------------------------------------------------------------------
# LBMA (London Bullion Market Association)
# ---------------------------------------------------------------------------

LBMA_FEEDS = {
    "gold_pm": (
        "https://prices.lbma.org.uk/json/gold_pm.json",
        "lbma_gold_daily.csv",
        ["USD", "GBP", "EUR"],
    ),
    "silver": (
        "https://prices.lbma.org.uk/json/silver.json",
        "lbma_silver_daily.csv",
        ["USD", "GBP", "EUR"],
    ),
}


def update_lbma():
    """Update LBMA gold and silver daily prices (from 1968)."""
    print("Updating LBMA precious metals prices...")

    dest_dir = SOURCES / "lbma"
    for feed_name, (url, filename, currencies) in LBMA_FEEDS.items():
        try:
            raw = fetch_url(url, timeout=180)
            data = json.loads(raw)
            lines = ["date," + ",".join(f"{feed_name}_{c.lower()}" for c in currencies)]
            for entry in data:
                date = entry.get("d", "")
                values = entry.get("v", [])
                # Pad to expected length, replace None with empty
                row_vals = []
                for i, cur in enumerate(currencies):
                    v = values[i] if i < len(values) and values[i] is not None else ""
                    row_vals.append(str(v))
                lines.append(f"{date},{','.join(row_vals)}")
            content = "\n".join(lines) + "\n"
            rows = len(data)
            write_atomic(dest_dir / filename, content)
            print(f"  {filename}: {rows:,} daily prices")
        except Exception as e:
            print(f"  ERROR {feed_name}: {e}")

    print("LBMA update complete.")


# ---------------------------------------------------------------------------
# IRR (Ilzetzki-Reinhart-Rogoff)
# ---------------------------------------------------------------------------

IRR_FILES = {
    "irr_anchor_monthly.xlsx": (
        "https://www.ilzetzki.com/_files/ugd/"
        "b3763a_7b72377cfe184f72ba0ad77dabbabae0.xlsx"
    ),
    "irr_regime_monthly.xlsx": (
        "https://www.ilzetzki.com/_files/ugd/"
        "b3763a_242513d0fba24aa1a64be41c8f73d887.xlsx"
    ),
    "irr_unified_market.xlsx": (
        "https://www.ilzetzki.com/_files/ugd/"
        "b3763a_48a9a40476c6465da949a3456b1b3e4c.xlsx"
    ),
}


def update_irr():
    """Update IRR regime classification data."""
    print("Updating IRR datasets...")

    dest_dir = SOURCES / "irr"
    for filename, url in sorted(IRR_FILES.items()):
        try:
            data = fetch_bytes(url, timeout=120)
            if len(data) < 10_000:
                print(f"  SKIP {filename}: too small ({len(data)} bytes)")
                continue
            write_atomic_bytes(dest_dir / filename, data)
            size_mb = len(data) / (1024 * 1024)
            print(f"  {filename}: {size_mb:.1f} MB")
        except Exception as e:
            print(f"  ERROR {filename}: {e}")

    print("IRR update complete.")


# ---------------------------------------------------------------------------
# Bank of England Millennium
# ---------------------------------------------------------------------------

def update_boe():
    """Update Bank of England Millennium dataset."""
    url = (
        "https://www.bankofengland.co.uk/-/media/boe/files/statistics/"
        "research-datasets/a-millennium-of-macroeconomic-data-for-the-uk.xlsx"
    )
    dest = SOURCES / "boe" / "boe_millennium.xlsx"

    print("Updating Bank of England Millennium dataset...")
    try:
        data = fetch_bytes(url, timeout=180)
        if len(data) < 1_000_000:
            print(f"  WARNING: file too small ({len(data)} bytes), possible error")
            return
        write_atomic_bytes(dest, data)
        size_mb = len(data) / (1024 * 1024)
        print(f"  boe_millennium.xlsx: {size_mb:.1f} MB")
    except Exception as e:
        print(f"  ERROR: {e}")

    print("Bank of England update complete.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

ALL_SOURCES = [
    ("fred", update_fred, "Update FRED daily series (requires FRED_API_KEY)"),
    ("imf", update_imf, "Update IMF exchange rates"),
    ("gold", update_gold, "Update DataHub gold prices"),
    ("bis", update_bis, "Update BIS bilateral + effective exchange rates"),
    ("riksbank", update_riksbank, "Update Riksbank SEK exchange rates"),
    ("worldbank", update_worldbank, "Update World Bank official exchange rates"),
    ("jst", update_jst, "Update JST Macrohistory dataset"),
    ("pwt", update_pwt, "Update Penn World Table"),
    ("measuringworth", update_measuringworth, "Update MeasuringWorth exchange rates + gold"),
    ("clio", update_clio, "Update Clio Infra datasets"),
    ("freegold", update_freegold, "Update FreeGoldAPI (768 years gold + silver)"),
    ("lbma", update_lbma, "Update LBMA gold + silver daily prices (from 1968)"),
    ("irr", update_irr, "Update IRR regime classifications"),
    ("boe", update_boe, "Update Bank of England Millennium dataset"),
]


def main():
    parser = argparse.ArgumentParser(description="Update forex-centuries source data")
    for name, _, help_text in ALL_SOURCES:
        parser.add_argument(f"--{name}", action="store_true", help=help_text)
    parser.add_argument("--all", action="store_true", help="Update all sources")
    args = parser.parse_args()

    flags = {name: getattr(args, name) for name, _, _ in ALL_SOURCES}
    if not any(flags.values()) and not args.all:
        parser.print_help()
        sys.exit(1)

    for name, func, _ in ALL_SOURCES:
        if flags[name] or args.all:
            func()

    print("\nDone.")


if __name__ == "__main__":
    main()
