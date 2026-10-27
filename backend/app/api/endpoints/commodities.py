"""
Commodities catalog endpoint for Tamil Nadu agricultural produce
"""
from typing import List
from fastapi import APIRouter, HTTPException
from app.schemas.price import CommodityInfo
from app.ml.dataset import COMMODITY_SPECS

router = APIRouter()

COMMODITIES_CATALOG = [
    {
        "id": "tomato",
        "name_en": "Tomato",
        "name_ta": "தக்காளி",
        "category": "Vegetables",
        "typical_msp_per_quintal": None,
        "seasonality": "Year-round, peaks Nov-Jan (NE Monsoon) & May-Jun",
        "unit": "quintal",
        "typical_price_range_per_kg": {"min": 12.0, "modal": 25.0, "max": 75.0},
    },
    {
        "id": "small_onion",
        "name_en": "Small Onion (Shallots)",
        "name_ta": "சின்ன வெங்காயம்",
        "category": "Condiments & Spices",
        "typical_msp_per_quintal": None,
        "seasonality": "Harvest in Feb-Apr; High prices during Sep-Dec",
        "unit": "quintal",
        "typical_price_range_per_kg": {"min": 25.0, "modal": 48.0, "max": 110.0},
    },
    {
        "id": "bellary_onion",
        "name_en": "Bellary Onion",
        "name_ta": "பெல்லாரி வெங்காயம்",
        "category": "Condiments & Spices",
        "typical_msp_per_quintal": None,
        "seasonality": "Inflows from Maharashtra & Karnataka; Peak Nov",
        "unit": "quintal",
        "typical_price_range_per_kg": {"min": 18.0, "modal": 28.0, "max": 65.0},
    },
    {
        "id": "potato",
        "name_en": "Potato (Nilgiris/Mettupalayam)",
        "name_ta": "உருளைக்கிழங்கு",
        "category": "Tubers",
        "typical_msp_per_quintal": None,
        "seasonality": "Autumn Nilgiris harvest; Stable trading in Mettupalayam",
        "unit": "quintal",
        "typical_price_range_per_kg": {"min": 20.0, "modal": 28.0, "max": 45.0},
    },
    {
        "id": "coconut",
        "name_en": "Coconut (Pollachi / Thanjavur)",
        "name_ta": "தேங்காய்",
        "category": "Plantation",
        "typical_msp_per_quintal": 3400.0,
        "seasonality": "Peak copra procurement season Feb-Jul",
        "unit": "quintal",
        "typical_price_range_per_kg": {"min": 24.0, "modal": 33.0, "max": 46.0},
    },
    {
        "id": "banana",
        "name_en": "Banana (Poovan/Nendran)",
        "name_ta": "வாழைப்பழம்",
        "category": "Fruits",
        "typical_msp_per_quintal": None,
        "seasonality": "Highest demand during Tamil festival seasons (Aug-Jan)",
        "unit": "quintal",
        "typical_price_range_per_kg": {"min": 18.0, "modal": 30.0, "max": 55.0},
    },
    {
        "id": "turmeric",
        "name_en": "Turmeric (Erode Finger)",
        "name_ta": "மஞ்சள் (ஈரோடு)",
        "category": "Spices (Commercial)",
        "typical_msp_per_quintal": None,
        "seasonality": "Harvest March-May; Highest trades at Erode Mandi",
        "unit": "quintal",
        "typical_price_range_per_kg": {"min": 95.0, "modal": 138.0, "max": 185.0},
    },
    {
        "id": "paddy",
        "name_en": "Paddy (Common / Delta)",
        "name_ta": "நெல்",
        "category": "Cereals",
        "typical_msp_per_quintal": 2300.0,
        "seasonality": "Kuruvai (Oct-Nov) & Samba (Jan-Feb) harvest",
        "unit": "quintal",
        "typical_price_range_per_kg": {"min": 21.0, "modal": 24.5, "max": 28.0},
    },
    {
        "id": "green_chilli",
        "name_en": "Green Chilli",
        "name_ta": "பச்சை மிளகாய்",
        "category": "Vegetables & Spices",
        "typical_msp_per_quintal": None,
        "seasonality": "High sensitivity to heavy monsoon and viral wilt",
        "unit": "quintal",
        "typical_price_range_per_kg": {"min": 25.0, "modal": 42.0, "max": 85.0},
    },
    {
        "id": "tapioca",
        "name_en": "Tapioca (Cassava - Sago Grade)",
        "name_ta": "மரவள்ளிக்கிழங்கு",
        "category": "Tubers / Industrial",
        "typical_msp_per_quintal": None,
        "seasonality": "Peak factory processing at Salem SAGOSERVE Nov-Feb",
        "unit": "quintal",
        "typical_price_range_per_kg": {"min": 10.0, "modal": 15.0, "max": 22.0},
    },
]

@router.get("", response_model=List[CommodityInfo])
def list_commodities():
    """
    Returns the catalogue of Tamil Nadu agricultural commodities.
    """
    return COMMODITIES_CATALOG

@router.get("/{commodity_id}", response_model=CommodityInfo)
def get_commodity_detail(commodity_id: str):
    """
    Returns specific commodity metadata.
    """
    for comm in COMMODITIES_CATALOG:
        if comm["id"] == commodity_id:
            return comm
    raise HTTPException(status_code=404, detail=f"Commodity '{commodity_id}' not found.")
