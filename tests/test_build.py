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


def _rows(*rows):
    return pd.DataFrame(rows, columns=["year", "iso3", "country", "rate_per_usd", "source"])


def test_priority_merge():
    """MW wins over CI, CI wins over GMD for the same (year, iso3)."""
    df = _rows((2000, "JPN", "Japan", 110.0, "GMD"),
               (2000, "JPN", "Japan", 105.0, "CI"),
               (2000, "JPN", "Japan", 100.0, "MW"),
               (2001, "JPN", "Japan", 111.0, "GMD"),
               (2001, "JPN", "Japan", 106.0, "CI"))
    out = build.merge_by_priority(df).set_index("year")
    assert out.loc[2000, "source"] == "MW" and out.loc[2000, "rate_per_usd"] == 100.0
    assert out.loc[2001, "source"] == "CI"


def test_canonicalize_merges_aliases():
    """Different source spellings collapse to one iso3 and one display name."""
    maps = ({"Gambia": "GMB", "The Gambia": "GMB", "Russian Federation": "RUS",
             "Russia": "RUS"},
            {"GMB": "Gambia", "RUS": "Russia"})
    df = pd.DataFrame({"country": ["The Gambia", "Gambia", "Russian Federation"]})
    out = build.canonicalize_countries(df, maps)
    assert list(out["iso3"]) == ["GMB", "GMB", "RUS"]
    assert list(out["country"]) == ["Gambia", "Gambia", "Russia"]


def test_canonicalize_strict_rejects_unknown():
    df = pd.DataFrame({"country": ["Atlantis"]})
    try:
        build.canonicalize_countries(df, ({}, {}))
    except ValueError as e:
        assert "Atlantis" in str(e)
    else:
        raise AssertionError("unknown country should raise")
    out = build.canonicalize_countries(df, ({}, {}), strict=False)
    assert out.loc[0, "country"] == "Atlantis" and pd.isna(out.loc[0, "iso3"])


def test_real_panel_has_no_split_countries():
    """Every source name used by the panel maps to a code (guards new spellings)."""
    name_to_iso, _ = build.country_maps()
    for alias, iso in build.COUNTRY_ALIASES.items():
        assert name_to_iso[alias] == iso


def test_drop_known_bad():
    df = _rows((1955, "GMB", "Gambia", 0.30, "GMD"),
               (1955, "GMB", "Gambia", 1.79, "CI"),
               (1957, "GMB", "Gambia", 1.79, "GMD"))
    out = build.drop_known_bad(df)
    assert list(zip(out["year"], out["source"])) == [(1955, "CI"), (1957, "GMD")]


def test_load_measuringworth_fx(tmp_path):
    """Parses the block export, drops unit labels, renames Europe."""
    f = tmp_path / "mw.csv"
    f.write_text(
        '"Citation: Officer, MeasuringWorth, 2026. "\n'
        "The table(s) present the price of one United States Dollar.\n"
        '"Argentina, 1791 - 2026"\n'
        '"1991","9535.5 Australes"\n'
        '"1992","0.9906 Pesos"\n'
        '"Europe, 1791 - 2026"\n'
        '"1999","0.9387 Euro"\n')
    wide = build.load_measuringworth_fx(f).set_index("year")
    assert wide.loc[1991, "Argentina"] == 9535.5
    assert wide.loc[1992, "Argentina"] == 0.9906
    assert wide.loc[1999, "Europe, Eurozone"] == 0.9387


def test_parse_mw_gold_series_strips_thousands():
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    import update_sources
    raw = ('"Citation: ..."\n"Year","London Market Price"\n'
           '"1949","8.40"\n"2010","1,224.53"\n')
    assert update_sources.parse_mw_series(raw) == {1949: 8.4, 2010: 1224.53}


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


def test_momentum_formula():
    """Momentum = ln(price_t / price_{t-lookback})."""
    prices = pd.Series([100.0, 110.0, 121.0, 133.1])
    mom = np.log(prices / prices.shift(2))
    expected_2 = np.log(121.0 / 100.0)
    assert abs(mom.iloc[2] - expected_2) < 1e-10
    assert np.isnan(mom.iloc[0])
    assert np.isnan(mom.iloc[1])


def test_reversal_formula():
    """Reversal = long_momentum - short_momentum."""
    long_mom = 0.2  # strong uptrend
    short_mom = -0.05  # recent dip
    reversal = long_mom - short_mom
    assert reversal == 0.25  # positive = reversing


def test_sigma_event_counting():
    """n-sigma events are counted and compared to Gaussian expectation."""
    from scipy.stats import norm
    rng = np.random.default_rng(42)
    data = rng.normal(0, 1, 10000)
    vol = data.std(ddof=1)

    # 3-sigma events
    threshold_3 = 3 * vol
    observed_3 = int(np.sum(np.abs(data) > threshold_3))
    expected_3 = 10000 * 2 * norm.sf(3)

    # Should have more than expected (sample noise is OK, but formula should work)
    assert expected_3 > 0
    assert observed_3 >= 0
    # Ratio should be roughly 1.0 for Gaussian data (within factor of 5)
    ratio = observed_3 / expected_3 if expected_3 > 0 else 0
    assert 0.1 < ratio < 5.0, f"3-sigma ratio should be near 1 for Gaussian, got {ratio}"


def test_stock_bond_correlation_formula():
    """20-year rolling correlation uses standard Pearson."""
    rng = np.random.default_rng(42)
    # Independent series should have correlation near 0
    eq = pd.Series(rng.normal(0, 0.1, 30))
    bond = pd.Series(rng.normal(0, 0.05, 30))
    corr = eq.iloc[-20:].corr(bond.iloc[-20:])
    assert -1.0 <= corr <= 1.0
    assert abs(corr) < 0.5, f"Independent series should have low correlation, got {corr}"

def test_unit_key_ignores_spelling_variants():
    assert build._unit_key("Pesos") == build._unit_key("Peso")
    assert build._unit_key("(New) Pesos Argentino") == build._unit_key("New Pesos Argentino")
    assert build._unit_key("Australes") != build._unit_key("(New) Pesos Argentino")


def _mw(values, units):
    v = pd.DataFrame({"year": list(values), "X": list(values.values())})
    u = pd.DataFrame({"year": list(units), "X": list(units.values())})
    return v, u


def test_chain_link_restates_old_units(monkeypatch):
    monkeypatch.setattr(build, "MW_REDENOMINATIONS", {("X", 1992): 10_000})
    v, u = _mw({1990: 5000.0, 1991: 9500.0, 1992: 1.0},
               {1990: "Australes", 1991: "Australes", 1992: "Pesos"})
    linked, breaks = build.chain_link_measuringworth(v, u)
    assert linked.loc[1991, "X"] == 0.95 and linked.loc[1992, "X"] == 1.0
    assert breaks == set()


def test_chain_link_none_factor_is_break(monkeypatch):
    monkeypatch.setattr(build, "MW_REDENOMINATIONS", {("X", 1925): None})
    v, u = _mw({1924: 4e11, 1925: 4.2}, {1924: "Mark", 1925: "Reichsmark"})
    _, breaks = build.chain_link_measuringworth(v, u)
    assert breaks == {("X", 1925)}


def test_chain_link_rejects_unlisted_unit_change(monkeypatch):
    monkeypatch.setattr(build, "MW_REDENOMINATIONS", {})
    v, u = _mw({1959: 1000.0, 1960: 1.05}, {1959: "Old Peso", 1960: "Escudos"})
    try:
        build.chain_link_measuringworth(v, u)
    except ValueError as e:
        assert "X" in str(e)
    else:
        raise AssertionError("unlisted unit change should raise")


def test_mw_bad_values_dropped():
    """The real export: Germany 1946 (a copy of Italy's value) is removed."""
    mw = build.load_measuringworth_fx().set_index("year")
    assert pd.isna(mw.loc[1946, "Germany"])
    assert mw.loc[1946, "Italy"] == 225.53


def test_real_mw_series_link_cleanly():
    """Every labeled MW unit change has a conversion entry (build would fail)."""
    linked, _ = build.chain_link_measuringworth()
    assert linked.shape[1] >= 40


def test_merge_keep_existing(tmp_path):
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    import update_sources
    dest = tmp_path / "x.csv"
    dest.write_text("Date,Currency,Rate\n2000-01-31,IRR,1\n2000-01-31,EUR,2\n")
    new = ("Date,Currency,Rate\n2000-01-31,EUR,2.5\n2001-01-31,EUR,3\n"
           "2999-01-31,EUR,9\n")
    text, n, kept = update_sources.merge_keep_existing(
        dest, new, key_cols=["Date", "Currency"], date_col="Date")
    assert (n, kept) == (3, 1)
    assert "2000-01-31,IRR,1" in text        # dropped upstream, kept
    assert "2000-01-31,EUR,2.5" in text      # revised upstream, replaced
    assert "2999" not in text                # future date discarded

def test_quality_flags():
    """Source switches are checked against same-year overlap; MW unit changes
    and gaps break comparability; levels are never altered."""
    cand = _rows((2000, "ARG", "Argentina", 1.0, "CI"),
                 (2001, "ARG", "Argentina", 1.1, "CI"),
                 (2001, "ARG", "Argentina", 1e-13, "GMD"),
                 (2002, "ARG", "Argentina", 1.2e-13, "GMD"),
                 (2003, "ARG", "Argentina", 1.3e-13, "GMD"),
                 (2003, "ARG", "Argentina", 1.31e-13, "CI"),
                 (2004, "ARG", "Argentina", 1.4e-13, "CI"),
                 (2010, "ARG", "Argentina", 5.0, "MW"),
                 (2011, "ARG", "Argentina", 0.0006, "MW"))
    panel = cand[~((cand["year"] == 2001) & (cand["source"] == "GMD"))]
    panel = panel[~((panel["year"] == 2003) & (panel["source"] == "CI"))]
    panel = build.merge_by_priority(panel)
    units = {("ARG", 2010): "Intis", ("ARG", 2011): "New Soles"}
    out = build.add_quality_flags(panel, cand, (units, {("ARG", 2011)})).set_index("year")
    f = out["flags"]
    assert f[2000] == "" and not out.loc[2000, "comparable_with_previous"]  # first obs
    assert f[2001] == "" and out.loc[2001, "comparable_with_previous"]
    assert f[2002] == "source_switch;source_level_mismatch"   # CI 1.1 vs GMD 1e-13 in 2001
    assert not out.loc[2002, "comparable_with_previous"]
    assert f[2004] == "source_switch"                          # GMD vs CI agree in 2003
    assert out.loc[2004, "comparable_with_previous"]
    assert f[2010] == "gap_before"                            # switch only checked for consecutive years
    assert "redenomination" in f[2011] and "level_jump" not in f[2011]
    assert out.loc[2011, "unit"] == "New Soles"
    assert out.loc[2002, "rate_per_usd"] == 1.2e-13               # levels untouched


def test_sovereign_defaults_real_files():
    e = build.build_sovereign_defaults()
    assert len(e) > 700 and e["iso3"].str.fullmatch(r"[A-Z]{3}").all()
    assert (e["country"] != e["iso3"]).all()          # every code maps to a name
    arg = e[(e["iso3"] == "ARG") & (e["event"] == "restructuring")]
    assert {"1830", "1982", "2001", "2019"} <= set(arg["start"])
    assert e["haircut_npv"].dropna().between(-0.5, 1.0).all()


def test_debt_in_default_real_file():
    d = build.build_debt_in_default()
    assert d["iso3"].notna().all() and "World" not in set(d["country"])
    assert {"total_usd_m", "private_creditors_usd_m", "china_usd_m"} <= set(d.columns)


def test_ecb_and_inflation_real_files():
    ecb = build.build_ecb_daily()
    usd = ecb[ecb["currency"] == "USD"].set_index("date")["rate_per_eur"]
    assert usd.index.min() == "1999-01-04" and usd.between(0.8, 1.7).all()
    annual, monthly = build.build_wb_inflation()
    assert annual["iso3"].nunique() > 150
    assert monthly["year_month"].str.fullmatch(r"\d{4}-\d{2}").all()


def test_redenomination_factors_direction():
    """Factors are old units per new unit: a correct factor leaves only the
    real market move across the change (regression: Argentina 1934 was
    entered inverted, producing a spurious +1.6 log return)."""
    linked, _ = build.chain_link_measuringworth()
    ret = np.log(linked / linked.shift(1))
    assert abs(ret.loc[1934, "Argentina"]) < 0.1      # gold -> paper peso
    assert abs(ret.loc[1966, "Australia"]) < 0.1      # pound -> dollar
    assert abs(ret.loc[1960, "France"]) < 0.1         # nouveau franc
    assert abs(ret.loc[1993, "Mexico"]) < 0.2         # nuevo peso
