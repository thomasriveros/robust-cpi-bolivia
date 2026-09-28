# Paper Analysis

`paper_analysis.py` re-runs the comparison analysis from *A Real-Time Supermarket Price Index for Bolivia* every day, after the tracker updates. It compares the synthetic index in `results/supermarket_1/` with official INE data from [live-ine-inflation-update](https://github.com/thomasriveros/live-ine-inflation-update).

```bash
python analysis/paper_analysis.py
```

## What it computes

- **Panel** (`national_cpi_data.csv`): daily synthetic indices and 30-day inflation for the nation and the three cities, merged with the official monthly series.
- **Correlation matrix** (`correlation_matrix.csv` / `.png`): correlations computed only on dates where both series are observed.
- **MAD table** (`mad_table.csv`): the correlation and mean absolute difference between each synthetic and official series.
- **Lag regressions** (`lag_regressions.csv`): official MoM inflation regressed on synthetic inflation measured 0, 15 and 20 days earlier. Each is estimated three ways: OLS, OLS with HC1 standard errors, and Huber RLM (the equivalent of `MASS::rlm` in R).
- **Figures**: the level and inflation comparison graph, plus scatterplots for the core-5 15-day lag and the overall 20-day lag.
- **Summary** (`summary.md`): the headline tables and the dates the data runs through.

## Official series

Every official series is rebased to July 2024 = 100.

- **Overall:** INE's national general index.
- **Core-5:** each of the five INE divisions is rebased first, then they are combined with the tracker's normalized weights. This is the same structure the synthetic index uses.
- **Cities:** the La Paz, Cochabamba (Región Metropolitana Kanata) and Santa Cruz series are built the same way as national core-5.

## Dating conventions

INE's index for month M is an average of prices collected during month M. The output is produced twice, differing only in where that monthly value is placed on the daily timeline:

| Folder | Official month M placed on |
|---|---|
| `output/mid_month/` | the 15th of month M (the primary convention) |
| `output/start_of_month/` | the 1st of month M |

Mid-month is the primary convention for two reasons:
- A monthly average is centred on the middle of the month.
- INE's month-over-month change then covers the same window as the tracker's 30-day change ending on the 15th.

With the paper's original dating and data, the script reproduces every correlation, MAD and Table 3 estimate in the paper. That original dating had core-5 on the 1st of month M and overall on the 1st of month M+1.
