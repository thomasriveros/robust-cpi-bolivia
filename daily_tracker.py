import json
import os
import pandas as pd
from datetime import datetime
from src.ingestion import fetch_all_files
from src.mapping import load_product_mapping, load_weights, map_products
from src.index import calculate_daily_change, calculate_index

TRACKER_FILE = "tracker_results.json"
CSV_FILE = "tracker_results.csv"

def save_tracker_state(state):
    """Saves the tracker state to JSON."""
    with open(TRACKER_FILE, 'w') as f:
        json.dump(state, f, indent=4)

from datetime import datetime, timedelta

def run_historical_tracker():
    print("Starting Historical CPI Rebuild (True Daily Series)...")
    
    # 1. Fetch ALL Data
    all_files = fetch_all_files()
    if not all_files:
        print("No data found. Exiting.")
        return

    # Map "YYYY-MM" -> file_path
    file_map = {}
    for f in all_files:
        basename = os.path.basename(f)
        key = basename.replace('.csv', '').replace('_', '-')
        file_map[key] = f

    print(f"Found {len(all_files)} monthly files.")

    # 2. Time Range
    start_date = datetime(2021, 11, 1)
    end_date = datetime.now()
    
    history = []
    
    mapping_dict = load_product_mapping()
    weights_df = load_weights()
    
    # State tracking
    current_date = start_date
    
    # We cache the currently loaded CSV to avoid re-reading every day
    loaded_file_path = None
    loaded_df = None       # Raw dataframe of the month
    
    # "Last Valid" state for Matched Model comparison
    # We compare Current Day vs Last Day with Data
    last_valid_mapped_df = None 
    
    # Current Indices state
    current_indices = {cat: 100.0 for cat in weights_df['Category'].unique()}
    active_cats = list(current_indices.keys())
    
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        month_key = current_date.strftime("%Y-%m")
        
        # 1. Get Data for TODAY
        daily_df = None
        
        # Determine file for this month
        target_file = file_map.get(month_key)
        
        if target_file:
            # Check if we need to load/reload file
            if target_file != loaded_file_path:
                print(f"Loading data file: {os.path.basename(target_file)}")
                try:
                    loaded_df = pd.read_csv(target_file)
                except:
                    loaded_df = pd.read_csv(target_file, encoding='latin1')
                
                # Ensure 'time' column is datetime
                # Possible names: 'time', 'date', 'scraped_at'
                # Inspecting 2021_11.csv showed 'time' column: 2021-11-15
                time_col = next((c for c in loaded_df.columns if 'time' in c or 'date' in c), None)
                if time_col:
                    loaded_df[time_col] = pd.to_datetime(loaded_df[time_col])
                
                loaded_file_path = target_file
            
            # Filter for current date
            if loaded_df is not None and not loaded_df.empty:
                 # Ensure we extracted a time column
                 time_col = next((c for c in loaded_df.columns if 'time' in c or 'date' in c), None)
                 if time_col:
                     # Filter
                     mask = loaded_df[time_col].dt.date == current_date.date()
                     daily_df = loaded_df[mask].copy()
        
        # 2. Process Data
        if daily_df is not None and not daily_df.empty:
            # We have data for this day!
            current_mapped = map_products(daily_df, mapping_dict)
            present_categories = current_mapped['Category'].unique().tolist()
            
            if last_valid_mapped_df is None:
                # First day with data ever. Initialize base.
                # Use default 100.0 indices (already set)
                # Just update active categories
                pass
            
            else:
                # Calculate Change vs Last Valid Day
                category_changes = calculate_daily_change(
                    current_mapped, 
                    last_valid_mapped_df, 
                    id_col='id', price_col='price', category_col='Category'
                )
                
                # Update Indices
                current_indices, cpi, active_cats = calculate_index(
                    current_indices, 
                    category_changes, 
                    weights_df, 
                    present_categories=present_categories
                )
            
            # Recalculate CPI for the record (even if no change, or if first day)
            # (calculate_index does it, but for first day we might skip the block above)
            
            # If we didn't run calculate_index (first day), we calculate CPI manually
            if last_valid_mapped_df is None:
                # Manual CPI calc
                # normalize weights
                from src.index import normalize_weights
                norm_w = normalize_weights(weights_df, list(current_indices.keys()))
                cpi = sum(current_indices[c] * w for c, w in norm_w.items())
            
            # Update Last Valid
            last_valid_mapped_df = current_mapped
            
            new_entry = {
                "date": date_str,
                "data_source": os.path.basename(loaded_file_path) if loaded_file_path else "Unknown",
                "cpi": cpi,
                "sub_indices": current_indices.copy(),
                "active_categories": active_cats
            }
            
        else:
            # No data for this day (Gap or Future)
            # Carry forward
            
            # Valid CPI?
            from src.index import normalize_weights
            norm_w = normalize_weights(weights_df, active_cats)
            cpi = sum(current_indices[c] * w for c, w in norm_w.items())
            
            new_entry = {
                "date": date_str,
                "data_source": "Forward Fill",
                "cpi": cpi,
                "sub_indices": current_indices.copy(),
                "active_categories": active_cats
            }
            
        history.append(new_entry)
        current_date += timedelta(days=1)

    # 3. Save
    state = {"history": history}
    save_tracker_state(state)
    print(f"Saved history ({len(history)} days) to {TRACKER_FILE}")
    export_to_csv(history)

def export_to_csv(history):
    """Flattens history and exports to CSV."""
    rows = []
    for entry in history:
        row = {
            "date": entry.get("date"),
            "data_source": entry.get("data_source"),
            "cpi": entry.get("cpi")
        }
        # Flatten sub-indices
        for cat, val in entry.get("sub_indices", {}).items():
            row[cat] = val
        rows.append(row)
        
    df = pd.DataFrame(rows)
    df.to_csv(CSV_FILE, index=False)
    print(f"Exported data to {CSV_FILE}")

if __name__ == "__main__":
    run_historical_tracker()
