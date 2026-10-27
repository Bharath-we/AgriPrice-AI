"""
Profit Calculator Endpoint for AgriPrice AI.
Calculates gross revenue, transport, loading, commission, optional wastage,
storage costs, and net farmer revenue based on real market prices.

All calculations are transparent with documented assumptions.
Advisory reflects forecast uncertainty and perishability constraints.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.price import ProfitCalculationRequest, ProfitCalculationResponse
from app.ml.predictor import AgriPricePredictor
from app.ml.dataset import COMMODITY_SPECS, MARKET_SPECS

router = APIRouter()


def get_predictor() -> AgriPricePredictor:
    return AgriPricePredictor()


def _build_profit_advisory(
    gross_revenue: float,
    net_farmer_profit: float,
    profit_margin_pct: float,
    is_perishable: bool,
    holding_days: int,
    commodity_name_en: str,
    commodity_name_ta: str,
    price_source_date: str,
) -> tuple[str, str]:
    """Build a bilingual advisory based on calculated figures and documented assumptions."""
    if profit_margin_pct >= 30:
        outlook_en = "strong positive return"
        outlook_ta = "நல்ல லாபம்"
    elif profit_margin_pct >= 10:
        outlook_en = "moderate return"
        outlook_ta = "மிதமான லாபம்"
    elif profit_margin_pct >= 0:
        outlook_en = "marginal return (near break-even)"
        outlook_ta = "சிறிய லாபம் (செலவை ஈடுகட்டும்)"
    else:
        outlook_en = "net loss — costs exceed revenues"
        outlook_ta = "நஷ்டம் — செலவு வருமானத்தை மீறுகிறது"

    perishability_note_en = ""
    perishability_note_ta = ""
    if is_perishable and holding_days > 5:
        max_days = COMMODITY_SPECS.get(commodity_name_en.lower().split("(")[0].strip(), {}).get("max_safe_holding_days", 5)
        perishability_note_en = (
            f" WARNING: {commodity_name_en} is a perishable crop with a safe holding limit of "
            f"~{max_days} days without cold-chain storage. Holding for {holding_days} days "
            f"carries a significant risk of post-harvest quality loss."
        )
        perishability_note_ta = (
            f" எச்சரிக்கை: {commodity_name_ta} ஒரு அழுகும் பொருள். குளிர் சேமிப்பு இல்லாமல் "
            f"~{max_days} நாட்களுக்கு மேல் வைத்திருப்பது அழிவு ஏற்படுத்தலாம்."
        )

    advisory_en = (
        f"Based on the modal price observed on {price_source_date} and your entered inputs, "
        f"this harvest yields a {outlook_en} with an estimated net profit of "
        f"₹{net_farmer_profit:,.0f} at a {profit_margin_pct:.1f}% margin.{perishability_note_en} "
        f"This is a decision-support estimate — actual mandi realisation may vary. "
        f"Negotiate commission rates where possible and verify transport costs before routing."
    )

    advisory_ta = (
        f"{price_source_date} அன்று பதிவு செய்யப்பட்ட மாடல் விலை மற்றும் உங்கள் உள்ளீடுகளின் படி, "
        f"இந்த அறுவடையில் {outlook_ta} எதிர்பார்க்கலாம். "
        f"மதிப்பிடப்பட்ட நிகர லாபம் ₹{net_farmer_profit:,.0f} ({profit_margin_pct:.1f}% வருமானம்).{perishability_note_ta} "
        f"இது ஒரு கணிப்பு மட்டுமே — உண்மையான மண்டி விலை மாறுபடலாம்."
    )

    return advisory_en, advisory_ta


@router.post("", response_model=ProfitCalculationResponse)
def calculate_profit(
    req: ProfitCalculationRequest,
    predictor: AgriPricePredictor = Depends(get_predictor),
):
    """
    Calculates gross revenue, transport expenses, loading costs, mandi commission,
    optional wastage, storage costs, and estimated net farmer revenue.

    - Uses the latest real observed modal price from the market dataset.
    - If an override unit_price_per_kg is provided, it is used instead (clearly flagged).
    - Never uses zero for missing prices; raises an error if no price is available.
    - All assumptions are returned transparently.
    """
    commodity = req.commodity.lower().strip()
    market = req.market.lower().strip()

    if commodity not in COMMODITY_SPECS:
        raise HTTPException(status_code=404, detail=f"Commodity '{commodity}' not found.")
    if market not in MARKET_SPECS:
        raise HTTPException(status_code=404, detail=f"Market '{market}' not found.")

    comm_spec = COMMODITY_SPECS[commodity]
    mkt_spec = MARKET_SPECS[market]

    # Resolve price: override or real market observation
    price_source_date = ""
    price_type = ""

    if req.unit_price_per_kg is not None:
        price_per_kg = req.unit_price_per_kg
        price_per_quintal = price_per_kg * 100.0
        price_source_date = "User-Provided Override"
        price_type = "User-entered price (not verified market data)"
    else:
        df = predictor.df
        subset = df[(df["commodity"] == commodity) & (df["market"] == market)].sort_values("date")
        if subset.empty:
            # Fall back to any market with data for this commodity
            subset = df[df["commodity"] == commodity].sort_values("date")

        if subset.empty:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"No price records found for '{commodity}'. "
                    "Please provide an override unit_price_per_kg or import the dataset."
                ),
            )

        last_row = subset.iloc[-1]
        price_per_quintal = float(last_row["modal_price_rs_per_quintal"])
        if price_per_quintal <= 0:
            raise HTTPException(
                status_code=422,
                detail="Latest recorded modal price is zero or negative. Cannot compute revenue.",
            )
        price_per_kg = price_per_quintal / 100.0
        price_source_date = last_row["date"].strftime("%Y-%m-%d")
        price_type = "Latest observed modal price (APMC mandi record)"

    # Perishability check
    is_perishable = comm_spec.get("perishable", False)
    max_safe_days = comm_spec.get("max_safe_holding_days", 30)
    perishability_warning = None
    if is_perishable and req.holding_days > max_safe_days:
        perishability_warning = (
            f"{comm_spec['name_en']} has a maximum safe holding period of ~{max_safe_days} days "
            f"without cold-chain storage. You have entered {req.holding_days} days, which exceeds "
            f"safe limits and may result in significant post-harvest losses."
        )

    # ── Revenue Calculations ────────────────────────────────────────────────
    # Wastage reduction
    wastage_loss_q = req.quantity_quintals * (req.wastage_percent / 100.0)
    salable_q = req.quantity_quintals - wastage_loss_q
    salable_kg = salable_q * 100.0
    total_volume_kg = req.quantity_quintals * 100.0

    gross_revenue = round(salable_kg * price_per_kg, 2)

    # Expenses
    transport_expenses = round(req.quantity_quintals * req.transport_cost_per_quintal, 2)
    loading_expenses = round(req.quantity_quintals * req.loading_cost_per_quintal, 2)
    mandi_commission = round((gross_revenue * req.commission_percent) / 100.0, 2)

    # Storage cost: per quintal per week, pro-rated for holding_days
    weeks_holding = req.holding_days / 7.0
    storage_expenses = round(req.quantity_quintals * weeks_holding * req.storage_cost_per_quintal_week, 2)

    total_marketing_expenses = round(transport_expenses + loading_expenses + mandi_commission + storage_expenses, 2)
    estimated_net_revenue = round(gross_revenue - total_marketing_expenses, 2)

    # Farmer profit after cultivation cost
    net_farmer_profit = round(estimated_net_revenue - req.cultivation_cost_total, 2)

    # Profit margin on gross revenue (avoids div-by-zero)
    profit_margin_pct = round((net_farmer_profit / max(gross_revenue, 1.0)) * 100.0, 2)

    advisory_en, advisory_ta = _build_profit_advisory(
        gross_revenue=gross_revenue,
        net_farmer_profit=net_farmer_profit,
        profit_margin_pct=profit_margin_pct,
        is_perishable=is_perishable,
        holding_days=req.holding_days,
        commodity_name_en=comm_spec["name_en"],
        commodity_name_ta=comm_spec["name_ta"],
        price_source_date=price_source_date,
    )

    return ProfitCalculationResponse(
        commodity=commodity,
        commodity_name_en=comm_spec["name_en"],
        commodity_name_ta=comm_spec["name_ta"],
        market=market,
        market_name_en=mkt_spec["name_en"],
        quantity_quintals=req.quantity_quintals,
        total_volume_kg=round(total_volume_kg, 2),
        wastage_percent=req.wastage_percent,
        wastage_loss_quintals=round(wastage_loss_q, 3),
        salable_quantity_quintals=round(salable_q, 3),
        salable_quantity_kg=round(salable_kg, 2),
        applied_modal_price_per_kg=round(price_per_kg, 2),
        applied_modal_price_per_quintal=round(price_per_quintal, 2),
        price_source_date=price_source_date,
        price_type=price_type,
        gross_revenue=gross_revenue,
        transport_expenses=transport_expenses,
        loading_expenses=loading_expenses,
        mandi_commission_fee=mandi_commission,
        storage_expenses=storage_expenses,
        total_marketing_expenses=total_marketing_expenses,
        estimated_net_revenue=estimated_net_revenue,
        cultivation_cost_total=req.cultivation_cost_total,
        net_farmer_profit=net_farmer_profit,
        profit_margin_pct=profit_margin_pct,
        holding_days=req.holding_days,
        is_perishable=is_perishable,
        perishability_warning=perishability_warning,
        advisory_en=advisory_en,
        advisory_ta=advisory_ta,
        assumptions=[
            f"Price source: {price_type} as of {price_source_date}.",
            f"Wastage of {req.wastage_percent}% reduces gross salable quantity.",
            f"Mandi commission of {req.commission_percent}% applied to gross revenue.",
            f"Storage cost of ₹{req.storage_cost_per_quintal_week}/quintal/week for {req.holding_days} days.",
            "All monetary values are in Indian Rupees (₹).",
            "Transport and loading costs are user-entered estimates.",
        ],
        forecast_limitations=(
            "Net revenue is estimated based on the latest recorded modal price and user-entered costs. "
            "Actual mandi realisation depends on produce quality, auction dynamics, and daily arrivals. "
            "The calculator does not account for price movement during the holding period. "
            "Use the Price Prediction page to estimate future prices before making holding decisions."
        ),
    )
