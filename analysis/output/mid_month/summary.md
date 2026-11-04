# Paper analysis: mid-month dating

- Tracker data through: 2026-11-04
- Latest official observation placed on: 2026-09-15
- Official series rebased to July 2024 = 100; synthetic inflation is a 30-day change.

## Correlation and mean absolute difference

| Region | Metric | N | Correlation | MAD |
|---|---|---|---|---|
| National | Index | 26 | 0.952 | 3.541 |
| National Overall | Index | 26 | 0.903 | 5.357 |
| LaPaz | Index | 26 | 0.912 | 4.905 |
| Cochabamba | Index | 26 | 0.959 | 2.640 |
| SantaCruz | Index | 26 | 0.974 | 2.625 |
| National | Inflation | 25 | 0.661 | 1.328 |
| National Overall | Inflation | 25 | 0.655 | 1.353 |
| LaPaz | Inflation | 25 | 0.369 | 2.023 |
| Cochabamba | Inflation | 25 | 0.632 | 1.541 |
| SantaCruz | Inflation | 25 | 0.783 | 1.174 |

## Lag regressions (official MoM inflation on lagged synthetic inflation)

| Dependent | Lag | Method | N | Slope | SE | p | Intercept |
|---|---|---|---|---|---|---|---|
| Core-5 | 0 | OLS | 25 | 0.685 | 0.162 | 0.0003 | 0.642 |
| Core-5 | 0 | OLS (HC1 SEs) | 25 | 0.685 | 0.162 | 0.0000 | 0.642 |
| Core-5 | 0 | Huber RLM | 25 | 0.737 | 0.120 | 0.0000 | 0.643 |
| Core-5 | 15 | OLS | 25 | 0.614 | 0.154 | 0.0006 | 0.715 |
| Core-5 | 15 | OLS (HC1 SEs) | 25 | 0.614 | 0.167 | 0.0002 | 0.715 |
| Core-5 | 15 | Huber RLM | 25 | 0.655 | 0.124 | 0.0000 | 0.717 |
| Core-5 | 20 | OLS | 24 | 0.622 | 0.176 | 0.0018 | 0.688 |
| Core-5 | 20 | OLS (HC1 SEs) | 24 | 0.622 | 0.225 | 0.0056 | 0.688 |
| Core-5 | 20 | Huber RLM | 24 | 0.719 | 0.147 | 0.0000 | 0.672 |
| Overall | 0 | OLS | 25 | 0.411 | 0.099 | 0.0004 | 0.723 |
| Overall | 0 | OLS (HC1 SEs) | 25 | 0.411 | 0.102 | 0.0001 | 0.723 |
| Overall | 0 | Huber RLM | 25 | 0.429 | 0.081 | 0.0000 | 0.750 |
| Overall | 15 | OLS | 25 | 0.370 | 0.094 | 0.0006 | 0.766 |
| Overall | 15 | OLS (HC1 SEs) | 25 | 0.370 | 0.108 | 0.0006 | 0.766 |
| Overall | 15 | Huber RLM | 25 | 0.385 | 0.081 | 0.0000 | 0.796 |
| Overall | 20 | OLS | 24 | 0.378 | 0.107 | 0.0018 | 0.758 |
| Overall | 20 | OLS (HC1 SEs) | 24 | 0.378 | 0.139 | 0.0065 | 0.758 |
| Overall | 20 | Huber RLM | 24 | 0.414 | 0.093 | 0.0000 | 0.782 |
