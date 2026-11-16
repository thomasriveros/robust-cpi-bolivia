# Tracking accuracy: Core-5

- Official data through: 2026-10
- Errors are synthetic minus official, in percentage points. Matched basket = official series built from the same INE divisions as the tracker.
- Theil shares split the MSE into bias, variance (scale mismatch) and covariance (unsystematic) parts.
- RW ratio < 1: the synthetic measure beats last month's official inflation (random walk) on the same months.

## In-sample accuracy

| Measure | Region | Target | N | Bias | MAE | RMSE | Corr | Theil bias/var/cov | Direction | Top-3 share of SSE | RW ratio |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Monthly average, MoM | National | Matched basket | 26 | -0.36 | 1.34 | 1.89 | 0.66 | 0.04/0.00/0.96 | 64% | 67% (2026-05 2026-07 2026-06) | 0.68 |
| Monthly average, MoM | National | Overall | 26 | -0.17 | 1.33 | 1.68 | 0.65 | 0.01/0.22/0.77 | 64% | 43% (2026-05 2024-09 2026-06) | 0.96 |
| Monthly average, MoM | LaPaz | Matched basket | 26 | -0.44 | 2.00 | 3.30 | 0.38 | 0.02/0.15/0.83 | 56% | 81% (2026-05 2026-07 2026-06) | 0.71 |
| Monthly average, MoM | Cochabamba | Matched basket | 26 | -0.32 | 1.57 | 2.25 | 0.60 | 0.02/0.03/0.95 | 60% | 64% (2026-06 2026-07 2026-05) | 0.63 |
| Monthly average, MoM | SantaCruz | Matched basket | 26 | -0.21 | 1.12 | 1.35 | 0.81 | 0.02/0.15/0.83 | 72% | 44% (2025-06 2024-12 2025-01) | 0.87 |
| 30-day change to the 15th | National | Matched basket | 26 | -0.39 | 1.32 | 1.87 | 0.67 | 0.04/0.00/0.95 | 76% | 68% (2026-05 2026-07 2026-06) | 0.67 |
| 30-day change to the 15th | National | Overall | 26 | -0.21 | 1.33 | 1.67 | 0.66 | 0.02/0.23/0.75 | 76% | 46% (2026-05 2025-06 2026-07) | 0.95 |
| 30-day change to the 15th | LaPaz | Matched basket | 26 | -0.47 | 1.99 | 3.32 | 0.37 | 0.02/0.15/0.83 | 60% | 83% (2026-05 2026-07 2025-07) | 0.71 |
| 30-day change to the 15th | Cochabamba | Matched basket | 26 | -0.36 | 1.55 | 2.19 | 0.62 | 0.03/0.03/0.94 | 64% | 65% (2026-07 2026-06 2026-05) | 0.62 |
| 30-day change to the 15th | SantaCruz | Matched basket | 26 | -0.25 | 1.20 | 1.53 | 0.77 | 0.03/0.16/0.81 | 56% | 54% (2025-06 2025-01 2024-12) | 0.98 |
| Monthly average, 12-month | National | Matched basket | 15 | -3.74 | 4.11 | 5.10 | 0.98 | 0.54/0.21/0.25 | 100% | 51% (2026-06 2026-10 2026-08) | 1.66 |
| Monthly average, 12-month | National | Overall | 15 | -1.83 | 6.97 | 8.01 | 0.99 | 0.05/0.92/0.03 | 100% | 44% (2026-06 2026-10 2026-07) | 4.36 |
| Monthly average, 12-month | LaPaz | Matched basket | 15 | -5.29 | 5.54 | 7.02 | 0.96 | 0.57/0.16/0.27 | 86% | 65% (2026-06 2026-05 2026-10) | 1.79 |
| Monthly average, 12-month | Cochabamba | Matched basket | 15 | -1.73 | 3.68 | 4.42 | 0.98 | 0.15/0.43/0.42 | 93% | 59% (2026-10 2026-09 2026-06) | 1.37 |
| Monthly average, 12-month | SantaCruz | Matched basket | 15 | -1.41 | 2.91 | 3.38 | 0.98 | 0.17/0.17/0.65 | 86% | 45% (2026-07 2026-08 2026-10) | 1.01 |

## Pseudo out-of-sample nowcasts (national MoM, expanding window, first 12 months for training)

| Measure | Target | Model | N | Bias | MAE | RMSE | RW ratio | DM p vs RW |
|---|---|---|---|---|---|---|---|---|
| Monthly average, MoM | Matched basket | Raw synthetic | 14 | -0.65 | 1.44 | 2.21 | 0.73 | 0.356 |
| Monthly average, MoM | Matched basket | Calibrated synthetic | 14 | +0.09 | 1.38 | 2.16 | 0.72 | 0.249 |
| Monthly average, MoM | Matched basket | Random walk | 14 | -0.10 | 1.98 | 3.02 | 1.00 |  |
| Monthly average, MoM | Matched basket | Expanding mean | 14 | +1.46 | 2.12 | 2.61 | 0.87 | 0.543 |
| Monthly average, MoM | Overall | Raw synthetic | 14 | -0.91 | 1.29 | 1.67 | 0.88 | 0.686 |
| Monthly average, MoM | Overall | Calibrated synthetic | 14 | +0.00 | 0.87 | 1.31 | 0.69 | 0.175 |
| Monthly average, MoM | Overall | Random walk | 14 | -0.08 | 1.26 | 1.90 | 1.00 |  |
| Monthly average, MoM | Overall | Expanding mean | 14 | +0.82 | 1.22 | 1.56 | 0.82 | 0.366 |
| 30-day change to the 15th | Matched basket | Raw synthetic | 14 | -0.64 | 1.41 | 2.20 | 0.73 | 0.350 |
| 30-day change to the 15th | Matched basket | Calibrated synthetic | 14 | +0.12 | 1.36 | 2.15 | 0.71 | 0.245 |
| 30-day change to the 15th | Matched basket | Random walk | 14 | -0.10 | 1.98 | 3.02 | 1.00 |  |
| 30-day change to the 15th | Matched basket | Expanding mean | 14 | +1.46 | 2.12 | 2.61 | 0.87 | 0.543 |
| 30-day change to the 15th | Overall | Raw synthetic | 14 | -0.90 | 1.27 | 1.67 | 0.88 | 0.683 |
| 30-day change to the 15th | Overall | Calibrated synthetic | 14 | +0.02 | 0.86 | 1.30 | 0.68 | 0.171 |
| 30-day change to the 15th | Overall | Random walk | 14 | -0.08 | 1.26 | 1.90 | 1.00 |  |
| 30-day change to the 15th | Overall | Expanding mean | 14 | +0.82 | 1.22 | 1.56 | 0.82 | 0.366 |

## Lag profile (synthetic 30-day change ending `lag` days before the 15th of month M)

| Target | RMSE at lag 0 | Lowest RMSE (lag) | Corr at lag 0 | Highest corr (lag) |
|---|---|---|---|---|
| Matched basket | 1.87 | 1.87 (4d) | 0.67 | 0.67 (4d) |
| Overall | 1.67 | 1.61 (-2d) | 0.66 | 0.67 (4d) |
