import os
import json
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
_CLIENT = None

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
    global _METHODOLOGY_FILE, _CCIF_FILE, _CLIENT
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not found in environment variables.")
        
    if _CLIENT is None:
        _CLIENT = genai.Client(api_key=GEMINI_API_KEY)
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    meth_path = os.path.join(base_dir, "docs", "DOCUMENTO-METODOLOGICO-IPC-2016.pdf")
    ccif_path = os.path.join(base_dir, "docs", "Clasificacion del Consumo Individual por Finalidades CCIF.pdf")
    
    if _METHODOLOGY_FILE is None:
        print(f"Uploading {os.path.basename(meth_path)} to Gemini Context...")
        _METHODOLOGY_FILE = _CLIENT.files.upload(file=meth_path, config={'display_name': 'Methodology'})
        # Wait for processing
        while getattr(_METHODOLOGY_FILE, 'state', None) == 'PROCESSING' or getattr(getattr(_METHODOLOGY_FILE, 'state', None), 'name', None) == 'PROCESSING':
            time.sleep(2)
            _METHODOLOGY_FILE = _CLIENT.files.get(name=_METHODOLOGY_FILE.name)
            
    if _CCIF_FILE is None:
        print(f"Uploading {os.path.basename(ccif_path)} to Gemini Context...")
        _CCIF_FILE = _CLIENT.files.upload(file=ccif_path, config={'display_name': 'CCIF'})
        # Wait for processing
        while getattr(_CCIF_FILE, 'state', None) == 'PROCESSING' or getattr(getattr(_CCIF_FILE, 'state', None), 'name', None) == 'PROCESSING':
            time.sleep(2)
            _CCIF_FILE = _CLIENT.files.get(name=_CCIF_FILE.name)

def cleanup_files():
    """Call this when the script finishes to clean up Gemini storage."""
    global _METHODOLOGY_FILE, _CCIF_FILE, _CLIENT
    if _CLIENT is None:
        return
        
    if _METHODOLOGY_FILE:
        try:
            _CLIENT.files.delete(name=_METHODOLOGY_FILE.name)
            _METHODOLOGY_FILE = None
        except Exception:
            pass
    if _CCIF_FILE:
        try:
            _CLIENT.files.delete(name=_CCIF_FILE.name)
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
    global _CLIENT
    
    prompt = f"""
    Please map the following JSON list of products to strictly one of these 12 available categories:
    {json.dumps(CORE_CATEGORIES, ensure_ascii=False, indent=2)}
    
    Output format should be a JSON array of objects with keys: "id", "name", "category", and "confidence" (where confidence is "high", "medium", or "low").
    If a product does not neatly fall into any core category or is an internal tracking SKU, label the category as "Unmapped".
    Ensure the "id" key in your output matches the exact "id" from the input.

    Products to map:
    {json.dumps(products_list, ensure_ascii=False, indent=2)}
    """
    
    print(f"Asking Gemini (google-genai) to categorize {len(products_list)} new products...")
    
    # We use Gemini 1.5 Flash
    try:
        response = _CLIENT.models.generate_content(
            model='gemini-2.5-flash',
            contents=[_METHODOLOGY_FILE, _CCIF_FILE, prompt],
            config=types.GenerateContentConfig(
                system_instruction="You are an expert Bolivian statistician responsible for creating the Consumer Price Index (CPI). Your task is to accurately categorize a list of supermarket products into their official INE (Instituto Nacional de Estadística) categories based on the provided methodology and CCIF (Classification of Individual Consumption According to Purpose) documents.",
                response_mime_type="application/json"
            )
        )
        
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


# ---------------------------------------------------------------------------
# Constrained suggestions for the rule-based classifier (src/classification.py)
# ---------------------------------------------------------------------------

import enum
from pydantic import BaseModel, Field

from src.classification import DIVISIONS

Division = enum.Enum("Division", {f"D{i}": name for i, name in enumerate(DIVISIONS)}, type=str)


class Suggestion(BaseModel):
    id: str
    ccif_class: str = Field(description="CCIF class code, e.g. '05.6.1'")
    division: Division


def suggest_classifications(products):
    """
    products: list of dicts with id, producto, categoria, subcategoria.
    Returns a list of dicts with id, suggested_ccif_class, suggested_division. The response schema
    restricts the division to the 12 INE divisions; failures return an empty list.
    """
    if not products:
        return []
    _upload_pdfs_if_needed()
    prompt = f"""
    Classify each supermarket product into its CCIF class (e.g. "05.6.1") and the matching INE division.
    Follow the INE 2016 methodology basket and the CCIF document provided. Use the store category and
    subcategory as context, but classify by what the product is.

    Products:
    {json.dumps(products, ensure_ascii=False, indent=2)}
    """
    try:
        response = _CLIENT.models.generate_content(
            model="gemini-2.5-flash",
            contents=[_METHODOLOGY_FILE, _CCIF_FILE, prompt],
            config=types.GenerateContentConfig(
                system_instruction="You classify products for the Bolivian CPI (INE) using the CCIF.",
                response_mime_type="application/json",
                response_schema=list[Suggestion],
            ),
        )
        parsed = response.parsed or []
    except Exception as e:
        print(f"Error during AI classification: {e}")
        return []
    wanted = {str(p["id"]) for p in products}
    return [{"id": s.id, "suggested_ccif_class": s.ccif_class, "suggested_division": s.division.value}
            for s in parsed if s.id in wanted]
