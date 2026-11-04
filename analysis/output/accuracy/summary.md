# Tracking accuracy: Core-5

- Official data through: 2026-09
- Errors are synthetic minus official, in percentage points. Matched basket = official series built from the same INE divisions as the tracker.
- Theil shares split the MSE into bias, variance (scale mismatch) and covariance (unsystematic) parts.
- RW ratio < 1: the synthetic measure beats last month's official inflation (random walk) on the same months.

## In-sample accuracy

| Measure | Region | Target | N | Bias | MAE | RMSE | Corr | Theil bias/var/cov | Direction | Top-3 share of SSE | RW ratio |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Monthly average, MoM | National | Matched basket | 25 | -0.31 | 1.35 | 1.95 | 0.65 | 0.03/0.00/0.97 | 67% | 70% (2026-05 2026-07 2026-06) | 0.69 |
| Monthly average, MoM | National | Overall | 25 | -0.13 | 1.36 | 1.73 | 0.64 | 0.01/0.23/0.77 | 67% | 44% (2026-05 2026-06 2024-09) | 0.98 |
| Monthly average, MoM | LaPaz | Matched basket | 25 | -0.41 | 2.03 | 3.36 | 0.38 | 0.01/0.15/0.84 | 54% | 82% (2026-05 2026-07 2026-06) | 0.71 |
| Monthly average, MoM | Cochabamba | Matched basket | 25 | -0.27 | 1.56 | 2.24 | 0.61 | 0.01/0.03/0.96 | 58% | 64% (2026-06 2026-07 2026-05) | 0.62 |
| Monthly average, MoM | SantaCruz | Matched basket | 25 | -0.15 | 1.10 | 1.33 | 0.82 | 0.01/0.17/0.82 | 75% | 46% (2025-06 2024-12 2025-01) | 0.88 |
| 30-day change to the 15th | National | Matched basket | 25 | -0.35 | 1.33 | 1.92 | 0.66 | 0.03/0.00/0.97 | 71% | 71% (2026-05 2026-07 2026-06) | 0.68 |
| 30-day change to the 15th | National | Overall | 25 | -0.17 | 1.35 | 1.71 | 0.65 | 0.01/0.24/0.75 | 71% | 47% (2026-05 2025-06 2026-07) | 0.96 |
| 30-day change to the 15th | LaPaz | Matched basket | 25 | -0.44 | 2.02 | 3.38 | 0.37 | 0.02/0.15/0.83 | 58% | 83% (2026-05 2026-07 2025-07) | 0.71 |
| 30-day change to the 15th | Cochabamba | Matched basket | 25 | -0.31 | 1.54 | 2.19 | 0.63 | 0.02/0.03/0.95 | 62% | 64% (2026-07 2026-06 2026-05) | 0.60 |
| 30-day change to the 15th | SantaCruz | Matched basket | 25 | -0.19 | 1.17 | 1.52 | 0.78 | 0.02/0.18/0.80 | 58% | 57% (2025-06 2025-01 2024-12) | 1.00 |
| Monthly average, 12-month | National | Matched basket | 14 | -3.48 | 3.88 | 4.91 | 0.98 | 0.50/0.21/0.29 | 100% | 58% (2026-06 2026-08 2026-09) | 1.56 |
| Monthly average, 12-month | National | Overall | 14 | -1.13 | 6.64 | 7.69 | 0.99 | 0.02/0.94/0.04 | 100% | 50% (2026-06 2026-07 2026-08) | 4.12 |
| Monthly average, 12-month | LaPaz | Matched basket | 14 | -5.05 | 5.31 | 6.88 | 0.95 | 0.54/0.16/0.30 | 85% | 71% (2026-06 2026-05 2026-09) | 1.71 |
| Monthly average, 12-month | Cochabamba | Matched basket | 14 | -1.24 | 3.33 | 3.99 | 0.98 | 0.10/0.40/0.50 | 92% | 64% (2026-09 2026-06 2026-08) | 1.20 |
| Monthly average, 12-month | SantaCruz | Matched basket | 14 | -1.19 | 2.80 | 3.29 | 0.98 | 0.13/0.15/0.72 | 85% | 51% (2026-07 2026-08 2025-11) | 0.95 |

## Pseudo out-of-sample nowcasts (national MoM, expanding window, first 12 months for training)

| Measure | Target | Model | N | Bias | MAE | RMSE | RW ratio | DM p vs RW |
|---|---|---|---|---|---|---|---|---|
| Monthly average, MoM | Matched basket | Raw synthetic | 13 | -0.57 | 1.46 | 2.32 | 0.75 | 0.381 |
| Monthly average, MoM | Matched basket | Calibrated synthetic | 13 | +0.19 | 1.41 | 2.26 | 0.73 | 0.270 |
| Monthly average, MoM | Matched basket | Random walk | 13 | +0.02 | 2.01 | 3.10 | 1.00 |  |
| Monthly average, MoM | Matched basket | Expanding mean | 13 | +1.66 | 2.19 | 2.69 | 0.87 | 0.558 |
| Monthly average, MoM | Overall | Raw synthetic | 13 | -0.89 | 1.33 | 1.76 | 0.90 | 0.751 |
| Monthly average, MoM | Overall | Calibrated synthetic | 13 | +0.08 | 0.87 | 1.36 | 0.70 | 0.193 |
| Monthly average, MoM | Overall | Random walk | 13 | +0.01 | 1.26 | 1.95 | 1.00 |  |
| Monthly average, MoM | Overall | Expanding mean | 13 | +0.96 | 1.24 | 1.59 | 0.82 | 0.384 |
| 30-day change to the 15th | Matched basket | Raw synthetic | 13 | -0.56 | 1.44 | 2.30 | 0.74 | 0.373 |
| 30-day change to the 15th | Matched basket | Calibrated synthetic | 13 | +0.22 | 1.40 | 2.25 | 0.73 | 0.266 |
| 30-day change to the 15th | Matched basket | Random walk | 13 | +0.02 | 2.01 | 3.10 | 1.00 |  |
| 30-day change to the 15th | Matched basket | Expanding mean | 13 | +1.66 | 2.19 | 2.69 | 0.87 | 0.558 |
| 30-day change to the 15th | Overall | Raw synthetic | 13 | -0.88 | 1.32 | 1.75 | 0.90 | 0.742 |
| 30-day change to the 15th | Overall | Calibrated synthetic | 13 | +0.10 | 0.86 | 1.35 | 0.70 | 0.189 |
| 30-day change to the 15th | Overall | Random walk | 13 | +0.01 | 1.26 | 1.95 | 1.00 |  |
| 30-day change to the 15th | Overall | Expanding mean | 13 | +0.96 | 1.24 | 1.59 | 0.82 | 0.384 |

## Lag profile (synthetic 30-day change ending `lag` days before the 15th of month M)

| Target | RMSE at lag 0 | Lowest RMSE (lag) | Corr at lag 0 | Highest corr (lag) |
|---|---|---|---|---|
| Matched basket | 1.92 | 1.91 (4d) | 0.66 | 0.66 (4d) |
| Overall | 1.71 | 1.66 (-2d) | 0.65 | 0.66 (4d) |
