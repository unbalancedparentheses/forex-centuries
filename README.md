# forex-centuries

Historical foreign exchange rate data spanning nine centuries (1106–2026), assembled for volatility research.

## Directory Structure

```
data/
├── medieval/          # Pre-modern exchange rates
├── yearly/            # Annual frequency data
├── monthly/           # Monthly + sub-monthly data
├── daily/             # Daily frequency data
├── regimes/           # Exchange rate regime classifications
├── macro/             # Supporting macroeconomic variables
└── analysis/          # Computed log returns and volatility stats
```

## Datasets

### `data/medieval/` — Medieval Exchange Rates (1106–1800)

| File | Source | Records | Period |
|------|--------|---------|--------|
| `memdb_spufford_medieval_exchange_rates.csv` | [Spufford, *Handbook of Medieval Exchange*](https://memdb.libraries.rutgers.edu/spufford-currency) | 13,197 | 1106–1500 |
| `memdb_metz_currency_exchanges.csv` | [Metz, *Geld, Währung und Preisentwicklung*](https://memdb.libraries.rutgers.edu/metz-currency) | 50,559 | 1350–1800 |

### `data/yearly/` — Annual Exchange Rates (1500–2025)

| File | Source | Coverage | Period |
|------|--------|----------|--------|
| `clio_infra_exchange_rates.csv` | [Clio Infra](https://clio-infra.eu/Indicators/ExchangeRatestoUSDollar.html) | 181 countries vs USD | 1500–2013 |
| `clio_infra_exchange_rates_gbp.csv` | [Clio Infra](https://clio-infra.eu/Indicators/ExchangeRatestoUKPound.html) | 181 countries vs GBP | 1500–2013 |
| `measuringworth_exchange_rates.csv` | [MeasuringWorth](https://www.measuringworth.com/datasets/exchangeglobal/) | 41 currencies vs USD | 1791–2025 |
| `gmd_exchange_rates.csv` | [Global Macro Database](https://www.globalmacrodata.com/data.html) | 243 countries (USDfx + REER) | 1960–2024 |
| `worldbank_exchange_rates.xls` | [World Bank](https://data.worldbank.org/indicator/PA.NUS.FCRF) | All member countries | 1960–present |
| `jst_macrohistory.xlsx` | [Jorda-Schularick-Taylor](https://www.macrohistory.net/database/) | 18 countries, 59 variables | 1870–2017 |
| `boe_millennium.xlsx` | [Bank of England](https://www.bankofengland.co.uk/statistics/research-datasets) | UK macro + $/£ | 1791–2016 |

Also includes original `.xlsx` variants of Clio Infra datasets.

### `data/monthly/` — Monthly Exchange Rates (1955–2026)

| File | Source | Coverage | Period |
|------|--------|----------|--------|
| `imf_exchange_rates.csv` | [IMF IFS](https://github.com/codeforIATI/imf-exchangerates) | 168 currencies vs USD | 1955–2025 |
| `bis_xru/WS_XRU_csv_flat.csv.gz` | [BIS](https://data.bis.org/topics/XRU) | ~190 economies vs USD (1.47M rows) | 1957–2026 |
| `bis_eer/WS_EER_csv_flat.csv.gz` | [BIS](https://data.bis.org/topics/EER) | NEER/REER for 64 economies (1.19M rows) | 1964–2026 |
| `riksbank_exchange_rates.csv` | [Sveriges Riksbank](https://www.riksbank.se/en-gb/statistics/) | 53 SEK bilateral series (295K obs) | 1900–2026 |

BIS files stored as `.gz` (700 MB uncompressed, 16 MB compressed). Decompress with `gunzip`.

### `data/daily/` — Daily Exchange Rates (1971–2026)

| File | Source | Coverage | Period |
|------|--------|----------|--------|
| `fred/*.csv` (25 files) | [FRED H.10](https://fred.stlouisfed.org/) | 23 currency pairs + 2 USD indices | 1971–2025 |
| `fred_daily_normalized.csv` | Derived | All 23 pairs, foreign-per-USD convention (long format) | 1971–2025 |
| `fred_daily_normalized_wide.csv` | Derived | Same in wide format (date x currency matrix) | 1971–2025 |

Pairs: GBP, JPY, CHF, CAD, AUD, EUR, DKK, MYR, NOK, NZD, SEK, MXN, BRL, CNY, INR, KRW, HKD, ZAR, SGD, LKR, TWD, THB, VEF.

### `data/regimes/` — Exchange Rate Regime Classifications (1940–2021)

| File | Source | Coverage | Period |
|------|--------|----------|--------|
| `irr_regime_coarse.csv` | [Ilzetzki-Reinhart-Rogoff](https://www.ilzetzki.com/irr-data) | ~190 countries, coarse classification | 1940–2019 |
| `irr_regime_fine.csv` | Same | Fine classification | 1940–2019 |
| `irr_anchor_master.csv` | Same | Anchor currency | 1946–2019 |
| `irr_unified_market_indicator.csv` | Same | Unified vs dual/parallel market | 1946–2021 |

Original `.xlsx` files also included.

### `data/macro/` — Supporting Macroeconomic Variables

| File | Variable | Period | Countries |
|------|----------|--------|-----------|
| `clio_infra_inflation.csv` | Inflation (annual %) | 1500–2010 | 181 |
| `clio_infra_gold_standard.csv` | Gold standard (binary) | 1800–2010 | 71 |
| `clio_infra_bond_yield.csv` | Long-term govt bond yield | 1727–2011 | 42 |
| `clio_infra_govt_debt.csv` | Govt debt (% GDP) | 1692–2010 | 86 |
| `clio_infra_gdp_per_capita_compact.xlsx` | GDP per capita (Maddison) | 1500–2016 | 181 |

### `data/analysis/` — Computed Statistics

| File | Description |
|------|-------------|
| `yearly_log_returns.csv` | Annual log returns for 41 currencies (1791–2025) |
| `daily_log_returns.csv` | Daily log returns for 23 currencies (1971–2025), 271K obs |
| `yearly_volatility_stats.csv` | Mean, vol, excess kurtosis, skew, max/min for 41 currencies |
| `daily_volatility_stats.csv` | Same at daily frequency + 3-sigma tail event counts |

## Data Coherence

Cross-validated across overlapping datasets:

- **MeasuringWorth vs Clio Infra**: Excellent agreement for stable currencies. Divergences from currency redenominations (Brazil, Mexico, Argentina), Euro switchover (France, Germany, Netherlands post-1999), and quoting conventions (Australia, South Africa).
- **FRED vs MeasuringWorth**: JPY/USD perfect match. GBP/USD exact inverses (different quoting convention).
- **All datasets coherent.** Differences explained by quoting conventions and redenomination tracking.

## Key Finding: Universal Fat Tails

Every single currency pair exhibits excess kurtosis. Daily 3-sigma events occur **3–6x more often** than a Gaussian distribution predicts:

| Currency | Daily Vol | Ann Vol | Excess Kurt | Tail Ratio |
|----------|-----------|---------|-------------|------------|
| GBP      | 0.0059    | 9.4%    | 6.9         | 4.8x       |
| JPY      | 0.0064    | 10.1%   | 9.0         | 5.4x       |
| CHF      | 0.0069    | 11.0%   | 14.5        | 4.5x       |
| EUR      | 0.0058    | 9.2%    | 2.5         | 4.0x       |
| BRL      | 0.0098    | 15.6%   | 13.1        | 5.5x       |
| KRW      | 0.0068    | 10.8%   | 139.7       | 4.4x       |

## TODO

- [ ] Reinhart-Rogoff official and parallel exchange rates from [carmenreinhart.com](https://carmenreinhart.com/exchange-rates-official-and-parallel/) (requires manual browser download — JavaScript-rendered link). Unique dataset with parallel/black-market rates.

## Purpose

Researching exchange rate volatility across centuries — fat tails, regime changes, and structural breaks in currency markets.

## References

- Denzel, M.A. (2010). *Handbook of World Exchange Rates, 1590–1914*. Ashgate/Routledge.
- Ilzetzki, E., Reinhart, C.M. & Rogoff, K.S. (2019). "Exchange Arrangements Entering the 21st Century." *QJE*, 134(2), 599–646.
- Jorda, O., Schularick, M. & Taylor, A.M. (2017). "Macrofinancial History and the New Business Cycle Facts." *NBER Macroeconomics Annual*, 31(1), 213–263.
- Metz, R. (1990). *Geld, Währung und Preisentwicklung: der Niederrheinraum im europäischen Vergleich, 1350–1800*. Frankfurt.
- Officer, L.H. & Williamson, S.H. *MeasuringWorth*.
- Reinhart, C.M. & Rogoff, K.S. (2009). *This Time Is Different: Eight Centuries of Financial Folly*. Princeton University Press.
- Spufford, P. (1986). *Handbook of Medieval Exchange*. Royal Historical Society.
- Thomas, R. & Dimsdale, N. (2017). "A Millennium of UK Data." Bank of England OBRA dataset.
