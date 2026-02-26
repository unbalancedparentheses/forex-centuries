# forex-centuries

Historical monetary and economic data spanning twenty centuries (1 CE-2026). 27 sources, 1,100+ files, ~240 countries. Exchange rates, gold, silver, interest rates, CPI, GDP per capita, commodity prices, real wages, sovereign debt, regime classifications, and real effective exchange rates — assembled for long-run volatility and tail-risk research.

Related project: [fatcrash](https://github.com/unbalancedparentheses/fatcrash) — crash detection via fat-tail statistics (LPPLS, EVT, Hill estimator, Kappa).

## Data overview

| Category | What | Countries/Series | Period |
|----------|------|-----------------|--------|
| **GDP per capita** | Real GDP per person | 178 countries | 1 CE - 2022 |
| **Exchange rates** | Bilateral FX vs USD, GBP, and cross rates | ~243 countries | 1106 - 2026 |
| **Gold** | Gold prices in GBP and USD | Global | 1257 - 2025 |
| **Silver** | Silver prices and gold/silver ratio | Global | 1687 - 2025 |
| **Commodity prices** | 973 historical + 70 modern series (wheat, rye, oil, metals, agriculture) | European/Asian cities + global | 1260 - present |
| **Interest rates** | Real and nominal, short and long term | 8 countries (historical), UK+US (nominal) | 1311 - 2025 |
| **Inflation / CPI** | Consumer price indices | ~180 countries | 1500 - 2025 |
| **Real wages** | Labourers' real wage in subsistence ratios | ~40 countries | 1820 - 2000+ |
| **Sovereign debt** | Public debt-to-GDP ratios | 191 countries | 1800 - 2016 |
| **FX regimes & crises** | Peg/float/fall classifications, banking/currency/debt crisis indices | ~190 countries | 1800 - 2021 |
| **Real effective exchange rates** | Trade-weighted, CPI-deflated REER | 178 countries | 1960s - 2026 |
| **Swedish historical macro** | FX, CPI, wages, GDP, money supply, stocks, bonds | Sweden | 1277 - 2026 |
| **Historical financial statistics** | Official/market FX, interest rates, money supply, central bank balance sheets | Various | ~1500 - 1950 |
| **Macroeconomic panel** | 59 variables (FX, CPI, rates, GDP, credit, housing, stocks) | 18 advanced economies | 1870 - 2017 |

Time depth: **2,000+ years** for GDP (Maddison, 1 CE), **900 years** for medieval exchange rates (MEMDB, 1106), **768 years** for gold (MeasuringWorth, 1257), **707 years** for real interest rates (Schmelzing, 1311), **654 years** for commodity prices (Allen-Unger, 1260), **526 years** for exchange rate panels (Clio Infra, 1500), **55 years** for daily FX (FRED, 1971).

## Citation

If you use this dataset in your research, please cite:

```bibtex
@misc{forex-centuries,
  author       = {Federico Carrone},
  title        = {forex-centuries: Twenty Centuries of Exchange Rate, Gold, Silver, Interest Rate, and Commodity Price Data (1 CE--2026)},
  year         = {2025},
  publisher    = {GitHub},
  url          = {https://github.com/unbalancedparentheses/forex-centuries}
}
```

> Federico Carrone, *forex-centuries: Twenty Centuries of Exchange Rate, Gold, Silver, Interest Rate, and Commodity Price Data (1 CE-2026)*, 2025. https://github.com/unbalancedparentheses/forex-centuries

Please also cite the underlying sources relevant to your work (see [Sources](#sources) below).

## Coverage

```
Asset                 0    500   1100   1200   1300   1400   1500   1600   1700   1800   1900   2000
                      :      :      :      :      :      :      :      :      :      :      :      :
EXCHANGE RATES        :      :      :      :      :      :      :      :      :      :      :      :
Medieval FX           :      :      ██████████████████████████████████████████████████████████      :
Clio Infra FX         :      :      :      :      :      :      ████████████████████████████████████████
MeasuringWorth FX     :      :      :      :      :      :      :      :      :      █████████████████
BoE Millennium        :      :      :      :      :      :      :      :      :      ██████████████████
JST Macrohistory      :      :      :      :      :      :      :      :      :      :     ████████████
Riksbank              :      :      :      :      :      :      :      :      :      :       ██████████
Bruegel REER          :      :      :      :      :      :      :      :      :      :          ███████
Penn World Table      :      :      :      :      :      :      :      :      :      :         ████████
BIS                   :      :      :      :      :      :      :      :      :      :            █████
IMF / WB / GMD / FRED :      :      :      :      :      :      :      :      :      :            █████
                      :      :      :      :      :      :      :      :      :      :      :      :
PRECIOUS METALS       :      :      :      :      :      :      :      :      :      :      :      :
Gold (GBP)            :      :      :      █████████████████████████████████████████████████████████████
Gold (USD)            :      :      :      :      :      :      :      :      :      █████████████████
Silver                :      :      :      :      :      :      :      :      ████████████████████████
LBMA Gold+Silver      :      :      :      :      :      :      :      :      :      :      :  ████████
Gold/Silver Ratio     :      :      :      :      :      :      :      :      ████████████████████████
                      :      :      :      :      :      :      :      :      :      :      :      :
COMMODITIES           :      :      :      :      :      :      :      :      :      :      :      :
Allen-Unger (973)     :      :      :      ██████████████████████████████████████████████      :      :
WB Pink Sheet (~70)   :      :      :      :      :      :      :      :      :      :          ███████
                      :      :      :      :      :      :      :      :      :      :      :      :
INTEREST RATES        :      :      :      :      :      :      :      :      :      :      :      :
Schmelzing (8 ctry)   :      :      :      ████████████████████████████████████████████████████████████
UK+US Nominal Rates   :      :      :      :      :      :      :      :      ████████████████████████
                      :      :      :      :      :      :      :      :      :      :      :      :
INFLATION / CPI       :      :      :      :      :      :      :      :      :      :      :      :
US CPI                :      :      :      :      :      :      :      :      :      █████████████████
Clio Infra CPI        :      :      :      :      :      :      ████████████████████████████████████████
                      :      :      :      :      :      :      :      :      :      :      :      :
GDP PER CAPITA        :      :      :      :      :      :      :      :      :      :      :      :
Maddison (178 ctry)   █████████████████████████████████████████████████████████████████████████████████
                      :      :      :      :      :      :      :      :      :      :      :      :
REAL WAGES            :      :      :      :      :      :      :      :      :      :      :      :
Clio Infra Wages      :      :      :      :      :      :      :      :      :      ██████████████████
                      :      :      :      :      :      :      :      :      :      :      :      :
SOVEREIGN DEBT        :      :      :      :      :      :      :      :      :      :      :      :
IMF HPDD (191 ctry)   :      :      :      :      :      :      :      :      :      ██████████████████
Reinhart-Rogoff       :      :      :      :      :      :      :      :      :      ██████████████████
                      :      :      :      :      :      :      :      :      :      :      :      :
REGIMES / CRISES      :      :      :      :      :      :      :      :      :      :      :      :
IRR Classifications   :      :      :      :      :      :      :      :      :      :       █████████
RR Crisis Indices     :      :      :      :      :      :      :      :      :      ██████████████████
                      :      :      :      :      :      :      :      :      :      :      :      :
SWEDEN (1277+)        :      :      :      :      :      :      :      :      :      :      :      :
Riksbank Hist FX      :      :      :      :      :      ██████████████████████████████████████████████
Riksbank Hist CPI     :      :      :      :      :      :      :      :      :      ██████████████████
Riksbank Hist Wages   :      :      :      :      :      :      :      :      :      ██████████████████
                      :      :      :      :      :      :      :      :      :      :      :      :
CFS HIST. FIN. STATS  :      :      :      :      :      :      ████████████████████████████      :
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
make update-sources           # fetch all remote data sources
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

23 sources are automatically fetched by `update_sources.py`. A weekly GitHub Actions workflow runs `--all` every Monday at 06:00 UTC, or trigger it manually from the Actions tab. Each run creates a GitHub Release with a tarball of all data.

```bash
python scripts/update_sources.py --all           # update all 23 sources
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
│   ├── sources/           # Raw data, untouched from provider (27 sources)
│   │   ├── maddison/      # GDP per capita, 178 countries (1 CE - 2022)
│   │   ├── memdb/         # Medieval exchange rates (1106-1800)
│   │   ├── allenunger/    # 973 commodity price series (1260-1914)
│   │   ├── measuringworth/# FX, gold, interest rates, CPI (1257-2025)
│   │   ├── riksbank_hist/ # Swedish FX, CPI, wages, GDP, money supply (1277-2020)
│   │   ├── schmelzing/    # Real interest rates, 8 countries (1311-2018)
│   │   ├── cfs/           # Historical Financial Statistics (FX, rates, money, ~1500-1950)
│   │   ├── clio_infra/    # FX, inflation, bonds, debt, GDP, wages (1500-2016)
│   │   ├── freegold/      # 768-year gold, silver, gold/silver ratio (1258-2025)
│   │   ├── lbma/          # Daily gold + silver prices in USD/GBP/EUR (1968-2025)
│   │   ├── reinhart_rogoff/ # Debt/GDP, inflation, crises, gold standard (1800-2016)
│   │   ├── imf_hpdd/      # Sovereign debt-to-GDP, 191 countries (1800-2015)
│   │   ├── bruegel/       # Real effective exchange rates, 178 countries (1960s-2026)
│   │   ├── imf/           # 173 currencies, monthly (1955-2025)
│   │   ├── bis/           # Bilateral + effective rates, ~190 economies (1957-2026)
│   │   ├── fred/          # 23 daily pairs + 2 USD indices (1971-2025)
│   │   ├── gold/          # Monthly gold prices USD (1833-2025)
│   │   ├── riksbank/      # 53 SEK bilateral series (1900-2026)
│   │   ├── worldbank/     # Official rates, all members (1960-present)
│   │   ├── worldbank_commodities/ # ~70 commodity prices, monthly + annual (1960-present)
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
├── scripts/               # update_sources.py (23 automated fetchers)
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
| [World Bank FX](https://data.worldbank.org/indicator/PA.NUS.FCRF) | `--worldbank` | Official rates, all member countries | 1960-present | |
| [World Bank Commodities](https://www.worldbank.org/en/research/commodity-markets) | `--commodities` | ~70 commodity prices (oil, metals, agriculture), monthly + annual | 1960-present | |
| [JST Macrohistory](https://www.macrohistory.net/database/) | `--jst` | 18 economies, 59 macro/financial variables | 1870-2017 | |
| [Penn World Table](https://www.rug.nl/ggdc/productivity/pwt/) | `--pwt` | 185 countries, exchange rates + PPP | 1950-2023 | |
| [MeasuringWorth](https://www.measuringworth.com/datasets/) | `--measuringworth` | 41 FX vs USD, gold (5 series), interest rates (UK+US), US CPI, $/£ | 1257-2025 | |
| [Clio Infra](https://clio-infra.eu/) | `--clio` | FX (USD+GBP), inflation, bonds, debt, GDP, gold standard, real wages | 1500-2016 | |
| [FreeGoldAPI](https://freegoldapi.com/) | `--freegold` | 768-year gold prices, gold/silver ratio, silver prices | 1258-2025 | |
| [LBMA](https://www.lbma.org.uk/prices-and-data/precious-metal-prices) | `--lbma` | Daily gold + silver in USD, GBP, EUR | 1968-2025 | |
| [DataHub Gold](https://github.com/datasets/gold-prices) | `--gold` | Monthly gold prices USD | 1833-2025 | |
| [IRR](https://www.ilzetzki.com/irr-data) | `--irr` | De facto FX regime classifications, ~190 countries | 1940-2021 | |
| [Bank of England](https://www.bankofengland.co.uk/statistics/research-datasets) | `--boe` | UK millennium dataset ($/£, rates, prices, GDP) | 1791-2016 | |
| [Schmelzing (BoE)](https://www.bankofengland.co.uk/working-paper/2020/eight-centuries-of-global-real-interest-rates-r-g-and-the-suprasecular-decline-1311-2018) | `--schmelzing` | Real interest rates, 8 countries (IT, UK, NL, DE, FR, ES, JP, US) | 1311-2018 | |
| [Maddison Project](https://www.rug.nl/ggdc/historicaldevelopment/maddison/) | `--maddison` | GDP per capita, 178 countries (via OWID API + Dataverse xlsx) | 1 CE-2022 | |
| [Allen-Unger GCPD](https://datasets.iisg.amsterdam/dataset.xhtml?persistentId=hdl:10622/3SV0BO) | `--allenunger` | 973 commodity price series (wheat, rye, silver, etc.) across cities | 1260-1914 | |
| [Bruegel/Darvas REER](https://www.bruegel.org/publications/datasets/real-effective-exchange-rates-for-178-countries-a-new-database) | `--bruegel` | Real effective exchange rates, 178 countries, monthly | 1960s-2026 | |
| [IMF HPDD](https://data.imf.org/) | `--imfhpdd` | Sovereign debt-to-GDP, 191 countries (via DBnomics) | 1800-2015 | |
| [CFS HFS](https://centerforfinancialstability.org/hfs.php) | `--cfs` | Exchange rates, interest rates, money supply, central bank balance sheets | ~1500-1950 | |
| [Riksbank Hist. Monetary](https://www.riksbank.se/en-gb/statistics/historical-monetary-statistics-of-sweden/) | `--riksbank_hist` | Swedish FX, CPI, wages, GDP, money supply, stocks/bonds (Vols I-III) | 1277-2020 | |
| [Reinhart-Rogoff](https://carmenreinhart.com/data/) | `--reinhartrogoff` | Regime classifications, debt/GDP, inflation, crisis indices, gold standard dates | 1800-2016 | |

### Static (committed to repo, updated manually)

| Source | Data | Period | Notes |
|--------|------|--------|-------|
| [MEMDB Spufford](https://memdb.libraries.rutgers.edu/spufford-currency) | Medieval exchange quotations (521 places) | 1106-1500 | No export API |
| [MEMDB Metz](https://memdb.libraries.rutgers.edu/metz-currency) | Lower Rhine + European comparison (29 places) | 1350-1800 | No export API |
| [Global Macro Database](https://www.globalmacrodata.com/data.html) | 243 countries, USDfx + REER | 1960-2024 | Email-gated |

## Longest series by asset type

| Asset | Series | Years | Period | Source |
|-------|--------|------:|--------|--------|
| GDP per capita | 178 countries | 2,021 | 1 CE-2022 | Maddison Project |
| Gold | British official price (GBP/oz) | 768 | 1257-2025 | MeasuringWorth |
| Gold | USD price per oz | 767 | 1258-2025 | FreeGoldAPI |
| Interest rates | Real rates, 8 countries | 707 | 1311-2018 | Schmelzing (BoE) |
| Medieval FX | European exchange quotations | 694 | 1106-1800 | MEMDB |
| Commodity prices | 973 series across European/Asian cities | 654 | 1260-1914 | Allen-Unger |
| Exchange rates | 186 countries vs GBP | 516 | 1500-2016 | Clio Infra |
| Silver | Silver-normalized prices | 337 | 1688-2025 | FreeGoldAPI |
| Gold/silver ratio | Annual ratio | 338 | 1687-2025 | MeasuringWorth |
| Interest rates | UK+US nominal short + long term | 296 | 1729-2025 | MeasuringWorth |
| US CPI | Consumer price index | 251 | 1774-2025 | MeasuringWorth |
| 41 FX vs USD | Annual rates | 234 | 1791-2025 | MeasuringWorth |
| REER | 178 countries, monthly | ~66 | 1960s-2026 | Bruegel/Darvas |
| Commodities | ~70 series (oil, metals, agriculture) | ~66 | 1960-present | World Bank |
| Real wages | Labourers' real wage, ~40 countries | ~180 | 1820-2000+ | Clio Infra |
| Swedish FX | Exchange rates from 1534 | 492 | 1534-2026 | Riksbank Hist. |
| Sovereign debt | Debt-to-GDP, 191 countries | 215 | 1800-2015 | IMF HPDD |
| Crisis indices | Banking/currency/debt crises | ~216 | 1800-2016 | Reinhart-Rogoff |
| FX regimes | De facto classifications | 81 | 1940-2021 | IRR |
| CFS FX/rates | Official + market exchange rates, interest rates | ~450 | ~1500-1950 | CFS |

## Source data schemas

### `sources/memdb/`

**`memdb_spufford_medieval_exchange_rates.csv`** (13,197 rows) — Place, Date_start, Date_end, Type_of_Exchange, Currency_From, Amount_From, Currency_To, Amount_To, Notes, Source.

**`memdb_metz_currency_exchanges.csv`** (50,559 rows) — Place, Year, Coin_Ratio, Relationship, Value, Length_of_Series, Note.

### `sources/clio_infra/`

All Clio Infra files share the same wide format: first column is `year`, remaining columns are country names. Values are yearly averages.

| File | Unit | Period |
|------|------|--------|
| `clio_infra_exchange_rates.csv` | Local currency per 1 USD | 1500-2013 |
| `clio_infra_exchange_rates_gbp.csv` | Local currency per 1 GBP | 1500-2013 |
| `clio_infra_inflation.csv` | Annual % change | 1500-2010 |
| `clio_infra_gold_standard.csv` | 0/1 indicator | 1800-2010 |
| `clio_infra_bond_yield.csv` | Annual avg % | 1727-2011 |
| `clio_infra_govt_debt.csv` | % of GDP | 1692-2010 |
| `clio_infra_gdp_per_capita_compact.xlsx` | 1990 Int'l GK dollars | 1500-2016 |
| `clio_infra_real_wages_compact.xlsx` | Subsistence ratios | 1820-2000+ |

### `sources/measuringworth/`

**`measuringworth_exchange_rates.csv`** — Wide format: `year` + 41 country columns. Values are foreign currency per 1 USD.

**`measuringworth_gold_prices.csv`** (769 rows) — year, British_price (GBP/oz, 1257-1945), london_price (GBP then USD), us_price (USD/oz, 1786-2025), newyork_price (USD/oz, 1791-2025), goldsilver_price (ratio, 1687-2025).

**`measuringworth_interest_rates.csv`** — UK+US short and long term rates, 1729-2025.

**`measuringworth_us_cpi.csv`** — US CPI index (avg 1982-84=100), 1774-2025.

**`measuringworth_dollar_pound.csv`** — USD per GBP, 1791-2025.

### `sources/gold/`

**`gold_monthly_usd.csv`** — Date (YYYY-MM), Price (USD/troy oz). 1833-2025.

### `sources/imf/`

**`imf_exchange_rates.csv`** (158K rows) — Date, Rate (LCU per USD), Currency, Frequency (M), Source, Country code, Country.

### `sources/bis/`

BIS SDMX flat CSV format. `xru/WS_XRU_csv_flat.csv.gz` (1.5M rows): bilateral rates vs USD. `eer/WS_EER_csv_flat.csv.gz` (1.2M rows): nominal+real effective rates (2020=100).

### `sources/fred/`

25 CSVs in `daily/`. Two columns: observation_date, rate. GBP/EUR/AUD/NZD quoted as USD-per-foreign; all others as foreign-per-USD. Missing values shown as `.`.

### `sources/riksbank/`

**`riksbank_exchange_rates.csv`** (295K rows) — date, series_id (`SEK[CURRENCY]PMI`), value.

### `sources/worldbank/`

**`worldbank_exchange_rates.csv`** — iso3, country, year, exchange_rate (LCU per USD). Via World Bank API.

### `sources/worldbank_commodities/`

**`wb_commodity_prices_monthly.xlsx`** and **`wb_commodity_prices_annual.xlsx`** — ~70 commodities (crude oil Brent/WTI/Dubai, natural gas, coal, metals, agriculture) from the World Bank "Pink Sheet". 1960-present.

### `sources/irr/`

Ilzetzki-Reinhart-Rogoff regime classifications. Rows are months (YYYY:MM), columns are countries. `irr_regime_coarse.csv` (1=peg to 6=dual market), `irr_regime_fine.csv` (1-15 scale), `irr_anchor_master.csv` (anchor currency), `irr_unified_market_indicator.csv` (0=unified, 1=parallel).

### `sources/jst/`

**`jst_macrohistory.xlsx`** (2,719 rows, 59 cols) — Long format, one row per country-year. Key columns: year, country, iso, xrusd, cpi, stir, ltrate, peg, crisisJST. 18 countries, 1870-2017.

### `sources/boe/`

**`boe_millennium.xlsx`** (26 MB, 90+ sheets) — UK data. Key sheets: A33 ($/£ from 1791), M14 (monthly bilateral rates 1963+), M15 (monthly $/£ 1791-2015), A31 (interest rates), D1 (daily Bank Rate).

### `sources/gmd/`

**`gmd_exchange_rates.csv`** (57K rows) — ISO3, countryname, year, USDfx (LCU per USD), REER.

### `sources/freegold/`

**`freegold_prices.csv`** — date, price. Gold prices 1258-2025 (GBP before 1791, USD after). **`freegold_silver_prices.csv`** — Silver prices 1688-2025. **`freegold_gold_silver_ratio.csv`** — Gold/silver ratio 1258-2025.

### `sources/lbma/`

**`lbma_gold_daily.csv`** (14.5K rows) — date, gold_pm_usd, gold_pm_gbp, gold_pm_eur. Daily PM fix from 1968. **`lbma_silver_daily.csv`** (14.7K rows) — Same for silver.

### `sources/schmelzing/`

**`schmelzing_real_interest_rates.xlsx`** (2.1 MB, 9 sheets) — Real interest rates 1311-2018 for Italy, UK, Netherlands, Germany, France, Spain, Japan, US. Key sheet: "II. Headline series" (719 rows x 35 cols).

### `sources/maddison/`

**`maddison_gdp_per_capita.csv`** (21.6K rows) — entity_code, entity_name, year, gdp_per_capita. 178 countries, 1 CE-2022. Via OWID API (Maddison Project Database 2023).

### `sources/allenunger/`

973 tab-delimited files, one per city-commodity pair (e.g. `Amsterdam_Wheat.tab`, `London_Coal.tab`). Columns: Commodity, Variety, Market, Original Measure, Standard Measure, Original Currency, Standard Currency, Year, Original Value, Standardized Value, Notes, Sources. Prices standardized to silver grams per litre. 1260-1914.

### `sources/pwt/`

**`pwt.xlsx`** (6.3 MB) — Penn World Table 10.0/11.0. 185 countries, 1950-2023. Key variables: xr (exchange rate), pl_gdpo (price level of GDP), rgdpe (real GDP).

### `sources/bruegel/`

**`REER_database_ver*.xls`** (9 MB) — Darvas/Bruegel real effective exchange rates. 178 countries, monthly, various start dates (many from 1960s). Nominal and CPI-based REER indices.

### `sources/imf_hpdd/`

**`imf_hpdd_debt_gdp.csv`** (9.6K rows) — country, indicator, year, value. Gross government debt as % of GDP, 191 countries, 1800-2015. Via DBnomics mirror of IMF HPDD.

### `sources/cfs/`

Center for Financial Stability Historical Financial Statistics. 8 files (~31 MB total). Key files: `cfs_official_exchange_rates.xlsb` (daily official FX rates), `cfs_market_exchange_rates.xlsb` (daily/monthly market FX), `cfs_interest_rates.xlsb` (interest rates), `cfs_general_tables.xlsx` (summary tables). Coverage: ~1500-1950. Note: `.xlsb` files require `pyxlsb` library to read.

### `sources/riksbank_hist/`

Riksbank Historical Monetary Statistics, 13 Excel files across 3 volumes. Vol I (1277-2008): exchange rates, CPI, wages. Vol II (1620-2012): GDP, stocks/bonds, money supply, Riksbank balance sheet. Vol III (1420-2020): bonds. Key files: `vol1_ch3_middle_ages.xls` (earliest data, from 1277), `vol1_ch4_exchange_rates_1534_1803.xls`, `vol1_ch8_cpi.xls`.

### `sources/reinhart_rogoff/`

12 Excel files from Reinhart & Rogoff. Key files: `rr_regime_classification.xlsx` (FX regime, annual), `rr_anchor_currency_1946_2016.xlsx` (anchor currency), `rr_total_public_debt_gdp.xls` (debt/GDP), `rr_inflation_annual.xls`, `rr_bcdi_crisis_index.xls` (banking/currency/debt/inflation crisis indicator), `rr_gold_standard_dates.xlsx`. Coverage: ~1800-2016, ~70 countries.

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

- [ ] **Reinhart-Rogoff parallel/black-market exchange rates** from [carmenreinhart.com](https://carmenreinhart.com/exchange-rates-official-and-parallel/). Unique dataset — links broken from site migration, requires manual browser download.
- [ ] **Energy Institute Statistical Review** from [energyinst.org](https://www.energyinst.org/statistical-review). Oil prices from 1861. Cloudflare-blocked — requires browser download.
- [ ] **MEMDB medieval exchange rates** from [memdb.libraries.rutgers.edu](https://memdb.libraries.rutgers.edu/). Spufford (1106-1500) and Metz (1350-1800). No export API — requires web scraping.
- [ ] **Global Macro Database** from [globalmacrodata.com](https://www.globalmacrodata.com/data.html). 243 countries, USDfx + REER. Email-gated download.
- [ ] **NBER Macrohistory Database** from [nber.org](https://www.nber.org/research/data/nber-macrohistory-database). 2,510 series of pre-WWI/interwar data. Available via FRED individual series or NBER directory scrape.

### Pipeline improvements

- [ ] Integrate new sources into `build.py` (Schmelzing, Maddison, Allen-Unger, Bruegel REER, WB commodities, PWT, LBMA silver, interest rates, CPI, real wages)
- [ ] Add silver purchasing power analysis (parallel to gold inflation)
- [ ] Add real exchange rate computation using CPI and Bruegel REER data
- [ ] Cross-validate overlapping series (e.g. MeasuringWorth gold vs FreeGoldAPI vs LBMA)

## References

- Allen, R.C. & Unger, R.W. "Global Commodity Prices Database." International Institute of Social History.
- Bolt, J. & van Zanden, J.L. (2024). "Maddison style estimates of the evolution of the world economy. A new 2023 update." *Journal of Economic Surveys*, 38(4), 1507-1545.
- Clark, G. "What Were the UK Earnings and Prices Then?" *MeasuringWorth*.
- Darvas, Z. (2012). "Real effective exchange rates for 178 countries: A new database." Bruegel Working Paper 2012/06.
- Denzel, M.A. (2010). *Handbook of World Exchange Rates, 1590-1914*. Ashgate/Routledge.
- Feenstra, R.C., Inklaar, R. & Timmer, M.P. (2015). "The Next Generation of the Penn World Table." *AER*, 105(10), 3150-3182.
- Ilzetzki, E., Reinhart, C.M. & Rogoff, K.S. (2019). "Exchange Arrangements Entering the 21st Century." *QJE*, 134(2), 599-646.
- Jorda, O., Schularick, M. & Taylor, A.M. (2017). "Macrofinancial History and the New Business Cycle Facts." *NBER Macroeconomics Annual*, 31(1), 213-263.
- Metz, R. (1990). *Geld, Wahrung und Preisentwicklung: der Niederrheinraum im europaischen Vergleich, 1350-1800*. Frankfurt.
- Officer, L.H. "What Was the Interest Rate Then?" *MeasuringWorth*.
- Officer, L.H. "Dollar-Pound Exchange Rate From 1791." *MeasuringWorth*.
- Officer, L.H. & Williamson, S.H. "The Price of Gold, 1257-Present." *MeasuringWorth*.
- Officer, L.H. & Williamson, S.H. "The Annual Consumer Price Index for the United States, 1774-Present." *MeasuringWorth*.
- Reinhart, C.M. & Rogoff, K.S. (2009). *This Time Is Different: Eight Centuries of Financial Folly*. Princeton University Press.
- Schmelzing, P. (2020). "Eight centuries of global real interest rates, R-G, and the 'suprasecular' decline, 1311-2018." *Bank of England Staff Working Paper No. 845*.
- Spufford, P. (1986). *Handbook of Medieval Exchange*. Royal Historical Society.
- Thomas, R. & Dimsdale, N. (2017). "A Millennium of UK Data." Bank of England OBRA dataset.
