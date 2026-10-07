# Paper analysis: mid-month dating

- Tracker data through: 2026-10-07
- Latest official observation placed on: 2026-09-15
- Official series rebased to July 2024 = 100; synthetic inflation is a 30-day change.

## Correlation and mean absolute difference

| Region | Metric | N | Correlation | MAD |
|---|---|---|---|---|
| National | Index | 26 | 0.953 | 3.532 |
| National Overall | Index | 26 | 0.904 | 5.350 |
| LaPaz | Index | 26 | 0.912 | 4.903 |
| Cochabamba | Index | 26 | 0.957 | 2.668 |
| SantaCruz | Index | 26 | 0.974 | 2.625 |
| National | Inflation | 25 | 0.676 | 1.308 |
| National Overall | Inflation | 25 | 0.669 | 1.334 |
| LaPaz | Inflation | 25 | 0.369 | 2.023 |
| Cochabamba | Inflation | 25 | 0.621 | 1.551 |
| SantaCruz | Inflation | 25 | 0.783 | 1.174 |

## Lag regressions (official MoM inflation on lagged synthetic inflation)

| Dependent | Lag | Method | N | Slope | SE | p | Intercept |
|---|---|---|---|---|---|---|---|
| Core-5 | 0 | OLS | 25 | 0.700 | 0.159 | 0.0002 | 0.628 |
| Core-5 | 0 | OLS (HC1 SEs) | 25 | 0.700 | 0.161 | 0.0000 | 0.628 |
| Core-5 | 0 | Huber RLM | 25 | 0.747 | 0.118 | 0.0000 | 0.634 |
| Core-5 | 15 | OLS | 25 | 0.609 | 0.155 | 0.0007 | 0.714 |
| Core-5 | 15 | OLS (HC1 SEs) | 25 | 0.609 | 0.167 | 0.0003 | 0.714 |
| Core-5 | 15 | Huber RLM | 25 | 0.652 | 0.124 | 0.0000 | 0.717 |
| Core-5 | 20 | OLS | 24 | 0.613 | 0.177 | 0.0022 | 0.697 |
| Core-5 | 20 | OLS (HC1 SEs) | 24 | 0.613 | 0.224 | 0.0061 | 0.697 |
| Core-5 | 20 | Huber RLM | 24 | 0.704 | 0.156 | 0.0000 | 0.683 |
| Overall | 0 | OLS | 25 | 0.421 | 0.097 | 0.0003 | 0.715 |
| Overall | 0 | OLS (HC1 SEs) | 25 | 0.421 | 0.101 | 0.0000 | 0.715 |
| Overall | 0 | Huber RLM | 25 | 0.435 | 0.085 | 0.0000 | 0.745 |
| Overall | 15 | OLS | 25 | 0.367 | 0.095 | 0.0008 | 0.766 |
| Overall | 15 | OLS (HC1 SEs) | 25 | 0.367 | 0.108 | 0.0007 | 0.766 |
| Overall | 15 | Huber RLM | 25 | 0.382 | 0.082 | 0.0000 | 0.797 |
| Overall | 20 | OLS | 24 | 0.373 | 0.107 | 0.0022 | 0.763 |
| Overall | 20 | OLS (HC1 SEs) | 24 | 0.373 | 0.139 | 0.0071 | 0.763 |
| Overall | 20 | Huber RLM | 24 | 0.409 | 0.094 | 0.0000 | 0.792 |
