# Table 4 provenance investigation — RESOLVED

**Question.** Table 4 reported an observed outcome distribution that could not be
reconciled with the ML modelling dataset. Both totalled 11,701, but Disability fell
195 → 114 and Required Intervention fell 343 → 5. Filling missing outcomes cannot
*reduce* a class, so the stated explanation could not be correct.

**Answer.** The pipeline was never at fault. Table 4's outcome block did not describe
this cohort. The true observed distribution is recoverable from the shipped data, and
DS *rose*; RI never moved.

---

## 1. The decisive evidence: `severity_score`

The "Leakage" dataset variants carry a `severity_score` column — the column the authors
themselves documented as target leakage. Cross-tabulating it against `outc_cod` in
`16 Columns Leakage with Source Quarter/ObesityAll_14_Drugs_Adolescent_15Columns_Imputed.xlsx`
gives a **perfect one-to-one mapping** for every score ≥ 1:

| severity_score | outcome | rows (broad obesity) |
|---|---|---|
| 7 | DE | 475 |
| 6 | LT | 389 |
| 5 | HO | 2,011 |
| 4 | DS | 77 |
| 2 | RI | 5 |
| 1 | OT | 2,811 |
| **0** | **no observed outcome** | **5,933** |

`severity_score` is therefore a direct record of the *original observed* outcome, and
`severity_score == 0` marks exactly the reports that had none. That count — 5,933 —
matches Table 4's Missing cell exactly.

The 14-column and 16-column files were verified byte-identical on every shared column,
so this mapping applies to the dataset actually used for modelling.

## 2. The reconciliation is exact

| | Observed (recovered) | + Imputed (severity_score = 0) | = ML dataset |
|---|---|---|---|
| HO | 2,011 | 1,646 | 3,657 ✓ |
| OT | 2,811 | 4,166 | 6,977 ✓ |
| DE | 475 | 50 | 525 ✓ |
| LT | 389 | 34 | 423 ✓ |
| DS | 77 | 37 | **114 ✓** |
| RI | 5 | 0 | **5 ✓** |
| Missing | 5,933 | — | 0 |

Every class total equals observed + imputed. The same holds in all four panels.

**No row was filtered, relabelled, collapsed, deduplicated or overwritten.** Both
`compute_pseudo.py` and `phase2_baselines_temporal.py` operate only on
`outc_cod.isna()` rows, and the data confirms it: no observed label was altered.
Disability did not fall from 195 to 114 — it *rose* from 77 to 114. Required
Intervention was 5 throughout.

## 3. Independent corroboration

Every demographic row of **S7 Table** reproduces exactly from the same files: N
6,831 / 2,058 / 2,812; Female 53.4 / 54.8 / 55.2 %; mean age 14.58 / 14.57 / 14.55;
Death 4.7 / 3.9 / 4.5 %; top drug; top PT; unique drugs 17 / 15 / 16; unique PTs
1,294 / 676 / 784. The 2025 test-set class supports also match the classification
report exactly (OT 1,624, HO 893, LT 152, DE 126, DS 17, RI 0).

Table 4's **age and sex** rows likewise match the shipped data exactly in all four
panels. Only its outcome and drug-role rows did not.

## 4. What was wrong with Table 4

Its outcome block was internally self-consistent — counts matched their own percentages
— but did not match the analytic data. It was a **mixture of two pipeline stages**: its
Death figure of 525 is the *post*-imputation count, reported alongside a Missing row
that only makes sense pre-imputation.

A second, independent discrepancy was found in the **drug-role block**. Primary suspect
and Concomitant matched exactly in all four panels; Secondary suspect and Interacting
did not. The SS + I *total* was preserved in every panel while the split differed
(broad obesity: table 549 / 364, data 857 / 56) — the signature of a re-allocation.

## 5. Corrections applied in V18

| Row | Was | Now |
|---|---|---|
| HO | 2,506 (21.4 %) | **2,011 (17.2 %)** |
| OT | 1,898 (16.2 %) | **2,811 (24.0 %)** |
| DE | 525 (4.5 %) | **475 (4.1 %)** |
| LT | 301 (2.6 %) | **389 (3.3 %)** |
| DS | 195 (1.7 %) | **77 (0.7 %)** |
| RI | 343 (2.9 %) | **5 (0.04 %)** |
| Missing | 5,933 (50.7 %) | 5,933 (50.7 %) — unchanged |
| Secondary suspect | 549 (4.7 %) | **857 (7.3 %)** |
| Interacting | 364 (3.1 %) | **56 (0.5 %)** |

Cascading text corrections: the outcome-missingness range becomes **33.9–53.1 %**
(was 45.9–51.3 %) in Methods, Results and Discussion. The Table 4 note was rewritten
and moved below the table.

All four panels sum exactly to N after correction.

## 6. Confidence, and what remains open

| Item | Confidence | Basis |
|---|---|---|
| Outcome block | **High** | Two independent internal witnesses (`severity_score` and `outc_cod`) agree; reconciliation exact in all four panels |
| Drug-role block | **Moderate** | One column only. The shipped analytic dataset is the sole available version of this cohort, and Table 4 purports to describe it; but no independent witness exists |
| Reporter type | **Unverifiable** | `occp_cod` is absent from every shipped dataset. Left unchanged |

**Open item for the authors.** `ObesityAll_14_Drugs_Adolescent_48cols.xlsx` and
`FAERS_Pediatric_ML_Dataset.xlsx` are the upstream sources and are not in the package.
If either is available, the drug-role split and reporter type should be re-derived from
it to confirm or override the corrections above. Nothing else in the manuscript depends
on them.

## 7. Values deliberately NOT changed

The primary scientific results were untouched and re-verified against S8: 2,098
drug-event pairs, 360 ROR signals, 105 four-metric concordant, 13 rounding notes;
metformin–lactic acidosis (N = 214, ROR 61.22, CI 25.21–148.68),
semaglutide–optic ischaemic neuropathy (N = 14, ROR 439.23, CI 99.33–1942.26,
EBGM 18.79, EB05 11.67), dapagliflozin–cardiac failure (N = 30, ROR 40.24,
CI 22.90–70.71), atorvastatin–myalgia (N = 46, ROR 16.89). Raw 7,612,804 →
deduplicated 6,985,217 → adolescent 403,278. All ML metrics unchanged.
