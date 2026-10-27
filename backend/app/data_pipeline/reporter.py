"""
Data Quality Reporter for AgriPrice AI.
Generates comprehensive JSON and Markdown reports analyzing agricultural price datasets.
"""
import json
from pathlib import Path
from typing import Dict, Any
import pandas as pd

def generate_data_quality_report(
    raw_df: pd.DataFrame,
    cleaned_df: pd.DataFrame,
    source_path: Path,
    is_synthetic: bool,
    duplicate_count: int,
    output_json_path: Path,
    output_md_path: Path,
) -> Dict[str, Any]:
    """
    Computes rigorous dataset quality statistics and saves reports.
    """
    # Date coverage
    dates = pd.to_datetime(cleaned_df["date"], errors="coerce").dropna()
    start_date = str(dates.min().date()) if not dates.empty else "N/A"
    end_date = str(dates.max().date()) if not dates.empty else "N/A"
    total_days = (dates.max() - dates.min()).days if not dates.empty else 0

    # Counts
    raw_row_count = len(raw_df)
    cleaned_row_count = len(cleaned_df)
    unique_commodities = sorted(cleaned_df["commodity"].dropna().unique().tolist())
    unique_markets = sorted(cleaned_df["market"].dropna().unique().tolist())
    unique_districts = sorted(cleaned_df["district"].dropna().unique().tolist())

    # Missing value statistics
    missing_stats = {}
    for col in cleaned_df.columns:
        null_count = int(cleaned_df[col].isna().sum())
        missing_stats[col] = {
            "missing_count": null_count,
            "missing_percentage": round((null_count / cleaned_row_count) * 100.0, 2) if cleaned_row_count > 0 else 0.0,
        }

    # Price validation summary
    modal_prices = cleaned_df["modal_price"].dropna()
    price_stats = {
        "min_rs_per_quintal": float(modal_prices.min()) if not modal_prices.empty else None,
        "max_rs_per_quintal": float(modal_prices.max()) if not modal_prices.empty else None,
        "mean_rs_per_quintal": round(float(modal_prices.mean()), 2) if not modal_prices.empty else None,
        "median_rs_per_quintal": round(float(modal_prices.median()), 2) if not modal_prices.empty else None,
    }

    # Suspicious records breakdown
    suspicious_mask = cleaned_df.get("is_suspicious_record", pd.Series([False] * cleaned_row_count))
    suspicious_count = int(suspicious_mask.sum()) if hasattr(suspicious_mask, "sum") else 0
    suspicious_reasons_breakdown = {}
    if "suspicious_reasons" in cleaned_df.columns:
        for r_list in cleaned_df["suspicious_reasons"].dropna():
            if r_list:
                for reason in str(r_list).split("; "):
                    if reason.strip():
                        suspicious_reasons_breakdown[reason.strip()] = (
                            suspicious_reasons_breakdown.get(reason.strip(), 0) + 1
                        )

    # Unit consistency
    units_detected = cleaned_df["unit"].dropna().unique().tolist() if "unit" in cleaned_df.columns else ["Rs/Quintal"]

    report = {
        "dataset_name": "AgriPrice AI Tamil Nadu Cleaned Market Prices",
        "source": {
            "file_path": str(source_path),
            "is_synthetic_fixture": is_synthetic,
            "source_type_description": (
                "Synthetic Test Fixture (Clearly Labeled - For Pipeline Verification Only)"
                if is_synthetic
                else "Official Raw Agricultural Mandi Transaction Data"
            ),
        },
        "date_coverage": {
            "start_date": start_date,
            "end_date": end_date,
            "total_calendar_days_span": total_days,
        },
        "row_count": {
            "raw_total_rows": raw_row_count,
            "cleaned_tamil_nadu_rows": cleaned_row_count,
            "duplicate_records_detected": duplicate_count,
            "suspicious_records_flagged": suspicious_count,
        },
        "commodity_count": {
            "unique_commodities_count": len(unique_commodities),
            "commodities_list": unique_commodities,
            "records_per_commodity": cleaned_df["commodity"].value_counts().to_dict(),
        },
        "market_count": {
            "unique_markets_count": len(unique_markets),
            "unique_districts_count": len(unique_districts),
            "districts_list": unique_districts,
            "records_per_market": cleaned_df["market"].value_counts().to_dict(),
        },
        "missing_value_statistics": missing_stats,
        "price_target_summary": {
            "target_variable": "modal_price",
            "unit": "Rs/Quintal",
            **price_stats,
        },
        "suspicious_records_summary": {
            "total_flagged_count": suspicious_count,
            "flagged_percentage": round((suspicious_count / cleaned_row_count) * 100.0, 2) if cleaned_row_count > 0 else 0.0,
            "reasons": suspicious_reasons_breakdown,
        },
        "unit_consistency": {
            "standardized_unit": "Rs/Quintal (100 kg)",
            "units_detected_in_raw": units_detected,
            "normalization_applied": "All prices normalized to Rs/Quintal (Ton converted via 0.1x multiplier, Kg converted via 100x multiplier)",
        },
    }

    # Save JSON report
    output_json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    # Generate Markdown report
    md_content = f"""# AgriPrice AI: Data Quality & Cleaning Report

**Generated For**: Tamil Nadu Agricultural Price Prediction Engine  
**Data Source**: `{source_path.name}` ({'⚠️ SYNTHETIC TEST FIXTURE' if is_synthetic else '✅ OFFICIAL RAW DATA'})  
**Prediction Target**: `modal_price` (Standardized in `Rs/Quintal`)

---

## 1. Executive Summary

| Metric | Value |
| :--- | :--- |
| **Data Source Type** | {report['source']['source_type_description']} |
| **Date Coverage** | {start_date} to {end_date} ({total_days} days span) |
| **Raw Input Rows** | {raw_row_count:,} |
| **Cleaned Tamil Nadu Rows** | {cleaned_row_count:,} |
| **Duplicate Rows Detected** | {duplicate_count:,} |
| **Suspicious Records Flagged** | {suspicious_count:,} ({report['suspicious_records_summary']['flagged_percentage']}%) |
| **Unique Commodities** | {len(unique_commodities)} |
| **Unique Regulated Mandis** | {len(unique_markets)} (across {len(unique_districts)} districts) |
| **Standardized Price Unit** | Rs / Quintal (100 kg) |

---

## 2. Missing Value Statistics

| Column Name | Missing Count | Missing % | Status |
| :--- | :---: | :---: | :--- |
"""
    for col, stat in missing_stats.items():
        status = "✅ Clean" if stat["missing_count"] == 0 else "⚠️ Missing Present (Preserved / Derived)"
        md_content += f"| `{col}` | {stat['missing_count']} | {stat['missing_percentage']}% | {status} |\n"

    md_content += f"""
> [!IMPORTANT]
> **Data Integrity Rule**: Missing prices are **NEVER replaced with zero**. Zero values distort regression baselines and ruin log-transforms. Missing modal values with valid min/max were systematically derived via `(min + max) / 2` with explicit audit flags.

---

## 3. Commodity & Market Coverage

### Commodities ({len(unique_commodities)})
{', '.join([f'`{c}`' for c in unique_commodities])}

### Top Markets by Record Volume
"""
    top_mkts = cleaned_df["market"].value_counts().head(8).to_dict()
    for m, cnt in top_mkts.items():
        md_content += f"- **{m}**: {cnt} transactions\n"

    md_content += f"""
---

## 4. Price Validation & Outlier Audit

- **Minimum Modal Price**: ₹{price_stats['min_rs_per_quintal']}/Quintal
- **Median Modal Price**: ₹{price_stats['median_rs_per_quintal']}/Quintal
- **Maximum Modal Price**: ₹{price_stats['max_rs_per_quintal']}/Quintal
- **Average Modal Price**: ₹{price_stats['mean_rs_per_quintal']}/Quintal

> [!NOTE]
> **Market Extremes Policy**: Genuine market spikes (e.g. Tomato surges during monsoon supply disruptions) are **retained** to reflect real market dynamics. Suspicious logic violations (e.g. `min_price > max_price` or non-positive prices) are flagged in `is_suspicious_record` for human or model review without silent data loss.

---
"""
    output_md_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    return report
