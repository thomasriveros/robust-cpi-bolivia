import json
import os
import pandas as pd
from datetime import datetime, timedelta
import requests
from io import StringIO
from src.ingestion import fetch_all_files, HIPERMAXI_GITHUB_API_URL, HIPERMAXI_RAW_DATA_DIR
from src.mapping import load_product_mapping, load_weights, map_products, append_new_mappings, normalize_id
from src.ai_categorizer import categorize_new_products
from src.index import calculate_daily_change, calculate_index

_PRODUCT_NAMES_DF = None

def get_product_name(pid):
    global _PRODUCT_NAMES_DF
    if _PRODUCT_NAMES_DF is None:
        try:
            url = "https://raw.githubusercontent.com/mauforonda/precios/master/data/hipermaxi/la_paz/productos.csv"
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                _PRODUCT_NAMES_DF = pd.read_csv(StringIO(res.text))
            else:
                _PRODUCT_NAMES_DF = pd.DataFrame()
        except:
            _PRODUCT_NAMES_DF = pd.DataFrame()
    
    if not _PRODUCT_NAMES_DF.empty:
        # Columns might be 'id_producto' and 'producto'
        if 'id_producto' in _PRODUCT_NAMES_DF.columns and 'producto' in _PRODUCT_NAMES_DF.columns:
            match = _PRODUCT_NAMES_DF[_PRODUCT_NAMES_DF['id_producto'].astype(str) == str(pid)]
            if not match.empty:
                return match.iloc[0]['producto']
    return f"Unknown Product {pid}"

OUTPUT_DIR = "Hipermaxi"
TRACKER_FILE = os.path.join(OUTPUT_DIR, "hipermaxi_tracker_results.json")
CSV_FILE = os.path.join(OUTPUT_DIR, "hipermaxi_tracker_results.csv")
MAPPING_FILE = "Final_Complete_Categories.csv"

def save_tracker_state(state):
    """Saves the tracker state to JSON."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(TRACKER_FILE, 'w') as f:
        json.dump(state, f, indent=4)

def run_historical_tracker():
    print("Starting Hipermaxi Historical CPI Rebuild...")
    
    # 1. Fetch ALL Data
    all_files = fetch_all_files(repo_url=HIPERMAXI_GITHUB_API_URL, output_dir=HIPERMAXI_RAW_DATA_DIR)
    if not all_files:
        print("No data found. Exiting.")
        return

    # Map "YYYY-MM" -> file_path
    file_map = {}
    for f in all_files:
        basename = os.path.basename(f)
        # Hipermaxi files are like 2026_02.csv.
        key = basename.replace('.csv', '').replace('_', '-')
        file_map[key] = f

    print(f"Found {len(all_files)} monthly files.")

    # 2. Time Range
    first_file_path = all_files[0]
    try:
        print(f"Reading start date from {os.path.basename(first_file_path)}...")
        df_start = pd.read_csv(first_file_path, encoding='latin1')
        
        time_col = next((c for c in df_start.columns if 'fecha' in c or 'time' in c or 'date' in c), None)
        
        if time_col:
            df_start[time_col] = pd.to_datetime(df_start[time_col], errors='coerce')
            start_date = df_start[time_col].min().to_pydatetime()
            print(f"Detected start date: {start_date.strftime('%Y-%m-%d')}")
        else:
             raise ValueError("No date column found")

    except Exception as e:
        print(f"Could not read start date from file: {e}. Fallback to filename.")
        first_file = os.path.basename(first_file_path)
        parts = first_file.replace('.csv', '').split('_')
        start_date = datetime(int(parts[0]), int(parts[1]), 1)

    end_date = datetime.now()
    
    history = []
    
    mapping_dict = load_product_mapping(mapping_file=MAPPING_FILE)
    print(f"Loaded mapping for {len(mapping_dict)} products.")
    
    weights_df = load_weights()
    
    current_date = start_date
    loaded_file_path = None
    loaded_df = None       
    last_valid_mapped_df = None 
    
    current_indices = {cat: 100.0 for cat in weights_df['Category'].unique()}
    active_cats = list(current_indices.keys())
    
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        month_key = current_date.strftime("%Y-%m")
        
        daily_df = None
        target_file = file_map.get(month_key)
        
        if target_file:
            if target_file != loaded_file_path:
                print(f"Loading data file: {os.path.basename(target_file)}")
                try:
                    loaded_df = pd.read_csv(target_file)
                except:
                    loaded_df = pd.read_csv(target_file, encoding='latin1')
                
                time_col = next((c for c in loaded_df.columns if 'fecha' in c or 'time' in c or 'date' in c), None)
                if time_col:
                    loaded_df[time_col] = pd.to_datetime(loaded_df[time_col], errors='coerce', format='mixed')
                    loaded_df = loaded_df.dropna(subset=[time_col])
                
                loaded_file_path = target_file
            
            if loaded_df is not None and not loaded_df.empty:
                 time_col = next((c for c in loaded_df.columns if 'fecha' in c or 'time' in c or 'date' in c), None)
                 if time_col:
                     mask = loaded_df[time_col].dt.date == current_date.date()
                     daily_df = loaded_df[mask].copy()
        
        if daily_df is not None and not daily_df.empty:
            if 'id_producto' in daily_df.columns:
                 daily_df['id'] = daily_df['id_producto']

            # --- AI CATEGORIZATION INTEGRATION ---
            # Identify new products not in mapping_dict
            daily_df['norm_id'] = daily_df['id'].apply(normalize_id)
            unmapped = daily_df[~daily_df['norm_id'].isin(mapping_dict.keys())]
            
            if not unmapped.empty:
                unique_unmapped = unmapped.drop_duplicates(subset=['norm_id'])
                new_products_batch = []
                for _, row in unique_unmapped.iterrows():
                    pid = row['norm_id']
                    if pd.notna(pid):
                        pname = get_product_name(row['id'])
                        new_products_batch.append({"id": pid, "name": str(pname)})
                
                if new_products_batch:
                    # Pass to AI
                    ai_results = categorize_new_products(new_products_batch)
                    if ai_results:
                        append_new_mappings(ai_results, mapping_file=MAPPING_FILE)
                        # Also update local dictionary immediately
                        for item in ai_results:
                            mapping_dict[item["id"]] = item.get("category", "Unmapped")
            # -------------------------------------

            current_mapped = map_products(daily_df, mapping_dict)
            
            if 'precio' in current_mapped.columns:
                current_mapped['price'] = current_mapped['precio']

            present_categories = current_mapped['Category'].unique().tolist()
            
            if last_valid_mapped_df is None:
                pass
            else:
                category_changes = calculate_daily_change(
                    current_mapped, 
                    last_valid_mapped_df, 
                    id_col='mapped_id', price_col='price', category_col='Category'
                )
                
                current_indices, cpi, active_cats = calculate_index(
                    current_indices, 
                    category_changes, 
                    weights_df, 
                    present_categories=present_categories
                )
            
            if current_date == start_date and not current_mapped.empty:
                print(f"Sample mapped data for first day ({date_str}):")
                print(current_mapped[['id', 'Category', 'price']].head())
            
            if last_valid_mapped_df is None:
                from src.index import normalize_weights
                norm_w = normalize_weights(weights_df, list(current_indices.keys()))
                cpi = sum(current_indices[c] * w for c, w in norm_w.items())
            
            last_valid_mapped_df = current_mapped
            
            new_entry = {
                "date": date_str,
                "data_source": os.path.basename(loaded_file_path) if loaded_file_path else "Unknown",
                "cpi": cpi,
                "sub_indices": current_indices.copy(),
                "active_categories": active_cats
            }
            
        else:
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

    state = {"history": history}
    save_tracker_state(state)
    print(f"Saved history ({len(history)} days) to {TRACKER_FILE}")
    export_to_csv(history)

def export_to_csv(history):
    """Flattens history and exports to CSV."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    rows = []
    for entry in history:
        row = {
            "date": entry.get("date"),
            "data_source": entry.get("data_source"),
            "cpi": entry.get("cpi")
        }
        for cat, val in entry.get("sub_indices", {}).items():
            row[cat] = val
        rows.append(row)
        
    df = pd.DataFrame(rows)
    df.to_csv(CSV_FILE, index=False)
    print(f"Exported data to {CSV_FILE}")

if __name__ == "__main__":
    run_historical_tracker()
