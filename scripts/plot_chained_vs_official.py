"""
scripts/plot_chained_vs_official.py
=====================================
Plots the Monthly-Chained Daily CPI (Supermarket 1 / Hipermaxi) against
the official synthetic equivalent basket CPI from:
    config/Synth. Eq Official.xlsx

Produces a 2x2 figure: La Paz | Cochabamba | Santa Cruz | National
Saves to: results/chained/supermarket_1/comparison_plot.png

Usage:
    source cpi_env/bin/activate
    python scripts/plot_chained_vs_official.py
"""

import os
import sys
import warnings
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
from matplotlib.lines import Line2D

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
EXCEL_PATH   = "config/Synth. Eq Official.xlsx"
RESULTS_BASE = "results/chained/supermarket_1"
OUTPUT_PATH  = os.path.join(RESULTS_BASE, "comparison_plot.png")

# Maps Excel tab name → (city folder, official CPI column name)
CITY_CONFIG = {
    "La Paz": (
        "la_paz",
        "CPI Equ. Basket",
    ),
    "Cochabamba": (
        "cochabamba",
        "CPI Equ. Basket",
    ),
    "Santa Cruz": (
        "santa_cruz",
        "Same Basket CPI Santa Cruz",
    ),
    "National": (
        "national",
        "CPI Equ. Basket",
    ),
}

# ---------------------------------------------------------------------------
# Style
# ---------------------------------------------------------------------------
DARK_BG     = "#0f1117"
PANEL_BG    = "#1a1d27"
GRID_COLOR  = "#2a2d3a"
TEXT_COLOR  = "#e8eaf0"
ACCENT1     = "#7c6af7"   # chained daily — violet
ACCENT2     = "#f0a500"   # official monthly — amber
LINK_COLOR  = "#3a3d50"   # month boundary lines

plt.rcParams.update({
    "figure.facecolor":  DARK_BG,
    "axes.facecolor":    PANEL_BG,
    "axes.edgecolor":    GRID_COLOR,
    "axes.labelcolor":   TEXT_COLOR,
    "xtick.color":       TEXT_COLOR,
    "ytick.color":       TEXT_COLOR,
    "text.color":        TEXT_COLOR,
    "grid.color":        GRID_COLOR,
    "grid.linewidth":    0.6,
    "font.family":       "sans-serif",
    "font.size":         10,
})


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_official(tab_name, cpi_col):
    """Load and return the official monthly CPI series for one tab."""
    df = pd.read_excel(EXCEL_PATH, sheet_name=tab_name, parse_dates=["Date"])
    df = df[["Date", cpi_col]].rename(columns={cpi_col: "official_cpi"})
    df = df.dropna(subset=["Date", "official_cpi"])
    df = df.sort_values("Date")
    return df


def load_chained(city_folder):
    """Load and return the daily chained CPI for one city/national."""
    csv_path = os.path.join(RESULTS_BASE, city_folder, "chained_cpi_results.csv")
    if not os.path.exists(csv_path):
        return None
    df = pd.read_csv(csv_path, parse_dates=["date"])
    df = df[["date", "cpi"]].dropna()
    df = df.sort_values("date")
    return df


def rebase_to_100(series, ref_date):
    """Re-index a Series so it equals 100 at ref_date (nearest available)."""
    # Find the closest date
    idx = (series.index - ref_date).abs().argmin()
    base_val = series.iloc[idx]
    if base_val == 0:
        return series
    return series / base_val * 100.0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    fig, axes = plt.subplots(
        2, 2,
        figsize=(14, 9),
        sharex=False,
    )
    axes_flat = axes.flatten()

    panel_order = ["La Paz", "Cochabamba", "Santa Cruz", "National"]
    any_chained = False

    for ax, tab_name in zip(axes_flat, panel_order):
        city_folder, cpi_col = CITY_CONFIG[tab_name]

        # --- Load data ---
        try:
            official = load_official(tab_name, cpi_col)
        except Exception as e:
            ax.text(0.5, 0.5, f"Official data error:\n{e}",
                    ha="center", va="center", transform=ax.transAxes,
                    color="tomato", fontsize=9)
            ax.set_title(tab_name, fontsize=12, fontweight="bold", pad=10)
            continue

        chained = load_chained(city_folder)

        # --- Rebase both series to 100 at their shared start ---
        # Find the earliest common date
        off_start = official["Date"].min()
        if chained is not None and not chained.empty:
            chain_start = chained["date"].min()
            common_start = max(off_start, chain_start)
        else:
            common_start = off_start

        # Rebase official to 100 at common_start
        off_s = official.set_index("Date")["official_cpi"]
        off_s = off_s.sort_index()
        off_rebase = off_start  # official already starts at 100 in July 2024

        # --- Plot official (monthly dots + line) ---
        ax.plot(
            official["Date"], official["official_cpi"],
            color=ACCENT2, linewidth=1.5, linestyle="--",
            marker="o", markersize=5, markerfacecolor=ACCENT2,
            markeredgewidth=0, zorder=3,
            label="Official Synthetic Basket (Monthly)",
        )

        # --- Plot chained daily ---
        if chained is not None and not chained.empty:
            any_chained = True

            # Align base: rebase chained to 100 at official start date
            # (find the chained value on or just after off_start)
            chain_at_start = chained[chained["date"] >= off_start]
            if not chain_at_start.empty:
                base_val = chain_at_start.iloc[0]["cpi"]
                chained = chained.copy()
                chained["cpi_rebased"] = chained["cpi"] / base_val * 100.0
            else:
                chained["cpi_rebased"] = chained["cpi"]

            ax.plot(
                chained["date"], chained["cpi_rebased"],
                color=ACCENT1, linewidth=1.6, alpha=0.95, zorder=4,
                label="Monthly-Chained Daily CPI (Supermarket 1)",
            )

            # Subtle vertical lines at month boundaries
            month_boundaries = (
                chained["date"]
                .dt.to_period("M")
                .drop_duplicates()
                .apply(lambda p: p.to_timestamp())
            )
            for mb in month_boundaries:
                ax.axvline(mb, color=LINK_COLOR, linewidth=0.5,
                           linestyle=":", alpha=0.7, zorder=1)
        else:
            ax.text(
                0.5, 0.45,
                "Chained CPI not yet available\n(tracker still running?)",
                ha="center", va="center", transform=ax.transAxes,
                color="#888899", fontsize=9, style="italic",
            )

        # --- Formatting ---
        ax.set_title(tab_name, fontsize=12, fontweight="bold",
                     color=TEXT_COLOR, pad=10)
        ax.set_ylabel("Index (Jul 2024 = 100)", fontsize=9, labelpad=6)
        ax.yaxis.set_major_formatter(ticker.FormatStrFormatter("%.1f"))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b '%y"))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=30, ha="right",
                 fontsize=8)
        ax.grid(True, axis="both", alpha=0.5)
        ax.spines[["top", "right"]].set_visible(False)

        # Compute and display RMSE if both series available
        if chained is not None and not chained.empty and "cpi_rebased" in chained.columns:
            # Merge on nearest month for RMSE
            off_m = official.copy()
            off_m["month"] = off_m["Date"].dt.to_period("M")
            cha_m = chained.copy()
            cha_m["month"] = cha_m["date"].dt.to_period("M")
            # Take last day of each month in chained as month-end
            cha_eom = cha_m.groupby("month")["cpi_rebased"].last().reset_index()
            merged = pd.merge(off_m[["month","official_cpi"]], cha_eom, on="month")
            if not merged.empty:
                rmse = ((merged["official_cpi"] - merged["cpi_rebased"])**2).mean()**0.5
                mae  = (merged["official_cpi"] - merged["cpi_rebased"]).abs().mean()
                ax.text(
                    0.03, 0.97,
                    f"RMSE: {rmse:.2f} pts\nMAE:  {mae:.2f} pts",
                    transform=ax.transAxes,
                    va="top", ha="left", fontsize=8,
                    color=TEXT_COLOR, alpha=0.8,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor=DARK_BG,
                              edgecolor=GRID_COLOR, alpha=0.7),
                )

    # --- Shared legend ---
    legend_handles = [
        Line2D([0], [0], color=ACCENT1, linewidth=2,
               label="Monthly-Chained Daily CPI (Supermarket 1)"),
        Line2D([0], [0], color=ACCENT2, linewidth=1.5, linestyle="--",
               marker="o", markersize=5,
               label="Official Synthetic Basket (Monthly)"),
        Line2D([0], [0], color=LINK_COLOR, linewidth=0.8, linestyle=":",
               label="Month Chain-Link Boundary"),
    ]
    fig.legend(
        handles=legend_handles,
        loc="lower center",
        ncol=3,
        frameon=True,
        framealpha=0.15,
        edgecolor=GRID_COLOR,
        fontsize=9,
        bbox_to_anchor=(0.5, 0.01),
    )

    # --- Title & layout ---
    fig.suptitle(
        "Monthly-Chained Daily Synthetic CPI vs. Official Basket Equivalent",
        fontsize=14, fontweight="bold", color=TEXT_COLOR, y=0.99,
    )
    fig.text(
        0.5, 0.965,
        "Supermarket 1 (Hipermaxi) · Core 5 Categories · Base: July 2024 = 100",
        ha="center", fontsize=9, color="#888899",
    )

    plt.tight_layout(rect=[0, 0.07, 1, 0.96])

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    fig.savefig(OUTPUT_PATH, dpi=160, bbox_inches="tight",
                facecolor=DARK_BG)
    print(f"Plot saved to: {OUTPUT_PATH}")
    plt.show()


if __name__ == "__main__":
    main()
