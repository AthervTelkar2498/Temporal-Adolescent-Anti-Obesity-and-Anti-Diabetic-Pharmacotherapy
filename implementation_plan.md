# Reviewer Critique Response — Implementation Plan

This plan addresses six major reviewer-level critiques (**A–F**) against [XGBOOST.tex](file:///e:/Adverse%20drugs%20Project%202/Research%20paper%20latex/XGBOOST.tex). Each section details the exact LaTeX lines affected, the fix strategy, and whether computational work (re-training, new tables) is needed.

---

## A. Abstract Overclaim vs. Table 14/Table 10 Reality

### Problem
The abstract (L191) states *"XGBoost achieved the highest accuracy in all cohorts"*, but Table 10 (L1338–1340) shows a **three-way tie at 65.22%** for Diabetes Selected 4, and Table 14 (L1627–1629) shows XGBoost **loses** under multi-seed averaging (61.16% vs RF's 66.96%, GNN's 65.80%).

### Proposed Changes

#### [MODIFY] [XGBOOST.tex](file:///e:/Adverse%20drugs%20Project%202/Research%20paper%20latex/XGBOOST.tex) — Abstract Results (L191)

Rewrite the Results sentence to accurately reflect the nuance:

> *"XGBoost achieved the highest accuracy in the three largest cohorts (Obesity All 76.98%/0.6250 macro-F1; Obesity Selected 4 76.79%/0.4948; Diabetes All 69.39%/0.4875). In the smallest cohort (Diabetes Selected 4, $n=342$), all three models converged to 65.22% on a single seed; under multi-seed evaluation, Random Forest (66.96% ± 1.08%) and HANConv (65.80% ± 2.17%) exceeded XGBoost's raw accuracy (61.16% ± 3.93%), although XGBoost retained the highest macro-F1."*

#### [MODIFY] [XGBOOST.tex](file:///e:/Adverse%20drugs%20Project%202/Research%20paper%20latex/XGBOOST.tex) — Abstract Conclusions (L194)

Add a boundary-condition finding sentence:

> *"Tabular superiority over graph attention held reliably for $N \ge 5{,}000$ but reversed on raw accuracy (while XGBoost retained superior macro-F1) below $N \approx 350$, establishing a sample-size boundary for architectural recommendations."*

#### [MODIFY] [XGBOOST.tex](file:///e:/Adverse%20drugs%20Project%202/Research%20paper%20latex/XGBOOST.tex) — Post-Table 10 text (L1345)

Current text overclaims: *"XGBoost achieved the highest performance across all four cohorts"*. Rewrite:

> *"XGBoost achieved the highest single-seed accuracy and macro-F1 in the three largest cohorts. On the smallest cohort (Diabetes Selected 4, $N=342$), all three models tied at 65.22% accuracy on Seed 42; multi-seed evaluation (Table~\ref{tab:multiseed_variance}) revealed that this tie breaks in favour of Random Forest and HANConv on raw accuracy, though XGBoost retains the highest macro-F1."*

#### [MODIFY] [XGBOOST.tex](file:///e:/Adverse%20drugs%20Project%202/Research%20paper%20latex/XGBOOST.tex) — Introduction summary (L223)

Current text says *"substantially outperforming both Random Forest and the graph-based learner"* — add the caveat: *"…in the three largest cohorts; Section~\ref{sec:robustness} quantifies the boundary conditions under which this advantage reverses."*

#### [MODIFY] [XGBOOST.tex](file:///e:/Adverse%20drugs%20Project%202/Research%20paper%20latex/XGBOOST.tex) — Conclusion Key Finding (L1754)

Same pattern — add caveat about boundary condition.

#### [NEW] Winner-summary column in Table 14

Add two columns to Table 14 (`tab:multiseed_variance`, L1618–1632): **"Best Accuracy"** and **"Best Macro-F1"** per cohort, making the boundary condition legible at a glance.

---

## B. pt_term-Mode Imputation Leakage Analysis

### Problem
Stage 1 imputation (Eq. 1, L788–791) uses `pt_term` to compute the mode of observed `outc_cod` for 86.78% of imputed labels. If `pt_term` is also a model input feature, the model may learn to reverse-predict the imputation rule, artificially inflating accuracy. A skeptical reviewer will want to know whether the model's 77% accuracy is real or partially an artifact of mode-imputation circularity.

### Proposed Changes

#### B1. Stratified Accuracy Report — [NEW] Table 16

> [!IMPORTANT]  
> This requires **computational work**: re-running predictions on the test set with a `label_source` tag (observed / stage1_imputed / stage2_imputed) and reporting accuracy/macro-F1 per stratum.

- Write a script (`scratch/compute_stratified_accuracy.py`) that:
  1. Loads each Excel dataset
  2. Tags each row as `observed`, `stage1_imputed`, or `stage2_imputed` based on original `outc_cod` missingness
  3. Trains XGBoost (Seed 42, 14-col leakage-free) on the full training set
  4. Reports accuracy/macro-F1 separately for each stratum on the test set
- Add as Table 16 in the paper with prose interpretation

#### B2. Leave-pt_term-out Ablation — extend Table 13

Add a fourth row to Table 13 (`tab:ablation`, L1569): **"13 columns, pt_term removed"** alongside the existing severity_score ablation. This shows the accuracy delta when `pt_term` is excluded as a feature.

- Script: extend `scratch/compute_adolescent_ablation.py` with a pt_term-removed configuration

#### B3. Imputation Methodology Clarification (Writing Fix)

Add a paragraph after Eq. 1 (L791) explicitly stating:
- The pt_term → mode mapping is computed **only from training-fold observed labels**, never from test-fold reports
- Per-fold recomputation ensures zero information leakage from test into training

If this is NOT how the code currently works, we need to fix the pipeline too.

> [!CAUTION]  
> **This is the most critical sub-item.** If the imputation mapping is built on the entire dataset (train + test) before the train/test split, that is a genuine data leakage bug. We must inspect the actual training code to verify.

#### B4. Complete-Case-Only Anchor Result

Add a supplementary analysis restricted to only reports with genuinely observed `outc_cod` (the ~49% with no missingness). Report this as a supplementary result in the paper.

---

## C. Eq. 2 Circularity / Undefined severity_score

### Problem
Step 11 (L635) computes `severity_score` from `outc_cod`. Eq. 2 (L794–803) uses `severity_score` to impute `outc_cod` when it's missing. For rows where `outc_cod` is null, what is `severity_score`? The paper never explains this.

### Proposed Changes

#### [MODIFY] [XGBOOST.tex](file:///e:/Adverse%20drugs%20Project%202/Research%20paper%20latex/XGBOOST.tex) — Section 4.3 (after Eq. 2, ~L803)

Add a **clarification paragraph** explaining the computation order:
- For Stage 2 rows, `severity_score` in Eq. 2 is computed from **raw FAERS seriousness indicator fields** (`is_fatal`, `hosp`, `life_threat`, `disab` binary flags from the OUTC/DEMO tables), **not** from the already-imputed `outc_cod`
- Add explicit sub-notation: $\text{severity\_proxy}_i = f(\text{is\_fatal}_i, \text{hosp\_flag}_i, \text{life\_threat\_flag}_i)$, distinguishing it from the Step 11 `severity_score`

#### [MODIFY] [XGBOOST.tex](file:///e:/Adverse%20drugs%20Project%202/Research%20paper%20latex/XGBOOST.tex) — Section 4.2.4 Step 11 (L635)

Add one sentence: *"Note that for reports entering Stage 2 imputation (where outc_cod is null), the severity_score used in Eq. 2 is derived from raw seriousness binary indicators (is_fatal, hosp, life_threat, disab) available independently in the OUTC/DEMO tables, not from outc_cod itself."*

> [!WARNING]  
> We need to verify this is actually how the code works. If severity_score for null-outc_cod rows is itself undefined/null in the pipeline, that's a code bug to fix, not just a writing fix.

---

## D. Unequal Class-Imbalance Handling Between GNN and Tree Ensembles

### Problem
Tree models may implicitly benefit from Gini/gain splitting that is naturally robust to class imbalance, while the GNN uses unweighted cross-entropy. This makes the architectural comparison unfair.

### Proposed Changes

#### [MODIFY] [XGBOOST.tex](file:///e:/Adverse%20drugs%20Project%202/Research%20paper%20latex/XGBOOST.tex) — GNN failure analysis (L1416)

Soften the *"architecture-driven"* claim. Currently L1416 attributes GNN failure to *"The GNN's loss function, dominated by the majority class"*. Change to:

> *"The GNN's unweighted cross-entropy loss function, combined with the absence of class-weight balancing applied to the tabular models, causes the network to collapse during training."*

#### [MODIFY] [XGBOOST.tex](file:///e:/Adverse%20drugs%20Project%202/Research%20paper%20latex/XGBOOST.tex) — Discussion L1702

Soften *"tabular gradient boosting substantially outperforms"* to include the caveat: *"…under identical default hyperparameters; the GNN was not equipped with class-weighted loss, which may partially explain the performance gap in addition to architectural differences."*

#### [MODIFY] [XGBOOST.tex](file:///e:/Adverse%20drugs%20Project%202/Research%20paper%20latex/XGBOOST.tex) — Limitations (L1728–1736)

Add a new limitation item:
> *"The GNN was trained with unweighted cross-entropy, while tree ensembles benefit from implicit class-imbalance handling via Gini/gain splitting. A class-weighted GNN loss may narrow the performance gap; this is deferred to future work."*

#### [MODIFY] [XGBOOST.tex](file:///e:/Adverse%20drugs%20Project%202/Research%20paper%20latex/XGBOOST.tex) — Future Work (L1738–1744)

The existing *"Imbalance Remedies"* bullet already mentions SMOTE/focal loss. Expand it to explicitly mention class-weighted HANConv cross-entropy.

---

## E. Self-Referential Novelty Table (Table 2 / tab:sysrev)

### Problem
Table 2 (L266–319) defines 5 evaluation criteria and then scores the proposed framework 5/5 on criteria it defined itself. This is tautological and will draw reviewer skepticism.

### Proposed Changes

#### [MODIFY] [XGBOOST.tex](file:///e:/Adverse%20drugs%20Project%202/Research%20paper%20latex/XGBOOST.tex) — Before Table 2 (L263)

Add provenance for each criterion:
- **Ped.** → ICH E11(R1) itself calls for age-band-specific pharmacovigilance
- **ICH E11** → cite ICH E11(R1) 2017 addendum
- **Outcome** → cite the shift from signal-detection to outcome prediction in recent pharmacovigilance literature
- **4M** → cite WHO-UMC/EMA multi-method concordance guidelines
- **Pipe.** → cite FAIR data principles / READUS-PV

#### [MODIFY] [XGBOOST.tex](file:///e:/Adverse%20drugs%20Project%202/Research%20paper%20latex/XGBOOST.tex) — After Table 2 (L319)

Add an explicit self-awareness caveat:
> *"As the evaluation criteria were derived from gaps identified in this review, the comparative scoring should be interpreted as illustrating relative literature coverage rather than an independent benchmark. The proposed framework trivially satisfies criteria it was designed to address."*

#### [MODIFY] [XGBOOST.tex](file:///e:/Adverse%20drugs%20Project%202/Research%20paper%20latex/XGBOOST.tex) — ICH E11 column for "This Study"

Currently shows `$\sim$` (partial). Should explain why it's partial, not full ✓, to show honest self-assessment.

---

## F. Data/Code Availability

### Problem
The current section (L1763) says *"planned for release upon journal acceptance"*, which reviewers discount as promissory.

### Proposed Changes

#### [MODIFY] [XGBOOST.tex](file:///e:/Adverse%20drugs%20Project%202/Research%20paper%20latex/XGBOOST.tex) — Data and Code Availability (L1759–1769)

Per the user's note (*"we do about the github afterwards"*), keep the GitHub promise but strengthen the language to specify **what** will be released:

> *"Raw FAERS quarterly source files are publicly available at [URL]. The complete feature-engineering pipeline code, cohort-construction scripts, the RxNorm mapping cache, the exact list of caseid/primaryid retained per cohort (enabling independent cohort membership verification against public FAERS), and trained model artifacts (XGBoost JSON/PKL) will be released on a public GitHub repository with a Zenodo-archived DOI upon journal acceptance. No protected health information is contained in the model artifacts, as all FAERS input data is de-identified."*

---

## Verification Plan

### Automated Tests
- Compile [XGBOOST.tex](file:///e:/Adverse%20drugs%20Project%202/Research%20paper%20latex/XGBOOST.tex) with `pdflatex` to confirm no LaTeX errors
- Run `scratch/compute_stratified_accuracy.py` for B1 (Table 16)
- Run extended `scratch/compute_adolescent_ablation.py` for B2 (pt_term ablation)

### Manual Verification
- Review compiled PDF to ensure Table 14 winner columns render correctly
- Verify all textual claims match the data in Tables 10, 13, 14, 15
- Cross-check Eq. 2 severity_score usage against actual pipeline code

---

## Open Questions

> [!IMPORTANT]
> **Q1 (Critical — B3):** In the actual training pipeline, is the `pt_term → mode(outc_cod)` mapping built **per training fold** (correct) or on the **entire dataset** before the train/test split (leakage bug)? We need to inspect the pipeline code to confirm.

> [!IMPORTANT]
> **Q2 (C):** For rows where `outc_cod` is null when entering Stage 2 imputation, what value does `severity_score` actually take in the code? Is it computed from raw FAERS binary indicators (is_fatal, hosp, etc.), or is it undefined/null?

> [!IMPORTANT]
> **Q3 (B4):** Do you want us to run the complete-case-only anchor analysis (training/testing only on the ~49% of rows with genuinely observed `outc_cod`) as a supplementary result? This would produce a smaller N but zero-circularity reference.

> [!IMPORTANT]
> **Q4 (D):** Do you want us to actually re-train the GNN with class-weighted loss and report the results, or just acknowledge the limitation in text? Re-training would be more convincing but takes GPU time.

> [!IMPORTANT]
> **Q5 (F):** You mentioned *"we do about the github afterwards"* — should we update the Data Availability section now with the strengthened language (specifying what artifacts will be shared), or leave it as-is until the repo is ready?
