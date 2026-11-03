"""Registry of published datasets: name -> (path under data/derived, description).

Shared by the loader and by scripts/export_parquet.py, which writes one
Parquet file per entry for each release.
"""

DATASETS = {
    "fx_yearly": ("normalized/yearly_unified_panel.csv",
                  "Yearly FX vs USD, 236 countries, 1500-present (MW > Clio Infra > GMD), "
                  "with iso3, source, unit and quality flags"),
    "fx_yearly_wide": ("normalized/yearly_unified_wide.csv",
                       "Same values as fx_yearly, year x country"),
    "fx_daily": ("normalized/fred_daily_normalized.csv",
                 "Daily FX, 23 currencies vs USD since 1971 (FRED H.10), foreign per USD"),
    "fx_daily_wide": ("normalized/fred_daily_normalized_wide.csv",
                      "Same values as fx_daily, date x currency"),
    "fx_yearly_log_returns": ("analysis/yearly_log_returns.csv",
                              "Yearly log returns, 40 MeasuringWorth currencies, "
                              "chain-linked across redenominations"),
    "fx_daily_log_returns": ("analysis/daily_log_returns.csv",
                             "Daily log returns, 23 FRED currencies"),
    "fx_yearly_volatility": ("analysis/yearly_volatility_stats.csv",
                             "Per-currency yearly volatility, kurtosis, extremes"),
    "fx_daily_volatility": ("analysis/daily_volatility_stats.csv",
                            "Per-currency daily volatility, kurtosis, tail ratios"),
    "fx_daily_rolling_volatility": ("analysis/daily_rolling_volatility.csv",
                                    "252-day rolling volatility per currency"),
    "fx_yearly_correlation": ("analysis/yearly_correlation_matrix.csv",
                              "Correlation matrix of yearly log returns"),
    "fx_daily_correlation": ("analysis/daily_correlation_matrix.csv",
                             "Correlation matrix of daily log returns"),
    "fx_regimes_yearly": ("analysis/yearly_regime_classification.csv",
                          "IRR de facto exchange rate regime per country-year"),
    "fx_regime_stats": ("analysis/regime_conditional_stats.csv",
                        "Return statistics by exchange rate regime"),
    "fx_sigma_events": ("analysis/sigma_event_frequency.csv",
                        "Observed vs Gaussian frequency of k-sigma daily moves"),
    "fx_momentum_signals": ("analysis/daily_momentum_signals.csv",
                            "Time-series momentum signals per currency and lookback"),
    "fx_momentum_reversals": ("analysis/daily_momentum_reversals.csv",
                              "Short-term reversal vs 12-month momentum"),
    "gold_inflation_yearly": ("analysis/yearly_gold_inflation.csv",
                              "Gold price in local currency, gold vs CPI inflation, 1257-present"),
    "gold_inflation_monthly": ("analysis/monthly_gold_inflation.csv",
                               "Monthly gold price in local currency, 174 currencies"),
    "asset_returns_jst": ("analysis/jst_asset_returns.csv",
                          "Equity, housing, bond and bill return statistics (JST, CC BY-NC-SA 4.0)"),
    "sovereign_default_events": ("analysis/sovereign_default_events.csv",
                                 "Sovereign defaults, restructurings and haircuts since 1815 "
                                 "(Asonuma-Trebesch; Graf von Luckner, Meyer, Reinhart & Trebesch)"),
    "sovereign_debt_in_default": ("analysis/sovereign_debt_in_default.csv",
                                  "Sovereign debt in default by country-year and creditor, "
                                  "US$ m, 1960-present (Bank of Canada / Bank of England)"),
    "fx_daily_ecb": ("normalized/ecb_daily.csv",
                     "ECB euro reference rates, ~40 currencies per EUR, daily since 1999"),
    "cpi_inflation_yearly": ("analysis/cpi_inflation_yearly.csv",
                             "Headline CPI inflation %, ~200 countries, 1970-present (World Bank)"),
    "cpi_monthly": ("normalized/cpi_monthly.csv",
                    "Headline CPI index, monthly, ~180 countries (World Bank)"),
    "stock_bond_correlation": ("analysis/stock_bond_correlation.csv",
                               "Rolling 20-year stock-bond correlation (JST, CC BY-NC-SA 4.0)"),
}
