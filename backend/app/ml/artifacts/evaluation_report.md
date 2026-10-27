# AgriPrice AI: Time-Series Forecasting Evaluation Report

**Evaluation Strategy**: Chronological Train/Val/Test Split (Zero Future Data Leakage)  
**Trained Timestamp**: `2026-10-27T19:42:32.683192`  
**Test Observation Window**: `2026-03-30` to `2026-10-18` (29,000 unseen observations)

---

## 1. Overall Model vs Baseline Comparison

| Model | MAE (₹/Quintal) | RMSE (₹/Quintal) | R² Score | Performance vs Baseline |
| :--- | :---: | :---: | :---: | :--- |
| **Last-Observed-Price Baseline** (Naive Persistence) | ₹338.99 | ₹627.09 | — | Benchmark |
| **Random Forest Regressor** (Multi-horizon Pipeline) | **₹128.62** | **₹205.12** | **0.9966** | **62.06% error reduction** |

---

## 2. Multi-Horizon Breakdown (7-Day, 15-Day, 30-Day)

Forecasts are evaluated separately across multiple forward horizons to verify that uncertainty scales realistically:

| Horizon | Test Samples | Baseline MAE | Random Forest MAE | Random Forest RMSE | MAE Improvement | Evaluation Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **7 Days** | 10,200 | ₹204.82 | ₹119.69 | ₹193.41 | 41.56% | `RESPONSIBLY_EVALUATED` |
| **15 Days** | 9,800 | ₹315.59 | ₹128.73 | ₹203.58 | 59.21% | `RESPONSIBLY_EVALUATED` |
| **30 Days** | 9,000 | ₹516.54 | ₹138.63 | ₹219.19 | 73.16% | `RESPONSIBLY_EVALUATED` |

---

## 3. Per-Commodity Test Evaluation

| Commodity | Test Samples | Baseline MAE (₹/Qtl) | Random Forest MAE (₹/Qtl) | Improvement % |
| :--- | :---: | :---: | :---: | :--- |
| `banana` | 2900 | ₹178.12 | ₹82.68 | 53.58% |
| `bellary_onion` | 2900 | ₹197.32 | ₹98.98 | 49.84% |
| `coconut` | 2900 | ₹179.06 | ₹83.33 | 53.46% |
| `green_chilli` | 2900 | ₹563.72 | ₹174.84 | 68.98% |
| `paddy` | 2900 | ₹112.7 | ₹38.89 | 65.49% |
| `potato` | 2900 | ₹159.54 | ₹74.93 | 53.03% |
| `small_onion` | 2900 | ₹577.75 | ₹211.48 | 63.4% |
| `tapioca` | 2900 | ₹83.45 | ₹32.18 | 61.44% |
| `tomato` | 2900 | ₹469.01 | ₹121.31 | 74.13% |
| `turmeric` | 2900 | ₹869.25 | ₹367.59 | 57.71% |

---

## 4. Documented Assumptions & Limitations

1. **Information Origin Guarantee**: All lag prices, moving averages, and supply volumes are computed strictly using records available up to origin date $T$. No future data from $T+1$ onward was utilized in feature computation or preprocessing fits.
2. **Horizon Degradation**: Forecast uncertainty expands over extended horizons. 7-day forecasts exhibit the lowest variance; 15-day and 30-day horizons are provided with wider prediction intervals.
3. **Perishability Constraints**: Farmer sell/hold advisory accounts for biological storage constraints:
   - Perishable crops (Tomato, Banana, Tapioca) have maximum safe holding windows of 3 to 6 days.
   - Non-perishable commodities (Turmeric, Paddy, Copra) support longer strategic storage up to 60-180 days.
4. **Non-Financial Disclaimer**: Market predictions represent probabilistic statistical forecasts and must not be considered guaranteed financial returns.
