"""
Re-runs the comparison analysis from "A Real-Time Supermarket Price Index for Bolivia"
against the latest tracker output and the latest official INE data.

Outputs one folder per dating convention for the official monthly series:
  analysis/output/mid_month/       INE month M is placed on the 15th of month M (primary)
  analysis/output/start_of_month/  INE month M is placed on the 1st of month M

INE's monthly index is an average of prices collected during the month, so mid-month is
the date that lines up with a point-in-time daily index, and INE's month-over-month change
lines up with the tracker's 30-day change ending on the 15th.

Usage (from the repo root):
  python analysis/paper_analysis.py
"""
import os
import sys
from io import StringIO

import numpy as np
import pandas as pd
import requests
import statsmodels.api as sm
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(REPO_ROOT, "results", "supermarket_1")
OUTPUT_DIR = os.path.join(REPO_ROOT, "analysis", "output")

INE_DATA_URL = "https://raw.githubusercontent.com/thomasriveros/live-ine-inflation-update/refs/heads/main/data"

# Synthetic city folder -> (column suffix, INE city name)
CITIES = {
    "la_paz": ("LaPaz", "CONURBACIÓN LA PAZ"),
    "cochabamba": ("Cochabamba", "REGION METROPOLITANA KANATA"),
    "santa_cruz": ("SantaCruz", "CONURBACIÓN SANTA CRUZ"),
}

# Official series are rebased so this month = 100 (the month the tracker starts)
BASE_MONTH = pd.Timestamp("2024-07-01")

# INE division names -> raw weights for the core-5 basket (same as the tracker)
CORE5_WEIGHTS = {
    "Alimentos y bebidas no alcohólicas": 27.06,
    "Prendas de vestir y calzado": 7.56,
    "Bienes y servicios diversos": 7.55,
    "Muebles, bienes y servicios domésticos": 6.08,
    "Bebidas alcohólicas y tabaco": 0.88,
}

# Days added to the first of the month to get the date an official value is placed on
CONVENTIONS = {"mid_month": 14, "start_of_month": 0}

SYNTHETIC_MOM_DAYS = 30
LAGS = [0, 15, 20]

# Records which official month the charts were last drawn for
CHARTS_MARKER = "charts_official_month.txt"
CHART_FILES = ["comparison_graph.png", "correlation_matrix.png",
               "scatter_core5_lag15.png", "scatter_overall_lag20.png"]


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def fetch_ine_csv(name):
    url = f"{INE_DATA_URL}/{name}.csv"
    res = requests.get(url, timeout=30)
    res.raise_for_status()
    df = pd.read_csv(StringIO(res.text))
    df["date"] = pd.to_datetime(df["date"])
    return df


def rebase(series):
    series = series.sort_index()
    series = series[series.index >= BASE_MONTH]
    if series.empty or series.index[0] != BASE_MONTH:
        raise ValueError(f"Official data does not include the base month {BASE_MONTH.date()}")
    return 100 * series / series.iloc[0]


def core5_index(category_rows):
    """
    Official core-5 equivalent: each INE division rebased to BASE_MONTH = 100, then
    combined with the normalized core-5 weights (the same structure as the tracker).
    """
    wide = category_rows.pivot(index="date", columns="category", values="CPI level")
    missing = [c for c in CORE5_WEIGHTS if c not in wide.columns]
    if missing:
        raise ValueError(f"INE category data is missing {missing}")
    wide = wide[list(CORE5_WEIGHTS)].dropna()
    rebased = wide.apply(rebase)
    weights = pd.Series(CORE5_WEIGHTS) / sum(CORE5_WEIGHTS.values())
    return (rebased * weights).sum(axis=1)


def load_official_monthly():
    """
    Monthly official indices (rebased to BASE_MONTH = 100) and their MoM inflation,
    indexed by the first day of the reference month.
    """
    national_overall = fetch_ine_csv("national_CPI").set_index("date")["CPI level"]
    national_categories = fetch_ine_csv("national_CPI_by_category")
    city_categories = fetch_ine_csv("city_level_CPI_by_category")

    series = {
        "Official_National": core5_index(national_categories),
        "Official_National_Overall": rebase(national_overall),
    }
    for suffix, ine_name in CITIES.values():
        rows = city_categories[city_categories["city"] == ine_name]
        if rows.empty:
            raise ValueError(f"INE city '{ine_name}' not found in city_level_CPI_by_category.csv")
        series[f"Official_{suffix}"] = core5_index(rows)

    monthly = pd.DataFrame(series).sort_index()

    for col in list(monthly.columns):
        monthly[f"{col}_Inflation"] = 100 * monthly[col].pct_change()
    return monthly


def load_synthetic_daily():
    """Daily synthetic indices (national and cities) and their 30-day inflation."""
    national = pd.read_csv(os.path.join(RESULTS_DIR, "national", "supermarket_1_tracker_results.csv"),
                           parse_dates=["date"])
    daily = national.set_index("date")[["data_source", "cpi"]].rename(
        columns={"data_source": "DataSource", "cpi": "Synthetic_National"})

    for city, (suffix, _) in CITIES.items():
        path = os.path.join(RESULTS_DIR, city, "supermarket_1_tracker_results.csv")
        city_df = pd.read_csv(path, parse_dates=["date"]).set_index("date")
        daily[f"Synthetic_{suffix}"] = city_df["cpi"]

    daily = daily.asfreq("D")
    for col in [c for c in daily.columns if c.startswith("Synthetic_")]:
        daily[f"{col}_Inflation"] = 100 * (daily[col] / daily[col].shift(SYNTHETIC_MOM_DAYS) - 1)
    return daily


def build_panel(daily, monthly, offset_days):
    """Daily panel with official values placed on (first of month + offset_days)."""
    official = monthly.copy()
    official.index = official.index + pd.Timedelta(days=offset_days)
    panel = daily.join(official, how="outer").sort_index()
    panel.index.name = "Date"

    regions = ["National"] + [suffix for suffix, _ in CITIES.values()]
    ordered = ["DataSource"]
    for region in regions:
        ordered += [f"Synthetic_{region}", f"Synthetic_{region}_Inflation"]
    for region in ["National", "National_Overall"] + regions[1:]:
        ordered += [f"Official_{region}", f"Official_{region}_Inflation"]
    return panel[ordered]


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------

def correlation_matrix(panel):
    numeric = panel.drop(columns=["DataSource"])
    return numeric.corr(min_periods=3)


def mad_table(panel):
    pairs = [
        ("National", "Synthetic_National", "Official_National"),
        ("National Overall", "Synthetic_National", "Official_National_Overall"),
    ] + [(suffix, f"Synthetic_{suffix}", f"Official_{suffix}") for suffix, _ in CITIES.values()]

    rows = []
    for metric, ext in [("Index", ""), ("Inflation", "_Inflation")]:
        for region, synth, official in pairs:
            both = panel[[synth + ext, official + ext]].dropna()
            rows.append({
                "Region": region,
                "Metric": metric,
                "N": len(both),
                "Correlation": both.corr().iloc[0, 1],
                "Mean_Absolute_Difference": (both.iloc[:, 0] - both.iloc[:, 1]).abs().mean(),
            })
    return pd.DataFrame(rows)


def lag_regressions(panel):
    """Official MoM inflation on synthetic 30-day inflation measured `lag` days earlier."""
    synth = panel["Synthetic_National_Inflation"]
    rows = []
    for target in ["Official_National_Inflation", "Official_National_Overall_Inflation"]:
        for lag in LAGS:
            df = pd.DataFrame({"y": panel[target]})
            df["x"] = synth.reindex(df.index - pd.Timedelta(days=lag)).values
            df = df.dropna()
            X = sm.add_constant(df["x"])

            ols = sm.OLS(df["y"], X).fit()
            hc1 = sm.OLS(df["y"], X).fit(cov_type="HC1")
            rlm = sm.RLM(df["y"], X, M=sm.robust.norms.HuberT()).fit()

            for method, fit, resid_se in [
                ("OLS", ols, np.sqrt(ols.mse_resid)),
                ("OLS (HC1 SEs)", hc1, np.sqrt(hc1.mse_resid)),
                ("Huber RLM", rlm, rlm.scale),
            ]:
                rows.append({
                    "Dependent": target,
                    "Lag_Days": lag,
                    "Method": method,
                    "N": int(fit.nobs),
                    "Intercept": fit.params["const"],
                    "Intercept_SE": fit.bse["const"],
                    "Slope": fit.params["x"],
                    "Slope_SE": fit.bse["x"],
                    "Slope_p": fit.pvalues["x"],
                    "Residual_SE_or_Scale": resid_se,
                    "R2": ols.rsquared if method != "Huber RLM" else np.nan,
                    "First_Obs": df.index.min().date(),
                    "Last_Obs": df.index.max().date(),
                })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Figures
# ---------------------------------------------------------------------------

COLORS = {"synthetic": "#1f3b73", "core": "#0f8c79", "overall": "#d62728"}


def plot_comparison(panel, path, label):
    fig, (top, bottom) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

    top.plot(panel.index, panel["Synthetic_National"], color=COLORS["synthetic"], lw=1.6, label="Supermarket CPI")
    for col, color, name, style in [
        ("Official_National", COLORS["core"], "Official core-5", "-"),
        ("Official_National_Overall", COLORS["overall"], "Official overall", "--"),
    ]:
        s = panel[col].dropna()
        top.plot(s.index, s.values, color=color, lw=1.6, ls=style, marker="o", ms=3, label=name)
    top.set_ylabel("Index (Jul 2024 = 100)")
    top.set_title(f"CPI levels: official vs. supermarket tracker ({label})")
    top.legend(frameon=False)

    bottom.plot(panel.index, panel["Synthetic_National_Inflation"], color=COLORS["synthetic"], lw=1.4,
                label="Synthetic (30-day change)")
    for col, color, name, style in [
        ("Official_National_Inflation", COLORS["core"], "Official core-5 (MoM)", "-"),
        ("Official_National_Overall_Inflation", COLORS["overall"], "Official overall (MoM)", "--"),
    ]:
        s = panel[col].dropna()
        bottom.plot(s.index, s.values, color=color, lw=1.6, ls=style, marker="o", ms=3, label=name)
    bottom.axhline(0, color="#999999", lw=0.8)
    bottom.set_ylabel("Inflation (%)")
    bottom.set_title("Monthly inflation")
    bottom.legend(frameon=False)

    for ax in (top, bottom):
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", color="#e5e5e5")
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)


def plot_correlation_matrix(corr, path):
    fig, ax = plt.subplots(figsize=(12, 10))
    im = ax.imshow(corr.values, cmap="RdBu", vmin=-1, vmax=1)
    ax.set_xticks(range(len(corr.columns)), corr.columns, rotation=60, ha="right", fontsize=7)
    ax.set_yticks(range(len(corr.index)), corr.index, fontsize=7)
    for i in range(len(corr.index)):
        for j in range(len(corr.columns)):
            if j <= i and not np.isnan(corr.values[i, j]):
                ax.text(j, i, f"{corr.values[i, j]:.2f}", ha="center", va="center", fontsize=5.5)
    fig.colorbar(im, ax=ax, shrink=0.8, label="Correlation")
    ax.set_title("Correlation matrix (observed dates only)")
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)


def plot_lag_scatter(panel, target, lag, path, ylabel):
    df = pd.DataFrame({"y": panel[target]})
    df["x"] = panel["Synthetic_National_Inflation"].reindex(df.index - pd.Timedelta(days=lag)).values
    df = df.dropna()
    X = sm.add_constant(df["x"])
    ols = sm.OLS(df["y"], X).fit()
    rlm = sm.RLM(df["y"], X, M=sm.robust.norms.HuberT()).fit()

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(df["x"], df["y"], s=28, alpha=0.6, color="#2c3e50")
    xs = np.linspace(df["x"].min(), df["x"].max(), 50)
    ax.plot(xs, ols.params["const"] + ols.params["x"] * xs, color="#e74c3c", ls="--", label="OLS")
    ax.plot(xs, rlm.params["const"] + rlm.params["x"] * xs, color="#2980b9", lw=2, label="Huber RLM")
    ax.set_xlabel(f"Synthetic supermarket tracker ({lag}-day lag) [%]")
    ax.set_ylabel(ylabel)
    ax.set_title(f"Synthetic vs. official inflation, {lag}-day lag (n={len(df)})")
    ax.legend(frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def write_summary(path, label, panel, mad, regs):
    synth_last = panel["Synthetic_National"].last_valid_index().date()
    official_last = panel["Official_National"].last_valid_index().date()
    lines = [
        f"# Paper analysis: {label}",
        "",
        f"- Tracker data through: {synth_last}",
        f"- Latest official observation placed on: {official_last}",
        f"- Official series rebased to {BASE_MONTH:%B %Y} = 100; synthetic inflation is a {SYNTHETIC_MOM_DAYS}-day change.",
        "",
        "## Correlation and mean absolute difference",
        "",
        "| Region | Metric | N | Correlation | MAD |",
        "|---|---|---|---|---|",
    ]
    for _, r in mad.iterrows():
        lines.append(f"| {r.Region} | {r.Metric} | {r.N} | {r.Correlation:.3f} | {r.Mean_Absolute_Difference:.3f} |")
    lines += [
        "",
        "## Lag regressions (official MoM inflation on lagged synthetic inflation)",
        "",
        "| Dependent | Lag | Method | N | Slope | SE | p | Intercept |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for _, r in regs.iterrows():
        dep = "Overall" if "Overall" in r.Dependent else "Core-5"
        lines.append(f"| {dep} | {r.Lag_Days} | {r.Method} | {r.N} | {r.Slope:.3f} | {r.Slope_SE:.3f} | "
                     f"{r.Slope_p:.4f} | {r.Intercept:.3f} |")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def charts_are_current(out_dir, official_month):
    """Charts are redrawn only when a new official month arrives, to keep repo growth small."""
    marker = os.path.join(out_dir, CHARTS_MARKER)
    if not os.path.exists(marker) or not all(os.path.exists(os.path.join(out_dir, f)) for f in CHART_FILES):
        return False
    with open(marker, encoding="utf-8") as f:
        return f.read().strip() == official_month


def run(convention, daily, monthly, force_charts=False):
    out_dir = os.path.join(OUTPUT_DIR, convention)
    os.makedirs(out_dir, exist_ok=True)
    label = convention.replace("_", "-") + " dating"

    panel = build_panel(daily, monthly, CONVENTIONS[convention])
    corr = correlation_matrix(panel)
    mad = mad_table(panel)
    regs = lag_regressions(panel)

    # Rounded so float noise across library versions does not create daily diffs
    panel.to_csv(os.path.join(out_dir, "national_cpi_data.csv"), date_format="%Y-%m-%d", float_format="%.6f")
    corr.to_csv(os.path.join(out_dir, "correlation_matrix.csv"), float_format="%.6f")
    mad.to_csv(os.path.join(out_dir, "mad_table.csv"), index=False, float_format="%.6f")
    regs.to_csv(os.path.join(out_dir, "lag_regressions.csv"), index=False, float_format="%.6f")
    write_summary(os.path.join(out_dir, "summary.md"), label, panel, mad, regs)

    official_month = f"{monthly.index.max():%Y-%m}"
    if force_charts or not charts_are_current(out_dir, official_month):
        plot_comparison(panel, os.path.join(out_dir, "comparison_graph.png"), label)
        plot_correlation_matrix(corr, os.path.join(out_dir, "correlation_matrix.png"))
        plot_lag_scatter(panel, "Official_National_Inflation", 15,
                         os.path.join(out_dir, "scatter_core5_lag15.png"), "Official core-5 inflation [%]")
        plot_lag_scatter(panel, "Official_National_Overall_Inflation", 20,
                         os.path.join(out_dir, "scatter_overall_lag20.png"), "Official overall inflation [%]")
        with open(os.path.join(out_dir, CHARTS_MARKER), "w", encoding="utf-8") as f:
            f.write(official_month + "\n")
        print(f"Redrew {convention} charts for official data through {official_month}")
    print(f"Wrote {convention} analysis to {out_dir}")


def main():
    force_charts = "--force-charts" in sys.argv
    daily = load_synthetic_daily()
    monthly = load_official_monthly()
    for convention in CONVENTIONS:
        run(convention, daily, monthly, force_charts)


if __name__ == "__main__":
    sys.exit(main())
