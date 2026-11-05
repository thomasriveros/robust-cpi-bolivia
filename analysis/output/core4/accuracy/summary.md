# Tracking accuracy: Core-4

- Official data through: 2026-09
- Errors are synthetic minus official, in percentage points. Matched basket = official series built from the same INE divisions as the tracker.
- Theil shares split the MSE into bias, variance (scale mismatch) and covariance (unsystematic) parts.
- RW ratio < 1: the synthetic measure beats last month's official inflation (random walk) on the same months.

## In-sample accuracy

| Measure | Region | Target | N | Bias | MAE | RMSE | Corr | Theil bias/var/cov | Direction | Top-3 share of SSE | RW ratio |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Monthly average, MoM | National | Matched basket | 25 | -0.32 | 1.44 | 2.02 | 0.65 | 0.02/0.04/0.93 | 58% | 70% (2026-07 2026-05 2026-06) | 0.63 |
| Monthly average, MoM | National | Overall | 25 | -0.10 | 1.23 | 1.55 | 0.69 | 0.00/0.22/0.78 | 62% | 38% (2026-05 2025-07 2026-06) | 0.87 |
| Monthly average, MoM | LaPaz | Matched basket | 25 | -0.42 | 2.17 | 3.63 | 0.41 | 0.01/0.25/0.74 | 54% | 82% (2026-07 2026-05 2026-06) | 0.66 |
| Monthly average, MoM | Cochabamba | Matched basket | 25 | -0.27 | 1.65 | 2.39 | 0.62 | 0.01/0.12/0.87 | 62% | 72% (2026-07 2026-06 2025-07) | 0.58 |
| Monthly average, MoM | SantaCruz | Matched basket | 25 | -0.15 | 1.09 | 1.34 | 0.79 | 0.01/0.04/0.95 | 62% | 49% (2025-06 2025-12 2024-12) | 0.78 |
| 30-day change to the 15th | National | Matched basket | 25 | -0.35 | 1.40 | 1.99 | 0.67 | 0.03/0.04/0.93 | 67% | 70% (2026-07 2026-05 2026-06) | 0.62 |
| 30-day change to the 15th | National | Overall | 25 | -0.14 | 1.24 | 1.53 | 0.71 | 0.01/0.23/0.76 | 71% | 41% (2026-05 2025-06 2025-07) | 0.86 |
| 30-day change to the 15th | LaPaz | Matched basket | 25 | -0.46 | 2.16 | 3.62 | 0.42 | 0.02/0.25/0.73 | 62% | 82% (2026-07 2026-05 2025-07) | 0.66 |
| 30-day change to the 15th | Cochabamba | Matched basket | 25 | -0.31 | 1.63 | 2.35 | 0.63 | 0.02/0.12/0.86 | 71% | 72% (2026-07 2026-06 2025-07) | 0.57 |
| 30-day change to the 15th | SantaCruz | Matched basket | 25 | -0.18 | 1.10 | 1.42 | 0.78 | 0.02/0.05/0.93 | 54% | 54% (2025-06 2025-12 2025-01) | 0.83 |
| Monthly average, 12-month | National | Matched basket | 14 | -3.48 | 3.92 | 4.58 | 0.98 | 0.58/0.06/0.37 | 92% | 49% (2026-06 2026-09 2026-05) | 1.36 |
| Monthly average, 12-month | National | Overall | 14 | -0.67 | 6.11 | 7.05 | 0.99 | 0.01/0.96/0.03 | 92% | 47% (2026-06 2026-09 2026-08) | 3.78 |
| Monthly average, 12-month | LaPaz | Matched basket | 14 | -5.26 | 5.51 | 6.94 | 0.95 | 0.57/0.10/0.33 | 85% | 72% (2026-06 2026-05 2026-09) | 1.52 |
| Monthly average, 12-month | Cochabamba | Matched basket | 14 | -1.20 | 2.61 | 3.16 | 0.98 | 0.14/0.14/0.72 | 92% | 63% (2026-09 2026-06 2026-03) | 0.89 |
| Monthly average, 12-month | SantaCruz | Matched basket | 14 | -0.89 | 3.13 | 3.52 | 0.97 | 0.06/0.01/0.93 | 85% | 56% (2025-11 2026-03 2025-10) | 0.94 |

## Pseudo out-of-sample nowcasts (national MoM, expanding window, first 12 months for training)

| Measure | Target | Model | N | Bias | MAE | RMSE | RW ratio | DM p vs RW |
|---|---|---|---|---|---|---|---|---|
| Monthly average, MoM | Matched basket | Raw synthetic | 13 | -0.50 | 1.63 | 2.44 | 0.67 | 0.256 |
| Monthly average, MoM | Matched basket | Calibrated synthetic | 13 | +0.20 | 1.59 | 2.48 | 0.68 | 0.212 |
| Monthly average, MoM | Matched basket | Random walk | 13 | +0.02 | 2.33 | 3.64 | 1.00 |  |
| Monthly average, MoM | Matched basket | Expanding mean | 13 | +1.74 | 2.42 | 3.03 | 0.83 | 0.451 |
| Monthly average, MoM | Overall | Raw synthetic | 13 | -0.83 | 1.21 | 1.52 | 0.78 | 0.471 |
| Monthly average, MoM | Overall | Calibrated synthetic | 13 | +0.05 | 0.83 | 1.27 | 0.65 | 0.159 |
| Monthly average, MoM | Overall | Random walk | 13 | +0.01 | 1.26 | 1.95 | 1.00 |  |
| Monthly average, MoM | Overall | Expanding mean | 13 | +0.96 | 1.24 | 1.59 | 0.82 | 0.384 |
| 30-day change to the 15th | Matched basket | Raw synthetic | 13 | -0.49 | 1.60 | 2.40 | 0.66 | 0.244 |
| 30-day change to the 15th | Matched basket | Calibrated synthetic | 13 | +0.25 | 1.57 | 2.45 | 0.67 | 0.203 |
| 30-day change to the 15th | Matched basket | Random walk | 13 | +0.02 | 2.33 | 3.64 | 1.00 |  |
| 30-day change to the 15th | Matched basket | Expanding mean | 13 | +1.74 | 2.42 | 3.03 | 0.83 | 0.451 |
| 30-day change to the 15th | Overall | Raw synthetic | 13 | -0.82 | 1.20 | 1.49 | 0.77 | 0.444 |
| 30-day change to the 15th | Overall | Calibrated synthetic | 13 | +0.08 | 0.82 | 1.26 | 0.65 | 0.150 |
| 30-day change to the 15th | Overall | Random walk | 13 | +0.01 | 1.26 | 1.95 | 1.00 |  |
| 30-day change to the 15th | Overall | Expanding mean | 13 | +0.96 | 1.24 | 1.59 | 0.82 | 0.384 |

## Lag profile (synthetic 30-day change ending `lag` days before the 15th of month M)

| Target | RMSE at lag 0 | Lowest RMSE (lag) | Corr at lag 0 | Highest corr (lag) |
|---|---|---|---|---|
| Matched basket | 1.99 | 1.98 (4d) | 0.67 | 0.67 (4d) |
| Overall | 1.53 | 1.50 (-2d) | 0.71 | 0.71 (4d) |
