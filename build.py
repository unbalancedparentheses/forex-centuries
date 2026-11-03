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


MW_FX_PATH = SOURCES / "measuringworth" / "measuringworth_exchange_rates.csv"

# MeasuringWorth block titles whose name differs from the historical column name.
MW_BLOCK_RENAMES = {"Europe": "Europe, Eurozone"}


# MeasuringWorth cells that are wrong in the export, dropped at parse time so
# Clio Infra / GMD fill those years in the panel: (country, first, last).
MW_BAD_VALUES = [
    # 1946-49 equal Italy's values exactly; 1941 equals Italy's 1941; 1945 is
    # 1.105 against an official RM rate of ~2.5. Export misalignment.
    ("Germany", 1941, 1941),
    ("Germany", 1945, 1949),
    # 1941 equals Germany's RM rate (2.50); 1942-44 ~1.1 against ~44-50 francs/USD.
    ("France", 1941, 1944),
    # 2.00 between 3,054 (2016) and 2,956 (2018): a typo.
    ("Colombia", 2017, 2017),
]


def _parse_measuringworth_fx(path):
    """Return ({country: {year: value}}, {country: {year: unit label}})."""
    import csv
    import re

    title = re.compile(r"^(.*), \d{4} - \d{4}$")
    values, units, current = {}, {}, None
    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.reader(fh):
            if len(row) == 1 and (m := title.match(row[0].strip())):
                current = MW_BLOCK_RENAMES.get(m.group(1), m.group(1))
                values.setdefault(current, {})
                units.setdefault(current, {})
            elif len(row) == 2 and current is not None and row[0].strip().isdigit():
                token, _, unit = row[1].strip().partition(" ")
                try:
                    values[current][int(row[0])] = float(token)
                except ValueError:
                    continue  # blank or non-numeric cell
                units[current][int(row[0])] = unit.strip()
    if not values:
        raise ValueError(f"No MeasuringWorth country blocks found in {path}")
    for country, first, last in MW_BAD_VALUES:
        for year in range(first, last + 1):
            values.get(country, {}).pop(year, None)
            units.get(country, {}).pop(year, None)
    return values, units


def _wide(series):
    wide = pd.DataFrame(series).sort_index()
    wide.index.name = "year"
    return wide.reset_index()


def load_measuringworth_fx(path=MW_FX_PATH):
    """Parse the MeasuringWorth exchange-rate export into a wide table.

    The export has a citation line, then one block per country: a title row
    like "Argentina, 1791 - 2026" followed by rows like "1916","0.9666 Gold Pesos".
    Returns a DataFrame with a `year` column plus one column per country.
    Values are as published, in the currency unit of each year, so
    redenominations appear as level shifts; see load_measuringworth_units()
    and chain_link_measuringworth().
    """
    return _wide(_parse_measuringworth_fx(path)[0])


def load_measuringworth_units(path=MW_FX_PATH):
    """Same shape as load_measuringworth_fx(), holding the unit label per value."""
    return _wide(_parse_measuringworth_fx(path)[1])


# Currency changes in the MeasuringWorth series, keyed by (country, first year
# quoted in the new unit). Value = old units per one new unit, used to restate
# earlier years in the new unit. None = no single conversion factor (or the
# change falls in a gap), so the return across the change is left undefined.
# chain_link_measuringworth() fails if MW reports a unit change not listed here.
MW_REDENOMINATIONS = {
    ("Argentina", 1934): 0.44,        # 1 paper peso m/n = 0.44 gold peso (1899 Conversion Law)
    ("Argentina", 1970): 100,         # peso ley 18.188
    ("Argentina", 1983): 10_000,      # peso argentino
    ("Argentina", 1985): 1_000,       # austral
    ("Argentina", 1992): 10_000,      # peso convertible
    ("Argentina", 2007): 1,           # label change only
    ("Australia", 1966): 0.5,         # 1 pound = 2 dollars
    ("Austria", 1925): 10_000,        # schilling replaces krone
    ("Austria", 1953): None,          # series gap 1939-52 (Reichsmark era)
    ("Belgium", 1927): 5,             # belga = 5 francs
    ("Belgium", 1945): 0.2,           # back to francs; series gap 1941-44
    ("Brazil", 1948): 1,              # cruzeiro replaced mil-reis 1:1 (1942)
    ("Brazil", 1967): 1_000,          # cruzeiro novo
    ("Brazil", 1986): 1_000,          # cruzado
    ("Brazil", 1989): 1_000,          # cruzado novo
    ("Brazil", 1990): 1,              # cruzeiro replaced cruzado novo 1:1
    ("Brazil", 1994): 1_000,          # cruzeiro real
    ("Brazil", 1995): 2_750,          # real
    ("Chile", 1960): 1_000,           # escudo
    ("Chile", 1976): 1_000,           # peso
    ("Chile", 2015): 1,               # label change only
    ("China", 1933): None,            # tael -> silver yuan; ratio varied
    ("China", 1981): None,            # series gap 1942-80
    ("Finland", 1971): 100,           # new markka (1963); series gap 1942-70
    ("France", 1960): 100,            # nouveau franc
    # Reichsmark = 1e12 paper marks, but MW's 1924 value (4.33e11) is 10x off
    # the stabilized 4.2e12, so the 1925 return is left undefined.
    ("Germany", 1925): None,
    # Deutsche mark (1948 reform, 10:1 for most claims, not uniform). MW's
    # 1941-49 values are dropped (MW_BAD_VALUES), so the change shows at 1950.
    ("Germany", 1950): None,
    ("Greece", 1982): 1_000,          # 1953 drachma; series gap 1941-81
    ("Israel", 1980): 10,             # shekel
    ("Israel", 1986): 1_000,          # new shekel
    ("Malaysia", 1952): 1,            # Straits -> Malayan dollar 1:1
    ("Malaysia", 1967): 1,            # Malayan -> Malaysian dollar 1:1
    ("Malaysia", 1976): 1,            # renamed ringgit
    ("Mexico", 1993): 1_000,          # nuevo peso
    ("New Zealand", 1968): 0.5,       # 1 pound = 2 dollars
    ("Peru", 1985): 1_000,            # inti
    ("Peru", 1991): 1_000_000,        # nuevo sol
    ("South Africa", 1961): 0.5,      # 1 pound = 2 rand
    # Venezuela: MW keeps the label "Bolivar(s)" across all three redenominations.
    ("Venezuela", 2008): 1_000,       # bolivar fuerte
    ("Venezuela", 2019): 100_000,     # bolivar soberano (Aug 2018; MW's 2018 avg is in fuertes)
    ("Venezuela", 2022): 1_000_000,   # bolivar digital (Oct 2021)
}


def _unit_key(label):
    """Normalize a unit label so spelling variants (Peso/Pesos) compare equal."""
    words = label.lower().replace("(", " ").replace(")", " ").split()
    return " ".join(w[:-1] if w.endswith("s") else w for w in words)


def mw_unit_changes(units):
    """Yield (country, year) where the unit differs from the previous quote."""
    units = units.set_index("year")
    for country in units.columns:
        s = units[country].dropna()
        keys = s.map(_unit_key)
        for year in s.index[1:][keys.values[1:] != keys.values[:-1]]:
            yield country, int(year)


def chain_link_measuringworth(values=None, units=None):
    """Restate each MW series in its latest currency unit.

    Returns (linked, breaks): `linked` is the wide year x country table on a
    continuous scale; `breaks` is a set of (country, year) whose return from
    the previous year is undefined (no conversion factor).
    """
    values = (values if values is not None else load_measuringworth_fx()).set_index("year")
    units = units if units is not None else load_measuringworth_units()
    changes = sorted(mw_unit_changes(units))
    missing = [c for c in changes if c not in MW_REDENOMINATIONS]
    if missing:
        raise ValueError(f"MeasuringWorth unit changes without a conversion entry "
                         f"(add to MW_REDENOMINATIONS): {missing}")
    linked = values.astype(float).copy()
    breaks = set()
    # Labeled changes must be listed; listed entries also cover unlabeled ones.
    for country, year in sorted(set(changes) | set(MW_REDENOMINATIONS)):
        if country not in linked.columns:
            continue
        factor = MW_REDENOMINATIONS[(country, year)]
        if factor is None:
            breaks.add((country, year))
        else:
            linked.loc[linked.index < year, country] /= factor
    return linked, breaks


# 12 significant digits: far beyond the precision of any source series, and
# it removes last-bit differences between platforms' math libraries (macOS
# arm64 vs Linux x86_64), so local and CI builds write identical files.
CSV_FLOAT_FORMAT = "%.12g"


def _write_csv(df, path, **kwargs):
    """Write a CSV with platform-independent float formatting."""
    df.to_csv(path, float_format=CSV_FLOAT_FORMAT, **kwargs)


def _round_and_write(df, path, precision_4=(), precision_6=()):
    """Round specified columns and write CSV."""
    for c in precision_4:
        df[c] = df[c].round(4)
    for c in precision_6:
        df[c] = df[c].round(6)
    df.pipe(_write_csv, path, index=False)


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

    long.pipe(_write_csv, NORM / "fred_daily_normalized.csv", index=False)
    print(f"    fred_daily_normalized.csv: {len(long):,} rows, "
          f"{long['currency'].nunique()} currencies")

    wide = long.pivot(index="date", columns="currency", values="rate_per_usd")
    wide.pipe(_write_csv, NORM / "fred_daily_normalized_wide.csv")
    print(f"    fred_daily_normalized_wide.csv: {wide.shape[0]:,} dates x "
          f"{wide.shape[1]} currencies")

    return long


# Source country names that differ from GMD's, mapped to ISO 3166-1 alpha-3
# (or ISO 3166-3 for dissolved states). GMD supplies codes for everything else.
COUNTRY_ALIASES = {
    "Congo": "COG",              # Clio Infra: Republic of the Congo (Brazzaville)
    "Congo, DRC": "COD",         # Clio Infra
    "Cote d'Ivoire": "CIV",      # Clio Infra
    "Russia": "RUS",             # Clio Infra
    "Solomon Is.": "SLB",        # Clio Infra
    "Swaziland": "SWZ",          # Clio Infra
    "The Gambia": "GMB",         # Clio Infra
    "Korea": "KOR",              # MeasuringWorth: South Korea
    "Europe, Eurozone": "EMU",   # MeasuringWorth: euro area (World Bank code)
    # Bank of Canada / Bank of England sovereign default database
    "Bosnia & Herzegovina": "BIH",
    "Cabo Verde": "CPV",
    "C\u00f4te d\u2019Ivoire": "CIV",
    "Dem. Rep. of Congo (Kinshasa)": "COD",
    "eSwatini (Swaziland)": "SWZ",
    "Korea, Democratic People's Republic of (North)": "PRK",
    "Kyrgyz Republic": "KGZ",
    "North Macedonia": "MKD",
    "Rep. Of Congo (Brazzaville)": "COG",
    "S\u00e3o Tom\u00e9 and Pr\u00edncipe": "STP",
    "Slovak Republic": "SVK",
    "St. Kitts & Nevis": "KNA",
    "St. Lucia": "LCA",
    "St. Vincent and the Grenadines": "VCT",
    "Trinidad & Tobago": "TTO",
    "USSR/Russian Federation": "RUS",
    "West Bank & Gaza": "PSE",
}

# Display names where GMD's name is non-standard or missing.
CANONICAL_NAMES = {
    "COD": "Democratic Republic of the Congo",
    "CIV": "Cote d'Ivoire",
    "RUS": "Russia",
    "EMU": "Euro Area",
}

# Source rows known to be wrong, dropped before merging: (source, iso3, first, last).
KNOWN_BAD_ROWS = [
    # GMD has ~0.30/USD for Gambia 1950-56; the West African pound peg implies
    # 1.7857 (dalasi units), which is what Clio Infra and GMD itself show from 1957.
    ("GMD", "GMB", 1950, 1956),
]


def country_maps():
    """Return (name -> iso3, iso3 -> canonical name) built from GMD plus aliases."""
    gmd = pd.read_csv(SOURCES / "gmd" / "gmd_exchange_rates.csv",
                      usecols=["ISO3", "countryname"]).dropna().drop_duplicates()
    name_to_iso = dict(zip(gmd["countryname"], gmd["ISO3"]))
    iso_to_name = dict(zip(gmd["ISO3"], gmd["countryname"]))
    name_to_iso.update(COUNTRY_ALIASES)
    iso_to_name.update(CANONICAL_NAMES)
    return name_to_iso, iso_to_name


def canonicalize_countries(df, maps=None, strict=True):
    """Add `iso3` and replace `country` with its canonical name.

    strict=True raises on unknown names so a new source spelling can't silently
    create a duplicate country; strict=False leaves unknown names untouched.
    """
    name_to_iso, iso_to_name = maps or country_maps()
    iso = df["country"].map(name_to_iso)
    unknown = sorted(df.loc[iso.isna(), "country"].unique())
    if unknown and strict:
        raise ValueError(f"Unmapped country names (add to COUNTRY_ALIASES): {unknown}")
    df = df.copy()
    df["iso3"] = iso
    df["country"] = iso.map(iso_to_name).fillna(df["country"])
    return df


def drop_known_bad(df):
    """Remove rows listed in KNOWN_BAD_ROWS."""
    bad = pd.Series(False, index=df.index)
    for source, iso3, first, last in KNOWN_BAD_ROWS:
        bad |= ((df["source"] == source) & (df["iso3"] == iso3)
                & df["year"].between(first, last))
    return df[~bad]


SOURCE_PRIORITY = {"MW": 0, "CI": 1, "GMD": 2}


def merge_by_priority(df):
    """Keep one row per (year, iso3), preferring MW > CI > GMD."""
    return (df.assign(priority=df["source"].map(SOURCE_PRIORITY))
              .sort_values("priority", kind="stable")
              .drop_duplicates(subset=["year", "iso3"], keep="first")
              .drop(columns=["priority"])
              .sort_values(["year", "country"])
              .reset_index(drop=True))


SOURCE_MISMATCH_TOL = 0.10   # |log ratio| between sources at a switch (~10%)
LEVEL_JUMP = np.log(10)      # year-on-year move flagged as level_jump


def mw_unit_breaks():
    """Return {(iso3, year): unit label} for MW plus the set of (iso3, year)
    where the MW currency unit changed (labeled or listed)."""
    units = load_measuringworth_units()
    name_to_iso, _ = country_maps()
    changes = set(mw_unit_changes(units)) | set(MW_REDENOMINATIONS)
    # Label-only changes (factor 1) keep levels comparable.
    redenom = {(name_to_iso[c], y) for c, y in changes
               if c in name_to_iso and MW_REDENOMINATIONS.get((c, y)) != 1}
    long = units.melt(id_vars="year", var_name="country", value_name="unit").dropna()
    unit = {(name_to_iso[c], int(y)): u
            for c, y, u in long[["country", "year", "unit"]].itertuples(index=False)
            if c in name_to_iso}
    return unit, redenom


def add_quality_flags(panel, candidates, mw_info):
    """Add `unit`, `flags` and `comparable_with_previous` to the merged panel.

    Levels are kept exactly as each source publishes them. Flags say where
    a year cannot be compared with the previous one:
      gap_before             previous year missing
      redenomination         MW currency unit changed (levels not comparable)
      source_switch          value comes from a different source than the
                             previous (consecutive) year
      source_level_mismatch  at a switch, the two sources disagree by >10% in
                             the same year (different units or definitions)
      source_unverified      at a switch, no year where both sources overlap
      level_jump             |log change| > ln(10) with no explanation above
      constant_growth        3rd+ identical non-zero log change in a row
                             (typical of interpolated data)
    comparable_with_previous is False for gap_before, redenomination,
    source_level_mismatch and source_unverified.
    """
    unit_map, redenom = mw_info
    p = panel.sort_values(["iso3", "year"]).reset_index(drop=True)
    by_key = candidates.set_index(["iso3", "year", "source"])["rate_per_usd"]
    by_key = by_key[~by_key.index.duplicated()]

    g = p.groupby("iso3")
    prev_year, prev_src = g["year"].shift(), g["source"].shift()
    gap = prev_year.notna() & (p["year"] - prev_year != 1)
    first = prev_year.isna()
    dlog = np.log(p["rate_per_usd"] / g["rate_per_usd"].shift())
    dlog[gap | first] = np.nan

    switch = ~first & ~gap & (p["source"] != prev_src)
    mismatch = pd.Series(False, index=p.index)
    unverified = pd.Series(False, index=p.index)
    for i in p.index[switch]:
        iso, year, src, old = p.at[i, "iso3"], p.at[i, "year"], p.at[i, "source"], prev_src[i]
        # Same-year values from both sources, at the switch or the year before.
        ratio = None
        for y in (year, year - 1):
            a, b = by_key.get((iso, y, old)), by_key.get((iso, y, src))
            if a and b and a > 0 and b > 0:
                ratio = np.log(a / b)
                break
        if ratio is None:
            unverified[i] = True
        elif abs(ratio) > SOURCE_MISMATCH_TOL:
            mismatch[i] = True

    is_mw = p["source"] == "MW"
    keys = list(zip(p["iso3"], p["year"]))
    p["unit"] = [unit_map.get(k, "") if m else "" for k, m in zip(keys, is_mw)]
    redenomination = pd.Series([k in redenom for k in keys], index=p.index) & is_mw & ~first

    r = dlog.round(6)
    gr = r.groupby(p["iso3"])
    constant = (r != 0) & r.notna() & (r == gr.shift(1)) & (r == gr.shift(2))
    jump = (dlog.abs() > LEVEL_JUMP) & ~redenomination & ~mismatch & ~unverified

    flags = {"gap_before": gap, "redenomination": redenomination,
             "source_switch": switch, "source_level_mismatch": mismatch,
             "source_unverified": unverified, "level_jump": jump,
             "constant_growth": constant}
    p["flags"] = [";".join(n for n, f in flags.items() if f[i]) for i in p.index]
    p["comparable_with_previous"] = ~first & ~(gap | redenomination | mismatch | unverified)
    return p.sort_values(["year", "country"]).reset_index(drop=True)


def build_yearly_panel():
    """Build unified yearly panel from MeasuringWorth + Clio Infra + GMD."""
    print("  Loading MeasuringWorth...")
    mw = load_measuringworth_fx()
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
    # GMD carries IMF forecasts for the current and future years; keep only
    # completed years so projections never enter the panel.
    gmd = gmd[gmd["year"] < date.today().year]
    gmd = gmd[["year", "country", "rate_per_usd"]]
    gmd["source"] = "GMD"

    candidates = drop_known_bad(
        canonicalize_countries(pd.concat([mw, ci, gmd], ignore_index=True)))
    all_data = merge_by_priority(candidates)
    all_data = add_quality_flags(all_data, candidates, mw_unit_breaks())

    all_data[["year", "iso3", "country", "rate_per_usd", "source", "unit",
              "flags", "comparable_with_previous"]].pipe(_write_csv, 
        NORM / "yearly_unified_panel.csv", index=False)
    print(f"    Not comparable with previous year: "
          f"{(~all_data['comparable_with_previous']).sum():,} rows")
    print(f"    yearly_unified_panel.csv: {len(all_data):,} rows, "
          f"{all_data['country'].nunique()} countries")

    src_counts = all_data["source"].value_counts()
    print(f"    Sources: {' | '.join(f'{s}={n:,}' for s, n in src_counts.items())}")

    wide = all_data.pivot(index="year", columns="country", values="rate_per_usd")
    wide.pipe(_write_csv, NORM / "yearly_unified_wide.csv")
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
    daily_ret.pipe(_write_csv, ANALYSIS / "daily_log_returns.csv", index=False)
    print(f"    daily_log_returns.csv: {len(daily_ret):,} rows")

    # Yearly log returns use MeasuringWorth only (not the full unified panel):
    # MW labels the currency unit of every value, so each series can be
    # chain-linked across redenominations (MW_REDENOMINATIONS). Without this,
    # e.g. Germany 1925 (1e12 marks = 1 reichsmark) shows a -25 log return.
    # Returns across changes with no single conversion factor are left NaN.
    # "Europe, Eurozone" is excluded: only 26 years of data (1999-2025) and overlaps
    # with constituent countries (Germany, France, etc.) in the correlation analysis.
    print("  Computing yearly log returns...")
    mw, breaks = chain_link_measuringworth()
    if "Europe, Eurozone" in mw.columns:
        mw = mw.drop(columns=["Europe, Eurozone"])
    mw = mw.reindex(range(mw.index.min(), mw.index.max() + 1))
    mw.index.name = "year"
    yearly_ret = np.log(mw / mw.shift(1))
    for country, year in breaks:
        if country in yearly_ret.columns:
            yearly_ret.loc[year, country] = np.nan
    print(f"    MW currency changes: {len(MW_REDENOMINATIONS) - len(breaks)} "
          f"chain-linked, {len(breaks)} left as breaks")
    yearly_ret.pipe(_write_csv, ANALYSIS / "yearly_log_returns.csv")
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
    daily_df.pipe(_write_csv, ANALYSIS / "daily_volatility_stats.csv", index=False)
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
    yearly_df.pipe(_write_csv, ANALYSIS / "yearly_volatility_stats.csv", index=False)
    print(f"    yearly_volatility_stats.csv: {len(yearly_df)} countries")


def build_correlations(daily_ret, yearly_ret):
    """Compute pairwise correlation matrices of log returns."""
    print("  Computing daily correlation matrix...")
    daily_wide = daily_ret.pivot(index="date", columns="currency", values="log_return")
    daily_corr = daily_wide.corr()
    daily_corr.pipe(_write_csv, ANALYSIS / "daily_correlation_matrix.csv")
    print(f"    daily_correlation_matrix.csv: {daily_corr.shape[0]}x{daily_corr.shape[1]}")

    print("  Computing yearly correlation matrix...")
    yearly_corr = yearly_ret.corr(min_periods=MIN_OVERLAP_YEARS)
    yearly_corr.pipe(_write_csv, ANALYSIS / "yearly_correlation_matrix.csv")
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

    long.pipe(_write_csv, ANALYSIS / "daily_rolling_volatility.csv", index=False)
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

    yearly_regime.pipe(_write_csv, ANALYSIS / "yearly_regime_classification.csv", index=False)
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
    stats_df.pipe(_write_csv, ANALYSIS / "regime_conditional_stats.csv", index=False)
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
    ci_gbp_long = canonicalize_countries(ci_gbp_long, strict=False)

    cpi = pd.read_csv(SOURCES / "clio_infra" / "clio_infra_inflation.csv")
    cpi_long = cpi.melt(id_vars=["year"], var_name="country", value_name="cpi_inflation_pct")
    cpi_long = cpi_long.dropna(subset=["cpi_inflation_pct"])
    cpi_long["year"] = cpi_long["year"].astype(int)
    cpi_long = canonicalize_countries(cpi_long, strict=False).drop(columns="iso3")

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


def build_momentum_analysis(daily_long):
    """Compute momentum signals for FRED daily currencies.

    3, 6, and 12-month trailing log returns, plus momentum reversal detection
    (strong positive momentum followed by sharp drop).

    Reference: Jegadeesh, N. & Titman, S. (1993). "Returns to Buying Winners
    and Selling Losers." Journal of Finance, 48(1), 65-91.
    """
    print("  Computing momentum signals...")
    wide = daily_long.pivot(index="date", columns="currency", values="rate_per_usd")
    wide.index = pd.to_datetime(wide.index)
    wide = wide.sort_index()

    lookbacks = {"3m": 63, "6m": 126, "12m": 252}
    records = []

    for currency in wide.columns:
        prices = wide[currency].dropna()
        if len(prices) < 252:
            continue
        for label, lb in lookbacks.items():
            mom = np.log(prices / prices.shift(lb))
            for date_val, m_val in mom.dropna().items():
                records.append({
                    "date": date_val.strftime("%Y-%m-%d"),
                    "currency": currency,
                    "lookback": label,
                    "momentum": round(m_val, 6),
                })

    mom_df = pd.DataFrame(records)
    mom_df = mom_df.sort_values(["date", "currency", "lookback"]).reset_index(drop=True)
    mom_df.pipe(_write_csv, ANALYSIS / "daily_momentum_signals.csv", index=False)
    print(f"    daily_momentum_signals.csv: {len(mom_df):,} rows, "
          f"{mom_df['currency'].nunique()} currencies")

    # Momentum reversal: 12m momentum minus 1m momentum
    # High positive = long-term up but short-term turning down
    print("  Computing momentum reversals...")
    reversal_records = []
    for currency in wide.columns:
        prices = wide[currency].dropna()
        if len(prices) < 252:
            continue
        mom_12m = np.log(prices / prices.shift(252))
        mom_1m = np.log(prices / prices.shift(21))
        reversal = mom_12m - mom_1m
        for date_val, rev_val in reversal.dropna().items():
            reversal_records.append({
                "date": date_val.strftime("%Y-%m-%d"),
                "currency": currency,
                "reversal": round(rev_val, 6),
                "mom_12m": round(mom_12m.loc[date_val], 6),
                "mom_1m": round(mom_1m.loc[date_val], 6),
            })

    rev_df = pd.DataFrame(reversal_records)
    rev_df = rev_df.sort_values(["date", "currency"]).reset_index(drop=True)
    rev_df.pipe(_write_csv, ANALYSIS / "daily_momentum_reversals.csv", index=False)
    print(f"    daily_momentum_reversals.csv: {len(rev_df):,} rows")


def build_sigma_events(daily_ret):
    """Count n-sigma events per currency vs Gaussian expected frequency.

    Inspired by Monday Morning Macro (2019): "The Impossible has Happened.
    Again." — documenting 10 four-sigma events in one month in Treasuries.
    """
    print("  Computing sigma event frequencies...")
    sigma_levels = [2, 3, 4, 5]
    records = []

    for currency, group in daily_ret.groupby("currency"):
        r = group["log_return"].values
        n = len(r)
        vol = r.std(ddof=1)
        if vol < 1e-10:
            continue

        for sigma in sigma_levels:
            threshold = sigma * vol
            observed = int(np.sum(np.abs(r) > threshold))
            expected = n * 2 * norm.sf(sigma)
            ratio = observed / expected if expected > 0 else 0.0

            records.append({
                "currency": currency,
                "n_days": n,
                "sigma_level": sigma,
                "threshold": round(threshold, 6),
                "observed": observed,
                "expected_gaussian": round(expected, 2),
                "ratio_vs_gaussian": round(ratio, 2),
            })

    sigma_df = pd.DataFrame(records)
    sigma_df = sigma_df.sort_values(
        ["sigma_level", "ratio_vs_gaussian"], ascending=[True, False]
    ).reset_index(drop=True)
    sigma_df.pipe(_write_csv, ANALYSIS / "sigma_event_frequency.csv", index=False)
    print(f"    sigma_event_frequency.csv: {len(sigma_df)} rows "
          f"({len(sigma_levels)} sigma levels x {sigma_df['currency'].nunique()} currencies)")

    # Summary: average ratio by sigma level
    summary = sigma_df.groupby("sigma_level").agg(
        mean_ratio=("ratio_vs_gaussian", "mean"),
        median_ratio=("ratio_vs_gaussian", "median"),
        max_ratio=("ratio_vs_gaussian", "max"),
        max_currency=("ratio_vs_gaussian", lambda x: sigma_df.loc[x.idxmax(), "currency"]),
    )
    print("    Sigma event ratios vs Gaussian:")
    for level, row in summary.iterrows():
        print(f"      {level}σ: mean={row['mean_ratio']:.1f}x, "
              f"median={row['median_ratio']:.1f}x, "
              f"max={row['max_ratio']:.1f}x ({row['max_currency']})")


def build_jst_returns():
    """Extract real asset class returns from JST Macrohistory database.

    Computes statistics on equities, housing, bonds, and bills from Jordà,
    Schularick & Taylor (2019) — 18 countries, 1870-2017.

    Reference: Jordà, Ò., Knoll, K., Kuvshinov, D., Schularick, M. &
    Taylor, A.M. (2019). "The Rate of Return on Everything, 1870-2015."
    Quarterly Journal of Economics, 134(3), 1225-1298.
    """
    jst_path = SOURCES / "jst" / "jst_macrohistory.xlsx"
    if not jst_path.exists():
        print("    Skipping: JST macrohistory not found")
        return

    print("  Loading JST macrohistory...")
    jst = pd.read_excel(jst_path, sheet_name="Sheet1")

    # Key return columns (nominal total returns)
    return_cols = {
        "eq_tr": "equity",
        "housing_tr": "housing",
        "bond_tr": "bonds",
        "bill_rate": "bills",
    }

    # Extract return data
    print("  Computing asset class return statistics...")
    records = []
    for col, asset in return_cols.items():
        for country, group in jst.groupby("country"):
            series = group[["year", col]].dropna()
            if len(series) < 10:
                continue
            returns = series[col].values
            years = series["year"].values

            # Real returns: deflate by same-year CPI inflation (exact Fisher).
            # Inflation is computed on the full CPI series before aligning, so
            # gaps in the return series don't produce multi-year changes.
            # bill_rate is a nominal annual rate, so it is deflated the same way.
            cpi = group.set_index("year")["cpi"].sort_index()
            inflation = cpi.pct_change().reindex(years).values
            real_returns = (1 + returns) / (1 + inflation) - 1
            returns_clean = returns
            years_clean = years

            # Drop NaN
            mask = np.isfinite(real_returns) & np.isfinite(returns_clean)
            real_returns = real_returns[mask]
            returns_clean = returns_clean[mask]
            years_clean = years_clean[mask]

            if len(real_returns) < 10:
                continue

            records.append({
                "country": country,
                "asset_class": asset,
                "n_years": len(real_returns),
                "start_year": int(years_clean.min()),
                "end_year": int(years_clean.max()),
                "mean_nominal_return": round(float(np.nanmean(returns_clean)), 4),
                "mean_real_return": round(float(np.nanmean(real_returns)), 4),
                "volatility": round(float(np.nanstd(returns_clean, ddof=1)), 4),
                "sharpe_ratio": round(
                    float(np.nanmean(real_returns) / np.nanstd(real_returns, ddof=1))
                    if np.nanstd(real_returns, ddof=1) > 0 else 0.0, 4),
                "excess_kurtosis": round(float(kurtosis(returns_clean, fisher=True, nan_policy="omit")), 4),
                "skewness": round(float(skew(returns_clean, nan_policy="omit")), 4),
                "max_return": round(float(np.nanmax(returns_clean)), 4),
                "min_return": round(float(np.nanmin(returns_clean)), 4),
            })

    returns_df = pd.DataFrame(records)
    returns_df = returns_df.sort_values(["asset_class", "country"]).reset_index(drop=True)
    returns_df.pipe(_write_csv, ANALYSIS / "jst_asset_returns.csv", index=False)
    print(f"    jst_asset_returns.csv: {len(returns_df)} rows "
          f"({returns_df['asset_class'].nunique()} asset classes, "
          f"{returns_df['country'].nunique()} countries)")

    # Global averages per asset class
    summary = returns_df.groupby("asset_class").agg(
        mean_real=("mean_real_return", "mean"),
        mean_vol=("volatility", "mean"),
        mean_sharpe=("sharpe_ratio", "mean"),
        mean_kurtosis=("excess_kurtosis", "mean"),
    ).round(4)
    print("    Global averages by asset class:")
    for asset, row in summary.iterrows():
        print(f"      {asset}: real={row['mean_real']:.1%}, vol={row['mean_vol']:.1%}, "
              f"sharpe={row['mean_sharpe']:.2f}, kurtosis={row['mean_kurtosis']:.1f}")


def _iso_name(iso3):
    """Canonical country name for ISO3 codes (falls back to the code)."""
    _, iso_to_name = country_maps()
    return iso3.map(iso_to_name).fillna(iso3)


# Non-ISO country codes used by the Trebesch files.
TREBESCH_CODE_FIXES = {
    "CRO": "HRV",  # Croatia (old WDI code)
    "ROM": "ROU",  # Romania (old WDI code)
    "SLO": "SVN",  # Slovenia
    "CZK": "CSK",  # Czechoslovakia (ISO 3166-3)
}


def build_sovereign_defaults():
    """Sovereign default / restructuring events from two Trebesch datasets.

    One row per event: iso3, country, event, start, end (dates or years),
    haircuts and restructured debt where available, and source.
    """
    print("  Loading Asonuma-Trebesch defaults and restructurings...")
    src = SOURCES / "trebesch"
    at = pd.read_excel(src / "asonuma_trebesch_defaults.xlsx",
                       sheet_name="DATASET Defaults & Restruct.", header=5)
    at.columns = [str(c).strip() for c in at.columns]
    at = at.dropna(subset=["WDI code"])
    kind = np.where(at["Post-default"] == 1, "restructuring_post_default",
                    np.where(at["Strictly preemptive"] == 1,
                             "restructuring_preemptive_strict",
                             "restructuring_preemptive_weak"))
    events_at = pd.DataFrame({
        "iso3": at["WDI code"].str.strip(),
        "event": kind,
        "start": pd.to_datetime(at["Start of default or restructuring process: "
                                   "default or announcement"]).dt.strftime("%Y-%m-%d"),
        "end": pd.to_datetime(at["End of restructuring: completion of exchange"],
                              errors="coerce").dt.strftime("%Y-%m-%d"),
        "source": "Asonuma-Trebesch (2026 update)",
    })

    print("  Loading Graf von Luckner et al. haircuts since 1815...")
    hc_path = src / "haircuts_since_1815.xlsx"
    # Header row 12; row 13 holds column numbers "(1)", "(2)", ... -> dropped.
    rs = pd.read_excel(hc_path, sheet_name="Individual Restructurings", header=12)
    rs.columns = [str(c).strip() for c in rs.columns]
    rs = rs[pd.to_numeric(rs["Year of Default"], errors="coerce").notna()]
    events_rs = pd.DataFrame({
        "iso3": rs["Country Code"].str.strip(),
        "event": "restructuring",
        "start": rs["Year of Default"].astype(int).astype(str),
        "end": rs["Year of Restructuring"].astype("Int64").astype(str),
        "haircut_npv": pd.to_numeric(rs["Net-Present-Value Haircut"], errors="coerce"),
        "haircut_face": pd.to_numeric(rs["Face Value Haircut"], errors="coerce"),
        "debt_restructured_usd_m": pd.to_numeric(
            rs["Debt Restructured (millions, current, USD)"], errors="coerce"),
        "spell_id": rs["Default Spell ID"],
        "source": "Graf von Luckner, Meyer, Reinhart & Trebesch (2024)",
    })
    sp = pd.read_excel(hc_path, sheet_name="Default Spells", header=12)
    sp.columns = [str(c).strip() for c in sp.columns]
    sp = sp[pd.to_numeric(sp["Year of Default Spell Begin"], errors="coerce").notna()]
    events_sp = pd.DataFrame({
        "iso3": sp["Country Code"].str.strip(),
        "event": "default_spell",
        "start": sp["Year of Default Spell Begin"].astype(int).astype(str),
        "end": sp["Year of Default Spell End"].astype("Int64").astype(str),
        "haircut_npv": pd.to_numeric(sp["Net-Present-Value Bulow-Rogoff Haircut"],
                                     errors="coerce"),
        "haircut_face": pd.to_numeric(sp["Face Value Bulow-Rogoff Haircut"],
                                      errors="coerce"),
        "spell_id": sp["Spell ID"],
        "source": "Graf von Luckner, Meyer, Reinhart & Trebesch (2024)",
    })

    events = pd.concat([events_at, events_rs, events_sp], ignore_index=True)
    events["iso3"] = events["iso3"].replace(TREBESCH_CODE_FIXES)
    events["end"] = events["end"].replace({"<NA>": "", "NaT": ""}).fillna("")
    events.insert(1, "country", _iso_name(events["iso3"]))
    events = events.sort_values(["iso3", "start", "event"]).reset_index(drop=True)
    events.pipe(_write_csv, ANALYSIS / "sovereign_default_events.csv", index=False)
    print(f"    sovereign_default_events.csv: {len(events):,} events, "
          f"{events['iso3'].nunique()} countries, "
          f"{events['start'].str[:4].min()}-{events['start'].str[:4].max()}")
    return events


BOC_BOE_FIELDS = ["TOTAL", "IMF", "IBRD", "IDA", "IADB", "PARIS_CLUB", "CHINA",
                  "OTHER_OFFICIAL_CREDITORS", "PRIVATE_CREDITORS", "FC_BANK_LOANS",
                  "FC_BONDS", "LC_DEBT", "FISCAL_ARREARS"]


def build_debt_in_default():
    """Sovereign debt in default by country-year and creditor (BoC-BoE), US$ m."""
    import io
    import re

    print("  Loading BoC-BoE sovereign default database...")
    text = (SOURCES / "bocboe" / "bocboe_sovereign_defaults.csv").read_text(encoding="utf-8-sig")
    body = text[text.index('"OBSERVATIONS"'):].split("\n", 1)[1]
    raw = pd.read_csv(io.StringIO(body))
    raw = raw[raw["DEBT_COUNTRY"] != "World"]
    # Columns are DEBT_<FIELD>_<edition year>; strip the edition suffix.
    rename = {}
    for col in raw.columns:
        m = re.fullmatch(r"DEBT_(.+)_\d{4}", col)
        if m and m.group(1) in BOC_BOE_FIELDS:
            rename[col] = m.group(1).lower() + "_usd_m"
    out = raw.rename(columns={**rename, "DEBT_COUNTRY": "country",
                              "DEBT_COUNTRY_GROUP": "country_group",
                              "DEBT_YEAR": "year"})
    out = canonicalize_countries(out[["country", "country_group", "year",
                                      *rename.values()]])
    out = out[["year", "iso3", "country", "country_group", *rename.values()]]
    out = out.sort_values(["year", "iso3"]).reset_index(drop=True)
    out.pipe(_write_csv, ANALYSIS / "sovereign_debt_in_default.csv", index=False)
    print(f"    sovereign_debt_in_default.csv: {len(out):,} rows, "
          f"{out['iso3'].nunique()} countries, {out['year'].min()}-{out['year'].max()}")
    return out


def build_ecb_daily():
    """ECB euro reference rates, long format: date, currency, rate_per_eur."""
    print("  Loading ECB euro reference rates...")
    wide = pd.read_csv(SOURCES / "ecb" / "eurofxref-hist.zip", na_values=["N/A"])
    wide = wide.loc[:, ~wide.columns.str.startswith("Unnamed")]
    long = (wide.melt(id_vars="Date", var_name="currency", value_name="rate_per_eur")
                .dropna(subset=["rate_per_eur"])
                .rename(columns={"Date": "date"})
                .sort_values(["date", "currency"])
                .reset_index(drop=True))
    long.pipe(_write_csv, NORM / "ecb_daily.csv", index=False)
    print(f"    ecb_daily.csv: {len(long):,} rows, {long['currency'].nunique()} currencies, "
          f"{long['date'].min()} to {long['date'].max()}")
    return long


def build_wb_inflation():
    """World Bank Global Database of Inflation: headline CPI, annual + monthly."""
    path = SOURCES / "wb_inflation" / "wb_inflation.xlsx"
    print("  Loading World Bank inflation database...")
    id_cols = ["Country Code", "IMF Country Code", "Country", "Indicator Type", "Series Name"]

    def long(sheet, value_name):
        df = pd.read_excel(path, sheet_name=sheet)
        df = df.dropna(subset=["Country Code"])
        df = df.drop(columns=[c for c in df.columns
                              if str(c).startswith("Unnamed") or c in id_cols[1:]])
        out = df.melt(id_vars="Country Code", var_name="period", value_name=value_name)
        out = out.dropna(subset=[value_name]).rename(columns={"Country Code": "iso3"})
        out["period"] = pd.to_numeric(out["period"], errors="coerce")
        return out.dropna(subset=["period"])

    annual = long("hcpi_a", "inflation_pct")
    annual["year"] = annual.pop("period").astype(int)
    annual.insert(1, "country", _iso_name(annual["iso3"]))
    annual = annual[["year", "iso3", "country", "inflation_pct"]].sort_values(["year", "iso3"])
    annual.pipe(_write_csv, ANALYSIS / "cpi_inflation_yearly.csv", index=False)

    monthly = long("hcpi_m", "cpi_index")
    p = monthly.pop("period").astype(int)  # YYYYMM
    monthly["year_month"] = (p // 100).astype(str) + "-" + (p % 100).astype(str).str.zfill(2)
    monthly.insert(1, "country", _iso_name(monthly["iso3"]))
    monthly = monthly[["year_month", "iso3", "country", "cpi_index"]].sort_values(
        ["year_month", "iso3"])
    monthly.pipe(_write_csv, NORM / "cpi_monthly.csv", index=False)
    print(f"    cpi_inflation_yearly.csv: {len(annual):,} rows, {annual['iso3'].nunique()} countries; "
          f"cpi_monthly.csv: {len(monthly):,} rows")
    return annual, monthly


def build_stock_bond_correlation():
    """Compute rolling stock-bond return correlation from JST data.

    Stock-bond negative correlation is historically RARE — only the last
    ~25 years. When it flips positive, diversification breaks.

    Reference: Artemis Capital Management (2020). "Volatility and the
    Allegory of the Prisoner's Dilemma: False Peace, the Alchemy of Risk,
    and Volgamageddon" ("Dennis Rodman" paper).
    """
    jst_path = SOURCES / "jst" / "jst_macrohistory.xlsx"
    if not jst_path.exists():
        print("    Skipping: JST macrohistory not found")
        return

    print("  Loading JST for stock-bond correlation...")
    jst = pd.read_excel(jst_path, sheet_name="Sheet1")

    # Need eq_tr and bond_tr
    records = []
    for country, group in jst.groupby("country"):
        data = group[["year", "eq_tr", "bond_tr"]].dropna()
        if len(data) < 20:
            continue
        data = data.sort_values("year")

        # 20-year rolling correlation
        window = 20
        for i in range(window, len(data) + 1):
            window_data = data.iloc[i - window:i]
            corr = window_data["eq_tr"].corr(window_data["bond_tr"])
            records.append({
                "year": int(window_data["year"].iloc[-1]),
                "country": country,
                "correlation_20y": round(corr, 4) if np.isfinite(corr) else None,
            })

    corr_df = pd.DataFrame(records).dropna()
    corr_df = corr_df.sort_values(["year", "country"]).reset_index(drop=True)
    corr_df.pipe(_write_csv, ANALYSIS / "stock_bond_correlation.csv", index=False)
    print(f"    stock_bond_correlation.csv: {len(corr_df):,} rows, "
          f"{corr_df['country'].nunique()} countries")

    # Summary: what fraction of observations are negative?
    n_neg = (corr_df["correlation_20y"] < 0).sum()
    n_total = len(corr_df)
    pct_neg = n_neg / n_total * 100
    recent = corr_df[corr_df["year"] >= 2000]
    n_neg_recent = (recent["correlation_20y"] < 0).sum()
    pct_neg_recent = n_neg_recent / len(recent) * 100 if len(recent) > 0 else 0

    print(f"    Negative stock-bond correlation: "
          f"{pct_neg:.1f}% overall, {pct_neg_recent:.1f}% since 2000")
    print(f"    (Negative correlation = diversification works; "
          f"historically RARE per Artemis)")


def main():
    print("forex-centuries build pipeline\n")

    NORM.mkdir(parents=True, exist_ok=True)
    ANALYSIS.mkdir(parents=True, exist_ok=True)

    print("[1/16] FRED daily normalization")
    daily_long = build_fred_daily()

    print("\n[2/16] Yearly unified panel")
    panel = build_yearly_panel()

    print("\n[3/16] Log returns")
    daily_ret, yearly_ret = build_log_returns(daily_long)

    print("\n[4/16] Volatility statistics")
    build_volatility_stats(daily_ret, yearly_ret)

    print("\n[5/16] Correlation matrices")
    build_correlations(daily_ret, yearly_ret)

    print("\n[6/16] Rolling volatility")
    build_rolling_volatility(daily_long)

    print("\n[7/16] Regime analysis")
    build_regime_analysis(yearly_ret)

    print("\n[8/16] Gold inflation")
    build_gold_inflation(daily_long, panel)

    print("\n[9/16] Momentum analysis (Jegadeesh-Titman 1993)")
    build_momentum_analysis(daily_long)

    print("\n[10/16] Sigma event frequency (Monday Morning Macro)")
    build_sigma_events(daily_ret)

    print("\n[11/16] Asset class returns (Jordà et al. 2019)")
    build_jst_returns()

    print("\n[12/16] Stock-bond correlation (Artemis 2020)")
    build_stock_bond_correlation()

    print("\n[13/16] Sovereign default events (Trebesch et al.)")
    build_sovereign_defaults()

    print("\n[14/16] Sovereign debt in default (BoC-BoE)")
    build_debt_in_default()

    print("\n[15/16] ECB euro reference rates")
    build_ecb_daily()

    print("\n[16/16] World Bank inflation")
    build_wb_inflation()

    print("\nDone. All derived files regenerated.")


if __name__ == "__main__":
    main()
