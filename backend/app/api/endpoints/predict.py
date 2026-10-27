"""
Prediction endpoint utilizing trained Scikit-learn model
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends
from app.schemas.price import PredictionRequest, PredictionResponse
from app.ml.predictor import AgriPricePredictor

router = APIRouter()

def get_predictor():
    return AgriPricePredictor()

@router.post("", response_model=PredictionResponse)
def predict_commodity_price(
    request: PredictionRequest,
    predictor: AgriPricePredictor = Depends(get_predictor),
):
    """
    Executes real Scikit-learn regression inference for commodity price prediction.
    Calculates confidence interval bounds and generates farmer advisory.
    """
    try:
        result = predictor.predict(
            commodity=request.commodity,
            market=request.market,
            target_date_str=request.target_date,
            arrival_volume=request.arrival_volume_quintals,
            rainfall_factor=request.rainfall_factor,
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Inference error in AgriPrice Scikit-learn pipeline: {str(e)}",
        )

@router.get("/sample", response_model=PredictionResponse)
def get_sample_prediction(predictor: AgriPricePredictor = Depends(get_predictor)):
    """
    Quick test endpoint returning a live prediction for Tomato in Dindigul (Ottanchatram).
    """
    target = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")
    return predictor.predict(
        commodity="tomato",
        market="dindigul",
        target_date_str=target,
        arrival_volume=650.0,
        rainfall_factor=1.1,
    )
