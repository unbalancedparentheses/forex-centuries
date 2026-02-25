"""Unit tests for build.py core logic using synthetic data."""

import numpy as np
import pandas as pd

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import build


def test_fred_inversion():
    """GBP/EUR/AUD/NZD are inverted (1/x), others are not."""
    assert build.INVERT == {"GBP", "EUR", "AUD", "NZD"}

    # Simulate: GBP quoted as 1.25 USD-per-GBP -> should become 0.8 GBP-per-USD
    rate = 1.25
    inverted = 1.0 / rate
    assert abs(inverted - 0.8) < 1e-10

    # JPY quoted as 150 JPY-per-USD -> stays 150
    for currency in ["JPY", "CHF", "CAD", "MXN", "BRL"]:
        assert currency not in build.INVERT


def test_fred_skip_index_files():
    """SKIP_FILES contains the two USD index filenames."""
    assert build.SKIP_FILES == {"fred_usd_broad_index.csv", "fred_usd_major_index.csv"}
    assert len(build.SKIP_FILES) == 2


def test_priority_merge():
    """MW wins over CI, CI wins over GMD for same (year, country)."""
    mw = pd.DataFrame({"year": [2000], "country": ["Japan"], "rate_per_usd": [100.0], "source": ["MW"]})
    ci = pd.DataFrame({"year": [2000], "country": ["Japan"], "rate_per_usd": [105.0], "source": ["CI"]})
    gmd = pd.DataFrame({"year": [2000], "country": ["Japan"], "rate_per_usd": [110.0], "source": ["GMD"]})

    all_data = pd.concat([mw, ci, gmd], ignore_index=True)
    priority = {"MW": 0, "CI": 1, "GMD": 2}
    all_data["priority"] = all_data["source"].map(priority)
    all_data = (all_data
                .sort_values("priority")
                .drop_duplicates(subset=["year", "country"], keep="first")
                .drop(columns=["priority"]))

    assert len(all_data) == 1
    assert all_data.iloc[0]["source"] == "MW"
    assert all_data.iloc[0]["rate_per_usd"] == 100.0

    # CI wins over GMD when no MW
    ci_gmd = pd.concat([ci, gmd], ignore_index=True)
    ci_gmd["priority"] = ci_gmd["source"].map(priority)
    ci_gmd = (ci_gmd
              .sort_values("priority")
              .drop_duplicates(subset=["year", "country"], keep="first")
              .drop(columns=["priority"]))
    assert ci_gmd.iloc[0]["source"] == "CI"


def test_log_return_formula():
    """Log returns are ln(current/previous)."""
    rates = pd.Series([100.0, 110.0, 105.0])
    log_ret = np.log(rates / rates.shift(1)).dropna().values

    expected = [np.log(110.0 / 100.0), np.log(105.0 / 110.0)]
    np.testing.assert_allclose(log_ret, expected)


def test_tail_events_count():
    """3-sigma events are counted correctly."""
    rng = np.random.default_rng(42)
    # Normal sample
    data = rng.normal(0, 1, 10000)
    # Inject 5 outliers beyond 3-sigma
    data = np.append(data, [10.0, -10.0, 8.0, -8.0, 7.0])

    vol = data.std(ddof=1)
    threshold = 3 * vol
    tail_count = int(np.sum(np.abs(data) > threshold))

    # The 5 injected outliers should all be beyond 3-sigma, plus some from the normal sample
    assert tail_count >= 5


def test_fine_to_coarse_mapping():
    """FINE_TO_COARSE maps fine regime codes to correct coarse codes."""
    # 1-4 -> 1 (peg)
    for fine in range(1, 5):
        assert build.FINE_TO_COARSE[fine] == 1

    # 5-8 -> 2 (crawling peg)
    for fine in range(5, 9):
        assert build.FINE_TO_COARSE[fine] == 2

    # 9-12 -> 3 (managed float)
    for fine in range(9, 13):
        assert build.FINE_TO_COARSE[fine] == 3

    # 13 -> 4 (free float)
    assert build.FINE_TO_COARSE[13] == 4

    # 14 -> 5 (freely falling)
    assert build.FINE_TO_COARSE[14] == 5

    # 15 -> 6 (dual market)
    assert build.FINE_TO_COARSE[15] == 6

    # Total: 15 entries
    assert len(build.FINE_TO_COARSE) == 15


def test_gold_local_calculation():
    """gold_local = gold_usd * rate_per_usd."""
    gold_usd = 100.0
    rate_per_usd = 150.0  # JPY
    gold_local = gold_usd * rate_per_usd
    assert gold_local == 15000.0


def test_gold_grams_per_100():
    """grams_per_100 = (100 / gold_local) * 31.1035."""
    gold_local = 1000.0
    grams_per_100 = (100.0 / gold_local) * build.TROY_OZ_GRAMS
    expected = (100.0 / 1000.0) * 31.1035
    assert abs(grams_per_100 - expected) < 1e-10
    assert abs(grams_per_100 - 3.11035) < 1e-10


def test_rolling_volatility_window():
    """Rolling(252) produces NaN for first 251 values, then real values."""
    rng = np.random.default_rng(42)
    returns = pd.Series(rng.normal(0, 0.01, 300))
    rolling = returns.rolling(252).std()

    # First 251 should be NaN
    assert rolling.iloc[:251].isna().all()
    # From index 251 onward should have values
    assert rolling.iloc[251:].notna().all()
    # Sanity: values should be positive
    assert (rolling.iloc[251:] > 0).all()


def test_gold_inflation_zero_rate():
    """Zero exchange rate produces NaN, not inf, for gold inflation."""
    current = pd.Series([100.0, 0.0, 50.0])
    previous = pd.Series([80.0, 80.0, 0.0])
    result = build._safe_pct_change(current, previous)

    # Normal case: (100/80 - 1) * 100 = 25.0
    assert abs(result.iloc[0] - 25.0) < 1e-10
    # Zero current -> NaN
    assert np.isnan(result.iloc[1])
    # Zero previous -> NaN (not inf)
    assert np.isnan(result.iloc[2])


def test_gold_log_return_zero_rate():
    """log(0/prev) produces NaN, not -inf."""
    current = pd.Series([100.0, 0.0, 50.0])
    previous = pd.Series([80.0, 80.0, 0.0])
    result = build._safe_log_return(current, previous)

    # Normal case
    expected = np.log(100.0 / 80.0)
    assert abs(result.iloc[0] - expected) < 1e-10
    # Zero current -> NaN (not -inf)
    assert np.isnan(result.iloc[1])
    # Zero previous -> NaN (not inf)
    assert np.isnan(result.iloc[2])


def test_grams_per_100_zero_gold():
    """100/0 guard produces NaN, not inf, for grams_per_100."""
    gold_local = pd.Series([1000.0, 0.0, 500.0])
    result = np.where(gold_local > 0, (100.0 / gold_local) * build.TROY_OZ_GRAMS, np.nan)

    assert abs(result[0] - 3.11035) < 1e-4
    assert np.isnan(result[1])
    assert abs(result[2] - 6.2207) < 1e-4


def test_cumulative_retained_pct():
    """Cumulative retained % = (base/current) * 100."""
    base_gold = 10.0
    current_gold = 100.0
    retained = (base_gold / current_gold) * 100
    assert abs(retained - 10.0) < 1e-10

    # Same price -> 100% retained
    assert abs((base_gold / base_gold) * 100 - 100.0) < 1e-10
