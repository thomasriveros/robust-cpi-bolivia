# Paper analysis: Core-4, mid-month dating

- Tracker data through: 2026-11-14
- Latest official observation placed on: 2026-10-15
- Official series rebased to July 2024 = 100; synthetic inflation is a 30-day change.

## Correlation and mean absolute difference

| Region | Metric | N | Correlation | MAD |
|---|---|---|---|---|
| National | Index | 27 | 0.962 | 4.761 |
| National Overall | Index | 27 | 0.918 | 4.712 |
| LaPaz | Index | 27 | 0.919 | 6.118 |
| Cochabamba | Index | 27 | 0.966 | 3.388 |
| SantaCruz | Index | 27 | 0.980 | 3.133 |
| National | Inflation | 26 | 0.664 | 1.416 |
| National Overall | Inflation | 26 | 0.700 | 1.243 |
| LaPaz | Inflation | 26 | 0.419 | 2.130 |
| Cochabamba | Inflation | 26 | 0.630 | 1.642 |
| SantaCruz | Inflation | 26 | 0.766 | 1.131 |

## Lag regressions (official MoM inflation on lagged synthetic inflation)

| Dependent | Lag | Method | N | Slope | SE | p | Intercept |
|---|---|---|---|---|---|---|---|
| Core-4 | 0 | OLS | 26 | 0.794 | 0.183 | 0.0002 | 0.611 |
| Core-4 | 0 | OLS (HC1 SEs) | 26 | 0.794 | 0.151 | 0.0000 | 0.611 |
| Core-4 | 0 | Huber RLM | 26 | 0.840 | 0.134 | 0.0000 | 0.681 |
| Core-4 | 15 | OLS | 26 | 0.677 | 0.190 | 0.0016 | 0.721 |
| Core-4 | 15 | OLS (HC1 SEs) | 26 | 0.677 | 0.209 | 0.0012 | 0.721 |
| Core-4 | 15 | Huber RLM | 26 | 0.713 | 0.164 | 0.0000 | 0.787 |
| Core-4 | 20 | OLS | 25 | 0.671 | 0.208 | 0.0038 | 0.724 |
| Core-4 | 20 | OLS (HC1 SEs) | 25 | 0.671 | 0.265 | 0.0115 | 0.724 |
| Core-4 | 20 | Huber RLM | 25 | 0.758 | 0.183 | 0.0000 | 0.782 |
| Overall | 0 | OLS | 26 | 0.464 | 0.097 | 0.0001 | 0.698 |
| Overall | 0 | OLS (HC1 SEs) | 26 | 0.464 | 0.085 | 0.0000 | 0.698 |
| Overall | 0 | Huber RLM | 26 | 0.457 | 0.084 | 0.0000 | 0.765 |
| Overall | 15 | OLS | 26 | 0.394 | 0.102 | 0.0008 | 0.764 |
| Overall | 15 | OLS (HC1 SEs) | 26 | 0.394 | 0.118 | 0.0009 | 0.764 |
| Overall | 15 | Huber RLM | 26 | 0.386 | 0.102 | 0.0002 | 0.834 |
| Overall | 20 | OLS | 25 | 0.396 | 0.112 | 0.0017 | 0.769 |
| Overall | 20 | OLS (HC1 SEs) | 25 | 0.396 | 0.147 | 0.0070 | 0.769 |
| Overall | 20 | Huber RLM | 25 | 0.404 | 0.111 | 0.0003 | 0.853 |
