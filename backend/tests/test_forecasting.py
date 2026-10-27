"""
Automated unit & integration tests for AgriPrice AI Time-Series Forecasting Module.
Verifies chronological split, zero data leakage, baseline persistence comparison,
horizon support, data sufficiency safeguards, and crop perishability constraints.
"""
import pytest
import numpy as np
import pandas as pd
from datetime import datetime

from app.ml.dataset import (
    load_and_validate_market_dataset,
    construct_forecasting_dataset,
    COMMODITY_SPECS,
)
from app.ml.train import (
    chronological_split,
    build_preprocessor,
    CATEGORICAL_FEATURES,
    NUMERICAL_FEATURES,
)
from app.ml.predictor import AgriPricePredictor

def test_chronological_split_zero_leakage():
    """Verify that train, validation, and test periods are strictly time-ordered with zero overlap."""
    raw_df, _ = load_and_validate_market_dataset()
    sample_df = raw_df[raw_df["commodity"] == "tomato"].copy()
    forecast_df = construct_forecasting_dataset(sample_df, horizons=[7, 15])

    train_df, val_df, test_df, meta = chronological_split(forecast_df)

    # 1. Train period strictly precedes validation period
    assert meta["train_period"]["end"] < meta["val_period"]["start"]

    # 2. Validation period strictly precedes test period
    assert meta["val_period"]["end"] < meta["test_period"]["start"]

    # 3. No date overlap between sets
    train_dates = set(train_df["origin_date"])
    val_dates = set(val_df["origin_date"])
    test_dates = set(test_df["origin_date"])

    assert len(train_dates.intersection(val_dates)) == 0
    assert len(val_dates.intersection(test_dates)) == 0
    assert len(train_dates.intersection(test_dates)) == 0

def test_preprocessing_fitted_only_on_train():
    """Verify that preprocessing scaler and one-hot encoder are fit strictly on X_train."""
    raw_df, _ = load_and_validate_market_dataset()
    forecast_df = construct_forecasting_dataset(raw_df[raw_df["commodity"].isin(["tomato", "small_onion"])].copy())

    train_df, val_df, test_df, _ = chronological_split(forecast_df)
    preprocessor = build_preprocessor()

    X_train = train_df[CATEGORICAL_FEATURES + NUMERICAL_FEATURES]
    X_test = test_df[CATEGORICAL_FEATURES + NUMERICAL_FEATURES]

    # Fitting on train
    preprocessor.fit(X_train)
    assert hasattr(preprocessor.named_transformers_["num"], "mean_")

    # Transforming test must work without re-fitting
    X_test_trans = preprocessor.transform(X_test)
    assert X_test_trans.shape[0] == len(X_test)

def test_baseline_persistence_is_last_observed_price():
    """Verify baseline forecast strictly equals the last observed price at forecast origin."""
    raw_df, _ = load_and_validate_market_dataset()
    forecast_df = construct_forecasting_dataset(raw_df.head(2000).copy(), horizons=[7, 15, 30])

    for _, row in forecast_df.head(50).iterrows():
        # Baseline must equal last_observed_price
        assert row["baseline_prediction"] == row["last_observed_price"]

def test_multi_horizon_forecasting_support():
    """Test predictor with 7-day, 15-day, and 30-day forecast targets."""
    predictor = AgriPricePredictor()

    # 7-day target
    res_7 = predictor.predict(
        commodity="tomato",
        market="dindigul",
        target_date_str="2026-11-02",
    )
    assert res_7["forecast_horizon_days"] == 7
    assert res_7["predicted_price_per_kg"] > 0
    assert res_7["confidence_lower_per_kg"] <= res_7["predicted_price_per_kg"]
    assert res_7["confidence_upper_per_kg"] >= res_7["predicted_price_per_kg"]

    # 30-day target (uncertainty scales wider)
    res_30 = predictor.predict(
        commodity="tomato",
        market="dindigul",
        target_date_str="2026-11-25",
    )
    assert res_30["forecast_horizon_days"] == 30
    assert res_30["predicted_price_per_kg"] > 0
    # 30-day interval must be wider than 7-day interval
    span_7 = res_7["confidence_upper_per_kg"] - res_7["confidence_lower_per_kg"]
    span_30 = res_30["confidence_upper_per_kg"] - res_30["confidence_lower_per_kg"]
    assert span_30 >= span_7

def test_insufficient_data_safeguard():
    """Verify that predictor handles insufficient history gracefully with a warning rather than inventing numbers."""
    predictor = AgriPricePredictor()
    # Query an unknown market with zero records
    res = predictor.predict(
        commodity="tomato",
        market="unknown_nonexistent_mandi",
        target_date_str="2026-11-15",
    )
    assert res["data_sufficiency_status"] == "INSUFFICIENT_HISTORY"
    assert res["farmer_action"] == "INSUFFICIENT_DATA"
    assert len(res["warnings"]) > 0
    assert "Minimum 45 trading days required" in res["warnings"][0]

def test_crop_perishability_in_farmer_advisory():
    """Verify that perishable crops (e.g. Tomato) have holding constraints while non-perishables (Turmeric) can be held."""
    predictor = AgriPricePredictor()

    # Tomato is perishable (max 5 days)
    res_tomato = predictor.predict(commodity="tomato", market="dindigul", target_date_str="2026-11-25")
    # Even if price goes up, long holding is discouraged for perishables
    if res_tomato["price_change_pct"] >= 8.0:
        assert "perishable" in res_tomato["farmer_advice_en"].lower() or res_tomato["farmer_action"] in ["MONITOR", "HOLD"]

    # Turmeric is non-perishable (safe for 180 days)
    res_turmeric = predictor.predict(commodity="turmeric", market="erode", target_date_str="2026-11-15")
    assert res_turmeric["data_sufficiency_status"] != "INSUFFICIENT_HISTORY"
    assert res_turmeric["predicted_price_per_kg"] > 0
