# Safety of Anti-Obesity and Anti-Diabetic Medications in Adolescents

**Full Title:** Safety of anti-obesity and anti-diabetic medications in adolescents: A disproportionality analysis and machine-learning validation from 2021-2025 on the basis of the FAERS database

**Authors:** Telkar A, Telkar A, Javalgikar A, Madanwale N, Ruikar D, Baligar P.

**Journal:** PLOS ONE (submitted)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22767355.svg)](https://doi.org/10.5281/zenodo.22767355)

---

## Overview

This repository contains the code, datasets, supplementary information, and figures for a pharmacovigilance study analysing adverse drug events in adolescents (aged 12-17) using the FDA Adverse Event Reporting System (FAERS) database (2021Q1-2025Q4). The study applies four established disproportionality metrics (ROR, PRR, IC, EBGM) across 2,098 drug-event pairs and complements the signal-detection analysis with a temporal machine-learning model (XGBoost) for outcome triage.

---

## Repository Structure

```
.
├── code/                          # ML pipeline and figure generation
│   ├── train_temporal.py          # Temporal XGBoost training (2025 hold-out)
│   ├── compute_pseudo.py          # Pseudo-labelling for missing outcomes
│   ├── phase2_baselines_temporal.py  # Baseline comparators
│   ├── regen_figs.py              # Regenerate Figs 1, 3, 4 and S1 Fig
│   ├── results_temporal.json      # Complete ML output (all metrics)
│   └── README.md                  # Code documentation
├── dataset/                       # Analytic datasets (4 model variants)
│   ├── 14 Columns Model/          # Final 14-feature temporal model
│   ├── 15 Columns Leakage/        # 15-feature with leakage audit
│   ├── 15 Columns Model with Source Quarter/  # Temporal split variant
│   └── 16 Columns Leakage with Source Quarter/
├── Submission_Figures/            # All figures (EPS + PNG, 300 DPI)
│   ├── Fig1-4 (.eps, .png)        # Main manuscript figures
│   ├── S1_Fig_Detailed_Flowchart  # Supplementary figure 1
│   └── S2_Fig_SHAP_Importance     # Supplementary figure 2
├── Supplementary_Information/     # S1-S9 Tables
│   ├── S1_Table_STROBE_Checklist.docx
│   ├── S2_Table_TRIPOD_AI_Checklist.docx
│   ├── S3_Table_READUS_PV_Checklist.docx
│   ├── S4_Table_Pipeline_Specification.docx
│   ├── S5_Table_Hyperparameter_Search_Space.docx
│   ├── S6_Table_Predictor_Leakage_Audit.docx
│   ├── S7_Table_Temporal_Shift.docx
│   ├── S8_Table_Complete_Signal_Detection_FULL.xlsx
│   └── S9_Table_Quarterly_Reporting_Volume.docx
├── regen_figs.py                  # Root-level figure regeneration script
└── README.md
```

---

## Key Results

### Signal Detection

| Quantity | Value |
|---|---|
| Drug-event pairs evaluated (N >= 2) | 2,098 |
| Met ROR criteria (N >= 3, CI lower bound > 1) | 360 |
| Concordant across all four metrics | 105 |

**Data flow:** Raw FAERS records 7,612,804 → deduplicated 6,985,217 → adolescent (12-17 y) 403,278.

### Machine Learning (XGBoost 3.2.0, temporal 2025 test)

| Model | Macro-F1 |
|---|---|
| Preferred-Term-only lookup (baseline) | **0.594** (95% CI 0.545-0.626) |
| XGBoost, 13 features, temporal 2025 test (N = 2,812) | 0.389 (95% CI 0.353-0.434) |
| Random-split XGBoost (comparison only) | 0.629 |

The lookup baseline outperforms the model because ~50% of outcome labels were reconstructed from `pt_term`, which is also a model feature. The case-level ML results describe how outcome labels relate to reported event terms in FAERS; they are **not** evidence of independent predictive capability. Full discussion in the manuscript.

---

## Reproducibility

| Component | Status |
|---|---|
| Temporal ML evaluation, baselines, McNemar, bootstrap CIs | Fully reproducible from shipped data |
| Figures 1, 3, 4 and S1 Fig | `code/regen_figs.py` |
| Signal-detection results (S8 Table) | Shipped as complete output (2,098 pairs) |
| ROR / PRR / IC / EBGM computation code | Not included - output provided in S8 |
| Fig 2 (SOC distribution) | Requires licensed MedDRA PT-to-SOC mapping |
| S2 Fig (SHAP importance) | Requires trained model object |

---

## Signal Detection Criteria

| Metric | Criterion |
|---|---|
| ROR | 95% CI lower bound > 1 and N >= 3 |
| PRR | PRR >= 2, chi-squared >= 4, N >= 3 |
| IC | IC_025 > 0 |
| EBGM | EB05 >= 2 |

---

## Data Availability

- **FAERS data:** Publicly available from the [U.S. FDA](https://fis.fda.gov/extensions/FPD-QDE-FAERS/FPD-QDE-FAERS.html)
- **Signal-detection output:** Complete results for all 2,098 drug-event pairs in `Supplementary_Information/S8_Table_Complete_Signal_Detection_FULL.xlsx`
- **ML pipeline:** `code/train_temporal.py` with complete output in `code/results_temporal.json`
- **MedDRA:** Licensed from the MSSO; no MedDRA files are redistributed

---

## Citation

> Telkar A, Telkar A, Javalgikar A, Madanwale N, Ruikar D, Baligar P. Safety of anti-obesity and anti-diabetic medications in adolescents: A disproportionality analysis and machine-learning validation from 2021-2025 on the basis of the FAERS database. *PLOS ONE* (submitted).

**Zenodo DOI:** [10.5281/zenodo.22767355](https://doi.org/10.5281/zenodo.22767355)

---

## License

This project is provided for academic and research purposes.
