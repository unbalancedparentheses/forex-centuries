"""
forex-centuries quickstart (pandas version)
Load and explore historical exchange rate data spanning 1106-2026.

pip install pandas openpyxl
"""

import pandas as pd
from pathlib import Path

DATA = Path(__file__).parent / "data"


def load_yearly_panel() -> pd.DataFrame:
    """Unified yearly panel: 243 countries, 1500-2025.
    Columns: year, country, rate_per_usd, source (MW/CI/GMD).
    """
    df = pd.read_csv(DATA / "derived/normalized/yearly_unified_panel.csv")
    df["year"] = df["year"].astype(int)
    return df


def load_yearly_wide() -> pd.DataFrame:
    """Same as yearly panel but pivoted: year x country matrix."""
    df = pd.read_csv(DATA / "derived/normalized/yearly_unified_wide.csv", index_col="year")
    df.index = df.index.astype(int)
    return df


def load_daily_normalized() -> pd.DataFrame:
    """23 FRED daily pairs, all foreign-per-USD. 271K obs."""
    df = pd.read_csv(DATA / "derived/normalized/fred_daily_normalized.csv")
    df["date"] = pd.to_datetime(df["date"])
    return df


def load_daily_wide() -> pd.DataFrame:
    """Same as daily normalized but pivoted: date x currency."""
    df = pd.read_csv(DATA / "derived/normalized/fred_daily_normalized_wide.csv", index_col="date")
    df.index = pd.to_datetime(df.index)
    return df


def load_imf() -> pd.DataFrame:
    """IMF IFS monthly rates: 168 currencies, 1955-2025."""
    df = pd.read_csv(DATA / "sources/imf/imf_exchange_rates.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    df["Rate"] = pd.to_numeric(df["Rate"], errors="coerce")
    return df


def load_medieval_spufford() -> pd.DataFrame:
    """13,197 medieval exchange quotations (1106-1500)."""
    return pd.read_csv(DATA / "sources/memdb/memdb_spufford_medieval_exchange_rates.csv")


def load_medieval_metz() -> pd.DataFrame:
    """50,559 early modern currency records (1350-1800)."""
    return pd.read_csv(DATA / "sources/memdb/memdb_metz_currency_exchanges.csv")


def load_gold_inflation() -> pd.DataFrame:
    """Yearly gold inflation for 243 countries, 1257-2025.
    Includes purchasing power (grams per 100 local), CPI comparison,
    cumulative debasement. Use 'decade' column to aggregate."""
    return pd.read_csv(DATA / "derived/analysis/yearly_gold_inflation.csv")


def load_gold_prices() -> pd.DataFrame:
    """Annual gold prices, 1257-2025. Six series: british_official_gbp,
    london_market_gbp, london_market_usd, us_official_usd,
    new_york_market_usd, gold_silver_ratio."""
    df = pd.read_csv(DATA / "sources/measuringworth/measuringworth_gold_prices.csv")
    df["year"] = df["year"].astype(int)
    return df.set_index("year")


def load_volatility_stats(freq: str = "daily") -> pd.DataFrame:
    """Precomputed volatility statistics. freq: 'daily' or 'yearly'."""
    return pd.read_csv(DATA / f"derived/analysis/{freq}_volatility_stats.csv")


def load_log_returns(freq: str = "daily") -> pd.DataFrame:
    """Precomputed log returns. freq: 'daily' or 'yearly'."""
    df = pd.read_csv(DATA / f"derived/analysis/{freq}_log_returns.csv")
    if freq == "daily":
        df["date"] = pd.to_datetime(df["date"])
    return df


def load_regimes() -> pd.DataFrame:
    """IRR coarse regime classification."""
    return pd.read_csv(DATA / "sources/irr/irr_regime_coarse.csv")


def load_jst() -> pd.DataFrame:
    """Jorda-Schularick-Taylor macrohistory (18 countries, 1870-2017)."""
    return pd.read_excel(DATA / "sources/jst/jst_macrohistory.xlsx")


if __name__ == "__main__":
    print("forex-centuries quickstart (pandas)\n")

    # Yearly panel
    panel = load_yearly_panel()
    print(f"Yearly panel: {len(panel):,} obs, {panel['country'].nunique()} countries, "
          f"{panel['year'].min()}-{panel['year'].max()}")
    print(f"Sources: {panel['source'].value_counts().to_dict()}\n")

    # Longest series
    counts = panel.groupby("country").agg(
        n=("year", "count"),
        start=("year", "min"),
        end=("year", "max"),
    ).sort_values("n", ascending=False)
    print("Longest series:")
    print(counts.head(10).to_string())

    # Daily
    daily = load_daily_wide()
    print(f"\nDaily: {daily.shape[0]:,} dates x {daily.shape[1]} currencies "
          f"({daily.index.min().date()} to {daily.index.max().date()})")

    # Log returns and vol
    log_ret = daily.pct_change().apply(lambda x: x.dropna())
    print(f"\nAnnualized vol (last 5 years):")
    recent = daily.loc["2020":].pct_change().std() * (252 ** 0.5)
    print(recent.sort_values(ascending=False).head(10).to_string())

    # Volatility stats
    stats = load_volatility_stats("daily")
    print(f"\nFat tails (excess kurtosis, top 5):")
    top = stats.nlargest(5, "excess_kurtosis")[["currency", "annualized_volatility", "excess_kurtosis", "tail_ratio"]]
    print(top.to_string(index=False))

    # Medieval
    spuf = load_medieval_spufford()
    metz = load_medieval_metz()
    print(f"\nMedieval: {len(spuf):,} Spufford + {len(metz):,} Metz records")
    print(f"Spufford places: {spuf['Place'].nunique()} cities")
    print(f"Metz places: {metz['Place'].nunique()} cities")
