# <p align="center"><span style="color:#0A3A70">Adolescent Anti-Obesity & Anti-Diabetic Pharmacotherapy Framework</span></p>

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
* **Institutional Faculty Mentors:** Prof. Akshay Javalgikar, Prof. Nitin Madanwale

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

1. **Step 0: Ingestion & Auto-Detection** – Parses quarterly files and dynamically determines columns.
2. **Step 1: Column Dropping** – Removes high-null fields (e.g. `drug_rec_act` >99% null).
3. **Step 2: Deduplication** – Resolves duplicate case files by prioritizing latest `caseversion` and follow-up reports.
4. **Step 3: Age Conversion** – Standardizes all age records into decimal years.
5. **Step 4: ICH E11 Stratification** – Stratifies cohorts into Neonate, Infant, Child, and Adolescent bands.
6. **Step 5: Weight Conversion** – Standardizes weight values to kilograms.
7. **Step 6: Pediatric Extraction** – Filters reports down to pediatric ranges (under 18).
8. **Step 7: Date Standardization** – Normalizes date columns null-safely.
9. **Step 8: Cross-Table Pruning** – Prunes sub-tables to match only pediatric primary IDs.
10. **Step 9: FDA Validation Filter** – Discards unvalidated (`val_vbm = 2`) entries.
11. **Step 10: RxNorm Drug Mapping** – Normalizes heterogeneous drug strings to standard RxCUI identifiers via the RxNav REST API.
12. **Step 11: Ordinal Severity Scoring** – Translates categorical outcome codes to an ordinal scale.
13. **Step 12: Indication Cleaning** – Nullifies non-informative terms (e.g., "unknown indication").
14. **Step 13: Quality Gate** – Displays a pipeline dashboard preview. **Writes to PostgreSQL are locked until human approval.**

---

## 🔮 <span style="color:#007346">Leakage-Free Two-Stage Imputation</span>

The target label `outc_cod` (Outcome Code) is missing in over 50% of raw FAERS records. To preserve sample sizes, the system uses an intelligent **two-stage clinical imputation pipeline**:

* **Stage 1 (AE-Specific Mode):** Missing values are imputed with the historical modal outcome of that specific adverse event (`pt_term`).
* **Stage 2 (Clinical Fallback):** Remaining missing outcomes are resolved via seriousness indicators (`is_fatal`, `hosp`, `life_threat`, `disab`) to compute a `severity_proxy` independent of the target.

### 🚫 Target Leakage Resolution
Leaving the derived `severity_score` in the training data acts as a target-leakage feature (near-deterministic proxy for outcomes), inflating accuracy to $\sim 100\%$. **In this repo, all primary modeling datasets are constructed with the `severity_score` feature strictly removed (13 columns remaining)** to ensure honest, leakage-free predictive metrics.

---

## 📊 <span style="color:#0A3A70">Model Benchmarks & Scientific Proof</span>

We compare two tabular classifiers against a Heterogeneous Attention Network (HANConv) Graph Neural Network:

### 1. Stratified Accuracy (XGBoost Test Set)
Decomposes test-set performance by label source to verify that imputation does not artificially inflate reported metrics:

| Cohort | Overall Acc. | Observed Acc. | Stage 1 (pt_term Mode) | Stage 2 (Fallback) |
|---|---|---|---|---|
| **Obesity All** ($N=11{,}701$) | **76.98%** | **65.34%** ($n=1{,}157$) | 88.36% ($n=1{,}031$) | 88.24% ($n=153$) |
| **Obesity Selected 4** ($N=10{,}701$) | **76.79%** | **63.40%** ($n=989$) | 88.41% ($n=984$) | 87.50% ($n=168$) |
| **Diabetes All** ($N=5{,}208$) | **69.48%** | **58.77%** ($n=587$) | 81.97% ($n=355$) | 88.00% ($n=100$) |
| **Diabetes Selected 4** ($N=342$) | **66.67%** | **65.96%** ($n=47$) | 28.57% ($n=7$) | 86.67% ($n=15$) |

### 2. Feature Ablation (Leave-`pt_term`-Out)
Quantifies the exact accuracy contribution ($\Delta$) of the adverse event type (`pt_term`):

* **Obesity All:** 14-Col (76.98%) vs 13-Col (64.25%) $\implies \Delta = -12.73\%$
* **Obesity Selected 4:** 14-Col (76.79%) vs 13-Col (64.22%) $\implies \Delta = -12.56\%$
* **Diabetes All:** 14-Col (69.48%) vs 13-Col (58.35%) $\implies \Delta = -11.13\%$
* **Diabetes Selected 4:** 14-Col (66.67%) vs 13-Col (63.77%) $\implies \Delta = -2.90\%$

### 3. Complete-Case-Only Anchor (Zero Imputation Circularity)
Trains and evaluates XGBoost **exclusively** on reports with genuinely observed outcome labels (no imputed data):

* **Obesity All ($N=5{,}768$):** **63.78%** Accuracy | 0.4564 Macro-F1
* **Obesity Selected 4 ($N=5{,}019$):** **62.35%** Accuracy | 0.5307 Macro-F1
* **Diabetes All ($N=3{,}039$):** **59.21%** Accuracy | 0.4907 Macro-F1
* **Diabetes Selected 4 ($N=226$):** **50.00%** Accuracy | 0.3582 Macro-F1

---

## 📁 <span style="color:#0A3A70">Repository Structure</span>

* `dataset/46 columns Model/` – Full analytical feature files with 46 variables.
* `dataset/15 Columns Leakage/` – Training files containing the leaky `severity_score` feature.
* `dataset/14 Columns Model/` – **Primary Predictive Model Data** (leakage-free 13-feature + target outcome format).
* `README.md` – Project documentation.