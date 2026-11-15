# Tracking accuracy: Core-5

- Official data through: 2026-04
- Errors are synthetic minus official, in percentage points. Matched basket = official series built from the same INE divisions as the tracker.
- Theil shares split the MSE into bias, variance (scale mismatch) and covariance (unsystematic) parts.
- RW ratio < 1: the synthetic measure beats last month's official inflation (random walk) on the same months.

## In-sample accuracy

| Measure | Region | Target | N | Bias | MAE | RMSE | Corr | Theil bias/var/cov | Direction | Top-3 share of SSE | RW ratio |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Monthly average, MoM | National | Matched basket | 20 | -0.16 | 0.94 | 1.18 | 0.87 | 0.02/0.05/0.93 | 79% | 60% (2025-07 2024-09 2025-03) | 0.58 |
| Monthly average, MoM | National | Overall | 20 | +0.06 | 1.19 | 1.45 | 0.85 | 0.00/0.56/0.44 | 74% | 51% (2024-09 2025-07 2025-05) | 1.10 |
| Monthly average, MoM | LaPaz | Matched basket | 20 | -0.16 | 1.22 | 1.59 | 0.77 | 0.01/0.01/0.98 | 63% | 59% (2025-07 2024-09 2025-06) | 0.57 |
| Monthly average, MoM | Cochabamba | Matched basket | 20 | -0.00 | 1.05 | 1.43 | 0.82 | 0.00/0.00/1.00 | 63% | 66% (2025-07 2024-09 2025-03) | 0.58 |
| Monthly average, MoM | SantaCruz | Matched basket | 20 | -0.15 | 1.22 | 1.45 | 0.82 | 0.01/0.18/0.81 | 74% | 49% (2025-06 2024-12 2025-01) | 0.91 |
| 30-day change to the 15th | National | Matched basket | 20 | -0.22 | 0.94 | 1.15 | 0.88 | 0.04/0.06/0.90 | 79% | 53% (2025-07 2025-03 2024-09) | 0.57 |
| 30-day change to the 15th | National | Overall | 20 | -0.00 | 1.20 | 1.44 | 0.86 | 0.00/0.59/0.41 | 74% | 52% (2025-06 2024-09 2025-07) | 1.09 |
| 30-day change to the 15th | LaPaz | Matched basket | 20 | -0.22 | 1.22 | 1.56 | 0.78 | 0.02/0.02/0.97 | 63% | 58% (2025-07 2025-06 2025-03) | 0.56 |
| 30-day change to the 15th | Cochabamba | Matched basket | 20 | -0.06 | 1.02 | 1.38 | 0.83 | 0.00/0.00/1.00 | 63% | 64% (2025-07 2024-09 2025-03) | 0.55 |
| 30-day change to the 15th | SantaCruz | Matched basket | 20 | -0.21 | 1.33 | 1.67 | 0.78 | 0.02/0.20/0.78 | 58% | 59% (2025-06 2025-01 2024-12) | 1.04 |
| Monthly average, 12-month | National | Matched basket | 9 | -1.25 | 1.88 | 2.37 | 0.97 | 0.28/0.28/0.44 | 100% | 83% (2025-10 2025-09 2025-11) | 0.91 |
| Monthly average, 12-month | National | Overall | 9 | +4.24 | 4.34 | 5.06 | 0.97 | 0.70/0.26/0.04 | 100% | 72% (2025-08 2025-09 2025-10) | 3.78 |
| Monthly average, 12-month | LaPaz | Matched basket | 9 | -2.04 | 2.46 | 2.78 | 0.96 | 0.54/0.14/0.32 | 100% | 66% (2025-09 2025-10 2025-12) | 1.10 |
| Monthly average, 12-month | Cochabamba | Matched basket | 9 | +1.13 | 2.13 | 2.44 | 0.97 | 0.21/0.37/0.41 | 100% | 73% (2026-03 2026-02 2025-09) | 0.91 |
| Monthly average, 12-month | SantaCruz | Matched basket | 9 | +0.24 | 2.29 | 2.67 | 0.96 | 0.01/0.40/0.60 | 88% | 70% (2025-11 2026-03 2026-01) | 0.80 |

## Pseudo out-of-sample nowcasts (national MoM, expanding window, first 12 months for training)

| Measure | Target | Model | N | Bias | MAE | RMSE | RW ratio | DM p vs RW |
|---|---|---|---|---|---|---|---|---|
| Monthly average, MoM | Matched basket | Raw synthetic | 8 | -0.36 | 0.53 | 0.63 | 0.63 | 0.204 |
| Monthly average, MoM | Matched basket | Calibrated synthetic | 8 | +0.43 | 0.58 | 0.73 | 0.74 | 0.005 |
| Monthly average, MoM | Matched basket | Random walk | 8 | +0.13 | 0.91 | 1.00 | 1.00 |  |
| Monthly average, MoM | Matched basket | Expanding mean | 8 | +2.25 | 2.25 | 2.36 | 2.37 | 0.003 |
| Monthly average, MoM | Overall | Raw synthetic | 8 | -0.89 | 0.89 | 0.98 | 1.16 | 0.673 |
| Monthly average, MoM | Overall | Calibrated synthetic | 8 | +0.15 | 0.42 | 0.49 | 0.58 | 0.257 |
| Monthly average, MoM | Overall | Random walk | 8 | +0.11 | 0.66 | 0.84 | 1.00 |  |
| Monthly average, MoM | Overall | Expanding mean | 8 | +1.24 | 1.24 | 1.35 | 1.61 | 0.015 |
| 30-day change to the 15th | Matched basket | Raw synthetic | 8 | -0.38 | 0.52 | 0.65 | 0.65 | 0.236 |
| 30-day change to the 15th | Matched basket | Calibrated synthetic | 8 | +0.45 | 0.62 | 0.75 | 0.75 | 0.008 |
| 30-day change to the 15th | Matched basket | Random walk | 8 | +0.13 | 0.91 | 1.00 | 1.00 |  |
| 30-day change to the 15th | Matched basket | Expanding mean | 8 | +2.25 | 2.25 | 2.36 | 2.37 | 0.003 |
| 30-day change to the 15th | Overall | Raw synthetic | 8 | -0.91 | 0.91 | 1.02 | 1.21 | 0.595 |
| 30-day change to the 15th | Overall | Calibrated synthetic | 8 | +0.15 | 0.43 | 0.50 | 0.60 | 0.271 |
| 30-day change to the 15th | Overall | Random walk | 8 | +0.11 | 0.66 | 0.84 | 1.00 |  |
| 30-day change to the 15th | Overall | Expanding mean | 8 | +1.24 | 1.24 | 1.35 | 1.61 | 0.015 |

## Lag profile (synthetic 30-day change ending `lag` days before the 15th of month M)

| Target | RMSE at lag 0 | Lowest RMSE (lag) | Corr at lag 0 | Highest corr (lag) |
|---|---|---|---|---|
| Matched basket | 1.15 | 1.15 (0d) | 0.88 | 0.88 (0d) |
| Overall | 1.44 | 1.33 (-2d) | 0.86 | 0.86 (4d) |
