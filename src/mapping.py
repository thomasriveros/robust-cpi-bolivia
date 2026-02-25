import pandas as pd
import os

# Paths (adjust based on where the script is run from, typically root)
# Default defaults for Ketal, but functions should accept overrides
DEFAULT_MAPPING_FILE = "Joined_Ketal_Data.csv"
WEIGHTS_FILE = "govt weights and cats.csv"

def normalize_id(val):
    """
    Normalizes a product ID to a string.
    Handles floats/scientific notation (e.g. 7.45014E+12 -> "7450140000000")
    """
    if pd.isna(val):
        return None
    
    try:
        # Convert scientific notation float to distinct integer string if needed
        # But wait, 7.45014E+12 might lose precision if it was just a float in CSV.
        # Ideally we read as string. If read as float, we try to convert back.
        float_val = float(val)
        return str(int(float_val))
    except (ValueError, TypeError):
        return str(val).strip()

def load_product_mapping(mapping_file=DEFAULT_MAPPING_FILE):
    """
    Loads the static mapping file and returns a dictionary/lookup.
    Returns a dictionary: {product_id: ine_category}
    """
    if not os.path.exists(mapping_file):
        raise FileNotFoundError(f"Mapping file not found at {mapping_file}")

    try:
        # Try reading ID as string to preserve precision
        df = pd.read_csv(mapping_file, dtype={'id': str, 'Product ID': str})
    except UnicodeDecodeError:
        df = pd.read_csv(mapping_file, encoding='latin1', dtype={'id': str, 'Product ID': str})
    
    # Identify columns
    # Ketal: 'id', 'Official'
    # Fidalga: 'Product ID', 'Category'
    
    id_col = 'id'
    cat_col = 'Official'
    
    if 'Product ID' in df.columns:
        id_col = 'Product ID'
    elif 'id_producto' in df.columns:
        id_col = 'id_producto'
        
    if 'Category' in df.columns:
        cat_col = 'Category'
    elif 'Govt Cat.' in df.columns:
        cat_col = 'Govt Cat.'
    elif 'categoria' in df.columns:
        cat_col = 'categoria'
        
    if id_col not in df.columns or cat_col not in df.columns:
         # Fallback search
         pass

    mapping = {}
    for idx, row in df.iterrows():
        pid_raw = row.get(id_col)
        cat = row.get(cat_col)
        
        pid = normalize_id(pid_raw)
        norm_cat = normalize_category(cat)
        
        if pid and norm_cat != 'nan' and norm_cat is not None:
             mapping[pid] = norm_cat
        
    return mapping

def load_weights(weights_file=WEIGHTS_FILE):
    """
    Loads the official INE weights.
    Returns a DataFrame with 'Category' and 'Weight' columns.
    Weight is decimal (e.g., 0.2706 instead of 27.06%).
    """
    if not os.path.exists(weights_file):
        raise FileNotFoundError(f"Weights file not found at {weights_file}")

    # The file has columns like: Numero, Divisíon, Ponderación
    # We need to handle encoding and potential BOM
    # We need to handle encoding and potential BOM
    # Try utf-8 first, then mac_roman (common on Mac), then latin1
    try:
        df = pd.read_csv(weights_file, encoding='utf-8')
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(weights_file, encoding='mac_roman')
        except UnicodeDecodeError:
            df = pd.read_csv(weights_file, encoding='latin1')

    # Normalize column names
    df.columns = [c.strip() for c in df.columns]
    
    # Identify the category name and weight columns
    # Based on previous output: 'Divisíon', 'Ponderación'
    
    # Try more lenient patterns (e.g. Divis instead of Divisi because 'í' != 'i')
    cat_col = next((c for c in df.columns if 'Divis' in c or 'divis' in c.lower()), None)
    weight_col = next((c for c in df.columns if 'Ponder' in c or 'ponder' in c.lower()), None)

    if not cat_col or not weight_col:
        raise ValueError("Could not identify Category or Weight columns in weights file")

    # Clean data
    df = df[[cat_col, weight_col]].copy()
    df.columns = ['Category', 'Weight']
    
    # Clean Category names (strip whitespace)
    df = df.dropna(subset=['Category'])
    df['Category'] = df['Category'].astype(str).apply(normalize_category)
    
    # Clean Weights (remove % and convert to float)
    if df['Weight'].dtype == 'object':
        df['Weight'] = df['Weight'].str.replace('%', '').str.replace(',', '.').astype(float)
    
    # If weights are in percentage (e.g. 24.5), convert to decimal (0.245)
    # Check sum to decide. If sum is near 100, divide by 100.
    if df['Weight'].sum() > 1.5:
        df['Weight'] = df['Weight'] / 100.0

    return df

def normalize_category(cat):
    """
    Normalizes category strings to handle encoding issues.
    e.g. "Alimentos y Bebidas No Alcoh—licas" -> "Alimentos y Bebidas No Alcoholicas"
    """
    if not isinstance(cat, str):
        return str(cat)
    
    cat = cat.strip()
    
    # Mapping of broken chars to correct ones (based on observed issues)
    # — (em dash) often replaces 'ó' in mac_roman or similar mismatches
    replacements = {
        '—': 'ó',
        '': 'ó',  # Replacement character
        'Alcoh—licas': 'Alcohólicas',
        'DomŽsticos': 'Domésticos',
        'Recreaci—n': 'Recreación',
        'Divisi—n': 'División',
        'Educaci—n': 'Educación',
        'Comunicaciones': 'Comunicaciones', # seems fine
        'Restaurantes': 'Restaurantes',
    }
    
    # Generic fix for common mojibake if possible, but specific replacements are safer for now
    # We can also just map to a standard set of 12 categories if we know them.
    
    # List of known standard categories (from experience or context)
    # 1. Alimentos y Bebidas No Alcohólicas
    # 2. Bebidas Alcohólicas y Tabaco
    # 3. Prendas de Vestir y Calzado
    # 4. Vivienda y Servicios Básicos
    # 5. Muebles, Bienes y Servicios Domésticos
    # 6. Salud
    # 7. Transporte
    # 8. Comunicaciones
    # 9. Recreación y Cultura
    # 10. Educación
    # 11. Restaurantes y Hoteles
    # 12. Bienes y Servicios Diversos
    
    # Heuristic matching
    if 'Alimentos' in cat: return "Alimentos y Bebidas No Alcohólicas"
    if 'Bebidas Alcoh' in cat and 'Tabaco' in cat: return "Bebidas Alcohólicas y Tabaco"
    if 'Vestir' in cat: return "Prendas de Vestir y Calzado"
    if 'Vivienda' in cat: return "Vivienda y Servicios Básicos"
    if 'Muebles' in cat: return "Muebles, Bienes y Servicios Domésticos"
    if 'Salud' in cat: return "Salud"
    if 'Transporte' in cat: return "Transporte"
    if 'Comunicaciones' in cat: return "Comunicaciones"
    if 'Recreac' in cat: return "Recreación y Cultura"
    if 'Educac' in cat: return "Educación"
    if 'Restaurantes' in cat: return "Restaurantes y Hoteles"
    if 'Diversos' in cat: return "Bienes y Servicios Diversos"
    
    return cat

def map_products(daily_df, mapping_dict):
    """
    Maps a DataFrame of daily products to their INE categories.
    Expects 'cal_id' or 'id' in daily_df to match keys in mapping_dict.
    Adds a 'Category' column.
    """
    # Ketal daily files usually have 'cal_id' as the product ID based on typical scrapers,
    # or just 'id'. We need to be robust.
    
    id_col = 'id'
    if 'id' not in daily_df.columns:
        # Check for other likely candidates
        if 'cal_id' in daily_df.columns:
            id_col = 'cal_id'
        # Fidalga might have 'product_id' or similar if we read it that way
        elif 'product_id' in daily_df.columns:
            id_col = 'product_id'
            
    # Normalize daily_df IDs before mapping
    # Apply normalize_id to the column
    daily_df['mapped_id'] = daily_df[id_col].apply(normalize_id)
            
    # Map
    daily_df['Category'] = daily_df['mapped_id'].map(mapping_dict)
    
    # Filter out unmapped products? 
    # User said: "map every product to one of the 12 Bolivian INE categories"
    # Products not in mapping will result in NaN. 
    # For a robust index, we should probably drop them or label them 'Unmapped'.
    # Implementation Plan says "Products not found ... will be excluded".
    
    mapped_df = daily_df.dropna(subset=['Category']).copy()
    
    return mapped_df
