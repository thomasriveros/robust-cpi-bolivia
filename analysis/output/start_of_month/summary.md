# Paper analysis: start-of-month dating

- Tracker data through: 2026-04-26
- Latest official observation placed on: 2026-10-01
- Official series rebased to July 2024 = 100; synthetic inflation is a 30-day change.

## Correlation and mean absolute difference

| Region | Metric | N | Correlation | MAD |
|---|---|---|---|---|
| National | Index | 21 | 0.986 | 2.182 |
| National Overall | Index | 21 | 0.975 | 5.156 |
| LaPaz | Index | 21 | 0.986 | 2.826 |
| Cochabamba | Index | 21 | 0.979 | 2.224 |
| SantaCruz | Index | 21 | 0.978 | 2.268 |
| National | Inflation | 20 | 0.800 | 1.256 |
| National Overall | Inflation | 20 | 0.797 | 1.260 |
| LaPaz | Inflation | 20 | 0.716 | 1.370 |
| Cochabamba | Inflation | 20 | 0.713 | 1.441 |
| SantaCruz | Inflation | 20 | 0.728 | 1.541 |

## Lag regressions (official MoM inflation on lagged synthetic inflation)

| Dependent | Lag | Method | N | Slope | SE | p | Intercept |
|---|---|---|---|---|---|---|---|
| Core-5 | 0 | OLS | 20 | 0.639 | 0.113 | 0.0000 | 0.629 |
| Core-5 | 0 | OLS (HC1 SEs) | 20 | 0.639 | 0.127 | 0.0000 | 0.629 |
| Core-5 | 0 | Huber RLM | 20 | 0.682 | 0.109 | 0.0000 | 0.635 |
| Core-5 | 15 | OLS | 20 | 0.476 | 0.182 | 0.0174 | 0.938 |
| Core-5 | 15 | OLS (HC1 SEs) | 20 | 0.476 | 0.308 | 0.1223 | 0.938 |
| Core-5 | 15 | Huber RLM | 20 | 0.460 | 0.161 | 0.0043 | 0.778 |
| Core-5 | 20 | OLS | 20 | 0.419 | 0.183 | 0.0343 | 1.012 |
| Core-5 | 20 | OLS (HC1 SEs) | 20 | 0.419 | 0.292 | 0.1507 | 1.012 |
| Core-5 | 20 | Huber RLM | 20 | 0.338 | 0.180 | 0.0602 | 0.846 |
| Overall | 0 | OLS | 20 | 0.386 | 0.069 | 0.0000 | 0.733 |
| Overall | 0 | OLS (HC1 SEs) | 20 | 0.386 | 0.086 | 0.0000 | 0.733 |
| Overall | 0 | Huber RLM | 20 | 0.431 | 0.062 | 0.0000 | 0.747 |
| Overall | 15 | OLS | 20 | 0.286 | 0.109 | 0.0173 | 0.923 |
| Overall | 15 | OLS (HC1 SEs) | 20 | 0.286 | 0.185 | 0.1227 | 0.923 |
| Overall | 15 | Huber RLM | 20 | 0.213 | 0.105 | 0.0423 | 0.886 |
| Overall | 20 | OLS | 20 | 0.253 | 0.110 | 0.0335 | 0.967 |
| Overall | 20 | OLS (HC1 SEs) | 20 | 0.253 | 0.176 | 0.1500 | 0.967 |
| Overall | 20 | Huber RLM | 20 | 0.163 | 0.093 | 0.0790 | 0.909 |
