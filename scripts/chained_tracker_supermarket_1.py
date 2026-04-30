"""
scripts/chained_tracker_supermarket_1.py
=========================================
Monthly-Chained Daily CPI Tracker — Supermarket 1 (Hipermaxi)
Three cities: La Paz, Cochabamba, Santa Cruz + National aggregation

Methodology: Monthly-Chained Daily Jevons Index (see src/chained_index.py).
Legacy matched-model tracker preserved at: scripts/_legacy/daily_tracker_supermarket_1.py
Output: results/chained/supermarket_1/{city}/ and results/chained/supermarket_1/national/
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import numpy as np
import pandas as pd
import requests
from io import StringIO
from datetime import datetime, timedelta

from src.ingestion import fetch_all_files
from src.mapping import load_product_mapping, map_products, normalize_id, append_new_mappings
from src.chained_index import (
    build_link_prices,
    calculate_direct_relative,
    compute_total_cpi,
    CHAINED_CORE_CATEGORIES,
)

try:
    from src.ai_categorizer import categorize_new_products
except ImportError:
    categorize_new_products = None

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
ENABLE_AI_CATEGORIZATION = bool(os.getenv("GEMINI_API_KEY"))

CITIES = ["la_paz", "cochabamba", "santa_cruz"]
MAPPING_FILE  = "mappings/Final_Complete_Categories.csv"
CITY_WEIGHTS_FILE = "config/City Weights.csv"
OUTPUT_BASE   = "results/chained/supermarket_1"
MIN_N         = 10   # Minimum products per category for the monthly BASKET SNAPSHOT
MIN_N_DAILY   = 1    # Minimum matched products for daily Jevons — no floor once
                     # the category is in the basket (snapshot already enforces quality)

# Outlier filter bounds for within-month price relatives (P_d / P_month_start).
# Set to None to disable filtering entirely (recommended for monthly-chained
# indexes — no chain-drift risk, and strict caps cause downward bias).
# To re-enable, e.g.: OUTLIER_LOWER, OUTLIER_UPPER = 0.45, 1/0.45
OUTLIER_LOWER = None
OUTLIER_UPPER = None


# ---------------------------------------------------------------------------
# Product name lookup (for AI categorization)
# ---------------------------------------------------------------------------
_PRODUCT_NAMES_DF = None

def _get_product_name(pid):
    global _PRODUCT_NAMES_DF
    if _PRODUCT_NAMES_DF is None:
        try:
            url = ("https://raw.githubusercontent.com/mauforonda/precios"
                   "/refs/heads/master/data/hipermaxi/productos.csv")
            res = requests.get(url, timeout=10)
            _PRODUCT_NAMES_DF = pd.read_csv(StringIO(res.text)) if res.status_code == 200 else pd.DataFrame()
        except Exception:
            _PRODUCT_NAMES_DF = pd.DataFrame()

    if not _PRODUCT_NAMES_DF.empty:
        if "id_producto" in _PRODUCT_NAMES_DF.columns and "producto" in _PRODUCT_NAMES_DF.columns:
            match = _PRODUCT_NAMES_DF[_PRODUCT_NAMES_DF["id_producto"].astype(str) == str(pid)]
            if not match.empty:
                return match.iloc[0]["producto"]
    return f"Unknown Product {pid}"


# ---------------------------------------------------------------------------
# File helpers
# ---------------------------------------------------------------------------

def _load_monthly_file(path):
    """Load a Hipermaxi monthly CSV and parse the date column."""
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
    """Filter, map, and prepare daily data. Returns mapped DataFrame or None."""
    if raw_df is None or raw_df.empty or time_col is None:
        return None

    mask = raw_df[time_col].dt.date == target_date.date()
    daily = raw_df[mask].copy()
    if daily.empty:
        return None

    if "id_producto" in daily.columns:
        daily["id"] = daily["id_producto"]

    daily["norm_id"] = daily["id"].apply(normalize_id)

    # Optional AI categorization for unmapped products
    if ENABLE_AI_CATEGORIZATION and categorize_new_products is not None:
        unmapped = daily[~daily["norm_id"].isin(mapping_dict.keys())]
        if not unmapped.empty:
            unique_unmapped = unmapped.drop_duplicates(subset=["norm_id"])
            new_products = [
                {"id": row["norm_id"], "name": str(_get_product_name(row["id"]))}
                for _, row in unique_unmapped.iterrows()
                if pd.notna(row["norm_id"])
            ]
            if new_products:
                for i in range(0, len(new_products), 50):
                    batch = new_products[i:i + 50]
                    ai_results = categorize_new_products(batch)
                    if ai_results:
                        valid = [x for x in ai_results if x.get("confidence") != "failed"]
                        if valid:
                            append_new_mappings(valid, mapping_file=MAPPING_FILE)
                        for item in ai_results:
                            mapping_dict[item["id"]] = item.get("category", "Unmapped")

    mapped = map_products(daily, mapping_dict)

    if "precio" in mapped.columns:
        mapped["price"] = mapped["precio"]

    return mapped if not mapped.empty else None


# ---------------------------------------------------------------------------
# Per-city tracker
# ---------------------------------------------------------------------------

def _run_city(city, mapping_dict):
    """
    Run the monthly-chained tracker for a single city.
    Returns the history list (one entry per day).
    """
    print(f"\n{'─' * 50}")
    print(f"  Processing: {city.upper()}")
    print(f"{'─' * 50}")

    output_dir = os.path.join(OUTPUT_BASE, city)
    raw_data_dir = f"data/hipermaxi/{city}"
    repo_url = (
        f"https://api.github.com/repos/mauforonda/precios"
        f"/contents/data/hipermaxi/{city}"
    )

    all_files = fetch_all_files(repo_url=repo_url, output_dir=raw_data_dir)
    if not all_files:
        print(f"  No data found for {city}. Skipping.")
        return []

    file_map = {
        os.path.basename(f).replace(".csv", "").replace("_", "-"): f
        for f in all_files
    }
    print(f"  {len(all_files)} monthly files found.")

    # Determine start date
    try:
        df_s, tc_s = _load_monthly_file(all_files[0])
        start_date = df_s[tc_s].min().to_pydatetime()
    except Exception:
        parts = os.path.basename(all_files[0]).replace(".csv", "").split("_")
        start_date = datetime(int(parts[0]), int(parts[1]), 1)

    end_date = datetime.now()

    # -------------------------------------------------------------------------
    # State  (R-equivalent hybrid methodology)
    # -------------------------------------------------------------------------
    # link_prices_df : mean prices from the PREVIOUS month (P_avg_M-1)
    #   → used as the denominator for today's Jevons relative
    # running_multiplier : cumprod of last-day relatives at each month boundary
    #   → replicates R's cumprod(chain_multiplier) step
    # last_relative : last weighted national relative (used as chain_multiplier
    #   at the next month boundary)
    # month_data_accum : accumulates all today_mapped DataFrames for the current
    #   month, so we can compute link_prices_df for the NEXT month
    # -------------------------------------------------------------------------
    link_prices_df     = None
    link_active_cats   = []
    running_multiplier = 1.0
    last_relative      = 1.0
    month_relatives    = []   # daily nat_relatives this month → mean used as chain link
    last_cpi           = 100.0
    current_month      = None
    month_data_accum   = []

    loaded_file_path = None
    loaded_df        = None
    loaded_time_col  = None

    history = []

    # ---- Day loop ------------------------------------------------------------
    current_date = start_date
    while current_date <= end_date:
        date_str  = current_date.strftime("%Y-%m-%d")
        month_key = current_date.strftime("%Y-%m")

        # Load/cache monthly file
        target_file = file_map.get(month_key)
        if target_file and target_file != loaded_file_path:
            print(f"  Loading: {os.path.basename(target_file)}")
            loaded_df, loaded_time_col = _load_monthly_file(target_file)
            loaded_file_path = target_file

        today_mapped = _prepare_daily_df(
            loaded_df, loaded_time_col, current_date, mapping_dict
        )

        # ---- Month transition ------------------------------------------------
        if month_key != current_month:
            if current_month is not None and month_data_accum:
                # Build link prices from the just-completed month's data
                all_month = pd.concat(month_data_accum, ignore_index=True)
                new_link, new_cats = build_link_prices(
                    all_month, id_col="mapped_id", price_col="price",
                    category_col="Category", min_n=MIN_N,
                )
                if new_link is not None:
                    if link_prices_df is not None:
                        # Chain link = MEAN relative across the completed month.
                        # Using the last-day relative caused upward bias because
                        # end-of-month prices > monthly average when prices trend up.
                        chain_link = float(np.mean(month_relatives)) if month_relatives else last_relative
                        running_multiplier *= chain_link
                        print(f"  [LINK] {current_month} → {month_key} "
                              f"| chain={chain_link:.4f} multiplier={running_multiplier:.4f}")
                    link_prices_df   = new_link
                    link_active_cats = new_cats
                month_relatives = []  # reset for new month

            month_data_accum = []
            current_month = month_key
            if link_prices_df is None:
                print(f"  [BASE MONTH] {month_key} — accumulating link prices, no index yet")
            else:
                print(f"  [NEW MONTH ] {month_key} | link cats: {link_active_cats}")

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
            cpi = last_cpi  # carry forward last known value

        history.append({
            "date":        date_str,
            "month":       month_key,
            "data_source": data_source,
            "cpi":         round(cpi, 6),
        })

        current_date += timedelta(days=1)

    # Save city results
    os.makedirs(output_dir, exist_ok=True)
    json_path = os.path.join(output_dir, "chained_cpi_results.json")
    csv_path  = os.path.join(output_dir, "chained_cpi_results.csv")

    with open(json_path, "w") as f:
        json.dump({"history": history}, f, indent=4)

    pd.DataFrame(history).to_csv(csv_path, index=False)
    print(f"  [{city.upper()}] Done — {len(history)} days saved to {csv_path}")
    return history


# ---------------------------------------------------------------------------
# National aggregation
# ---------------------------------------------------------------------------

def _aggregate_national(all_city_histories):
    """Weighted average of city CPIs using official city weights."""
    print("\n" + "=" * 50)
    print("  Aggregating National Chained CPI")
    print("=" * 50)

    if not os.path.exists(CITY_WEIGHTS_FILE):
        print(f"  ERROR: {CITY_WEIGHTS_FILE} not found. Skipping national aggregation.")
        return

    city_weights_df = pd.read_csv(CITY_WEIGHTS_FILE)
    weight_map = {
        str(row["City"]).lower().strip().replace(" ", "_"): float(row["Weight"])
        for _, row in city_weights_df.iterrows()
    }

    # Build per-city DataFrames
    dfs = []
    for city, history in all_city_histories.items():
        if not history:
            continue
        if city not in weight_map:
            print(f"  Warning: no city weight defined for '{city}'. Skipping.")
            continue
        df = pd.DataFrame(history)[["date", "cpi"]].copy()
        df = df.rename(columns={"cpi": f"{city}_cpi"})
        dfs.append(df)

    if not dfs:
        print("  No valid city data to aggregate.")
        return

    national = dfs[0]
    for d in dfs[1:]:
        national = pd.merge(national, d, on="date", how="outer")

    national = national.sort_values("date")
    national = national.ffill().bfill()

    def _weighted_avg(row):
        total_val, total_w = 0.0, 0.0
        for city, w in weight_map.items():
            col = f"{city}_cpi"
            if col in row and pd.notna(row[col]):
                total_val += row[col] * w
                total_w   += w
        return total_val / total_w if total_w > 0 else 100.0

    national["cpi"] = national.apply(_weighted_avg, axis=1)

    out_dir = os.path.join(OUTPUT_BASE, "national")
    os.makedirs(out_dir, exist_ok=True)

    csv_path  = os.path.join(out_dir, "chained_cpi_results.csv")
    json_path = os.path.join(out_dir, "chained_cpi_results.json")

    national.to_csv(csv_path, index=False)
    national.to_json(json_path, orient="records", indent=4)
    print(f"  National CPI saved to {csv_path}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def run_chained_tracker():
    print("=" * 60)
    print("Supermarket 1 — Monthly-Chained Daily CPI Tracker")
    print("=" * 60)

    mapping_dict = load_product_mapping(mapping_file=MAPPING_FILE)
    print(f"Loaded mapping for {len(mapping_dict)} products.\n")

    all_city_histories = {}
    for city in CITIES:
        history = _run_city(city, mapping_dict)
        all_city_histories[city] = history

    _aggregate_national(all_city_histories)
    print("\nAll done!")


if __name__ == "__main__":
    run_chained_tracker()
