# Paper analysis: Core-4, start-of-month dating

- Tracker data through: 2026-09-30
- Latest official observation placed on: 2026-08-01
- Official series rebased to July 2024 = 100; synthetic inflation is a 30-day change.

## Correlation and mean absolute difference

| Region | Metric | N | Correlation | MAD |
|---|---|---|---|---|
| National | Index | 25 | 0.965 | 4.566 |
| National Overall | Index | 25 | 0.939 | 4.320 |
| LaPaz | Index | 25 | 0.927 | 5.912 |
| Cochabamba | Index | 25 | 0.965 | 3.438 |
| SantaCruz | Index | 25 | 0.975 | 3.162 |
| National | Inflation | 24 | 0.608 | 1.712 |
| National Overall | Inflation | 24 | 0.651 | 1.339 |
| LaPaz | Inflation | 24 | 0.419 | 2.452 |
| Cochabamba | Inflation | 24 | 0.525 | 1.982 |
| SantaCruz | Inflation | 24 | 0.680 | 1.362 |

## Lag regressions (official MoM inflation on lagged synthetic inflation)

| Dependent | Lag | Method | N | Slope | SE | p | Intercept |
|---|---|---|---|---|---|---|---|
| Core-4 | 0 | OLS | 24 | 0.695 | 0.193 | 0.0016 | 0.685 |
| Core-4 | 0 | OLS (HC1 SEs) | 24 | 0.695 | 0.191 | 0.0003 | 0.685 |
| Core-4 | 0 | Huber RLM | 24 | 0.701 | 0.176 | 0.0001 | 0.779 |
| Core-4 | 15 | OLS | 23 | 0.516 | 0.237 | 0.0411 | 0.803 |
| Core-4 | 15 | OLS (HC1 SEs) | 23 | 0.516 | 0.346 | 0.1355 | 0.803 |
| Core-4 | 15 | Huber RLM | 23 | 0.399 | 0.236 | 0.0903 | 0.933 |
| Core-4 | 20 | OLS | 23 | 0.430 | 0.237 | 0.0831 | 0.895 |
| Core-4 | 20 | OLS (HC1 SEs) | 23 | 0.430 | 0.321 | 0.1796 | 0.895 |
| Core-4 | 20 | Huber RLM | 23 | 0.272 | 0.216 | 0.2081 | 1.030 |
| Overall | 0 | OLS | 24 | 0.411 | 0.102 | 0.0006 | 0.731 |
| Overall | 0 | OLS (HC1 SEs) | 24 | 0.411 | 0.108 | 0.0001 | 0.731 |
| Overall | 0 | Huber RLM | 24 | 0.410 | 0.098 | 0.0000 | 0.804 |
| Overall | 15 | OLS | 23 | 0.306 | 0.129 | 0.0267 | 0.810 |
| Overall | 15 | OLS (HC1 SEs) | 23 | 0.306 | 0.192 | 0.1099 | 0.810 |
| Overall | 15 | Huber RLM | 23 | 0.177 | 0.106 | 0.0943 | 0.906 |
| Overall | 20 | OLS | 23 | 0.259 | 0.129 | 0.0567 | 0.860 |
| Overall | 20 | OLS (HC1 SEs) | 23 | 0.259 | 0.178 | 0.1456 | 0.860 |
| Overall | 20 | Huber RLM | 23 | 0.147 | 0.110 | 0.1803 | 0.945 |
