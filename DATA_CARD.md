# Data card: forex-centuries

A compilation of long-run exchange rate, precious metal, interest rate, price, output and debt data (1 CE–present) from 27 public sources, with a reproducible pipeline (`build.py`) that turns raw source files (`data/sources/`) into normalized panels and analysis tables (`data/derived/`).

- **Maintainer:** Federico Carrone
- **Updates:** weekly, via GitHub Actions (`.github/workflows/update-data.yml`). Each update is committed to `main` and published as a dated release (`data-YYYY-MM-DD`).
- **Citation:** see `CITATION.cff`. Also cite every underlying source you use (table below).

## Licensing: read this first

**The MIT license in this repository covers the code only.** Every dataset keeps the license and terms of its original publisher. Some of those terms are restrictive, and a few sources say they should not be redistributed at all. They are included here as published, with their terms documented below. **If you reuse or republish data from this repository, you are responsible for complying with each source's terms.** When in doubt, download from the original publisher.

Status key:
- **Open**: an open license or explicit permission to redistribute with attribution.
- **Restricted**: redistribution allowed only under conditions (non-commercial, share-alike, educational).
- **Unclear**: no license found; the authors ask only for citation.
- **Not redistributable**: the publisher's terms say not to redistribute or re-host. Included at the maintainer's discretion. Do not republish these, and obtain them from the publisher for any further use.

Terms were checked on the publishers' websites on 2026-11-03. They change over time, so check the linked page before relying on them.

| Source | Directory | Terms | Status | Terms page |
|---|---|---|---|---|
| FRED (Federal Reserve H.10 daily FX) | `fred/` | Public domain (US government); citation requested | Open | https://fred.stlouisfed.org/legal/ |
| IMF exchange rates (IFS, via codeforIATI mirror) | `imf/` | IMF terms for statistical data: reuse and redistribution allowed with attribution; commercial use needs IMF permission; changes must be stated | Restricted | https://www.imf.org/en/About/copyright-and-terms |
| IMF Historical Public Debt Database | `imf_hpdd/` | As IMF above | Restricted | https://www.imf.org/en/About/copyright-and-terms |
| BIS | `bis/` | Use unrestricted provided the BIS is cited | Open | https://data.bis.org/help/legal |
| Sveriges Riksbank (SWEA API) | `riksbank/` | Swedish open-data law: reuse without special consent | Open | https://www.riksbank.se/en-gb/about-the-riksbank/about-the-website/open-data--information-available-for-re-use/ |
| Riksbank Historical Monetary Statistics | `riksbank_hist/` | No explicit license; Riksbank open-data policy likely applies | Unclear | https://www.riksbank.se/en-gb/about-the-riksbank/the-tasks-of-the-riksbank/research/historical-monetary-statistics-of-sweden/ |
| World Bank official exchange rates (WDI) | `worldbank/` | CC BY 4.0 (underlying data from IMF IFS) | Open | https://datacatalog.worldbank.org/search/dataset/0037712 |
| World Bank Commodity Prices (Pink Sheet) | `worldbank_commodities/` | World Bank default CC BY 4.0; some series are credited to commercial vendors | Open (vendor series unclear) | https://www.worldbank.org/en/research/commodity-markets |
| JST Macrohistory Database | `jst/` | CC BY-NC-SA 4.0 | Restricted | https://www.macrohistory.net/database/ |
| Penn World Table | `pwt/` | CC BY 4.0 | Open | https://www.rug.nl/ggdc/productivity/pwt/ |
| MeasuringWorth | `measuringworth/` | "All rights reserved. This work may be used for non-profit educational purposes if proper credit is given." | Restricted | https://www.measuringworth.com/ |
| Clio Infra | `clio_infra/` | CC0 1.0 | Open | https://doi.org/10.34894/NBIFGP |
| FreeGoldAPI | `freegold/` | Data "for non-profit educational purposes"; merges MeasuringWorth, World Bank and Yahoo Finance futures | Restricted | https://github.com/olddatasets/gold-spot-downloader |
| DataHub gold prices | `gold/` | ODC-PDDL 1.0 (upstream: World Bank Pink Sheet, Timothy Green) | Open | https://github.com/datasets/gold-prices |
| LBMA gold and silver prices | `lbma/` | "A licence from IBA is required in order to obtain, use or redistribute real-time or historical benchmark data" | **Not redistributable** | https://www.lbma.org.uk/prices-and-data/precious-metal-prices |
| Ilzetzki–Reinhart–Rogoff regimes | `irr/` | No explicit license; citation requested | Unclear | https://www.ilzetzki.com/irr-data |
| Reinhart–Rogoff data | `reinhart_rogoff/` | "All Rights Reserved"; citation requested | Unclear | https://carmenreinhart.com/data/ |
| Bank of England, A Millennium of Macroeconomic Data | `boe/` | Bank of England site terms: non-commercial use; reuse by permission | Restricted | https://www.bankofengland.co.uk/legal |
| Schmelzing, eight centuries of real rates (BoE SWP 845) | `schmelzing/` | Bank of England site terms | Restricted | https://www.bankofengland.co.uk/legal |
| Maddison Project Database 2023 | `maddison/` | CC BY 4.0 | Open | https://www.rug.nl/ggdc/historicaldevelopment/maddison/ |
| Allen–Unger Global Commodity Prices | `allenunger/` | CC BY-SA 4.0 (derivatives must keep the license) | Restricted | https://dataverse.nl/dataset.xhtml?persistentId=doi:10.34894/IPVXMW |
| Bruegel / Darvas REER | `bruegel/` | Free distribution with attribution | Open | https://www.bruegel.org/dataset/real-effective-exchange-rates-178-countries-new-database |
| Center for Financial Stability, Historical Financial Statistics | `cfs/` | "Restrictions exist on reproducing data for any commercial use and for noncommercial database use" | **Not redistributable** (full conditions in the CFS data notes PDF) | https://www.centerforfinancialstability.org/hfs.php |
| MEMDB (Spufford, Metz), Rutgers | `memdb/` | Data free for non-commercial scholarly use, but the contents "may not be used as part of any other website, online database, or commercial product" | **Not redistributable** | https://memdb.libraries.rutgers.edu/about |
| Global Macro Database | `gmd/` | "Do not re-host or redistribute it"; exception for a paper's replication package | **Not redistributable** | https://www.globalmacrodata.com/license.html |

## Citations for the underlying sources

- **FRED:** Board of Governors of the Federal Reserve System (US), H.10 Foreign Exchange Rates, retrieved from FRED, Federal Reserve Bank of St. Louis.
- **IMF:** International Monetary Fund, International Financial Statistics.
- **IMF HPDD:** Abbas, Belhocine, ElGanainy & Horton (2011), "Historical Patterns and Dynamics of Public Debt: Evidence from a New Database", *IMF Economic Review* 59(4).
- **BIS:** Bank for International Settlements, exchange rate statistics.
- **Riksbank, historical:** Edvinsson, Jacobson & Waldenström (eds.) (2010), *Exchange Rates, Prices, and Wages, 1277–2008*, Sveriges Riksbank / Ekerlids (Historical Monetary Statistics of Sweden, Vol. I); Vols. II–III likewise.
- **JST:** Jordà, Schularick & Taylor (2017), "Macrofinancial History and the New Business Cycle Facts", *NBER Macroeconomics Annual 2016*. Returns data: Jordà, Knoll, Kuvshinov, Schularick & Taylor (2019), "The Rate of Return on Everything, 1870–2015", *QJE*.
- **Penn World Table:** Feenstra, Inklaar & Timmer (2015), "The Next Generation of the Penn World Table", *AER* 105(10).
- **MeasuringWorth:** Officer, "Exchange Rates Between the United States Dollar and Forty-one Currencies"; Officer & Williamson, "The Price of Gold, 1257–Present"; MeasuringWorth.
- **Clio Infra:** Bosch (2026), "Exchange Rates to US Dollar", doi:10.34894/NBIFGP (GBP version doi:10.34894/5NLBWR).
- **IRR:** Ilzetzki, Reinhart & Rogoff (2019), "Exchange Arrangements Entering the 21st Century: Which Anchor Will Hold?", *QJE* 134(2).
- **Reinhart–Rogoff:** Reinhart & Rogoff (2009), *This Time Is Different*, Princeton University Press, plus the paper for each series.
- **Bank of England:** Thomas & Dimsdale (2017), "A Millennium of UK Data", Bank of England OBRA dataset.
- **Schmelzing:** Schmelzing (2020), "Eight centuries of global real interest rates, R-G, and the 'suprasecular' decline, 1311–2018", Bank of England Staff Working Paper 845.
- **Maddison:** Bolt & van Zanden (2024), "Maddison style estimates of the evolution of the world economy: A new 2023 update", *Journal of Economic Surveys*.
- **Allen–Unger:** Allen & Unger (2019), "The Allen-Unger Global Commodity Prices Database", *Research Data Journal for the Humanities and Social Sciences* 4(1).
- **Bruegel:** Darvas (2012), "Real effective exchange rates for 178 countries: a new database", Bruegel Working Paper 2012/06.
- **CFS:** Center for Financial Stability, Historical Financial Statistics (ed. Kurt Schuler).
- **MEMDB:** Spufford (1986), *Handbook of Medieval Exchange*; Metz (1990), *Geld, Währung und Preisentwicklung*; Medieval and Early Modern Data Bank, Rutgers University.
- **GMD:** Müller, Xu, Lehbib & Chen (2025), "The Global Macro Database", NBER Working Paper 33714.

## Composition

Source files under `data/sources/<source>/` are kept as downloaded (see the README for schemas). The build produces:

| File | What | Key columns |
|---|---|---|
| `normalized/yearly_unified_panel.csv` | Yearly exchange rates, 236 countries, 1500–last full year | `year, iso3, country, rate_per_usd, source, unit, flags, comparable_with_previous` |
| `normalized/yearly_unified_wide.csv` | Same values, year × country | |
| `normalized/fred_daily_normalized*.csv` | 23 daily FX pairs since 1971, foreign currency per USD | `date, currency, rate_per_usd` |
| `analysis/*.csv` | Log returns, volatility, correlations, regimes, gold inflation, asset returns | see README |

## How the yearly panel is built

1. MeasuringWorth (MW), Clio Infra (CI) and GMD are loaded. Every country name is mapped to an ISO3 code (GMD codes plus explicit aliases); an unknown name fails the build.
2. Known-bad source rows are dropped (see "Known problems").
3. For each (year, iso3), one value is kept, preferring MW, then CI, then GMD.
4. **Levels are kept exactly as each source publishes them.** Sources differ in currency units: MW quotes each year in that year's currency (e.g. australes in 1990), while CI and GMD often restate history in a later unit, sometimes off by 10¹³. The panel therefore does **not** guarantee a consistent unit within a country. Use the quality flags before computing changes.

## Quality flags (yearly panel)

`flags` is a semicolon-separated list (empty when there is nothing to note):

| Flag | Meaning |
|---|---|
| `gap_before` | The previous year is missing |
| `redenomination` | MW's currency unit changed from the previous year (label-only renames excluded) |
| `source_switch` | The value comes from a different source than the previous consecutive year |
| `source_level_mismatch` | At a switch, the two sources disagree by more than 10% in the same year: different units or definitions |
| `source_unverified` | At a switch, there is no same-year overlap to check the two sources against each other |
| `level_jump` | Year-on-year move larger than 10× with none of the explanations above: a real hyperinflation or an unlabeled redenomination |
| `constant_growth` | Third or later identical non-zero log change in a row, typical of interpolated data |

`comparable_with_previous` is `False` for the first observation of each country and wherever `gap_before`, `redenomination`, `source_level_mismatch` or `source_unverified` applies. **Compute year-on-year changes only where it is `True`.** `unit` gives the MW currency unit (empty for other sources).

For returns, prefer `analysis/yearly_log_returns.csv`. It uses MW only, chain-linked across redenominations with official conversion factors (`MW_REDENOMINATIONS` in `build.py`).

## Known problems

Corrections applied in code (see `build.py` and the README "Data corrections" table):
- **MeasuringWorth FX:** 41 currency changes. 36 are chain-linked; 5 have no single conversion factor and are left as breaks (China 1933, Germany 1925 and 1950, and two that fall in series gaps). Venezuela's 2008, 2018 and 2021 redenominations are not labeled by MW and are listed explicitly.
- **MeasuringWorth FX, bad cells dropped:** Germany 1941 and 1945–49 duplicate Italy's values; France 1941–44 duplicates Germany's; Colombia 2017 reads `2.00`.
- **GMD:** Gambia 1950–56 is about 0.30/USD against the 1.7857 peg rate (dropped). Values for the current and future years are IMF forecasts (excluded).
- **IMF mirror (codeforIATI):** the November 2026 refresh dropped IRR 1957–2024, MRU and UYW history and added a 2027-dated row. The updater keeps observations dropped upstream and discards future dates.

Known and **not** corrected:
- The panel mixes currency units across sources within a country (see "How the yearly panel is built"). There are 150 `source_level_mismatch` rows.
- MW's Germany 1924 value (4.33×10¹¹ marks/USD) is about 10× below the stabilized rate of 4.2×10¹².
- Medieval and early modern series (MEMDB, Allen–Unger, Schmelzing, Maddison before 1820) are sparse and partly reconstructed. Treat tail statistics from them with caution.
- FRED daily data is not refreshed by CI until a `FRED_API_KEY` repository secret is set.
- The Riksbank API rate-limits anonymous clients. Series it does not return keep their previous values until the next run.
