"""
build.py — Reproducible ETL pipeline for forex-centuries.
Regenerates all data/derived/ files from data/sources/.

Usage: python build.py
"""

import numpy as np
import pandas as pd
from datetime import date
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


def _round_and_write(df, path, precision_4=(), precision_6=()):
    """Round specified columns and write CSV."""
    for c in precision_4:
        df[c] = df[c].round(4)
    for c in precision_6:
        df[c] = df[c].round(6)
    df.to_csv(path, index=False)


def build_fred_daily():
    """Normalize all FRED daily CSVs to foreign-per-USD convention."""
    print("  Loading FRED daily files...")
    fred_dir = SOURCES / "fred" / "daily"
    if not fred_dir.exists():
        raise FileNotFoundError(f"FRED source directory missing: {fred_dir}")
    frames = []
    for f in sorted(fred_dir.glob("fred_*.csv")):
        if f.name in SKIP_FILES:
            continue
        parts = f.stem.split("_")
        if len(parts) < 2:
            print(f"    Skipping malformed filename: {f.name}")
            continue
        currency = parts[1].upper()
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
    gmd = gmd[gmd["year"] <= date.today().year]
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

    # Yearly log returns use MeasuringWorth only (not the full unified panel) because
    # MW is carefully curated for continuity — Clio Infra and GMD may have rate jumps
    # at redenomination boundaries that produce spurious log returns.
    # "Europe, Eurozone" is excluded: only 26 years of data (1999-2025) and overlaps
    # with constituent countries (Germany, France, etc.) in the correlation analysis.
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
        ann_vol = daily_vol * np.sqrt(TRADING_DAYS_PER_YEAR)
        threshold = TAIL_SIGMA_THRESHOLD * daily_vol
        tail_events = int(np.sum(np.abs(r) > threshold))
        expected = n * 2 * norm.sf(TAIL_SIGMA_THRESHOLD)

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
        clean = yearly_ret[country].dropna()
        r = clean.values
        if len(r) < 3:
            continue
        years = clean.index.values

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
    yearly_corr = yearly_ret.corr(min_periods=MIN_OVERLAP_YEARS)
    yearly_corr.to_csv(ANALYSIS / "yearly_correlation_matrix.csv")
    n_valid = yearly_corr.notna().sum().sum() - len(yearly_corr)
    print(f"    yearly_correlation_matrix.csv: {yearly_corr.shape[0]}x{yearly_corr.shape[1]} "
          f"({n_valid} valid pairs)")


TROY_OZ_GRAMS = 31.1035
TRADING_DAYS_PER_YEAR = 252
TAIL_SIGMA_THRESHOLD = 3
MIN_OVERLAP_YEARS = 30
MIN_REGIME_OBSERVATIONS = 10


def _safe_pct_change(current, previous):
    """Percentage change that returns NaN instead of inf for zero/NaN rates."""
    mask = (previous > 0) & (current > 0) & previous.notna()
    result = pd.Series(np.nan, index=current.index)
    result[mask] = ((current[mask] / previous[mask]) - 1) * 100
    return result


def _safe_log_return(current, previous):
    """Log return that returns NaN instead of -inf for zero/NaN rates."""
    mask = (previous > 0) & (current > 0) & previous.notna()
    result = pd.Series(np.nan, index=current.index)
    result[mask] = np.log(current[mask] / previous[mask])
    return result


def build_rolling_volatility(daily_long):
    """Compute rolling annualized volatility for all daily currencies."""
    print("  Computing rolling volatility...")
    wide = daily_long.pivot(index="date", columns="currency", values="rate_per_usd")
    wide.index = pd.to_datetime(wide.index)
    log_ret = np.log(wide / wide.shift(1))

    rolling = log_ret.rolling(TRADING_DAYS_PER_YEAR).std() * np.sqrt(TRADING_DAYS_PER_YEAR)
    rolling = rolling.dropna(how="all")

    # Long format
    long = rolling.reset_index().melt(
        id_vars=["date"], var_name="currency", value_name="rolling_volatility_252d")
    long = long.dropna(subset=["rolling_volatility_252d"])
    long["date"] = long["date"].dt.strftime("%Y-%m-%d")
    long = long.sort_values(["date", "currency"]).reset_index(drop=True)
    long["rolling_volatility_252d"] = long["rolling_volatility_252d"].round(6)

    long.to_csv(ANALYSIS / "daily_rolling_volatility.csv", index=False)
    print(f"    daily_rolling_volatility.csv: {len(long):,} rows")


FINE_TO_COARSE = {}
for f in range(1, 5):
    FINE_TO_COARSE[f] = 1   # peg
for f in range(5, 9):
    FINE_TO_COARSE[f] = 2   # crawling peg
for f in range(9, 13):
    FINE_TO_COARSE[f] = 3   # managed float
FINE_TO_COARSE[13] = 4      # free float
FINE_TO_COARSE[14] = 5      # freely falling
FINE_TO_COARSE[15] = 6      # dual market

COARSE_LABELS = {
    1: "peg", 2: "crawling_peg", 3: "managed_float",
    4: "free_float", 5: "freely_falling", 6: "dual_market",
}


def build_regime_analysis(yearly_ret=None):
    """Parse IRR fine regime data and compute regime-conditional statistics."""
    print("  Parsing IRR fine regime data...")
    # The fine CSV has actual numeric values (unlike coarse which has Excel formulas).
    # Header: rows 0-4 are metadata, row 5 has partial country names (first word),
    # row 6 has the rest of country names, row 7 is blank, data starts at row 8.
    # Column 0 is empty, column 1 is month label (e.g. "1940M1"), columns 2+ are values.
    raw = pd.read_csv(SOURCES / "irr" / "irr_regime_fine.csv", header=None)

    # Extract country names from rows 5 and 6 (0-indexed: 4 and 5)
    row_a = raw.iloc[4, 2:].fillna("").astype(str).str.strip()
    row_b = raw.iloc[5, 2:].fillna("").astype(str).str.strip()
    countries = []
    for a, b in zip(row_a, row_b):
        name = f"{a} {b}".strip() if b else a
        countries.append(name)

    # Extract data rows (skip metadata rows 0-7)
    data = raw.iloc[7:].copy()
    data = data.dropna(subset=[1])  # keep rows with month labels
    data[1] = data[1].astype(str).str.strip()
    data = data[data[1].str.match(r"^\d{4}M\d+$", na=False)]

    # Parse month labels
    months = data[1].values
    values = data.iloc[:, 2:2+len(countries)].values

    # Build long-format DataFrame
    records = []
    for i, month in enumerate(months):
        year = int(month.split("M")[0])
        for j, country in enumerate(countries):
            if not country:
                continue
            val = values[i, j] if j < values.shape[1] else np.nan
            try:
                fine = int(float(val))
            except (ValueError, TypeError):
                continue
            coarse = FINE_TO_COARSE.get(fine)
            if coarse is None:
                print(f"    Warning: unmapped fine regime code {fine} "
                      f"for {country} in {month}")
                continue
            records.append({
                "year": year,
                "month": month,
                "country": country,
                "fine_regime": fine,
                "coarse_regime": coarse,
                "regime_label": COARSE_LABELS[coarse],
            })

    regime_df = pd.DataFrame(records)

    # Aggregate to yearly (modal regime per country-year)
    yearly_regime = (regime_df.groupby(["year", "country"])["coarse_regime"]
                     .agg(lambda x: x.mode().iloc[0] if not x.mode().empty else np.nan)
                     .reset_index())
    yearly_regime = yearly_regime.dropna(subset=["coarse_regime"])
    yearly_regime["coarse_regime"] = yearly_regime["coarse_regime"].astype(int)
    yearly_regime["regime_label"] = yearly_regime["coarse_regime"].map(COARSE_LABELS)

    yearly_regime.to_csv(ANALYSIS / "yearly_regime_classification.csv", index=False)
    print(f"    yearly_regime_classification.csv: {len(yearly_regime):,} rows, "
          f"{yearly_regime['country'].nunique()} countries")

    # Compute regime-conditional volatility stats using yearly log returns
    print("  Computing regime-conditional statistics...")
    if yearly_ret is None:
        try:
            yearly_ret = pd.read_csv(ANALYSIS / "yearly_log_returns.csv", index_col="year")
        except FileNotFoundError:
            print("    Skipping: yearly_log_returns.csv not found")
            return

    ret_long = yearly_ret.reset_index().melt(
        id_vars=["year"], var_name="country", value_name="log_return")
    ret_long = ret_long.dropna(subset=["log_return"])

    merged = ret_long.merge(yearly_regime, on=["year", "country"], how="inner")

    stats = []
    for label, grp in merged.groupby("regime_label"):
        r = grp["log_return"].values
        if len(r) < MIN_REGIME_OBSERVATIONS:
            continue
        stats.append({
            "regime": label,
            "n_observations": len(r),
            "n_countries": grp["country"].nunique(),
            "mean_log_return": round(r.mean(), 6),
            "volatility": round(r.std(ddof=1), 6),
            "excess_kurtosis": round(kurtosis(r, fisher=True), 4),
            "skewness": round(skew(r), 4),
            "max_return": round(r.max(), 6),
            "min_return": round(r.min(), 6),
        })

    stats_df = pd.DataFrame(stats).sort_values("volatility", ascending=False)
    stats_df.to_csv(ANALYSIS / "regime_conditional_stats.csv", index=False)
    print(f"    regime_conditional_stats.csv: {len(stats_df)} regimes")

    return yearly_regime


def _build_yearly_gold(panel):
    """Compute yearly gold inflation in local currency."""
    print("  Computing yearly gold inflation...")
    gold_raw = pd.read_csv(SOURCES / "measuringworth" / "measuringworth_gold_prices.csv")
    gold_raw["year"] = gold_raw["year"].astype(int)

    gold_usd = gold_raw[["year", "new_york_market_usd", "us_official_usd"]].copy()
    gold_usd["gold_usd"] = gold_usd["new_york_market_usd"].fillna(gold_usd["us_official_usd"])
    gold_usd = gold_usd[["year", "gold_usd"]].dropna()

    gold_gbp = gold_raw[["year", "british_official_gbp"]].dropna()
    gold_gbp = gold_gbp.rename(columns={"british_official_gbp": "gold_gbp"})

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

    # Priority: direct GBP measurements > GBP cross-rates > USD-based.
    # Concat order matters: keep="first" retains the earliest entry per (year, country).
    all_gold = pd.concat([
        uk_gbp[["year", "country", "gold_local"]],
        pre_1791[["year", "country", "gold_local"]],
        usd_based[["year", "country", "gold_local"]],
    ], ignore_index=True)
    all_gold = all_gold.sort_values(["country", "year"]).drop_duplicates(
        subset=["year", "country"], keep="first")

    all_gold["gold_local_prev"] = all_gold.groupby("country")["gold_local"].shift(1)
    all_gold["gold_inflation_pct"] = _safe_pct_change(all_gold["gold_local"], all_gold["gold_local_prev"])
    all_gold["gold_log_return"] = _safe_log_return(all_gold["gold_local"], all_gold["gold_local_prev"])
    all_gold["grams_per_100"] = np.where(
        all_gold["gold_local"] > 0,
        (100.0 / all_gold["gold_local"]) * TROY_OZ_GRAMS,
        np.nan,
    )
    all_gold["base_gold"] = all_gold.groupby("country")["gold_local"].transform("first")
    all_gold["base_year"] = all_gold.groupby("country")["year"].transform("first")
    all_gold["cumulative_retained_pct"] = np.where(
        all_gold["gold_local"] > 0,
        (all_gold["base_gold"] / all_gold["gold_local"]) * 100,
        np.nan,
    )
    all_gold["decade"] = (all_gold["year"] // 10) * 10

    yearly = all_gold.merge(cpi_long, on=["year", "country"], how="left")
    yearly["gold_vs_cpi_gap_pct"] = yearly["gold_inflation_pct"] - yearly["cpi_inflation_pct"]

    yearly_out = yearly[["year", "decade", "country", "gold_local", "grams_per_100",
                          "gold_inflation_pct", "gold_log_return",
                          "cpi_inflation_pct", "gold_vs_cpi_gap_pct",
                          "cumulative_retained_pct", "base_year"]].copy()
    yearly_out = yearly_out.sort_values(["year", "country"]).reset_index(drop=True)
    yearly_out["base_year"] = yearly_out["base_year"].astype(int)
    _round_and_write(yearly_out, ANALYSIS / "yearly_gold_inflation.csv",
                     precision_4=["gold_local", "grams_per_100", "gold_inflation_pct",
                                  "gold_log_return", "cpi_inflation_pct",
                                  "gold_vs_cpi_gap_pct", "cumulative_retained_pct"])
    print(f"    yearly_gold_inflation.csv: {len(yearly_out):,} rows, "
          f"{yearly_out['country'].nunique()} countries")


def _build_monthly_gold(daily_long):
    """Compute monthly gold inflation in local currency."""
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
    imf_monthly = imf.groupby(["year_month", "Currency"])["Rate"].mean().reset_index()
    imf_monthly = imf_monthly.rename(columns={"Currency": "currency", "Rate": "rate_per_usd"})
    imf_monthly["source"] = "IMF"

    # Priority: FRED > IMF (explicit sort, not relying on alphabetical order)
    fx_priority = {"FRED": 0, "IMF": 1}
    all_fx = pd.concat([monthly_fx, imf_monthly], ignore_index=True)
    all_fx["_priority"] = all_fx["source"].map(fx_priority)
    all_fx = all_fx.sort_values("_priority").drop_duplicates(
        subset=["year_month", "currency"], keep="first").drop(columns=["_priority"])

    merged = all_fx.merge(gold_monthly, on="year_month", how="inner")
    merged["gold_local"] = merged["gold_usd"] * merged["rate_per_usd"]
    merged["grams_per_100"] = np.where(
        merged["gold_local"] > 0,
        (100.0 / merged["gold_local"]) * TROY_OZ_GRAMS,
        np.nan,
    )

    merged = merged.sort_values(["currency", "year_month"])
    merged["gold_local_prev"] = merged.groupby("currency")["gold_local"].shift(1)
    merged["gold_inflation_mom_pct"] = _safe_pct_change(merged["gold_local"], merged["gold_local_prev"])
    merged["gold_log_return"] = _safe_log_return(merged["gold_local"], merged["gold_local_prev"])
    # YoY: join on (currency, year_month - 12 months) instead of row-based shift,
    # so missing months don't corrupt the calculation.
    merged["ym_12m_ago"] = merged["year_month"] - 12
    yoy_lookup = merged[["currency", "year_month", "gold_local"]].rename(
        columns={"year_month": "ym_12m_ago", "gold_local": "gold_local_12m"})
    merged = merged.merge(yoy_lookup, on=["currency", "ym_12m_ago"], how="left")
    merged["gold_inflation_yoy_pct"] = _safe_pct_change(merged["gold_local"], merged["gold_local_12m"])
    merged["base_gold"] = merged.groupby("currency")["gold_local"].transform("first")
    merged["cumulative_retained_pct"] = np.where(
        merged["gold_local"] > 0,
        (merged["base_gold"] / merged["gold_local"]) * 100,
        np.nan,
    )

    monthly_out = merged[["year_month", "currency", "source", "rate_per_usd", "gold_usd",
                           "gold_local", "grams_per_100", "gold_inflation_mom_pct",
                           "gold_log_return", "gold_inflation_yoy_pct",
                           "cumulative_retained_pct"]].copy()
    monthly_out["year_month"] = monthly_out["year_month"].astype(str)
    monthly_out = monthly_out.sort_values(["year_month", "currency"]).reset_index(drop=True)
    _round_and_write(monthly_out, ANALYSIS / "monthly_gold_inflation.csv",
                     precision_4=["rate_per_usd", "gold_usd", "gold_local", "grams_per_100",
                                  "gold_inflation_mom_pct", "gold_log_return",
                                  "gold_inflation_yoy_pct", "cumulative_retained_pct"])
    print(f"    monthly_gold_inflation.csv: {len(monthly_out):,} rows, "
          f"{monthly_out['currency'].nunique()} currencies")


def build_gold_inflation(daily_long, panel):
    """Compute gold inflation in local currency at yearly and monthly granularity."""
    _build_yearly_gold(panel)
    _build_monthly_gold(daily_long)


def main():
    print("forex-centuries build pipeline\n")

    NORM.mkdir(parents=True, exist_ok=True)
    ANALYSIS.mkdir(parents=True, exist_ok=True)

    print("[1/8] FRED daily normalization")
    daily_long = build_fred_daily()

    print("\n[2/8] Yearly unified panel")
    panel = build_yearly_panel()

    print("\n[3/8] Log returns")
    daily_ret, yearly_ret = build_log_returns(daily_long)

    print("\n[4/8] Volatility statistics")
    build_volatility_stats(daily_ret, yearly_ret)

    print("\n[5/8] Correlation matrices")
    build_correlations(daily_ret, yearly_ret)

    print("\n[6/8] Rolling volatility")
    build_rolling_volatility(daily_long)

    print("\n[7/8] Regime analysis")
    build_regime_analysis(yearly_ret)

    print("\n[8/8] Gold inflation")
    build_gold_inflation(daily_long, panel)

    print("\nDone. All derived files regenerated.")


if __name__ == "__main__":
    main()
