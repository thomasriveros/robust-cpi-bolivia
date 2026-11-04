# Paper analysis: start-of-month dating

- Tracker data through: 2026-11-04
- Latest official observation placed on: 2026-09-01
- Official series rebased to July 2024 = 100; synthetic inflation is a 30-day change.

## Correlation and mean absolute difference

| Region | Metric | N | Correlation | MAD |
|---|---|---|---|---|
| National | Index | 26 | 0.953 | 3.771 |
| National Overall | Index | 26 | 0.913 | 4.813 |
| LaPaz | Index | 26 | 0.923 | 5.208 |
| Cochabamba | Index | 26 | 0.952 | 3.139 |
| SantaCruz | Index | 26 | 0.971 | 2.828 |
| National | Inflation | 25 | 0.616 | 1.618 |
| National Overall | Inflation | 25 | 0.619 | 1.433 |
| LaPaz | Inflation | 25 | 0.426 | 2.143 |
| Cochabamba | Inflation | 25 | 0.479 | 1.898 |
| SantaCruz | Inflation | 25 | 0.733 | 1.399 |

## Lag regressions (official MoM inflation on lagged synthetic inflation)

| Dependent | Lag | Method | N | Slope | SE | p | Intercept |
|---|---|---|---|---|---|---|---|
| Core-5 | 0 | OLS | 25 | 0.576 | 0.154 | 0.0010 | 0.766 |
| Core-5 | 0 | OLS (HC1 SEs) | 25 | 0.576 | 0.160 | 0.0003 | 0.766 |
| Core-5 | 0 | Huber RLM | 25 | 0.597 | 0.134 | 0.0000 | 0.801 |
| Core-5 | 15 | OLS | 24 | 0.475 | 0.197 | 0.0250 | 0.820 |
| Core-5 | 15 | OLS (HC1 SEs) | 24 | 0.475 | 0.299 | 0.1120 | 0.820 |
| Core-5 | 15 | Huber RLM | 24 | 0.342 | 0.190 | 0.0712 | 0.875 |
| Core-5 | 20 | OLS | 24 | 0.414 | 0.198 | 0.0485 | 0.888 |
| Core-5 | 20 | OLS (HC1 SEs) | 24 | 0.414 | 0.281 | 0.1398 | 0.888 |
| Core-5 | 20 | Huber RLM | 24 | 0.258 | 0.179 | 0.1483 | 0.942 |
| Overall | 0 | OLS | 25 | 0.351 | 0.093 | 0.0010 | 0.793 |
| Overall | 0 | OLS (HC1 SEs) | 25 | 0.351 | 0.105 | 0.0008 | 0.793 |
| Overall | 0 | Huber RLM | 25 | 0.386 | 0.072 | 0.0000 | 0.825 |
| Overall | 15 | OLS | 24 | 0.286 | 0.120 | 0.0262 | 0.840 |
| Overall | 15 | OLS (HC1 SEs) | 24 | 0.286 | 0.181 | 0.1138 | 0.840 |
| Overall | 15 | Huber RLM | 24 | 0.166 | 0.094 | 0.0768 | 0.905 |
| Overall | 20 | OLS | 24 | 0.250 | 0.120 | 0.0494 | 0.881 |
| Overall | 20 | OLS (HC1 SEs) | 24 | 0.250 | 0.170 | 0.1403 | 0.881 |
| Overall | 20 | Huber RLM | 24 | 0.141 | 0.094 | 0.1355 | 0.934 |
