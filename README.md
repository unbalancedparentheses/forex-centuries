# forex-centuries

Historical foreign exchange rate data spanning centuries, assembled for volatility research. All data normalized to CSV where possible.

## Datasets

### 1. Clio Infra — Exchange Rates to USD (1500–2013)

Yearly average exchange rates to one unit of US currency for **181 countries**. Longest series: UK (1789), France/Netherlands (1792), Germany (1794).

Based on Denzel's *Handbook of World Exchange Rates, 1590–1914* and IMF IFS. Project led by Jan Luiten van Zanden (Utrecht / IISH Amsterdam).

- `clio_infra_exchange_rates.csv` — 181 countries, yearly, year-per-row
- `clio_infra_exchange_rates_compact.xlsx` / `_broad.xlsx` — original formats
- [Source](https://clio-infra.eu/Indicators/ExchangeRatestoUSDollar.html)

### 2. Clio Infra — Exchange Rates to GBP (1500–2013)

Same structure as above but vs the British Pound — **the key pre-20th-century reserve currency**. Starts earlier than USD series for many countries since GBP was the global reference currency.

- `clio_infra_exchange_rates_gbp.csv` — 181 countries, yearly
- `clio_infra_exchange_rates_gbp_compact.xlsx`
- [Source](https://clio-infra.eu/Indicators/ExchangeRatestoUKPound.html)

### 3. MeasuringWorth — Exchange Rates vs USD (1791–2025)

Yearly exchange rates for **41 currencies** vs USD. Compiled by Lawrence H. Officer and Samuel H. Williamson. UK from 1791, Spain from 1850, many European currencies from 1913.

- `measuringworth_exchange_rates.csv` — all 41 currencies, year-per-row
- [Source](https://www.measuringworth.com/datasets/exchangeglobal/)

### 4. IMF IFS — Exchange Rates (1955–2025)

Monthly exchange rates for **168 currencies** vs USD from the IMF International Financial Statistics, pre-processed by codeforIATI. 158,518 observations.

- `imf_exchange_rates.csv` — columns: Date, Rate, Currency, Frequency, Source, Country code, Country
- [Source](https://github.com/codeforIATI/imf-exchangerates)

### 5. World Bank — Official Exchange Rates (1960–present)

Official exchange rate (LCU per US$, period average) for all World Bank member countries.

- `worldbank_exchange_rates.xls`
- [Source](https://data.worldbank.org/indicator/PA.NUS.FCRF)

### 6. FRED Daily Exchange Rates (1971–2025)

Daily exchange rates from the Federal Reserve H.10 release. **23 currency pairs** + 2 dollar indices:

| File | Pair | From |
|------|------|------|
| `fred_gbp_usd.csv` | GBP/USD | 1971-01-04 |
| `fred_jpy_usd.csv` | JPY/USD | 1971-01-04 |
| `fred_chf_usd.csv` | CHF/USD | 1971-01-04 |
| `fred_cad_usd.csv` | CAD/USD | 1971-01-04 |
| `fred_aud_usd.csv` | AUD/USD | 1971-01-04 |
| `fred_dkk_usd.csv` | DKK/USD | 1971-01-04 |
| `fred_myr_usd.csv` | MYR/USD | 1971-01-04 |
| `fred_nok_usd.csv` | NOK/USD | 1971-01-04 |
| `fred_nzd_usd.csv` | NZD/USD | 1971-01-04 |
| `fred_sek_usd.csv` | SEK/USD | 1971-01-04 |
| `fred_eur_usd.csv` | EUR/USD | 1999-01-04 |
| `fred_mxn_usd.csv` | MXN/USD | 1993-11-08 |
| `fred_brl_usd.csv` | BRL/USD | 1995-01-02 |
| `fred_cny_usd.csv` | CNY/USD | 1981-01-02 |
| `fred_inr_usd.csv` | INR/USD | 1973-01-02 |
| `fred_krw_usd.csv` | KRW/USD | 1981-04-13 |
| `fred_hkd_usd.csv` | HKD/USD | 1981-01-02 |
| `fred_zar_usd.csv` | ZAR/USD | 1980-01-02 |
| `fred_sgd_usd.csv` | SGD/USD | 1981-01-02 |
| `fred_lkr_usd.csv` | LKR/USD | 1973-01-02 |
| `fred_twd_usd.csv` | TWD/USD | 1983-10-03 |
| `fred_thb_usd.csv` | THB/USD | 1981-01-02 |
| `fred_vef_usd.csv` | VEF/USD | 2000-01-03 |
| `fred_usd_broad_index.csv` | USD Broad Index | 2006-01-02 |
| `fred_usd_major_index.csv` | USD Major Index | 1973-01-02 |

- [Source](https://fred.stlouisfed.org/)

### 7. Jorda-Schularick-Taylor Macrohistory Database (1870–2017)

Annual data for **18 advanced economies** with 59 variables including exchange rates (`xrusd`), interest rates, GDP, credit, housing prices, and crisis indicators.

Countries: AUS, BEL, CAN, DNK, FIN, FRA, DEU, ITA, JPN, NLD, NOR, PRT, ESP, SWE, CHE, GBR, USA + more.

- `jst_macrohistory.xlsx`
- [Source](https://www.macrohistory.net/database/)

### 8. Bank of England — A Millennium of Macroeconomic Data

UK-focused dataset with $/£ exchange rate from **1791**, monthly bilateral rates from **1963**, plus interest rates, prices, wages, GDP back to the 13th century. Sheet `A33. Exchange rate data` has nominal and real $/£ rates plus effective exchange rate indices.

- `boe_millennium.xlsx` (26 MB, many sheets)
- [Source](https://www.bankofengland.co.uk/statistics/research-datasets)

### 9. Ilzetzki-Reinhart-Rogoff — Exchange Rate Regimes (1940–2021)

Classification of de facto exchange rate arrangements for ~190 countries:

- `irr_anchor_monthly.xlsx` — anchor currency classification (monthly, 1946–2019)
- `irr_regime_monthly.xlsx` — regime classification (monthly, 1940–2019)
- `irr_unified_market.xlsx` — unified vs dual/parallel market indicator (1946–2021)
- [Source: Ilzetzki](https://www.ilzetzki.com/irr-data) | [Source: Reinhart](https://carmenreinhart.com/exchange-rate/)

### 10. Clio Infra — Supporting Macro Variables

Additional datasets useful for understanding exchange rate dynamics:

| File | Variable | Period | Countries |
|------|----------|--------|-----------|
| `clio_infra_inflation.csv` | Inflation (annual %) | 1500–2010 | 181 |
| `clio_infra_gold_standard.csv` | Gold standard (binary) | 1800–2010 | 71 |
| `clio_infra_bond_yield.csv` | Long-term govt bond yield | 1727–2011 | 42 |
| `clio_infra_govt_debt.csv` | Govt debt (% GDP) | 1692–2010 | 86 |
| `clio_infra_gdp_per_capita_compact.xlsx` | GDP per capita (Maddison) | 1500–2016 | 181 |

## Data Coherence

Cross-validation between overlapping datasets shows:

**MeasuringWorth vs Clio Infra (yearly):** Excellent agreement for stable currencies (UK, Canada, Japan, Switzerland, Scandinavia — ratios within 0.1% of 1.0). Systematic divergences in three cases:
- **Currency redenominations**: Brazil, Mexico, Argentina show factor-of-1000 differences in certain periods — Clio Infra tracks the "new" currency unit post-redenomination while MeasuringWorth tracks the old. Both are correct, different conventions.
- **Euro-era**: France, Germany, Netherlands post-1999 — Clio Infra switches to EUR while MeasuringWorth continues reporting legacy currency rates. Both valid.
- **Quoting convention**: South Africa (1953) and Australia (1960) show ~2x ratios, consistent with a per-pound vs per-dollar quoting change.

**FRED daily vs MeasuringWorth (annual avg):**
- **JPY/USD**: Perfect match (0.00–0.12% difference across all years)
- **GBP/USD**: 100% mismatch — FRED quotes USD per GBP (e.g., 2.44), MeasuringWorth quotes GBP per USD (e.g., 0.41). These are exact inverses.

**Conclusion:** All datasets are coherent. Differences are explained by quoting conventions (USD per foreign vs foreign per USD) and currency redenomination tracking. Users should verify quoting direction before combining series.

## TODO

- [ ] Download Reinhart-Rogoff official and parallel exchange rates from [carmenreinhart.com](https://carmenreinhart.com/exchange-rates-official-and-parallel/) (requires manual browser download)
- [ ] Download MEMDB Spufford medieval exchange rates (1106–1500) from [Rutgers](https://memdb.libraries.rutgers.edu/spufford-currency)
- [ ] Download MEMDB Metz currency exchanges (1350–1800) from [Rutgers](https://memdb.libraries.rutgers.edu/metz-currency)
- [ ] Download BIS effective exchange rates (bulk CSV blocked programmatically, try via [data portal](https://data.bis.org/topics/EER))
- [ ] Download Sveriges Riksbank historical rates (1277–2008) from [riksbank.se](https://www.riksbank.se/en-gb/statistics/)
- [ ] Download Global Macro Database from [globalmacrodata.com](https://www.globalmacrodata.com/data.html) (243 countries, 1086–2024)
- [ ] Convert IRR xlsx files to CSV
- [ ] Compute log returns and basic volatility measures
- [ ] Normalize all series to common quoting convention (foreign currency per USD)

## Purpose

Researching exchange rate volatility across centuries — fat tails, regime changes, and structural breaks in currency markets.

## References

- Denzel, M.A. (2010). *Handbook of World Exchange Rates, 1590–1914*. Ashgate/Routledge.
- Ilzetzki, E., Reinhart, C.M. & Rogoff, K.S. (2019). "Exchange Arrangements Entering the 21st Century." *QJE*, 134(2), 599–646.
- Jorda, O., Schularick, M. & Taylor, A.M. (2017). "Macrofinancial History and the New Business Cycle Facts." *NBER Macroeconomics Annual*, 31(1), 213–263.
- Officer, L.H. & Williamson, S.H. *MeasuringWorth*.
- Reinhart, C.M. & Rogoff, K.S. (2009). *This Time Is Different: Eight Centuries of Financial Folly*. Princeton University Press.
- Spufford, P. (1986). *Handbook of Medieval Exchange*. Royal Historical Society.
- Thomas, R. & Dimsdale, N. (2017). "A Millennium of UK Data." Bank of England OBRA dataset.
