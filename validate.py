"""
validate.py — Data quality checks for forex-centuries derived data.
Exit codes: 0 = pass, 1 = warnings, 2 = errors.

Usage: python validate.py
"""

import sys
import numpy as np
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).parent
DERIVED = ROOT / "data" / "derived"

EXPECTED_DAILY_CURRENCIES = sorted([
    "AUD", "BRL", "CAD", "CHF", "CNY", "DKK", "EUR", "GBP", "HKD",
    "INR", "JPY", "KRW", "LKR", "MXN", "MYR", "NOK", "NZD", "SEK",
    "SGD", "THB", "TWD", "VEF", "ZAR",
])

EXPECTED_MW_COUNTRIES = sorted([
    "Argentina", "Australia", "Austria", "Belgium", "Brazil", "Canada",
    "Chile", "China", "Colombia", "Denmark", "Finland", "France",
    "Germany", "Greece", "Hong Kong", "India", "Indonesia", "Ireland",
    "Israel", "Italy", "Japan", "Korea", "Malaysia", "Mexico",
    "Netherlands", "New Zealand", "Norway", "Peru", "Philippines",
    "Portugal", "Singapore", "South Africa", "Spain", "Sri Lanka",
    "Sweden", "Switzerland", "Taiwan", "Thailand", "United Kingdom",
    "Venezuela",
])

errors = []
warnings = []


def error(msg):
    errors.append(msg)
    print(f"  ERROR: {msg}")


def warn(msg):
    warnings.append(msg)
    print(f"  WARN:  {msg}")


def ok(msg):
    print(f"  OK:    {msg}")


def check_file_exists(path):
    if not path.exists():
        error(f"Missing file: {path.relative_to(ROOT)}")
        return False
    return True


def check_schema():
    """Check that derived files have correct columns and types."""
    print("[Schema validation]")

    checks = {
        "normalized/fred_daily_normalized.csv": [
            "date", "currency", "rate_per_usd"],
        "normalized/yearly_unified_panel.csv": [
            "year", "country", "rate_per_usd", "source"],
        "analysis/daily_log_returns.csv": [
            "date", "currency", "log_return"],
        "analysis/daily_volatility_stats.csv": [
            "currency", "n_days", "start_date", "end_date",
            "daily_volatility", "annualized_volatility",
            "excess_kurtosis", "skewness",
            "max_daily_log_return", "min_daily_log_return",
            "tail_events_3sigma", "expected_normal", "tail_ratio"],
        "analysis/yearly_volatility_stats.csv": [
            "country", "n_years", "start_year", "end_year",
            "mean_log_return", "annual_volatility",
            "excess_kurtosis",
            "max_annual_log_return", "min_annual_log_return"],
    }

    for relpath, expected_cols in checks.items():
        path = DERIVED / relpath
        if not check_file_exists(path):
            continue
        actual = list(pd.read_csv(path, nrows=0).columns)
        if actual != expected_cols:
            error(f"{relpath}: expected columns {expected_cols}, got {actual}")
        else:
            ok(f"{relpath}: columns match")

    # Wide files just need to exist and have the right index
    for relpath in ["normalized/fred_daily_normalized_wide.csv",
                    "normalized/yearly_unified_wide.csv",
                    "analysis/yearly_log_returns.csv",
                    "analysis/daily_correlation_matrix.csv",
                    "analysis/yearly_correlation_matrix.csv"]:
        path = DERIVED / relpath
        if check_file_exists(path):
            ok(f"{relpath}: exists")


def check_duplicates():
    """Check for duplicate keys in derived files."""
    print("\n[Duplicate detection]")

    path = DERIVED / "normalized/fred_daily_normalized.csv"
    if path.exists():
        df = pd.read_csv(path)
        dupes = df.duplicated(subset=["date", "currency"]).sum()
        if dupes > 0:
            error(f"fred_daily_normalized.csv: {dupes} duplicate (date, currency) pairs")
        else:
            ok(f"fred_daily_normalized.csv: no duplicates ({len(df):,} rows)")

    path = DERIVED / "normalized/yearly_unified_panel.csv"
    if path.exists():
        df = pd.read_csv(path)
        dupes = df.duplicated(subset=["year", "country"]).sum()
        if dupes > 0:
            error(f"yearly_unified_panel.csv: {dupes} duplicate (year, country) pairs")
        else:
            ok(f"yearly_unified_panel.csv: no duplicates ({len(df):,} rows)")


def check_missing_values():
    """Report missing values per currency/country."""
    print("\n[Missing value report]")

    path = DERIVED / "normalized/fred_daily_normalized_wide.csv"
    if path.exists():
        df = pd.read_csv(path, index_col="date")
        missing = df.isnull().sum()
        total = len(df)
        flagged = 0
        for currency in missing.index:
            pct = missing[currency] / total * 100
            if pct > 50:
                warn(f"Daily {currency}: {pct:.1f}% missing "
                     f"({missing[currency]:,}/{total:,})")
                flagged += 1
        if flagged == 0:
            ok(f"Daily wide: no currency >50% missing "
               f"({missing.sum():,} total NaN across {len(missing)} currencies)")

    path = DERIVED / "normalized/yearly_unified_panel.csv"
    if path.exists():
        df = pd.read_csv(path)
        null_rates = df["rate_per_usd"].isnull().sum()
        if null_rates > 0:
            warn(f"Yearly panel: {null_rates} null rate_per_usd values")
        else:
            ok(f"Yearly panel: no null rates")


def check_outliers():
    """Flag extreme values that may indicate data errors."""
    print("\n[Outlier sanity check]")

    path = DERIVED / "analysis/daily_log_returns.csv"
    if path.exists():
        df = pd.read_csv(path)
        extreme = df[df["log_return"].abs() > 0.5]
        if len(extreme) > 0:
            warn(f"Daily log returns: {len(extreme)} observations with |return| > 0.5")
            for _, row in extreme.iterrows():
                warn(f"  {row['date']} {row['currency']}: {row['log_return']:.4f}")
        else:
            ok("Daily log returns: no |return| > 0.5")

    path = DERIVED / "analysis/yearly_log_returns.csv"
    if path.exists():
        df = pd.read_csv(path, index_col="year")
        outlier_count = 0
        for country in df.columns:
            vals = df[country].dropna()
            extreme = vals[vals.abs() > 3.0]
            for year, val in extreme.items():
                warn(f"Yearly {country} {year}: log return = {val:.4f}")
                outlier_count += 1
        if outlier_count == 0:
            ok("Yearly log returns: no |return| > 3.0")


def check_cross_source_consistency():
    """Compare MeasuringWorth and Clio Infra where they overlap."""
    print("\n[Cross-source consistency]")

    mw_path = ROOT / "data/sources/measuringworth/measuringworth_exchange_rates.csv"
    ci_path = ROOT / "data/sources/clio_infra/clio_infra_exchange_rates.csv"
    if not mw_path.exists() or not ci_path.exists():
        warn("Cannot check: source files missing")
        return

    mw = pd.read_csv(mw_path).melt(
        id_vars=["year"], var_name="country", value_name="mw_rate")
    mw = mw.dropna(subset=["mw_rate"])

    ci = pd.read_csv(ci_path).melt(
        id_vars=["year"], var_name="country", value_name="ci_rate")
    ci = ci.dropna(subset=["ci_rate"])

    merged = pd.merge(mw, ci, on=["year", "country"])
    if len(merged) == 0:
        ok("No overlapping MW/CI data points")
        return

    merged["pct_diff"] = ((merged["mw_rate"] - merged["ci_rate"])
                           / merged["ci_rate"]).abs()
    divergent = merged[merged["pct_diff"] > 0.10]

    if len(divergent) > 0:
        warn(f"MW vs CI: {len(divergent)} pairs diverge >10% "
             f"(out of {len(merged)} overlap)")
        for _, row in divergent.nlargest(5, "pct_diff").iterrows():
            warn(f"  {row['country']} {int(row['year'])}: "
                 f"MW={row['mw_rate']:.4f}, CI={row['ci_rate']:.4f} "
                 f"({row['pct_diff']:.1%})")
    else:
        ok(f"MW vs CI: all {len(merged)} overlapping values within 10%")


def check_completeness():
    """Check that expected currencies/countries appear."""
    print("\n[Completeness check]")

    path = DERIVED / "normalized/fred_daily_normalized.csv"
    if path.exists():
        actual = sorted(pd.read_csv(path)["currency"].unique())
        missing = set(EXPECTED_DAILY_CURRENCIES) - set(actual)
        if missing:
            error(f"Daily data missing currencies: {missing}")
        else:
            ok(f"Daily data: all {len(EXPECTED_DAILY_CURRENCIES)} currencies present")

    path = DERIVED / "analysis/yearly_volatility_stats.csv"
    if path.exists():
        actual = sorted(pd.read_csv(path)["country"].unique())
        missing = set(EXPECTED_MW_COUNTRIES) - set(actual)
        if missing:
            warn(f"Yearly vol stats missing countries: {missing}")
        else:
            ok(f"Yearly vol stats: all {len(EXPECTED_MW_COUNTRIES)} MW countries present")


def main():
    print("forex-centuries data validation\n")

    check_schema()
    check_duplicates()
    check_missing_values()
    check_outliers()
    check_cross_source_consistency()
    check_completeness()

    print(f"\n{'=' * 50}")
    if errors:
        print(f"FAILED: {len(errors)} error(s), {len(warnings)} warning(s)")
        sys.exit(2)
    elif warnings:
        print(f"PASSED with {len(warnings)} warning(s)")
        sys.exit(1)
    else:
        print("ALL CHECKS PASSED")
        sys.exit(0)


if __name__ == "__main__":
    main()
