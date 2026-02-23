# Data Sources — Column Schemas and Notes

## `sources/memdb/`

### `memdb_spufford_medieval_exchange_rates.csv` (13,197 rows)

| Column | Description |
|--------|-------------|
| Place | City where exchange was quoted (e.g. Florence, Bruges, Venice) |
| Date_start | Start year of the quotation |
| Date_end | End year (empty if point-in-time) |
| Type_of_Exchange | Official, Commercial, or Manual |
| Currency_From | Source currency (e.g. "Florence, florin of") |
| Amount_From | Units of source currency |
| Currency_To | Target currency (e.g. "Florence, soldo of") |
| Amount_To | Units of target currency |
| Notes | Reference notes |
| Source | Bibliography reference number |

### `memdb_metz_currency_exchanges.csv` (50,559 rows)

| Column | Description |
|--------|-------------|
| Place | City (e.g. Aachen, Amsterdam, Cologne) |
| Year | Year of observation |
| Coin_Ratio | Coin type (e.g. Reichstaler, Ducat) |
| Relationship | Exchange relationship (e.g. Mark/Kurs) |
| Value | Exchange rate value |
| Length_of_Series | Series date range (e.g. "1569 1720") |
| Note | Reference note number |

## `sources/clio_infra/`

All Clio Infra CSV files share the same wide format: first column is `year`, remaining columns are country names. Values are yearly averages. Original `.xlsx` files contain additional sheets: "Data Long Format" and "Metadata".

| File | Unit | Period |
|------|------|--------|
| `clio_infra_exchange_rates.csv` | Local currency units per 1 USD | 1500–2013 |
| `clio_infra_exchange_rates_gbp.csv` | Local currency units per 1 GBP | 1500–2013 |
| `clio_infra_inflation.csv` | Annual percentage change | 1500–2010 |
| `clio_infra_gold_standard.csv` | 0 = not on gold standard, 1 = on gold standard | 1800–2010 |
| `clio_infra_bond_yield.csv` | Annual average percentage | 1727–2011 |
| `clio_infra_govt_debt.csv` | Percentage of GDP | 1692–2010 |
| `clio_infra_gdp_per_capita_compact.xlsx` | 1990 International Geary-Khamis dollars | 1500–2016 |

## `sources/measuringworth/`

### `measuringworth_exchange_rates.csv` (235 rows)

Wide format: `year` + 41 country columns. Values are **foreign currency units per 1 USD** (e.g. UK=0.22 means 0.22 GBP per USD).

**Quoting convention note**: UK, Australia, and New Zealand are quoted as foreign-per-USD here (unlike FRED which quotes USD-per-foreign for these currencies).

### `measuringworth_gold_prices.csv` (769 rows)

Annual gold prices from MeasuringWorth, 1257–2025. Six series:

| Column | Unit | Period |
|--------|------|--------|
| `british_official_gbp` | British pounds per fine ounce (end of year) | 1257–1945 |
| `london_market_gbp` | British pounds per fine ounce (London fix) | 1718–1949 |
| `london_market_usd` | US dollars per fine ounce (London fix) | 1950–2025 |
| `us_official_usd` | US dollars per fine ounce (end of year) | 1791–2025 |
| `new_york_market_usd` | US dollars per fine ounce (NY market) | 1791–2025 |
| `gold_silver_ratio` | Ounces of silver per ounce of gold | 1687–2025 |

The London Market Price switches currency mid-stream (GBP before 1950, USD from 1950), so it's split into two columns. Citation: Lawrence H. Officer and Samuel H. Williamson, "The Price of Gold, 1257-2014," MeasuringWorth, 2026.

## `sources/gold/`

### `gold_monthly_usd.csv` (2,311 rows)

Monthly gold price in USD per troy ounce, 1833–2025. From DataHub/datasets/gold-prices (Timothy Green's historical series + World Bank commodity data).

| Column | Description |
|--------|-------------|
| Date | YYYY-MM |
| Price | USD per troy ounce |

- [Source](https://github.com/datasets/gold-prices)

## `sources/imf/`

### `imf_exchange_rates.csv` (158,518 rows)

| Column | Description |
|--------|-------------|
| Date | End-of-month date (YYYY-MM-DD) |
| Rate | Local currency units per 1 USD |
| Currency | ISO 4217 currency code |
| Frequency | Always "M" (monthly) |
| Source | Always "IMF" |
| Country code | ISO 2-letter country code |
| Country | Full country name |

## `sources/bis/`

BIS files are gzipped CSV (`gunzip` to decompress). Both use the BIS SDMX flat format.

### `xru/WS_XRU_csv_flat.csv.gz` (1,474,826 rows)

Bilateral exchange rates vs USD. Key columns:

| Column | Description |
|--------|-------------|
| FREQ:Frequency | M (Monthly), Q (Quarterly), A (Annual) |
| REF_AREA:Reference area | ISO 2-letter country code with label |
| CURRENCY:Currency | Currency code with label |
| COLLECTION:Collection | A (Average), E (End of period), H (High), L (Low) |
| TIME_PERIOD | Date (YYYY-MM for monthly, YYYY for annual) |
| OBS_VALUE | Exchange rate (local currency per USD) |

### `eer/WS_EER_csv_flat.csv.gz` (1,189,410 rows)

Effective exchange rates. Key columns:

| Column | Description |
|--------|-------------|
| EER_TYPE:Type | N (Nominal), R (Real) |
| EER_BASKET:Basket | B (Broad, 64 economies), N (Narrow, 27 economies) |
| REF_AREA:Reference area | Country code |
| TIME_PERIOD | Date |
| OBS_VALUE | Index value (2020 = 100) |

## `sources/fred/`

25 CSV files in `daily/`. Each has two columns:

| Column | Description |
|--------|-------------|
| observation_date | YYYY-MM-DD |
| DEX* | Exchange rate |

**Quoting conventions** (important):
- **USD per 1 foreign unit**: GBP (`DEXUSUK`), EUR (`DEXUSEU`), AUD (`DEXUSAL`), NZD (`DEXUSNZ`)
- **Foreign units per 1 USD**: all other pairs
- Missing values shown as `.` (Fed holidays, weekends)

Dollar indices (`fred_usd_broad_index.csv`, `fred_usd_major_index.csv`) are trade-weighted index values.

## `sources/riksbank/`

### `riksbank_exchange_rates.csv` (295,018 rows)

| Column | Description |
|--------|-------------|
| date | YYYY-MM-DD |
| series_id | Riksbank series ID (e.g. SEKUSDPMI = SEK per USD) |
| value | Exchange rate (foreign currency per SEK) |

Series naming: `SEK[CURRENCY]PMI` where CURRENCY is the ISO code. `SEKETT` is the trade-weighted SEK index (from 1900).

## `sources/worldbank/`

### `worldbank_exchange_rates.xls`

Standard World Bank WDI format. Official exchange rate (LCU per US$, period average). Rows are countries, columns are years.

## `sources/irr/`

Ilzetzki-Reinhart-Rogoff exchange rate regime classifications. Complex matrix format: rows are months (YYYY:MM), columns are countries.

| File | Description | Values |
|------|-------------|--------|
| `irr_regime_coarse.csv` | Coarse classification | 1=peg, 2=crawling peg, 3=managed float, 4=free float, 5=freely falling, 6=dual market |
| `irr_regime_fine.csv` | Fine classification | 1-15 scale with finer distinctions |
| `irr_anchor_master.csv` | Anchor currency | Which major currency each country pegs to |
| `irr_unified_market_indicator.csv` | Market structure | 0=unified, 1=dual/parallel/black market |

## `sources/jst/`

### `jst_macrohistory.xlsx` (2,718 rows, 59 columns)

Long format: each row is one country-year. Key columns for FX research:

| Column | Description |
|--------|-------------|
| year | Year |
| country | Country name |
| iso | ISO 3-letter code |
| xrusd | Exchange rate vs USD |
| cpi | Consumer price index |
| stir | Short-term interest rate |
| ltrate | Long-term interest rate |
| peg | Peg indicator |
| peg_type | Type of peg |
| crisisJST | Financial crisis indicator |

18 countries: AUS, BEL, CAN, CHE, DEU, DNK, ESP, FIN, FRA, GBR, ITA, JPN, NLD, NOR, PRT, SWE, USA + more.

## `sources/boe/`

### `boe_millennium.xlsx` (26 MB, 90+ sheets)

Key sheets for FX research:

| Sheet | Description |
|-------|-------------|
| A33. Exchange rate data | $/£ from 1791, real $/£, nominal effective rate |
| M14. Mthly Exchange rates 1963+ | Monthly bilateral rates (CAD, EUR, FRF, DEM, JPY, etc.) |
| M15. Mthly $-£ 1791-2015 | Monthly $/£ rate |
| A31. Interest rates & asset ps | Interest rates and asset prices |
| D1. Official Interest Rates | Daily Bank Rate |

## `sources/gmd/`

### `gmd_exchange_rates.csv` (56,850 rows)

| Column | Description |
|--------|-------------|
| ISO3 | ISO 3-letter country code |
| countryname | Full country name |
| year | Year (float) |
| USDfx | Local currency per USD |
| REER | Real effective exchange rate index |

## Derived Data

### `derived/normalized/fred_daily_normalized.csv` (271,228 rows)

| Column | Description |
|--------|-------------|
| date | YYYY-MM-DD |
| currency | ISO 3-letter currency code |
| rate_per_usd | Foreign currency units per 1 USD |

All FRED pairs normalized to the same convention. GBP, EUR, AUD, NZD inverted from their original FRED quoting.

### `derived/normalized/fred_daily_normalized_wide.csv` (13,802 rows)

Same data pivoted: `date` column + one column per currency. Empty cells = no data for that date.

### `derived/normalized/yearly_unified_panel.csv` (24,656 rows)

| Column | Description |
|--------|-------------|
| year | Year |
| country | Country name |
| rate_per_usd | Foreign currency units per 1 USD |
| source | MW (MeasuringWorth), CI (Clio Infra), or GMD (Global Macro Database) |

Merged yearly panel: MeasuringWorth preferred, then Clio Infra, then Global Macro Database. 243 countries, 1500–2025. GMD projections (2026–2029) excluded.

### `derived/normalized/yearly_unified_wide.csv`

Same data pivoted: `year` column + one column per country.

### `derived/analysis/daily_volatility_stats.csv` (23 rows)

| Column | Description |
|--------|-------------|
| currency | ISO 3-letter code |
| n_days | Number of trading days |
| start_date / end_date | Date range |
| daily_volatility | Standard deviation of daily log returns |
| annualized_volatility | daily_volatility * sqrt(252) |
| excess_kurtosis | Kurtosis - 3 (0 = Gaussian) |
| skewness | Skewness of log returns |
| max/min_daily_log_return | Largest daily moves |
| tail_events_3sigma | Count of days exceeding 3 standard deviations |
| expected_normal | Expected 3-sigma events under Gaussian |
| tail_ratio | tail_events / expected_normal |

### `derived/analysis/yearly_volatility_stats.csv` (40 rows)

Same structure but for annual log returns from MeasuringWorth data. No tail_events columns.

### `derived/analysis/daily_log_returns.csv` (271,205 rows)

| Column | Description |
|--------|-------------|
| date | YYYY-MM-DD |
| currency | ISO 3-letter code |
| log_return | ln(rate_t / rate_{t-1}) |

### `derived/analysis/monthly_gold_inflation.csv` (119,346 rows)

| Column | Description |
|--------|-------------|
| year_month | YYYY-MM |
| currency | ISO currency code |
| source | FRED or IMF |
| rate_per_usd | Monthly avg exchange rate |
| gold_usd | Gold price in USD (per troy oz) |
| gold_local | Gold price in local currency |
| grams_per_100 | Grams of gold per 100 local currency units |
| gold_inflation_mom_pct | Month-over-month gold price change (%) |
| gold_log_return | Monthly log return |
| gold_inflation_yoy_pct | Year-over-year gold price change (%) |
| cumulative_retained_pct | % of gold purchasing power retained since first month |

174 currencies (23 FRED + 168 IMF), 1940–2025.

### `derived/analysis/yearly_gold_inflation.csv` (26,114 rows)

| Column | Description |
|--------|-------------|
| year | Year |
| decade | Decade (for easy grouping) |
| country | Country name |
| gold_local | Gold price in local currency (per troy ounce) |
| grams_per_100 | Grams of gold per 100 local currency units |
| gold_inflation_pct | Year-over-year gold price change in local currency (%) |
| gold_log_return | ln(gold_t / gold_{t-1}) |
| cpi_inflation_pct | CPI inflation (from Clio Infra, where available) |
| gold_vs_cpi_gap_pct | Gold inflation minus CPI inflation (pp) |
| cumulative_retained_pct | % of gold purchasing power retained since base_year |
| base_year | First available year for this country |

### `derived/analysis/yearly_log_returns.csv` (234 rows)

Wide format: `year` + one column per country. Values are annual log returns.
