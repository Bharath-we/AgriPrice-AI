"""
Tests for the three farmer-focused features:
  1. Market Comparison endpoint
  2. Profit Calculator endpoint & calculation logic
  3. Price Alerts endpoint (create, list, delete, trigger evaluation)

All price resolution uses the AgriPricePredictor which loads synthetic
test fixtures — no real data is needed for these tests.
"""
import os
import json
import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
def _alerts_file_path():
    """Return the alerts.json path used by the backend."""
    from app.config import DATA_DIR
    return DATA_DIR / "alerts.json"


def _clear_alerts():
    """Remove all persisted alerts before/after test."""
    path = _alerts_file_path()
    if path.exists():
        path.write_text("[]", encoding="utf-8")


# ─────────────────────────────────────────────────────────────────────────────
# Feature 1: Market Comparison
# ─────────────────────────────────────────────────────────────────────────────
class TestMarketComparison:
    def test_compare_valid_commodity_returns_200(self):
        resp = client.get("/api/compare?commodity=tomato")
        assert resp.status_code == 200, resp.text

    def test_compare_response_schema(self):
        resp = client.get("/api/compare?commodity=tomato")
        data = resp.json()
        assert "commodity" in data
        assert "commodity_name_en" in data
        assert "markets_data" in data
        assert isinstance(data["markets_data"], list)
        assert data["markets_count"] >= 1

    def test_compare_prices_never_zero_or_negative(self):
        resp = client.get("/api/compare?commodity=small_onion")
        data = resp.json()
        for mkt in data["markets_data"]:
            assert mkt["modal_price_rs_per_quintal"] > 0, (
                f"Market {mkt['market_id']} has non-positive modal price"
            )
            assert mkt["modal_price_per_kg"] > 0

    def test_compare_sorted_descending_by_price(self):
        resp = client.get("/api/compare?commodity=turmeric")
        data = resp.json()
        prices = [m["modal_price_rs_per_quintal"] for m in data["markets_data"]]
        assert prices == sorted(prices, reverse=True), (
            "Markets should be sorted from highest to lowest modal price"
        )

    def test_compare_highest_market_flagged(self):
        resp = client.get("/api/compare?commodity=tomato")
        data = resp.json()
        flagged = [m for m in data["markets_data"] if m["is_highest_paying"]]
        assert len(flagged) == 1
        assert flagged[0]["market_id"] == data["highest_market"]["market_id"]

    def test_compare_spread_computed_correctly(self):
        resp = client.get("/api/compare?commodity=paddy")
        data = resp.json()
        prices_kg = [m["modal_price_per_kg"] for m in data["markets_data"]]
        expected_spread = round(max(prices_kg) - min(prices_kg), 2)
        assert abs(data["max_price_spread_per_kg"] - expected_spread) < 0.05

    def test_compare_bilingual_advisory_present(self):
        resp = client.get("/api/compare?commodity=banana")
        data = resp.json()
        assert len(data.get("advisory_en", "")) > 20
        assert len(data.get("advisory_ta", "")) > 20

    def test_compare_assumptions_and_limitations_present(self):
        resp = client.get("/api/compare?commodity=coconut")
        data = resp.json()
        assert len(data.get("assumptions", [])) >= 3
        assert len(data.get("forecast_limitations", "")) > 20

    def test_compare_invalid_commodity_returns_404(self):
        resp = client.get("/api/compare?commodity=mango_fake")
        assert resp.status_code == 404

    def test_compare_market_filter_subset(self):
        resp = client.get("/api/compare?commodity=tomato&markets=dindigul,chennai")
        data = resp.json()
        market_ids = [m["market_id"] for m in data["markets_data"]]
        for mkt_id in market_ids:
            assert mkt_id in ("dindigul", "chennai")


# ─────────────────────────────────────────────────────────────────────────────
# Feature 2: Profit Calculator (backend endpoint)
# ─────────────────────────────────────────────────────────────────────────────
class TestProfitCalculator:
    BASE_PAYLOAD = {
        "commodity": "tomato",
        "market": "dindigul",
        "quantity_quintals": 50.0,
        "transport_cost_per_quintal": 60.0,
        "loading_cost_per_quintal": 20.0,
        "commission_percent": 2.0,
        "wastage_percent": 5.0,
        "cultivation_cost_total": 35000.0,
        "holding_days": 0,
        "storage_cost_per_quintal_week": 25.0,
    }

    def test_profit_endpoint_returns_200(self):
        resp = client.post("/api/profit", json=self.BASE_PAYLOAD)
        assert resp.status_code == 200, resp.text

    def test_profit_response_schema(self):
        resp = client.post("/api/profit", json=self.BASE_PAYLOAD)
        data = resp.json()
        required = [
            "gross_revenue", "transport_expenses", "loading_expenses",
            "mandi_commission_fee", "storage_expenses", "total_marketing_expenses",
            "estimated_net_revenue", "net_farmer_profit", "profit_margin_pct",
            "salable_quantity_quintals", "wastage_loss_quintals",
        ]
        for key in required:
            assert key in data, f"Missing field: {key}"

    def test_profit_gross_revenue_is_positive(self):
        resp = client.post("/api/profit", json=self.BASE_PAYLOAD)
        data = resp.json()
        assert data["gross_revenue"] > 0

    def test_profit_commission_calculated_correctly(self):
        payload = {**self.BASE_PAYLOAD, "commission_percent": 2.0, "wastage_percent": 0.0}
        resp = client.post("/api/profit", json=payload)
        data = resp.json()
        expected_commission = round((data["gross_revenue"] * 2.0) / 100.0, 2)
        assert abs(data["mandi_commission_fee"] - expected_commission) < 0.05

    def test_profit_wastage_reduces_salable_quantity(self):
        payload = {**self.BASE_PAYLOAD, "wastage_percent": 10.0}
        resp = client.post("/api/profit", json=payload)
        data = resp.json()
        expected_salable = payload["quantity_quintals"] * 0.90
        assert abs(data["salable_quantity_quintals"] - expected_salable) < 0.01

    def test_profit_storage_cost_for_7_day_holding(self):
        payload = {**self.BASE_PAYLOAD, "holding_days": 7, "storage_cost_per_quintal_week": 30.0}
        resp = client.post("/api/profit", json=payload)
        data = resp.json()
        # 1 week * 50 quintals * 30 rs = 1500
        expected_storage = 50.0 * 1.0 * 30.0
        assert abs(data["storage_expenses"] - expected_storage) < 0.5

    def test_profit_net_revenue_equals_gross_minus_expenses(self):
        resp = client.post("/api/profit", json=self.BASE_PAYLOAD)
        data = resp.json()
        expected_net_revenue = round(
            data["gross_revenue"] - data["total_marketing_expenses"], 2
        )
        assert abs(data["estimated_net_revenue"] - expected_net_revenue) < 0.05

    def test_profit_net_farmer_profit_equals_net_revenue_minus_cultivation(self):
        resp = client.post("/api/profit", json=self.BASE_PAYLOAD)
        data = resp.json()
        expected_profit = round(data["estimated_net_revenue"] - data["cultivation_cost_total"], 2)
        assert abs(data["net_farmer_profit"] - expected_profit) < 0.05

    def test_profit_override_price_is_used(self):
        payload = {**self.BASE_PAYLOAD, "unit_price_per_kg": 99.9}
        resp = client.post("/api/profit", json=payload)
        data = resp.json()
        assert abs(data["applied_modal_price_per_kg"] - 99.9) < 0.01
        assert "User-entered" in data["price_type"]

    def test_profit_perishable_warning_when_holding_exceeds_limit(self):
        payload = {**self.BASE_PAYLOAD, "commodity": "tomato", "holding_days": 15}
        resp = client.post("/api/profit", json=payload)
        data = resp.json()
        assert data["is_perishable"] is True
        assert data["perishability_warning"] is not None
        assert "tomato" in data["perishability_warning"].lower() or "Tomato" in data["perishability_warning"]

    def test_profit_no_perishable_warning_within_safe_limit(self):
        payload = {**self.BASE_PAYLOAD, "commodity": "turmeric", "holding_days": 30}
        resp = client.post("/api/profit", json=payload)
        data = resp.json()
        assert data["is_perishable"] is False
        assert data["perishability_warning"] is None

    def test_profit_bilingual_advisory_present(self):
        resp = client.post("/api/profit", json=self.BASE_PAYLOAD)
        data = resp.json()
        assert len(data.get("advisory_en", "")) > 30
        assert len(data.get("advisory_ta", "")) > 30

    def test_profit_invalid_commodity_returns_404(self):
        payload = {**self.BASE_PAYLOAD, "commodity": "fake_crop"}
        resp = client.post("/api/profit", json=payload)
        assert resp.status_code == 404

    def test_profit_invalid_market_returns_404(self):
        payload = {**self.BASE_PAYLOAD, "market": "atlantis"}
        resp = client.post("/api/profit", json=payload)
        assert resp.status_code == 404

    def test_profit_zero_quantity_rejected(self):
        payload = {**self.BASE_PAYLOAD, "quantity_quintals": 0}
        resp = client.post("/api/profit", json=payload)
        assert resp.status_code == 422  # Pydantic gt=0 validation


# ─────────────────────────────────────────────────────────────────────────────
# Feature 3: Price Alerts
# ─────────────────────────────────────────────────────────────────────────────
class TestPriceAlerts:
    def setup_method(self):
        """Clear alerts before each test."""
        _clear_alerts()

    def teardown_method(self):
        """Clean up after each test."""
        _clear_alerts()

    def _create_alert(self, commodity="tomato", market="dindigul",
                      condition="GREATER_THAN_OR_EQUAL", price=1.0):
        return client.post("/api/alerts", json={
            "commodity": commodity,
            "market": market,
            "condition": condition,
            "target_price_per_kg": price,
        })

    def test_list_alerts_returns_200(self):
        resp = client.get("/api/alerts")
        assert resp.status_code == 200

    def test_list_empty_alerts(self):
        resp = client.get("/api/alerts")
        data = resp.json()
        assert data["total_alerts"] == 0
        assert data["alerts"] == []
        assert data["triggered_alerts_count"] == 0

    def test_create_alert_returns_201_or_200(self):
        resp = self._create_alert(price=50.0)
        assert resp.status_code in (200, 201), resp.text

    def test_create_alert_schema(self):
        resp = self._create_alert(price=50.0)
        data = resp.json()
        required = [
            "id", "commodity", "commodity_name_en", "market", "market_name_en",
            "condition", "target_price_per_kg", "is_triggered",
            "in_app_message_en", "in_app_message_ta", "delivery_channel", "disclaimer",
        ]
        for key in required:
            assert key in data, f"Missing field: {key}"

    def test_create_alert_delivery_channel_is_in_app_only(self):
        resp = self._create_alert(price=50.0)
        data = resp.json()
        assert data["delivery_channel"] == "IN_APP_NOTIFICATION_ONLY"
        assert "SMS" in data["disclaimer"] or "Email" in data["disclaimer"]

    def test_create_alert_persisted_and_listed(self):
        self._create_alert(price=50.0)
        resp = client.get("/api/alerts")
        data = resp.json()
        assert data["total_alerts"] == 1

    def test_create_multiple_alerts_all_listed(self):
        self._create_alert(commodity="tomato", price=30.0)
        self._create_alert(commodity="turmeric", price=150.0)
        resp = client.get("/api/alerts")
        data = resp.json()
        assert data["total_alerts"] == 2

    def test_alert_trigger_gte_when_price_above_target(self):
        # Very low target: should trigger (current prices are >> 0.01 Rs/kg)
        resp = self._create_alert(condition="GREATER_THAN_OR_EQUAL", price=0.01)
        data = resp.json()
        # Current mandi price should be >> 0.01
        assert data["is_triggered"] is True

    def test_alert_no_trigger_gte_when_price_below_target(self):
        # Astronomically high target: should NOT trigger
        resp = self._create_alert(condition="GREATER_THAN_OR_EQUAL", price=999999.0)
        data = resp.json()
        assert data["is_triggered"] is False

    def test_alert_trigger_lte_when_price_below_target(self):
        # Very high target with LTE: should trigger
        resp = self._create_alert(condition="LESS_THAN_OR_EQUAL", price=999999.0)
        data = resp.json()
        assert data["is_triggered"] is True

    def test_alert_no_trigger_lte_when_price_above_target(self):
        # Negative LTE: should NOT trigger (prices are always positive)
        resp = self._create_alert(condition="LESS_THAN_OR_EQUAL", price=0.001)
        data = resp.json()
        assert data["is_triggered"] is False

    def test_delete_alert_removes_it(self):
        create_resp = self._create_alert(price=50.0)
        alert_id = create_resp.json()["id"]

        del_resp = client.delete(f"/api/alerts/{alert_id}")
        assert del_resp.status_code == 200

        list_resp = client.get("/api/alerts")
        assert list_resp.json()["total_alerts"] == 0

    def test_delete_nonexistent_alert_returns_404(self):
        resp = client.delete(f"/api/alerts/{uuid.uuid4()}")
        assert resp.status_code == 404

    def test_create_alert_invalid_commodity_returns_404(self):
        resp = client.post("/api/alerts", json={
            "commodity": "saffron_fake",
            "market": "dindigul",
            "condition": "GREATER_THAN_OR_EQUAL",
            "target_price_per_kg": 50.0,
        })
        assert resp.status_code == 404

    def test_create_alert_invalid_condition_returns_422(self):
        resp = client.post("/api/alerts", json={
            "commodity": "tomato",
            "market": "dindigul",
            "condition": "NOT_A_CONDITION",
            "target_price_per_kg": 50.0,
        })
        assert resp.status_code == 422

    def test_create_alert_zero_price_rejected(self):
        resp = client.post("/api/alerts", json={
            "commodity": "tomato",
            "market": "dindigul",
            "condition": "GREATER_THAN_OR_EQUAL",
            "target_price_per_kg": 0.0,
        })
        assert resp.status_code == 422  # Pydantic gt=0 validation

    def test_alert_messages_bilingual(self):
        resp = self._create_alert(price=0.01)  # triggers immediately
        data = resp.json()
        assert len(data.get("in_app_message_en", "")) > 20
        assert len(data.get("in_app_message_ta", "")) > 20

    def test_audit_timestamp_present(self):
        resp = client.get("/api/alerts")
        data = resp.json()
        assert "audit_timestamp" in data
        assert len(data["audit_timestamp"]) > 0
