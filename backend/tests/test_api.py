"""
Integration tests for FastAPI endpoints
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_list_commodities():
    response = client.get("/api/commodities")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 10
    ids = [item["id"] for item in data]
    assert "tomato" in ids
    assert "small_onion" in ids
    assert "turmeric" in ids

def test_list_markets():
    response = client.get("/api/markets")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 10
    market_ids = [item["id"] for item in data]
    assert "dindigul" in market_ids
    assert "coimbatore" in market_ids
    assert "chennai" in market_ids

def test_predict_endpoint():
    payload = {
        "commodity": "small_onion",
        "market": "dindigul",
        "target_date": "2026-11-20",
        "arrival_volume_quintals": 450.0,
        "rainfall_factor": 1.0,
    }
    response = client.post("/api/predict", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert res["commodity"] == "small_onion"
    assert res["market"] == "dindigul"
    assert res["predicted_price_per_kg"] > 0
    assert "farmer_action" in res

def test_historical_analytics_endpoint():
    response = client.get("/api/analytics/historical?commodity=tomato&market=dindigul&limit=25")
    assert response.status_code == 200
    data = response.json()
    assert data["commodity"] == "tomato"
    assert len(data["data"]) > 0

def test_model_info_endpoint():
    response = client.get("/api/analytics/model-info")
    assert response.status_code == 200
    data = response.json()
    assert "r2_score" in data
    assert "mae_rs_per_quintal" in data
    assert "algorithm" in data

def test_predict_endpoint_rejects_invalid_date():
    payload = {
        "commodity": "tomato",
        "market": "dindigul",
        "target_date": "invalid-date-format",
    }
    response = client.post("/api/predict", json=payload)
    assert response.status_code == 422
    assert "target_date" in str(response.json())

def test_data_quality_endpoint_confirms_tamil_nadu_filtering():
    response = client.get("/api/analytics/data-quality")
    assert response.status_code == 200
    data = response.json()
    assert "row_count" in data
    assert data["row_count"]["cleaned_tamil_nadu_rows"] > 0
    assert data["market_count"]["unique_markets_count"] >= 10
    assert "unit_consistency" in data

