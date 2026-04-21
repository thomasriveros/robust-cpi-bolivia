import os
import json
import time
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Global variables to cache file uploads during a single execution run
_METHODOLOGY_FILE = None
_CCIF_FILE = None

CORE_CATEGORIES = [
    "Alimentos y Bebidas No Alcohólicas",
    "Bebidas Alcohólicas y Tabaco",
    "Prendas de Vestir y Calzado",
    "Vivienda y Servicios Básicos",
    "Muebles, Bienes y Servicios Domésticos",
    "Salud",
    "Transporte",
    "Comunicaciones",
    "Recreación y Cultura",
    "Educación",
    "Restaurantes y Hoteles",
    "Bienes y Servicios Diversos"
]

def _upload_pdfs_if_needed():
    global _METHODOLOGY_FILE, _CCIF_FILE
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not found in environment variables.")
        
    genai.configure(api_key=GEMINI_API_KEY)
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    meth_path = os.path.join(base_dir, "DOCUMENTO-METODOLOGICO-IPC-2016.pdf")
    ccif_path = os.path.join(base_dir, "Clasificacion del Consumo Individual por Finalidades CCIF.pdf")
    
    if _METHODOLOGY_FILE is None:
        print(f"Uploading {os.path.basename(meth_path)} to Gemini Context...")
        _METHODOLOGY_FILE = genai.upload_file(path=meth_path, display_name="Methodology")
        while _METHODOLOGY_FILE.state.name == "PROCESSING":
            time.sleep(2)
            _METHODOLOGY_FILE = genai.get_file(_METHODOLOGY_FILE.name)
            
    if _CCIF_FILE is None:
        print(f"Uploading {os.path.basename(ccif_path)} to Gemini Context...")
        _CCIF_FILE = genai.upload_file(path=ccif_path, display_name="CCIF")
        while _CCIF_FILE.state.name == "PROCESSING":
            time.sleep(2)
            _CCIF_FILE = genai.get_file(_CCIF_FILE.name)

def cleanup_files():
    """Call this when the script finishes to clean up Gemini storage."""
    global _METHODOLOGY_FILE, _CCIF_FILE
    if _METHODOLOGY_FILE:
        try:
            genai.delete_file(_METHODOLOGY_FILE.name)
            _METHODOLOGY_FILE = None
        except Exception:
            pass
    if _CCIF_FILE:
        try:
            genai.delete_file(_CCIF_FILE.name)
            _CCIF_FILE = None
        except Exception:
            pass

def categorize_new_products(products_list):
    """
    products_list: list of dicts like [{"id": "123", "name": "Leche pil..."}, ...]
    Returns: list of dicts like [{"id": "123", "name": "Leche pil...", "category": "Alimentos...", "confidence": "high"}]
    """
    if not products_list:
        return []
        
    _upload_pdfs_if_needed()
    
    # We use Gemini 1.5 Flash as it's extremely fast and cheap for this kind of text classification
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction="You are an expert Bolivian statistician responsible for creating the Consumer Price Index (CPI). Your task is to accurately categorize a list of supermarket products into their official INE (Instituto Nacional de Estadística) categories based on the provided methodology and CCIF (Classification of Individual Consumption According to Purpose) documents.",
        generation_config={"response_mime_type": "application/json"}
    )
    
    prompt = f"""
    Please map the following JSON list of products to strictly one of these 12 available categories:
    {json.dumps(CORE_CATEGORIES, ensure_ascii=False, indent=2)}
    
    Output format should be a JSON array of objects with keys: "id", "name", "category", and "confidence" (where confidence is "high", "medium", or "low").
    If a product does to neatly fall into any core category or is an internal tracking SKU, label the category as "Unmapped".
    Ensure the "id" key in your output matches the exact "id" from the input.

    Products to map:
    {json.dumps(products_list, ensure_ascii=False, indent=2)}
    """
    
    print(f"Asking Gemini to categorize {len(products_list)} new products...")
    
    try:
        response = model.generate_content([_METHODOLOGY_FILE, _CCIF_FILE, prompt])
        result_json = response.text
        
        # Parse the JSON
        mapped_products = json.loads(result_json)
        return mapped_products
        
    except Exception as e:
        print(f"Error during AI Categorization: {e}")
        # If AI fails, return them as Unmapped so tracker doesn't crash
        fallback = []
        for p in products_list:
            fallback.append({
                "id": p["id"],
                "name": p["name"],
                "category": "Unmapped",
                "confidence": "failed"
            })
        return fallback
