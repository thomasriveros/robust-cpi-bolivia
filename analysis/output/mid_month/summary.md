# Paper analysis: mid-month dating

- Tracker data through: 2026-04-26
- Latest official observation placed on: 2026-10-15
- Official series rebased to July 2024 = 100; synthetic inflation is a 30-day change.

## Correlation and mean absolute difference

| Region | Metric | N | Correlation | MAD |
|---|---|---|---|---|
| National | Index | 21 | 0.992 | 1.830 |
| National Overall | Index | 21 | 0.972 | 5.762 |
| LaPaz | Index | 21 | 0.992 | 2.308 |
| Cochabamba | Index | 21 | 0.991 | 1.448 |
| SantaCruz | Index | 21 | 0.983 | 2.071 |
| National | Inflation | 20 | 0.882 | 0.936 |
| National Overall | Inflation | 20 | 0.861 | 1.202 |
| LaPaz | Inflation | 20 | 0.783 | 1.216 |
| Cochabamba | Inflation | 20 | 0.829 | 1.022 |
| SantaCruz | Inflation | 20 | 0.782 | 1.332 |

## Lag regressions (official MoM inflation on lagged synthetic inflation)

| Dependent | Lag | Method | N | Slope | SE | p | Intercept |
|---|---|---|---|---|---|---|---|
| Core-5 | 0 | OLS | 20 | 0.776 | 0.098 | 0.0000 | 0.489 |
| Core-5 | 0 | OLS (HC1 SEs) | 20 | 0.776 | 0.096 | 0.0000 | 0.489 |
| Core-5 | 0 | Huber RLM | 20 | 0.825 | 0.100 | 0.0000 | 0.531 |
| Core-5 | 15 | OLS | 20 | 0.665 | 0.115 | 0.0000 | 0.575 |
| Core-5 | 15 | OLS (HC1 SEs) | 20 | 0.665 | 0.131 | 0.0000 | 0.575 |
| Core-5 | 15 | Huber RLM | 20 | 0.722 | 0.096 | 0.0000 | 0.573 |
| Core-5 | 20 | OLS | 20 | 0.635 | 0.149 | 0.0005 | 0.767 |
| Core-5 | 20 | OLS (HC1 SEs) | 20 | 0.635 | 0.213 | 0.0028 | 0.767 |
| Core-5 | 20 | Huber RLM | 20 | 0.754 | 0.143 | 0.0000 | 0.640 |
| Overall | 0 | OLS | 20 | 0.459 | 0.064 | 0.0000 | 0.660 |
| Overall | 0 | OLS (HC1 SEs) | 20 | 0.459 | 0.070 | 0.0000 | 0.660 |
| Overall | 0 | Huber RLM | 20 | 0.481 | 0.064 | 0.0000 | 0.692 |
| Overall | 15 | OLS | 20 | 0.397 | 0.071 | 0.0000 | 0.706 |
| Overall | 15 | OLS (HC1 SEs) | 20 | 0.397 | 0.088 | 0.0000 | 0.706 |
| Overall | 15 | Huber RLM | 20 | 0.435 | 0.062 | 0.0000 | 0.707 |
| Overall | 20 | OLS | 20 | 0.386 | 0.088 | 0.0004 | 0.815 |
| Overall | 20 | OLS (HC1 SEs) | 20 | 0.386 | 0.131 | 0.0031 | 0.815 |
| Overall | 20 | Huber RLM | 20 | 0.439 | 0.087 | 0.0000 | 0.773 |
