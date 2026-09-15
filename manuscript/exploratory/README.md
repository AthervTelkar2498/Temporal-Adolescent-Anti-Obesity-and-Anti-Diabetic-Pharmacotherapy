# exploratory/ -- ML Code: Results Qualified in Manuscript

This folder contains the ML evaluation code for the secondary ML analysis in the manuscript.

## Files

| File | Purpose |
|------|---------|
| train_temporal.py | Chronological XGBoost pipeline (2021-2023 train / 2024 val / 2025 test) |
| results_temporal.json | Output of train_temporal.py with XGBoost 3.2.0 |

## Key results (XGBoost 3.2.0, seed 42, train-only preprocessing)

- Temporal Macro-F1 (5-class, 2025 test): 0.389 (95% CI 0.353-0.434)
- Random-split Macro-F1: 0.629
- PT-only lookup Macro-F1: 0.594 (outperforms XGBoost)

## Why PT-lookup outperforms XGBoost

~50% of FAERS outcome codes were imputed from pt_term (the Preferred Term),
which is also model feature 13. The PT-lookup heuristic partially recovers
the imputation rule. This is disclosed as a limitation in the manuscript.

## How to reproduce

    pip install xgboost scikit-learn pandas openpyxl numpy
    python exploratory/train_temporal.py --boot 100

Output: exploratory/results_temporal.json
