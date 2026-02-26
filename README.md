# forex-centuries

Historical monetary and exchange rate data spanning nine centuries (1106-2026). 17 sources, 88 files, ~240 countries. Exchange rates, gold, silver, interest rates, CPI, and regime classifications — assembled for long-run volatility and tail-risk research.

Related project: [fatcrash](https://github.com/unbalancedparentheses/fatcrash) — crash detection via fat-tail statistics (LPPLS, EVT, Hill estimator, Kappa).

## Coverage

```
Asset                1100   1200   1300   1400   1500   1600   1700   1800   1900   2000
                     :      :      :      :      :      :      :      :      :      :
EXCHANGE RATES       :      :      :      :      :      :      :      :      :      :
Medieval FX          ██████████████████████████████████████████████████████████      :
Clio Infra FX        :      :      :      :      ████████████████████████████████████████
MeasuringWorth FX    :      :      :      :      :      :      :      █████████████████
BoE Millennium       :      :      :      :      :      :      :      ██████████████████
JST Macrohistory     :      :      :      :      :      :      :      :     ████████████
Riksbank             :      :      :      :      :      :      :      :       ██████████
Penn World Table     :      :      :      :      :      :      :      :         ████████
BIS                  :      :      :      :      :      :      :      :            █████
IMF IFS              :      :      :      :      :      :      :      :            █████
World Bank           :      :      :      :      :      :      :      :            █████
GMD                  :      :      :      :      :      :      :      :            █████
FRED Daily           :      :      :      :      :      :      :      :             ████
                     :      :      :      :      :      :      :      :      :      :
PRECIOUS METALS      :      :      :      :      :      :      :      :      :      :
Gold (GBP)           :      █████████████████████████████████████████████████████████████
Gold (USD)           :      :      :      :      :      :      :      █████████████████
Silver               :      :      :      :      :      :      ████████████████████████
LBMA Gold+Silver     :      :      :      :      :      :      :      :      :  ████████
Gold/Silver Ratio    :      :      :      :      :      :      ████████████████████████
                     :      :      :      :      :      :      :      :      :      :
INTEREST RATES       :      :      :      :      :      :      :      :      :      :
UK+US Rates          :      :      :      :      :      :      ████████████████████████
                     :      :      :      :      :      :      :      :      :      :
INFLATION            :      :      :      :      :      :      :      :      :      :
US CPI               :      :      :      :      :      :      :      █████████████████
Clio Infra CPI       :      :      :      :      ████████████████████████████████████████
                     :      :      :      :      :      :      :      :      :      :
REGIMES              :      :      :      :      :      :      :      :      :      :
IRR Classifications  :      :      :      :      :      :      :      :       █████████
```

## What the data shows

### Fat tails are universal and persistent

Every single currency pair — across all time scales and all centuries — shows heavier tails than a Gaussian distribution.

**Daily (1971-2025, 23 currencies):** 3-sigma events happen **3-6x more often** than a normal distribution predicts. Even the most "stable" pair (EUR/USD, excess kurtosis 2.5) has 4x too many tail events. Pegged and managed currencies (HKD, CNY, LKR) show the **highest** kurtosis — the peg suppresses daily moves but creates catastrophic jumps when it breaks.

**Yearly (1791-2025, 40 currencies):** Germany's Weimar hyperinflation produces kurtosis of 36.8 (a single year, 1923, saw a 16x log move). Latin American currencies (Mexico 82, Argentina 19, Brazil 13) show the fattest tails from repeated devaluations and redenominations. Even the UK, with 234 years of data, has excess kurtosis of 5.1.

| Currency | Ann Vol | Excess Kurtosis | Tail Ratio |
|----------|---------|-----------------|------------|
| GBP      | 9.4%    | 6.9             | 4.8x       |
| JPY      | 10.1%   | 9.0             | 5.4x       |
| CHF      | 11.0%   | 14.5            | 4.5x       |
| EUR      | 9.2%    | 2.5             | 4.0x       |
| BRL      | 15.6%   | 13.1            | 5.5x       |
| KRW      | 10.8%   | 139.7           | 4.4x       |

### The peg paradox

Currencies with the lowest daily volatility (HKD at 3.2%, CNY at 8.2%) have some of the **highest** excess kurtosis (261 and 3846). Pegs compress the distribution most of the time but produce massive outliers when they break. This is the classic problem with using volatility as a risk measure — it underestimates the probability of extreme moves in managed currencies.

### Volatility clusters by regime

Three distinct regimes emerge from the data:

- **Gold standard era** (~1870-1914): low nominal volatility, sudden large breaks
- **Bretton Woods** (1944-1971): artificially suppressed vol, then explosive devaluations
- **Free float** (1971-present): higher day-to-day vol but fewer catastrophic jumps

The regime-conditional statistics quantify this: freely falling currencies have annual volatility of 225% vs 10.8% for free-floating. Pegged currencies show excess kurtosis of 133 vs 0.8 for free float — confirming that pegs suppress daily volatility but produce catastrophic jumps.

### Cross-currency correlations

Daily log-return correlations reveal geographic clustering: Scandinavian currencies (DKK, SEK, NOK) move together, as do Asian managed currencies (SGD, TWD, THB). European currencies are tightly correlated with each other but less with emerging market pairs.

### Implications

The data strongly supports modeling FX returns with fat-tailed distributions (stable, Student-t, or power-law) rather than Gaussian. Standard VaR and options pricing models systematically underestimate tail risk in currency markets.

## Quickstart

```bash
# 1. Install dependencies
nix develop                      # Nix flake (recommended)
pip install -r requirements.txt  # pip fallback

# 2. Explore the data
python quickstart.py             # pure stdlib, no dependencies
python quickstart_pandas.py      # pandas version
```

```
Yearly panel: 24,656 obs, 243 countries, 1500-2025
Sources: MW=3,444 | CI=9,031 | GMD=12,181

Longest series:
  United States              526 years (1500-2025)
  United Kingdom             236 years (1789-2025)
  Denmark                    235 years (1791-2025)

Daily: 13,802 dates x 23 currencies (1971-2025)
Medieval: 13,197 Spufford (521 places) + 50,559 Metz records (29 places)
```

## Build pipeline

All derived data and charts are reproducible from source files:

```bash
python build.py               # regenerate data/derived/ from data/sources/
python validate.py            # run data quality checks (52 checks)
python visualize.py           # generate charts/ (9 PNGs)

make all                      # build + validate + visualize in one step
```

The 8-step build pipeline produces:
1. FRED daily normalization (23 currencies, foreign-per-USD convention)
2. Yearly unified panel (243 countries, MW > CI > GMD priority merge)
3. Log returns (daily and yearly)
4. Volatility statistics (kurtosis, tail events, 3-sigma counts)
5. Correlation matrices (daily 23x23, yearly 40x40)
6. Rolling volatility (252-day window)
7. Regime analysis (IRR fine->coarse, regime-conditional stats)
8. Gold inflation (yearly 243 countries since 1257, monthly 174 currencies)

## Testing

```bash
pytest tests/ -v              # 13 unit tests for build pipeline correctness
make test                     # same via make
```

Tests cover FRED inversion logic, source priority merge, log return formulas, tail event counting, regime mapping, gold calculations, and rolling window behavior — all using synthetic data with no network calls.

## Interactive notebook

```bash
jupyter lab notebooks/exploration.ipynb
```

Seven sections: yearly panel, daily data, fat tails (histogram + QQ-plot), regime analysis, gold inflation, and medieval data. Each section loads the relevant dataset and produces inline charts.

## Updating source data

14 sources are automatically fetched by `update_sources.py`. A weekly GitHub Actions workflow runs `--all` every Monday at 06:00 UTC, or trigger it manually from the Actions tab.

```bash
python scripts/update_sources.py --all           # update all 14 sources
python scripts/update_sources.py --fred          # or update individually
```

FRED requires a free API key from [fred.stlouisfed.org](https://fred.stlouisfed.org/docs/api/api_key.html). Set it as `FRED_API_KEY` in your environment or as a GitHub repository secret. All other sources require no authentication.

## Charts

`python visualize.py` generates 9 PNGs in `charts/`:

| Chart | Description |
|-------|-------------|
| `fat_tails_histogram.png` | EUR/USD daily log returns vs fitted normal — shows excess density in the tails |
| `peg_paradox.png` | Annualized volatility vs excess kurtosis — low-vol pegs cluster at extreme kurtosis |
| `tail_ratio_bar.png` | Observed 3-sigma events / Gaussian expectation — every currency exceeds 1.0 |
| `rolling_volatility.png` | 1-year rolling vol for GBP, JPY, CHF, EUR with Nixon shock, Lehman, COVID markers |
| `correlation_heatmap.png` | Hierarchically clustered daily log-return correlations (23x23) |
| `gold_erosion.png` | Cumulative gold purchasing power retained for USD, GBP, JPY, CHF, FRF, DEM, INR, CNY |
| `regime_timeline.png` | Exchange rate regime (peg -> free float -> freely falling) for 25 countries, 1940-2019 |
| `qq_daily.png` | QQ-plots for 6 daily currencies — tail deviation from the normal reference line |
| `qq_regimes.png` | QQ-plots comparing peg vs free float vs freely falling return distributions |

## Project structure

```
forex-centuries/
├── data/
│   ├── sources/           # Raw data, untouched from provider (17 sources)
│   │   ├── memdb/         # Medieval exchange rates (1106-1800)
│   │   ├── clio_infra/    # Exchange rates, inflation, bonds, debt, GDP (1500-2016)
│   │   ├── measuringworth/# FX, gold, silver, interest rates, CPI (1257-2025)
│   │   ├── freegold/      # 768-year gold, silver, gold/silver ratio (1258-2025)
│   │   ├── lbma/          # Daily gold + silver prices in USD/GBP/EUR (1968-2025)
│   │   ├── imf/           # 173 currencies, monthly (1955-2025)
│   │   ├── bis/           # Bilateral + effective rates, ~190 economies (1957-2026)
│   │   ├── fred/          # 23 daily pairs + 2 USD indices (1971-2025)
│   │   ├── gold/          # Monthly gold prices USD (1833-2025)
│   │   ├── riksbank/      # 53 SEK bilateral series (1900-2026)
│   │   ├── worldbank/     # Official rates, all members (1960-present)
│   │   ├── pwt/           # Penn World Table: 185 countries, FX + PPP (1950-2023)
│   │   ├── irr/           # Exchange rate regime classifications (1940-2021)
│   │   ├── jst/           # Macrohistory: 18 countries, 59 variables (1870-2017)
│   │   ├── boe/           # UK millennium dataset (1791-2016)
│   │   └── gmd/           # 243 countries, USDfx + REER (1960-2024)
│   └── derived/           # Computed by build.py (never hand-edited)
│       ├── normalized/    # Unified panels (yearly 243 countries, daily 23 currencies)
│       └── analysis/      # Log returns, volatility, correlations, regimes, gold
├── charts/                # Generated by visualize.py (9 PNGs)
├── notebooks/             # Jupyter exploration notebook
├── scripts/               # update_sources.py (14 automated fetchers)
├── tests/                 # Unit tests (13 tests, synthetic data)
├── build.py               # 8-step ETL pipeline
├── validate.py            # Data quality checks (52 checks)
├── visualize.py           # Chart generation (9 PNGs)
├── quickstart.py          # Explore data with pure stdlib
└── quickstart_pandas.py   # Explore data with pandas
```

## Sources

### Automated (`update_sources.py --all`)

| Source | Flag | Data | Period | Auth |
|--------|------|------|--------|------|
| [FRED](https://fred.stlouisfed.org/) | `--fred` | 23 daily FX pairs + 2 USD indices | 1971-2025 | `FRED_API_KEY` |
| [IMF IFS](https://codeforiati.org/imf-exchangerates/) | `--imf` | 173 currencies vs USD, monthly | 1955-2025 | |
| [BIS](https://data.bis.org/bulkdownload) | `--bis` | Bilateral + effective rates, ~190 economies | 1957-2026 | |
| [Sveriges Riksbank](https://www.riksbank.se/en-gb/statistics/) | `--riksbank` | 53 SEK bilateral series, daily | 1900-2026 | |
| [World Bank](https://data.worldbank.org/indicator/PA.NUS.FCRF) | `--worldbank` | Official rates, all member countries | 1960-present | |
| [JST Macrohistory](https://www.macrohistory.net/database/) | `--jst` | 18 economies, 59 macro/financial variables | 1870-2017 | |
| [Penn World Table](https://www.rug.nl/ggdc/productivity/pwt/) | `--pwt` | 185 countries, exchange rates + PPP | 1950-2023 | |
| [MeasuringWorth](https://www.measuringworth.com/datasets/) | `--measuringworth` | 41 FX vs USD, gold (5 series), interest rates (UK+US), US CPI, $/£ | 1257-2025 | |
| [Clio Infra](https://clio-infra.eu/) | `--clio` | FX (USD+GBP), inflation, bonds, debt, GDP, gold standard | 1500-2016 | |
| [FreeGoldAPI](https://freegoldapi.com/) | `--freegold` | 768-year gold prices, gold/silver ratio, silver prices | 1258-2025 | |
| [LBMA](https://www.lbma.org.uk/prices-and-data/precious-metal-prices) | `--lbma` | Daily gold + silver in USD, GBP, EUR | 1968-2025 | |
| [DataHub Gold](https://github.com/datasets/gold-prices) | `--gold` | Monthly gold prices USD | 1833-2025 | |
| [IRR](https://www.ilzetzki.com/irr-data) | `--irr` | De facto FX regime classifications, ~190 countries | 1940-2021 | |
| [Bank of England](https://www.bankofengland.co.uk/statistics/research-datasets) | `--boe` | UK millennium dataset ($/£, rates, prices, GDP) | 1791-2016 | |

### Static (committed to repo, updated manually)

| Source | Data | Period | Notes |
|--------|------|--------|-------|
| [MEMDB Spufford](https://memdb.libraries.rutgers.edu/spufford-currency) | Medieval exchange quotations (521 places) | 1106-1500 | No export API |
| [MEMDB Metz](https://memdb.libraries.rutgers.edu/metz-currency) | Lower Rhine + European comparison (29 places) | 1350-1800 | No export API |
| [Global Macro Database](https://www.globalmacrodata.com/data.html) | 243 countries, USDfx + REER | 1960-2024 | Email-gated |

See [SOURCES.md](SOURCES.md) for column schemas, quoting conventions, and file-level details.

## Longest series by asset type

| Asset | Series | Years | Period | Source |
|-------|--------|------:|--------|--------|
| Gold | British official price (GBP/oz) | 768 | 1257-2025 | MeasuringWorth |
| Gold | USD price per oz | 767 | 1258-2025 | FreeGoldAPI |
| Exchange rates | 186 countries vs GBP | 516 | 1500-2016 | Clio Infra |
| Exchange rates | 186 countries vs USD | 516 | 1500-2016 | Clio Infra |
| Medieval FX | European exchange quotations | 694 | 1106-1800 | MEMDB |
| Silver | Silver-normalized prices | 337 | 1688-2025 | FreeGoldAPI |
| Gold/silver ratio | Annual ratio | 338 | 1687-2025 | MeasuringWorth |
| Interest rates | UK short + long term | 296 | 1729-2025 | MeasuringWorth |
| US CPI | Consumer price index | 251 | 1774-2025 | MeasuringWorth |
| Dollar-pound | $/£ rate | 234 | 1791-2025 | MeasuringWorth |
| 41 FX vs USD | Annual rates | 234 | 1791-2025 | MeasuringWorth |
| FX regimes | De facto classifications | 81 | 1940-2021 | IRR |

## Derived data

### Normalized (`data/derived/normalized/`)

| File | Description |
|------|-------------|
| `yearly_unified_panel.csv` | 243 countries, 1500-2025 (MW + CI + GMD with source priority tag) |
| `yearly_unified_wide.csv` | Same, year x country matrix |
| `fred_daily_normalized.csv` | 23 FRED pairs, foreign-per-USD convention |
| `fred_daily_normalized_wide.csv` | Same, date x currency matrix |

### Analysis (`data/derived/analysis/`)

| File | Description |
|------|-------------|
| `daily_log_returns.csv` | Daily log returns, 23 currencies, 271K obs |
| `yearly_log_returns.csv` | Annual log returns, 40 currencies (MeasuringWorth only) |
| `daily_volatility_stats.csv` | Vol, kurtosis, skew, 3-sigma tail counts per currency |
| `yearly_volatility_stats.csv` | Same at annual frequency for 40 countries |
| `daily_rolling_volatility.csv` | 252-day rolling annualized vol, 231K obs |
| `daily_correlation_matrix.csv` | Pairwise Pearson correlations (23x23) |
| `yearly_correlation_matrix.csv` | Pairwise Pearson correlations (min 30 shared years) |
| `yearly_regime_classification.csv` | IRR regime per country-year (194 countries, 1940-2019) |
| `regime_conditional_stats.csv` | Volatility and kurtosis by regime type |
| `yearly_gold_inflation.csv` | Gold inflation, purchasing power, CPI gap (243 countries, 1257-2025) |
| `monthly_gold_inflation.csv` | Monthly gold inflation and debasement (174 currencies, 1940-2025) |

## TODO

### Manual data sources (not yet automatable)

- [ ] **Reinhart-Rogoff official and parallel exchange rates** from [carmenreinhart.com](https://carmenreinhart.com/exchange-rates-official-and-parallel/). Unique dataset with parallel/black-market rates. Requires manual browser download.
- [ ] **Reinhart-Rogoff "This Time Is Different"** crisis dataset from [rogoff.scholars.harvard.edu](https://rogoff.scholars.harvard.edu/time-different%E2%80%94data-files). 66 countries, eight centuries of currency crashes, debasements, sovereign defaults. ~100 individual Excel files per chapter.
- [ ] **MEMDB medieval exchange rates** from [memdb.libraries.rutgers.edu](https://memdb.libraries.rutgers.edu/). Spufford (1106-1500) and Metz (1350-1800). No export API — requires web scraping with pagination.
- [ ] **Global Macro Database** from [globalmacrodata.com](https://www.globalmacrodata.com/data.html). 243 countries, USDfx + REER. Email-gated download. Alternative: `pip install global_macro_data`.
- [ ] **NBER Macrohistory Database** from [nber.org](https://www.nber.org/research/data/nber-macrohistory-xiv-money-and-banking). Pre-WWI and interwar US/UK/France/Germany money, banking, exchange rates. .db/.dat format. Some series on [FRED](https://fred.stlouisfed.org/categories/33061).
- [ ] **Center for Financial Stability** from [centerforfinancialstability.org](https://centerforfinancialstability.org/hfs.php). Exchange rates, central bank balance sheets, interest rates, money supply.

### Pipeline improvements

- [ ] Integrate new sources into `build.py` (PWT, LBMA silver, interest rates, CPI)
- [ ] Add silver purchasing power analysis (parallel to gold inflation)
- [ ] Add real exchange rate computation using CPI data
- [ ] Cross-validate overlapping series (e.g. MeasuringWorth gold vs FreeGoldAPI vs LBMA)

## References

- Denzel, M.A. (2010). *Handbook of World Exchange Rates, 1590-1914*. Ashgate/Routledge.
- Feenstra, R.C., Inklaar, R. & Timmer, M.P. (2015). "The Next Generation of the Penn World Table." *AER*, 105(10), 3150-3182.
- Ilzetzki, E., Reinhart, C.M. & Rogoff, K.S. (2019). "Exchange Arrangements Entering the 21st Century." *QJE*, 134(2), 599-646.
- Jorda, O., Schularick, M. & Taylor, A.M. (2017). "Macrofinancial History and the New Business Cycle Facts." *NBER Macroeconomics Annual*, 31(1), 213-263.
- Metz, R. (1990). *Geld, Wahrung und Preisentwicklung: der Niederrheinraum im europaischen Vergleich, 1350-1800*. Frankfurt.
- Officer, L.H. & Williamson, S.H. *MeasuringWorth*.
- Reinhart, C.M. & Rogoff, K.S. (2009). *This Time Is Different: Eight Centuries of Financial Folly*. Princeton University Press.
- Spufford, P. (1986). *Handbook of Medieval Exchange*. Royal Historical Society.
- Thomas, R. & Dimsdale, N. (2017). "A Millennium of UK Data." Bank of England OBRA dataset.
