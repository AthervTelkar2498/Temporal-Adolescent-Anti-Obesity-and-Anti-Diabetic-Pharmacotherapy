# <p align="center"><span style="color:#0A3A70">Machine learning as a pharmacovigilance triage tool for serious adverse events in adolescents: A leakage-aware FAERS study</span></p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/PostgreSQL-16-4169E1?style=flat-square&logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/scikit--learn-1.5.0-F7931E?style=flat-square&logo=scikitlearn&logoColor=white" alt="scikit-learn">
  <img src="https://img.shields.io/badge/XGBoost-2.0.3-189FDD?style=flat-square" alt="XGBoost">
  <img src="https://img.shields.io/badge/License-Educational-007346?style=flat-square" alt="License">
</p>

This repository contains the verified clinical datasets, submission figures, supplementary information and machine learning codebase for analyzing and predicting **Adverse Drug Reactions (ADRs)** in adolescent populations (ages 12–17) receiving anti-obesity and anti-diabetic medications. The system utilizes the FDA Adverse Event Reporting System (FAERS) database spanning 20 quarters (2021–2025).

> **Note:** The manuscript LaTeX source and cover letter are not included in this repository for confidentiality reasons. The compiled manuscript is available upon request from the corresponding author.

---

## 📜 <span style="color:#0A3A70">Copyright & Academic Integrity</span>

This system is registered and protected under the **Indian Copyright Office**:
* **Project Reference ID:** `ANC-031` (PulseTech Framework)
* **Registration Title:** *PulseTech Source Code & Dataset Validation Framework*
* **Primary Developer / Concept Designer:** Amey Telkar
* **Institutional Faculty Mentors:** Prof. Akshay Javalgikar, Prof. Nitin Madanwale, Prof. Darshan Ruikar, Dr. Preethi Baligar

All source code, custom schemas, pipeline structures, and processed datasets in this repository are protected by international copyright laws. Use or citation of these materials must credit the authors and reference the official registration document: `PulseTech_ANC031_SourceCode_Copyright_20260603.pdf`.

---

## 🔬 <span style="color:#0A3A70">The 13-Step Validated Cleaning Pipeline</span>

To process spontaneous reporting data without signal bias, the framework implements a strict, deterministic **13-step cleaning and normalization pipeline** prior to database ingestion:

```text
RAW FAERS ASCII FILES (7 × .txt)
        │
        ├──► Step 0: Ingestion & Header-Based Schema Auto-Detection
        ├──► Step 1: Low-Quality Column Filtering (>90% Null Drop)
        ├──► Step 2: Demographics Deduplication (4-Level Version & Date Tie-Break)
        ├──► Step 3: Age Unit Normalization (6 units to decimal years)
        ├──► Step 4: ICH E11 Pediatric Band Assignment (Ages 12-17 = ADOLESCENT)
        ├──► Step 5: Weight Unit Standardization (Pounds to Kilograms)
        ├──► Step 6: Pediatric Cohort Extraction (Strict Age Filter Gates)
        ├──► Step 7: Date Formatting & Partial Date Flags (ISO 8601 formatting)
        ├──► Step 8: Filter Related Tables to Pediatric (Early join restriction)
        ├──► Step 9: FDA Validation and Role Code Filtering (Drop invalid / DN role codes)
        ├──► Step 10: Drug Mapping to RxNorm CUIs (94% API match + 85% fuzzy threshold)
        ├──► Step 11: Ordinal Severity Scale Construction (DE = 7 down to OT = 1)
        ├──► Step 12: Clinical Indication Normalization (Non-informative nullification)
        └
   [Step 13: Human-in-the-Loop Approve/Reject Quality Gate] ──► PostgreSQL DB
```

*(See Supplementary Information S4 Table for full details on this pipeline).*

---

## 🏆 <span style="color:#007346">Core Contribution: The 89.3% Precision Triage Tool</span>

The primary finding of this research is the operational validation of the machine learning framework as an automated triage tool. While predicting exact 6-class regulatory outcomes is highly noisy due to label ambiguity, the model successfully learns complex clinical patterns to reliably prioritize high-risk cases.

In a strict **chronological prospective evaluation** (trained on 2021-2024, tested on genuinely observed 2025 reports):
* When operating at a **5% review capacity**, the model captured priority cases with **89.7% precision**.
* When operating at a **20% review capacity**, the model flagged 469 total cases, of which **419 were true serious regulatory outcomes**.
* This achieves **89.3% precision (419/469)** in prioritizing the top 20% of adverse events, establishing a practical, leakage-controlled pathway for integrating machine learning into modern pharmacovigilance workflows.

---

## 📊 <span style="color:#0A3A70">Leakage-Free Validation & Model Benchmarks</span>

### 1. Leakage Quantification (5-Fold CV, XGBoost)
Directly quantifies the inflation caused by `pt_term`-to-outcome mapping when constructed on the full dataset versus strictly within each training fold:

| Approach | Mean Acc | Std Acc | Mean F1 | Std F1 |
|---|---|---|---|---|
| **Full-Dataset Mapping** | 0.7531 | 0.0077 | 0.4963 | 0.0610 |
| **Fold-Internal Mapping** | 0.4633 | 0.0105 | 0.1792 | 0.0063 |
| **Leakage Inflation** | **+0.2898** | --- | **+0.3171** | --- |

### 2. Stratified Accuracy (XGBoost Test Set)
Decomposes test-set performance by label source to verify that imputation does not artificially inflate reported metrics:

| Cohort | Overall Acc. | Observed Acc. | Stage 1 (pt_term Mode) | Stage 2 (Fallback) |
|---|---|---|---|---|
| **Obesity All** ($N=11{,}701$) | **76.98%** | **65.34%** ($n=1{,}157$) | 88.36% ($n=1{,}031$) | 88.24% ($n=153$) |
| **Obesity Selected 4** ($N=10{,}701$) | **76.79%** | **63.40%** ($n=989$) | 88.41% ($n=984$) | 87.50% ($n=168$) |
| **Diabetes All** ($N=5{,}208$) | **69.48%** | **58.77%** ($n=587$) | 81.97% ($n=355$) | 88.00% ($n=100$) |
| **Diabetes Selected 4** ($N=342$) | **66.67%** | **65.96%** ($n=47$) | 28.57% ($n=7$) | 86.67% ($n=15$) |

---

## 📁 <span style="color:#0A3A70">Repository Structure</span>

```
├── Submission_Figures/          # High-resolution EPS + PDF figures for journal submission
│   ├── Fig1.eps / Fig1.pdf      # Leakage-aware framework diagram
│   ├── Fig2.eps / Fig2.pdf      # STROBE-compliant cohort flow diagram
│   ├── Fig3.eps / Fig3.pdf      # SHAP feature importance
│   ├── Fig4.eps / Fig4.pdf      # Temporal confusion matrix
│   ├── Fig5.eps / Fig5.pdf      # Disproportionality heatmap
│   └── Striking_Image.*         # Journal striking image
├── Supplementary_Information/   # PLOS ONE supporting information
│   ├── S1_Table_STROBE_Checklist.docx
│   ├── S2_Table_TRIPOD_AI_Checklist.docx
│   ├── S3_Table_READUS_PV_Checklist.docx
│   ├── S4_Table_Pipeline_Specification.docx
│   ├── S5_Table_Hyperparameter_Search_Space.docx
│   └── S1_Fig_Cohort_Flow_Diagram.eps
├── dataset/                     # Cleaned analytical datasets & training scripts
│   ├── 14 Columns Model/       # Leakage-free 13-feature + target
│   ├── 15 Columns Leakage/     # With leaky severity_score feature
│   ├── 15 Columns Model with Source Quarter/
│   └── 16 Columns Leakage with Source Quarter/
├── README.md                    # This file
└── .gitignore                   # Excludes manuscript & cover letter
```

---

## 📧 <span style="color:#0A3A70">Contact</span>

For questions about this research, access to the manuscript, or collaboration inquiries:
* **Atherv Telkar** — [ORCID: 0009-0008-6422-7614](https://orcid.org/0009-0008-6422-7614)
* **Amey Telkar** — [ORCID: 0009-0000-5133-6012](https://orcid.org/0009-0000-5133-6012)
