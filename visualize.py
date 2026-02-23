"""
visualize.py — Generate charts for forex-centuries key findings.
Outputs PNGs to charts/ directory.

Usage: python visualize.py
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import norm
from scipy.spatial.distance import squareform
from scipy.cluster.hierarchy import linkage, dendrogram
from pathlib import Path

ROOT = Path(__file__).parent
DERIVED = ROOT / "data" / "derived"
CHARTS = ROOT / "charts"


def fat_tails_histogram():
    """EUR/USD daily log returns vs fitted normal distribution."""
    print("  fat_tails_histogram.png")

    df = pd.read_csv(DERIVED / "analysis/daily_log_returns.csv")
    eur = df[df["currency"] == "EUR"]["log_return"].values

    fig, ax = plt.subplots(figsize=(10, 6))
    n, bins, _ = ax.hist(eur, bins=200, density=True, alpha=0.7,
                          color="#4C72B0", label="EUR/USD observed")

    mu, sigma = eur.mean(), eur.std()
    x = np.linspace(bins[0], bins[-1], 500)
    ax.plot(x, norm.pdf(x, mu, sigma), "r-", linewidth=2,
            label=f"Normal fit (μ={mu:.5f}, σ={sigma:.5f})")

    ax.set_xlabel("Daily log return")
    ax.set_ylabel("Density")
    ax.set_title("EUR/USD daily log returns vs Gaussian distribution")
    ax.legend()
    ax.set_xlim(-0.05, 0.05)

    fig.tight_layout()
    fig.savefig(CHARTS / "fat_tails_histogram.png", dpi=150)
    plt.close(fig)


def peg_paradox():
    """Scatter: annualized volatility vs excess kurtosis for all currencies."""
    print("  peg_paradox.png")

    stats = pd.read_csv(DERIVED / "analysis/daily_volatility_stats.csv")
    # Exclude VEF (hyperinflation outlier distorts the scale)
    stats = stats[stats["currency"] != "VEF"]

    fig, ax = plt.subplots(figsize=(10, 7))
    ax.scatter(stats["annualized_volatility"] * 100, stats["excess_kurtosis"],
               s=80, alpha=0.8, color="#4C72B0", edgecolors="white", linewidth=0.5)

    labels = {"HKD", "CNY", "LKR", "KRW", "THB", "MXN"}
    for _, row in stats.iterrows():
        if row["currency"] in labels:
            ax.annotate(row["currency"],
                        (row["annualized_volatility"] * 100, row["excess_kurtosis"]),
                        textcoords="offset points", xytext=(8, 4),
                        fontsize=9, fontweight="bold")

    ax.set_xlabel("Annualized volatility (%)")
    ax.set_ylabel("Excess kurtosis")
    ax.set_title("The peg paradox: low volatility ≠ low tail risk")
    ax.set_yscale("log")

    fig.tight_layout()
    fig.savefig(CHARTS / "peg_paradox.png", dpi=150)
    plt.close(fig)


def tail_ratio_bar():
    """Horizontal bar chart of tail ratios across currencies."""
    print("  tail_ratio_bar.png")

    stats = pd.read_csv(DERIVED / "analysis/daily_volatility_stats.csv")
    stats = stats.sort_values("tail_ratio")

    fig, ax = plt.subplots(figsize=(10, 8))
    colors = ["#D65F5F" if r > 1 else "#4C72B0" for r in stats["tail_ratio"]]
    ax.barh(stats["currency"], stats["tail_ratio"], color=colors, edgecolor="white")
    ax.axvline(x=1.0, color="black", linestyle="--", linewidth=1,
               label="Gaussian expectation")

    ax.set_xlabel("Tail ratio (observed 3σ events / expected under normal)")
    ax.set_title("Tail event frequency vs Gaussian prediction")
    ax.legend()

    fig.tight_layout()
    fig.savefig(CHARTS / "tail_ratio_bar.png", dpi=150)
    plt.close(fig)


def rolling_volatility():
    """1-year rolling annualized volatility for major currencies."""
    print("  rolling_volatility.png")

    wide = pd.read_csv(DERIVED / "normalized/fred_daily_normalized_wide.csv",
                        index_col="date", parse_dates=True)
    log_ret = np.log(wide / wide.shift(1))

    currencies = ["GBP", "JPY", "CHF", "EUR"]
    colors = ["#4C72B0", "#DD8452", "#55A868", "#C44E52"]

    fig, ax = plt.subplots(figsize=(14, 6))
    for currency, color in zip(currencies, colors):
        if currency in log_ret.columns:
            rolling = log_ret[currency].rolling(252).std() * np.sqrt(252) * 100
            ax.plot(rolling.index, rolling, label=currency, color=color, linewidth=1)

    events = {
        "1971-08-15": "Nixon shock",
        "1999-01-01": "EUR launch",
        "2008-09-15": "Lehman",
        "2020-03-11": "COVID",
    }
    for date_str, label in events.items():
        ts = pd.Timestamp(date_str)
        ax.axvline(ts, color="gray", linestyle=":", alpha=0.7)
        ax.text(ts, ax.get_ylim()[1] * 0.95, f" {label}",
                fontsize=8, rotation=90, va="top", color="gray")

    ax.set_xlabel("Date")
    ax.set_ylabel("1-year rolling annualized volatility (%)")
    ax.set_title("FX volatility regimes (252-day rolling window)")
    ax.legend(loc="upper left")
    ax.set_ylim(bottom=0)

    fig.tight_layout()
    fig.savefig(CHARTS / "rolling_volatility.png", dpi=150)
    plt.close(fig)


def correlation_heatmap():
    """Heatmap of daily log-return correlations, hierarchically clustered."""
    print("  correlation_heatmap.png")

    corr = pd.read_csv(DERIVED / "analysis/daily_correlation_matrix.csv", index_col=0)

    # Hierarchical clustering for reordering
    dist = 1 - corr.fillna(0).values
    np.fill_diagonal(dist, 0)
    condensed = squareform(dist)
    link = linkage(condensed, method="average")
    order = dendrogram(link, no_plot=True)["leaves"]

    corr_ordered = corr.iloc[order, order]

    fig, ax = plt.subplots(figsize=(12, 10))
    im = ax.imshow(corr_ordered.values, cmap="RdBu_r", vmin=-1, vmax=1, aspect="equal")

    ax.set_xticks(range(len(corr_ordered)))
    ax.set_yticks(range(len(corr_ordered)))
    ax.set_xticklabels(corr_ordered.columns, rotation=45, ha="right", fontsize=9)
    ax.set_yticklabels(corr_ordered.index, fontsize=9)

    fig.colorbar(im, ax=ax, shrink=0.8, label="Pearson correlation")
    ax.set_title("Daily log-return correlations (hierarchically clustered)")

    fig.tight_layout()
    fig.savefig(CHARTS / "correlation_heatmap.png", dpi=150)
    plt.close(fig)


def gold_erosion():
    """Cumulative gold purchasing power retained for major currencies."""
    print("  gold_erosion.png")

    df = pd.read_csv(DERIVED / "analysis/yearly_gold_inflation.csv")

    currencies = {
        "United States": ("#4C72B0", "USD"),
        "United Kingdom": ("#DD8452", "GBP"),
        "Japan": ("#55A868", "JPY"),
        "Switzerland": ("#C44E52", "CHF"),
        "France": ("#8172B3", "FRF"),
        "Germany": ("#937860", "DEM"),
        "India": ("#DA8BC3", "INR"),
        "China": ("#8C8C8C", "CNY"),
    }

    fig, ax = plt.subplots(figsize=(14, 7))
    for country, (color, label) in currencies.items():
        sub = df[df["country"] == country].sort_values("year")
        if len(sub) > 0:
            ax.plot(sub["year"], sub["cumulative_retained_pct"],
                    label=f"{label} (since {int(sub['base_year'].iloc[0])})",
                    color=color, linewidth=1.2)

    ax.set_yscale("log")
    ax.set_xlabel("Year")
    ax.set_ylabel("% of gold purchasing power retained (log scale)")
    ax.set_title("Currency debasement against gold")
    ax.legend(loc="lower left", fontsize=8)
    ax.set_ylim(bottom=0.001)
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(CHARTS / "gold_erosion.png", dpi=150)
    plt.close(fig)


def regime_timeline():
    """Timeline of exchange rate regimes for major countries."""
    print("  regime_timeline.png")

    path = DERIVED / "analysis/yearly_regime_classification.csv"
    if not path.exists():
        print("    Skipped: yearly_regime_classification.csv not found")
        return

    df = pd.read_csv(path)

    # Select countries with long histories
    counts = df.groupby("country").size().sort_values(ascending=False)
    top_countries = counts.head(25).index.tolist()
    df = df[df["country"].isin(top_countries)]

    regime_colors = {
        1: "#2166AC",  # peg - blue
        2: "#67A9CF",  # crawling peg - light blue
        3: "#FDDBC7",  # managed float - light orange
        4: "#EF8A62",  # free float - orange
        5: "#B2182B",  # freely falling - red
        6: "#762A83",  # dual market - purple
    }

    countries_sorted = sorted(top_countries)
    fig, ax = plt.subplots(figsize=(16, 10))

    for i, country in enumerate(countries_sorted):
        sub = df[df["country"] == country].sort_values("year")
        for _, row in sub.iterrows():
            color = regime_colors.get(row["coarse_regime"], "#CCCCCC")
            ax.barh(i, 1, left=row["year"], height=0.8, color=color, edgecolor="none")

    ax.set_yticks(range(len(countries_sorted)))
    ax.set_yticklabels(countries_sorted, fontsize=8)
    ax.set_xlabel("Year")
    ax.set_title("Exchange rate regimes (IRR classification)")

    # Legend
    from matplotlib.patches import Patch
    labels = {1: "Peg", 2: "Crawling peg", 3: "Managed float",
              4: "Free float", 5: "Freely falling", 6: "Dual market"}
    patches = [Patch(color=regime_colors[k], label=labels[k]) for k in sorted(labels)]
    ax.legend(handles=patches, loc="lower right", fontsize=8)

    fig.tight_layout()
    fig.savefig(CHARTS / "regime_timeline.png", dpi=150)
    plt.close(fig)


def main():
    print("forex-centuries chart generation\n")
    CHARTS.mkdir(exist_ok=True)

    fat_tails_histogram()
    peg_paradox()
    tail_ratio_bar()
    rolling_volatility()
    correlation_heatmap()
    gold_erosion()
    regime_timeline()

    print(f"\nDone. Charts saved to {CHARTS}/")


if __name__ == "__main__":
    main()
