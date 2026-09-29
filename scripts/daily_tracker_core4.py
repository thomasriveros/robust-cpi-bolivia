"""
Core-4 supermarket CPI, published alongside the original core-5 index.

Same index method as scripts/daily_tracker_supermarket_1.py (day-over-day relatives, 40-day
attrition rule, elementary Jevons, chaining, city and national weighted averages), with two
differences:
  - products are classified by the reviewed CCIF concordance in mappings/ccif/ (src/classification.py)
    instead of mappings/Final_Complete_Categories.csv;
  - the basket is four INE divisions. Clothing is left out: after CCIF reclassification the retailer
    sells only a few dozen clothing products and their prices almost never change.

Outputs go to results/core4/. The core-5 index and its mappings are untouched.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datetime import datetime
from io import StringIO

import numpy as np
import pandas as pd
import requests

from src.ingestion import fetch_all_files
from src.mapping import normalize_id
from src.classification import classify, record_changes, REVIEW_QUEUE_FILE
try:
    from src.ai_categorizer import suggest_classifications
except ImportError:
    suggest_classifications = None

ENABLE_AI_CATEGORIZATION = bool(os.getenv("GEMINI_API_KEY"))
PRODUCTS_URL = "https://raw.githubusercontent.com/mauforonda/precios/refs/heads/master/data/hipermaxi/productos.csv"
CITIES = ["la_paz", "cochabamba", "santa_cruz"]
OUTPUT_DIR = "results/core4"
FILE_NAME = "core4_tracker_results"

# INE 2016 division weights for the four divisions in the basket
CORE4_WEIGHTS = {
    "Alimentos y Bebidas No Alcohólicas": 27.06,
    "Bienes y Servicios Diversos": 7.55,
    "Muebles, Bienes y Servicios Domésticos": 6.08,
    "Bebidas Alcohólicas y Tabaco": 0.88,
}
ATTRITION_DAYS = 40

REVIEW_QUEUE_COLUMNS = ["id", "producto", "categoria", "subcategoria", "suggested_ccif_class",
                        "suggested_division", "model", "date", "status"]


def load_catalog():
    """Product metadata. Unlike the core-5 tracker, a failed download stops the run."""
    res = requests.get(PRODUCTS_URL, timeout=60)
    res.raise_for_status()
    df = pd.read_csv(StringIO(res.text))
    for col in ["producto", "categoria", "subcategoria"]:
        df[col] = df[col].astype(str).str.lower().str.strip()
    df["id"] = df["id_producto"].apply(normalize_id)
    return df


def load_prices():
    frames = []
    for city in CITIES:
        print(f"Loading raw data for {city.upper()}...")
        repo_url = f"https://api.github.com/repos/mauforonda/precios/contents/data/hipermaxi/{city}"
        for path in fetch_all_files(repo_url=repo_url, output_dir=f"data/hipermaxi/{city}"):
            df = pd.read_csv(path)
            df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce", format="mixed").dt.date
            df = df.dropna(subset=["fecha"])
            df["city"] = city
            df["data_source"] = os.path.basename(path)
            frames.append(df)
    if not frames:
        raise RuntimeError("No price data found")
    prices = pd.concat(frames, ignore_index=True)
    prices["norm_id"] = prices["id_producto"].apply(normalize_id)
    prices["price"] = pd.to_numeric(prices["precio"], errors="coerce")
    return prices


def queue_ai_suggestions(pending, today, batch_size=50):
    """Asks the AI to classify products no rule covers and appends its answers to the review queue."""
    records = pending[["id", "producto", "categoria", "subcategoria"]].to_dict("records")
    rows = []
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        by_id = {str(r["id"]): r for r in batch}
        for s in suggest_classifications(batch):
            rows.append({**by_id[s["id"]], **s, "model": "gemini-2.5-flash", "date": today, "status": "provisional"})
    if rows:
        pd.DataFrame(rows)[REVIEW_QUEUE_COLUMNS].to_csv(REVIEW_QUEUE_FILE, mode="a", header=False, index=False)
        print(f"Queued {len(rows)} AI suggestions for review in {REVIEW_QUEUE_FILE}")


def classify_products(catalog, prices, today):
    classified = classify(catalog)
    seen = set(prices["norm_id"].dropna())
    pending = classified[(classified["source"] == "unclassified") & classified["id"].isin(seen)]
    if not pending.empty:
        print(f"{len(pending)} products are not covered by any classification rule")
        if ENABLE_AI_CATEGORIZATION and suggest_classifications is not None:
            queue_ai_suggestions(pending, today)
            classified = classify(catalog)
    record_changes(classified, today)
    missing = seen - set(classified["id"])
    if missing:
        print(f"WARNING: {len(missing)} product ids in the price data are missing from productos.csv and are excluded")
    return dict(zip(classified["id"], classified["ine_division"]))


def price_relatives(prices, divisions, temporada_ids):
    """Day-over-day relatives with the 40-day attrition rule, restricted to the core-4 basket."""
    df = prices.sort_values(["city", "norm_id", "fecha"]).copy()
    g = df.groupby(["city", "norm_id"])
    df["relative_dod"] = df["price"] / g["price"].shift(1)
    gap = (pd.to_datetime(df["fecha"]) - pd.to_datetime(g["fecha"].shift(1))).dt.days
    df.loc[gap > ATTRITION_DAYS, "relative_dod"] = np.nan
    df["Category"] = df["norm_id"].map(divisions)
    keep = (~df["norm_id"].isin(temporada_ids) & df["Category"].isin(CORE4_WEIGHTS)
            & (df["relative_dod"] > 0) & df["relative_dod"].notna())
    return df[keep]


def build_indices(relatives, city_weights):
    elementary = (relatives.groupby(["city", "Category", "fecha"])["relative_dod"]
                  .agg(lambda x: np.exp(np.mean(np.log(x)))).reset_index(name="daily_jevons")
                  .sort_values(["city", "Category", "fecha"]))
    elementary["chained_index"] = 100 * elementary.groupby(["city", "Category"])["daily_jevons"].cumprod()

    weights = pd.Series(CORE4_WEIGHTS) / sum(CORE4_WEIGHTS.values())
    elementary["w"] = elementary["Category"].map(weights)
    city = (elementary.groupby(["city", "fecha"])
            .apply(lambda g: np.sum(g["chained_index"] * g["w"]) / np.sum(g["w"]), include_groups=False)
            .reset_index(name="city_index"))
    city["w"] = city["city"].map(city_weights)
    national = (city.dropna(subset=["w"]).groupby("fecha")
                .apply(lambda g: np.sum(g["city_index"] * g["w"]) / np.sum(g["w"]), include_groups=False)
                .reset_index(name="cpi"))
    return elementary, city, national


def fill_daily(df, sources):
    """Adds the data_source column and forward-fills missing dates, as in the core-5 output."""
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    df = df.merge(sources, on="date", how="left").sort_values("date")
    dates = pd.date_range(df["date"].min(), df["date"].max()).strftime("%Y-%m-%d")
    df = df.set_index("date").reindex(dates)
    df["data_source"] = df["data_source"].fillna("Forward Fill")
    df = df.ffill().bfill().reset_index().rename(columns={"index": "date"})
    return df[["date", "data_source", "cpi"] + [c for c in df.columns if c not in ("date", "data_source", "cpi")]]


def write(df, directory):
    os.makedirs(directory, exist_ok=True)
    df.to_csv(os.path.join(directory, f"{FILE_NAME}.csv"), index=False)
    df.to_json(os.path.join(directory, f"{FILE_NAME}.json"), orient="records", indent=4)


def check_not_shorter(national):
    """Refuses to publish a series that ends earlier than the one already committed."""
    path = os.path.join(OUTPUT_DIR, "national", f"{FILE_NAME}.csv")
    if os.path.exists(path):
        previous_end = pd.read_csv(path, usecols=["date"])["date"].max()
        if national["date"].max() < previous_end:
            raise RuntimeError(f"New series ends {national['date'].max()}, before the published {previous_end}; "
                               "the price data looks incomplete, so nothing was written.")


def run():
    print("Starting core-4 CPI rebuild...")
    today = datetime.utcnow().strftime("%Y-%m-%d")
    city_weights = pd.read_csv("config/City Weights.csv")
    city_weights = (city_weights.assign(key=city_weights["City"].str.lower().str.replace(" ", "_"))
                    .set_index("key")["Weight"])
    city_weights = city_weights / city_weights.sum()

    catalog = load_catalog()
    prices = load_prices()
    divisions = classify_products(catalog, prices, today)
    temporada_ids = set(catalog.loc[catalog["subcategoria"].str.contains("temporada", na=False), "id"])

    relatives = price_relatives(prices, divisions, temporada_ids)
    elementary, city, national = build_indices(relatives, city_weights)

    national_out = national.rename(columns={"fecha": "date"})
    city_wide = city.pivot(index="fecha", columns="city", values="city_index")
    city_wide.columns = [f"{c}_cpi" for c in city_wide.columns]
    national_out = national_out.merge(city_wide.reset_index().rename(columns={"fecha": "date"}), on="date", how="left")
    national_sources = (prices[["fecha", "data_source"]].drop_duplicates("fecha")
                        .assign(date=lambda d: pd.to_datetime(d["fecha"]).dt.strftime("%Y-%m-%d"))[["date", "data_source"]])
    national_out = fill_daily(national_out, national_sources)
    check_not_shorter(national_out)

    for c in CITIES:
        sub = elementary[elementary["city"] == c].pivot(index="fecha", columns="Category", values="chained_index")
        out = (city[city["city"] == c].set_index("fecha")[["city_index"]].rename(columns={"city_index": "cpi"})
               .join(sub).reset_index().rename(columns={"fecha": "date"}))
        sources = (prices.loc[prices["city"] == c, ["fecha", "data_source"]].drop_duplicates("fecha")
                   .assign(date=lambda d: pd.to_datetime(d["fecha"]).dt.strftime("%Y-%m-%d"))[["date", "data_source"]])
        write(fill_daily(out, sources), os.path.join(OUTPUT_DIR, c))
    write(national_out, os.path.join(OUTPUT_DIR, "national"))

    # Number of price relatives used per category and day, summed across cities
    counts = relatives.groupby(["fecha", "Category"]).size().unstack(fill_value=0).reset_index()
    counts["Date"] = pd.to_datetime(counts["fecha"]).dt.strftime("%m/%d/%y")
    counts[["Date"] + [c for c in CORE4_WEIGHTS if c in counts.columns]].to_csv(
        os.path.join(OUTPUT_DIR, "core4_daily_n_counts.csv"), index=False)
    print(f"Core-4 CPI written to {OUTPUT_DIR} (through {national_out['date'].max()})")


if __name__ == "__main__":
    run()
