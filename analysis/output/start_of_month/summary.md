# Paper analysis: start-of-month dating

- Tracker data through: 2026-10-08
- Latest official observation placed on: 2026-09-01
- Official series rebased to July 2024 = 100; synthetic inflation is a 30-day change.

## Correlation and mean absolute difference

| Region | Metric | N | Correlation | MAD |
|---|---|---|---|---|
| National | Index | 26 | 0.954 | 3.763 |
| National Overall | Index | 26 | 0.913 | 4.807 |
| LaPaz | Index | 26 | 0.923 | 5.205 |
| Cochabamba | Index | 26 | 0.951 | 3.158 |
| SantaCruz | Index | 26 | 0.971 | 2.828 |
| National | Inflation | 25 | 0.630 | 1.598 |
| National Overall | Inflation | 25 | 0.633 | 1.414 |
| LaPaz | Inflation | 25 | 0.426 | 2.142 |
| Cochabamba | Inflation | 25 | 0.490 | 1.880 |
| SantaCruz | Inflation | 25 | 0.733 | 1.399 |

## Lag regressions (official MoM inflation on lagged synthetic inflation)

| Dependent | Lag | Method | N | Slope | SE | p | Intercept |
|---|---|---|---|---|---|---|---|
| Core-5 | 0 | OLS | 25 | 0.590 | 0.152 | 0.0007 | 0.753 |
| Core-5 | 0 | OLS (HC1 SEs) | 25 | 0.590 | 0.158 | 0.0002 | 0.753 |
| Core-5 | 0 | Huber RLM | 25 | 0.606 | 0.134 | 0.0000 | 0.794 |
| Core-5 | 15 | OLS | 24 | 0.465 | 0.199 | 0.0287 | 0.830 |
| Core-5 | 15 | OLS (HC1 SEs) | 24 | 0.465 | 0.295 | 0.1151 | 0.830 |
| Core-5 | 15 | Huber RLM | 24 | 0.322 | 0.189 | 0.0886 | 0.892 |
| Core-5 | 20 | OLS | 24 | 0.403 | 0.199 | 0.0557 | 0.899 |
| Core-5 | 20 | OLS (HC1 SEs) | 24 | 0.403 | 0.276 | 0.1441 | 0.899 |
| Core-5 | 20 | Huber RLM | 24 | 0.252 | 0.169 | 0.1364 | 0.954 |
| Overall | 0 | OLS | 25 | 0.360 | 0.092 | 0.0007 | 0.786 |
| Overall | 0 | OLS (HC1 SEs) | 25 | 0.360 | 0.103 | 0.0005 | 0.786 |
| Overall | 0 | Huber RLM | 25 | 0.390 | 0.072 | 0.0000 | 0.821 |
| Overall | 15 | OLS | 24 | 0.280 | 0.121 | 0.0300 | 0.846 |
| Overall | 15 | OLS (HC1 SEs) | 24 | 0.280 | 0.179 | 0.1169 | 0.846 |
| Overall | 15 | Huber RLM | 24 | 0.162 | 0.094 | 0.0837 | 0.911 |
| Overall | 20 | OLS | 24 | 0.244 | 0.121 | 0.0566 | 0.887 |
| Overall | 20 | OLS (HC1 SEs) | 24 | 0.244 | 0.167 | 0.1446 | 0.887 |
| Overall | 20 | Huber RLM | 24 | 0.138 | 0.095 | 0.1482 | 0.941 |
