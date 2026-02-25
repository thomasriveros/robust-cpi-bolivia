import json
import os
import pandas as pd
from datetime import datetime
from datetime import datetime, timedelta
from src.ingestion import fetch_all_files, FIDALGA_GITHUB_API_URL, FIDALGA_RAW_DATA_DIR
from src.mapping import load_product_mapping, load_weights, map_products
from src.index import calculate_daily_change, calculate_index

TRACKER_FILE = "fidalga_tracker_results.json"
CSV_FILE = "fidalga_tracker_results.csv"
MAPPING_FILE = "Fixed Map.csv"

def save_tracker_state(state):
    """Saves the tracker state to JSON."""
    with open(TRACKER_FILE, 'w') as f:
        json.dump(state, f, indent=4)

def run_historical_tracker():
    print("Starting Fidalga Historical CPI Rebuild...")
    
    # 1. Fetch ALL Data
    all_files = fetch_all_files(repo_url=FIDALGA_GITHUB_API_URL, output_dir=FIDALGA_RAW_DATA_DIR)
    if not all_files:
        print("No data found. Exiting.")
        return

    # Map "YYYY-MM" -> file_path
    file_map = {}
    for f in all_files:
        basename = os.path.basename(f)
        # Fidalga files are like 2026_02.csv.
        # We need a robust way to match dates.
        # Identify the month/year from filename.
        key = basename.replace('.csv', '').replace('_', '-')
        file_map[key] = f

    print(f"Found {len(all_files)} monthly files.")

    # 2. Time Range
    # Determine start date from the first file or a fixed date if known.
    # Looking at Fidalga data, let's start from a reasonable point or just iterate through files.
    # Let's derive start date from the sorted files to be safe.
    # Determine start date from the actual content of the first file
    first_file_path = all_files[0]
    try:
        print(f"Reading start date from {os.path.basename(first_file_path)}...")
        df_start = pd.read_csv(first_file_path, encoding='latin1') # Fidalga often latin1
        
        # Identify date column
        time_col = next((c for c in df_start.columns if 'fecha' in c or 'time' in c or 'date' in c), None)
        
        if time_col:
            df_start[time_col] = pd.to_datetime(df_start[time_col], errors='coerce')
            start_date = df_start[time_col].min().to_pydatetime()
            print(f"Detected start date: {start_date.strftime('%Y-%m-%d')}")
        else:
             raise ValueError("No date column found")

    except Exception as e:
        print(f"Could not read start date from file: {e}. Fallback to filename.")
        # Fallback to filename parsing
        first_file = os.path.basename(first_file_path)
        parts = first_file.replace('.csv', '').split('_')
        start_date = datetime(int(parts[0]), int(parts[1]), 1)

    end_date = datetime.now()
    
    history = []
    
    mapping_dict = load_product_mapping(mapping_file=MAPPING_FILE)
    print(f"Loaded mapping for {len(mapping_dict)} products.")
    
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
                
                # Ensure 'fecha' or 'time' column is datetime
                # Fidalga CSVs have 'fecha'
                time_col = next((c for c in loaded_df.columns if 'fecha' in c or 'time' in c or 'date' in c), None)
                if time_col:
                    # Attempt robust parsing with mixed format support
                    # Some files have '2025-06-13 00:00:00' then '2025-06-14'
                    loaded_df[time_col] = pd.to_datetime(loaded_df[time_col], errors='coerce', format='mixed')
                    # Drop rows with invalid dates
                    loaded_df = loaded_df.dropna(subset=[time_col])
                
                loaded_file_path = target_file
            
            # Filter for current date
            if loaded_df is not None and not loaded_df.empty:
                 # Ensure we extracted a time column
                 time_col = next((c for c in loaded_df.columns if 'fecha' in c or 'time' in c or 'date' in c), None)
                 if time_col:
                     # Filter
                     mask = loaded_df[time_col].dt.date == current_date.date()
                     daily_df = loaded_df[mask].copy()
        
        # 2. Process Data
        if daily_df is not None and not daily_df.empty:
            # We have data for this day!
            # Map products
            # Fidalga needs 'id_producto' mapped to 'Category'
            # src/mapping.py logic handles 'id' or 'cal_id' or 'product_id'.
            # Fidalga CSV has 'id_producto'. We might need to rename or ensure mapping handles it.
            # Let's rename 'id_producto' to 'id' temporarily for compatibility if simpler,
            # or rely on `map_products` robust checking.
            if 'id_producto' in daily_df.columns:
                 daily_df['id'] = daily_df['id_producto']

            current_mapped = map_products(daily_df, mapping_dict)
            
            # Fidalga CSV has 'precio', create 'price' column for logic
            if 'precio' in current_mapped.columns:
                current_mapped['price'] = current_mapped['precio']

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
                    id_col='mapped_id', price_col='price', category_col='Category'
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
            
            # Print sample mapping for verification (only once)
            if current_date == start_date and not current_mapped.empty:
                print(f"Sample mapped data for first day ({date_str}):")
                print(current_mapped[['id', 'Category', 'price']].head())
            
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
