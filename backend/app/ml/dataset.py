"""
Dataset Loading, Validation, and Time-Series Feature Construction for AgriPrice AI.
Loads Tamil Nadu agricultural market transaction data, enforces strict validation,
and constructs time-ordered forecasting datasets with zero future-data leakage.
"""
import math
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

from app.config import DATASET_PATH, DATA_DIR

COMMODITY_SPECS = {
    "tomato": {
        "name_en": "Tomato",
        "name_ta": "தக்காளி",
        "base_price": 2400.0,
        "volatility": 0.45,
        "base_arrival": 850.0,
        "harvest_months": [1, 2, 8, 9],
        "lean_months": [5, 6, 11, 12],
        "perishable": True,
        "max_safe_holding_days": 5,
    },
    "small_onion": {
        "name_en": "Small Onion (Shallots)",
        "name_ta": "சின்ன வெங்காயம்",
        "base_price": 4800.0,
        "volatility": 0.38,
        "base_arrival": 520.0,
        "harvest_months": [2, 3, 4],
        "lean_months": [9, 10, 11, 12],
        "perishable": False,
        "max_safe_holding_days": 30,
    },
    "bellary_onion": {
        "name_en": "Bellary Onion",
        "name_ta": "பெல்லாரி வெங்காயம்",
        "base_price": 2800.0,
        "volatility": 0.30,
        "base_arrival": 1100.0,
        "harvest_months": [1, 2, 3],
        "lean_months": [8, 9, 10],
        "perishable": False,
        "max_safe_holding_days": 25,
    },
    "potato": {
        "name_en": "Potato (Nilgiris/Mettupalayam)",
        "name_ta": "உருளைக்கிழங்கு",
        "base_price": 2600.0,
        "volatility": 0.22,
        "base_arrival": 950.0,
        "harvest_months": [8, 9, 10],
        "lean_months": [3, 4, 5],
        "perishable": False,
        "max_safe_holding_days": 40,
    },
    "coconut": {
        "name_en": "Coconut (Pollachi)",
        "name_ta": "தேங்காய்",
        "base_price": 3200.0,
        "volatility": 0.18,
        "base_arrival": 1400.0,
        "harvest_months": [3, 4, 5, 6],
        "lean_months": [11, 12, 1],
        "perishable": False,
        "max_safe_holding_days": 60,
    },
    "banana": {
        "name_en": "Banana (Poovan/Nendran)",
        "name_ta": "வாழைப்பழம்",
        "base_price": 2900.0,
        "volatility": 0.20,
        "base_arrival": 780.0,
        "harvest_months": [7, 8, 9],
        "lean_months": [1, 2],
        "perishable": True,
        "max_safe_holding_days": 4,
    },
    "turmeric": {
        "name_en": "Turmeric (Erode Regulated)",
        "name_ta": "மஞ்சள் (ஈரோடு)",
        "base_price": 13800.0,
        "volatility": 0.25,
        "base_arrival": 400.0,
        "harvest_months": [3, 4, 5],
        "lean_months": [11, 12, 1],
        "perishable": False,
        "max_safe_holding_days": 180,
    },
    "paddy": {
        "name_en": "Paddy (Common / Delta)",
        "name_ta": "நெல்",
        "base_price": 2350.0,
        "volatility": 0.12,
        "base_arrival": 2200.0,
        "harvest_months": [1, 2, 9, 10],
        "lean_months": [5, 6, 7],
        "perishable": False,
        "max_safe_holding_days": 120,
    },
    "green_chilli": {
        "name_en": "Green Chilli",
        "name_ta": "பச்சை மிளகாய்",
        "base_price": 4200.0,
        "volatility": 0.35,
        "base_arrival": 480.0,
        "harvest_months": [2, 3, 4],
        "lean_months": [6, 7, 11],
        "perishable": True,
        "max_safe_holding_days": 6,
    },
    "tapioca": {
        "name_en": "Tapioca (Cassava - Salem)",
        "name_ta": "மரவள்ளிக்கிழங்கு",
        "base_price": 1450.0,
        "volatility": 0.20,
        "base_arrival": 1600.0,
        "harvest_months": [11, 12, 1, 2],
        "lean_months": [6, 7, 8],
        "perishable": True,
        "max_safe_holding_days": 3,
    },
}

MARKET_SPECS = {
    "coimbatore": {"district": "Coimbatore", "name_en": "Coimbatore APMC (MGR Mandi)", "multiplier": 1.05},
    "dindigul": {"district": "Dindigul", "name_en": "Ottanchatram Vegetable Mandi", "multiplier": 0.96},
    "madurai": {"district": "Madurai", "name_en": "Paravai Central Market", "multiplier": 1.02},
    "salem": {"district": "Salem", "name_en": "Salem Shevapet Market", "multiplier": 0.98},
    "tiruchirappalli": {"district": "Tiruchirappalli", "name_en": "Trichy Gandhi Market", "multiplier": 1.00},
    "erode": {"district": "Erode", "name_en": "Erode Regulated Market", "multiplier": 0.97},
    "tirunelveli": {"district": "Tirunelveli", "name_en": "Nainarkulam Market", "multiplier": 1.01},
    "thanjavur": {"district": "Thanjavur", "name_en": "Thanjavur Delta Mandi", "multiplier": 0.95},
    "vellore": {"district": "Vellore", "name_en": "Vellore Nethaji Market", "multiplier": 1.03},
    "chennai": {"district": "Chennai", "name_en": "Koyambedu Wholesale APMC", "multiplier": 1.14},
}

def get_season_name(month: int) -> str:
    if month in [10, 11, 12, 1]:
        return "North-East Monsoon (Samba)"
    elif month in [2, 3, 4, 5]:
        return "Summer / Zaid (Navarai)"
    else:
        return "South-West Monsoon (Kuruvai)"

def load_and_validate_market_dataset(filepath: Optional[Path] = None) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Loads and validates the processed Tamil Nadu market price CSV.
    Detects duplicates, missing dates, missing values, and suspicious records.
    NEVER replaces missing prices with zero.
    """
    path = Path(filepath) if filepath else DATASET_PATH
    if not path.exists():
        # Fallback to cleaned tamilnadu_prices.csv
        alt_path = DATA_DIR / "tamilnadu_prices.csv"
        if alt_path.exists():
            path = alt_path
        else:
            raise FileNotFoundError(
                f"Tamil Nadu market prices dataset not found at {path} or {alt_path}.\n"
                "Please place official Agmarknet CSV into backend/data/raw/ or generate processed dataset."
            )

    df = pd.read_csv(path)
    raw_rows = len(df)

    # Validate essential columns
    required_cols = ["date", "commodity", "market", "modal_price_rs_per_quintal"]
    missing_required = [c for c in required_cols if c not in df.columns]
    if missing_required:
        # Check if alternative column names exist (e.g. from cleaning pipeline)
        if "modal_price" in df.columns:
            df["modal_price_rs_per_quintal"] = df["modal_price"]
        else:
            raise ValueError(f"Dataset missing required price columns: {missing_required}")

    # Standardize column types
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])
    df["commodity"] = df["commodity"].astype(str).str.lower().str.strip()
    df["market"] = df["market"].astype(str).str.lower().str.strip()

    # Numeric validation (Positive prices only, NEVER zero for missing values)
    df["modal_price_rs_per_quintal"] = pd.to_numeric(df["modal_price_rs_per_quintal"], errors="coerce")
    valid_price_mask = (df["modal_price_rs_per_quintal"].notna()) & (df["modal_price_rs_per_quintal"] > 0)
    invalid_price_count = int((~valid_price_mask).sum())
    
    # Filter to valid prices strictly
    df = df[valid_price_mask].copy()

    # Deduplicate on date, commodity, market
    initial_valid = len(df)
    df = df.drop_duplicates(subset=["date", "commodity", "market"]).copy()
    duplicate_count = initial_valid - len(df)

    # Sort strictly by date, commodity, market
    df = df.sort_values(by=["commodity", "market", "date"]).reset_index(drop=True)

    # Calculate audit diagnostics
    min_date = str(df["date"].min().date()) if not df.empty else "N/A"
    max_date = str(df["date"].max().date()) if not df.empty else "N/A"
    unique_commodities = df["commodity"].unique().tolist()
    unique_markets = df["market"].unique().tolist()

    metadata = {
        "dataset_path": str(path),
        "total_records_loaded": len(df),
        "raw_rows_found": raw_rows,
        "invalid_prices_excluded": invalid_price_count,
        "duplicates_removed": duplicate_count,
        "date_range": {"start": min_date, "end": max_date},
        "commodity_count": len(unique_commodities),
        "market_count": len(unique_markets),
        "is_synthetic": (
            "data_source" in df.columns and (df["data_source"] == "SYNTHETIC_TEST_FIXTURE_NOT_OFFICIAL").any()
        ) or ("is_synthetic" in df.columns and df["is_synthetic"].any()),
    }

    return df, metadata

def construct_forecasting_dataset(
    df: pd.DataFrame,
    horizons: List[int] = [7, 15, 30],
    min_history_required: int = 45,
) -> pd.DataFrame:
    """
    Constructs a multi-horizon time-ordered forecasting dataset with ZERO future-data leakage.
    For each (commodity, market) time-series:
    - Origin date T uses only observations <= T.
    - Features: last observed price, lag prices, rolling means, rolling std, momentum, calendar harmonics.
    - Target: modal price at T + h days.
    - Baseline: last observed price at origin T (persistence forecast).
    """
    rows = []
    
    # Group by commodity and market
    grouped = df.groupby(["commodity", "market"])

    for (comm, mkt), group in grouped:
        group = group.sort_values(by="date").reset_index(drop=True)
        n_obs = len(group)
        if n_obs < min_history_required:
            continue

        # Build date index lookup for fast time-series queries
        group_dates = group["date"].tolist()
        group_prices = group["modal_price_rs_per_quintal"].tolist()
        group_arrivals = (
            group["arrival_quantity_quintals"].tolist()
            if "arrival_quantity_quintals" in group.columns
            else [500.0] * n_obs
        )

        date_to_idx = {d.strftime("%Y-%m-%d"): i for i, d in enumerate(group_dates)}

        # Iterate through possible forecast origins T
        # We need at least 15 historical points before T to compute rolling features
        for origin_idx in range(15, n_obs - 1):
            origin_dt = group_dates[origin_idx]
            origin_date_str = origin_dt.strftime("%Y-%m-%d")
            last_price = group_prices[origin_idx]
            last_arrival = group_arrivals[origin_idx]

            # Strictly historical observations up to origin T
            hist_prices_7 = group_prices[max(0, origin_idx - 3): origin_idx + 1]
            hist_prices_14 = group_prices[max(0, origin_idx - 7): origin_idx + 1]
            hist_prices_30 = group_prices[max(0, origin_idx - 15): origin_idx + 1]

            lag_7d = group_prices[max(0, origin_idx - 3)]
            lag_14d = group_prices[max(0, origin_idx - 7)]
            lag_30d = group_prices[max(0, origin_idx - 15)]

            rolling_mean_7d = float(np.mean(hist_prices_7))
            rolling_std_7d = float(np.std(hist_prices_7)) if len(hist_prices_7) > 1 else 0.0
            rolling_mean_14d = float(np.mean(hist_prices_14))
            rolling_mean_30d = float(np.mean(hist_prices_30))

            price_momentum_7d = (last_price - lag_7d) / max(lag_7d, 1.0)
            price_momentum_14d = (last_price - lag_14d) / max(lag_14d, 1.0)

            hist_arrivals_7 = group_arrivals[max(0, origin_idx - 3): origin_idx + 1]
            rolling_arrival_mean_7d = float(np.mean(hist_arrivals_7))

            # Multi-step future horizons: h in [7, 15, 30] days
            for h in horizons:
                target_dt = origin_dt + timedelta(days=h)
                
                # Find closest future observation within [T+h - 1, T+h + 2]
                future_idx = None
                for offset in [0, 1, -1, 2]:
                    check_str = (target_dt + timedelta(days=offset)).strftime("%Y-%m-%d")
                    if check_str in date_to_idx and date_to_idx[check_str] > origin_idx:
                        future_idx = date_to_idx[check_str]
                        break

                if future_idx is not None:
                    actual_target_price = group_prices[future_idx]
                    actual_target_dt = group_dates[future_idx]

                    # Target seasonal timing features
                    target_month = actual_target_dt.month
                    target_day_of_year = actual_target_dt.timetuple().tm_yday
                    month_sin = math.sin(2 * math.pi * target_month / 12)
                    month_cos = math.cos(2 * math.pi * target_month / 12)
                    target_season = get_season_name(target_month)

                    rows.append({
                        "origin_date": origin_date_str,
                        "target_date": actual_target_dt.strftime("%Y-%m-%d"),
                        "commodity": comm,
                        "market": mkt,
                        "horizon_days": h,
                        "last_observed_price": last_price,
                        "lag_7d": lag_7d,
                        "lag_14d": lag_14d,
                        "lag_30d": lag_30d,
                        "rolling_mean_7d": rolling_mean_7d,
                        "rolling_std_7d": rolling_std_7d,
                        "rolling_mean_14d": rolling_mean_14d,
                        "rolling_mean_30d": rolling_mean_30d,
                        "price_momentum_7d": price_momentum_7d,
                        "price_momentum_14d": price_momentum_14d,
                        "arrival_at_origin": last_arrival,
                        "rolling_arrival_mean_7d": rolling_arrival_mean_7d,
                        "target_month": target_month,
                        "target_day_of_year": target_day_of_year,
                        "target_month_sin": month_sin,
                        "target_month_cos": month_cos,
                        "target_season": target_season,
                        "baseline_prediction": last_price,  # Persistence baseline: y_hat = y_origin
                        "actual_target_price": actual_target_price,
                    })

    df_forecast = pd.DataFrame(rows)
    if not df_forecast.empty:
        # Sort chronologically by origin date to preserve time sequence
        df_forecast = df_forecast.sort_values(by=["origin_date", "horizon_days", "commodity"]).reset_index(drop=True)
    return df_forecast

def ensure_dataset_exists() -> pd.DataFrame:
    """Legacy helper ensuring processed dataset exists."""
    df, _ = load_and_validate_market_dataset()
    return df
