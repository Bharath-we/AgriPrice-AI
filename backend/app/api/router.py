"""
Central API Router uniting all endpoint modules
"""
from fastapi import APIRouter
from app.api.endpoints import commodities, markets, predict, analytics, compare, profit, alerts

api_router = APIRouter()

api_router.include_router(commodities.router, prefix="/commodities", tags=["Commodities"])
api_router.include_router(markets.router, prefix="/markets", tags=["Markets"])
api_router.include_router(predict.router, prefix="/predict", tags=["Prediction"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(compare.router, prefix="/compare", tags=["Market Comparison"])
api_router.include_router(profit.router, prefix="/profit", tags=["Profit Calculator"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["Price Alerts"])
