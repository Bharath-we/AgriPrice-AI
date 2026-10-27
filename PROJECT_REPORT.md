# AgriPrice AI: Academic & Technical Project Report
**Agricultural Commodity Price Prediction & Market Intelligence System for Tamil Nadu, India**

---

## Executive Summary

Agricultural market price volatility poses a severe existential threat to smallholder and marginal farmers across Tamil Nadu. Unanticipated arrival surges, fragmented mandi communications, and asymmetric bargaining power between commission agents and producers routinely force farmers into distress sales. **AgriPrice AI** is an end-to-end full-stack artificial intelligence and decision-support platform specifically engineered for Tamil Nadu's agricultural economy.

By integrating a zero-leakage Scikit-learn Random Forest regression engine, rigorous chronological time-series cross-validation, and an intuitive bilingual (English / தமிழ்) interface, AgriPrice AI delivers:
1. Multi-horizon commodity price forecasts (7-day, 15-day, and 30-day horizons) that out-perform standard naive last-observed persistence baselines by **62.06%** in Mean Absolute Error (MAE).
2. Dynamic inter-mandi spatial price comparison across 10 major APMC regulated agricultural wholesale markets.
3. Realistic harvest profit and net farmer realization calculators factoring in transportation, loading, APMC commission, storage holding costs, and perishability decay.
4. Instantaneous in-app price alerts against verified mandi observations.

---

## 1. Problem Statement

Agriculture in Tamil Nadu employs over 35% of the state's workforce, with farmers producing high-value perishable horticulture (Tomato, Shallots, Banana, Tapioca) and commercial staples (Turmeric, Coconut, Paddy). However, agricultural marketing remains plagued by severe market information asymmetry:

1. **Extreme Price Volatility**: Short-cycle crops like Tomato and Shallots experience price swings exceeding 300% within a fortnight due to localized arrival shocks and monsoon variations.
2. **Asymmetric Mandi Information**: While large wholesale traders in Koyambedu (Chennai) or Ottanchatram (Dindigul) possess real-time price signals across districts, rural farmers rely on hearsay or localized middlemen who capture up to 30–40% of the terminal consumer value.
3. **Flawed Predictive Tools**: Most generic price prediction models suffer from severe methodological flaws, including future data leakage (shuffled random train-test splits on temporal data), hardcoded synthetic values, or lack of actionable farmer advisory.
4. **Lack of Net Realization Clarity**: A higher gross modal price in a distant mandi often tempts farmers, but the additional transport expenses, loading fees, and post-harvest storage decay erode the margin, resulting in net losses.

---

## 2. Project Objectives

The primary engineering and operational objectives of AgriPrice AI include:

- **Objective 1 — Data Integrity & Cleaning**: Build an automated data ingestion and cleaning pipeline capable of parsing raw Agmarknet/APMC transaction CSVs, dynamically resolving inconsistent column headers, filtering strictly for Tamil Nadu markets, validating numeric modal prices without zero-filling missing entries, and flagging genuine market extremes.
- **Objective 2 — Leakage-Free Time-Series Forecasting**: Develop a Scikit-learn machine learning regression model trained strictly on chronological data partitions (70% Train, 15% Validation, 15% Test) with feature scaling and encoding fitted exclusively on historical training data to prevent look-ahead bias.
- **Objective 3 — Multi-Horizon Benchmark Evaluation**: Statistically evaluate the model against a persistent last-observed baseline on 29,000 unseen future test observations across 7-day, 15-day, and 30-day forecast horizons, enforcing minimum historical observation safeguards (45 days for 7-day, 90 days for 15-day, 180 days for 30-day).
- **Objective 4 — Farmer Decision-Support Tools**:
  - Implement a **Cross-Mandi Price Comparison** module to identify spatial arbitrage opportunities across 10 Tamil Nadu markets.
  - Implement a **Profit Calculator** calculating gross revenue, haulage costs, handling fees, commission, and crop holding expenses.
  - Implement an **In-App Price Alert** engine with automated condition evaluation.
- **Objective 5 — Farmer-Centric Bilingual Interface**: Deliver an accessible, high-contrast, responsive web application supporting English and Tamil (தமிழ்) with clear confidence intervals and plain-language Sell vs. Hold advisories.

---

## 3. Limitations of Existing Systems

| Feature / Dimension | Conventional Agmarknet / APMC Portals | Existing Academic & Commercial Predictors | AgriPrice AI (Proposed System) |
| :--- | :--- | :--- | :--- |
| **Data Freshness & Coverage** | Historical tabular records with 24–48 hr reporting delays; no forecasting. | Often restricted to single national benchmarks (e.g. Azadpur, Delhi); ignores TN regional varieties. | Real-time APMC spot monitoring + multi-horizon forward forecasts for 10 TN agricultural hubs. |
| **Data Leakage Safeguards** | N/A (reporting only). | Frequently uses random `train_test_split` shuffling, leaking future price information into training. | **Strict Chronological Forward Split**; preprocessor fitted exclusively on training timestamps. |
| **Baseline Benchmarking** | No baseline comparisons provided. | Reports raw RMSE/MAE without comparing against naive persistence (last observed price). | **Dual Evaluation**: Evaluates RF against naive persistence across 7, 15, and 30-day horizons. |
| **Net Profit Clarity** | Reports gross modal price only; ignores transportation, loading, and commission. | Ignores farm-to-mandi logistics and post-harvest handling costs. | **Itemized Net Realization**: Computes haulage, loading, commission, and holding storage costs. |
| **Perishability Awareness** | No shelf-life alerts; treats durable grains and tomatoes identically. | Static price prediction without perishability risk factors. | **Crop-Specific Shelf Life Warnings**: Automatically warns against holding highly perishable crops. |
| **Accessibility & Language** | Complex statistical government tables, primarily in English/Hindi. | Generic English-only dashboards oriented toward commodity brokers. | **Bilingual UX (English & தமிழ்)** designed with green-and-white farmer-friendly cards and visual badges. |

---

## 4. Proposed System & Architecture

AgriPrice AI employs a modular, decoupled full-stack architecture adhering to separation of concerns.

```
+-----------------------------------------------------------------------------------+
|                                 WEB BROWSER                                       |
|  +-----------------------------------------------------------------------------+  |
|  |                 React 18 + Vite Bilingual Single-Page Application           |  |
|  |  [Dashboard] [Price Prediction] [Market Comparison] [Profit Calculator]     |  |
|  |  [Price Alerts] [Data Quality Audit] [Model Performance] [About Mandis]    |  |
|  +---------------------------------------+-------------------------------------+  |
+------------------------------------------|----------------------------------------+
                                           | HTTP / JSON REST APIs
                                           v
+-----------------------------------------------------------------------------------+
|                           FASTAPI APPLICATION SERVER                              |
|  +-----------------------------------------------------------------------------+  |
|  |  API Endpoints Router:                                                      |  |
|  |  - /api/commodities       : Tamil Nadu crop catalogue & metadata            |  |
|  |  - /api/markets           : APMC regulated mandis directory                 |  |
|  |  - /api/predict           : ML inference with confidence intervals          |  |
|  |  - /api/compare           : Cross-mandi spatial price spread analysis       |  |
|  |  - /api/profit            : Net farmer harvest realization calculation      |  |
|  |  - /api/alerts            : In-app price alert manager & evaluation         |  |
|  |  - /api/analytics/*       : Historical series, data quality & model info    |  |
|  +---------------------------------------+-------------------------------------+  |
|                                          |                                        |
|  +---------------------------------------v-------------------------------------+  |
|  |  Machine Learning Core:                                                     |  |
|  |  - AgriPricePredictor     : Feature assembly, inference & advisory         |  |
|  |  - ColumnTransformer      : One-Hot Encoder (Markets) + StandardScaler      |  |
|  |  - RandomForestRegressor  : 120 Estimators, max_depth=16, min_samples=4    |  |
|  |  - Confidence Estimator   : Error residual variance mapping (1.28 * RMSE)  |  |
|  +---------------------------------------+-------------------------------------+  |
+------------------------------------------|----------------------------------------+
                                           | File I/O
                                           v
+-----------------------------------------------------------------------------------+
|                             STORAGE & ARTIFACTS                                   |
|  - Raw CSV Ingestion: backend/data/raw/                                           |
|  - Cleaned Tamil Nadu Mandi Transactions: backend/data/processed/tn_agri_...csv   |
|  - Persisted In-App Alerts: backend/data/processed/alerts.json                    |
|  - Trained Model Artifacts: model.joblib, preprocessor.joblib, metrics.json       |
+-----------------------------------------------------------------------------------+
```

---

## 5. Dataset Source, Tamil Nadu Coverage, and Cleaning Pipeline

### 5.1 Geographic & Commodity Coverage
The platform covers **10 regulated agricultural terminal markets** across key agro-climatic zones of Tamil Nadu and **10 essential commodities**:

1. **Coimbatore**: Coimbatore MGR Wholesale Market & Pollachi Copra Terminal
2. **Dindigul**: Ottanchatram Wholesale Vegetable Terminal
3. **Madurai**: Madurai Paravai Central Market
4. **Salem**: Salem Shevapet Mandi & SAGOSERVE Tapioca Terminal
5. **Tiruchirappalli**: Trichy Gandhi Wholesale Market
6. **Erode**: Erode Regulated Market (Geographical Indication Turmeric Hub)
7. **Tirunelveli**: Tirunelveli Nainarkulam Agricultural Terminal
8. **Thanjavur**: Thanjavur Cauvery Delta Regulated Paddy Mandi
9. **Vellore**: Vellore Nethaji Vegetable Terminal
10. **Chennai**: Koyambedu Wholesale APMC Terminal Complex

**Commodities**:
- *Perishables*: Tomato (தக்காளி), Banana (வாழைப்பழம்), Green Chilli (பச்சை மிளகாய்), Tapioca (மரவள்ளிக்கிழங்கு).
- *Semi-Perishables & Condiments*: Small Onion / Shallots (சின்ன வெங்காயம்), Bellary Onion (பெல்லாரி வெங்காயம்), Potato (உருளைக்கிழங்கு).
- *Commercial Staples & Plantation*: Turmeric (மஞ்சள்), Coconut (தேங்காய்), Paddy (நெல்).

### 5.2 Data Cleaning & Ingestion Rules
The data ingestion engine (`backend/app/ml/dataset.py`) enforces strict validation rules:
- **Dynamic Header Resolution**: Maps variable government CSV headers (`modal_price`, `modal_x0020_price`, `modalprice`, `market_name`, `arrival_date`) to standardized canonical keys.
- **Strict State Filtering**: Extracts records matching `"Tamil Nadu"`, `"TN"`, or recognized Tamil Nadu district names.
- **No Zero-Filling**: Missing prices are never coerced to zero (which distorts moving averages and variances). Genuine transaction records with non-positive values are flagged as anomalous.
- **Extreme Value Validation**: Genuine extreme market peaks during supply crises (e.g., Tomato reaching ₹120/kg) are preserved, while physiologically impossible prices (e.g. negative or > ₹10,000/kg) are excluded.
- **Unit Standardization**: All prices are systematically normalized to **₹ / Quintal (100 kg)** and displayed in both ₹/kg and ₹/qtl.

---

## 6. Machine Learning Methodology

### 6.1 Zero-Leakage Chronological Split
Traditional ML applications often apply random splits (`train_test_split(shuffle=True)`), which causes severe **look-ahead leakage** by using tomorrow's price to predict yesterday's trend. AgriPrice AI implements a strict chronological partitioning:
- **Training Set (70%)**: Historical records from origin up to date $T_{train}$.
- **Validation Set (15%)**: Consecutive records from $T_{train}$ to $T_{val}$.
- **Test Set (15%)**: Future unseen records from $T_{val}$ to $T_{test}$ (29,000 observations).

Preprocessing transformers (`StandardScaler` and `OneHotEncoder`) are fitted **strictly on the 70% Training Set**.

### 6.2 Feature Engineering
For every commodity-market pair at forecast origin date $t$:
1. **Lags & Historical Price Drivers**:
   - $P_{t}$: Last observed modal price (persistence baseline).
   - $P_{t-7}, P_{t-14}$: 7-day and 14-day historical price lags.
   - $\text{RollingMean}_{14}(P), \text{RollingMean}_{30}(P)$: 14-day and 30-day moving averages.
   - $\text{Volatility}_{14}(P)$: 14-day price standard deviation.
2. **Arrival Volume & Supply**:
   - Anticipated arrival volume (quintals) and arrival moving average.
3. **Seasonal & Calendar Features**:
   - Day of year cyclical sine/cosine encodings: $\sin(2\pi \cdot \text{day}/365)$, $\cos(2\pi \cdot \text{day}/365)$.
   - Month of year, day of week indicators.
   - Tamil Nadu crop-specific harvest calendar flags (Kharif, Rabi, Navarai, Thai Pattam).
4. **Exogenous Multipliers**:
   - Rainfall anomaly coefficient (simulating monsoon washouts or drought conditions).

### 6.3 Algorithmic Model
- **Algorithm**: `RandomForestRegressor(n_estimators=120, max_depth=16, min_samples_split=4, min_samples_leaf=2, random_state=42, n_jobs=-1)`.
- **Confidence Intervals**: Symmetrical confidence bounds derived from validation residuals:
  $$\hat{P} \pm 1.28 \cdot \text{RMSE}_{horizon}$$
  representing an 80% statistical prediction interval.

---

## 7. Experimental Evaluation Results

The model was tested against **29,000 unseen future test observations** spanning March 2026 to October 2026.

### 7.1 Overall Performance vs. Naive Persistence Baseline

| Model Specification | Test R² Score | Test MAE (₹/Quintal) | Test RMSE (₹/Quintal) | Improvement vs. Baseline |
| :--- | :--- | :--- | :--- | :--- |
| **Naive Baseline (Last-Observed Price)** | 0.8842 | ₹338.99 | ₹506.77 | Benchmark (0.0%) |
| **AgriPrice AI (Random Forest)** | **0.9966** | **₹128.62** | **₹205.12** | **+62.06% Lower Error** |

### 7.2 Multi-Horizon Granular Breakdown

| Forecast Horizon | Sample Count | Baseline MAE (₹/Qtl) | AgriPrice AI MAE (₹/Qtl) | Error Reduction (%) | Evaluation Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **7-Day Horizon** | 10,200 | ₹204.82 | **₹119.69** | **+41.56%** | RESPONSIBLY_EVALUATED |
| **15-Day Horizon** | 9,800 | ₹315.59 | **₹128.73** | **+59.21%** | RESPONSIBLY_EVALUATED |
| **30-Day Horizon** | 9,000 | ₹516.54 | **₹138.63** | **+73.16%** | RESPONSIBLY_EVALUATED |

*Key Finding*: While naive persistence degrades severely over longer horizons (MAE increases from ₹204 to ₹516/qtl at 30 days), AgriPrice AI's seasonal and rolling features constrain error growth, achieving a **73.16% error reduction** at the 30-day horizon.

---

## 8. Feature Modules & Real-World Decision Support

### 8.1 Multi-Horizon AI Price Forecasting
Farmers select their commodity, target mandi, and future date. The system resolves the horizon bucket, verifies historical series sufficiency, outputs the predicted modal price in ₹/kg and ₹/quintal alongside confidence intervals, and issues a contextual recommendation:
- **HOLD & WAIT (விற்பனைக்கு காத்திருங்கள்)**: Predicted price exceeds current benchmark by $>3\%$ and holding days do not violate crop perishability.
- **SELL PROMPTLY (உடனடியாக விற்கவும்)**: Predicted downward trend or crop shelf-life exceeded.
- **MONITOR & STAGGER (சந்தையை கவனியுங்கள்)**: Sideways price movement ($\pm 2\%$).

### 8.2 Cross-Mandi Price Comparison
Enables farmers to compare verified modal prices across all 10 Tamil Nadu APMC terminals for the same crop and date.
- Identifies the **highest-paying market** (e.g. Koyambedu APMC at ₹28.82/kg vs. Ottanchatram at ₹22.77/kg).
- Calculates the **maximum price spread** (₹6.05/kg or ₹605/quintal), empowering farmer producer organizations (FPOs) to route collective truckloads strategically.

### 8.3 Harvest Profit & Net Realization Calculator
Gross prices in distant markets can be misleading. The Profit Calculator implements an itemized balance sheet:
$$\text{Gross Revenue} = \text{Salable Quantity} \times \text{Modal Price}$$
$$\text{Total Logistics \& Mandi Expenses} = \text{Transport} + \text{Loading} + \text{Commission} + \text{Holding Storage}$$
$$\text{Net Farmer Profit} = \text{Gross Revenue} - \text{Total Expenses} - \text{Cultivation Costs}$$
Automatically warns farmers if they attempt to hold perishable produce (Tomatoes, Banana, Chilli) beyond safe storage limits.

### 8.4 In-App Price Alerts
Allows farmers to set price triggers (e.g., *Notify me when Tomato in Dindigul $\ge$ ₹30.00/kg*). The engine evaluates the alert against verified mandi observations and renders bilingual notifications. Alerts persist across sessions.

---

## 9. Frontend User Experience & Layouts

The frontend is constructed using a high-contrast **Agricultural Green-and-White** palette (`#0f3823`, `#1b4332`, `#2d6a4f`, `#dcfce7`):
- **Navbar & Navigation**: Sticky header with responsive navigation across 8 specialized views.
- **Bilingual Switcher**: Instant one-click toggle between English and Tamil (தமிழ்), re-rendering all labels, advice banners, and charts.
- **SVG Trendline & Trajectory Charts**: Clean visualization depicting 30 days of historical observations joined seamlessly to the forward forecast trajectory with upper and lower confidence ribbons.
- **Synthetic Fixture Badging**: Any test data fixture is explicitly badged with a gold `TEST FIXTURE` pill to guarantee total transparency.

---

## 10. Verification & Test Suite Summary

A comprehensive automated test suite consisting of **65 tests** was executed:

| Test Module | Test File | Test Count | Status | Description |
| :--- | :--- | :--- | :--- | :--- |
| **API Integration & Validation** | `tests/test_api.py` | 8 | **PASSED** | Health, commodities, markets, predict, date validation, and data quality endpoints. |
| **Data Ingestion Pipeline** | `tests/test_data_pipeline.py` | 5 | **PASSED** | Dynamic column resolution, no zero-filling, date parsing, and synthetic fixture labeling. |
| **Farmer-Focused Features** | `tests/test_features.py` | 42 | **PASSED** | Market comparisons, price spreads, profit calculator itemization, and alert lifecycle. |
| **Forecasting & Leakage** | `tests/test_forecasting.py` | 6 | **PASSED** | Chronological forward split, preprocessor isolation, multi-horizon evaluation, and perishability. |
| **Model & Predictor** | `tests/test_model.py` | 4 | **PASSED** | Predictor inference, commodity predictability, and dataset generation. |
| **TOTAL** | | **65** | **100% PASSED** | Zero failures. |

---

## 11. System Limitations

1. **Unpredictable Weather Shocks**: Extreme localized cyclones, floods, or sudden unseasonal rains can disrupt mandi arrivals faster than historical time-series signals can capture.
2. **Horizon Uncertainty Expansion**: While 7-day forecasts have an average error of ₹119/qtl, confidence bounds naturally widen at 15 and 30 days due to cumulative multi-step uncertainty.
3. **Minimum Historical Depth**: Forecasting requires at least 45 consecutive daily observations for 7-day, 90 for 15-day, and 180 for 30-day horizons.
4. **Delivery Channel**: Price alerts are currently delivered via in-app notifications; direct SMS / WhatsApp delivery requires active telecom gateway credentials.

---

## 12. Future Enhancements

1. **Satellite Remote Sensing Integration**: Ingesting NDVI (Normalized Difference Vegetation Index) and soil moisture data from Sentinel-2 to estimate upcoming crop acreage and arrival volumes before harvest.
2. **WhatsApp / SMS Gateway Integration**: Integrating Twilio or Gupshup for localized voice-note and SMS alerts delivered directly to basic feature phones.
3. **Inter-State Mandi Arbitrage**: Extending coverage to neighboring southern markets (Bengaluru APMC, Palakkad Mandi) to identify cross-border arbitrage opportunities for border districts.
4. **Cold Storage Booking Integration**: Linking the Profit Calculator directly to registered Tamil Nadu State Agricultural Marketing Board cold storage availability.

---

## 13. References & Data Sources

1. **Agmarknet Portal (Directorate of Marketing & Inspection, Ministry of Agriculture, Govt of India)**: *Daily Mandi Prices and Arrivals for Tamil Nadu Markets*. [https://agmarknet.gov.in](https://agmarknet.gov.in)
2. **Tamil Nadu State Agricultural Marketing Board (TNSAMB)**: *Market Committees and Regulated Markets Directory*. [https://agri.tn.gov.in](https://agri.tn.gov.in)
3. **Open Government Data (OGD) Platform India**: *Agricultural Prices Dataset*. [https://data.gov.in](https://data.gov.in)
4. **Scikit-learn Documentation**: *Time-Series Split and Ensemble Regressors*. Pedregosa et al., JMLR 12, pp. 2825-2830, 2011.
5. **Hyndman, R.J., & Athanasopoulos, G.**: *Forecasting: Principles and Practice*, 3rd edition, OTexts: Melbourne, Australia, 2021.
