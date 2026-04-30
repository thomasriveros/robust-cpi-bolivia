import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
from io import StringIO
from src.ingestion import fetch_all_files
from src.mapping import load_product_mapping, load_weights, map_products, append_new_mappings, normalize_id, CORE_CATEGORIES
try:
    from src.ai_categorizer import categorize_new_products
except ImportError:
    categorize_new_products = None
from src.index import calculate_daily_change, calculate_index

ENABLE_AI_CATEGORIZATION = bool(os.getenv("GEMINI_API_KEY"))

_PRODUCT_DATA_DF = None

def load_product_data():
    global _PRODUCT_DATA_DF
    if _PRODUCT_DATA_DF is None:
        try:
            url = "https://raw.githubusercontent.com/mauforonda/precios/refs/heads/master/data/hipermaxi/productos.csv"
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                df = pd.read_csv(StringIO(res.text))
                # Sanitization: lowercase and strip to handle casing inconsistencies
                for col in ['producto', 'categoria', 'subcategoria']:
                    if col in df.columns:
                        df[col] = df[col].astype(str).str.lower().str.strip()
                _PRODUCT_DATA_DF = df
            else:
                _PRODUCT_DATA_DF = pd.DataFrame()
        except:
            _PRODUCT_DATA_DF = pd.DataFrame()
    return _PRODUCT_DATA_DF

def get_product_name(pid):
    df = load_product_data()
    if not df.empty and 'id_producto' in df.columns and 'producto' in df.columns:
        match = df[df['id_producto'].astype(str) == str(pid)]
        if not match.empty:
            return match.iloc[0]['producto']
    return f"Unknown Product {pid}"

def get_temporada_ids():
    df = load_product_data()
    if not df.empty and 'subcategoria' in df.columns:
        mask = df['subcategoria'].str.contains('temporada', na=False, case=False) | \
               df['categoria'].str.contains('temporada', na=False, case=False) | \
               df['producto'].str.contains('temporada', na=False, case=False)
        return set(df[mask]['id_producto'].astype(str))
    return set()

CITIES = ["la_paz", "cochabamba", "santa_cruz"]
MAPPING_FILE = "mappings/Final_Complete_Categories.csv"

def save_tracker_state(state, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "supermarket_1_tracker_results.json"), 'w') as f:
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
    df.to_csv(os.path.join(output_dir, "supermarket_1_tracker_results.csv"), index=False)

def run_historical_tracker():
    print("Starting Supermarket 1 National CPI Rebuild (Vectorized Mode)...")
    
    # 1. LOAD WEIGHTS EXACTLY AS IN R SCRIPT
    core_basket = pd.DataFrame({
        'Category': [
            "Alimentos y Bebidas No Alcohólicas",
            "Bienes y Servicios Diversos",
            "Muebles, Bienes y Servicios Domésticos",
            "Bebidas Alcohólicas y Tabaco",
            "Prendas de Vestir y Calzados"
        ],
        'Raw_Weight': [27.06, 7.55, 6.08, 0.88, 7.56]
    })
    core_basket['Normalized_Weight'] = core_basket['Raw_Weight'] / core_basket['Raw_Weight'].sum()

    city_weights_path = "config/City Weights.csv"
    if not os.path.exists(city_weights_path):
        print(f"ERROR: {city_weights_path} not found.")
        return
    city_weights = pd.read_csv(city_weights_path)
    city_weights['join_key'] = city_weights['City'].str.lower().str.replace(' ', '_')
    city_weights['Weight'] = city_weights['Weight'] / city_weights['Weight'].sum()

    # 2. FETCH ALL HISTORICAL DATA
    raw_dfs = []
    for city in CITIES:
        print(f"Loading raw data for {city.upper()}...")
        raw_data_dir = f"data/hipermaxi/{city}"
        repo_url = f"https://api.github.com/repos/mauforonda/precios/contents/data/hipermaxi/{city}"
        
        all_files = fetch_all_files(repo_url=repo_url, output_dir=raw_data_dir)
        for f in all_files:
            try:
                df = pd.read_csv(f)
            except:
                df = pd.read_csv(f, encoding='latin1')
            time_col = next((c for c in df.columns if 'fecha' in c or 'time' in c or 'date' in c), None)
            if time_col:
                df['fecha'] = pd.to_datetime(df[time_col], errors='coerce', format='mixed').dt.date
                df = df.dropna(subset=['fecha'])
                df['city'] = city
                raw_dfs.append(df)
                
    if not raw_dfs:
        print("No valid data found.")
        return
        
    raw_prices = pd.concat(raw_dfs, ignore_index=True)
    if 'id_producto' in raw_prices.columns:
        raw_prices['id'] = raw_prices['id_producto']
    raw_prices['norm_id'] = raw_prices['id'].apply(normalize_id)

    # 3. AI MAPPING OF UNMAPPED PRODUCTS
    mapping_dict = load_product_mapping(mapping_file=MAPPING_FILE)
    unmapped = raw_prices[~raw_prices['norm_id'].isin(mapping_dict.keys())]
    if ENABLE_AI_CATEGORIZATION and not unmapped.empty:
        unique_unmapped = unmapped.drop_duplicates(subset=['norm_id'])
        new_products_list = []
        for _, row in unique_unmapped.iterrows():
            pid = row['norm_id']
            if pd.notna(pid):
                pname = get_product_name(row['id'])
                new_products_list.append({"id": pid, "name": str(pname)})
        
        if new_products_list:
            batch_size = 50
            for i in range(0, len(new_products_list), batch_size):
                batch = new_products_list[i:i + batch_size]
                ai_results = categorize_new_products(batch)
                if ai_results:
                    valid_results = [item for item in ai_results if item.get("confidence") != "failed"]
                    if valid_results:
                        append_new_mappings(valid_results, mapping_file=MAPPING_FILE)
                    for item in ai_results:
                        mapping_dict[item["id"]] = item.get("category", "Unmapped")

    # 4. MERGE MAPPINGS AND FILTER TEMPORADA
    raw_prices['Category'] = raw_prices['norm_id'].map(mapping_dict)
    
    prod_df = load_product_data()
    if not prod_df.empty and 'subcategoria' in prod_df.columns:
        # R logic filters strictly on subcategoria "temporada"
        mask = prod_df['subcategoria'].str.contains('temporada', na=False, case=False)
        temporada_ids = set(prod_df[mask]['id_producto'].astype(str))
    else:
        temporada_ids = set()

    # 5. CALCULATE DOD RELATIVE
    print("Calculating relative DOD...")
    raw_prices = raw_prices.sort_values(by=['city', 'norm_id', 'fecha'])
    if 'precio' in raw_prices.columns:
        raw_prices['price'] = pd.to_numeric(raw_prices['precio'], errors='coerce')
        
    raw_prices['precio_prev'] = raw_prices.groupby(['city', 'norm_id'])['price'].shift(1)
    raw_prices['fecha_prev'] = raw_prices.groupby(['city', 'norm_id'])['fecha'].shift(1)
    
    # Calculate gap in days and apply 40-day attrition rule
    raw_prices['fecha_dt'] = pd.to_datetime(raw_prices['fecha'])
    raw_prices['fecha_prev_dt'] = pd.to_datetime(raw_prices['fecha_prev'])
    raw_prices['gap_days'] = (raw_prices['fecha_dt'] - raw_prices['fecha_prev_dt']).dt.days
    
    raw_prices['relative_dod'] = raw_prices['price'] / raw_prices['precio_prev']
    raw_prices.loc[raw_prices['gap_days'] > 40, 'relative_dod'] = np.nan

    # 6. FILTER CORE AND CLEAN
    clean_core = raw_prices[~raw_prices['norm_id'].isin(temporada_ids)]
    clean_core = clean_core[clean_core['Category'].isin(core_basket['Category'])]
    clean_core = clean_core[(clean_core['relative_dod'] > 0) & (clean_core['relative_dod'].notna())]

    # 7. JEVONS INDEX (No outlier bounds, strictly mimicking R)
    print("Calculating Jevons Index...")
    def jevons_mean(x):
        return np.exp(np.mean(np.log(x)))
        
    chained_elementary = clean_core.groupby(['city', 'Category', 'fecha'])['relative_dod'].agg(jevons_mean).reset_index(name='daily_jevons')
    chained_elementary = chained_elementary.sort_values(['city', 'Category', 'fecha'])
    chained_elementary['chained_index'] = 100 * chained_elementary.groupby(['city', 'Category'])['daily_jevons'].cumprod()

    # 8. AGGREGATE TO CITY LEVEL
    print("Aggregating City Level...")
    city_level = pd.merge(chained_elementary, core_basket[['Category', 'Normalized_Weight']], on='Category', how='left')
    def weighted_avg(g):
        return np.sum(g['chained_index'] * g['Normalized_Weight']) / np.sum(g['Normalized_Weight'])
        
    city_cpi = city_level.groupby(['city', 'fecha']).apply(weighted_avg, include_groups=False).reset_index(name='city_index')

    # 9. AGGREGATE TO NATIONAL LEVEL
    print("Aggregating National Level...")
    city_cpi['join_key'] = city_cpi['city'].str.lower().str.replace(' ', '_')
    national_merged = pd.merge(city_cpi, city_weights[['join_key', 'Weight']], on='join_key', how='inner')
    
    def national_weighted_avg(g):
        return np.sum(g['city_index'] * g['Weight']) / np.sum(g['Weight'])
        
    national_cpi = national_merged.groupby('fecha').apply(national_weighted_avg, include_groups=False).reset_index(name='national_index')

    # 10. FORMAT EXPORT AND SAVE
    # Export individual city CSVs
    print("Exporting City Data...")
    for city in CITIES:
        city_out_dir = f"results/supermarket_1/{city}"
        os.makedirs(city_out_dir, exist_ok=True)
        
        c_elem = chained_elementary[chained_elementary['city'] == city]
        if c_elem.empty: continue
        
        c_sub = c_elem.pivot(index='fecha', columns='Category', values='chained_index')
        c_cpi = city_cpi[city_cpi['city'] == city].set_index('fecha')
        
        c_final = c_cpi[['city_index']].rename(columns={'city_index': 'cpi'}).join(c_sub)
        c_final.index.name = 'date'
        c_final = c_final.reset_index()
        c_final['date'] = pd.to_datetime(c_final['date']).dt.strftime('%Y-%m-%d')
        c_final = c_final.sort_values('date')
        
        c_final_dates = pd.date_range(start=c_final['date'].min(), end=c_final['date'].max()).strftime('%Y-%m-%d')
        c_final = c_final.set_index('date').reindex(c_final_dates).ffill().bfill().reset_index().rename(columns={'index': 'date'})
        c_final.to_csv(os.path.join(city_out_dir, "supermarket_1_tracker_results.csv"), index=False)

    out_dir = "results/supermarket_1/national"
    os.makedirs(out_dir, exist_ok=True)
    
    # Pivot city cpi for the final table format
    pivot_cities = city_cpi.pivot(index='fecha', columns='city', values='city_index')
    pivot_cities.columns = [f"{c.lower()}_cpi" for c in pivot_cities.columns]
    
    final_df = national_cpi.set_index('fecha').join(pivot_cities)
    final_df.index.name = 'date'
    final_df = final_df.rename(columns={'national_index': 'cpi'})
    final_df = final_df.reset_index()
    final_df['date'] = pd.to_datetime(final_df['date']).dt.strftime('%Y-%m-%d')
    final_df = final_df.sort_values('date')
    
    # Fill missing dates to forward fill CPI just like the old tracker format
    all_dates = pd.date_range(start=final_df['date'].min(), end=final_df['date'].max()).strftime('%Y-%m-%d')
    final_df = final_df.set_index('date').reindex(all_dates).ffill().bfill().reset_index().rename(columns={'index': 'date'})
    
    csv_path = os.path.join(out_dir, "supermarket_1_tracker_results.csv")
    final_df.to_csv(csv_path, index=False)
    final_df.to_json(os.path.join(out_dir, "supermarket_1_tracker_results.json"), orient="records", indent=4)
    print(f"Successfully generated National CPI! Saved to {csv_path}")

    # Generate N Counts
    print("Aggregating N counts...")
    counts = raw_prices.groupby(['fecha', 'city', 'Category']).size().reset_index(name='count')
    pivot_counts = counts.groupby(['fecha', 'Category'])['count'].sum().unstack(fill_value=0).reset_index()
    pivot_counts['Date'] = pd.to_datetime(pivot_counts['fecha']).dt.strftime('%m/%d/%y')
    
    cols = ["Date"] + [c for c in CORE_CATEGORIES if c in pivot_counts.columns]
    pivot_counts = pivot_counts[cols]
    
    counts_path = "results/supermarket_1/supermarket_1_daily_n_counts.csv"
    pivot_counts.to_csv(counts_path, index=False)
    print(f"Successfully updated counts file: {counts_path}")

if __name__ == "__main__":
    run_historical_tracker()
