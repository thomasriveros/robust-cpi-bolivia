# Paper analysis: Core-4, mid-month dating

- Tracker data through: 2026-10-06
- Latest official observation placed on: 2026-09-15
- Official series rebased to July 2024 = 100; synthetic inflation is a 30-day change.

## Correlation and mean absolute difference

| Region | Metric | N | Correlation | MAD |
|---|---|---|---|---|
| National | Index | 26 | 0.965 | 4.453 |
| National Overall | Index | 26 | 0.926 | 4.736 |
| LaPaz | Index | 26 | 0.921 | 5.776 |
| Cochabamba | Index | 26 | 0.971 | 3.073 |
| SantaCruz | Index | 26 | 0.982 | 2.963 |
| National | Inflation | 25 | 0.669 | 1.398 |
| National Overall | Inflation | 25 | 0.708 | 1.244 |
| LaPaz | Inflation | 25 | 0.420 | 2.156 |
| Cochabamba | Inflation | 25 | 0.634 | 1.631 |
| SantaCruz | Inflation | 25 | 0.778 | 1.101 |

## Lag regressions (official MoM inflation on lagged synthetic inflation)

| Dependent | Lag | Method | N | Slope | SE | p | Intercept |
|---|---|---|---|---|---|---|---|
| Core-4 | 0 | OLS | 25 | 0.795 | 0.184 | 0.0003 | 0.552 |
| Core-4 | 0 | OLS (HC1 SEs) | 25 | 0.795 | 0.153 | 0.0000 | 0.552 |
| Core-4 | 0 | Huber RLM | 25 | 0.826 | 0.134 | 0.0000 | 0.598 |
| Core-4 | 15 | OLS | 25 | 0.683 | 0.192 | 0.0016 | 0.648 |
| Core-4 | 15 | OLS (HC1 SEs) | 25 | 0.683 | 0.209 | 0.0011 | 0.648 |
| Core-4 | 15 | Huber RLM | 25 | 0.733 | 0.155 | 0.0000 | 0.691 |
| Core-4 | 20 | OLS | 24 | 0.680 | 0.210 | 0.0038 | 0.643 |
| Core-4 | 20 | OLS (HC1 SEs) | 24 | 0.680 | 0.266 | 0.0106 | 0.643 |
| Core-4 | 20 | Huber RLM | 24 | 0.784 | 0.180 | 0.0000 | 0.682 |
| Overall | 0 | OLS | 25 | 0.465 | 0.097 | 0.0001 | 0.657 |
| Overall | 0 | OLS (HC1 SEs) | 25 | 0.465 | 0.086 | 0.0000 | 0.657 |
| Overall | 0 | Huber RLM | 25 | 0.466 | 0.079 | 0.0000 | 0.717 |
| Overall | 15 | OLS | 25 | 0.398 | 0.102 | 0.0007 | 0.715 |
| Overall | 15 | OLS (HC1 SEs) | 25 | 0.398 | 0.118 | 0.0008 | 0.715 |
| Overall | 15 | Huber RLM | 25 | 0.382 | 0.107 | 0.0004 | 0.782 |
| Overall | 20 | OLS | 24 | 0.401 | 0.112 | 0.0016 | 0.716 |
| Overall | 20 | OLS (HC1 SEs) | 24 | 0.401 | 0.147 | 0.0063 | 0.716 |
| Overall | 20 | Huber RLM | 24 | 0.419 | 0.112 | 0.0002 | 0.779 |
