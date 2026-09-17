# PLOS ONE compliance audit — V18

Every row below was checked against the supplied `PLOSNE Guidelines/` and the actual
files in this package, not against assumption.

| # | Area | Result | Evidence |
|---|---|---|---|
| 1 | **Scientific validity** | PASS | Table 4 provenance resolved; all four panels sum exactly to N; no primary result altered |
| 2 | Publication criteria | PASS | Original, not under consideration elsewhere; conclusions supported |
| 3 | **Ethics** | PASS | Expanded to a detailed non-exemption rationale. The "relevant regulations" clause in the supplied guidelines sits in the **animal** research section; human-subjects requires a detailed statement, which is now given. No regulation invented |
| 4 | **Data availability** | PASS | Rewritten. No longer claims the disproportionality source code is public — it is not. Three limitations stated explicitly |
| 5 | Title / short title | PASS | Unchanged |
| 6 | **Abstract** | PASS | **296 words** (limit 300), recounted from the compiled PDF |
| 7 | Headings | PASS | 3 levels maximum |
| 8 | **Tables** | PASS | 5 tables; Table 4 note moved **below** the table per PLOS; all tables editable, none an image |
| 9 | **Figures** | PASS | All PNGs 300 DPI; all within PLOS dimension limits; EPS + PNG retained |
| 10 | **Equations** | PASS | 4 genuine formulae are Word equation objects; single symbols left as Unicode per PLOS |
| 11 | References | PASS | 0 undefined; unsupported claim on ref [30] corrected |
| 12 | **Supporting Information** | PASS | S1–S9 numbered and cross-referenced; obsolete-metric sweep returns **0** |
| 13 | Line numbers | PASS | Continuous, in both PDF and DOCX |
| 14 | Page numbers | PASS | Present in both |
| 15 | Double spacing | PASS | Body double-spaced |
| 16 | Single column | PASS | Confirmed |
| 17 | **DOCX editability** | PASS | 5 real Word tables, 4 equation objects, 0 page images, 0 LaTeX leakage |
| 18 | **TEX/PDF/DOCX consistency** | PASS | All 10 checked values agree across all three; all 8 forbidden strings absent |
| 19 | **ML reproducibility** | PASS | Every reported metric matches `code/results_temporal.json` to 5 dp |
| 20 | **Signal detection** | PASS | 2,098 / 360 / 105 / 13 verified directly against S8 |
| 21 | **MedDRA** | PASS | Excluded from every public artefact; licensing stated |
| 22 | **Repository hygiene** | PASS | 0 private paths, 0 duplicates, 0 build artefacts in the public tree |
| 23 | **Cover letter** | PASS | 0 placeholders; no names invented; code claim corrected |
| 24 | Compilation | PASS | 27 pages, **0 errors, 0 undefined references** |

## Figures — font decision

Fig 1, Fig 3, Fig 4 and S1 Fig embed **Liberation Sans**; Fig 2 and S2 Fig embed
**ArialMT**. The supplied `PLOSNE Guidelines/Submission Guidelines.txt` states: *use any
standard font except the font named "Symbol"*. Liberation Sans is a standard,
metrically Arial-compatible font and is therefore compliant. **No figure was
regenerated** — per instruction, fonts were not changed merely because they differ.
The V17 README claim that Liberation Sans "is not on the PLOS accepted font list" is not
supported by the supplied guidelines and has been removed.

Note that `regen_figs.py` can regenerate only Fig 1, 3, 4 and S1 — precisely the
Liberation Sans figures. Fig 2 needs the licensed MedDRA mapping and S2 Fig needs the
fitted model, so a fully uniform font pass is not possible from this package alone.

## Open items for the authors

1. **Drug-role split (moderate confidence).** Corrected from the analytic data, which is
   the only available version of this cohort. Unlike the outcome block it has no second
   internal witness. Re-derive from `ObesityAll_14_Drugs_Adolescent_48cols.xlsx` to
   confirm.
2. **Reporter type (unverifiable).** `occp_cod` is absent from every shipped dataset.
   Left unchanged; cannot be checked from this package.
3. **GitHub URL.** Returned 404 when this package was assembled. Removed from the
   manuscript. Restore only after confirming the repository is public.
4. **Zenodo.** No V18 version has been deposited; none is quoted. The concept DOI
   10.5281/zenodo.22767355 is cited, which is correct regardless of version.
5. **Cover letter length** is ~1.3 pages against PLOS's one-page preference.

## Verdict

# 🟡 CONDITIONAL GO

The blocking issue is resolved: the Table 4 discrepancy is explained, the pipeline is
sound, and every primary result verifies against source. The manuscript, PDF, DOCX,
SI, figures, cover letter and README are internally consistent with zero forbidden
values remaining.

It is conditional on items 1–3 above — two Table 4 rows that cannot be independently
confirmed without a file not supplied, and a repository URL that does not currently
resolve. None affects a scientific result. Submission should not proceed until the
authors confirm the drug-role split and the reporter-type row against the 48-column
source.
