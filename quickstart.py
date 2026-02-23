"""
forex-centuries quickstart
Load and explore historical exchange rate data spanning 1106-2025.
"""

import csv
from pathlib import Path

DATA = Path(__file__).parent / "data"


def load_csv(path, **kwargs):
    """Load a CSV into a list of dicts."""
    with open(path) as f:
        return list(csv.DictReader(f, **kwargs))


def load_yearly_panel():
    """Load the unified yearly panel (243 countries, 1500-2025).
    Returns list of dicts with keys: year, country, rate_per_usd, source (MW/CI/GMD).
    """
    return load_csv(DATA / "derived/normalized/yearly_unified_panel.csv")


def load_daily_normalized():
    """Load normalized FRED daily data (23 currencies, 1971-2025).
    All rates in foreign-currency-per-USD convention.
    Returns list of dicts with keys: date, currency, rate_per_usd.
    """
    return load_csv(DATA / "derived/normalized/fred_daily_normalized.csv")


def load_medieval_spufford():
    """Load Spufford medieval exchange rates (13,197 records, 1106-1500)."""
    return load_csv(DATA / "sources/memdb/memdb_spufford_medieval_exchange_rates.csv")


def load_medieval_metz():
    """Load Metz currency exchanges (50,559 records, 1350-1800)."""
    return load_csv(DATA / "sources/memdb/memdb_metz_currency_exchanges.csv")


def load_volatility_stats(freq="daily"):
    """Load precomputed volatility statistics.
    freq: 'daily' or 'yearly'
    """
    return load_csv(DATA / f"derived/analysis/{freq}_volatility_stats.csv")


def load_log_returns(freq="daily"):
    """Load precomputed log returns.
    freq: 'daily' or 'yearly'
    """
    return load_csv(DATA / f"derived/analysis/{freq}_log_returns.csv")


if __name__ == "__main__":
    print("forex-centuries quickstart\n")

    # Yearly panel
    panel = load_yearly_panel()
    countries = set(r["country"] for r in panel)
    years = [int(r["year"]) for r in panel]
    print(f"Yearly panel: {len(panel):,} observations, {len(countries)} countries, {min(years)}-{max(years)}")

    # Show longest series
    from collections import Counter
    counts = Counter(r["country"] for r in panel)
    print("\nLongest series:")
    for country, n in counts.most_common(10):
        yrs = sorted(int(r["year"]) for r in panel if r["country"] == country)
        print(f"  {country:<25} {n:>4} years ({yrs[0]}-{yrs[-1]})")

    # Daily data
    daily = load_daily_normalized()
    currencies = set(r["currency"] for r in daily)
    print(f"\nDaily data: {len(daily):,} observations, {len(currencies)} currencies")

    # Volatility stats
    stats = load_volatility_stats("daily")
    print("\nDaily volatility (sorted by excess kurtosis):")
    stats_sorted = sorted(stats, key=lambda x: -float(x["excess_kurtosis"]))
    print(f"  {'Currency':<8} {'Ann Vol':>8} {'Kurtosis':>10} {'Tail Ratio':>12}")
    for s in stats_sorted[:10]:
        ann_vol = f"{float(s['annualized_volatility'])*100:.1f}%"
        print(f"  {s['currency']:<8} {ann_vol:>8} {float(s['excess_kurtosis']):>10.1f} {float(s['tail_ratio']):>11.1f}x")

    # Medieval
    spufford = load_medieval_spufford()
    metz = load_medieval_metz()
    print(f"\nMedieval data: {len(spufford):,} Spufford + {len(metz):,} Metz records")
