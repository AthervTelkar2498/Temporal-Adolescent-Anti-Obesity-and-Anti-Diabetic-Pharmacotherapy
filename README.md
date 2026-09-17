# PLOS ONE submission package — V18 FINAL COMPLETE

**Manuscript:** Safety of anti-obesity and anti-diabetic medications in adolescents:
A disproportionality analysis and machine-learning validation from 2021–2025 on the
basis of the FAERS database

Telkar A, Telkar A, Javalgikar A, Madanwale N, Ruikar D, Baligar P.

> **V18 supersedes V17.** The substantive change in V18 is a corrected Table 4 outcome
> block. See `PROVENANCE_TABLE4.md` — read that before citing any outcome count.

---

## What changed in V18

| # | Change | Evidence |
|---|---|---|
| 1 | **Table 4 outcome distribution corrected** in all four panels | `PROVENANCE_TABLE4.md` |
| 2 | Outcome-missingness range corrected to **33.9–53.1%** (was 45.9–51.3%) in Methods, Results and Discussion | recomputed from the analytic datasets |
| 3 | Table 4 note moved **below** the table and rewritten to match the pipeline | PLOS: legends/footnotes below tables |
| 4 | Reference [30] — an unsupported concordance claim **removed** | S8: ataxia and areflexia absent; rhabdomyolysis ROR 0.77 and muscular weakness ROR 0.76 are non-signals |
| 5 | Data Availability rewritten — no longer claims the disproportionality source code is public | the code is genuinely not in the package |
| 6 | Ethics statement expanded to a detailed non-exemption rationale | no regulation invented |
| 7 | Abstract reduced to **296 words** (PLOS limit 300) | recounted from the compiled PDF |
| 8 | S2 and S7 updated to the verified final ML metrics; three obsolete values replaced throughout the SI | `code/results_temporal.json` |
| 9 | The four disproportionality formulae are now **Word equation objects** | PLOS equation policy |
| 10 | Duplicate code copies consolidated; private absolute filesystem paths removed | see below |

---

## Verified results — do not alter without re-deriving

**Signal detection** (all three verified against `Supporting_Documents/S8_Table_Complete_Signal_Detection_FULL.xlsx`)

| Quantity | Value |
|---|---|
| Drug–event pairs evaluated (N ≥ 2) | 2,098 |
| Met ROR criteria (N ≥ 3, CI lower bound > 1) | 360 |
| Concordant across all four metrics | 105 |
| Pairs with a two-decimal rounding note | 13 |

Raw FAERS records 7,612,804 → deduplicated 6,985,217 → adolescent (12–17 y) 403,278.

**Machine learning** (XGBoost 3.2.0, seed 42, train-only preprocessing; reproduced from `code/results_temporal.json`)

| | Macro-F1 |
|---|---|
| Preferred-Term-only lookup (no model at all) | **0.594** (95% CI 0.545–0.626) |
| XGBoost, all 13 features, temporal 2025 test (N = 2,812) | 0.389 (95% CI 0.353–0.434) |
| XGBoost with `pt_term` removed | 0.222 |
| Random-split XGBoost (leakage-preserving, comparison only) | 0.629 |
| Random-split Random Forest | 0.563 |
| Six-class sensitivity analysis (RI as zero-support class) | 0.324 |

Required Intervention has **zero** test support in 2025, so its F1 is undefined; the
headline figure is the five-class Macro-F1. The lookup beats the model
(McNemar b = 134, c = 453, χ² = 172.27, p = 2.4 × 10⁻³⁹) because roughly half the
outcome labels were reconstructed from `pt_term`, which is also model feature 13.
The case-level results describe how outcome labels relate to reported event terms in
FAERS; they are **not** evidence of independent predictive capability.

---

## Repository archive

**Concept DOI (stable citation target, always resolves to the newest version):**
`10.5281/zenodo.22767355`

Version DOIs: V17.1 `10.5281/zenodo.22767981`, V17.0 `10.5281/zenodo.22767356`.

> **V17.1 predates the V18 corrections.** It is not the final manuscript version.
> Cite the **concept DOI** for a general archive reference. A new Zenodo version should
> be deposited once V18 is finalised; no V18 DOI exists yet and none is quoted anywhere
> in this package.

A GitHub repository was previously referenced in the Data Availability statement. At the
time this package was assembled that URL did **not** resolve publicly, so it has been
removed from the manuscript. Only the Zenodo concept DOI is cited. Restore a GitHub URL
only after confirming the repository is public.

---

## What is and is not reproducible from this package

| Component | Status |
|---|---|
| Temporal ML evaluation, baselines, McNemar, bootstrap CIs | runs end to end from the shipped data |
| Figures 1, 3, 4 and S1 Fig | `code/regen_figs.py` |
| Signal-detection results (S8 workbook) | shipped as output |
| ROR / PRR / IC / EBGM **computation code** | **not in this package** — only the S8 output |
| Pseudo-labelling (`compute_pseudo.py`) | needs `FAERS_Pediatric_ML_Dataset.xlsx`, not shipped |
| Seriousness-rule baseline (`phase2_baselines_temporal.py`) | needs `ObesityAll_14_Drugs_Adolescent_48cols.xlsx`, not shipped; contains absolute local paths |
| Fig 2 | needs the licensed MedDRA PT→SOC mapping |
| S2 Fig (SHAP) | needs the trained model object |

The scripts inside `Obesity Drugs & Diabetic Drugs & MEDRA/*.zip` perform a **random
80/20 split**, not a temporal one, and fit encoders and scaler on the full dataset before
splitting. They are retained as the historical record of what produced the results
workbook. `code/train_temporal.py` is the corrected implementation.

---

## MedDRA

Adverse events were coded to Preferred Terms by the FDA using the MedDRA version current
at each quarterly extract. **MedDRA version 28.1** was used by the authors to map those
PTs to primary System Organ Class and HLGT.

MedDRA is licensed by the MSSO. **No MedDRA distribution file is published in the public
repository or the Zenodo archive**, and MedDRA is not available from this project.
Reproducing the exact SOC mapping requires your own MedDRA licence from the MSSO.
The local master ZIP retains the licensed MedDRA archive for the owner's own records
only; it is excluded from every public artefact.

---

## Package layout

- `PONE_Condensed_V18_FINAL.tex` / `.pdf` — manuscript source and compiled PDF (27 pages,
  0 errors, 0 undefined references)
- `PONE_Condensed_V18_FINAL_EDITABLE.docx` — editable Word manuscript, synchronised with
  the TEX (27 pages, 5 real Word tables, 4 Word equation objects, continuous line
  numbering, page numbers, no page images, no LaTeX leakage)
- `PLOS_ONE_Cover_Letter_Corrected.docx` — no placeholders remaining
- `Figures/` — Fig 1–4 and S1/S2 Fig as EPS (submission) and PNG (preview, all 300 DPI)
- `Supporting_Documents/` — S1–S9
- `code/` — the single authoritative code location
- `PROVENANCE_TABLE4.md`, `V18_AUDIT_REPORT.md`, `MANIFEST.md`, `PUBLIC_GITHUB_TREE.md`
- `Obesity Drugs & Diabetic Drugs & MEDRA/` — analytic dataset variants (**local only**)
- `PLOSNE Guidelines/`, `Formatting Documents PLOSONE/`, `Adolsence Paper/` — reference
  material used during preparation (**local only**, not for publication)

Funding and competing-interest statements are entered in the submission system:

- Financial Disclosure: "The author(s) received no specific funding for this work."
- Competing Interests: "The authors have declared that no competing interests exist."

---

## Signal-detection criteria

| Metric | Criterion |
|---|---|
| ROR | 95% CI lower bound > 1 and N ≥ 3 |
| PRR | PRR ≥ 2, χ² ≥ 4, N ≥ 3 |
| IC | IC₀₂₅ > 0 |
| EBGM | EB05 ≥ 2 |

The EBGM prior hyperparameters (α₁ = 0.2, β₁ = 0.06; α₂ = 1.4, β₂ = 1.8; w = 0.1) were
**fixed** rather than estimated by maximum likelihood — a simplification of the original
GPS procedure, stated in the manuscript.
