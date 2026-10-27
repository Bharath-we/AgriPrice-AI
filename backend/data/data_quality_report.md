# AgriPrice AI: Data Quality & Cleaning Report

**Generated For**: Tamil Nadu Agricultural Price Prediction Engine  
**Data Source**: `synthetic_test_market_data.csv` (⚠️ SYNTHETIC TEST FIXTURE)  
**Prediction Target**: `modal_price` (Standardized in `Rs/Quintal`)

---

## 1. Executive Summary

| Metric | Value |
| :--- | :--- |
| **Data Source Type** | Synthetic Test Fixture (Clearly Labeled - For Pipeline Verification Only) |
| **Date Coverage** | 2026-10-01 to 2026-10-22 (21 days span) |
| **Raw Input Rows** | 10 |
| **Cleaned Tamil Nadu Rows** | 8 |
| **Duplicate Rows Detected** | 1 |
| **Suspicious Records Flagged** | 1 (12.5%) |
| **Unique Commodities** | 6 |
| **Unique Regulated Mandis** | 5 (across 5 districts) |
| **Standardized Price Unit** | Rs / Quintal (100 kg) |

---

## 2. Missing Value Statistics

| Column Name | Missing Count | Missing % | Status |
| :--- | :---: | :---: | :--- |
| `state` | 0 | 0.0% | ✅ Clean |
| `district` | 0 | 0.0% | ✅ Clean |
| `market` | 0 | 0.0% | ✅ Clean |
| `commodity` | 0 | 0.0% | ✅ Clean |
| `variety` | 0 | 0.0% | ✅ Clean |
| `date` | 0 | 0.0% | ✅ Clean |
| `min_price` | 0 | 0.0% | ✅ Clean |
| `max_price` | 0 | 0.0% | ✅ Clean |
| `modal_price` | 0 | 0.0% | ✅ Clean |
| `arrivals` | 0 | 0.0% | ✅ Clean |
| `unit` | 0 | 0.0% | ✅ Clean |
| `is_modal_derived` | 0 | 0.0% | ✅ Clean |
| `is_suspicious_record` | 0 | 0.0% | ✅ Clean |
| `suspicious_reasons` | 0 | 0.0% | ✅ Clean |
| `is_synthetic` | 0 | 0.0% | ✅ Clean |
| `data_source` | 0 | 0.0% | ✅ Clean |

> [!IMPORTANT]
> **Data Integrity Rule**: Missing prices are **NEVER replaced with zero**. Zero values distort regression baselines and ruin log-transforms. Missing modal values with valid min/max were systematically derived via `(min + max) / 2` with explicit audit flags.

---

## 3. Commodity & Market Coverage

### Commodities (6)
`Brinjal`, `Coconut`, `Paddy`, `Small Onion`, `Tomato`, `Turmeric`

### Top Markets by Record Volume
- **Ottanchatram**: 4 transactions
- **Erode**: 1 transactions
- **Pollachi**: 1 transactions
- **Thanjavur**: 1 transactions
- **Paravai**: 1 transactions

---

## 4. Price Validation & Outlier Audit

- **Minimum Modal Price**: ₹2100.0/Quintal
- **Median Modal Price**: ₹3450.0/Quintal
- **Maximum Modal Price**: ₹13600.0/Quintal
- **Average Modal Price**: ₹5068.75/Quintal

> [!NOTE]
> **Market Extremes Policy**: Genuine market spikes (e.g. Tomato surges during monsoon supply disruptions) are **retained** to reflect real market dynamics. Suspicious logic violations (e.g. `min_price > max_price` or non-positive prices) are flagged in `is_suspicious_record` for human or model review without silent data loss.

---
