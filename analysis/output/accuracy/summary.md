# Tracking accuracy: Core-5

- Official data through: 2026-09
- Errors are synthetic minus official, in percentage points. Matched basket = official series built from the same INE divisions as the tracker.
- Theil shares split the MSE into bias, variance (scale mismatch) and covariance (unsystematic) parts.
- RW ratio < 1: the synthetic measure beats last month's official inflation (random walk) on the same months.

## In-sample accuracy

| Measure | Region | Target | N | Bias | MAE | RMSE | Corr | Theil bias/var/cov | Direction | Top-3 share of SSE | RW ratio |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Monthly average, MoM | National | Matched basket | 25 | -0.31 | 1.33 | 1.90 | 0.66 | 0.03/0.00/0.97 | 67% | 69% (2026-05 2026-07 2026-06) | 0.68 |
| Monthly average, MoM | National | Overall | 25 | -0.13 | 1.34 | 1.70 | 0.65 | 0.01/0.23/0.76 | 67% | 44% (2026-05 2024-09 2026-06) | 0.96 |
| Monthly average, MoM | LaPaz | Matched basket | 25 | -0.41 | 2.03 | 3.36 | 0.38 | 0.01/0.15/0.84 | 54% | 82% (2026-05 2026-07 2026-06) | 0.71 |
| Monthly average, MoM | Cochabamba | Matched basket | 25 | -0.27 | 1.57 | 2.27 | 0.60 | 0.01/0.03/0.96 | 58% | 65% (2026-06 2026-07 2026-05) | 0.63 |
| Monthly average, MoM | SantaCruz | Matched basket | 25 | -0.15 | 1.10 | 1.33 | 0.82 | 0.01/0.17/0.82 | 75% | 46% (2025-06 2024-12 2025-01) | 0.88 |
| 30-day change to the 15th | National | Matched basket | 25 | -0.35 | 1.31 | 1.88 | 0.68 | 0.03/0.00/0.96 | 75% | 70% (2026-05 2026-07 2026-06) | 0.67 |
| 30-day change to the 15th | National | Overall | 25 | -0.17 | 1.33 | 1.68 | 0.67 | 0.01/0.25/0.74 | 75% | 47% (2026-05 2025-06 2026-07) | 0.95 |
| 30-day change to the 15th | LaPaz | Matched basket | 25 | -0.44 | 2.02 | 3.38 | 0.37 | 0.02/0.15/0.83 | 58% | 83% (2026-05 2026-07 2025-07) | 0.71 |
| 30-day change to the 15th | Cochabamba | Matched basket | 25 | -0.31 | 1.55 | 2.22 | 0.62 | 0.02/0.03/0.95 | 62% | 66% (2026-07 2026-06 2026-05) | 0.61 |
| 30-day change to the 15th | SantaCruz | Matched basket | 25 | -0.19 | 1.17 | 1.52 | 0.78 | 0.02/0.18/0.80 | 58% | 57% (2025-06 2025-01 2024-12) | 1.00 |
| Monthly average, 12-month | National | Matched basket | 14 | -3.47 | 3.87 | 4.89 | 0.98 | 0.50/0.21/0.29 | 100% | 57% (2026-06 2026-08 2026-09) | 1.55 |
| Monthly average, 12-month | National | Overall | 14 | -1.11 | 6.63 | 7.67 | 0.99 | 0.02/0.94/0.04 | 100% | 50% (2026-06 2026-07 2026-08) | 4.11 |
| Monthly average, 12-month | LaPaz | Matched basket | 14 | -5.04 | 5.31 | 6.88 | 0.95 | 0.54/0.16/0.30 | 85% | 71% (2026-06 2026-05 2026-09) | 1.71 |
| Monthly average, 12-month | Cochabamba | Matched basket | 14 | -1.28 | 3.37 | 4.05 | 0.98 | 0.10/0.41/0.49 | 92% | 65% (2026-09 2026-06 2026-08) | 1.22 |
| Monthly average, 12-month | SantaCruz | Matched basket | 14 | -1.19 | 2.80 | 3.29 | 0.98 | 0.13/0.15/0.72 | 85% | 51% (2026-07 2026-08 2025-11) | 0.95 |

## Pseudo out-of-sample nowcasts (national MoM, expanding window, first 12 months for training)

| Measure | Target | Model | N | Bias | MAE | RMSE | RW ratio | DM p vs RW |
|---|---|---|---|---|---|---|---|---|
| Monthly average, MoM | Matched basket | Raw synthetic | 13 | -0.57 | 1.42 | 2.25 | 0.73 | 0.356 |
| Monthly average, MoM | Matched basket | Calibrated synthetic | 13 | +0.19 | 1.38 | 2.21 | 0.71 | 0.256 |
| Monthly average, MoM | Matched basket | Random walk | 13 | +0.02 | 2.01 | 3.10 | 1.00 |  |
| Monthly average, MoM | Matched basket | Expanding mean | 13 | +1.66 | 2.19 | 2.69 | 0.87 | 0.558 |
| Monthly average, MoM | Overall | Raw synthetic | 13 | -0.89 | 1.29 | 1.70 | 0.87 | 0.689 |
| Monthly average, MoM | Overall | Calibrated synthetic | 13 | +0.08 | 0.86 | 1.33 | 0.68 | 0.184 |
| Monthly average, MoM | Overall | Random walk | 13 | +0.01 | 1.26 | 1.95 | 1.00 |  |
| Monthly average, MoM | Overall | Expanding mean | 13 | +0.96 | 1.24 | 1.59 | 0.82 | 0.384 |
| 30-day change to the 15th | Matched basket | Raw synthetic | 13 | -0.56 | 1.40 | 2.24 | 0.72 | 0.351 |
| 30-day change to the 15th | Matched basket | Calibrated synthetic | 13 | +0.22 | 1.37 | 2.21 | 0.71 | 0.254 |
| 30-day change to the 15th | Matched basket | Random walk | 13 | +0.02 | 2.01 | 3.10 | 1.00 |  |
| 30-day change to the 15th | Matched basket | Expanding mean | 13 | +1.66 | 2.19 | 2.69 | 0.87 | 0.558 |
| 30-day change to the 15th | Overall | Raw synthetic | 13 | -0.88 | 1.28 | 1.70 | 0.87 | 0.687 |
| 30-day change to the 15th | Overall | Calibrated synthetic | 13 | +0.10 | 0.85 | 1.32 | 0.68 | 0.180 |
| 30-day change to the 15th | Overall | Random walk | 13 | +0.01 | 1.26 | 1.95 | 1.00 |  |
| 30-day change to the 15th | Overall | Expanding mean | 13 | +0.96 | 1.24 | 1.59 | 0.82 | 0.384 |

## Lag profile (synthetic 30-day change ending `lag` days before the 15th of month M)

| Target | RMSE at lag 0 | Lowest RMSE (lag) | Corr at lag 0 | Highest corr (lag) |
|---|---|---|---|---|
| Matched basket | 1.88 | 1.87 (4d) | 0.68 | 0.68 (4d) |
| Overall | 1.68 | 1.63 (-2d) | 0.67 | 0.68 (4d) |
