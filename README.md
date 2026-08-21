# <p align="center"><span style="color:#0A3A70">Machine learning as a pharmacovigilance triage tool for serious adverse events in adolescents: A leakage-aware FAERS study</span></p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/PostgreSQL-16-4169E1?style=flat-square&logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/PyTorch-2.3-EE4C2C?style=flat-square&logo=pytorch&logoColor=white" alt="PyTorch">
  <img src="https://img.shields.io/badge/License-Educational-007346?style=flat-square" alt="License">
</p>

This repository contains the verified clinical datasets and machine learning codebase for analyzing and predicting **Adverse Drug Reactions (ADRs)** in adolescent populations (ages 12–17) receiving anti-obesity and anti-diabetic medications. The system utilizes the FDA Adverse Event Reporting System (FAERS) database spanning 20 quarters (2021–2025).

---

## 🛡️ <span style="color:#0A3A70">Copyright & Academic Integrity</span>

This system is registered and protected under the **Indian Copyright Office**:
* **Project Reference ID:** `ANC-031` (PulseTech Framework)
* **Registration Title:** *PulseTech Source Code & Dataset Validation Framework*
* **Primary Developer / Concept Designer:** Amey Telkar
* **Institutional Faculty Mentors:** Prof. Akshay Javalgikar, Prof. Nitin Madanwale, Prof. Darshan Ruikar, Dr. Preethi Baligar

All source code, custom schemas, pipeline structures, and processed datasets in this repository are protected by international copyright laws. Use or citation of these materials must credit the authors and reference the official registration document: `PulseTech_ANC031_SourceCode_Copyright_20260603.pdf`.

---

## ⚙️ <span style="color:#0A3A70">The 13-Step Validated Cleaning Pipeline</span>

To process spontaneous reporting data without signal bias, the framework implements a strict, deterministic **13-step cleaning and normalization pipeline** prior to database ingestion:

```text
RAW FAERS ASCII FILES (7 × .txt)
        │
        ├─► Step 0: Ingestion & Header-Based Schema Auto-Detection
        ├─► Step 1: Low-Quality Column Filtering (>90% Null Drop)
        ├─► Step 2: Demographics Deduplication (4-Level Version & Date Tie-Break)
        ├─► Step 3: Age Unit Normalization (6 units to decimal years)
        ├─► Step 4: ICH E11 Pediatric Band Assignment (Ages 12-17 = ADOLESCENT)
        ├─► Step 5: Weight Unit Standardization (Pounds to Kilograms)
        ├─► Step 6: Pediatric Cohort Extraction (Strict Age Filter Gates)
        ├─► Step 7: Date Formatting & Partial Date Flags (ISO 8601 formatting)
        ├─► Step 8: Filter Related Tables to Pediatric (Early join restriction)
        ├─► Step 9: FDA Validation and Role Code Filtering (Drop invalid / DN role codes)
        ├─► Step 10: Drug Mapping to RxNorm CUIs (94% API match + 85% fuzzy threshold)
        ├─► Step 11: Ordinal Severity Scale Construction (DE = 7 down to OT = 1)
        ├─► Step 12: Clinical Indication Normalization (Non-informative nullification)
        ▼
   [Step 13: Human-in-the-Loop Approve/Reject Quality Gate] ──► PostgreSQL DB
```

*(See Supplementary Information S4 Table for full details on this pipeline).*

---

## 🚀 <span style="color:#007346">Core Contribution: The 89.3% Precision Triage Tool</span>

The primary finding of this research is the operational validation of the machine learning framework as an automated triage tool. While predicting exact 6-class regulatory outcomes is highly noisy due to label ambiguity, the model successfully learns complex clinical patterns to reliably prioritize high-risk cases.

In a strict **chronological prospective evaluation** (trained on 2021-2024, tested on genuinely observed 2025 reports):
* When operating at a **5% review capacity**, the model captured priority cases with **89.7% precision**.
* When operating at a **20% review capacity**, the model flagged 469 total cases, of which **419 were true serious regulatory outcomes**.
* This achieves **89.3% precision (419/469)** in prioritizing the top 20% of adverse events, establishing a practical, leakage-controlled pathway for integrating machine learning into modern pharmacovigilance workflows.

---

## 🔮 <span style="color:#0A3A70">Leakage-Free Validation & Model Benchmarks</span>

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

* `dataset/14 Columns Model/` – Primary Predictive Model Data (leakage-free 13-feature + target outcome format).
* `dataset/15 Columns Leakage/` – Training files containing the leaky `severity_score` feature.
* `Figures/` – High-resolution export of all generated plots, confusion matrices, and SHAP analyses.
* `Supplementary_Information/` – Checklists and tabular parameter documentation.
* `README.md` – Project documentation.