# forex-centuries

Historical foreign exchange rate data spanning nine centuries (1106–2026), assembled for volatility research. 12 sources, 65 files, ~240 countries.

Related project: [fatcrash](https://github.com/unbalancedparentheses/fatcrash) — crash detection via fat-tail statistics (LPPLS, EVT, Hill estimator, Kappa).

## What the data shows

### Fat tails are universal and persistent

Every single currency pair — across all time scales and all centuries — shows heavier tails than a Gaussian distribution.

**Daily (1971–2025, 23 currencies):** 3-sigma events happen **3–6x more often** than a normal distribution predicts. Even the most "stable" pair (EUR/USD, excess kurtosis 2.5) has 4x too many tail events. Pegged and managed currencies (HKD, CNY, LKR) show the **highest** kurtosis — the peg suppresses daily moves but creates catastrophic jumps when it breaks.

**Yearly (1791–2025, 41 currencies):** Germany's Weimar hyperinflation produces kurtosis of 36.8 (a single year, 1923, saw a 16x log move). Latin American currencies (Mexico 82, Argentina 19, Brazil 13) show the fattest tails from repeated devaluations and redenominations. Even the UK, with 234 years of data, has excess kurtosis of 5.1.

| Currency | Ann Vol | Excess Kurtosis | Tail Ratio |
|----------|---------|-----------------|------------|
| GBP      | 9.4%    | 6.9             | 4.8x       |
| JPY      | 10.1%   | 9.0             | 5.4x       |
| CHF      | 11.0%   | 14.5            | 4.5x       |
| EUR      | 9.2%    | 2.5             | 4.0x       |
| BRL      | 15.6%   | 13.1            | 5.5x       |
| KRW      | 10.8%   | 139.7           | 4.4x       |

### Volatility clusters by regime

The data shows three regimes with different volatility profiles:

- **Gold standard era** (~1870–1914): low nominal volatility, sudden large breaks
- **Bretton Woods** (1944–1971): artificially suppressed vol, then explosive devaluations
- **Free float** (1971–present): higher day-to-day vol but fewer catastrophic jumps

The IRR regime data confirms this — countries classified as "freely falling" or "dual market" align with the biggest tail events.

### The peg paradox

Currencies with the lowest daily volatility (HKD at 3.2%, CNY at 8.2%) have some of the **highest** excess kurtosis (261 and 3846). Pegs compress the distribution most of the time but produce massive outliers when they break. This is the classic problem with using volatility as a risk measure — it underestimates the probability of extreme moves in managed currencies.

### Implications

The data strongly supports modeling FX returns with fat-tailed distributions (stable, Student-t, or power-law) rather than Gaussian. Standard VaR and options pricing models systematically underestimate tail risk in currency markets.

## Quickstart

```bash
python quickstart.py          # pure stdlib, no dependencies
python quickstart_pandas.py   # pandas version (pip install pandas openpyxl)
```

```
Yearly panel: 25,404 obs, 243 countries, 1500-2029
Sources: MW=3,444 | CI=9,031 | GMD=12,929

Longest series:
  United States              530 years (1500-2029)
  United Kingdom             240 years (1789-2029)
  Denmark                    239 years (1791-2029)

Daily: 13,802 dates x 23 currencies (1971-2025)
Medieval: 13,197 Spufford + 50,559 Metz records (521 cities)
```

See [SOURCES.md](SOURCES.md) for column schemas and quoting conventions.

## Coverage

```
                     1100   1200   1300   1400   1500   1600   1700   1800   1900   2000
MEMDB Spufford       ███████████████████████████████
MEMDB Metz                              ███████████████████████████████████
Clio Infra (GBP)                                   ████████████████████████████████████████
Clio Infra (USD)                                                         ██████████████████
BoE Millennium                                                            █████████████████
MeasuringWorth                                                            █████████████████
JST Macrohistory                                                                ███████████
Riksbank                                                                          █████████
IRR Regimes                                                                        ████████
IMF IFS                                                                               █████
BIS                                                                                   █████
World Bank                                                                            █████
GMD                                                                                   █████
FRED Daily                                                                             ████
```

## Directory Structure

```
data/
├── sources/           # Raw data organized by provider
│   ├── memdb/         # Medieval exchange rates (1106–1800)
│   ├── clio_infra/    # Exchange rates, inflation, bonds, debt, GDP (1500–2016)
│   ├── measuringworth/# 41 currencies vs USD (1791–2025)
│   ├── imf/           # 168 currencies, monthly (1955–2025)
│   ├── bis/           # Bilateral + effective rates, ~190 economies (1957–2026)
│   ├── fred/          # 23 daily pairs + 2 USD indices (1971–2025)
│   ├── riksbank/      # 53 SEK bilateral series (1900–2026)
│   ├── worldbank/     # Official rates, all members (1960–present)
│   ├── irr/           # Exchange rate regime classifications (1940–2021)
│   ├── jst/           # Macrohistory: 18 countries, 59 variables (1870–2017)
│   ├── boe/           # UK millennium dataset (1791–2016)
│   └── gmd/           # 243 countries, USDfx + REER (1960–2024)
└── derived/           # Computed from sources
    ├── normalized/    # Unified panels and normalized FRED data
    └── analysis/      # Log returns and volatility statistics
```

## Sources

### `sources/memdb/` — Medieval Exchange Rates

| File | Description | Records | Period |
|------|-------------|---------|--------|
| `memdb_spufford_medieval_exchange_rates.csv` | Exchange quotations across Europe, Byzantium, the Levant, and North Africa | 13,197 | 1106–1500 |
| `memdb_metz_currency_exchanges.csv` | Lower Rhine region and European comparison | 50,559 | 1350–1800 |

- Spufford: [MEMDB at Rutgers](https://memdb.libraries.rutgers.edu/spufford-currency)
- Metz: [MEMDB at Rutgers](https://memdb.libraries.rutgers.edu/metz-currency)

### `sources/clio_infra/` — Clio Infra

Project led by Jan Luiten van Zanden (Utrecht / IISH Amsterdam). Based on Denzel's *Handbook of World Exchange Rates, 1590–1914* and IMF IFS. Each dataset has a `.csv` (year-per-row) and original `.xlsx`.

| File | Description | Period | Countries |
|------|-------------|--------|-----------|
| `clio_infra_exchange_rates.csv` | Exchange rates vs USD | 1500–2013 | 181 |
| `clio_infra_exchange_rates_gbp.csv` | Exchange rates vs GBP | 1500–2013 | 181 |
| `clio_infra_inflation.csv` | Inflation (annual %) | 1500–2010 | 181 |
| `clio_infra_gold_standard.csv` | Gold standard (binary) | 1800–2010 | 71 |
| `clio_infra_bond_yield.csv` | Long-term govt bond yield | 1727–2011 | 42 |
| `clio_infra_govt_debt.csv` | Govt debt (% GDP) | 1692–2010 | 86 |
| `clio_infra_gdp_per_capita_compact.xlsx` | GDP per capita (Maddison) | 1500–2016 | 181 |

- [Source](https://clio-infra.eu/)

### `sources/measuringworth/`

41 currencies vs USD, yearly. UK from 1791, Spain from 1850, many European currencies from 1913. Compiled by Lawrence H. Officer and Samuel H. Williamson.

- `measuringworth_exchange_rates.csv`
- [Source](https://www.measuringworth.com/datasets/exchangeglobal/)

### `sources/imf/`

168 currencies vs USD, monthly. 158,518 observations.

- `imf_exchange_rates.csv` — columns: Date, Rate, Currency, Frequency, Source, Country code, Country
- [Source](https://github.com/codeforIATI/imf-exchangerates)

### `sources/bis/`

From the Bank for International Settlements. Stored as `.gz` (700 MB uncompressed, 16 MB compressed).

| File | Description | Rows | Period |
|------|-------------|------|--------|
| `xru/WS_XRU_csv_flat.csv.gz` | Bilateral exchange rates vs USD, ~190 economies | 1.47M | 1957–2026 |
| `eer/WS_EER_csv_flat.csv.gz` | Nominal and real effective exchange rates (NEER/REER), 64 economies | 1.19M | 1964–2026 |

- [Source](https://data.bis.org/bulkdownload)

### `sources/fred/`

23 daily currency pairs + 2 USD trade-weighted indices from the Federal Reserve H.10 release.

Pairs: GBP, JPY, CHF, CAD, AUD, EUR, DKK, MYR, NOK, NZD, SEK, MXN, BRL, CNY, INR, KRW, HKD, ZAR, SGD, LKR, TWD, THB, VEF.

- `daily/fred_*.csv` (25 files, 1971–2025)
- [Source](https://fred.stlouisfed.org/)

### `sources/riksbank/`

53 SEK bilateral exchange rate series (daily), including the trade-weighted SEK index from 1900. 295,018 total observations.

- `riksbank_exchange_rates.csv` — columns: date, series_id, value
- [Source](https://www.riksbank.se/en-gb/statistics/)

### `sources/worldbank/`

Official exchange rate (LCU per US$, period average) for all World Bank member countries.

- `worldbank_exchange_rates.xls`
- [Source](https://data.worldbank.org/indicator/PA.NUS.FCRF)

### `sources/irr/` — Ilzetzki-Reinhart-Rogoff

De facto exchange rate regime classifications for ~190 countries. Each dataset has a `.csv` and original `.xlsx`.

| File | Description | Period |
|------|-------------|--------|
| `irr_regime_coarse.csv` | Coarse regime classification | 1940–2019 |
| `irr_regime_fine.csv` | Fine regime classification | 1940–2019 |
| `irr_anchor_master.csv` | Anchor currency | 1946–2019 |
| `irr_unified_market_indicator.csv` | Unified vs dual/parallel market | 1946–2021 |

- [Source](https://www.ilzetzki.com/irr-data)

### `sources/jst/` — Jorda-Schularick-Taylor

18 advanced economies, 59 variables including exchange rates (`xrusd`), interest rates, GDP, credit, housing prices, and crisis indicators.

- `jst_macrohistory.xlsx`
- [Source](https://www.macrohistory.net/database/)

### `sources/boe/` — Bank of England

UK-focused: $/£ from 1791, monthly bilateral rates from 1963, effective exchange rates. Plus interest rates, prices, wages, GDP back to the 13th century.

- `boe_millennium.xlsx` (26 MB)
- [Source](https://www.bankofengland.co.uk/statistics/research-datasets)

### `sources/gmd/` — Global Macro Database

243 countries, harmonized from 111 data sources. Includes USD exchange rates and Real Effective Exchange Rates.

- `gmd_exchange_rates.csv` — columns: ISO3, countryname, year, USDfx, REER
- [Source](https://www.globalmacrodata.com/data.html)

## Derived Data

### `derived/normalized/`

| File | Description |
|------|-------------|
| `yearly_unified_panel.csv` | Merged yearly panel: 243 countries, 1500–2029 (MeasuringWorth + Clio Infra + GMD, with source tag) |
| `yearly_unified_wide.csv` | Same in wide format (year x country matrix) |
| `fred_daily_normalized.csv` | All 23 FRED pairs, foreign-per-USD convention (long format) |
| `fred_daily_normalized_wide.csv` | Same in wide format (date x currency matrix) |

### `derived/analysis/`

| File | Description |
|------|-------------|
| `yearly_log_returns.csv` | Annual log returns for 41 currencies (1791–2025) |
| `daily_log_returns.csv` | Daily log returns for 23 currencies (1971–2025), 271K obs |
| `yearly_volatility_stats.csv` | Mean, vol, excess kurtosis, skew, max/min for 41 currencies |
| `daily_volatility_stats.csv` | Same at daily frequency + 3-sigma tail event counts |

## Data Inventory

| Directory | Source | Files | Rows | Period |
|-----------|--------|------:|-----:|--------|
| `sources/memdb/` | MEMDB Spufford | 1 | 13,197 | 1106–1500 |
| `sources/memdb/` | MEMDB Metz | 1 | 50,559 | 1350–1800 |
| `sources/clio_infra/` | Clio Infra | 15 | ~3K rows/file | 1500–2016 |
| `sources/measuringworth/` | MeasuringWorth | 1 | 235 | 1791–2025 |
| `sources/imf/` | IMF IFS | 1 | 158,518 | 1955–2025 |
| `sources/bis/` | BIS | 2 | 2,664,238 | 1957–2026 |
| `sources/fred/` | FRED | 25 | ~14K/file | 1971–2025 |
| `sources/riksbank/` | Sveriges Riksbank | 1 | 295,018 | 1900–2026 |
| `sources/worldbank/` | World Bank | 1 | — | 1960–present |
| `sources/irr/` | Ilzetzki-Reinhart-Rogoff | 7 | — | 1940–2021 |
| `sources/jst/` | Jorda-Schularick-Taylor | 1 | 2,718 | 1870–2017 |
| `sources/boe/` | Bank of England | 1 | — | 1791–2016 |
| `sources/gmd/` | Global Macro Database | 1 | 56,850 | 1960–2024 |
| `derived/normalized/` | Derived | 4 | 296,632 | 1500–2029 |
| `derived/analysis/` | Derived | 4 | 271,205 | 1791–2025 |
| **Total** | **12 sources** | **65** | | **1106–2026** |

## TODO

- [ ] Reinhart-Rogoff official and parallel exchange rates from [carmenreinhart.com](https://carmenreinhart.com/exchange-rates-official-and-parallel/) (requires manual browser download). Unique dataset with parallel/black-market rates.

## References

- Denzel, M.A. (2010). *Handbook of World Exchange Rates, 1590–1914*. Ashgate/Routledge.
- Ilzetzki, E., Reinhart, C.M. & Rogoff, K.S. (2019). "Exchange Arrangements Entering the 21st Century." *QJE*, 134(2), 599–646.
- Jorda, O., Schularick, M. & Taylor, A.M. (2017). "Macrofinancial History and the New Business Cycle Facts." *NBER Macroeconomics Annual*, 31(1), 213–263.
- Metz, R. (1990). *Geld, Währung und Preisentwicklung: der Niederrheinraum im europäischen Vergleich, 1350–1800*. Frankfurt.
- Officer, L.H. & Williamson, S.H. *MeasuringWorth*.
- Reinhart, C.M. & Rogoff, K.S. (2009). *This Time Is Different: Eight Centuries of Financial Folly*. Princeton University Press.
- Spufford, P. (1986). *Handbook of Medieval Exchange*. Royal Historical Society.
- Thomas, R. & Dimsdale, N. (2017). "A Millennium of UK Data." Bank of England OBRA dataset.
