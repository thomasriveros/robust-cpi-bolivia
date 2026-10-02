# Paper analysis: Core-4, mid-month dating

- Tracker data through: 2026-10-02
- Latest official observation placed on: 2026-08-15
- Official series rebased to July 2024 = 100; synthetic inflation is a 30-day change.

## Correlation and mean absolute difference

| Region | Metric | N | Correlation | MAD |
|---|---|---|---|---|
| National | Index | 25 | 0.967 | 4.231 |
| National Overall | Index | 25 | 0.932 | 4.827 |
| LaPaz | Index | 25 | 0.922 | 5.500 |
| Cochabamba | Index | 25 | 0.974 | 2.845 |
| SantaCruz | Index | 25 | 0.982 | 2.884 |
| National | Inflation | 24 | 0.668 | 1.437 |
| National Overall | Inflation | 24 | 0.707 | 1.279 |
| LaPaz | Inflation | 24 | 0.419 | 2.218 |
| Cochabamba | Inflation | 24 | 0.640 | 1.621 |
| SantaCruz | Inflation | 24 | 0.782 | 1.111 |

## Lag regressions (official MoM inflation on lagged synthetic inflation)

| Dependent | Lag | Method | N | Slope | SE | p | Intercept |
|---|---|---|---|---|---|---|---|
| Core-4 | 0 | OLS | 24 | 0.795 | 0.189 | 0.0004 | 0.553 |
| Core-4 | 0 | OLS (HC1 SEs) | 24 | 0.795 | 0.154 | 0.0000 | 0.553 |
| Core-4 | 0 | Huber RLM | 24 | 0.826 | 0.139 | 0.0000 | 0.602 |
| Core-4 | 15 | OLS | 24 | 0.683 | 0.196 | 0.0021 | 0.653 |
| Core-4 | 15 | OLS (HC1 SEs) | 24 | 0.683 | 0.210 | 0.0012 | 0.653 |
| Core-4 | 15 | Huber RLM | 24 | 0.729 | 0.164 | 0.0000 | 0.703 |
| Core-4 | 20 | OLS | 23 | 0.679 | 0.215 | 0.0047 | 0.659 |
| Core-4 | 20 | OLS (HC1 SEs) | 23 | 0.679 | 0.267 | 0.0108 | 0.659 |
| Core-4 | 20 | Huber RLM | 23 | 0.777 | 0.197 | 0.0001 | 0.707 |
| Overall | 0 | OLS | 24 | 0.465 | 0.099 | 0.0001 | 0.658 |
| Overall | 0 | OLS (HC1 SEs) | 24 | 0.465 | 0.086 | 0.0000 | 0.658 |
| Overall | 0 | Huber RLM | 24 | 0.461 | 0.085 | 0.0000 | 0.722 |
| Overall | 15 | OLS | 24 | 0.398 | 0.105 | 0.0010 | 0.718 |
| Overall | 15 | OLS (HC1 SEs) | 24 | 0.398 | 0.119 | 0.0008 | 0.718 |
| Overall | 15 | Huber RLM | 24 | 0.381 | 0.111 | 0.0006 | 0.791 |
| Overall | 20 | OLS | 23 | 0.401 | 0.114 | 0.0021 | 0.726 |
| Overall | 20 | OLS (HC1 SEs) | 23 | 0.401 | 0.147 | 0.0064 | 0.726 |
| Overall | 20 | Huber RLM | 23 | 0.412 | 0.114 | 0.0003 | 0.806 |
