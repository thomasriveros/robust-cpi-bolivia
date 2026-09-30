# Paper analysis: start-of-month dating

- Tracker data through: 2026-09-30
- Latest official observation placed on: 2026-08-01
- Official series rebased to July 2024 = 100; synthetic inflation is a 30-day change.

## Correlation and mean absolute difference

| Region | Metric | N | Correlation | MAD |
|---|---|---|---|---|
| National | Index | 25 | 0.957 | 3.508 |
| National Overall | Index | 25 | 0.922 | 4.848 |
| LaPaz | Index | 25 | 0.925 | 4.907 |
| Cochabamba | Index | 25 | 0.957 | 2.930 |
| SantaCruz | Index | 25 | 0.972 | 2.712 |
| National | Inflation | 24 | 0.630 | 1.659 |
| National Overall | Inflation | 24 | 0.633 | 1.470 |
| LaPaz | Inflation | 24 | 0.426 | 2.229 |
| Cochabamba | Inflation | 24 | 0.491 | 1.913 |
| SantaCruz | Inflation | 24 | 0.737 | 1.431 |

## Lag regressions (official MoM inflation on lagged synthetic inflation)

| Dependent | Lag | Method | N | Slope | SE | p | Intercept |
|---|---|---|---|---|---|---|---|
| Core-5 | 0 | OLS | 24 | 0.590 | 0.155 | 0.0010 | 0.766 |
| Core-5 | 0 | OLS (HC1 SEs) | 24 | 0.590 | 0.158 | 0.0002 | 0.766 |
| Core-5 | 0 | Huber RLM | 24 | 0.606 | 0.139 | 0.0000 | 0.813 |
| Core-5 | 15 | OLS | 23 | 0.465 | 0.203 | 0.0326 | 0.846 |
| Core-5 | 15 | OLS (HC1 SEs) | 23 | 0.465 | 0.296 | 0.1162 | 0.846 |
| Core-5 | 15 | Huber RLM | 23 | 0.312 | 0.198 | 0.1139 | 0.921 |
| Core-5 | 20 | OLS | 23 | 0.402 | 0.204 | 0.0622 | 0.908 |
| Core-5 | 20 | OLS (HC1 SEs) | 23 | 0.402 | 0.276 | 0.1455 | 0.908 |
| Core-5 | 20 | Huber RLM | 23 | 0.257 | 0.186 | 0.1688 | 0.981 |
| Overall | 0 | OLS | 24 | 0.360 | 0.094 | 0.0009 | 0.795 |
| Overall | 0 | OLS (HC1 SEs) | 24 | 0.360 | 0.103 | 0.0005 | 0.795 |
| Overall | 0 | Huber RLM | 24 | 0.384 | 0.079 | 0.0000 | 0.841 |
| Overall | 15 | OLS | 23 | 0.280 | 0.123 | 0.0339 | 0.858 |
| Overall | 15 | OLS (HC1 SEs) | 23 | 0.280 | 0.179 | 0.1179 | 0.858 |
| Overall | 15 | Huber RLM | 23 | 0.166 | 0.103 | 0.1046 | 0.930 |
| Overall | 20 | OLS | 23 | 0.243 | 0.124 | 0.0633 | 0.895 |
| Overall | 20 | OLS (HC1 SEs) | 23 | 0.243 | 0.167 | 0.1462 | 0.895 |
| Overall | 20 | Huber RLM | 23 | 0.140 | 0.105 | 0.1819 | 0.961 |
