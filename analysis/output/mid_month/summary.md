# Paper analysis: mid-month dating

- Tracker data through: 2026-11-21
- Latest official observation placed on: 2026-10-15
- Official series rebased to July 2024 = 100; synthetic inflation is a 30-day change.

## Correlation and mean absolute difference

| Region | Metric | N | Correlation | MAD |
|---|---|---|---|---|
| National | Index | 27 | 0.948 | 3.835 |
| National Overall | Index | 27 | 0.895 | 5.322 |
| LaPaz | Index | 27 | 0.909 | 5.258 |
| Cochabamba | Index | 27 | 0.951 | 2.960 |
| SantaCruz | Index | 27 | 0.971 | 2.788 |
| National | Inflation | 26 | 0.668 | 1.327 |
| National Overall | Inflation | 26 | 0.659 | 1.337 |
| LaPaz | Inflation | 26 | 0.385 | 1.970 |
| Cochabamba | Inflation | 26 | 0.620 | 1.545 |
| SantaCruz | Inflation | 26 | 0.771 | 1.199 |

## Lag regressions (official MoM inflation on lagged synthetic inflation)

| Dependent | Lag | Method | N | Slope | SE | p | Intercept |
|---|---|---|---|---|---|---|---|
| Core-5 | 0 | OLS | 26 | 0.696 | 0.158 | 0.0002 | 0.680 |
| Core-5 | 0 | OLS (HC1 SEs) | 26 | 0.696 | 0.159 | 0.0000 | 0.680 |
| Core-5 | 0 | Huber RLM | 26 | 0.758 | 0.117 | 0.0000 | 0.700 |
| Core-5 | 15 | OLS | 26 | 0.607 | 0.153 | 0.0006 | 0.768 |
| Core-5 | 15 | OLS (HC1 SEs) | 26 | 0.607 | 0.166 | 0.0003 | 0.768 |
| Core-5 | 15 | Huber RLM | 26 | 0.636 | 0.126 | 0.0000 | 0.790 |
| Core-5 | 20 | OLS | 25 | 0.611 | 0.175 | 0.0020 | 0.756 |
| Core-5 | 20 | OLS (HC1 SEs) | 25 | 0.611 | 0.223 | 0.0061 | 0.756 |
| Core-5 | 20 | Huber RLM | 25 | 0.692 | 0.154 | 0.0000 | 0.760 |
| Overall | 0 | OLS | 26 | 0.418 | 0.097 | 0.0003 | 0.756 |
| Overall | 0 | OLS (HC1 SEs) | 26 | 0.418 | 0.100 | 0.0000 | 0.756 |
| Overall | 0 | Huber RLM | 26 | 0.423 | 0.082 | 0.0000 | 0.800 |
| Overall | 15 | OLS | 26 | 0.365 | 0.094 | 0.0007 | 0.808 |
| Overall | 15 | OLS (HC1 SEs) | 26 | 0.365 | 0.108 | 0.0007 | 0.808 |
| Overall | 15 | Huber RLM | 26 | 0.372 | 0.087 | 0.0000 | 0.855 |
| Overall | 20 | OLS | 25 | 0.371 | 0.107 | 0.0021 | 0.809 |
| Overall | 20 | OLS (HC1 SEs) | 25 | 0.371 | 0.138 | 0.0071 | 0.809 |
| Overall | 20 | Huber RLM | 25 | 0.404 | 0.096 | 0.0000 | 0.851 |
