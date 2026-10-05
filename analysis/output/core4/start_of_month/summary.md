# Paper analysis: Core-4, start-of-month dating

- Tracker data through: 2026-10-05
- Latest official observation placed on: 2026-09-01
- Official series rebased to July 2024 = 100; synthetic inflation is a 30-day change.

## Correlation and mean absolute difference

| Region | Metric | N | Correlation | MAD |
|---|---|---|---|---|
| National | Index | 26 | 0.963 | 4.792 |
| National Overall | Index | 26 | 0.932 | 4.265 |
| LaPaz | Index | 26 | 0.926 | 6.182 |
| Cochabamba | Index | 26 | 0.962 | 3.654 |
| SantaCruz | Index | 26 | 0.975 | 3.258 |
| National | Inflation | 25 | 0.609 | 1.665 |
| National Overall | Inflation | 25 | 0.652 | 1.306 |
| LaPaz | Inflation | 25 | 0.420 | 2.377 |
| Cochabamba | Inflation | 25 | 0.522 | 1.967 |
| SantaCruz | Inflation | 25 | 0.680 | 1.325 |

## Lag regressions (official MoM inflation on lagged synthetic inflation)

| Dependent | Lag | Method | N | Slope | SE | p | Intercept |
|---|---|---|---|---|---|---|---|
| Core-4 | 0 | OLS | 25 | 0.695 | 0.189 | 0.0012 | 0.684 |
| Core-4 | 0 | OLS (HC1 SEs) | 25 | 0.695 | 0.190 | 0.0003 | 0.684 |
| Core-4 | 0 | Huber RLM | 25 | 0.707 | 0.166 | 0.0000 | 0.768 |
| Core-4 | 15 | OLS | 24 | 0.517 | 0.232 | 0.0361 | 0.792 |
| Core-4 | 15 | OLS (HC1 SEs) | 24 | 0.517 | 0.345 | 0.1340 | 0.792 |
| Core-4 | 15 | Huber RLM | 24 | 0.415 | 0.208 | 0.0455 | 0.889 |
| Core-4 | 20 | OLS | 24 | 0.431 | 0.231 | 0.0751 | 0.886 |
| Core-4 | 20 | OLS (HC1 SEs) | 24 | 0.431 | 0.320 | 0.1774 | 0.886 |
| Core-4 | 20 | Huber RLM | 24 | 0.264 | 0.193 | 0.1716 | 0.994 |
| Overall | 0 | OLS | 25 | 0.411 | 0.100 | 0.0004 | 0.730 |
| Overall | 0 | OLS (HC1 SEs) | 25 | 0.411 | 0.107 | 0.0001 | 0.730 |
| Overall | 0 | Huber RLM | 25 | 0.421 | 0.091 | 0.0000 | 0.796 |
| Overall | 15 | OLS | 24 | 0.307 | 0.126 | 0.0230 | 0.802 |
| Overall | 15 | OLS (HC1 SEs) | 24 | 0.307 | 0.191 | 0.1085 | 0.802 |
| Overall | 15 | Huber RLM | 24 | 0.177 | 0.101 | 0.0789 | 0.895 |
| Overall | 20 | OLS | 24 | 0.260 | 0.125 | 0.0503 | 0.854 |
| Overall | 20 | OLS (HC1 SEs) | 24 | 0.260 | 0.178 | 0.1438 | 0.854 |
| Overall | 20 | Huber RLM | 24 | 0.143 | 0.098 | 0.1466 | 0.927 |
