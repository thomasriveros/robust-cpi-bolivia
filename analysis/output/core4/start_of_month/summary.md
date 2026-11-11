# Paper analysis: Core-4, start-of-month dating

- Tracker data through: 2026-11-11
- Latest official observation placed on: 2026-10-01
- Official series rebased to July 2024 = 100; synthetic inflation is a 30-day change.

## Correlation and mean absolute difference

| Region | Metric | N | Correlation | MAD |
|---|---|---|---|---|
| National | Index | 27 | 0.960 | 5.096 |
| National Overall | Index | 27 | 0.924 | 4.267 |
| LaPaz | Index | 27 | 0.924 | 6.516 |
| Cochabamba | Index | 27 | 0.957 | 3.956 |
| SantaCruz | Index | 27 | 0.973 | 3.426 |
| National | Inflation | 26 | 0.606 | 1.667 |
| National Overall | Inflation | 26 | 0.647 | 1.296 |
| LaPaz | Inflation | 26 | 0.420 | 2.340 |
| Cochabamba | Inflation | 26 | 0.520 | 1.963 |
| SantaCruz | Inflation | 26 | 0.674 | 1.334 |

## Lag regressions (official MoM inflation on lagged synthetic inflation)

| Dependent | Lag | Method | N | Slope | SE | p | Intercept |
|---|---|---|---|---|---|---|---|
| Core-4 | 0 | OLS | 26 | 0.696 | 0.186 | 0.0010 | 0.734 |
| Core-4 | 0 | OLS (HC1 SEs) | 26 | 0.696 | 0.189 | 0.0002 | 0.734 |
| Core-4 | 0 | Huber RLM | 26 | 0.719 | 0.166 | 0.0000 | 0.825 |
| Core-4 | 15 | OLS | 25 | 0.509 | 0.229 | 0.0361 | 0.868 |
| Core-4 | 15 | OLS (HC1 SEs) | 25 | 0.509 | 0.344 | 0.1389 | 0.868 |
| Core-4 | 15 | Huber RLM | 25 | 0.397 | 0.213 | 0.0621 | 0.999 |
| Core-4 | 20 | OLS | 25 | 0.428 | 0.227 | 0.0727 | 0.950 |
| Core-4 | 20 | OLS (HC1 SEs) | 25 | 0.428 | 0.320 | 0.1813 | 0.950 |
| Core-4 | 20 | Huber RLM | 25 | 0.264 | 0.198 | 0.1828 | 1.091 |
| Overall | 0 | OLS | 26 | 0.411 | 0.099 | 0.0004 | 0.765 |
| Overall | 0 | OLS (HC1 SEs) | 26 | 0.411 | 0.107 | 0.0001 | 0.765 |
| Overall | 0 | Huber RLM | 26 | 0.416 | 0.097 | 0.0000 | 0.838 |
| Overall | 15 | OLS | 25 | 0.301 | 0.124 | 0.0237 | 0.853 |
| Overall | 15 | OLS (HC1 SEs) | 25 | 0.301 | 0.191 | 0.1138 | 0.853 |
| Overall | 15 | Huber RLM | 25 | 0.174 | 0.105 | 0.0984 | 0.963 |
| Overall | 20 | OLS | 25 | 0.257 | 0.124 | 0.0494 | 0.898 |
| Overall | 20 | OLS (HC1 SEs) | 25 | 0.257 | 0.178 | 0.1479 | 0.898 |
| Overall | 20 | Huber RLM | 25 | 0.141 | 0.107 | 0.1898 | 0.989 |
