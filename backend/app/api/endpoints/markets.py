"""
Markets endpoint for major Tamil Nadu APMC / regulated mandis
"""
from typing import List
from fastapi import APIRouter
from app.schemas.price import MarketInfo

router = APIRouter()

MARKETS_CATALOG = [
    {
        "id": "coimbatore",
        "district": "Coimbatore",
        "market_name": "Coimbatore MGR Mandi & Pollachi APMC",
        "market_name_ta": "கோயம்புத்தூர் எம்.ஜி.ஆர் மார்க்கெட் & பொள்ளாச்சி",
        "market_type": "Major Wholesale & Copra Mandi",
    },
    {
        "id": "dindigul",
        "district": "Dindigul",
        "market_name": "Ottanchatram Vegetable Market",
        "market_name_ta": "ஒட்டன்சத்திரம் காய்கறி சந்தை (திண்டுக்கல்)",
        "market_type": "Primary South India Vegetable & Shallot Hub",
    },
    {
        "id": "madurai",
        "district": "Madurai",
        "market_name": "Madurai Paravai Central Market",
        "market_name_ta": "மதுரை பரவை மத்திய சந்தை",
        "market_type": "Regional Vegetable & Fruit Terminal",
    },
    {
        "id": "salem",
        "district": "Salem",
        "market_name": "Salem Shevapet & SAGOSERVE Tapioca Mandi",
        "market_name_ta": "சேலம் செவ்வாய்பேட்டை & சாகோசர்வ் சந்தை",
        "market_type": "Tapioca & Agro Commodity Market",
    },
    {
        "id": "tiruchirappalli",
        "district": "Tiruchirappalli",
        "market_name": "Trichy Gandhi Market & Banana Mandi",
        "market_name_ta": "திருச்சி காந்தி மார்க்கெட் & வாழை சந்தை",
        "market_type": "Central Tamil Nadu Distribution Hub",
    },
    {
        "id": "erode",
        "district": "Erode",
        "market_name": "Erode Regulated Market (Semmampalayam & Perundurai)",
        "market_name_ta": "ஈரோடு ஒழுங்குமுறை விற்பனைக்கூடம்",
        "market_type": "Turmeric GI Hub & Spices Mandi",
    },
    {
        "id": "tirunelveli",
        "district": "Tirunelveli",
        "market_name": "Tirunelveli Nainarkulam Vegetable Market",
        "market_name_ta": "திருநெல்வேலி நயினார்குளம் சந்தை",
        "market_type": "Southern District Regulated Market",
    },
    {
        "id": "thanjavur",
        "district": "Thanjavur",
        "market_name": "Thanjavur Delta Paddy Regulated Market",
        "market_name_ta": "தஞ்சாவூர் டெல்டா நெல் ஒழுங்குமுறை விற்பனைக்கூடம்",
        "market_type": "Cauvery Delta Grain & Paddy APMC",
    },
    {
        "id": "vellore",
        "district": "Vellore",
        "market_name": "Vellore Nethaji Vegetable Market",
        "market_name_ta": "வேலூர் நேதாஜி காய்கறி சந்தை",
        "market_type": "Northern District Transit Hub",
    },
    {
        "id": "chennai",
        "district": "Chennai",
        "market_name": "Koyambedu Wholesale APMC Market Complex",
        "market_name_ta": "சென்னை கோயம்பேடு மொத்த விற்பனை வளாகம்",
        "market_type": "Apex Consumer Wholesale APMC",
    },
]

@router.get("", response_model=List[MarketInfo])
def list_markets():
    """
    Returns the list of Tamil Nadu agricultural markets.
    """
    return MARKETS_CATALOG
