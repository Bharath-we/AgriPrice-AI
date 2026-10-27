"""
Synthetic Test Fixture Generator for AgriPrice AI Data Pipeline.
Used ONLY when no official raw dataset is provided.
CRITICAL: Never presented as official data. All records are explicitly labeled.
"""
from pathlib import Path
import pandas as pd

FIXTURES_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "fixtures"
RAW_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "raw"

OFFICIAL_DATA_INSTRUCTIONS = """
================================================================================
OFFICIAL DATASET PLACEMENT INSTRUCTIONS FOR AGRIPRICE AI:
================================================================================
To use your real/official agricultural market data:
1. Obtain historical APMC/mandi transaction data (from Agmarknet / Data.gov.in / APMC e-NAM).
2. Place your raw CSV file(s) into:
   c:\\Users\\user\\Desktop\\Agri-price-AI\\backend\\data\\raw\\
   Example:
   backend/data/raw/tamil_nadu_agmarknet_2023_2026.csv
3. Run the cleaning pipeline:
   python -m app.data_pipeline.cleaner --input backend/data/raw/tamil_nadu_agmarknet_2023_2026.csv
   Or simply execute `python -m app.data_pipeline.cleaner` which automatically scans `backend/data/raw/`.

Supported CSV Column Variations:
- State: 'State', 'State Name', 'state_name'
- District: 'District', 'District Name', 'District_x0020_Name'
- Market: 'Market', 'Market Name', 'Mandi', 'Center'
- Commodity: 'Commodity', 'Commodity Name', 'Crop'
- Variety: 'Variety', 'Grade'
- Date: 'Arrival_Date', 'Date', 'Price Date', 'Reported Date'
- Prices: 'Min Price', 'Max Price', 'Modal Price', 'Min_Price(Rs./Quintal)', etc.
- Arrivals: 'Arrivals', 'Arrival_Quantity', 'Arrivals(Tonnes)'
- Unit: 'Unit', 'Unit of Price'
================================================================================
"""

def generate_synthetic_test_fixture(output_path: Path = None) -> Path:
    """
    Creates a small, clearly labeled test fixture for data pipeline verification.
    Includes edge cases (dirty dates, commas in numbers, unit variances,
    genuine market extremes, and intentional suspicious records for audit testing).
    """
    if output_path is None:
        FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
        output_path = FIXTURES_DIR / "synthetic_test_market_data.csv"
        
    records = [
        # Normal Tamil Nadu records
        {
            "State Name": "Tamil Nadu",
            "District_x0020_Name": "Dindigul",
            "Market": "Ottanchatram",
            "Commodity": "Tomato",
            "Variety": "Hybrid Local",
            "Arrival_Date": "01/10/2026",
            "Min_Price(Rs./Quintal)": "1,800",
            "Max_Price(Rs./Quintal)": "2,400",
            "Modal_Price(Rs./Quintal)": "2,100",
            "Arrival_Quantity": "850.5",
            "Unit": "Rs/Quintal",
            "data_source": "SYNTHETIC_TEST_FIXTURE_NOT_OFFICIAL",
        },
        {
            "State Name": "Tamil Nadu",
            "District_x0020_Name": "Dindigul",
            "Market": "Ottanchatram",
            "Commodity": "Tomato",
            "Variety": "Hybrid Local",
            "Arrival_Date": "02/10/2026",
            "Min_Price(Rs./Quintal)": "1,900",
            "Max_Price(Rs./Quintal)": "2,600",
            "Modal_Price(Rs./Quintal)": "2,250",
            "Arrival_Quantity": "790.0",
            "Unit": "Rs/Quintal",
            "data_source": "SYNTHETIC_TEST_FIXTURE_NOT_OFFICIAL",
        },
        # Genuine market extreme (Heavy NE Monsoon flood disruption in TN -> Tomato jumps to ₹8,500/Qtl)
        # Should NEVER be silently dropped!
        {
            "State Name": "Tamil Nadu",
            "District_x0020_Name": "Dindigul",
            "Market": "Ottanchatram",
            "Commodity": "Tomato",
            "Variety": "Country",
            "Arrival_Date": "15/10/2026",
            "Min_Price(Rs./Quintal)": "7,500",
            "Max_Price(Rs./Quintal)": "9,200",
            "Modal_Price(Rs./Quintal)": "8,500",
            "Arrival_Quantity": "120.0",
            "Unit": "Rs/Quintal",
            "data_source": "SYNTHETIC_TEST_FIXTURE_NOT_OFFICIAL",
        },
        # Shallots (Small Onion) in Perambalur / Dindigul
        {
            "State Name": "Tamil Nadu",
            "District_x0020_Name": "Dindigul",
            "Market": "Ottanchatram",
            "Commodity": "Small Onion",
            "Variety": "Co-4 / Podisu",
            "Arrival_Date": "05-10-2026",
            "Min_Price(Rs./Quintal)": "4,200",
            "Max_Price(Rs./Quintal)": "5,400",
            "Modal_Price(Rs./Quintal)": "4,800",
            "Arrival_Quantity": "420.0",
            "Unit": "Rs/Quintal",
            "data_source": "SYNTHETIC_TEST_FIXTURE_NOT_OFFICIAL",
        },
        # Erode Turmeric (Regulated Market)
        {
            "State Name": "Tamil Nadu",
            "District_x0020_Name": "Erode",
            "Market": "Erode",
            "Commodity": "Turmeric",
            "Variety": "Finger",
            "Arrival_Date": "2026-10-12",
            "Min_Price(Rs./Quintal)": "12,500",
            "Max_Price(Rs./Quintal)": "14,800",
            "Modal_Price(Rs./Quintal)": "13,600",
            "Arrival_Quantity": "350.0",
            "Unit": "Rs/Quintal",
            "data_source": "SYNTHETIC_TEST_FIXTURE_NOT_OFFICIAL",
        },
        # Coimbatore Coconut with Tonnes unit (to test unit normalization)
        {
            "State Name": "Tamil Nadu",
            "District_x0020_Name": "Coimbatore",
            "Market": "Pollachi",
            "Commodity": "Coconut",
            "Variety": "Grade-A",
            "Arrival_Date": "18/10/2026",
            "Min_Price(Rs./Quintal)": "28,000",   # Rs 28,000 per Ton = Rs 2,800 per Quintal
            "Max_Price(Rs./Quintal)": "34,000",
            "Modal_Price(Rs./Quintal)": "31,000",
            "Arrival_Quantity": "15.0",
            "Unit": "Rs/Ton",
            "data_source": "SYNTHETIC_TEST_FIXTURE_NOT_OFFICIAL",
        },
        # Missing modal price (min and max present -> modal should be derived: (2200+2600)/2 = 2400)
        # NEVER replace with zero!
        {
            "State Name": "Tamil Nadu",
            "District_x0020_Name": "Thanjavur",
            "Market": "Thanjavur",
            "Commodity": "Paddy",
            "Variety": "Common / ADT-37",
            "Arrival_Date": "20/10/2026",
            "Min_Price(Rs./Quintal)": "2,200",
            "Max_Price(Rs./Quintal)": "2,600",
            "Modal_Price(Rs./Quintal)": "",       # Empty/Missing! Must NEVER be zeroed
            "Arrival_Quantity": "1200.0",
            "Unit": "Rs/Quintal",
            "data_source": "SYNTHETIC_TEST_FIXTURE_NOT_OFFICIAL",
        },
        # Duplicate record (identical date, market, commodity, variety)
        {
            "State Name": "Tamil Nadu",
            "District_x0020_Name": "Dindigul",
            "Market": "Ottanchatram",
            "Commodity": "Tomato",
            "Variety": "Hybrid Local",
            "Arrival_Date": "01/10/2026",
            "Min_Price(Rs./Quintal)": "1,800",
            "Max_Price(Rs./Quintal)": "2,400",
            "Modal_Price(Rs./Quintal)": "2,100",
            "Arrival_Quantity": "850.5",
            "Unit": "Rs/Quintal",
            "data_source": "SYNTHETIC_TEST_FIXTURE_NOT_OFFICIAL",
        },
        # Suspicious record: Min price > Max price (must be flagged for review, not silently dropped)
        {
            "State Name": "Tamil Nadu",
            "District_x0020_Name": "Madurai",
            "Market": "Paravai",
            "Commodity": "Brinjal",
            "Variety": "Local",
            "Arrival_Date": "22/10/2026",
            "Min_Price(Rs./Quintal)": "4,500",   # Inverted! min > max
            "Max_Price(Rs./Quintal)": "3,200",
            "Modal_Price(Rs./Quintal)": "3,800",
            "Arrival_Quantity": "180.0",
            "Unit": "Rs/Quintal",
            "data_source": "SYNTHETIC_TEST_FIXTURE_NOT_OFFICIAL",
        },
        # Non-Tamil Nadu record (Karnataka -> should be filtered out by TN filter)
        {
            "State Name": "Karnataka",
            "District_x0020_Name": "Kolar",
            "Market": "Kolar APMC",
            "Commodity": "Tomato",
            "Variety": "Local",
            "Arrival_Date": "01/10/2026",
            "Min_Price(Rs./Quintal)": "1,600",
            "Max_Price(Rs./Quintal)": "2,200",
            "Modal_Price(Rs./Quintal)": "1,900",
            "Arrival_Quantity": "1500.0",
            "Unit": "Rs/Quintal",
            "data_source": "SYNTHETIC_TEST_FIXTURE_NOT_OFFICIAL",
        },
    ]
    
    df = pd.DataFrame(records)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    return output_path
