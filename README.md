# Temporal Adolescent Anti-Obesity and Anti-Diabetic Pharmacotherapy

## Comprehensive Multi-Metric Disproportionality Analysis of Anti-Obesity and Anti-Diabetic Drug Safety in Adolescents Using FAERS Data (2021–2025)

[![PLOS ONE](https://img.shields.io/badge/Journal-PLOS%20ONE-blue)](https://journals.plos.org/plosone/)
[![FAERS](https://img.shields.io/badge/Data-FDA%20FAERS-green)](https://www.fda.gov/drugs/questions-and-answers-fdas-adverse-event-reporting-system-faers/fda-adverse-event-reporting-system-faers-public-dashboard)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

---

## Abstract

This study provides the first large-scale, multi-metric disproportionality analysis of anti-obesity and anti-diabetic drug safety specifically in adolescents aged 12–17 years. Using the FDA Adverse Event Reporting System (FAERS) database covering 2021Q1–2025Q4, we analysed **7,612,804** raw reports, identifying **403,278** adolescent-specific cases. From these, **11,701** reports involved anti-obesity medications (14 drugs) and **5,208** involved anti-diabetic medications (10 drugs).

Signal detection was performed using four established disproportionality methods (ROR, PRR, IC, EBGM), complemented by an XGBoost machine-learning model for case-level outcome triage. Key findings include:

- **Metformin–Lactic acidosis**: ROR = 61.22 (95% CI: 25.21–148.68), N = 214
- **Atorvastatin–Myalgia**: ROR = 16.89 (95% CI: 8.94–31.92), N = 46
- **Semaglutide–Optic ischaemic neuropathy**: ROR = 439.23 (95% CI: 99.33–1942.26), N = 14
- **Dapagliflozin–Cardiac failure**: ROR = 40.24 (95% CI: 22.90–70.71), N = 30

---

## Repository Structure

```
├── README.md
├── dataset/
│   ├── 14 Columns Model/           # Primary model (no data leakage)
│   │   ├── ObesityAll_14_Drugs_Adolescent_14Columns_Imputed.xlsx
│   │   ├── DiabeticsAll_10_Drugs_Adolescent_14Columns_Imputed.xlsx
│   │   ├── Obesity_Selected4Drgs_Adolescent_14Columns_Imputed.xlsx
│   │   ├── Diabetics_Selected4Drgs_Adolescent_14Columns_Imputed.xlsx
│   │   ├── ML_Multiclass_Model_Comparison_Results.xlsx
│   │   └── train_*.py              # Training scripts
│   ├── 15 Columns Leakage/         # Leakage analysis (severity_score included)
│   ├── 15 Columns Model with Source Quarter/  # Temporal split model
│   └── 16 Columns Leakage with Source Quarter/
├── Submission_Figures/
│   ├── Fig1_Flowchart.png/eps       # STROBE-compliant study flowchart
│   ├── Fig2_SOC_Distribution.png/eps # SOC-level AE bar chart
│   ├── Fig3_Forest_Metformin_Atorvastatin.png  # Forest plot (a,b)
│   ├── Fig3_Forest_Semaglutide.png  # Forest plot (c)
│   ├── Fig4_Forest_Dapagliflozin_Glargine.png  # Forest plot (a,b)
│   └── Fig4_Forest_Tirzepatide_Empagliflozin.png  # Forest plot (c,d)
└── Supplementary_Information/
    ├── S1_Table_STROBE_Checklist.docx
    ├── S2_Table_TRIPOD_AI_Checklist.docx
    ├── S3_Table_READUS_PV_Checklist.docx
    ├── S4_Table_Pipeline_Specification.docx
    ├── S5_Table_Hyperparameter_Search_Space.docx
    ├── S6_Table_Predictor_Leakage_Audit.docx
    ├── S7_Table_Temporal_Shift.docx
    ├── S8_Table_Complete_Signal_Detection.docx  # 2,098 drug-event pairs
    ├── S1_Fig_Detailed_Flowchart.png/eps
    └── S2_Fig_SHAP_Importance.png/eps
```

---

## Study Design

### Data Source
- **Database**: FDA Adverse Event Reporting System (FAERS)
- **Period**: 2021Q1 – 2025Q4 (20 consecutive quarters)
- **Population**: Adolescents aged 12–17 years
- **Total raw records**: 7,612,804
- **After deduplication**: 6,985,217 unique cases
- **Age-eligible**: 403,278 adolescent reports

### Drug Panels

| Panel | Drugs | N (reports) |
|-------|-------|-------------|
| Broad Obesity (14 drugs) | Metformin, atorvastatin, lisinopril, losartan, dapagliflozin, insulin (regular, aspart, glargine, lispro), semaglutide, empagliflozin, tirzepatide | 11,701 |
| Selected Obesity (4 drugs) | Metformin, atorvastatin, lisinopril, losartan | 10,701 |
| Broad Diabetes (10 drugs) | Metformin, dapagliflozin, insulin (aspart, regular, lispro, glargine), semaglutide, empagliflozin, tirzepatide | 5,208 |
| Selected Diabetes (4 drugs) | Semaglutide, empagliflozin, tirzepatide, dapagliflozin | 342 |

### Signal Detection Methods

| Method | Criteria |
|--------|----------|
| **ROR** (Reporting Odds Ratio) | 95% CI lower bound > 1, N ≥ 3 |
| **PRR** (Proportional Reporting Ratio) | PRR ≥ 2, χ² ≥ 4, N ≥ 3 |
| **IC** (Information Component, BCPNN) | IC₀₂₅ > 0 |
| **EBGM** (Empirical Bayes Geometric Mean) | EB05 ≥ 2 |

### Machine Learning Component
- **Model**: XGBoost (leakage-aware, 14-column model)
- **Features**: 13 case-level features (age, sex, weight, drug sequence, route, role code, drug name, RxCUI, dose amount/unit/form, indication, AE PT)
- **Target**: Outcome severity (DE/LT/HO/DS/RI/OT)
- **Split**: Chronological (Train: 2021Q1–2023Q4, Validation: 2024, Test: 2025)
- **Performance**: Macro-F1 = 0.625 (random split), 0.177 (temporal split)

---

## Key Findings

### Strongest Disproportionality Signals

| Drug | Adverse Event (PT) | N | ROR | 95% CI |
|------|-------------------|---|-----|--------|
| Metformin | Lactic acidosis | 214 | 61.22 | 25.21–148.68 |
| Semaglutide | Optic ischaemic neuropathy | 14 | 439.23 | 99.33–1942.26 |
| Dapagliflozin | Cardiac failure | 30 | 40.24 | 22.90–70.71 |
| Atorvastatin | Myalgia | 46 | 16.89 | 8.94–31.92 |
| Atorvastatin | Drug-induced liver injury | 38 | 16.70 | 8.56–32.59 |
| Dapagliflozin | Ketoacidosis | 10 | 9.72 | 4.88–19.37 |

### Demographics
- **Sex**: ~54% female predominance across all panels
- **Mean age**: 14.57 years (mid-adolescence peak)
- **Top reporter**: Healthcare professionals (51–56%)
- **Outcome missingness**: 45.9–51.3% (a known FAERS limitation)

---

## Figures

### Fig 1. Study Flowchart
STROBE-compliant case-selection flow from 7,612,804 raw FAERS records through deduplication, age filtering, and drug panel filtering to final analytical cohorts.

### Fig 2. SOC Distribution
Horizontal bar chart showing the proportion of AE reports across 23 System Organ Class categories for both obesity-related and diabetes-related panels.

### Fig 3. Forest Plots (Metformin, Atorvastatin, Semaglutide)
Multi-panel forest plots showing top AE signals ranked by report count, with ROR point estimates and 95% confidence intervals.

### Fig 4. Forest Plots (Dapagliflozin, Insulin Glargine, Tirzepatide, Empagliflozin)
Forest plots for remaining drug-specific adverse event profiles.

---

## Supplementary Information

| File | Description |
|------|-------------|
| **S1 Table** | STROBE checklist for observational studies |
| **S2 Table** | TRIPOD+AI checklist for prediction model development |
| **S3 Table** | READUS-PV checklist for disproportionality analysis |
| **S4 Table** | Complete preprocessing pipeline specification |
| **S5 Table** | Hyperparameter search space and optimal configurations |
| **S6 Table** | Predictor specification and data-leakage audit |
| **S7 Table** | Temporal dataset shift analysis across train/val/test |
| **S8 Table** | Complete signal detection results (2,098 drug-event pairs) |
| **S1 Fig** | Detailed case-selection flow diagram |
| **S2 Fig** | SHAP feature importance for XGBoost model |

---

## Dataset Description

### 14-Column Model (Primary – No Leakage)
The primary analysis uses 14 features per FAERS report:

| Column | Description | Type |
|--------|-------------|------|
| `age_years` | Patient age in years | Continuous |
| `sex` | Patient sex | Categorical |
| `weight_kg` | Patient weight (kg) | Continuous |
| `drug_seq` | Drug sequence in report | Ordinal |
| `route` | Route of administration | Categorical |
| `role_cod` | Drug role (PS/SS/C/I) | Categorical |
| `drugname_normalized` | Standardised drug name | Categorical |
| `rxcui` | RxNorm Concept Unique ID | Categorical |
| `dose_amt` | Dose amount | Continuous |
| `dose_unit` | Dose unit | Categorical |
| `dose_form` | Dosage form | Categorical |
| `indi_pt` | Indication (PT) | Categorical |
| `pt_term` | Adverse event (PT) | Categorical |
| `outc_cod` | Outcome code (target) | Categorical |

### 15-Column Leakage Model
Includes `severity_score` (derived from outcome) — used for leakage analysis only. This column was excluded from the primary analysis as it constitutes target leakage.

---

## Ethics Statement

This study used publicly available, de-identified data from the FAERS database. No personally identifiable information was accessed. All procedures adhered to the ethical principles of the Declaration of Helsinki.

---

## Citation

If you use this dataset or methodology, please cite:

```
Telkar A, et al. Comprehensive Multi-Metric Disproportionality Analysis of 
Anti-Obesity and Anti-Diabetic Drug Safety in Adolescents Using FAERS Data 
(2021–2025). PLOS ONE. 2025. [Submitted]
```

---

## License

This work is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

## Contact

For questions about this repository, please open an issue or contact the corresponding author.
