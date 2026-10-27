"""
Unit and integration tests for AgriPrice AI Data-Import & Cleaning Pipeline
"""
import pytest
import numpy as np
import pandas as pd
from pathlib import Path

from app.data_pipeline.cleaner import (
    resolve_column_mapping,
    clean_numeric_price,
    parse_date_safely,
    AgriDataCleaner,
)
from app.data_pipeline.fixtures import generate_synthetic_test_fixture

@pytest.fixture
def test_csv_path(tmp_path):
    """Generates a sample CSV with non-standard column names for testing."""
    fixture_file = tmp_path / "raw_mandi_test.csv"
    data = [
        {
            "State Name": "Tamil Nadu",
            "District_x0020_Name": "Dindigul",
            "Market": "Ottanchatram",
            "Commodity": "Tomato",
            "Arrival_Date": "05/10/2026",
            "Min_Price(Rs./Quintal)": "1,800",
            "Max_Price(Rs./Quintal)": "2,400",
            "Modal_Price(Rs./Quintal)": "2,100",
            "Unit": "Rs/Quintal",
        },
        # High market extreme (Tomato surge during monsoon) - MUST be preserved!
        {
            "State Name": "Tamil Nadu",
            "District_x0020_Name": "Dindigul",
            "Market": "Ottanchatram",
            "Commodity": "Tomato",
            "Arrival_Date": "12-10-2026",
            "Min_Price(Rs./Quintal)": "7,500",
            "Max_Price(Rs./Quintal)": "9,200",
            "Modal_Price(Rs./Quintal)": "8,500",
            "Unit": "Rs/Quintal",
        },
        # Missing modal price - MUST NOT be zeroed!
        {
            "State Name": "Tamil Nadu",
            "District_x0020_Name": "Erode",
            "Market": "Perundurai",
            "Commodity": "Turmeric",
            "Arrival_Date": "2026-10-15",
            "Min_Price(Rs./Quintal)": "12,000",
            "Max_Price(Rs./Quintal)": "14,000",
            "Modal_Price(Rs./Quintal)": "",
            "Unit": "Rs/Quintal",
        },
        # Suspicious record: min > max
        {
            "State Name": "Tamil Nadu",
            "District_x0020_Name": "Madurai",
            "Market": "Paravai",
            "Commodity": "Small Onion",
            "Arrival_Date": "18/10/2026",
            "Min_Price(Rs./Quintal)": "5,500",
            "Max_Price(Rs./Quintal)": "4,000",
            "Modal_Price(Rs./Quintal)": "4,800",
            "Unit": "Rs/Quintal",
        },
        # Non-Tamil Nadu record (Karnataka) - MUST be filtered out
        {
            "State Name": "Karnataka",
            "District_x0020_Name": "Kolar",
            "Market": "Kolar APMC",
            "Commodity": "Tomato",
            "Arrival_Date": "05/10/2026",
            "Min_Price(Rs./Quintal)": "1,500",
            "Max_Price(Rs./Quintal)": "2,000",
            "Modal_Price(Rs./Quintal)": "1,800",
            "Unit": "Rs/Quintal",
        },
        # Ton unit record (testing normalization to Quintal)
        {
            "State Name": "Tamil Nadu",
            "District_x0020_Name": "Coimbatore",
            "Market": "Pollachi",
            "Commodity": "Coconut",
            "Arrival_Date": "20/10/2026",
            "Min_Price(Rs./Quintal)": "30,000",
            "Max_Price(Rs./Quintal)": "36,000",
            "Modal_Price(Rs./Quintal)": "33,000",
            "Unit": "Rs/Ton",
        },
    ]
    pd.DataFrame(data).to_csv(fixture_file, index=False)
    return fixture_file

def test_dynamic_column_resolution():
    """Verify columns with weird Agmarknet formatting are correctly resolved."""
    columns = [
        "State_x0020_Name",
        "District_x0020_Name",
        "Market_x0020_Name",
        "Commodity_x0020_Name",
        "Arrival_Date",
        "Min_x0020_Price",
        "Max_x0020_Price",
        "Modal_x0020_Price",
    ]
    mapping = resolve_column_mapping(columns)
    assert mapping["state"] == "State_x0020_Name"
    assert mapping["district"] == "District_x0020_Name"
    assert mapping["market"] == "Market_x0020_Name"
    assert mapping["commodity"] == "Commodity_x0020_Name"
    assert mapping["date"] == "Arrival_Date"
    assert mapping["min_price"] == "Min_x0020_Price"
    assert mapping["modal_price"] == "Modal_x0020_Price"

def test_clean_numeric_price_never_zeros_missing():
    """Ensure missing price returns np.nan and never 0.0."""
    assert np.isnan(clean_numeric_price(""))
    assert np.isnan(clean_numeric_price(None))
    assert np.isnan(clean_numeric_price("N/A"))
    assert np.isnan(clean_numeric_price("-"))
    # Valid numeric conversion
    assert clean_numeric_price("1,850.50") == 1850.50
    assert clean_numeric_price("₹ 2400") == 2400.0

def test_date_parsing_varieties():
    """Test standardizing different Indian date formats to YYYY-MM-DD."""
    assert parse_date_safely("05/10/2026") == "2026-10-05"
    assert parse_date_safely("05-10-2026") == "2026-10-05"
    assert parse_date_safely("2026-10-05") == "2026-10-05"

def test_cleaning_pipeline_execution(test_csv_path, tmp_path):
    """Test full pipeline on the sample fixture."""
    clean_csv = tmp_path / "cleaned_prices.csv"
    report_json = tmp_path / "report.json"
    report_md = tmp_path / "report.md"

    cleaner = AgriDataCleaner(input_file=test_csv_path)
    df_clean, report = cleaner.run_pipeline(
        output_csv_path=clean_csv,
        output_report_json=report_json,
        output_report_md=report_md,
    )

    # 1. Karnataka record must be filtered out
    states = df_clean["state"].unique().tolist()
    assert "Karnataka" not in states
    assert all("Tamil" in s for s in states)

    # 2. Genuine market extreme (₹8,500 Tomato) must NOT be silently removed
    tomato_prices = df_clean[df_clean["commodity"] == "Tomato"]["modal_price"].tolist()
    assert 8500.0 in tomato_prices

    # 3. Missing modal price in Turmeric must be derived as (12000 + 14000) / 2 = 13000
    turmeric_row = df_clean[df_clean["commodity"] == "Turmeric"].iloc[0]
    assert turmeric_row["modal_price"] == 13000.0
    assert turmeric_row["is_modal_derived"] == True

    # 4. Suspicious record (min > max in Madurai Small Onion) must be flagged, not dropped
    onion_row = df_clean[df_clean["commodity"] == "Small Onion"].iloc[0]
    assert onion_row["is_suspicious_record"] == True
    assert "min_price (5500.0) > max_price (4000.0)" in onion_row["suspicious_reasons"]

    # 5. Unit normalization: Coconut quoted at Rs 33,000/Ton -> 3,300/Quintal
    coconut_row = df_clean[df_clean["commodity"] == "Coconut"].iloc[0]
    assert coconut_row["modal_price"] == 3300.0
    assert coconut_row["unit"] == "Rs/Quintal"

    # 6. Quality report generation
    assert report_json.exists()
    assert report_md.exists()
    assert report["row_count"]["cleaned_tamil_nadu_rows"] == 5
    assert report["commodity_count"]["unique_commodities_count"] == 4
    assert report["price_target_summary"]["target_variable"] == "modal_price"

def test_synthetic_fixture_labeling():
    """Ensure synthetic fixtures are explicitly tagged as synthetic."""
    fixture_path = generate_synthetic_test_fixture()
    df = pd.read_csv(fixture_path)
    assert "data_source" in df.columns
    assert (df["data_source"] == "SYNTHETIC_TEST_FIXTURE_NOT_OFFICIAL").all()
