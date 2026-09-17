# code/ — authoritative reproducibility location

This is the **single authoritative copy** of the analysis code. In V17 the same files
existed in three places (`code/`, `Code_Reproducibility/`, `exploratory/`) as
byte-identical duplicates. In V18 `code/` is the only copy published; the other two
directories are retained in the local master archive as historical record only.

| File | Purpose | Runs from this package? |
|---|---|---|
| `train_temporal.py` | Chronological XGBoost pipeline (2021–2023 train / 2024 val / 2025 test), baselines, McNemar, bootstrap CIs | **Yes**, end to end |
| `results_temporal.json` | Complete output of the above — every value in Table 5 and the ML subsection | output artefact |
| `regen_figs.py` | Regenerates Figs 1, 3, 4 and S1 Fig from the S8 workbook | **Yes** |
| `compute_pseudo.py` | Two-stage outcome pseudo-labelling (PT-mode fill → overall-mode fill) | No — needs `FAERS_Pediatric_ML_Dataset.xlsx`, not distributed |
| `phase2_baselines_temporal.py` | Seriousness-rule and baseline comparators | No — needs `ObesityAll_14_Drugs_Adolescent_48cols.xlsx`, not distributed |

No absolute filesystem paths are hard-coded. The two scripts that need an external
dataset take it as a command-line argument or environment variable and exit with a clear
message if it is absent.

## Reproduce

```bash
pip install xgboost==3.2.0 scikit-learn pandas openpyxl numpy scipy matplotlib
python code/train_temporal.py            # -> code/results_temporal.json
python code/regen_figs.py                # -> Figs 1, 3, 4, S1
```

Optional, with your own copies of the upstream datasets:

```bash
python code/compute_pseudo.py --data /path/to/FAERS_Pediatric_ML_Dataset.xlsx
python code/phase2_baselines_temporal.py --data /path/to/ObesityAll_14_Drugs_Adolescent_48cols.xlsx --out results/
```

## Expected output (XGBoost 3.2.0, seed 42)

| Metric | Value |
|---|---|
| Temporal Macro-F1 (5-class, 2025 test, N = 2,812) | **0.389** (95% CI 0.353–0.434) |
| Six-class sensitivity (RI as zero-support class) | 0.324 |
| Random-split Macro-F1 (leakage-preserving, comparison only) | 0.629 |
| Random-split Random Forest | 0.563 |
| PT-only lookup Macro-F1 | **0.594** (95% CI 0.545–0.626) — beats the model |
| XGBoost without `pt_term` | 0.222 |
| McNemar XGBoost vs PT-lookup | b = 134, c = 453, χ² = 172.27, p = 2.4 × 10⁻³⁹ |

## Not included

No ROR / PRR / IC / EBGM computation code is in this repository. The disproportionality
analysis is deposited as its complete numerical output (S8 Table), not as executable
code. `regen_figs.py` only *reads* those columns. No MedDRA dictionary file is
redistributed; MedDRA is licensed from the MSSO.
