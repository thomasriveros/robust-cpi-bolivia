# Paper analysis: mid-month dating

- Tracker data through: 2026-11-10
- Latest official observation placed on: 2026-10-15
- Official series rebased to July 2024 = 100; synthetic inflation is a 30-day change.

## Correlation and mean absolute difference

| Region | Metric | N | Correlation | MAD |
|---|---|---|---|---|
| National | Index | 27 | 0.948 | 3.839 |
| National Overall | Index | 27 | 0.895 | 5.326 |
| LaPaz | Index | 27 | 0.910 | 5.243 |
| Cochabamba | Index | 27 | 0.951 | 2.960 |
| SantaCruz | Index | 27 | 0.971 | 2.788 |
| National | Inflation | 26 | 0.672 | 1.319 |
| National Overall | Inflation | 26 | 0.663 | 1.329 |
| LaPaz | Inflation | 26 | 0.370 | 1.988 |
| Cochabamba | Inflation | 26 | 0.620 | 1.545 |
| SantaCruz | Inflation | 26 | 0.771 | 1.199 |

## Lag regressions (official MoM inflation on lagged synthetic inflation)

| Dependent | Lag | Method | N | Slope | SE | p | Intercept |
|---|---|---|---|---|---|---|---|
| Core-5 | 0 | OLS | 26 | 0.699 | 0.157 | 0.0002 | 0.676 |
| Core-5 | 0 | OLS (HC1 SEs) | 26 | 0.699 | 0.159 | 0.0000 | 0.676 |
| Core-5 | 0 | Huber RLM | 26 | 0.758 | 0.117 | 0.0000 | 0.694 |
| Core-5 | 15 | OLS | 26 | 0.607 | 0.153 | 0.0006 | 0.769 |
| Core-5 | 15 | OLS (HC1 SEs) | 26 | 0.607 | 0.166 | 0.0003 | 0.769 |
| Core-5 | 15 | Huber RLM | 26 | 0.636 | 0.126 | 0.0000 | 0.791 |
| Core-5 | 20 | OLS | 25 | 0.610 | 0.175 | 0.0020 | 0.757 |
| Core-5 | 20 | OLS (HC1 SEs) | 25 | 0.610 | 0.223 | 0.0062 | 0.757 |
| Core-5 | 20 | Huber RLM | 25 | 0.688 | 0.154 | 0.0000 | 0.763 |
| Overall | 0 | OLS | 26 | 0.420 | 0.097 | 0.0002 | 0.753 |
| Overall | 0 | OLS (HC1 SEs) | 26 | 0.420 | 0.100 | 0.0000 | 0.753 |
| Overall | 0 | Huber RLM | 26 | 0.424 | 0.082 | 0.0000 | 0.796 |
| Overall | 15 | OLS | 26 | 0.365 | 0.094 | 0.0007 | 0.808 |
| Overall | 15 | OLS (HC1 SEs) | 26 | 0.365 | 0.108 | 0.0007 | 0.808 |
| Overall | 15 | Huber RLM | 26 | 0.372 | 0.087 | 0.0000 | 0.855 |
| Overall | 20 | OLS | 25 | 0.370 | 0.107 | 0.0021 | 0.809 |
| Overall | 20 | OLS (HC1 SEs) | 25 | 0.370 | 0.138 | 0.0072 | 0.809 |
| Overall | 20 | Huber RLM | 25 | 0.402 | 0.096 | 0.0000 | 0.852 |
