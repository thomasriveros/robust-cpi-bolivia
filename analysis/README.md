# Paper Analysis

`paper_analysis.py` re-runs the comparison analysis from *A Real-Time Supermarket Price Index for Bolivia* every day, after the trackers update. It compares each published index with official INE data from [live-ine-inflation-update](https://github.com/thomasriveros/live-ine-inflation-update). Each index is compared with an official series built from the same INE divisions:

| Index | Tracker results | Official benchmark | Output |
|---|---|---|---|
| Core-5 (original) | `results/supermarket_1/` | INE core-5 | `output/mid_month/`, `output/start_of_month/` |
| Core-4 | `results/core4/` | INE core-4 (core-5 without clothing) | `output/core4/mid_month/`, `output/core4/start_of_month/` |

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
- **Index comparison** (`output/core4/core4_vs_core5.png`): core-5 and core-4 side by side, each against its own official benchmark.

The CSVs and summary are rewritten every day. The charts are redrawn only when a new month of official data arrives, which keeps the repo from growing by about 1.5 MB a day. `charts_official_month.txt` records the month they were last drawn for. To redraw them on demand, run `python analysis/paper_analysis.py --force-charts`.

## Tracking accuracy

`tracking_accuracy.py` runs after the paper analysis and measures how closely synthetic inflation tracks official inflation. It writes to `output/accuracy/` (core-5) and `output/core4/accuracy/` (core-4).

```bash
python analysis/tracking_accuracy.py
```

Each index is compared with two official targets: the **matched basket** (the official series built from the same INE divisions, nationally and for each city) and **overall** national CPI. Three synthetic measures are scored:

| Measure | Definition |
|---|---|
| Monthly average, MoM | The daily index is averaged over calendar month M, then compared with the M-1 average. INE's index is a monthly average of prices, so this measure matches its concept. |
| 30-day change to the 15th | The point-in-time measure used with mid-month dating above. It is available about two weeks earlier. |
| Monthly average, 12-month | Year-over-year change in the monthly average. |

Outputs:

- **`accuracy_table.csv`**: for each measure, region and target:
  - bias, MAE, median absolute error, RMSE, and RMSE with the bias removed
  - correlation
  - the Theil decomposition of the MSE into bias, variance (scale mismatch) and covariance (noise) shares
  - directional accuracy: the share of months where synthetic and official inflation move the same way
  - the share of squared error that comes from the three worst months
  - RMSE relative to a random walk, i.e. last month's official inflation
- **`nowcast_evaluation.csv`**: pseudo out-of-sample nowcasts of national MoM inflation over an expanding window, after the first 12 months.
  - Models: raw synthetic, calibrated synthetic (an OLS of official on synthetic, fitted only on earlier months), the random walk, and the expanding mean.
  - Each model also gets a Diebold-Mariano test against the random walk, with the Harvey-Leybourne-Newbold correction.
- **`lag_profile.csv`** and `lag_profile.png`: RMSE and correlation as the synthetic 30-day window is moved from 10 days after the 15th to 30 days before it.
- **`monthly_inflation.csv`**: the official and synthetic monthly series behind the tables.
- **`errors_by_month.png`**: synthetic minus official MoM inflation for each month.
- **`summary.md`**: the headline tables.

As in the paper analysis, charts are only redrawn when a new official month arrives. To redraw them now, pass `--force-charts`.

## Official series

Every official series is rebased to July 2024 = 100.

- **Overall:** INE's national general index.
- **Core-5:** each of the five INE divisions is rebased first, then they are combined with the tracker's normalized weights. This is the same structure the synthetic index uses.
- **Core-4:** built the same way from the four divisions other than clothing.
- **Cities:** the La Paz, Cochabamba (Región Metropolitana Kanata) and Santa Cruz series are built the same way as national core-5.

## Dating conventions

INE's index for month M is an average of prices collected during month M. The output is produced twice, differing only in where that monthly value is placed on the daily timeline:

| Folder | Official month M placed on |
|---|---|
| `mid_month/` | the 15th of month M (the primary convention) |
| `start_of_month/` | the 1st of month M |

Mid-month is the primary convention for two reasons:
- A monthly average is centred on the middle of the month.
- INE's month-over-month change then covers the same window as the tracker's 30-day change ending on the 15th.

For the core-5 index, with the paper's original dating and data, the script reproduces every correlation, MAD and Table 3 estimate in the paper. That original dating had core-5 on the 1st of month M and overall on the 1st of month M+1.
