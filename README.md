# FAERS Pediatric ADR — Adolescent Adverse Drug Event Analysis (2021–2025)

[![PLOS ONE Submission](https://img.shields.io/badge/Journal-PLOS%20ONE-brightgreen)](https://journals.plos.org/plosone/)
[![XGBoost](https://img.shields.io/badge/XGBoost-3.2.0-orange)](https://xgboost.readthedocs.io/)
[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Overview

This repository contains the full data pipeline, reproducible code, manuscript, figures, and supporting materials for our PLOS ONE submission:

> **"Adverse Drug Event Profiling for Adolescent Anti-Obesity and Anti-Diabetic Medications Using FAERS (2021–2025): A Multi-Metric Disproportionality Analysis with Complementary Machine Learning Outcome Classification"**
>
> Atherv Telkar, Amey Telkar, Akshay Javalgikar, Nitin Madanwale, Darshan Ruikar, Preethi Baligar

---

## Key Results

### Primary Analysis — Signal Detection (FAERS 2021Q1–2025Q4)

| Metric | Value |
|--------|-------|
| Raw FAERS records | 7,612,804 |
| Adolescent reports (12–17 yrs) | 403,278 |
| Obesity-related panel | 11,701 reports (14 drugs) |
| Diabetes-related panel | 5,208 reports (10 drugs) |
| Drug-event pairs evaluated | **2,098** |
| ROR signals (N≥3, 95% CI lower >1) | **360** |
| Four-metric concordant signals | **105** |

**Key pharmacovigilance signals:**
- Metformin → Lactic Acidosis (ROR = 61.22, 95% CI 25.21–148.68)
- Semaglutide → Optic Ischaemic Neuropathy (ROR = 439.23) — 4-metric concordant
- Dapagliflozin → Cardiac Failure (ROR = 40.24)
- Atorvastatin → Myalgia (ROR = 16.89)

### Secondary Analysis — XGBoost Outcome Classification

| Model | Temporal Macro-F1 | Random-split |
|-------|------------------|--------------|
| **XGBoost (13 features)** | **0.389** (95% CI 0.353–0.434) | **0.629** |
| PT-only lookup | 0.594 ← outperforms XGBoost | — |
| Decision Tree | 0.298 | — |
| Random Forest | 0.267 | 0.563 |
| Logistic Regression | 0.172 | — |

> ℹ️ PT-lookup outperforms XGBoost because ~50% of outcome labels were imputed from the Preferred Term, which is also model feature 13. This is disclosed as a limitation. XGBoost significantly outperforms all other learned baselines (McNemar p<0.001).

---

## Repository Structure

```
faers-pediatric-adr/
├── manuscript/                         ← PLOS ONE submission package
│   ├── PONE_Condensed_V17_FINAL.pdf          ← Final manuscript PDF (25 pages)
│   ├── PONE_Condensed_V17_FINAL.tex          ← LaTeX source
│   ├── PONE_Condensed_V17_FINAL.docx         ← Word version
│   ├── PLOS_ONE_Cover_Letter_Corrected.docx
│   ├── Figures/                        ← All figures (EPS + PNG)
│   │   ├── Fig1.{eps,png}              ← FAERS report flow
│   │   ├── Fig2.{eps,png}              ← SOC-level AE distribution
│   │   ├── Fig3.{eps,png}              ← Forest plot top signals
│   │   ├── Fig4.{eps,png}              ← Temporal reporting trends
│   │   ├── S1_Fig_Detailed_Flowchart.{eps,png}
│   │   └── S2_Fig_SHAP_Importance.{eps,png}
│   ├── Code_Reproducibility/           ← ✅ All code with proof
│   │   ├── README.md                   ← How to reproduce
│   │   ├── train_temporal.py           ← XGBoost temporal pipeline
│   │   ├── results_temporal.json       ← Reproducible results (XGB 3.2.0)
│   │   ├── compute_pseudo.py           ← Pseudo-labelling (2-stage)
│   │   ├── phase2_baselines_temporal.py ← Baseline comparators
│   │   └── regen_figs.py              ← Figure generation
│   ├── exploratory/                    ← ML evaluation (not-in-primary-analysis note)
│   │   ├── README.md
│   │   ├── train_temporal.py
│   │   └── results_temporal.json
│   └── Supporting_Documents/
│       ├── S1_Table_STROBE_Checklist.docx
│       ├── S3_Table_READUS_PV_Checklist.docx
│       ├── S4_Table_Pipeline_Specification.docx
│       ├── S8_Table_Complete_Signal_Detection_FULL.xlsx  ← 2,098 pairs
│       └── S9_Table_Quarterly_Reporting_Volume.docx
├── backend/                            ← FastAPI + signal detection pipeline
├── frontend/                           ← React dashboard
└── README.md
```

---

## Reproducibility

### Signal Detection (Primary)
Signal detection is computed from raw FAERS contingency tables — completely independent of ML. See `manuscript/Code_Reproducibility/regen_figs.py` and `manuscript/Supporting_Documents/S8_Table_Complete_Signal_Detection_FULL.xlsx`.

### ML Classification (Secondary)
```bash
pip install xgboost==3.2.0 scikit-learn pandas openpyxl numpy shap
python manuscript/Code_Reproducibility/train_temporal.py
```

Expected output: `results_temporal.json` with temporal Macro-F1 = **0.389**

### Pseudo-Labelling Provenance
```bash
python manuscript/Code_Reproducibility/compute_pseudo.py
```
Stage 1: PT-mode fill (outcome imputed from most-frequent outcome for that Preferred Term)
Stage 2: Overall-mode fill (remaining missing filled with dataset mode)

---

## Data Availability

FAERS quarterly ASCII files are publicly available from the U.S. FDA:
https://fis.fda.gov/extensions/FPD-QDE-FAERS/FPD-QDE-FAERS.html

---

## Authors

| Author | Institution | Role |
|--------|-------------|------|
| **Atherv Telkar** | MIT Vishwaprayag University | Conceptualization, Software, Analysis |
| **Amey Telkar** | MIT Vishwaprayag University | Conceptualization, Software, Analysis |
| Akshay Javalgikar | MIT Vishwaprayag University | Investigation, Validation |
| Nitin Madanwale | MIT Vishwaprayag University | Investigation, Validation |
| Darshan Ruikar | MIT Vishwaprayag University | Data Curation, Supervision |
| Preethi Baligar | MIT Vishwaprayag University | Methodology, Supervision |

---

*Last updated: September 2026 | XGBoost 3.2.0 | Python 3.11 | PLOS ONE under review*
