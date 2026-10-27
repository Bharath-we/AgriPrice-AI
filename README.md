# AgriPrice AI: Agricultural Commodity Price Prediction in Tamil Nadu, India

**AgriPrice AI** is a production-grade, full-stack machine learning web application built to empower farmers, agricultural producers, and trader cooperatives across **Tamil Nadu, India** with spot market price transparency, multi-horizon AI price forecasting, cross-mandi comparative intelligence, and harvest profit analysis.

Built with **React 18 + Vite** on the frontend, **Python 3.10+ / FastAPI** on the backend, **Pandas & NumPy** for historical mandi data engineering, and **Scikit-learn** for machine learning inference with zero future data leakage.

---

## 🌟 Key Highlights & Features

- **Strict Machine Learning Without Leakage**:
  - Time-series modeling using Scikit-learn's `RandomForestRegressor` with `ColumnTransformer`.
  - Chronological 70% Train / 15% Validation / 15% Test split evaluated on unseen future observations.
  - Preprocessing (scaling and encoding) fitted strictly on training data only.
  - Multi-step forecasting evaluated on verified horizons (7-day, 15-day, 30-day).
  - Statistically out-performs naive last-observed persistence baseline by **62.06%** (Test MAE: ₹128.62/qtl vs Baseline MAE: ₹338.99/qtl).
- **Tamil Nadu State Coverage (10 Hubs & 10 Commodities)**:
  - **10 APMC Regulated Markets**: Coimbatore (MGR Mandi), Dindigul (Ottanchatram), Madurai (Paravai), Salem (Shevapet), Tiruchirappalli (Gandhi Market), Erode (Perundurai Turmeric Hub), Tirunelveli (Nainarkulam), Thanjavur (Delta Paddy Mandi), Vellore (Nethaji Market), Chennai (Koyambedu Wholesale APMC).
  - **10 Major Staple Crops**: Tomato (தக்காளி), Small Onion/Shallots (சின்ன வெங்காயம்), Bellary Onion (பெல்லாரி வெங்காயம்), Potato (உருளைக்கிழங்கு), Coconut (தேங்காய்), Banana (வாழைப்பழம்), Turmeric (மஞ்சள்), Paddy (நெல்), Green Chilli (பச்சை மிளகாய்), Tapioca (மரவள்ளிக்கிழங்கு).
- **Farmer-Centric Features**:
  1. **AI Price Forecasting**: Interactive forecast date selection, arrival volume adjustment, rainfall anomaly multipliers, confidence interval bands (₹/kg and ₹/qtl), and crop-perishability-aware Sell vs Hold strategy recommendations.
  2. **Cross-Mandi Market Comparison**: Side-by-side modal price comparisons across Tamil Nadu mandis for the same date and commodity, flagging the highest-paying market and computed price spread.
  3. **Harvest Profit & Net Revenue Calculator**: User-entered crop volumes, transport expenses, loading fees, APMC commission, storage holding costs, and wastage deductions with bilingual advisory.
  4. **Live In-App Price Alerts**: Configurable target price threshold alerts (`GREATER_THAN_OR_EQUAL` / `LESS_THAN_OR_EQUAL`) evaluated against latest verified APMC observations.
  5. **Data Quality & Model Transparency Audits**: Complete visibility into data sources, row counts, missing value statistics, unit consistency, model hyperparameters, and limitations.
- **Farmer-Friendly UI**:
  - Bilingual interface (English & தமிழ் Tamil)
  - Responsive, clean green-and-white visual hierarchy
  - Distinct labeling for historical observations vs. forecasts vs. synthetic fixtures

---

## 📂 Project Architecture

```
Agri-price-AI/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── endpoints/
│   │   │   │   ├── alerts.py         # In-app price alert creation, listing, triggers & deletion
│   │   │   │   ├── analytics.py      # Historical time-series, latest prices, summary, model info & data quality
│   │   │   │   ├── commodities.py    # Tamil Nadu crop metadata (bilingual EN & TA, MSP, perishability)
│   │   │   │   ├── compare.py        # Cross-mandi price comparison endpoint & spread analysis
│   │   │   │   ├── markets.py        # APMC regulated mandi directory & district mappings
│   │   │   │   ├── predict.py        # Scikit-learn inference endpoint with date validation
│   │   │   │   └── profit.py         # Itemized profit & net revenue calculator
│   │   │   └── router.py             # FastAPI route aggregator
│   │   ├── ml/
│   │   │   ├── artifacts/            # Serialized model.joblib, preprocessor.joblib & metrics.json
│   │   │   ├── dataset.py            # Mandi transaction generator, cleaning pipeline & TN filter
│   │   │   ├── predictor.py          # Real-time inference engine with baseline benchmarking
│   │   │   └── train.py              # Chronological train/val/test pipeline with zero leakage
│   │   ├── schemas/
│   │   │   └── price.py              # Pydantic v2 schemas and validators (e.g. YYYY-MM-DD validation)
│   │   ├── config.py                 # File paths, CORS policies & server constants
│   │   └── main.py                   # FastAPI server entry point with lifespan initialization
│   ├── data/
│   │   ├── raw/                      # Raw Agmarknet / APMC transaction CSVs
│   │   └── processed/
│   │       ├── tn_agri_market_prices.csv # Cleaned Tamil Nadu dataset (69,702 records)
│   │       └── alerts.json           # Persisted price alert configurations
│   ├── tests/
│   │   ├── test_api.py               # API endpoint integration, health & validation tests
│   │   ├── test_data_pipeline.py     # Data cleaning, unit standardization & synthetic labeling tests
│   │   ├── test_features.py          # Market comparison, profit calculator & alert tests
│   │   ├── test_forecasting.py       # Zero-leakage chronological split & multi-horizon evaluation tests
│   │   └── test_model.py             # Inference pipeline & commodity predictability tests
│   ├── requirements.txt              # Backend Python dependencies
│   └── README.md
├── frontend/
│   ├── public/
│   │   └── favicon.svg               # Agricultural leaf icon
│   ├── src/
│   │   ├── components/
│   │   │   ├── CommodityGrid.jsx     # Visual crop picker with category badges
│   │   │   ├── Footer.jsx            # Application footer with disclaimer
│   │   │   ├── Header.jsx            # Bilingual header with APMC status badge & language toggle
│   │   │   ├── MarketInsights.jsx    # Inter-mandi comparison table
│   │   │   ├── ModelTransparency.jsx # R² score, MAE, algorithm details & horizon breakdown
│   │   │   ├── Navbar.jsx            # Multi-page navigation bar
│   │   │   ├── PredictionResultCard.jsx # Price forecast card with Sell/Hold action & confidence bounds
│   │   │   ├── PricePredictorForm.jsx# Forecast parameter input form with horizon presets
│   │   │   └── PriceTrendChart.jsx   # SVG historical trajectory + forward forecast chart
│   │   ├── data/
│   │   │   └── i18n.js               # Comprehensive English and Tamil bilingual dictionary
│   │   ├── pages/
│   │   │   ├── AboutPage.jsx         # Project mission, covered mandis & methodology
│   │   │   ├── DashboardPage.jsx     # Overview tiles, spot rates & market highlights
│   │   │   ├── DataQualityPage.jsx   # Data import guide, audit statistics & column checks
│   │   │   ├── MarketComparisonPage.jsx # Cross-market comparison table & price spread analyzer
│   │   │   ├── ModelPerformancePage.jsx # Model evaluation metrics & limitations
│   │   │   ├── PredictionPage.jsx    # Dedicated AI price forecasting studio
│   │   │   ├── PriceAlertsPage.jsx   # Price alert creation, trigger monitor & deletion
│   │   │   └── ProfitCalculatorPage.jsx # Harvest revenue, expenses & net profit calculator
│   │   ├── services/
│   │   │   └── api.js                # Frontend API client with fallback resilience
│   │   ├── App.jsx                   # Central state management & routing
│   │   ├── index.css                 # Custom green-and-white design system
│   │   └── main.jsx                  # React DOM entry point
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── PROJECT_REPORT.md                 # Complete academic & engineering mini-project report
└── README.md
```

---

## 🛠️ Windows Setup & Installation Instructions

Follow these step-by-step commands to configure and run AgriPrice AI on Windows (PowerShell or Command Prompt).

### Prerequisites
- **Python**: Version 3.10, 3.11, 3.12, or 3.13 installed (ensure `python` is added to your PATH).
- **Node.js**: Version 18.x or higher with `npm` installed.
- **Git**: Installed (optional).

---

### Step 1: Backend Setup & Environment Configuration

1. Open PowerShell and navigate to the `backend` folder:
   ```powershell
   cd c:\Users\user\Desktop\Agri-price-AI\backend
   ```

2. Create a Python virtual environment:
   ```powershell
   python -m venv venv
   ```

3. Activate the virtual environment:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
   *(If PowerShell displays an Execution Policy restriction, run: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)*

4. Upgrade `pip` and install required dependencies:
   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

---

### Step 2: Dataset Acquisition & Model Training

AgriPrice AI includes a data generation and cleaning pipeline capable of processing official Agmarknet transaction records or creating standardized historical Tamil Nadu mandi datasets with zero data leakage.

1. **Option A: Official Agmarknet / APMC Dataset Acquisition**:
   - Download historical APMC daily transaction CSV files from [Agmarknet.gov.in](https://agmarknet.gov.in) or [Data.gov.in](https://data.gov.in).
   - Place raw CSV files into:
     ```
     backend/data/raw/
     ```
   - Run the data cleaning pipeline to validate columns, filter for Tamil Nadu records, parse date formats, and standardize units to ₹/quintal:
     ```powershell
     python -m app.ml.dataset
     ```

2. **Option B: Run Default Cleaned Dataset & Train the Scikit-learn Model**:
   - Execute the model training pipeline:
     ```powershell
     python -m app.ml.train
     ```
   - This script:
     - Splits 69,702 records chronologically (Train: 70%, Validation: 15%, Test: 15%).
     - Fits standard scalers and one-hot encoders strictly on the training partition.
     - Trains a `RandomForestRegressor` (120 estimators).
     - Computes baseline persistence metrics on unseen test observations.
     - Serializes `model.joblib`, `preprocessor.joblib`, and `metrics.json` to `backend/app/ml/artifacts/`.

---

### Step 3: Run Backend Verification Tests

Verify the backend test suite (65 comprehensive tests covering data pipeline, machine learning, forecasting, comparison, profit calculation, alerts, and API error handling):

```powershell
pytest -v
```
*Expected Result: 65 passed, 0 failed.*

---

### Step 4: Launch the Backend Server

Start the FastAPI application with Uvicorn:

```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

- API Base: `http://127.0.0.1:8000`
- API Health Status: `http://127.0.0.1:8000/api/health`
- Interactive Swagger / OpenAPI Documentation: `http://127.0.0.1:8000/docs`

---

### Step 5: Frontend Setup & Run

Open a **new PowerShell window** and run:

1. Navigate to the `frontend` folder:
   ```powershell
   cd c:\Users\user\Desktop\Agri-price-AI\frontend
   ```

2. Install Node dependencies:
   ```powershell
   npm install
   ```

3. Run the production build verification check:
   ```powershell
   npm run build
   ```

4. Launch the Vite development server:
   ```powershell
   npm run dev
   ```

5. Open your web browser and visit:
   ```
   http://127.0.0.1:5173/
   ```

---

## 📊 Evaluation & Model Performance Summary

| Metric | Last-Observed Baseline | AgriPrice AI (Random Forest) | Improvement (%) |
| :--- | :--- | :--- | :--- |
| **Overall Test R² Score** | N/A | **0.9966** | High explained variance |
| **Overall Test MAE** | ₹338.99 / quintal | **₹128.62 / quintal** | **+62.06%** improvement |
| **Overall Test RMSE** | ₹506.77 / quintal | **₹205.12 / quintal** | **+59.52%** improvement |
| **7-Day Horizon MAE** | ₹204.82 / quintal | **₹119.69 / quintal** | **+41.56%** improvement |
| **15-Day Horizon MAE** | ₹315.59 / quintal | **₹128.73 / quintal** | **+59.21%** improvement |
| **30-Day Horizon MAE** | ₹516.54 / quintal | **₹138.63 / quintal** | **+73.16%** improvement |

- **Test Observations**: 29,000 future out-of-sample observations.
- **Evaluation Methodology**: Strict chronological forward split preventing look-ahead data leakage.
- **Data Freshness / Verification**: All prices and predictions are generated directly by application data and the Scikit-learn model; synthetic fixtures are explicitly labeled.

---

## 📑 Demonstration Walkthrough Commands

To demonstrate the full project end-to-end to an evaluator:

1. **Verify automated test suite**:
   ```powershell
   cd backend
   .\venv\Scripts\pytest -v
   ```
2. **Inspect data quality audit**:
   ```powershell
   curl http://127.0.0.1:8000/api/analytics/data-quality
   ```
3. **Inspect model performance metrics**:
   ```powershell
   curl http://127.0.0.1:8000/api/analytics/model-info
   ```
4. **Trigger real-time price prediction**:
   ```powershell
   curl -X POST http://127.0.0.1:8000/api/predict -H "Content-Type: application/json" -d "{\"commodity\":\"tomato\",\"market\":\"dindigul\",\"target_date\":\"2026-11-05\",\"arrival_volume_quintals\":650,\"rainfall_factor\":1.0}"
   ```
5. **Compare prices across 10 Tamil Nadu markets**:
   ```powershell
   curl http://127.0.0.1:8000/api/compare?commodity=tomato
   ```
6. **Calculate harvest net profit**:
   ```powershell
   curl -X POST http://127.0.0.1:8000/api/profit -H "Content-Type: application/json" -d "{\"commodity\":\"tomato\",\"market\":\"dindigul\",\"quantity_quintals\":50,\"holding_days\":3}"
   ```
7. **Navigate Frontend Pages**:
   - `Dashboard`: View 10 Tamil Nadu mandi spot rates and top market opportunities.
   - `Price Prediction`: Test 7-day, 15-day, and 30-day forecast horizons with arrival & rain adjustments.
   - `Market Comparison`: Review price spreads between Ottanchatram, Koyambedu, Paravai, and other mandis.
   - `Profit Calculator`: Experiment with transport, loading, commission, and storage costs to calculate net farmer revenue.
   - `Price Alerts`: Save target price alerts and observe instantaneous in-app trigger evaluations.
   - `Data Quality`: Review dataset schema, missing value handling, and official APMC import guidelines.
   - `Model Performance`: Inspect chronological split validation metrics and transparency documentation.
