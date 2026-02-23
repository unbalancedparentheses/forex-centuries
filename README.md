# forex-centuries

Historical foreign exchange rate data spanning centuries, assembled for volatility research. All data normalized to CSV where possible.

## Datasets

### 1. Clio Infra — Exchange Rates to USD (1500–2013)

Yearly average exchange rates to one unit of US currency for **181 countries**. The longest series are:

| Country        | From |
|----------------|------|
| United Kingdom | 1789 |
| France         | 1792 |
| Netherlands    | 1792 |
| Germany        | 1794 |

Based on Denzel's *Handbook of World Exchange Rates, 1590–1914* and IMF International Financial Statistics. Project led by Jan Luiten van Zanden (Utrecht University / IISH Amsterdam).

- `clio_infra_exchange_rates.csv` — 181 countries, yearly, transposed to year-per-row format
- `clio_infra_exchange_rates_compact.xlsx` — original compact format
- `clio_infra_exchange_rates_broad.xlsx` — includes all 224 countries (many empty)
- [Source](https://clio-infra.eu/Indicators/ExchangeRatestoUSDollar.html)

### 2. MeasuringWorth — Exchange Rates vs USD (1791–2025)

Yearly exchange rates for **41 currencies** vs USD. Compiled by Lawrence H. Officer and Samuel H. Williamson. Highlights:

| Country        | From |
|----------------|------|
| United Kingdom | 1791 |
| Spain          | 1850 |
| South Africa   | 1928 |
| Canada         | 1913 |

- `measuringworth_exchange_rates.csv` — all 41 currencies, year-per-row
- [Source](https://www.measuringworth.com/datasets/exchangeglobal/)

### 3. FRED Daily Exchange Rates (1971–2025)

Daily exchange rates from the Federal Reserve Bank of St. Louis. 11 major currency pairs:

| File               | Pair    | From       |
|--------------------|---------|------------|
| `fred_gbp_usd.csv` | GBP/USD | 1971-01-04 |
| `fred_jpy_usd.csv` | JPY/USD | 1971-01-04 |
| `fred_chf_usd.csv` | CHF/USD | 1971-01-04 |
| `fred_cad_usd.csv` | CAD/USD | 1971-01-04 |
| `fred_aud_usd.csv` | AUD/USD | 1971-01-04 |
| `fred_eur_usd.csv` | EUR/USD | 1999-01-04 |
| `fred_mxn_usd.csv` | MXN/USD | 1993-11-08 |
| `fred_brl_usd.csv` | BRL/USD | 1995-01-02 |
| `fred_cny_usd.csv` | CNY/USD | 1981-01-02 |
| `fred_inr_usd.csv` | INR/USD | 1973-01-02 |
| `fred_krw_usd.csv` | KRW/USD | 1981-04-13 |

- [Source](https://fred.stlouisfed.org/)

### 4. Ilzetzki-Reinhart-Rogoff — Exchange Rate Regimes (1940–2021)

Classification of de facto exchange rate arrangements for ~190 countries. Three datasets:

- `irr_anchor_monthly.xlsx` — anchor currency classification (monthly, 1946–2019). Sheets per anchor: USD, GBP, FRF, DEM, JPY, EUR, Basket
- `irr_regime_monthly.xlsx` — exchange rate regime classification (monthly, 1940–2019). Fine and coarse classifications
- `irr_unified_market.xlsx` — unified vs dual/parallel market indicator (1946–2021). Includes GDP-weighted aggregates
- [Source: Ilzetzki](https://www.ilzetzki.com/irr-data) | [Source: Reinhart](https://carmenreinhart.com/exchange-rate/)

### 5. Clio Infra — Inflation (1500–2010)

Annual inflation rates (percentage change) for 181 countries. Useful for computing real exchange rates.

- `clio_infra_inflation.csv`
- `clio_infra_inflation_compact.xlsx`
- [Source](https://clio-infra.eu/Indicators/Inflation.html)

### 6. Clio Infra — Gold Standard (1800–2010)

Binary indicator of whether a country was on the gold standard. 71 countries. Based on Reinhart & Rogoff.

- `clio_infra_gold_standard.csv`
- `clio_infra_gold_standard_compact.xlsx`
- [Source](https://clio-infra.eu/Indicators/GoldStandard.html)

## Directory Structure

```
data/
├── clio_infra_exchange_rates.csv
├── clio_infra_exchange_rates_compact.xlsx
├── clio_infra_exchange_rates_broad.xlsx
├── clio_infra_inflation.csv
├── clio_infra_inflation_compact.xlsx
├── clio_infra_gold_standard.csv
├── clio_infra_gold_standard_compact.xlsx
├── measuringworth_exchange_rates.csv
├── irr_anchor_monthly.xlsx
├── irr_regime_monthly.xlsx
├── irr_unified_market.xlsx
└── fred_daily/
    ├── fred_gbp_usd.csv
    ├── fred_jpy_usd.csv
    ├── fred_chf_usd.csv
    ├── fred_cad_usd.csv
    ├── fred_aud_usd.csv
    ├── fred_eur_usd.csv
    ├── fred_mxn_usd.csv
    ├── fred_brl_usd.csv
    ├── fred_cny_usd.csv
    ├── fred_inr_usd.csv
    └── fred_krw_usd.csv
```

## TODO

- [ ] Download Reinhart-Rogoff official and parallel exchange rates from [carmenreinhart.com](https://carmenreinhart.com/exchange-rates-official-and-parallel/) (requires manual browser download)
- [ ] Download data from [IISG Historical Prices & Wages Dataverse](https://datasets.iisg.amsterdam/) — exchange rate series going back to the 13th century
- [ ] Add more FRED daily pairs (NOK, SEK, DKK, ZAR, TRY, etc.)
- [ ] Convert IRR xlsx files to CSV
- [ ] Add pre-1590 exchange rates from Denzel and Spufford sources
- [ ] Add BIS effective exchange rate indices
- [ ] Compute log returns and basic volatility measures

## Purpose

Researching exchange rate volatility across centuries — fat tails, regime changes, and structural breaks in currency markets.

## References

- Denzel, M.A. (2010). *Handbook of World Exchange Rates, 1590–1914*. Ashgate/Routledge.
- Ilzetzki, E., Reinhart, C.M. & Rogoff, K.S. (2019). "Exchange Arrangements Entering the 21st Century." *QJE*, 134(2), 599–646.
- Reinhart, C.M. & Rogoff, K.S. (2009). *This Time Is Different: Eight Centuries of Financial Folly*. Princeton University Press.
- Officer, L.H. & Williamson, S.H. *MeasuringWorth*.
