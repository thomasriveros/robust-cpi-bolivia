# Paper analysis: start-of-month dating

- Tracker data through: 2026-11-21
- Latest official observation placed on: 2026-10-01
- Official series rebased to July 2024 = 100; synthetic inflation is a 30-day change.

## Correlation and mean absolute difference

| Region | Metric | N | Correlation | MAD |
|---|---|---|---|---|
| National | Index | 27 | 0.949 | 4.070 |
| National Overall | Index | 27 | 0.904 | 4.811 |
| LaPaz | Index | 27 | 0.919 | 5.554 |
| Cochabamba | Index | 27 | 0.944 | 3.458 |
| SantaCruz | Index | 27 | 0.968 | 2.993 |
| National | Inflation | 26 | 0.623 | 1.601 |
| National Overall | Inflation | 26 | 0.623 | 1.408 |
| LaPaz | Inflation | 26 | 0.429 | 2.090 |
| Cochabamba | Inflation | 26 | 0.487 | 1.872 |
| SantaCruz | Inflation | 26 | 0.730 | 1.388 |

## Lag regressions (official MoM inflation on lagged synthetic inflation)

| Dependent | Lag | Method | N | Slope | SE | p | Intercept |
|---|---|---|---|---|---|---|---|
| Core-5 | 0 | OLS | 26 | 0.586 | 0.150 | 0.0007 | 0.798 |
| Core-5 | 0 | OLS (HC1 SEs) | 26 | 0.586 | 0.156 | 0.0002 | 0.798 |
| Core-5 | 0 | Huber RLM | 26 | 0.610 | 0.129 | 0.0000 | 0.846 |
| Core-5 | 15 | OLS | 25 | 0.464 | 0.196 | 0.0265 | 0.883 |
| Core-5 | 15 | OLS (HC1 SEs) | 25 | 0.464 | 0.296 | 0.1167 | 0.883 |
| Core-5 | 15 | Huber RLM | 25 | 0.320 | 0.197 | 0.1043 | 0.973 |
| Core-5 | 20 | OLS | 25 | 0.405 | 0.196 | 0.0501 | 0.941 |
| Core-5 | 20 | OLS (HC1 SEs) | 25 | 0.405 | 0.277 | 0.1432 | 0.941 |
| Core-5 | 20 | Huber RLM | 25 | 0.258 | 0.171 | 0.1329 | 1.023 |
| Overall | 0 | OLS | 26 | 0.358 | 0.092 | 0.0007 | 0.822 |
| Overall | 0 | OLS (HC1 SEs) | 26 | 0.358 | 0.102 | 0.0005 | 0.822 |
| Overall | 0 | Huber RLM | 26 | 0.396 | 0.073 | 0.0000 | 0.861 |
| Overall | 15 | OLS | 25 | 0.279 | 0.120 | 0.0287 | 0.888 |
| Overall | 15 | OLS (HC1 SEs) | 25 | 0.279 | 0.179 | 0.1191 | 0.888 |
| Overall | 15 | Huber RLM | 25 | 0.164 | 0.098 | 0.0956 | 0.972 |
| Overall | 20 | OLS | 25 | 0.245 | 0.120 | 0.0516 | 0.921 |
| Overall | 20 | OLS (HC1 SEs) | 25 | 0.245 | 0.168 | 0.1436 | 0.921 |
| Overall | 20 | Huber RLM | 25 | 0.141 | 0.097 | 0.1485 | 0.994 |
