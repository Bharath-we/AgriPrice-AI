"""
Robust Data-Import & Cleaning Pipeline for AgriPrice AI.
Standardizes, validates, filters, and audits agricultural market price datasets
for Tamil Nadu, India.
"""
import re
import argparse
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any

from app.data_pipeline.fixtures import (
    RAW_DIR,
    OFFICIAL_DATA_INSTRUCTIONS,
    generate_synthetic_test_fixture,
)
from app.data_pipeline.reporter import generate_data_quality_report

# Output paths
DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
OUTPUT_CLEAN_CSV = DATA_DIR / "tamilnadu_prices.csv"
OUTPUT_REPORT_JSON = DATA_DIR / "data_quality_report.json"
OUTPUT_REPORT_MD = DATA_DIR / "data_quality_report.md"

# Canonical schema dictionary of regex/synonyms for flexible header resolution
COLUMN_SYNONYMS = {
    "state": [
        r"^state$", r"^state[_\s]?name$", r"^state[_\s]?x0020[_\s]?name$",
        r"^state[_\s/]?ut$", r"^state[_\s]?code$"
    ],
    "district": [
        r"^district$", r"^district[_\s]?name$", r"^district[_\s]?x0020[_\s]?name$",
        r"^dist[_\s]?name$", r"^district[_\s/]?market$"
    ],
    "market": [
        r"^market$", r"^market[_\s]?name$", r"^market[_\s]?x0020[_\s]?name$",
        r"^mandi$", r"^center$", r"^market[_\s]?center$", r"^apmc$"
    ],
    "commodity": [
        r"^commodity$", r"^commodity[_\s]?name$", r"^commodity[_\s]?x0020[_\s]?name$",
        r"^crop$", r"^produce$", r"^item$"
    ],
    "variety": [
        r"^variety$", r"^variety[_\s]?name$", r"^variety[_\s]?x0020[_\s]?name$",
        r"^grade$", r"^quality$"
    ],
    "date": [
        r"^arrival[_\s]?date$", r"^date$", r"^price[_\s]?date$",
        r"^reported[_\s]?date$", r"^txn[_\s]?date$", r"^transaction[_\s]?date$"
    ],
    "min_price": [
        r"^min[_\s]?price", r"^min[_\s]?x0020[_\s]?price", r"^minimum[_\s]?price",
        r"^minprice", r"^min$"
    ],
    "max_price": [
        r"^max[_\s]?price", r"^max[_\s]?x0020[_\s]?price", r"^maximum[_\s]?price",
        r"^maxprice", r"^max$"
    ],
    "modal_price": [
        r"^modal[_\s]?price", r"^modal[_\s]?x0020[_\s]?price", r"^modalprice",
        r"^modal$", r"^average[_\s]?price", r"^avg[_\s]?price"
    ],
    "arrivals": [
        r"^arrival[_\s]?quantity", r"^arrival[_\s]?x0020[_\s]?quantity",
        r"^arrivals", r"^arrivals[_\s(]?tonnes[_\s)]?", r"^arrivals[_\s(]?quintals[_\s)]?",
        r"^volume$"
    ],
    "unit": [
        r"^unit$", r"^unit[_\s]?of[_\s]?price$", r"^price[_\s]?unit$", r"^units$"
    ],
}

KNOWN_TN_DISTRICTS = {
    "ariyalur", "chengalpattu", "chennai", "coimbatore", "cuddalore",
    "dharmapuri", "dindigul", "erode", "kallakurichi", "kanchipuram",
    "kanyakumari", "karur", "krishnagiri", "madurai", "mayiladuthurai",
    "nagapattinam", "namakkal", "nilgiris", "perambalur", "pudukkottai",
    "ramanathapuram", "ranipet", "salem", "sivaganga", "tenkasi",
    "thanjavur", "theni", "thoothukudi", "tiruchirappalli", "tirunelveli",
    "tirupathur", "tiruppur", "tiruvallur", "tiruvannamalai", "tiruvarur",
    "vellore", "viluppuram", "virudhunagar"
}

def normalize_text(text: str) -> str:
    """Removes special formatting characters and extra whitespace."""
    if pd.isna(text):
        return ""
    return str(text).strip()

def resolve_column_mapping(columns: List[str]) -> Dict[str, str]:
    """
    Dynamically maps raw CSV column names to canonical schema without hardcoding.
    Returns: dict mapping canonical_key -> actual_csv_column_name
    """
    mapping = {}
    cleaned_col_map = {col: re.sub(r"[^\w]", "_", str(col).strip().lower()) for col in columns}

    for canonical, patterns in COLUMN_SYNONYMS.items():
        matched_col = None
        for pattern in patterns:
            for original_col, clean_col in cleaned_col_map.items():
                if re.search(pattern, clean_col):
                    matched_col = original_col
                    break
            if matched_col:
                break
        if matched_col:
            mapping[canonical] = matched_col

    # Verify essential columns are resolved
    essential = ["commodity", "date"]
    missing_essential = [c for c in essential if c not in mapping]
    if missing_essential:
        raise ValueError(
            f"Unable to resolve essential column(s) {missing_essential} in dataset.\n"
            f"Detected columns in CSV: {list(columns)}"
        )
    return mapping

def clean_numeric_price(val: Any) -> Optional[float]:
    """
    Cleans strings like '1,800', '₹ 2400', ' 3,250.00 ' to float.
    Never returns 0.0 for missing values; returns np.nan.
    """
    if pd.isna(val) or val is None or val == "":
        return np.nan
    s = str(val).strip()
    if s.lower() in ["nan", "null", "none", "-", "n/a", "nil", ""]:
        return np.nan
    # Remove currency symbols, commas, and trailing characters
    s_cleaned = re.sub(r"[^\d.]", "", s)
    if not s_cleaned:
        return np.nan
    try:
        f = float(s_cleaned)
        return f
    except ValueError:
        return np.nan

def parse_date_safely(val: Any) -> Optional[str]:
    """
    Parses varied date representations and returns ISO YYYY-MM-DD format.
    """
    if pd.isna(val) or val is None or str(val).strip() == "":
        return None
    s = str(val).strip()
    formats = [
        "%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%d-%b-%Y",
        "%d-%b-%y", "%d/%m/%y", "%Y/%m/%d", "%d.%m.%Y"
    ]
    for fmt in formats:
        try:
            return pd.to_datetime(s, format=fmt).strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            continue
    # Fallback to general parser with dayfirst=True
    try:
        parsed = pd.to_datetime(s, dayfirst=True, errors="coerce")
        if pd.notna(parsed):
            return parsed.strftime("%Y-%m-%d")
    except Exception:
        pass
    return None

class AgriDataCleaner:
    def __init__(
        self,
        input_file: Optional[Union[str, Path]] = None,
        commodities_filter: Optional[List[str]] = None,
        districts_filter: Optional[List[str]] = None,
        markets_filter: Optional[List[str]] = None,
    ):
        self.input_file = Path(input_file) if input_file else None
        self.commodities_filter = [c.lower().strip() for c in commodities_filter] if commodities_filter else None
        self.districts_filter = [d.lower().strip() for d in districts_filter] if districts_filter else None
        self.markets_filter = [m.lower().strip() for m in markets_filter] if markets_filter else None
        self.is_synthetic = False

    def locate_source_file(self) -> Path:
        """
        Locates the dataset to process.
        If user specified a path, verifies existence.
        Otherwise scans backend/data/raw/ for official CSV files.
        If none found, creates and uses a clearly labeled synthetic test fixture.
        """
        if self.input_file and self.input_file.exists():
            print(f"[Data Cleaner] Using provided source file: {self.input_file}")
            return self.input_file

        RAW_DIR.mkdir(parents=True, exist_ok=True)
        raw_csvs = list(RAW_DIR.glob("*.csv"))
        if raw_csvs:
            chosen = raw_csvs[0]
            print(f"[Data Cleaner] Found official raw dataset in {RAW_DIR}: {chosen.name}")
            return chosen

        # No official source found -> Provide clear instructions and create synthetic test fixture
        print(OFFICIAL_DATA_INSTRUCTIONS)
        print("[Data Cleaner] Generating clearly labeled SYNTHETIC TEST FIXTURE for pipeline verification...")
        self.is_synthetic = True
        fixture_path = generate_synthetic_test_fixture()
        return fixture_path

    def run_pipeline(
        self,
        output_csv_path: Path = OUTPUT_CLEAN_CSV,
        output_report_json: Path = OUTPUT_REPORT_JSON,
        output_report_md: Path = OUTPUT_REPORT_MD,
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Executes the end-to-end data import, cleaning, filtering, and audit pipeline.
        """
        source_path = self.locate_source_file()
        print(f"[Data Cleaner] Reading raw file from: {source_path}")
        raw_df = pd.read_csv(source_path)
        print(f"[Data Cleaner] Raw row count: {len(raw_df)} | Raw columns: {list(raw_df.columns)}")

        # Step 1: Inspect actual CSV columns dynamically
        col_map = resolve_column_mapping(raw_df.columns.tolist())
        print(f"[Data Cleaner] Resolved column mapping: {col_map}")

        # Check if the dataset itself is labeled as synthetic
        if "data_source" in raw_df.columns:
            has_synthetic_label = (raw_df["data_source"] == "SYNTHETIC_TEST_FIXTURE_NOT_OFFICIAL").any()
            if has_synthetic_label:
                self.is_synthetic = True

        # Build working standardized DataFrame
        df = pd.DataFrame()
        for canonical, raw_col in col_map.items():
            df[canonical] = raw_df[raw_col]

        # Ensure mandatory columns exist even if absent in raw
        if "state" not in df.columns:
            df["state"] = "Tamil Nadu"
        if "district" not in df.columns:
            df["district"] = df["market"] if "market" in df.columns else "Tamil Nadu Center"
        if "market" not in df.columns:
            df["market"] = df["district"]
        if "variety" not in df.columns:
            df["variety"] = "Common"
        if "unit" not in df.columns:
            df["unit"] = "Rs/Quintal"
        if "arrivals" not in df.columns:
            df["arrivals"] = np.nan

        # Step 2: Filter for Tamil Nadu
        # Match case-insensitive state name or check if district belongs to Tamil Nadu
        state_col = df["state"].astype(str).str.strip().str.lower()
        district_col = df["district"].astype(str).str.strip().str.lower()

        tn_mask = (
            state_col.str.contains("tamil", na=False) |
            (state_col == "tn") |
            district_col.isin(KNOWN_TN_DISTRICTS)
        )
        df_tn = df[tn_mask].copy()
        print(f"[Data Cleaner] Filtered to Tamil Nadu records: {len(df_tn)} rows remaining (from {len(df)})")

        if df_tn.empty:
            raise ValueError(
                f"No Tamil Nadu records found in {source_path}. "
                "Ensure State column includes 'Tamil Nadu' or District is a recognized Tamil Nadu market."
            )

        # Optional user filters
        if self.commodities_filter:
            df_tn = df_tn[df_tn["commodity"].astype(str).str.strip().str.lower().isin(self.commodities_filter)]
        if self.districts_filter:
            df_tn = df_tn[df_tn["district"].astype(str).str.strip().str.lower().isin(self.districts_filter)]
        if self.markets_filter:
            df_tn = df_tn[df_tn["market"].astype(str).str.strip().str.lower().isin(self.markets_filter)]

        # Step 3: Standardize Text Fields
        for text_col in ["state", "district", "market", "commodity", "variety"]:
            df_tn[text_col] = df_tn[text_col].astype(str).str.strip().str.title()

        # Step 4: Parse Dates
        df_tn["date"] = df_tn["date"].apply(parse_date_safely)

        # Step 5: Clean and Validate Numeric Prices
        for p_col in ["min_price", "max_price", "modal_price"]:
            if p_col in df_tn.columns:
                df_tn[p_col] = df_tn[p_col].apply(clean_numeric_price)
            else:
                df_tn[p_col] = np.nan

        # Clean arrivals
        df_tn["arrivals"] = df_tn["arrivals"].apply(clean_numeric_price)

        # Step 6: Check Unit Consistency and Normalize
        # Normalizes to Rs/Quintal (1 Quintal = 100 kg = 0.1 Ton)
        unit_series = df_tn["unit"].astype(str).str.lower().str.strip()
        for idx in df_tn.index:
            u = unit_series[idx]
            if "ton" in u:
                # 1 Ton = 10 Quintals -> Price per Quintal = Price per Ton * 0.1
                for p_col in ["min_price", "max_price", "modal_price"]:
                    if pd.notna(df_tn.at[idx, p_col]):
                        df_tn.at[idx, p_col] = round(df_tn.at[idx, p_col] * 0.1, 2)
            elif "kg" in u:
                # 1 Quintal = 100 kg -> Price per Quintal = Price per Kg * 100
                for p_col in ["min_price", "max_price", "modal_price"]:
                    if pd.notna(df_tn.at[idx, p_col]):
                        df_tn.at[idx, p_col] = round(df_tn.at[idx, p_col] * 100.0, 2)
        df_tn["unit"] = "Rs/Quintal"

        # Step 7: Handle Missing Values & Derive Modal Price (Never zero!)
        # "Use modal price as the default prediction target when available."
        # If modal price is missing but min and max exist, derive (min + max) / 2
        df_tn["is_modal_derived"] = False
        for idx in df_tn.index:
            modal = df_tn.at[idx, "modal_price"]
            min_p = df_tn.at[idx, "min_price"]
            max_p = df_tn.at[idx, "max_price"]

            if pd.isna(modal) or modal is None:
                if pd.notna(min_p) and pd.notna(max_p):
                    df_tn.at[idx, "modal_price"] = round((min_p + max_p) / 2.0, 2)
                    df_tn.at[idx, "is_modal_derived"] = True
                elif pd.notna(min_p):
                    df_tn.at[idx, "modal_price"] = min_p
                    df_tn.at[idx, "is_modal_derived"] = True
                elif pd.notna(max_p):
                    df_tn.at[idx, "modal_price"] = max_p
                    df_tn.at[idx, "is_modal_derived"] = True
                # If all are missing, it remains np.nan! NEVER replace with 0.

        # Step 8: Flag Suspicious Price Records for Review
        # "Never replace missing prices with zero and never silently remove genuine market extremes."
        df_tn["is_suspicious_record"] = False
        df_tn["suspicious_reasons"] = ""

        for idx in df_tn.index:
            reasons = []
            min_p = df_tn.at[idx, "min_price"]
            max_p = df_tn.at[idx, "max_price"]
            modal = df_tn.at[idx, "modal_price"]

            # Suspicious 1: Non-positive price
            for p, name in [(min_p, "min_price"), (max_p, "max_price"), (modal, "modal_price")]:
                if pd.notna(p) and p <= 0:
                    reasons.append(f"{name} <= 0 ({p})")

            # Suspicious 2: Min price > Max price
            if pd.notna(min_p) and pd.notna(max_p) and min_p > max_p:
                reasons.append(f"min_price ({min_p}) > max_price ({max_p})")

            # Suspicious 3: Modal price outside [min, max] by more than 10% tolerance
            if pd.notna(min_p) and pd.notna(modal) and modal < (min_p * 0.90):
                reasons.append(f"modal_price ({modal}) significantly below min_price ({min_p})")
            if pd.notna(max_p) and pd.notna(modal) and modal > (max_p * 1.10):
                reasons.append(f"modal_price ({modal}) significantly above max_price ({max_p})")

            if reasons:
                df_tn.at[idx, "is_suspicious_record"] = True
                df_tn.at[idx, "suspicious_reasons"] = "; ".join(reasons)

        # Step 9: Identify Duplicates
        duplicate_subset = ["date", "commodity", "district", "market", "variety"]
        valid_cols = [c for c in duplicate_subset if c in df_tn.columns]
        duplicates_mask = df_tn.duplicated(subset=valid_cols, keep="first")
        duplicate_count = int(duplicates_mask.sum())
        print(f"[Data Cleaner] Identified {duplicate_count} duplicate records. Deduplicating...")
        df_cleaned = df_tn[~duplicates_mask].copy()

        # Step 10: Tag Synthetic Status Clearly
        df_cleaned["is_synthetic"] = self.is_synthetic
        df_cleaned["data_source"] = (
            "SYNTHETIC_TEST_FIXTURE_NOT_OFFICIAL" if self.is_synthetic else "OFFICIAL_TAMIL_NADU_APMC_DATA"
        )

        # Sort cleanly by Date, Commodity, District
        df_cleaned = df_cleaned.sort_values(by=["date", "commodity", "district"], ascending=True).reset_index(drop=True)

        # Step 11: Save Cleaned Dataset
        output_csv_path.parent.mkdir(parents=True, exist_ok=True)
        df_cleaned.to_csv(output_csv_path, index=False)
        print(f"[Data Cleaner] Cleaned dataset saved to: {output_csv_path}")
        print(f"[Data Cleaner] Total rows: {len(df_cleaned)}")

        # Step 12: Generate Data Quality Report
        report = generate_data_quality_report(
            raw_df=raw_df,
            cleaned_df=df_cleaned,
            source_path=source_path,
            is_synthetic=self.is_synthetic,
            duplicate_count=duplicate_count,
            output_json_path=output_report_json,
            output_md_path=output_report_md,
        )
        print(f"[Data Cleaner] Data quality reports generated at:")
        print(f"  - JSON: {output_report_json}")
        print(f"  - Markdown: {output_report_md}")

        return df_cleaned, report

def main():
    parser = argparse.ArgumentParser(description="AgriPrice AI Data Import & Cleaning Pipeline")
    parser.add_argument("--input", type=str, default=None, help="Path to raw agricultural CSV file")
    parser.add_argument("--commodity", type=str, nargs="*", default=None, help="Filter by specific commodity/commodities")
    parser.add_argument("--district", type=str, nargs="*", default=None, help="Filter by specific district(s)")
    parser.add_argument("--market", type=str, nargs="*", default=None, help="Filter by specific market(s)")
    args = parser.parse_args()

    cleaner = AgriDataCleaner(
        input_file=args.input,
        commodities_filter=args.commodity,
        districts_filter=args.district,
        markets_filter=args.market,
    )
    cleaner.run_pipeline()

if __name__ == "__main__":
    main()
