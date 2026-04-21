import json
import os
import pandas as pd
from datetime import datetime, timedelta
import requests
from io import StringIO
from src.ingestion import fetch_all_files
from src.mapping import load_product_mapping, load_weights, map_products, append_new_mappings, normalize_id
from src.ai_categorizer import categorize_new_products
from src.index import calculate_daily_change, calculate_index

_PRODUCT_NAMES_DF = None

def get_product_name(pid):
    global _PRODUCT_NAMES_DF
    if _PRODUCT_NAMES_DF is None:
        try:
            url = "https://raw.githubusercontent.com/mauforonda/precios/refs/heads/master/data/hipermaxi/productos.csv"
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                _PRODUCT_NAMES_DF = pd.read_csv(StringIO(res.text))
            else:
                _PRODUCT_NAMES_DF = pd.DataFrame()
        except:
            _PRODUCT_NAMES_DF = pd.DataFrame()
    
    if not _PRODUCT_NAMES_DF.empty:
        if 'id_producto' in _PRODUCT_NAMES_DF.columns and 'producto' in _PRODUCT_NAMES_DF.columns:
            match = _PRODUCT_NAMES_DF[_PRODUCT_NAMES_DF['id_producto'].astype(str) == str(pid)]
            if not match.empty:
                return match.iloc[0]['producto']
    return f"Unknown Product {pid}"

CITIES = ["la_paz", "cochabamba", "santa_cruz"]
MAPPING_FILE = "Final_Complete_Categories.csv"

def save_tracker_state(state, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "hipermaxi_tracker_results.json"), 'w') as f:
        json.dump(state, f, indent=4)

def export_to_csv(history, output_dir):
    os.makedirs(output_dir, exist_ok=True)
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
    df.to_csv(os.path.join(output_dir, "hipermaxi_tracker_results.csv"), index=False)

def run_historical_tracker():
    print("Starting Hipermaxi National CPI Rebuild...")
    weights_df = load_weights()
    all_city_histories = {}
    
    for city in CITIES:
        print(f"\n--- Processing City: {city.upper()} ---")
        output_dir = f"Hipermaxi/{city}"
        raw_data_dir = f"data/hipermaxi/{city}"
        repo_url = f"https://api.github.com/repos/mauforonda/precios/contents/data/hipermaxi/{city}"
        
        all_files = fetch_all_files(repo_url=repo_url, output_dir=raw_data_dir)
        if not all_files:
            print(f"No data found for {city}. Skipping.")
            continue

        file_map = {}
        for f in all_files:
            basename = os.path.basename(f)
            key = basename.replace('.csv', '').replace('_', '-')
            file_map[key] = f

        first_file_path = all_files[0]
        try:
            df_start = pd.read_csv(first_file_path, encoding='latin1')
            time_col = next((c for c in df_start.columns if 'fecha' in c or 'time' in c or 'date' in c), None)
            if time_col:
                df_start[time_col] = pd.to_datetime(df_start[time_col], errors='coerce')
                start_date = df_start[time_col].min().to_pydatetime()
            else:
                 raise ValueError("No date column")
        except:
            parts = os.path.basename(first_file_path).replace('.csv', '').split('_')
            start_date = datetime(int(parts[0]), int(parts[1]), 1)

        end_date = datetime.now()
        history = []
        mapping_dict = load_product_mapping(mapping_file=MAPPING_FILE)
        
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
            
            if target_file and target_file != loaded_file_path:
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
                        ai_results = categorize_new_products(new_products_batch)
                        if ai_results:
                            append_new_mappings(ai_results, mapping_file=MAPPING_FILE)
                            for item in ai_results:
                                mapping_dict[item["id"]] = item.get("category", "Unmapped")

                current_mapped = map_products(daily_df, mapping_dict)
                if 'precio' in current_mapped.columns:
                    current_mapped['price'] = current_mapped['precio']
                
                present_categories = current_mapped['Category'].unique().tolist()
                
                if last_valid_mapped_df is not None:
                    category_changes = calculate_daily_change(
                        current_mapped, last_valid_mapped_df, 
                        id_col='mapped_id', price_col='price', category_col='Category'
                    )
                    current_indices, cpi, active_cats = calculate_index(
                        current_indices, category_changes, weights_df, present_categories=present_categories
                    )
                
                if last_valid_mapped_df is None:
                    from src.index import normalize_weights
                    norm_w = normalize_weights(weights_df, list(current_indices.keys()))
                    cpi = sum(current_indices[c] * w for c, w in norm_w.items())
                
                last_valid_mapped_df = current_mapped
                
                history.append({
                    "date": date_str,
                    "data_source": os.path.basename(loaded_file_path) if loaded_file_path else "Unknown",
                    "cpi": cpi,
                    "sub_indices": current_indices.copy(),
                    "active_categories": active_cats
                })
            else:
                from src.index import normalize_weights
                norm_w = normalize_weights(weights_df, active_cats)
                cpi = sum(current_indices[c] * w for c, w in norm_w.items())
                history.append({
                    "date": date_str,
                    "data_source": "Forward Fill",
                    "cpi": cpi,
                    "sub_indices": current_indices.copy(),
                    "active_categories": active_cats
                })
            
            current_date += timedelta(days=1)

        state = {"history": history}
        save_tracker_state(state, output_dir)
        export_to_csv(history, output_dir)
        all_city_histories[city] = history
        print(f"[{city.upper()}] Done! Saved {len(history)} days of history.")
        
    aggregate_national_cpi(all_city_histories)

def aggregate_national_cpi(all_city_histories):
    print("\n--- Aggregating National CPI ---")
    
    # Load Weights
    weights_path = "City Weights.csv"
    if not os.path.exists(weights_path):
        print(f"ERROR: {weights_path} not found. Cannot calculate national CPI.")
        return
        
    city_weights = pd.read_csv(weights_path)
    
    # We map names explicitly
    weight_map = {}
    for _, row in city_weights.iterrows():
        n = str(row["City"]).lower().strip().replace(" ", "_")
        weight_map[n] = float(row["Weight"])
    
    # Align DataFrames
    dfs = []
    for city, history in all_city_histories.items():
        if city not in weight_map:
            print(f"Warning: {city} has no defined weight. Skipping in national aggregation.")
            continue
            
        df = pd.DataFrame(history)
        if df.empty: continue
        
        df = df[["date", "cpi"]].copy()
        df.rename(columns={"cpi": f"{city}_cpi"}, inplace=True)
        dfs.append(df)
        
    if not dfs:
        print("No valid city data to aggregate.")
        return
        
    # Merge on date
    national_df = dfs[0]
    for i in range(1, len(dfs)):
        national_df = pd.merge(national_df, dfs[i], on="date", how="outer")
        
    national_df = national_df.sort_values(by="date").fillna(method="ffill").fillna(method="bfill")
    
    # Compute Weighted Average
    def calc_weighted_avg(row):
        total_val = 0.0
        total_weight = 0.0
        for city, w in weight_map.items():
            col = f"{city}_cpi"
            if col in row and pd.notna(row[col]):
                total_val += row[col] * w
                total_weight += w
        if total_weight == 0: return 100.0
        return total_val / total_weight

    national_df["cpi"] = national_df.apply(calc_weighted_avg, axis=1)
    
    # Export National
    out_dir = "Hipermaxi/national"
    os.makedirs(out_dir, exist_ok=True)
    national_df.to_csv(os.path.join(out_dir, "hipermaxi_tracker_results.csv"), index=False)
    national_df.to_json(os.path.join(out_dir, "hipermaxi_tracker_results.json"), orient="records", indent=4)
    print(f"Successfully generated National CPI! Saved to {out_dir}")

if __name__ == "__main__":
    run_historical_tracker()
