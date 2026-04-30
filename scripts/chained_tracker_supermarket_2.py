"""
scripts/chained_tracker_supermarket_2.py
=========================================
Monthly-Chained Daily CPI Tracker — Supermarket 2 (Fidalga)

Methodology: Monthly-Chained Daily Jevons Index (see src/chained_index.py).
Legacy matched-model tracker preserved at: scripts/_legacy/daily_tracker_supermarket_2.py
Output: results/chained/supermarket_2/
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

from src.ingestion import fetch_all_files, FIDALGA_GITHUB_API_URL, FIDALGA_RAW_DATA_DIR
from src.mapping import load_product_mapping, map_products, normalize_id
from src.chained_index import (
    build_link_prices,
    calculate_direct_relative,
    compute_total_cpi,
    CHAINED_CORE_CATEGORIES,
)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
MAPPING_FILE = "mappings/Fixed Map.csv"
OUTPUT_DIR   = "results/chained/supermarket_2"
OUTPUT_JSON  = os.path.join(OUTPUT_DIR, "chained_cpi_results.json")
OUTPUT_CSV   = os.path.join(OUTPUT_DIR, "chained_cpi_results.csv")
MIN_N        = 10   # Minimum products per category for the monthly BASKET SNAPSHOT
MIN_N_DAILY  = 1    # Minimum matched products for daily Jevons — no floor once
                    # the category is in the basket (snapshot already enforces quality)

# Outlier filter bounds for within-month price relatives (P_d / P_month_start).
# Set to None to disable filtering entirely (recommended for monthly-chained
# indexes — no chain-drift risk, and strict caps cause downward bias).
# To re-enable, e.g.: OUTLIER_LOWER, OUTLIER_UPPER = 0.45, 1/0.45
OUTLIER_LOWER = None
OUTLIER_UPPER = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_monthly_file(path):
    """Load a Fidalga monthly CSV, parse the date column, return DataFrame."""
    try:
        df = pd.read_csv(path)
    except Exception:
        df = pd.read_csv(path, encoding="latin1")

    time_col = next(
        (c for c in df.columns if any(k in c.lower() for k in ("fecha", "time", "date"))),
        None,
    )
    if time_col:
        df[time_col] = pd.to_datetime(df[time_col], errors="coerce", format="mixed")
        df = df.dropna(subset=[time_col])

    return df, time_col


def _prepare_daily_df(raw_df, time_col, target_date, mapping_dict):
    """Filter to target_date, rename columns, map products. Returns mapped DataFrame or None."""
    if raw_df is None or raw_df.empty or time_col is None:
        return None

    mask = raw_df[time_col].dt.date == target_date.date()
    daily = raw_df[mask].copy()

    if daily.empty:
        return None

    # Normalise ID column for Fidalga files
    if "id_producto" in daily.columns:
        daily["id"] = daily["id_producto"]

    daily["norm_id"] = daily["id"].apply(normalize_id)
    mapped = map_products(daily, mapping_dict)

    if "precio" in mapped.columns:
        mapped["price"] = mapped["precio"]

    return mapped if not mapped.empty else None


def _save_results(history):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # JSON
    with open(OUTPUT_JSON, "w") as f:
        json.dump({"history": history}, f, indent=4)

    # CSV (flat)
    rows = []
    for entry in history:
        row = {
            "date":        entry["date"],
            "data_source": entry["data_source"],
            "cpi":         entry["cpi"],
            "month":       entry["month"],
        }
        row.update(entry.get("chain_indices", {}))
        rows.append(row)

    pd.DataFrame(rows).to_csv(OUTPUT_CSV, index=False)
    print(f"  Saved {len(history)} days → {OUTPUT_CSV}")


# ---------------------------------------------------------------------------
# Main tracker
# ---------------------------------------------------------------------------

def run_chained_tracker():
    print("=" * 60)
    print("Supermarket 2 — Monthly-Chained Daily CPI Tracker")
    print("=" * 60)

    # 1. Fetch all monthly files
    all_files = fetch_all_files(repo_url=FIDALGA_GITHUB_API_URL, output_dir=FIDALGA_RAW_DATA_DIR)
    if not all_files:
        print("No data files found. Exiting.")
        return

    # Build month_key → file_path map
    file_map = {}
    for f in all_files:
        key = os.path.basename(f).replace(".csv", "").replace("_", "-")
        file_map[key] = f
    print(f"Found {len(all_files)} monthly files.")

    # 2. Determine start date from first file
    first_path = all_files[0]
    try:
        df_start, tc = _load_monthly_file(first_path)
        start_date = df_start[tc].min().to_pydatetime()
        print(f"Start date detected: {start_date.strftime('%Y-%m-%d')}")
    except Exception:
        parts = os.path.basename(first_path).replace(".csv", "").split("_")
        start_date = datetime(int(parts[0]), int(parts[1]), 1)

    end_date = datetime.now()

    # 3. Load product mapping
    mapping_dict = load_product_mapping(mapping_file=MAPPING_FILE)
    print(f"Loaded mapping for {len(mapping_dict)} products.")

    # -------------------------------------------------------------------------
    # State  (R-equivalent hybrid methodology — same as chained_tracker_supermarket_1)
    # -------------------------------------------------------------------------
    link_prices_df     = None
    link_active_cats   = []
    running_multiplier = 1.0
    last_relative      = 1.0
    month_relatives    = []    # daily nat_relatives → mean used as chain link
    last_cpi           = 100.0
    current_month      = None
    month_data_accum   = []

    loaded_file_path = None
    loaded_df        = None
    loaded_time_col  = None

    history = []

    # ---------------------------------------------------------------------------
    # Day loop
    # ---------------------------------------------------------------------------
    current_date = start_date
    while current_date <= end_date:
        date_str  = current_date.strftime("%Y-%m-%d")
        month_key = current_date.strftime("%Y-%m")

        # ---- Load / cache monthly file ----------------------------------------
        target_file = file_map.get(month_key)
        if target_file and target_file != loaded_file_path:
            print(f"  Loading: {os.path.basename(target_file)}")
            loaded_df, loaded_time_col = _load_monthly_file(target_file)
            loaded_file_path = target_file

        # ---- Get today's mapped data ------------------------------------------
        today_mapped = _prepare_daily_df(
            loaded_df, loaded_time_col, current_date, mapping_dict
        )

        # ---- Month transition -------------------------------------------------
        if month_key != current_month:
            if current_month is not None and month_data_accum:
                all_month = pd.concat(month_data_accum, ignore_index=True)
                new_link, new_cats = build_link_prices(
                    all_month, id_col="mapped_id", price_col="price",
                    category_col="Category", min_n=MIN_N,
                )
                if new_link is not None:
                    if link_prices_df is not None:
                        chain_link = float(np.mean(month_relatives)) if month_relatives else last_relative
                        running_multiplier *= chain_link
                        print(f"  [LINK] {current_month} → {month_key} "
                              f"| chain={chain_link:.4f} multiplier={running_multiplier:.4f}")
                    link_prices_df   = new_link
                    link_active_cats = new_cats
                month_relatives = []

            month_data_accum = []
            current_month = month_key
            if link_prices_df is None:
                print(f"  [BASE MONTH] {month_key} — accumulating link prices, no index yet")
            else:
                print(f"  [NEW MONTH ] {month_key} | cats: {link_active_cats}")

        # ---- Daily calculation -----------------------------------------------
        if today_mapped is not None:
            data_source = os.path.basename(loaded_file_path) if loaded_file_path else "Unknown"
            month_data_accum.append(today_mapped.copy())

            if link_prices_df is not None:
                within_rels = calculate_direct_relative(
                    today_mapped, link_prices_df,
                    id_col="mapped_id", price_col="price",
                    category_col="Category", min_n=MIN_N_DAILY,
                    lower_bound=OUTLIER_LOWER, upper_bound=OUTLIER_UPPER,
                )
                nat_relative = compute_total_cpi(
                    within_rels.to_dict(), link_active_cats
                )
                last_relative = nat_relative
                month_relatives.append(nat_relative)
                cpi = 100.0 * nat_relative * running_multiplier
            else:
                cpi = 100.0
                last_relative = 1.0
            last_cpi = cpi
        else:
            data_source = "Forward Fill"
            cpi = last_cpi

        history.append({
            "date":        date_str,
            "month":       month_key,
            "data_source": data_source,
            "cpi":         round(cpi, 6),
        })

        current_date += timedelta(days=1)

    # 4. Save
    _save_results(history)
    print(f"\nDone! {len(history)} days processed.")


if __name__ == "__main__":
    run_chained_tracker()
