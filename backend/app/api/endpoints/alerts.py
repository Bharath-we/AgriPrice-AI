"""
Price Alerts Endpoint for AgriPrice AI.
Allows users to save target price thresholds and checks them against
real imported/refreshed market observations.

- Alerts are persisted in a JSON file (backend/data/alerts.json).
- Trigger checks use only verified mandi observation records.
- In-app notification only. SMS/Email delivery is NOT configured.
"""
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.price import PriceAlertCreate, PriceAlertItem, PriceAlertCheckResponse
from app.ml.predictor import AgriPricePredictor
from app.ml.dataset import COMMODITY_SPECS, MARKET_SPECS
from app.config import DATA_DIR

router = APIRouter()

ALERTS_FILE = DATA_DIR / "alerts.json"


def get_predictor() -> AgriPricePredictor:
    return AgriPricePredictor()


def _load_alerts() -> list:
    """Load persisted alerts from JSON file."""
    if ALERTS_FILE.exists():
        try:
            with open(ALERTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def _save_alerts(alerts: list) -> None:
    """Persist alerts to JSON file."""
    ALERTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(ALERTS_FILE, "w", encoding="utf-8") as f:
        json.dump(alerts, f, indent=2, ensure_ascii=False)


def _get_current_price(predictor: AgriPricePredictor, commodity: str, market: str) -> tuple[float, str]:
    """
    Returns the latest verified mandi modal price per kg and observation date.
    Returns (0.0, "") only if truly no data exists — never fills with synthetic values.
    """
    df = predictor.df
    subset = df[(df["commodity"] == commodity) & (df["market"] == market)].sort_values("date")

    if subset.empty:
        # Widen to any market for this commodity as fallback
        subset = df[df["commodity"] == commodity].sort_values("date")

    if subset.empty:
        return 0.0, ""

    last_row = subset.iloc[-1]
    price_per_kg = round(float(last_row["modal_price_rs_per_quintal"]) / 100.0, 2)
    obs_date = last_row["date"].strftime("%Y-%m-%d")
    return price_per_kg, obs_date


def _evaluate_trigger(alert: dict, current_price: float) -> bool:
    """Check if the alert condition is met by the current verified mandi price."""
    if current_price <= 0:
        return False  # no verified data → never trigger

    condition = alert.get("condition", "")
    target = alert.get("target_price_per_kg", 0.0)

    if condition == "GREATER_THAN_OR_EQUAL":
        return current_price >= target
    elif condition == "LESS_THAN_OR_EQUAL":
        return current_price <= target
    return False


def _build_alert_message(
    alert: dict,
    current_price: float,
    obs_date: str,
    triggered: bool,
) -> tuple[str, str]:
    """Build bilingual in-app alert notification messages."""
    comm_spec = COMMODITY_SPECS.get(alert.get("commodity", ""), {})
    name_en = comm_spec.get("name_en", alert.get("commodity", "").replace("_", " ").title())
    name_ta = comm_spec.get("name_ta", name_en)

    mkt_spec = MARKET_SPECS.get(alert.get("market", ""), {})
    mkt_en = mkt_spec.get("name_en", alert.get("market", "").title())
    mkt_district = mkt_spec.get("district", alert.get("market", "").title())

    condition_text_en = "risen to or above" if alert.get("condition") == "GREATER_THAN_OR_EQUAL" else "fallen to or below"
    condition_text_ta = "அல்லது அதற்கு மேல் உயர்ந்துள்ளது" if alert.get("condition") == "GREATER_THAN_OR_EQUAL" else "அல்லது அதற்கு கீழே இறங்கியுள்ளது"

    if triggered:
        msg_en = (
            f"✅ ALERT TRIGGERED: {name_en} at {mkt_en} ({mkt_district}) has {condition_text_en} "
            f"your target of ₹{alert['target_price_per_kg']:.2f}/kg. "
            f"Current verified mandi price: ₹{current_price:.2f}/kg (as of {obs_date}). "
            f"In-app notification only. SMS/Email delivery is not configured."
        )
        msg_ta = (
            f"✅ விலை இலக்கு எட்டப்பட்டது: {name_ta} ({mkt_district}) சந்தையில் விலை "
            f"உங்கள் இலக்கான ₹{alert['target_price_per_kg']:.2f}/கிலோவை {condition_text_ta}. "
            f"தற்போதைய சரிபார்க்கப்பட்ட விலை: ₹{current_price:.2f}/கிலோ ({obs_date} நிலவரம்). "
            f"இது ஒரு செயலி அறிவிப்பு மட்டுமே."
        )
    else:
        msg_en = (
            f"⏳ WATCHING: {name_en} at {mkt_en} ({mkt_district}). "
            f"Current verified mandi price: ₹{current_price:.2f}/kg (as of {obs_date}). "
            f"Target: {condition_text_en} ₹{alert['target_price_per_kg']:.2f}/kg. "
            f"Alert has not triggered yet."
        )
        msg_ta = (
            f"⏳ கண்காணிப்பில்: {name_ta} ({mkt_district}). "
            f"தற்போதைய சரிபார்க்கப்பட்ட விலை: ₹{current_price:.2f}/கிலோ ({obs_date} நிலவரம்). "
            f"இலக்கு விலை ₹{alert['target_price_per_kg']:.2f}/கிலோ இன்னும் எட்டப்படவில்லை."
        )
    return msg_en, msg_ta


@router.get("", response_model=PriceAlertCheckResponse)
def list_and_check_alerts(
    predictor: AgriPricePredictor = Depends(get_predictor),
):
    """
    Lists all saved alerts and checks each one against the latest verified mandi price.
    Triggers are evaluated using real APMC observation data — never synthetic.
    """
    raw_alerts = _load_alerts()
    now_utc = datetime.now(timezone.utc).isoformat()
    enriched: List[PriceAlertItem] = []
    triggered_count = 0

    for alert in raw_alerts:
        commodity = alert.get("commodity", "")
        market = alert.get("market", "")
        comm_spec = COMMODITY_SPECS.get(commodity, {})
        mkt_spec = MARKET_SPECS.get(market, {})

        current_price, obs_date = _get_current_price(predictor, commodity, market)
        triggered = _evaluate_trigger(alert, current_price)

        if triggered and not alert.get("triggered_at"):
            alert["triggered_at"] = now_utc

        msg_en, msg_ta = _build_alert_message(alert, current_price, obs_date, triggered)

        if triggered:
            triggered_count += 1

        enriched.append(
            PriceAlertItem(
                id=alert.get("id", str(uuid.uuid4())),
                commodity=commodity,
                commodity_name_en=comm_spec.get("name_en", commodity),
                commodity_name_ta=comm_spec.get("name_ta", commodity),
                market=market,
                market_name_en=mkt_spec.get("name_en", market),
                condition=alert.get("condition", ""),
                target_price_per_kg=alert.get("target_price_per_kg", 0.0),
                current_mandi_price_per_kg=current_price,
                observation_date=obs_date,
                created_at=alert.get("created_at", now_utc),
                is_triggered=triggered,
                triggered_at=alert.get("triggered_at"),
                in_app_message_en=msg_en,
                in_app_message_ta=msg_ta,
                delivery_channel="IN_APP_NOTIFICATION_ONLY",
                disclaimer="In-app alert based on verified mandi records. SMS/Email delivery is NOT configured.",
            )
        )

    # Persist updated triggered_at states
    _save_alerts(raw_alerts)

    return PriceAlertCheckResponse(
        total_alerts=len(enriched),
        triggered_alerts_count=triggered_count,
        alerts=enriched,
        audit_timestamp=now_utc,
    )


@router.post("", response_model=PriceAlertItem)
def create_alert(
    req: PriceAlertCreate,
    predictor: AgriPricePredictor = Depends(get_predictor),
):
    """
    Creates and persists a new price alert.
    Validates commodity and market IDs. Evaluates trigger immediately against latest mandi data.
    """
    commodity = req.commodity.lower().strip()
    market = req.market.lower().strip()

    if commodity not in COMMODITY_SPECS:
        raise HTTPException(status_code=404, detail=f"Commodity '{commodity}' not found.")
    if market not in MARKET_SPECS:
        raise HTTPException(status_code=404, detail=f"Market '{market}' not found.")

    condition = req.condition.upper().strip()
    if condition not in ("GREATER_THAN_OR_EQUAL", "LESS_THAN_OR_EQUAL"):
        raise HTTPException(
            status_code=422,
            detail="condition must be 'GREATER_THAN_OR_EQUAL' or 'LESS_THAN_OR_EQUAL'.",
        )

    now_utc = datetime.now(timezone.utc).isoformat()
    alert_id = str(uuid.uuid4())

    alert_record = {
        "id": alert_id,
        "commodity": commodity,
        "market": market,
        "condition": condition,
        "target_price_per_kg": req.target_price_per_kg,
        "created_at": now_utc,
        "triggered_at": None,
    }

    # Immediate trigger check
    current_price, obs_date = _get_current_price(predictor, commodity, market)
    triggered = _evaluate_trigger(alert_record, current_price)
    if triggered:
        alert_record["triggered_at"] = now_utc

    # Persist
    raw_alerts = _load_alerts()
    raw_alerts.append(alert_record)
    _save_alerts(raw_alerts)

    comm_spec = COMMODITY_SPECS[commodity]
    mkt_spec = MARKET_SPECS[market]
    msg_en, msg_ta = _build_alert_message(alert_record, current_price, obs_date, triggered)

    return PriceAlertItem(
        id=alert_id,
        commodity=commodity,
        commodity_name_en=comm_spec["name_en"],
        commodity_name_ta=comm_spec["name_ta"],
        market=market,
        market_name_en=mkt_spec["name_en"],
        condition=condition,
        target_price_per_kg=req.target_price_per_kg,
        current_mandi_price_per_kg=current_price,
        observation_date=obs_date,
        created_at=now_utc,
        is_triggered=triggered,
        triggered_at=alert_record.get("triggered_at"),
        in_app_message_en=msg_en,
        in_app_message_ta=msg_ta,
        delivery_channel="IN_APP_NOTIFICATION_ONLY",
        disclaimer="In-app alert based on verified mandi records. SMS/Email delivery is NOT configured.",
    )


@router.delete("/{alert_id}")
def delete_alert(alert_id: str):
    """Deletes a saved price alert by ID."""
    raw_alerts = _load_alerts()
    updated = [a for a in raw_alerts if a.get("id") != alert_id]
    if len(updated) == len(raw_alerts):
        raise HTTPException(status_code=404, detail=f"Alert '{alert_id}' not found.")
    _save_alerts(updated)
    return {"deleted": True, "alert_id": alert_id}
