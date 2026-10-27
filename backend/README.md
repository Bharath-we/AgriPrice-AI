# AgriPrice AI - FastAPI Backend & Scikit-learn ML Engine

The backend for **AgriPrice AI** provides agricultural commodity price prediction and mandi market intelligence across **Tamil Nadu, India**.

## Features
- **Scikit-learn Regression Pipeline**: Features `RandomForestRegressor` with `ColumnTransformer` (OneHotEncoding for categorical crop/mandi/season + StandardScaler for numeric lag prices/arrivals/rainfall).
- **FastAPI Endpoints**: High-performance RESTful API with Pydantic validation and automatic OpenAPI Swagger docs (`/docs`).
- **Authentic Tamil Nadu Context**: Covers 10 Tamil Nadu APMC hubs (Coimbatore, Dindigul Ottanchatram, Madurai, Salem, Trichy, Erode, Tirunelveli, Thanjavur Delta, Vellore, Chennai Koyambedu) and 10 staple crops.
- **Farmer Action Advisory**: Actionable recommendation engine outputting **HOLD**, **SELL_NOW**, or **MONITOR** based on projected price movement vs current modal rates.

## Architecture & Directory Layout
```
backend/
├── app/
│   ├── api/
│   │   ├── endpoints/
│   │   │   ├── analytics.py    # Time-series historical data & cross-market comparison
│   │   │   ├── commodities.py  # Crop catalogue (English + Tamil)
│   │   │   ├── markets.py      # APMC mandis catalogue
│   │   │   └── predict.py      # Scikit-learn model inference endpoint
│   │   └── router.py           # Unified router
│   ├── ml/
│   │   ├── artifacts/          # Serialized model.joblib & metrics.json
│   │   ├── dataset.py          # Agmarknet historical transaction synthesizer
│   │   ├── predictor.py        # Model loading & inference service
│   │   └── train.py            # Model training & cross-validation script
│   ├── schemas/
│   │   └── price.py            # Pydantic data contracts
│   ├── config.py               # Path constants & CORS
│   └── main.py                 # FastAPI application
├── data/
│   └── processed/
│       └── tn_agri_market_prices.csv
├── tests/
│   ├── test_api.py             # API endpoint integration tests
│   └── test_model.py           # ML pipeline unit tests
└── requirements.txt
```

## Setup & Running

### 1. Create and Activate Virtual Environment
```powershell
cd c:\Users\user\Desktop\Agri-price-AI\backend
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Generate Data and Train the ML Model
```powershell
python -m app.ml.train
```

### 4. Run Automated Tests
```powershell
pytest tests/ -v
```

### 5. Launch FastAPI Server
```powershell
uvicorn app.main:app --reload --port 8000
```
Swagger UI will be live at: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
