"""
build.py — Reproducible ETL pipeline for forex-centuries.
Regenerates all data/derived/ files from data/sources/.

Usage: python build.py
"""

import numpy as np
import pandas as pd
from pathlib import Path
from scipy.stats import kurtosis, skew, norm

ROOT = Path(__file__).parent
SOURCES = ROOT / "data" / "sources"
DERIVED = ROOT / "data" / "derived"
NORM = DERIVED / "normalized"
ANALYSIS = DERIVED / "analysis"

# Currencies where FRED quotes USD-per-foreign (need 1/x for foreign-per-USD)
INVERT = {"GBP", "EUR", "AUD", "NZD"}

# Skip USD index files
SKIP_FILES = {"fred_usd_broad_index.csv", "fred_usd_major_index.csv"}


def build_fred_daily():
    """Normalize all FRED daily CSVs to foreign-per-USD convention."""
    print("  Loading FRED daily files...")
    frames = []
    for f in sorted((SOURCES / "fred" / "daily").glob("fred_*.csv")):
        if f.name in SKIP_FILES:
            continue
        currency = f.stem.split("_")[1].upper()
        df = pd.read_csv(f, na_values=["."])
        df.columns = ["date", "rate"]
        df["rate"] = pd.to_numeric(df["rate"], errors="coerce")
        df = df.dropna(subset=["rate"])
        if currency in INVERT:
            df["rate"] = 1.0 / df["rate"]
        df["currency"] = currency
        frames.append(df[["date", "currency", "rate"]])

    long = pd.concat(frames, ignore_index=True)
    long = long.sort_values(["date", "currency"]).reset_index(drop=True)
    long.columns = ["date", "currency", "rate_per_usd"]

    long.to_csv(NORM / "fred_daily_normalized.csv", index=False)
    print(f"    fred_daily_normalized.csv: {len(long):,} rows, "
          f"{long['currency'].nunique()} currencies")

    wide = long.pivot(index="date", columns="currency", values="rate_per_usd")
    wide.to_csv(NORM / "fred_daily_normalized_wide.csv")
    print(f"    fred_daily_normalized_wide.csv: {wide.shape[0]:,} dates x "
          f"{wide.shape[1]} currencies")

    return long


def build_yearly_panel():
    """Build unified yearly panel from MeasuringWorth + Clio Infra + GMD."""
    print("  Loading MeasuringWorth...")
    mw = pd.read_csv(SOURCES / "measuringworth" / "measuringworth_exchange_rates.csv")
    mw = mw.melt(id_vars=["year"], var_name="country", value_name="rate_per_usd")
    mw = mw.dropna(subset=["rate_per_usd"])
    mw["source"] = "MW"

    print("  Loading Clio Infra...")
    ci = pd.read_csv(SOURCES / "clio_infra" / "clio_infra_exchange_rates.csv")
    ci = ci.melt(id_vars=["year"], var_name="country", value_name="rate_per_usd")
    ci = ci.dropna(subset=["rate_per_usd"])
    ci["source"] = "CI"

    print("  Loading GMD...")
    gmd = pd.read_csv(SOURCES / "gmd" / "gmd_exchange_rates.csv", index_col=0)
    gmd = gmd.rename(columns={"countryname": "country", "USDfx": "rate_per_usd"})
    gmd = gmd.dropna(subset=["year", "rate_per_usd"])
    gmd["year"] = gmd["year"].astype(int)
    gmd = gmd[gmd["year"] <= 2025]
    gmd = gmd[["year", "country", "rate_per_usd"]]
    gmd["source"] = "GMD"

    # Merge with priority: MW > CI > GMD
    all_data = pd.concat([mw, ci, gmd], ignore_index=True)
    priority = {"MW": 0, "CI": 1, "GMD": 2}
    all_data["priority"] = all_data["source"].map(priority)
    all_data = (all_data
                .sort_values("priority")
                .drop_duplicates(subset=["year", "country"], keep="first")
                .drop(columns=["priority"])
                .sort_values(["year", "country"])
                .reset_index(drop=True))

    all_data[["year", "country", "rate_per_usd", "source"]].to_csv(
        NORM / "yearly_unified_panel.csv", index=False)
    print(f"    yearly_unified_panel.csv: {len(all_data):,} rows, "
          f"{all_data['country'].nunique()} countries")

    src_counts = all_data["source"].value_counts()
    print(f"    Sources: {' | '.join(f'{s}={n:,}' for s, n in src_counts.items())}")

    wide = all_data.pivot(index="year", columns="country", values="rate_per_usd")
    wide.to_csv(NORM / "yearly_unified_wide.csv")
    print(f"    yearly_unified_wide.csv: {wide.shape[0]:,} years x "
          f"{wide.shape[1]} countries")

    return all_data


def build_log_returns(daily_long):
    """Compute log returns from normalized rates."""
    print("  Computing daily log returns...")
    daily = daily_long.sort_values(["currency", "date"]).copy()
    daily["log_return"] = daily.groupby("currency")["rate_per_usd"].transform(
        lambda x: np.log(x / x.shift(1))
    )
    daily_ret = (daily
                 .dropna(subset=["log_return"])[["date", "currency", "log_return"]]
                 .sort_values(["date", "currency"])
                 .reset_index(drop=True))
    daily_ret.to_csv(ANALYSIS / "daily_log_returns.csv", index=False)
    print(f"    daily_log_returns.csv: {len(daily_ret):,} rows")

    print("  Computing yearly log returns...")
    mw = pd.read_csv(SOURCES / "measuringworth" / "measuringworth_exchange_rates.csv")
    mw = mw.set_index("year")
    if "Europe, Eurozone" in mw.columns:
        mw = mw.drop(columns=["Europe, Eurozone"])
    yearly_ret = np.log(mw / mw.shift(1))
    yearly_ret.to_csv(ANALYSIS / "yearly_log_returns.csv")
    n_values = yearly_ret.count().sum()
    print(f"    yearly_log_returns.csv: {len(yearly_ret)} years, "
          f"{len(yearly_ret.columns)} countries, {n_values:,} values")

    return daily_ret, yearly_ret


def build_volatility_stats(daily_ret, yearly_ret):
    """Compute volatility statistics per currency/country."""
    print("  Computing daily volatility stats...")
    daily_stats = []
    for currency, group in daily_ret.groupby("currency"):
        r = group["log_return"].values
        n = len(r)
        daily_vol = r.std(ddof=1)
        ann_vol = daily_vol * np.sqrt(252)
        threshold = 3 * daily_vol
        tail_events = int(np.sum(np.abs(r) > threshold))
        expected = n * 2 * norm.sf(3)

        daily_stats.append({
            "currency": currency,
            "n_days": n,
            "start_date": group["date"].min(),
            "end_date": group["date"].max(),
            "daily_volatility": daily_vol,
            "annualized_volatility": ann_vol,
            "excess_kurtosis": kurtosis(r, fisher=True),
            "skewness": skew(r),
            "max_daily_log_return": r.max(),
            "min_daily_log_return": r.min(),
            "tail_events_3sigma": tail_events,
            "expected_normal": round(expected, 1),
            "tail_ratio": round(tail_events / expected, 2) if expected > 0 else 0,
        })

    daily_df = (pd.DataFrame(daily_stats)
                .sort_values("excess_kurtosis", ascending=False)
                .reset_index(drop=True))
    daily_df.to_csv(ANALYSIS / "daily_volatility_stats.csv", index=False)
    print(f"    daily_volatility_stats.csv: {len(daily_df)} currencies")

    print("  Computing yearly volatility stats...")
    yearly_stats = []
    for country in yearly_ret.columns:
        r = yearly_ret[country].dropna().values
        if len(r) < 3:
            continue
        years = yearly_ret[country].dropna().index.values

        yearly_stats.append({
            "country": country,
            "n_years": len(r),
            "start_year": int(years.min()),
            "end_year": int(years.max()),
            "mean_log_return": r.mean(),
            "annual_volatility": r.std(ddof=1),
            "excess_kurtosis": kurtosis(r, fisher=True),
            "max_annual_log_return": r.max(),
            "min_annual_log_return": r.min(),
        })

    yearly_df = (pd.DataFrame(yearly_stats)
                 .sort_values("excess_kurtosis", ascending=False)
                 .reset_index(drop=True))
    yearly_df.to_csv(ANALYSIS / "yearly_volatility_stats.csv", index=False)
    print(f"    yearly_volatility_stats.csv: {len(yearly_df)} countries")


def build_correlations(daily_ret, yearly_ret):
    """Compute pairwise correlation matrices of log returns."""
    print("  Computing daily correlation matrix...")
    daily_wide = daily_ret.pivot(index="date", columns="currency", values="log_return")
    daily_corr = daily_wide.corr()
    daily_corr.to_csv(ANALYSIS / "daily_correlation_matrix.csv")
    print(f"    daily_correlation_matrix.csv: {daily_corr.shape[0]}x{daily_corr.shape[1]}")

    print("  Computing yearly correlation matrix...")
    yearly_corr = yearly_ret.corr(min_periods=30)
    yearly_corr.to_csv(ANALYSIS / "yearly_correlation_matrix.csv")
    n_valid = yearly_corr.notna().sum().sum() - len(yearly_corr)
    print(f"    yearly_correlation_matrix.csv: {yearly_corr.shape[0]}x{yearly_corr.shape[1]} "
          f"({n_valid} valid pairs)")


TROY_OZ_GRAMS = 31.1035


def build_gold_inflation(daily_long):
    """Compute gold inflation in local currency at yearly and monthly granularity."""
    # --- Yearly gold inflation ---
    print("  Computing yearly gold inflation...")
    gold_raw = pd.read_csv(SOURCES / "measuringworth" / "measuringworth_gold_prices.csv")
    gold_raw["year"] = gold_raw["year"].astype(int)

    gold_usd = gold_raw[["year", "new_york_market_usd", "us_official_usd"]].copy()
    gold_usd["gold_usd"] = gold_usd["new_york_market_usd"].fillna(gold_usd["us_official_usd"])
    gold_usd = gold_usd[["year", "gold_usd"]].dropna()

    gold_gbp = gold_raw[["year", "british_official_gbp"]].dropna()
    gold_gbp = gold_gbp.rename(columns={"british_official_gbp": "gold_gbp"})

    panel = pd.read_csv(NORM / "yearly_unified_panel.csv")

    ci_gbp = pd.read_csv(SOURCES / "clio_infra" / "clio_infra_exchange_rates_gbp.csv")
    ci_gbp_long = ci_gbp.melt(id_vars=["year"], var_name="country", value_name="rate_per_gbp")
    ci_gbp_long = ci_gbp_long.dropna(subset=["rate_per_gbp"])
    ci_gbp_long["year"] = ci_gbp_long["year"].astype(int)

    cpi = pd.read_csv(SOURCES / "clio_infra" / "clio_infra_inflation.csv")
    cpi_long = cpi.melt(id_vars=["year"], var_name="country", value_name="cpi_inflation_pct")
    cpi_long = cpi_long.dropna(subset=["cpi_inflation_pct"])
    cpi_long["year"] = cpi_long["year"].astype(int)

    # Gold in local currency via USD rates
    usd_based = panel.merge(gold_usd, on="year", how="inner")
    usd_based["gold_local"] = usd_based["gold_usd"] * usd_based["rate_per_usd"]

    # UK direct from GBP gold
    uk_gbp = gold_gbp.copy()
    uk_gbp["country"] = "United Kingdom"
    uk_gbp["gold_local"] = uk_gbp["gold_gbp"]

    # Pre-1791 via GBP exchange rates
    pre_1791 = ci_gbp_long[ci_gbp_long["year"] < 1791].merge(gold_gbp, on="year", how="inner")
    pre_1791["gold_local"] = pre_1791["gold_gbp"] * pre_1791["rate_per_gbp"]

    all_gold = pd.concat([
        usd_based[["year", "country", "gold_local"]],
        uk_gbp[["year", "country", "gold_local"]],
        pre_1791[["year", "country", "gold_local"]],
    ], ignore_index=True)
    all_gold = all_gold.sort_values(["country", "year"]).drop_duplicates(
        subset=["year", "country"], keep="first")

    all_gold["gold_local_prev"] = all_gold.groupby("country")["gold_local"].shift(1)
    all_gold["gold_inflation_pct"] = ((all_gold["gold_local"] / all_gold["gold_local_prev"]) - 1) * 100
    all_gold["gold_log_return"] = np.log(all_gold["gold_local"] / all_gold["gold_local_prev"])
    all_gold["grams_per_100"] = (100.0 / all_gold["gold_local"]) * TROY_OZ_GRAMS
    all_gold["base_gold"] = all_gold.groupby("country")["gold_local"].transform("first")
    all_gold["base_year"] = all_gold.groupby("country")["year"].transform("first")
    all_gold["cumulative_retained_pct"] = (all_gold["base_gold"] / all_gold["gold_local"]) * 100
    all_gold["decade"] = (all_gold["year"] // 10) * 10

    yearly = all_gold.merge(cpi_long, on=["year", "country"], how="left")
    yearly["gold_vs_cpi_gap_pct"] = yearly["gold_inflation_pct"] - yearly["cpi_inflation_pct"]

    yearly_out = yearly[["year", "decade", "country", "gold_local", "grams_per_100",
                          "gold_inflation_pct", "gold_log_return",
                          "cpi_inflation_pct", "gold_vs_cpi_gap_pct",
                          "cumulative_retained_pct", "base_year"]].copy()
    yearly_out = yearly_out.sort_values(["year", "country"]).reset_index(drop=True)
    for c in ["gold_local", "grams_per_100"]:
        yearly_out[c] = yearly_out[c].round(4)
    for c in ["gold_inflation_pct", "gold_log_return", "cpi_inflation_pct",
              "gold_vs_cpi_gap_pct", "cumulative_retained_pct"]:
        yearly_out[c] = yearly_out[c].round(4)
    yearly_out["base_year"] = yearly_out["base_year"].astype(int)

    yearly_out.to_csv(ANALYSIS / "yearly_gold_inflation.csv", index=False)
    print(f"    yearly_gold_inflation.csv: {len(yearly_out):,} rows, "
          f"{yearly_out['country'].nunique()} countries")

    # --- Monthly gold inflation ---
    print("  Computing monthly gold inflation...")
    gold_monthly = pd.read_csv(SOURCES / "gold" / "gold_monthly_usd.csv")
    gold_monthly["date"] = pd.to_datetime(gold_monthly["Date"])
    gold_monthly["year_month"] = gold_monthly["date"].dt.to_period("M")
    gold_monthly = gold_monthly.rename(columns={"Price": "gold_usd"})[["year_month", "gold_usd"]]

    # FRED daily -> monthly averages
    daily = daily_long.copy()
    daily["date"] = pd.to_datetime(daily["date"])
    daily["year_month"] = daily["date"].dt.to_period("M")
    monthly_fx = daily.groupby(["year_month", "currency"])["rate_per_usd"].mean().reset_index()
    monthly_fx["source"] = "FRED"

    # IMF monthly
    imf = pd.read_csv(SOURCES / "imf" / "imf_exchange_rates.csv")
    imf["date"] = pd.to_datetime(imf["Date"])
    imf["year_month"] = imf["date"].dt.to_period("M")
    imf["Rate"] = pd.to_numeric(imf["Rate"], errors="coerce")
    imf = imf.dropna(subset=["Rate"])
    imf_monthly = imf.groupby(["year_month", imf["Currency"]])["Rate"].mean().reset_index()
    imf_monthly.columns = ["year_month", "currency", "rate_per_usd"]
    imf_monthly["source"] = "IMF"

    all_fx = pd.concat([monthly_fx, imf_monthly], ignore_index=True)
    all_fx = all_fx.sort_values(["source"]).drop_duplicates(
        subset=["year_month", "currency"], keep="first")

    merged = all_fx.merge(gold_monthly, on="year_month", how="inner")
    merged["gold_local"] = merged["gold_usd"] * merged["rate_per_usd"]
    merged["grams_per_100"] = (100.0 / merged["gold_local"]) * TROY_OZ_GRAMS

    merged = merged.sort_values(["currency", "year_month"])
    merged["gold_local_prev"] = merged.groupby("currency")["gold_local"].shift(1)
    merged["gold_inflation_mom_pct"] = ((merged["gold_local"] / merged["gold_local_prev"]) - 1) * 100
    merged["gold_log_return"] = np.log(merged["gold_local"] / merged["gold_local_prev"])
    merged["gold_local_12m"] = merged.groupby("currency")["gold_local"].shift(12)
    merged["gold_inflation_yoy_pct"] = ((merged["gold_local"] / merged["gold_local_12m"]) - 1) * 100
    merged["base_gold"] = merged.groupby("currency")["gold_local"].transform("first")
    merged["cumulative_retained_pct"] = (merged["base_gold"] / merged["gold_local"]) * 100

    monthly_out = merged[["year_month", "currency", "source", "rate_per_usd", "gold_usd",
                           "gold_local", "grams_per_100", "gold_inflation_mom_pct",
                           "gold_log_return", "gold_inflation_yoy_pct",
                           "cumulative_retained_pct"]].copy()
    monthly_out["year_month"] = monthly_out["year_month"].astype(str)
    monthly_out = monthly_out.sort_values(["year_month", "currency"]).reset_index(drop=True)
    for c in ["rate_per_usd", "gold_usd", "gold_local", "grams_per_100"]:
        monthly_out[c] = monthly_out[c].round(4)
    for c in ["gold_inflation_mom_pct", "gold_log_return", "gold_inflation_yoy_pct",
              "cumulative_retained_pct"]:
        monthly_out[c] = monthly_out[c].round(4)

    monthly_out.to_csv(ANALYSIS / "monthly_gold_inflation.csv", index=False)
    print(f"    monthly_gold_inflation.csv: {len(monthly_out):,} rows, "
          f"{monthly_out['currency'].nunique()} currencies")


def main():
    print("forex-centuries build pipeline\n")

    NORM.mkdir(parents=True, exist_ok=True)
    ANALYSIS.mkdir(parents=True, exist_ok=True)

    print("[1/6] FRED daily normalization")
    daily_long = build_fred_daily()

    print("\n[2/6] Yearly unified panel")
    build_yearly_panel()

    print("\n[3/6] Log returns")
    daily_ret, yearly_ret = build_log_returns(daily_long)

    print("\n[4/6] Volatility statistics")
    build_volatility_stats(daily_ret, yearly_ret)

    print("\n[5/6] Correlation matrices")
    build_correlations(daily_ret, yearly_ret)

    print("\n[6/6] Gold inflation")
    build_gold_inflation(daily_long)

    print("\nDone. All derived files regenerated.")


if __name__ == "__main__":
    main()
