# Legacy Matched-Model Trackers

This folder preserves the **original day-on-day matched-model CPI trackers** exactly as they were before the Monthly-Chained methodology was introduced.

## Methodology (Original)

- **Comparison period**: today vs. the *previous day with data* (`last_valid_mapped_df`)
- **Price relative**: Jevons geometric mean of `P_t / P_{t-1}` per category
- **Outlier filter**: symmetric bounds `[0.45, 1/0.45]`
- **Min-N filter**: ≥ 10 matched products per category
- **Basket**: evolves naturally — products enter/exit as they appear day-to-day

## Known Limitation

A systematic upward bias was detected vs. the official INE Core 5 index, traced to the
Christmas 2024 discount period. When heavily discounted products sold out and were
relisted at regular prices in January 2025, the day-on-day chain never corrected — the
recovery leg was never captured because those products re-entered the basket at "new"
prices with no prior reference. This creates a permanent ratchet in the index level.

## Files

| File | Description |
|---|---|
| `daily_tracker_supermarket_1.py` | Hipermaxi (3-city + national aggregation) |
| `daily_tracker_supermarket_2.py` | Fidalga (single city) |

## Output Location (unchanged)

- `results/supermarket_1/` — Hipermaxi city and national results
- `results/supermarket_2/` — Fidalga results
