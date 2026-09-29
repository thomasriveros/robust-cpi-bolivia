"""
Rule-based product classification into INE divisions (CCIF), used by the core-4 index.

Each product is classified by the first source that applies, in this order:
  1. mappings/ccif/product_overrides.csv        explicit per-product decisions
  2. mappings/ccif/mixed_subcategory_rules.csv  keyword rules inside mixed subcategories
  3. mappings/ccif/subcategory_ccif.csv         the reviewed subcategory -> CCIF table
  4. mappings/ccif/review_queue.csv             AI suggestions for unknown subcategories,
                                           used provisionally until reviewed

Products in none of these are left unclassified and excluded from the index; the
tracker sends them to the AI categorizer, which adds them to the review queue.
"""
import os
import re

import pandas as pd

MAPPINGS_DIR = os.path.join("mappings", "ccif")
SUBCATEGORY_FILE = os.path.join(MAPPINGS_DIR, "subcategory_ccif.csv")
RULES_FILE = os.path.join(MAPPINGS_DIR, "mixed_subcategory_rules.csv")
OVERRIDES_FILE = os.path.join(MAPPINGS_DIR, "product_overrides.csv")
REVIEW_QUEUE_FILE = os.path.join(MAPPINGS_DIR, "review_queue.csv")
CLASSIFICATION_FILE = os.path.join(MAPPINGS_DIR, "product_classification.csv")
CHANGES_FILE = os.path.join(MAPPINGS_DIR, "classification_changes.csv")

EXCLUDED = "Excluido (temporada)"
DIVISIONS = [
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
    "Bienes y Servicios Diversos",
]
VALID_DIVISIONS = set(DIVISIONS) | {EXCLUDED}
CCIF_CLASS_PATTERN = re.compile(r"^(\d{2}(\.\d(\.\d)?)?|—)$")


def _clean(s):
    return s.fillna("").astype(str).str.lower().str.strip()


def load_tables(mappings_dir=MAPPINGS_DIR):
    read = lambda name: pd.read_csv(os.path.join(mappings_dir, name), dtype=str, keep_default_na=False)
    subcats = read(os.path.basename(SUBCATEGORY_FILE))
    rules = read(os.path.basename(RULES_FILE))
    overrides = read(os.path.basename(OVERRIDES_FILE))
    queue = read(os.path.basename(REVIEW_QUEUE_FILE))
    for df, cols in [(subcats, ["categoria", "subcategoria"]), (rules, ["categoria", "subcategoria"]),
                     (queue, ["categoria", "subcategoria"])]:
        for c in cols:
            df[c] = _clean(df[c])
    return subcats, rules, overrides, queue


def validate_tables(subcats, rules, overrides, queue):
    """Returns a list of error messages (empty when the tables are consistent)."""
    errors = []
    for name, df, div_col, cls_col in [("subcategory_ccif", subcats, "ine_division", "ccif_class"),
                                       ("mixed_subcategory_rules", rules, "ine_division", "ccif_class"),
                                       ("product_overrides", overrides, "ine_division", "ccif_class")]:
        bad_div = df[~df[div_col].isin(VALID_DIVISIONS)]
        for _, r in bad_div.iterrows():
            errors.append(f"{name}: invalid division '{r[div_col]}' in row {r.to_dict()}")
        bad_cls = df[~df[cls_col].str.match(CCIF_CLASS_PATTERN)]
        for _, r in bad_cls.iterrows():
            errors.append(f"{name}: invalid CCIF class '{r[cls_col]}' in row {r.to_dict()}")

    dup = subcats[subcats.duplicated(["categoria", "subcategoria"], keep=False)]
    for _, r in dup.iterrows():
        errors.append(f"subcategory_ccif: duplicate row for ({r.categoria}, {r.subcategoria})")
    dup = overrides[overrides.duplicated("id", keep=False)]
    for pid in dup.id.unique():
        errors.append(f"product_overrides: duplicate id {pid}")

    known = set(subcats.subcategoria)
    for _, r in rules.iterrows():
        try:
            re.compile(r.pattern)
        except re.error as e:
            errors.append(f"mixed_subcategory_rules: bad pattern '{r.pattern}': {e}")
        if r.subcategoria not in known:
            errors.append(f"mixed_subcategory_rules: subcategory '{r.subcategoria}' is not in subcategory_ccif")

    bad_status = queue[~queue.status.isin(["provisional", "approved", "rejected"])]
    for _, r in bad_status.iterrows():
        errors.append(f"review_queue: invalid status '{r.status}' for id {r.id}")
    return errors


def classify(products, tables=None):
    """
    products: DataFrame with columns id, producto, categoria, subcategoria.
    Returns one row per product with ccif_class, ine_division and source
    (override / rule / subcategory / review_queue); unclassified products have source 'unclassified'.
    """
    subcats, rules, overrides, queue = tables or load_tables()
    df = products[["id", "producto", "categoria", "subcategoria"]].copy()
    df["id"] = df["id"].astype(str)
    df["_name"] = _clean(df["producto"])
    df["categoria"] = _clean(df["categoria"])
    df["subcategoria"] = _clean(df["subcategoria"])
    df["ccif_class"] = pd.NA
    df["ine_division"] = pd.NA
    df["source"] = pd.NA

    def assign(mask, ccif_class, division, source):
        mask = mask & df["source"].isna()
        df.loc[mask, ["ccif_class", "ine_division", "source"]] = [ccif_class, division, source]

    # 1. Explicit per-product overrides
    for _, o in overrides.iterrows():
        assign(df["id"] == str(o.id), o.ccif_class, o.ine_division, "override")

    # 2. Keyword rules in mixed subcategories (first matching rule wins)
    for _, r in rules.iterrows():
        in_sub = df["subcategoria"] == r.subcategoria
        if r.categoria:
            in_sub &= df["categoria"] == r.categoria
        pattern = re.compile(r.pattern)
        matches = df["_name"].map(lambda name: bool(pattern.search(name)))
        assign(in_sub & matches, r.ccif_class, r.ine_division, "rule")

    # 3. Subcategory table: an exact (categoria, subcategoria) row first, then the subcategory alone
    exact = {(r.categoria, r.subcategoria): (r.ccif_class, r.ine_division) for r in subcats.itertuples()}
    by_sub = {}
    for r in subcats.itertuples():
        by_sub.setdefault(r.subcategoria, (r.ccif_class, r.ine_division))
    found = pd.Series([exact.get((c, s)) or by_sub.get(s) for c, s in zip(df["categoria"], df["subcategoria"])],
                      index=df.index)
    hit = df["source"].isna() & found.notna()
    df.loc[hit, "ccif_class"] = found[hit].str[0]
    df.loc[hit, "ine_division"] = found[hit].str[1]
    df.loc[hit, "source"] = "subcategory"

    # 4. Reviewed or provisional AI suggestions
    usable = queue[queue.status.isin(["provisional", "approved"])].drop_duplicates("id", keep="last").set_index("id")
    q = df["source"].isna() & df["id"].isin(usable.index)
    df.loc[q, "ccif_class"] = df.loc[q, "id"].map(usable["suggested_ccif_class"])
    df.loc[q, "ine_division"] = df.loc[q, "id"].map(usable["suggested_division"])
    df.loc[q, "source"] = "review_queue"

    df["source"] = df["source"].fillna("unclassified")
    return df.drop(columns="_name")


def record_changes(new, date, path=CLASSIFICATION_FILE, changes_path=CHANGES_FILE):
    """Writes the full classification and appends any division changes to the change log."""
    cols = ["id", "producto", "categoria", "subcategoria", "ccif_class", "ine_division", "source"]
    new = new[cols].sort_values("id")
    if os.path.exists(path):
        old = pd.read_csv(path, dtype=str, keep_default_na=False)
        merged = old[["id", "ine_division"]].merge(new[["id", "ine_division", "source"]], on="id",
                                                   how="outer", suffixes=("_old", "_new"))
        merged = merged.fillna("")
        changed = merged[merged.ine_division_old != merged.ine_division_new].copy()
        if not changed.empty:
            changed.insert(0, "date", date)
            header = not os.path.exists(changes_path)
            changed.to_csv(changes_path, mode="a", header=header, index=False)
            print(f"Classification changes: {len(changed)} products (logged to {changes_path})")
    new.to_csv(path, index=False)
