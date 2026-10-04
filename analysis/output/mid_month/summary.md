# Paper analysis: mid-month dating

- Tracker data through: 2026-10-04
- Latest official observation placed on: 2026-08-15
- Official series rebased to July 2024 = 100; synthetic inflation is a 30-day change.

## Correlation and mean absolute difference

| Region | Metric | N | Correlation | MAD |
|---|---|---|---|---|
| National | Index | 25 | 0.955 | 3.295 |
| National Overall | Index | 25 | 0.910 | 5.440 |
| LaPaz | Index | 25 | 0.915 | 4.606 |
| Cochabamba | Index | 25 | 0.962 | 2.435 |
| SantaCruz | Index | 25 | 0.975 | 2.547 |
| National | Inflation | 24 | 0.676 | 1.356 |
| National Overall | Inflation | 24 | 0.669 | 1.386 |
| LaPaz | Inflation | 24 | 0.369 | 2.083 |
| Cochabamba | Inflation | 24 | 0.624 | 1.559 |
| SantaCruz | Inflation | 24 | 0.792 | 1.177 |

## Lag regressions (official MoM inflation on lagged synthetic inflation)

| Dependent | Lag | Method | N | Slope | SE | p | Intercept |
|---|---|---|---|---|---|---|---|
| Core-5 | 0 | OLS | 24 | 0.699 | 0.163 | 0.0003 | 0.638 |
| Core-5 | 0 | OLS (HC1 SEs) | 24 | 0.699 | 0.161 | 0.0000 | 0.638 |
| Core-5 | 0 | Huber RLM | 24 | 0.745 | 0.123 | 0.0000 | 0.649 |
| Core-5 | 15 | OLS | 24 | 0.609 | 0.159 | 0.0009 | 0.730 |
| Core-5 | 15 | OLS (HC1 SEs) | 24 | 0.609 | 0.167 | 0.0003 | 0.730 |
| Core-5 | 15 | Huber RLM | 24 | 0.647 | 0.133 | 0.0000 | 0.741 |
| Core-5 | 20 | OLS | 23 | 0.615 | 0.181 | 0.0028 | 0.720 |
| Core-5 | 20 | OLS (HC1 SEs) | 23 | 0.615 | 0.224 | 0.0060 | 0.720 |
| Core-5 | 20 | Huber RLM | 23 | 0.700 | 0.158 | 0.0000 | 0.718 |
| Overall | 0 | OLS | 24 | 0.420 | 0.100 | 0.0003 | 0.723 |
| Overall | 0 | OLS (HC1 SEs) | 24 | 0.420 | 0.101 | 0.0000 | 0.723 |
| Overall | 0 | Huber RLM | 24 | 0.429 | 0.082 | 0.0000 | 0.760 |
| Overall | 15 | OLS | 24 | 0.367 | 0.097 | 0.0010 | 0.777 |
| Overall | 15 | OLS (HC1 SEs) | 24 | 0.367 | 0.108 | 0.0007 | 0.777 |
| Overall | 15 | Huber RLM | 24 | 0.373 | 0.091 | 0.0000 | 0.821 |
| Overall | 20 | OLS | 23 | 0.374 | 0.110 | 0.0027 | 0.779 |
| Overall | 20 | OLS (HC1 SEs) | 23 | 0.374 | 0.138 | 0.0069 | 0.779 |
| Overall | 20 | Huber RLM | 23 | 0.405 | 0.103 | 0.0001 | 0.822 |
