# forex-centuries

Load the [forex-centuries](https://github.com/unbalancedparentheses/forex-centuries) datasets (exchange rates for 236 countries since 1500, daily FX since 1971, gold since 1257, and more) as pandas DataFrames.

```python
import forex_centuries as fc

fc.list_datasets()                 # name -> description
panel = fc.load("fx_yearly")       # yearly FX vs USD with quality flags
daily = fc.load("fx_daily")
pinned = fc.load("fx_yearly", version="data-2026-11-03.38")  # reproducible
```

Files are downloaded from the GitHub release assets on first use and cached under `~/.cache/forex-centuries` (set `FOREX_CENTURIES_CACHE` to change this). The latest-release lookup is cached for a day.

In `fx_yearly`, levels are as published by each source, so compute year-on-year changes only where `comparable_with_previous` is true. For returns, use `fx_yearly_log_returns`, which is chain-linked across redenominations.

**Licensing:** the MIT license covers this package's code. The data comes from 27 sources, each with its own terms (some non-commercial or share-alike). See the [data card](https://github.com/unbalancedparentheses/forex-centuries/blob/main/DATA_CARD.md) and cite the sources you use.
