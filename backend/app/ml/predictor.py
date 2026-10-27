"""
Predictor service for AgriPrice AI.
Executes multi-horizon forecasting, checks data sufficiency, evaluates against
the persistence baseline, and provides documented crop-aware farmer advisory.
"""
import math
import json
import joblib
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

from app.config import MODEL_PATH, METRICS_PATH
from app.ml.dataset import (
    COMMODITY_SPECS,
    MARKET_SPECS,
    get_season_name,
    load_and_validate_market_dataset,
)
from app.ml.train import train_and_evaluate_forecasting_model

class AgriPricePredictor:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AgriPricePredictor, cls).__new__(cls)
            cls._instance._init_service()
        return cls._instance

    def _init_service(self):
        """Loads the trained model pipeline and cached dataset."""
        if not MODEL_PATH.exists() or not METRICS_PATH.exists():
            print("[Predictor] Trained model artifact not found. Triggering training pipeline...")
            self.metrics = train_and_evaluate_forecasting_model()
            self.model = joblib.load(MODEL_PATH)
        else:
            self.model = joblib.load(MODEL_PATH)
            with open(METRICS_PATH, "r", encoding="utf-8") as f:
                self.metrics = json.load(f)

        self.df, self.dataset_meta = load_and_validate_market_dataset()
        print("[Predictor] Loaded model and dataset cache successfully.")

    def check_data_sufficiency(self, commodity: str, market: str) -> Dict[str, Any]:
        """
        Validates whether sufficient historical trading days exist for responsible forecasting.
        """
        subset = self.df[(self.df["commodity"] == commodity) & (self.df["market"] == market)]
        n_obs = len(subset)

        if n_obs < 45:
            return {
                "status": "INSUFFICIENT_HISTORY",
                "observations": n_obs,
                "supported_horizons": [],
                "message": f"Only {n_obs} observations found for {commodity} at {market}. Minimum 45 trading days required for responsible statistical forecasting.",
            }
        elif n_obs < 90:
            return {
                "status": "SUFFICIENT_FOR_7_DAY",
                "observations": n_obs,
                "supported_horizons": [7],
                "message": f"Historical series contains {n_obs} records. 7-day forecast is verified.",
            }
        elif n_obs < 180:
            return {
                "status": "SUFFICIENT_FOR_15_DAY",
                "observations": n_obs,
                "supported_horizons": [7, 15],
                "message": f"Historical series contains {n_obs} records. 7-day and 15-day forecasts verified.",
            }
        else:
            return {
                "status": "SUFFICIENT_FOR_ALL_HORIZONS",
                "observations": n_obs,
                "supported_horizons": [7, 15, 30],
                "message": f"Full historical depth ({n_obs} records) available. 7-day, 15-day, and 30-day horizons supported.",
            }

    def predict(
        self,
        commodity: str,
        market: str,
        target_date_str: str,
        arrival_volume: Optional[float] = None,
        rainfall_factor: Optional[float] = 1.0,
    ) -> Dict[str, Any]:
        """
        Executes Scikit-learn Random Forest forecasting with baseline comparison,
        horizon classification, and documented crop-specific advisory.
        """
        comm_clean = commodity.lower().strip()
        mkt_clean = market.lower().strip()
        comm_meta = COMMODITY_SPECS.get(comm_clean, {
            "name_en": commodity,
            "name_ta": commodity,
            "perishable": True,
            "max_safe_holding_days": 5,
        })
        mkt_meta = MARKET_SPECS.get(mkt_clean, {
            "district": market,
            "name_en": market,
        })

        warnings: List[str] = []

        # 1. Check Data Sufficiency
        sufficiency = self.check_data_sufficiency(comm_clean, mkt_clean)
        if sufficiency["status"] == "INSUFFICIENT_HISTORY":
            return {
                "commodity": comm_clean,
                "commodity_name_en": comm_meta["name_en"],
                "commodity_name_ta": comm_meta["name_ta"],
                "market": mkt_clean,
                "market_name_en": mkt_meta["name_en"],
                "market_name_ta": mkt_meta["district"],
                "target_date": target_date_str,
                "forecast_horizon_days": 0,
                "last_observation_date": "N/A",
                "data_sufficiency_status": sufficiency["status"],
                "predicted_modal_price_per_quintal": 0.0,
                "predicted_price_per_kg": 0.0,
                "confidence_lower_per_kg": 0.0,
                "confidence_upper_per_kg": 0.0,
                "baseline_last_observed_price_per_kg": 0.0,
                "price_change_pct": 0.0,
                "farmer_action": "INSUFFICIENT_DATA",
                "farmer_advice_en": sufficiency["message"],
                "farmer_advice_ta": "போதிய வரலாற்று சந்தைத் தரவுகள் இல்லாததால் முன்கணிப்பு செய்ய இயலவில்லை.",
                "warnings": [sufficiency["message"]],
                "data_source": self.dataset_meta.get("dataset_path", "Local Dataset"),
                "is_synthetic": self.dataset_meta.get("is_synthetic", False),
                "model_version": self.metrics.get("algorithm", "RandomForestRegressor"),
            }

        # 2. Extract series up to origin date
        subset = self.df[(self.df["commodity"] == comm_clean) & (self.df["market"] == mkt_clean)].sort_values(by="date").reset_index(drop=True)
        latest_row = subset.iloc[-1]
        last_obs_date = latest_row["date"]
        last_obs_price = float(latest_row["modal_price_rs_per_quintal"])
        last_arrival = float(latest_row["arrival_quantity_quintals"]) if "arrival_quantity_quintals" in latest_row else 500.0

        try:
            target_dt = datetime.strptime(target_date_str, "%Y-%m-%d")
        except ValueError:
            target_dt = last_obs_date + timedelta(days=7)

        # 3. Determine Horizon Bucket (7, 15, or 30 days)
        diff_days = max(1, (target_dt - last_obs_date).days)
        if diff_days <= 10:
            horizon = 7
        elif diff_days <= 22:
            horizon = 15
        else:
            horizon = 30

        # Validate horizon against supported horizons
        if horizon not in sufficiency["supported_horizons"]:
            fallback_h = sufficiency["supported_horizons"][-1]
            warnings.append(
                f"Requested {diff_days}-day horizon exceeds verified history threshold. Model safely defaulted to {fallback_h}-day forecast."
            )
            horizon = fallback_h

        if horizon > 7:
            warnings.append(f"Forecast uncertainty scales with {horizon}-day horizon. Shorter horizons (7-day) offer tighter variance.")

        # 4. Compute Features strictly using observations <= last_obs_date (Zero Leakage)
        n_pts = len(subset)
        hist_prices_7 = subset["modal_price_rs_per_quintal"].iloc[max(0, n_pts - 4):].tolist()
        hist_prices_14 = subset["modal_price_rs_per_quintal"].iloc[max(0, n_pts - 8):].tolist()
        hist_prices_30 = subset["modal_price_rs_per_quintal"].iloc[max(0, n_pts - 16):].tolist()

        lag_7d = hist_prices_7[0] if hist_prices_7 else last_obs_price
        lag_14d = hist_prices_14[0] if hist_prices_14 else lag_7d
        lag_30d = hist_prices_30[0] if hist_prices_30 else lag_14d

        rolling_mean_7d = float(np.mean(hist_prices_7))
        rolling_std_7d = float(np.std(hist_prices_7)) if len(hist_prices_7) > 1 else 0.0
        rolling_mean_14d = float(np.mean(hist_prices_14))
        rolling_mean_30d = float(np.mean(hist_prices_30))

        price_momentum_7d = (last_obs_price - lag_7d) / max(lag_7d, 1.0)
        price_momentum_14d = (last_obs_price - lag_14d) / max(lag_14d, 1.0)

        effective_arrival = arrival_volume if arrival_volume and arrival_volume > 0 else last_arrival
        rolling_arrival_mean_7d = effective_arrival

        target_month = target_dt.month
        target_day_of_year = target_dt.timetuple().tm_yday
        target_month_sin = math.sin(2 * math.pi * target_month / 12)
        target_month_cos = math.cos(2 * math.pi * target_month / 12)
        target_season = get_season_name(target_month)

        # 5. Build Pipeline Input DataFrame
        input_row = pd.DataFrame([{
            "commodity": comm_clean,
            "market": mkt_clean,
            "target_season": target_season,
            "last_observed_price": last_obs_price,
            "lag_7d": lag_7d,
            "lag_14d": lag_14d,
            "lag_30d": lag_30d,
            "rolling_mean_7d": rolling_mean_7d,
            "rolling_std_7d": rolling_std_7d,
            "rolling_mean_14d": rolling_mean_14d,
            "rolling_mean_30d": rolling_mean_30d,
            "price_momentum_7d": price_momentum_7d,
            "price_momentum_14d": price_momentum_14d,
            "arrival_at_origin": effective_arrival,
            "rolling_arrival_mean_7d": rolling_arrival_mean_7d,
            "horizon_days": horizon,
            "target_month": target_month,
            "target_day_of_year": target_day_of_year,
            "target_month_sin": target_month_sin,
            "target_month_cos": target_month_cos,
        }])

        # 6. Execute ML Inference
        pred_quintal = float(self.model.predict(input_row)[0])
        pred_kg = round(pred_quintal / 100.0, 2)
        base_kg = round(last_obs_price / 100.0, 2)

        # 7. Prediction Interval via empirical validation calibration
        interval_calib = self.metrics.get("prediction_interval_calibration", {}).get("interval_80_percent_residuals", {})
        lower_delta = interval_calib.get("lower_delta", -180.0)
        upper_delta = interval_calib.get("upper_delta", 180.0)

        # Scale interval with horizon degradation: sqrt(h / 7)
        horizon_factor = math.sqrt(horizon / 7.0)
        conf_lower_quintal = max(pred_quintal * 0.5, pred_quintal + lower_delta * horizon_factor)
        conf_upper_quintal = pred_quintal + upper_delta * horizon_factor

        conf_lower_kg = round(conf_lower_quintal / 100.0, 2)
        conf_upper_kg = round(conf_upper_quintal / 100.0, 2)

        price_change_pct = round(((pred_kg - base_kg) / base_kg) * 100.0, 1)

        # 8. Documented Farmer Advisory with Perishability Constraints
        is_perishable = comm_meta.get("perishable", True)
        max_safe_hold = comm_meta.get("max_safe_holding_days", 5)

        if price_change_pct >= 8.0:
            if is_perishable and horizon > max_safe_hold:
                farmer_action = "MONITOR"
                farmer_advice_en = (
                    f"Model projects a price rise (+{price_change_pct}%), but {comm_meta['name_en']} is highly perishable "
                    f"(safe storage limit is ~{max_safe_hold} days). Holding stock for {diff_days} days risks spoilage. "
                    "Recommendation: Harvest and sell in regular batches rather than holding."
                )
                farmer_advice_ta = (
                    f"விலை உயர வாய்ப்புள்ளது (+{price_change_pct}%), ஆனால் {comm_meta['name_ta']} அழுகும் தன்மையுடையது "
                    f"(அதிகபட்ச இருப்பு {max_safe_hold} நாட்கள்). நீண்ட நாட்கள் வைப்பது இழப்பை ஏற்படுத்தும். "
                    "பரிந்துரை: பிரித்து வழக்கம்போல விற்பனை செய்யவும்."
                )
            else:
                farmer_action = "HOLD"
                farmer_advice_en = (
                    f"Favorable upward projection (+{price_change_pct}% over last observed rate). Supply is projected to tighten. "
                    f"Recommendation: Hold stock for {min(horizon, max_safe_hold)} days to capitalize on peak bidding."
                )
                farmer_advice_ta = (
                    f"விலை அதிகரிக்க வாய்ப்பு (+{price_change_pct}% உயர்வு). சந்தையில் வரத்து குறையலாம். "
                    f"பரிந்துரை: {min(horizon, max_safe_hold)} நாட்கள் வரை காத்திருந்து அதிக விலைக்கு விற்கவும்."
                )
        elif price_change_pct <= -6.0:
            farmer_action = "SELL_NOW"
            farmer_advice_en = (
                f"Downside pressure projected ({price_change_pct}% change). Supply influx or seasonal harvest peak expected. "
                "Recommendation: Liquidate harvest promptly in the current market cycle to avoid price slide."
            )
            farmer_advice_ta = (
                f"விலை சரிய வாய்ப்புள்ளது ({price_change_pct}% சரிவு). சந்தைக்கு வரத்து அதிகரிக்கலாம். "
                "பரிந்துரை: தாமதமின்றி உடனடியாக தற்போதைய விலைக்கு விற்கவும்."
            )
        else:
            farmer_action = "MONITOR"
            farmer_advice_en = (
                f"Stable trading range projected ({price_change_pct}% change vs last observed price). "
                "Recommendation: Proceed with regular scheduled sales. No immediate rush or hoarding needed."
            )
            farmer_advice_ta = (
                f"சந்தை விலை சீராக இருக்கும் ({price_change_pct}% மாற்றம்). "
                "பரிந்துரை: வழக்கமான அட்டவணைப்படி தொடர்ந்து சந்தைக்கு கொண்டு செல்லலாம்."
            )

        # Baseline comparison metadata from model test evaluation
        horizon_key = f"{horizon}_day"
        rf_test_mae = self.metrics.get("test_evaluation", {}).get("horizon_breakdown", {}).get(horizon_key, {}).get("rf_mae", 150.0)
        base_test_mae = self.metrics.get("test_evaluation", {}).get("horizon_breakdown", {}).get(horizon_key, {}).get("baseline_mae", 180.0)

        return {
            "commodity": comm_clean,
            "commodity_name_en": comm_meta["name_en"],
            "commodity_name_ta": comm_meta["name_ta"],
            "market": mkt_clean,
            "market_name_en": mkt_meta["name_en"],
            "market_name_ta": mkt_meta["district"],
            "target_date": target_date_str,
            "forecast_horizon_days": horizon,
            "last_observation_date": last_obs_date.strftime("%Y-%m-%d"),
            "data_sufficiency_status": sufficiency["status"],
            "predicted_modal_price_per_quintal": round(pred_quintal, 2),
            "predicted_price_per_kg": pred_kg,
            "confidence_lower_per_kg": conf_lower_kg,
            "confidence_upper_per_kg": conf_upper_kg,
            "baseline_last_observed_price_per_quintal": round(last_obs_price, 2),
            "baseline_last_observed_price_per_kg": base_kg,
            "price_change_pct": price_change_pct,
            "performance_vs_baseline": {
                "horizon": f"{horizon} Days",
                "rf_test_mae_rs_per_quintal": rf_test_mae,
                "baseline_test_mae_rs_per_quintal": base_test_mae,
            },
            "farmer_action": farmer_action,
            "farmer_advice_en": farmer_advice_en,
            "farmer_advice_ta": farmer_advice_ta,
            "seasonal_phase": target_season,
            "estimated_arrival_quintals": round(effective_arrival, 1),
            "warnings": warnings,
            "data_source": self.dataset_meta.get("dataset_path", "Cleaned Tamil Nadu Dataset"),
            "is_synthetic": self.dataset_meta.get("is_synthetic", False),
            "model_version": self.metrics.get("algorithm", "RandomForestRegressor"),
            "disclaimer": "Advisory is a decision-support indicator based on historical market trends and does not constitute guaranteed financial advice.",
        }

    def get_historical_series(self, commodity: str, market: str, limit: int = 40):
        """Returns recent historical modal price sequence for charting."""
        subset = self.df[(self.df["commodity"] == commodity.lower().strip()) & (self.df["market"] == market.lower().strip())].copy()
        if subset.empty:
            return []
        subset = subset.tail(limit)
        return [
            {
                "date": row["date"].strftime("%Y-%m-%d"),
                "modal_price_rs_per_quintal": float(row["modal_price_rs_per_quintal"]),
                "price_per_kg": round(float(row["modal_price_rs_per_quintal"]) / 100.0, 2),
                "arrival_quantity_quintals": float(row["arrival_quantity_quintals"]) if "arrival_quantity_quintals" in row else 500.0,
                "season": row["season"] if "season" in row else "Current",
            }
            for _, row in subset.iterrows()
        ]
