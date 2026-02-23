# forex-centuries

Historical foreign exchange rate data spanning centuries, gathered for volatility research.

## Data Sources

### Clio Infra — Exchange Rates to USD (1500–2050)
- **181 countries**, yearly averages
- Oldest series: UK (1789), France/Netherlands (1792), Germany (1794)
- Based on Denzel's *Handbook of World Exchange Rates, 1590–1914* and IMF IFS
- [Source](https://clio-infra.eu/Indicators/ExchangeRatestoUSDollar.html)

### Clio Infra — Inflation (1500–2010)
- 16,676 observations across all continents
- Annual percentage change
- [Source](https://clio-infra.eu/Indicators/Inflation.html)

### Clio Infra — Gold Standard (1800–2010)
- Binary variable: whether a country was on gold standard per year
- 71 countries, based on Reinhart & Rogoff
- [Source](https://clio-infra.eu/Indicators/GoldStandard.html)

## Additional Sources (not yet downloaded)

- **[MeasuringWorth](https://www.measuringworth.com/datasets/exchangeglobal/)** — USD vs 41 currencies, UK from 1791. Requires manual download.
- **[IISG Historical Prices & Wages](https://datasets.iisg.amsterdam/)** — Open-access datasets on Dataverse, various exchange rate series going back to the 13th century
- **[Denzel, *Handbook of World Exchange Rates, 1590–1914*](https://www.routledge.com/Handbook-of-World-Exchange-Rates-1590-1914/Denzel/p/book/9780754603566)** — The canonical reference. Book format (not machine-readable).

## Structure

```
data/
  clio_infra_exchange_rates_compact.xlsx   # 181 countries, yearly FX to USD
  clio_infra_exchange_rates_broad.xlsx     # Same but includes all 224 countries
  clio_infra_inflation_compact.xlsx        # Inflation rates
  clio_infra_gold_standard_compact.xlsx    # Gold standard indicator
```

## Purpose

Researching exchange rate volatility across centuries — fat tails, regime changes, and structural breaks in currency markets.
