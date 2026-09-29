# CCIF Product Classification (core-4 index)

The repo publishes two indices:

| Index | Classification | Tracker | Results |
|---|---|---|---|
| **Core-5** (original) | `mappings/Final_Complete_Categories.csv` (per-product AI mapping) | `scripts/daily_tracker_supermarket_1.py` | `results/supermarket_1/` |
| **Core-4** | this folder (reviewed CCIF concordance) | `scripts/daily_tracker_core4.py` | `results/core4/` |

The core-5 index, its mapping and its outputs are unchanged. This folder only affects core-4.

## The core-4 basket

The basket has four INE divisions, weighted by their INE 2016 weights:

| INE division | INE weight | Share of basket |
|---|---|---|
| Alimentos y Bebidas No Alcohólicas | 27.06 | 65.10% |
| Bienes y Servicios Diversos | 7.55 | 18.16% |
| Muebles, Bienes y Servicios Domésticos | 6.08 | 14.63% |
| Bebidas Alcohólicas y Tabaco | 0.88 | 2.12% |

Clothing is left out of core-4. Under the CCIF, most products the old mapping put in clothing belong elsewhere: shoe polish is 05.6.1 and hair accessories are 12.1.3. What remains is a few dozen products whose prices almost never change. The core-4 analysis compares the index with an official core-4 series built from the same four INE divisions.

## How a product is classified

`src/classification.py` applies the first source that matches, in this order:

1. **`product_overrides.csv`**: explicit decisions for single products (`id`, `ccif_class`, `ine_division`, `reason`, `added`).
2. **`mixed_subcategory_rules.csv`**: keyword rules for subcategories that mix divisions. For example, napkins in *cuidado familiar* go to 05.6.1, while toilet paper stays in 12.1.3. Rules are regular expressions matched against the lowercased product name, and the first match wins.
3. **`subcategory_ccif.csv`**: the reviewed concordance. It maps each of the supermarket's (categoria, subcategoria) pairs to a CCIF class and INE division, citing INE 2016 basket item codes where they exist and the CCIF text otherwise.
4. **`review_queue.csv`**: AI suggestions for products in subcategories the table doesn't cover yet. They are used provisionally (`status = provisional`) until reviewed.

Products none of these cover are left out of the index. The daily run sends them to the AI (Gemini 2.5 Flash, with a response schema that only allows the 12 INE divisions), and its answers are added to the review queue.

## Reviewing the queue

For each `provisional` row in `review_queue.csv`, do one of the following:
- set `status` to `approved` if the suggestion is right;
- set `status` to `rejected` and add a row to `product_overrides.csv` with the right division;
- preferably, when a whole new subcategory has appeared, add it to `subcategory_ccif.csv`, so later products are classified without the AI.

## Outputs and checks

- **`product_classification.csv`**: the full classification used by the latest run (division, CCIF class and which source decided it). It is rewritten daily.
- **`classification_changes.csv`**: a log, appended automatically whenever a product's division changes between runs. An empty `ine_division_old` means the product is new to the catalog.
- **`comparison_with_legacy_mapping_2026-09-28.csv`**: every product whose division here differs from the core-5 mapping.
- **Validation:** `scripts/validate_classification.py` runs before the core-4 tracker in CI. It stops the core-4 step on an invalid division or CCIF class, a duplicate row, a malformed rule, or a rule for an unknown subcategory. The core-5 update runs regardless.
