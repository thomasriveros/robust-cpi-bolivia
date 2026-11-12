# Paper analysis: start-of-month dating

- Tracker data through: 2026-11-12
- Latest official observation placed on: 2026-10-01
- Official series rebased to July 2024 = 100; synthetic inflation is a 30-day change.

## Correlation and mean absolute difference

| Region | Metric | N | Correlation | MAD |
|---|---|---|---|---|
| National | Index | 27 | 0.949 | 4.076 |
| National Overall | Index | 27 | 0.904 | 4.818 |
| LaPaz | Index | 27 | 0.919 | 5.551 |
| Cochabamba | Index | 27 | 0.944 | 3.458 |
| SantaCruz | Index | 27 | 0.968 | 2.993 |
| National | Inflation | 26 | 0.629 | 1.589 |
| National Overall | Inflation | 26 | 0.629 | 1.397 |
| LaPaz | Inflation | 26 | 0.426 | 2.106 |
| Cochabamba | Inflation | 26 | 0.487 | 1.872 |
| SantaCruz | Inflation | 26 | 0.730 | 1.388 |

## Lag regressions (official MoM inflation on lagged synthetic inflation)

| Dependent | Lag | Method | N | Slope | SE | p | Intercept |
|---|---|---|---|---|---|---|---|
| Core-5 | 0 | OLS | 26 | 0.592 | 0.149 | 0.0006 | 0.793 |
| Core-5 | 0 | OLS (HC1 SEs) | 26 | 0.592 | 0.157 | 0.0002 | 0.793 |
| Core-5 | 0 | Huber RLM | 26 | 0.617 | 0.126 | 0.0000 | 0.837 |
| Core-5 | 15 | OLS | 25 | 0.463 | 0.196 | 0.0268 | 0.884 |
| Core-5 | 15 | OLS (HC1 SEs) | 25 | 0.463 | 0.295 | 0.1168 | 0.884 |
| Core-5 | 15 | Huber RLM | 25 | 0.316 | 0.197 | 0.1090 | 0.975 |
| Core-5 | 20 | OLS | 25 | 0.405 | 0.196 | 0.0504 | 0.941 |
| Core-5 | 20 | OLS (HC1 SEs) | 25 | 0.405 | 0.276 | 0.1432 | 0.941 |
| Core-5 | 20 | Huber RLM | 25 | 0.257 | 0.171 | 0.1338 | 1.024 |
| Overall | 0 | OLS | 26 | 0.361 | 0.091 | 0.0006 | 0.819 |
| Overall | 0 | OLS (HC1 SEs) | 26 | 0.361 | 0.102 | 0.0004 | 0.819 |
| Overall | 0 | Huber RLM | 26 | 0.398 | 0.069 | 0.0000 | 0.856 |
| Overall | 15 | OLS | 25 | 0.278 | 0.119 | 0.0289 | 0.888 |
| Overall | 15 | OLS (HC1 SEs) | 25 | 0.278 | 0.179 | 0.1191 | 0.888 |
| Overall | 15 | Huber RLM | 25 | 0.163 | 0.098 | 0.0966 | 0.973 |
| Overall | 20 | OLS | 25 | 0.245 | 0.119 | 0.0518 | 0.922 |
| Overall | 20 | OLS (HC1 SEs) | 25 | 0.245 | 0.168 | 0.1435 | 0.922 |
| Overall | 20 | Huber RLM | 25 | 0.140 | 0.097 | 0.1492 | 0.994 |
