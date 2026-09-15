# Code_Reproducibility/

This folder contains all code needed to reproduce the computational results in the manuscript:
**"Adverse Drug Event Profiling for Adolescent Anti-Obesity and Anti-Diabetic Medications Using FAERS (2021-2025): A Multi-Metric Disproportionality Analysis with Complementary Machine Learning Outcome Classification"**

---

## Contents

| File | Purpose | Manuscript Section |
|------|---------|-------------------|
| `train_temporal.py` | **Primary ML script** — XGBoost temporal pipeline (2021-2023 train / 2024 val / 2025 test) | Methods: Complementary ML Analysis |
| `results_temporal.json` | **Reproducible output** — all Macro-F1, per-class metrics, McNemar b/c values, CIs | Results: Table 5, ML subsection |
| `compute_pseudo.py` | Pseudo-labelling code — 2-stage outcome imputation (PT-mode fill → overall-mode fill) | Methods: Outcome-label handling |
| `phase2_baselines_temporal.py` | Seriousness-rule and baseline comparators | Methods: Baseline comparators |
| `regen_figs.py` | Regenerates Figures 1-4 and S1-S2 from S8 Table data | Figure legends |

---

## Reproducible Key Results (XGBoost 3.2.0, seed=42)

| Metric | Value |
|--------|-------|
| Temporal Macro-F1 (5-class, 2025 test) | **0.389** (95% CI 0.353–0.434) |
| Random-split Macro-F1 | **0.629** |
| PT-only lookup Macro-F1 | **0.594** ← outperforms XGBoost |
| McNemar: XGBoost vs Majority | b=433, c=193, p=1.3×10⁻²¹ |
| McNemar: XGBoost vs PT-lookup | b=134, c=453, p=2.4×10⁻³⁹ (PT wins) |

---

## How to Reproduce

```bash
pip install xgboost==3.2.0 scikit-learn pandas openpyxl numpy shap
python train_temporal.py
```

Output: `results_temporal.json`

To regenerate figures:
```bash
pip install matplotlib pandas openpyxl
python regen_figs.py
```

---

## Note on Pseudo-Labelling

`compute_pseudo.py` implements the 2-stage procedure described in the manuscript:
1. **Stage 1 (PT-mode fill):** Missing outcome codes filled with the most frequent outcome for that Preferred Term in the training set
2. **Stage 2 (overall-mode fill):** Any remaining missing outcomes filled with the dataset-wide mode

This is disclosed as a limitation in the manuscript — the Preferred Term is both a predictor (feature 13) and the source of Stage 1 imputation, creating a label-proxy dependency.

---

## Note on Seriousness-Rule Baseline

`phase2_baselines_temporal.py` contains the seriousness-rule classifier which uses `is_fatal`, `severity_score`, and `is_serious`. These are outcome-derived columns **not** present in the 14-column leakage-free feature set used for XGBoost. This baseline was therefore excluded from Table 5 as it is not comparable.

---

*XGBoost 3.2.0 · Python 3.11 · Verified 2026-09-15*
