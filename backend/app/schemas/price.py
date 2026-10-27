"""
Pydantic schemas for AgriPrice AI requests and responses
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator

class CommodityInfo(BaseModel):
    id: str
    name_en: str
    name_ta: str
    category: str
    typical_msp_per_quintal: Optional[float] = None
    seasonality: str
    unit: str = "quintal"
    typical_price_range_per_kg: Dict[str, float]

class MarketInfo(BaseModel):
    id: str
    district: str
    market_name: str
    market_name_ta: str
    market_type: str = "Regulated Market / APMC"

class PredictionRequest(BaseModel):
    commodity: str = Field(..., description="Commodity ID (e.g. tomato, small_onion, coconut)")
    market: str = Field(..., description="Market/District ID (e.g. dindigul, coimbatore, madurai)")
    target_date: str = Field(..., description="Target forecast date (YYYY-MM-DD)")
    arrival_volume_quintals: Optional[float] = Field(None, description="Optional anticipated arrival volume in quintals")
    rainfall_factor: Optional[float] = Field(1.0, description="Rainfall factor multiplier (1.0 = normal, 1.5 = excess/monsoon, 0.7 = drought)")

    @field_validator("target_date")
    @classmethod
    def validate_target_date(cls, v: str) -> str:
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Target date must be a valid calendar date in YYYY-MM-DD format")
        return v

class PerformanceComparison(BaseModel):
    horizon: str
    rf_test_mae_rs_per_quintal: float
    baseline_test_mae_rs_per_quintal: float

class PredictionResponse(BaseModel):
    commodity: str
    commodity_name_en: str
    commodity_name_ta: str
    market: str
    market_name_en: str
    market_name_ta: str
    target_date: str
    forecast_horizon_days: int = 7
    last_observation_date: str = ""
    data_sufficiency_status: str = "SUFFICIENT"
    predicted_modal_price_per_quintal: float
    predicted_price_per_kg: float
    confidence_lower_per_kg: float
    confidence_upper_per_kg: float
    baseline_last_observed_price_per_quintal: float = 0.0
    baseline_last_observed_price_per_kg: float = 0.0
    current_benchmark_price_per_kg: Optional[float] = None
    price_change_pct: float
    performance_vs_baseline: Optional[Dict[str, Any]] = None
    farmer_action: str = Field(..., description="HOLD, SELL_NOW, MONITOR, or INSUFFICIENT_DATA")
    farmer_advice_en: str
    farmer_advice_ta: str
    seasonal_phase: str = "Normal"
    estimated_arrival_quintals: float = 500.0
    warnings: List[str] = []
    data_source: str = ""
    is_synthetic: bool = False
    model_version: str = "RandomForestRegressor"
    disclaimer: str = "Advisory is a decision-support indicator and not guaranteed financial advice."
    price_unit: str = "Rs/Quintal"
    price_unit_kg: str = "Rs/kg"

class ModelMetrics(BaseModel):
    model_name: str
    algorithm: str
    evaluation_strategy: str = ""
    r2_score: float
    mae_rs_per_quintal: float
    rmse_rs_per_quintal: float
    baseline_mae_rs_per_quintal: float = 0.0
    improvement_vs_baseline_pct: float = 0.0
    test_observations: int = 0
    test_start_date: str = ""
    test_end_date: str = ""
    trained_at: str
    horizon_breakdown: Optional[Dict[str, Any]] = None
    commodity_breakdown: Optional[Dict[str, Any]] = None
    limitations: Optional[List[str]] = None

class HistoricalDataPoint(BaseModel):
    date: str
    modal_price_rs_per_quintal: float
    price_per_kg: float
    arrival_quantity_quintals: float
    season: str

class HistoricalSeriesResponse(BaseModel):
    commodity: str
    market: str
    total_records: int
    data: List[HistoricalDataPoint]

# ==============================================================================
# Feature 1: Market Comparison Schemas
# ==============================================================================
class MarketComparisonItem(BaseModel):
    market_id: str
    district: str
    market_name: str
    variety: str
    observation_date: str
    unit: str = "Rs/Quintal"
    modal_price_rs_per_quintal: float
    modal_price_per_kg: float
    min_price_per_kg: float
    max_price_per_kg: float
    arrival_quintals: float
    spread_vs_lowest_per_kg: float
    is_highest_paying: bool = False

class MarketComparisonResponse(BaseModel):
    commodity: str
    commodity_name_en: str
    commodity_name_ta: str
    requested_variety: str
    effective_observation_date: str
    price_unit: str = "Rs/Quintal (100 kg)"
    markets_count: int
    highest_market: Dict[str, Any]
    lowest_market: Dict[str, Any]
    max_price_spread_per_kg: float
    markets_data: List[MarketComparisonItem]
    advisory_en: str
    advisory_ta: str
    assumptions: List[str]
    forecast_limitations: str

# ==============================================================================
# Feature 2: Profit Calculator Schemas
# ==============================================================================
class ProfitCalculationRequest(BaseModel):
    commodity: str = Field(..., description="Commodity ID")
    market: str = Field(..., description="Target market ID")
    quantity_quintals: float = Field(..., gt=0, description="Quantity in quintals")
    unit_price_per_kg: Optional[float] = Field(None, gt=0, description="Optional override price per kg")
    transport_cost_per_quintal: float = Field(50.0, ge=0, description="Mandi transport expense per quintal")
    loading_cost_per_quintal: float = Field(20.0, ge=0, description="Handling/hamali cost per quintal")
    commission_percent: float = Field(2.0, ge=0, le=25, description="Mandi commission percentage")
    wastage_percent: float = Field(0.0, ge=0, le=40, description="Optional post-harvest wastage percentage")
    cultivation_cost_total: float = Field(0.0, ge=0, description="Total cost of cultivation")
    holding_days: int = Field(0, ge=0, le=180, description="Planned storage holding days")
    storage_cost_per_quintal_week: float = Field(25.0, ge=0, description="Storage cost per quintal per week")

class ProfitCalculationResponse(BaseModel):
    commodity: str
    commodity_name_en: str
    commodity_name_ta: str
    market: str
    market_name_en: str
    quantity_quintals: float
    total_volume_kg: float
    wastage_percent: float
    wastage_loss_quintals: float
    salable_quantity_quintals: float
    salable_quantity_kg: float
    applied_modal_price_per_kg: float
    applied_modal_price_per_quintal: float
    price_source_date: str
    price_type: str
    gross_revenue: float
    transport_expenses: float
    loading_expenses: float
    mandi_commission_fee: float
    storage_expenses: float
    total_marketing_expenses: float
    estimated_net_revenue: float
    cultivation_cost_total: float
    net_farmer_profit: float
    profit_margin_pct: float
    holding_days: int
    is_perishable: bool
    perishability_warning: Optional[str] = None
    advisory_en: str
    advisory_ta: str
    assumptions: List[str]
    forecast_limitations: str

# ==============================================================================
# Feature 3: Price Alerts Schemas
# ==============================================================================
class PriceAlertCreate(BaseModel):
    commodity: str = Field(..., description="Commodity ID")
    market: str = Field(..., description="Market ID")
    condition: str = Field(..., description="GREATER_THAN_OR_EQUAL or LESS_THAN_OR_EQUAL")
    target_price_per_kg: float = Field(..., gt=0, description="Target trigger price in Rs/kg")

class PriceAlertItem(BaseModel):
    id: str
    commodity: str
    commodity_name_en: str
    commodity_name_ta: str
    market: str
    market_name_en: str
    condition: str
    target_price_per_kg: float
    current_mandi_price_per_kg: float
    observation_date: str
    created_at: str
    is_triggered: bool
    triggered_at: Optional[str] = None
    in_app_message_en: str
    in_app_message_ta: str
    delivery_channel: str = "IN_APP_NOTIFICATION_ONLY"
    disclaimer: str = "In-app alert notification based on verified mandi transaction records. SMS/Email delivery is not configured."

class PriceAlertCheckResponse(BaseModel):
    total_alerts: int
    triggered_alerts_count: int
    alerts: List[PriceAlertItem]
    audit_timestamp: str
