"""
Unit and integration tests for Scikit-learn model and predictor
"""
import pytest
from app.ml.dataset import ensure_dataset_exists, COMMODITY_SPECS, MARKET_SPECS
from app.ml.predictor import AgriPricePredictor

def test_dataset_generation():
    """Verify historical dataset contains realistic Tamil Nadu records and all required columns."""
    df = ensure_dataset_exists()
    assert not df.empty
    assert len(df) > 1000
    expected_cols = [
        "date", "commodity", "market", "month", "season",
        "arrival_quantity_quintals", "lag_price_7d", "modal_price_rs_per_quintal", "price_per_kg"
    ]
    for col in expected_cols:
        assert col in df.columns
    # Check that price is strictly positive
    assert (df["modal_price_rs_per_quintal"] > 0).all()

def test_predictor_inference():
    """Verify that predictor loads model and produces valid predictions with confidence bounds."""
    predictor = AgriPricePredictor()
    result = predictor.predict(
        commodity="tomato",
        market="dindigul",
        target_date_str="2026-11-15",
        arrival_volume=700.0,
        rainfall_factor=1.2,
    )
    assert result["commodity"] == "tomato"
    assert result["market"] == "dindigul"
    assert result["predicted_modal_price_per_quintal"] > 500.0
    assert result["predicted_price_per_kg"] > 5.0
    assert result["confidence_lower_per_kg"] <= result["predicted_price_per_kg"]
    assert result["confidence_upper_per_kg"] >= result["predicted_price_per_kg"]
    assert result["farmer_action"] in ["HOLD", "SELL_NOW", "MONITOR"]
    assert len(result["farmer_advice_en"]) > 10
    assert len(result["farmer_advice_ta"]) > 10

def test_all_commodities_predictable():
    """Verify prediction works across all 10 Tamil Nadu commodities."""
    predictor = AgriPricePredictor()
    for comm_id in COMMODITY_SPECS.keys():
        res = predictor.predict(
            commodity=comm_id,
            market="coimbatore",
            target_date_str="2026-12-01",
        )
        assert res["predicted_price_per_kg"] > 0.0
