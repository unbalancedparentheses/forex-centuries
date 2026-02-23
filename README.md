# forex-centuries

Historical foreign exchange rate data spanning nine centuries (1106–2026), assembled for volatility research. 57 files, 850 MB.

## Datasets

### Medieval Exchange Rates (1106–1800)

#### MEMDB Spufford — Medieval Currency Exchanges (1106–1500)
13,197 exchange rate quotations from Peter Spufford's *Handbook of Medieval Exchange*. Covers all of Europe, Byzantium, the Levant, and North Africa. Silver penny coinages and early gold coinages.

- `memdb_spufford_medieval_exchange_rates.csv` — columns: Place, Date_start, Date_end, Type_of_Exchange, Currency_From, Amount_From, Currency_To, Amount_To, Notes, Source
- Scraped from [MEMDB at Rutgers](https://memdb.libraries.rutgers.edu/spufford-currency)

#### MEMDB Metz — Currency Exchanges (1350–1800)
50,559 records from Rainer Metz, *Geld, Währung und Preisentwicklung*. Covers the Lower Rhine region and broader European comparison. Bridges medieval and modern eras.

- `memdb_metz_currency_exchanges.csv` — columns: Place, Year, Coin_Ratio, Relationship, Value, Length_of_Series, Note
- Scraped from [MEMDB at Rutgers](https://memdb.libraries.rutgers.edu/metz-currency)

### Yearly Exchange Rates (1500–2025)

#### Clio Infra — Exchange Rates to USD (1500–2013)
181 countries, yearly averages. Longest: UK (1789), France/Netherlands (1792), Germany (1794). Based on Denzel's *Handbook* and IMF IFS.

- `clio_infra_exchange_rates.csv` + `.xlsx` variants
- [Source](https://clio-infra.eu/Indicators/ExchangeRatestoUSDollar.html)

#### Clio Infra — Exchange Rates to GBP (1500–2013)
Same structure, vs the British Pound — the pre-20th-century global reserve currency.

- `clio_infra_exchange_rates_gbp.csv` + `.xlsx`
- [Source](https://clio-infra.eu/Indicators/ExchangeRatestoUKPound.html)

#### MeasuringWorth — Exchange Rates vs USD (1791–2025)
41 currencies. UK from 1791, Spain from 1850, many European currencies from 1913.

- `measuringworth_exchange_rates.csv`
- [Source](https://www.measuringworth.com/datasets/exchangeglobal/)

#### Global Macro Database (1960–2024)
243 countries, harmonized from 111 data sources. Includes USD exchange rates and Real Effective Exchange Rates.

- `gmd_exchange_rates.csv` — columns: ISO3, countryname, year, USDfx, REER
- [Source](https://www.globalmacrodata.com/data.html)

#### World Bank — Official Exchange Rates (1960–present)
Official exchange rate (LCU per US$, period average) for all member countries.

- `worldbank_exchange_rates.xls`
- [Source](https://data.worldbank.org/indicator/PA.NUS.FCRF)

### Monthly Exchange Rates (1940–2026)

#### IMF IFS — Exchange Rates (1955–2025)
168 currencies vs USD, monthly. 158,518 observations.

- `imf_exchange_rates.csv`
- [Source](https://github.com/codeforIATI/imf-exchangerates)

#### BIS — Bilateral Exchange Rates vs USD (1957–2026)
**1.47 million rows.** ~190 economies, daily/monthly/quarterly/annual. 14 currencies back to 1950.

- `bis_xru/WS_XRU_csv_flat.csv` (423 MB)
- [Source](https://data.bis.org/topics/XRU)

#### BIS — Effective Exchange Rates (1964–2026)
**1.19 million rows.** Nominal and real effective exchange rates (NEER/REER) for 64 economies.

- `bis_eer/WS_EER_csv_flat.csv` (277 MB)
- [Source](https://data.bis.org/topics/EER)

#### Sveriges Riksbank (1900–2026)
28 SEK bilateral exchange rate series (daily) plus the trade-weighted SEK index from 1900. 162,314 total observations.

- `riksbank_exchange_rates.csv`
- [Source](https://www.riksbank.se/en-gb/statistics/)

### Daily Exchange Rates (1971–2026)

#### FRED — 23 Currency Pairs + 2 Dollar Indices
Daily from the Federal Reserve H.10 release. See `fred_daily/` for all files.

Major pairs: GBP, JPY, CHF, CAD, AUD, EUR, DKK, MYR, NOK, NZD, SEK, MXN, BRL, CNY, INR, KRW, HKD, ZAR, SGD, LKR, TWD, THB, VEF vs USD. Plus Broad and Major dollar indices.

- [Source](https://fred.stlouisfed.org/)

### Macro-Historical Databases

#### Jorda-Schularick-Taylor (1870–2017)
18 advanced economies, 59 variables including exchange rates (`xrusd`), interest rates, GDP, credit, housing prices, crisis indicators.

- `jst_macrohistory.xlsx`
- [Source](https://www.macrohistory.net/database/)

#### Bank of England — A Millennium of Macroeconomic Data
$/£ from 1791, monthly bilateral rates from 1963, effective exchange rates. Plus interest rates, prices, wages, GDP back to the 13th century.

- `boe_millennium.xlsx` (26 MB)
- [Source](https://www.bankofengland.co.uk/statistics/research-datasets)

### Exchange Rate Regime Classifications (1940–2021)

#### Ilzetzki-Reinhart-Rogoff
De facto exchange rate arrangements for ~190 countries.

- `irr_regime_coarse.csv` / `irr_regime_fine.csv` — regime classifications (monthly, 1940–2019)
- `irr_anchor_master.csv` — anchor currency (monthly, 1946–2019)
- `irr_unified_market_indicator.csv` — unified vs dual/parallel market (1946–2021)
- Original `.xlsx` files also included
- [Source: Ilzetzki](https://www.ilzetzki.com/irr-data) | [Source: Reinhart](https://carmenreinhart.com/exchange-rate/)

### Supporting Macro Variables

| File | Variable | Period | Countries |
|------|----------|--------|-----------|
| `clio_infra_inflation.csv` | Inflation (annual %) | 1500–2010 | 181 |
| `clio_infra_gold_standard.csv` | Gold standard (binary) | 1800–2010 | 71 |
| `clio_infra_bond_yield.csv` | Long-term govt bond yield | 1727–2011 | 42 |
| `clio_infra_govt_debt.csv` | Govt debt (% GDP) | 1692–2010 | 86 |
| `clio_infra_gdp_per_capita_compact.xlsx` | GDP per capita (Maddison) | 1500–2016 | 181 |

## Data Coherence

Cross-validation between overlapping datasets:

- **MeasuringWorth vs Clio Infra**: Excellent agreement for stable currencies. Divergences only from currency redenominations (Brazil, Mexico, Argentina), Euro-era switchover (France, Germany, Netherlands post-1999), and quoting conventions (Australia, South Africa).
- **FRED daily vs MeasuringWorth**: JPY/USD perfect match (0.00–0.12% diff). GBP/USD exact inverses (different quoting convention — USD per GBP vs GBP per USD).
- **All datasets coherent.** Differences explained by quoting conventions and redenomination tracking.

## TODO

- [ ] Reinhart-Rogoff official and parallel exchange rates from [carmenreinhart.com](https://carmenreinhart.com/exchange-rates-official-and-parallel/) (requires manual browser download — JavaScript-rendered link)
- [ ] Remaining Riksbank series (~17 still rate-limited)
- [ ] Normalize all series to common quoting convention (foreign currency per USD)
- [ ] Compute log returns and basic volatility measures

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
