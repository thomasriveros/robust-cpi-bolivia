"""
How closely does synthetic (supermarket) inflation track official INE inflation?

Complements paper_analysis.py (correlation, MAD, lag regressions) with forecast-style
accuracy measures, for both the matched basket (official series built from the same INE
divisions) and official overall inflation:

  accuracy_table.csv     bias, MAE, RMSE, Theil decomposition of the MSE, directional accuracy,
                         and RMSE relative to a random-walk benchmark
  nowcast_evaluation.csv pseudo out-of-sample nowcasts (raw and calibrated synthetic) against
                         naive benchmarks, with Diebold-Mariano tests
  lag_profile.csv        RMSE and correlation as the synthetic window is shifted earlier or later
  monthly_inflation.csv  the month-by-month official and synthetic series behind the tables

Two synthetic monthly inflation measures are compared:
  - Monthly average: the daily index averaged over calendar month M, then the change on
    month M-1. INE's index is a monthly average of prices, so this is the matched concept.
  - 30-day change to the 15th: the point-in-time change used in paper_analysis.py with
    mid-month dating. It is available about two weeks earlier.

Outputs go to analysis/output/accuracy/ (core-5) and analysis/output/core4/accuracy/.

Usage (from the repo root):
  python analysis/tracking_accuracy.py [--force-charts]
"""
import os
import sys

import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from paper_analysis import (CITIES, CHARTS_MARKER, INDEXES, charts_are_current,
                            load_official_monthly, load_synthetic_daily)

# A month's average needs at least this many daily observations (the tracker starts 29 Jul 2024)
MIN_DAYS_IN_MONTH = 15
# Months of history before the first out-of-sample nowcast
MIN_TRAIN = 12
# Days the synthetic 30-day window is shifted earlier (positive) or later (negative) than the 15th
LAG_RANGE = range(-10, 31)
# Months whose squared errors are reported as a share of the total
TOP_MONTHS = 3

REGIONS = ["National"] + [suffix for suffix, _ in CITIES.values()]
MEASURES = {
    "avg_mom": "Monthly average, MoM",
    "d30_mom": "30-day change to the 15th",
    "avg_yoy": "Monthly average, 12-month",
}
CHART_FILES = ["errors_by_month.png", "lag_profile.png"]


# ---------------------------------------------------------------------------
# Monthly series
# ---------------------------------------------------------------------------

def monthly_frame(daily, monthly):
    """
    One row per official month (first of month): official MoM and 12-month inflation for
    every region, plus each synthetic measure.
    """
    official = monthly.asfreq("MS")
    out = pd.DataFrame(index=official.index)
    out.index.name = "Month"

    targets = {r: f"Official_{r}" for r in REGIONS}
    targets["National_Overall"] = "Official_National_Overall"
    for name, col in targets.items():
        out[f"Official_{name}_MoM"] = official[f"{col}_Inflation"]
        out[f"Official_{name}_YoY"] = 100 * (official[col] / official[col].shift(12) - 1)

    for region in REGIONS:
        col = f"Synthetic_{region}"
        grouped = daily[col].resample("MS")
        avg = grouped.mean().where(grouped.count() >= MIN_DAYS_IN_MONTH)
        avg = avg.reindex(out.index)
        out[f"{col}_avg_mom"] = 100 * avg.pct_change(fill_method=None)
        out[f"{col}_avg_yoy"] = 100 * (avg / avg.shift(12) - 1)
        out[f"{col}_d30_mom"] = daily[f"{col}_Inflation"].reindex(out.index + pd.Timedelta(days=14)).values
    return out


def pairs():
    """(region label, target label, synthetic region, official column stem)."""
    rows = [(r, "Matched basket", r, r) for r in REGIONS]
    rows.insert(1, ("National", "Overall", "National", "National_Overall"))
    return rows


def aligned(frame, measure, synth_region, official_stem):
    horizon = "YoY" if measure.endswith("yoy") else "MoM"
    df = pd.DataFrame({
        "synthetic": frame[f"Synthetic_{synth_region}_{measure}"],
        "official": frame[f"Official_{official_stem}_{horizon}"],
    })
    df["official_prev"] = df["official"].shift(1)
    return df.dropna(subset=["synthetic", "official"])


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------

def theil_shares(s, o):
    """MSE = bias^2 + (sd_s - sd_o)^2 + 2(1 - r) sd_s sd_o, each term as a share of the MSE."""
    mse = np.mean((s - o) ** 2)
    sd_s, sd_o = s.std(ddof=0), o.std(ddof=0)
    r = np.corrcoef(s, o)[0, 1]
    return ((s.mean() - o.mean()) ** 2 / mse, (sd_s - sd_o) ** 2 / mse, 2 * (1 - r) * sd_s * sd_o / mse)


def diebold_mariano(e1, e2):
    """Two-sided p-value for equal squared-error loss, one-step horizon, Harvey-Leybourne-Newbold correction."""
    d = np.asarray(e1) ** 2 - np.asarray(e2) ** 2
    n = len(d)
    if n < 3 or np.allclose(d, d[0]):
        return np.nan
    dm = d.mean() / np.sqrt(d.var(ddof=0) / n) * np.sqrt((n - 1) / n)
    return 2 * stats.t.sf(abs(dm), df=n - 1)


def accuracy_table(frame):
    rows = []
    for measure, measure_label in MEASURES.items():
        for region, target, synth_region, stem in pairs():
            df = aligned(frame, measure, synth_region, stem)
            if len(df) < 3:
                continue
            s, o = df["synthetic"], df["official"]
            err = s - o
            sq = (err ** 2).sort_values(ascending=False)
            u_bias, u_var, u_cov = theil_shares(s, o)
            moves = pd.concat([s.diff(), o.diff()], axis=1).dropna()
            rw = df.dropna(subset=["official_prev"])
            rmse_rw_sample = np.sqrt(((rw["synthetic"] - rw["official"]) ** 2).mean())
            rmse_rw = np.sqrt(((rw["official_prev"] - rw["official"]) ** 2).mean())
            rows.append({
                "Measure": measure_label,
                "Region": region,
                "Target": target,
                "N": len(df),
                "First_Month": f"{df.index.min():%Y-%m}",
                "Last_Month": f"{df.index.max():%Y-%m}",
                "Official_Mean": o.mean(),
                "Official_SD": o.std(),
                "Synthetic_Mean": s.mean(),
                "Synthetic_SD": s.std(),
                "Bias": err.mean(),
                "MAE": err.abs().mean(),
                "Median_AE": err.abs().median(),
                "RMSE": np.sqrt((err ** 2).mean()),
                "Debiased_RMSE": err.std(ddof=0),
                "Correlation": s.corr(o),
                "Theil_Bias_Share": u_bias,
                "Theil_Variance_Share": u_var,
                "Theil_Covariance_Share": u_cov,
                "Direction_Accuracy": (np.sign(moves.iloc[:, 0]) == np.sign(moves.iloc[:, 1])).mean(),
                f"Top{TOP_MONTHS}_Months_SSE_Share": sq.iloc[:TOP_MONTHS].sum() / sq.sum(),
                f"Top{TOP_MONTHS}_Months": " ".join(f"{m:%Y-%m}" for m in sq.index[:TOP_MONTHS]),
                "RMSE_Random_Walk": rmse_rw,
                "RMSE_Ratio_vs_Random_Walk": rmse_rw_sample / rmse_rw,
            })
    return pd.DataFrame(rows)


def nowcast_evaluation(frame):
    """
    Pseudo out-of-sample nowcasts of official national MoM inflation for month t, each using
    only what is known when month t's synthetic measure is complete (official data through t-1):
      Raw synthetic   synthetic inflation itself
      Calibrated      OLS of official on synthetic, fitted on months before t
      Random walk     official inflation in t-1
      Expanding mean  average official inflation before t
    Every model is scored on the same months.
    """
    rows = []
    for measure in ["avg_mom", "d30_mom"]:
        for region, target, synth_region, stem in pairs()[:2]:
            df = aligned(frame, measure, synth_region, stem)
            preds = []
            for i in range(MIN_TRAIN, len(df)):
                train, now = df.iloc[:i], df.iloc[i]
                if np.isnan(now["official_prev"]):
                    continue
                slope, intercept = np.polyfit(train["synthetic"], train["official"], 1)
                preds.append({
                    "Month": df.index[i],
                    "official": now["official"],
                    "Raw synthetic": now["synthetic"],
                    "Calibrated synthetic": intercept + slope * now["synthetic"],
                    "Random walk": now["official_prev"],
                    "Expanding mean": train["official"].mean(),
                })
            if not preds:
                continue
            p = pd.DataFrame(preds).set_index("Month")
            errors = {m: p[m] - p["official"] for m in p.columns if m != "official"}
            rmse_rw = np.sqrt((errors["Random walk"] ** 2).mean())
            for model, e in errors.items():
                rmse = np.sqrt((e ** 2).mean())
                rows.append({
                    "Measure": MEASURES[measure],
                    "Target": target,
                    "Model": model,
                    "N": len(e),
                    "First_Month": f"{p.index.min():%Y-%m}",
                    "Last_Month": f"{p.index.max():%Y-%m}",
                    "Bias": e.mean(),
                    "MAE": e.abs().mean(),
                    "RMSE": rmse,
                    "RMSE_Ratio_vs_Random_Walk": rmse / rmse_rw,
                    "DM_p_vs_Random_Walk": np.nan if model == "Random walk" else diebold_mariano(e, errors["Random walk"]),
                })
    return pd.DataFrame(rows)


def lag_profile(daily, frame):
    """RMSE and correlation of official MoM against the synthetic 30-day change ending `lag` days before the 15th."""
    rows = []
    for _, target, synth_region, stem in pairs()[:2]:
        official = frame[f"Official_{stem}_MoM"]
        for lag in LAG_RANGE:
            dates = official.index + pd.Timedelta(days=14 - lag)
            df = pd.DataFrame({"official": official.values,
                               "synthetic": daily[f"Synthetic_{synth_region}_Inflation"].reindex(dates).values},
                              index=official.index).dropna()
            err = df["synthetic"] - df["official"]
            rows.append({"Target": target, "Lag_Days": lag, "N": len(df), "Bias": err.mean(),
                         "MAE": err.abs().mean(), "RMSE": np.sqrt((err ** 2).mean()),
                         "Correlation": df["synthetic"].corr(df["official"])})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Figures
# ---------------------------------------------------------------------------

INK, INK2, GRID, SURFACE = "#0b0b0b", "#52514e", "#e7e6e2", "#fcfcfb"
TARGET_COLORS = {"Matched basket": "#2a78d6", "Overall": "#eb6834"}


def style(ax, title):
    ax.set_title(title, loc="left", fontsize=10.5, color=INK, fontweight="bold", pad=8)
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(length=0, colors=INK2)


def plot_errors_by_month(frame, acc, path, label):
    """Monthly-average synthetic minus official MoM inflation, national, one panel per target."""
    fig, axes = plt.subplots(2, 1, figsize=(10, 7), sharex=True, sharey=True, facecolor=SURFACE)
    for ax, (region, target, synth_region, stem) in zip(axes, pairs()[:2]):
        df = aligned(frame, "avg_mom", synth_region, stem)
        err = df["synthetic"] - df["official"]
        ax.set_facecolor(SURFACE)
        ax.bar(err.index, err.values, width=22, color=TARGET_COLORS[target], edgecolor=SURFACE, lw=1)
        ax.axhline(0, color=INK2, lw=0.6)
        r = acc[(acc.Measure == MEASURES["avg_mom"]) & (acc.Region == region) & (acc.Target == target)].iloc[0]
        name = f"official {label.lower()}" if target == "Matched basket" else "official overall"
        style(ax, f"Synthetic minus {name} (pp)")
        ax.set_title(f"RMSE {r.RMSE:.2f}   MAE {r.MAE:.2f}   bias {r.Bias:+.2f}", loc="right",
                     fontsize=8.5, color=INK2, pad=8)
        ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 4, 7, 10]))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %y"))
    fig.text(0.01, 0.005, "National month-over-month inflation. Synthetic = change in the monthly average of the "
             "daily supermarket index. Positive bars: the tracker ran hotter than INE.", fontsize=7.5, color=INK2)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(path, dpi=110, facecolor=SURFACE)
    plt.close(fig)


def plot_lag_profile(lags, path):
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), facecolor=SURFACE)
    for ax, metric, best in [(axes[0], "RMSE", "idxmin"), (axes[1], "Correlation", "idxmax")]:
        ax.set_facecolor(SURFACE)
        for (target, color), dy in zip(TARGET_COLORS.items(), [10, -14]):
            s = lags[lags.Target == target].set_index("Lag_Days")[metric]
            ax.plot(s.index, s.values, color=color, lw=2, label=target)
            k = getattr(s, best)()
            ax.plot(k, s[k], "o", color=color, ms=8, mec=SURFACE, mew=2)
            ax.annotate(f"{target}: {k}d, {s[k]:.2f}", (k, s[k]), xytext=(8, dy),
                        textcoords="offset points", fontsize=8.5, color=INK)
        ax.axvline(0, color=INK2, lw=0.6, ls=":")
        ax.set_xlabel("Days the synthetic 30-day window ends before the 15th of month M", color=INK2, fontsize=8.5)
        style(ax, f"{metric} vs official national MoM")
    axes[0].legend(frameon=False, fontsize=8.5)
    fig.tight_layout()
    fig.savefig(path, dpi=110, facecolor=SURFACE)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def write_summary(path, label, acc, nowcast, lags):
    top = f"Top{TOP_MONTHS}_Months_SSE_Share"
    lines = [
        f"# Tracking accuracy: {label}",
        "",
        f"- Official data through: {acc.Last_Month.max()}",
        "- Errors are synthetic minus official, in percentage points. Matched basket = official series built "
        "from the same INE divisions as the tracker.",
        "- Theil shares split the MSE into bias, variance (scale mismatch) and covariance (unsystematic) parts.",
        "- RW ratio < 1: the synthetic measure beats last month's official inflation (random walk) on the same months.",
        "",
        "## In-sample accuracy",
        "",
        "| Measure | Region | Target | N | Bias | MAE | RMSE | Corr | Theil bias/var/cov | Direction | "
        f"Top-{TOP_MONTHS} share of SSE | RW ratio |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for _, r in acc.iterrows():
        lines.append(
            f"| {r.Measure} | {r.Region} | {r.Target} | {r.N} | {r.Bias:+.2f} | {r.MAE:.2f} | {r.RMSE:.2f} | "
            f"{r.Correlation:.2f} | {r.Theil_Bias_Share:.2f}/{r.Theil_Variance_Share:.2f}/{r.Theil_Covariance_Share:.2f} | "
            f"{r.Direction_Accuracy:.0%} | {r[top]:.0%} ({r[f'Top{TOP_MONTHS}_Months']}) | {r.RMSE_Ratio_vs_Random_Walk:.2f} |")
    lines += [
        "",
        f"## Pseudo out-of-sample nowcasts (national MoM, expanding window, first {MIN_TRAIN} months for training)",
        "",
        "| Measure | Target | Model | N | Bias | MAE | RMSE | RW ratio | DM p vs RW |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for _, r in nowcast.iterrows():
        dm = "" if np.isnan(r.DM_p_vs_Random_Walk) else f"{r.DM_p_vs_Random_Walk:.3f}"
        lines.append(f"| {r.Measure} | {r.Target} | {r.Model} | {r.N} | {r.Bias:+.2f} | {r.MAE:.2f} | {r.RMSE:.2f} | "
                     f"{r.RMSE_Ratio_vs_Random_Walk:.2f} | {dm} |")
    lines += [
        "",
        "## Lag profile (synthetic 30-day change ending `lag` days before the 15th of month M)",
        "",
        "| Target | RMSE at lag 0 | Lowest RMSE (lag) | Corr at lag 0 | Highest corr (lag) |",
        "|---|---|---|---|---|",
    ]
    for target, g in lags.groupby("Target", sort=False):
        g = g.set_index("Lag_Days")
        lo, hi = g.RMSE.idxmin(), g.Correlation.idxmax()
        lines.append(f"| {target} | {g.RMSE[0]:.2f} | {g.RMSE[lo]:.2f} ({lo}d) | {g.Correlation[0]:.2f} | "
                     f"{g.Correlation[hi]:.2f} ({hi}d) |")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def run(key, force_charts=False):
    index = INDEXES[key]
    out_dir = os.path.join(index["output_dir"], "accuracy")
    os.makedirs(out_dir, exist_ok=True)

    daily = load_synthetic_daily(index["results_dir"], index["file_name"])
    monthly = load_official_monthly(index["weights"])
    frame = monthly_frame(daily, monthly)
    acc = accuracy_table(frame)
    nowcast = nowcast_evaluation(frame)
    lags = lag_profile(daily, frame)

    # Rounded so float noise across library versions does not create daily diffs
    frame.to_csv(os.path.join(out_dir, "monthly_inflation.csv"), date_format="%Y-%m", float_format="%.6f")
    acc.to_csv(os.path.join(out_dir, "accuracy_table.csv"), index=False, float_format="%.6f")
    nowcast.to_csv(os.path.join(out_dir, "nowcast_evaluation.csv"), index=False, float_format="%.6f")
    lags.to_csv(os.path.join(out_dir, "lag_profile.csv"), index=False, float_format="%.6f")
    write_summary(os.path.join(out_dir, "summary.md"), index["label"], acc, nowcast, lags)

    official_month = f"{monthly.index.max():%Y-%m}"
    if force_charts or not charts_are_current(out_dir, official_month, CHART_FILES):
        plot_errors_by_month(frame, acc, os.path.join(out_dir, "errors_by_month.png"), index["label"])
        plot_lag_profile(lags, os.path.join(out_dir, "lag_profile.png"))
        with open(os.path.join(out_dir, CHARTS_MARKER), "w", encoding="utf-8") as f:
            f.write(official_month + "\n")
        print(f"Redrew {key} accuracy charts for official data through {official_month}")
    print(f"Wrote {key} tracking accuracy to {out_dir}")


def main():
    force_charts = "--force-charts" in sys.argv
    for key, index in INDEXES.items():
        if not os.path.exists(os.path.join(index["results_dir"], "national", index["file_name"])):
            print(f"Skipping {key}: no tracker results yet")
            continue
        run(key, force_charts)


if __name__ == "__main__":
    sys.exit(main())
