# Tracking accuracy: Core-4

- Official data through: 2026-10
- Errors are synthetic minus official, in percentage points. Matched basket = official series built from the same INE divisions as the tracker.
- Theil shares split the MSE into bias, variance (scale mismatch) and covariance (unsystematic) parts.
- RW ratio < 1: the synthetic measure beats last month's official inflation (random walk) on the same months.

## In-sample accuracy

| Measure | Region | Target | N | Bias | MAE | RMSE | Corr | Theil bias/var/cov | Direction | Top-3 share of SSE | RW ratio |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Monthly average, MoM | National | Matched basket | 26 | -0.38 | 1.46 | 2.01 | 0.65 | 0.03/0.05/0.92 | 60% | 67% (2026-07 2026-05 2026-06) | 0.63 |
| Monthly average, MoM | National | Overall | 26 | -0.14 | 1.23 | 1.54 | 0.68 | 0.01/0.20/0.79 | 64% | 37% (2026-05 2025-07 2026-06) | 0.87 |
| Monthly average, MoM | LaPaz | Matched basket | 26 | -0.47 | 2.15 | 3.57 | 0.41 | 0.02/0.25/0.73 | 56% | 81% (2026-07 2026-05 2026-06) | 0.66 |
| Monthly average, MoM | Cochabamba | Matched basket | 26 | -0.34 | 1.67 | 2.38 | 0.61 | 0.02/0.12/0.86 | 64% | 70% (2026-07 2026-06 2025-07) | 0.58 |
| Monthly average, MoM | SantaCruz | Matched basket | 26 | -0.22 | 1.12 | 1.37 | 0.78 | 0.03/0.03/0.94 | 64% | 45% (2025-06 2025-12 2024-12) | 0.77 |
| 30-day change to the 15th | National | Matched basket | 26 | -0.41 | 1.42 | 1.98 | 0.66 | 0.04/0.04/0.91 | 68% | 68% (2026-07 2026-05 2026-06) | 0.62 |
| 30-day change to the 15th | National | Overall | 26 | -0.18 | 1.24 | 1.52 | 0.70 | 0.01/0.22/0.77 | 72% | 40% (2026-05 2025-06 2025-07) | 0.87 |
| 30-day change to the 15th | LaPaz | Matched basket | 26 | -0.50 | 2.13 | 3.56 | 0.42 | 0.02/0.25/0.73 | 64% | 81% (2026-07 2026-05 2025-07) | 0.66 |
| 30-day change to the 15th | Cochabamba | Matched basket | 26 | -0.37 | 1.64 | 2.33 | 0.63 | 0.03/0.12/0.85 | 72% | 70% (2026-07 2026-06 2025-07) | 0.57 |
| 30-day change to the 15th | SantaCruz | Matched basket | 26 | -0.25 | 1.13 | 1.44 | 0.77 | 0.03/0.04/0.93 | 56% | 51% (2025-06 2025-12 2025-01) | 0.82 |
| Monthly average, 12-month | National | Matched basket | 15 | -3.67 | 4.09 | 4.72 | 0.98 | 0.60/0.07/0.33 | 93% | 45% (2026-06 2026-10 2026-09) | 1.44 |
| Monthly average, 12-month | National | Overall | 15 | -1.34 | 6.42 | 7.35 | 0.99 | 0.03/0.94/0.03 | 93% | 41% (2026-10 2026-06 2026-09) | 4.00 |
| Monthly average, 12-month | LaPaz | Matched basket | 15 | -5.47 | 5.70 | 7.04 | 0.95 | 0.60/0.10/0.30 | 86% | 67% (2026-06 2026-05 2026-10) | 1.59 |
| Monthly average, 12-month | Cochabamba | Matched basket | 15 | -1.56 | 2.88 | 3.50 | 0.98 | 0.20/0.18/0.62 | 93% | 61% (2026-10 2026-09 2026-06) | 1.02 |
| Monthly average, 12-month | SantaCruz | Matched basket | 15 | -1.01 | 3.10 | 3.46 | 0.97 | 0.08/0.00/0.91 | 86% | 54% (2025-11 2026-03 2025-10) | 0.95 |

## Pseudo out-of-sample nowcasts (national MoM, expanding window, first 12 months for training)

| Measure | Target | Model | N | Bias | MAE | RMSE | RW ratio | DM p vs RW |
|---|---|---|---|---|---|---|---|---|
| Monthly average, MoM | Matched basket | Raw synthetic | 14 | -0.60 | 1.65 | 2.40 | 0.68 | 0.256 |
| Monthly average, MoM | Matched basket | Calibrated synthetic | 14 | +0.07 | 1.59 | 2.42 | 0.68 | 0.206 |
| Monthly average, MoM | Matched basket | Random walk | 14 | -0.11 | 2.29 | 3.54 | 1.00 |  |
| Monthly average, MoM | Matched basket | Expanding mean | 14 | +1.51 | 2.35 | 2.94 | 0.83 | 0.437 |
| Monthly average, MoM | Overall | Raw synthetic | 14 | -0.86 | 1.22 | 1.50 | 0.79 | 0.471 |
| Monthly average, MoM | Overall | Calibrated synthetic | 14 | -0.03 | 0.85 | 1.26 | 0.66 | 0.152 |
| Monthly average, MoM | Overall | Random walk | 14 | -0.08 | 1.26 | 1.90 | 1.00 |  |
| Monthly average, MoM | Overall | Expanding mean | 14 | +0.82 | 1.22 | 1.56 | 0.82 | 0.366 |
| 30-day change to the 15th | Matched basket | Raw synthetic | 14 | -0.58 | 1.62 | 2.37 | 0.67 | 0.244 |
| 30-day change to the 15th | Matched basket | Calibrated synthetic | 14 | +0.13 | 1.56 | 2.40 | 0.68 | 0.197 |
| 30-day change to the 15th | Matched basket | Random walk | 14 | -0.11 | 2.29 | 3.54 | 1.00 |  |
| 30-day change to the 15th | Matched basket | Expanding mean | 14 | +1.51 | 2.35 | 2.94 | 0.83 | 0.437 |
| 30-day change to the 15th | Overall | Raw synthetic | 14 | -0.84 | 1.20 | 1.48 | 0.78 | 0.442 |
| 30-day change to the 15th | Overall | Calibrated synthetic | 14 | +0.00 | 0.84 | 1.24 | 0.65 | 0.143 |
| 30-day change to the 15th | Overall | Random walk | 14 | -0.08 | 1.26 | 1.90 | 1.00 |  |
| 30-day change to the 15th | Overall | Expanding mean | 14 | +0.82 | 1.22 | 1.56 | 0.82 | 0.366 |

## Lag profile (synthetic 30-day change ending `lag` days before the 15th of month M)

| Target | RMSE at lag 0 | Lowest RMSE (lag) | Corr at lag 0 | Highest corr (lag) |
|---|---|---|---|---|
| Matched basket | 1.98 | 1.98 (4d) | 0.66 | 0.67 (4d) |
| Overall | 1.52 | 1.49 (-2d) | 0.70 | 0.70 (4d) |
