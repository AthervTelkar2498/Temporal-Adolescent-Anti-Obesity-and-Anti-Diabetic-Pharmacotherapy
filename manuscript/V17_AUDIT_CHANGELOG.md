# V17 audit changelog

Independent audit of the V16 package against the PLOS ONE criteria, the submission and
formatting guidelines in this package, and the reference papers in `Adolsence Paper/`.
Every numerical claim was traced to the shipped code, data and workbooks. Numbers were
corrected only where the evidence required it; nothing was tuned toward a desired value.

## Verified correct — left untouched

- Citation numbering. First-appearance order is exactly 1..N in the .tex, .pdf and .docx;
  no orphans, no over-numbered references. Markers such as `[7]` appearing after `[10]`
  are legitimate re-citations under Vancouver numbering, and the PLOS ONE reference paper
  (`Adolsence Paper/1.pdf`, Zhou et al.) uses the identical convention.
- Fig 1 arithmetic: 7,612,804 - 627,587 = 6,985,217; - 6,581,939 = 403,278. Exact.
- Panel counts 11,701 / 10,701 / 5,208 / 342, and S9 quarterly volumes, which sum to them.
- S8: 2,098 pairs, 360 ROR signals, 105 four-metric concordant. All three exact.
- Every headline ROR / CI / N in the manuscript matches S8 to the decimal.
- All ML values match `results_temporal.json` exactly, including Table 5.
- S7 split sizes 6,831 / 2,058 / 2,812, reproduced by re-running the chronological split.
- Fig 2 percentages match the Results text for both panels.
- All figures: content, resolution (300 dpi), dimensions (within PLOS limits), no Type 3
  fonts. **No figure was altered.**

## Corrected

1. **2025 test partition described inaccurately.** Methods claimed the temporal test used
   "exclusively genuinely observed outcomes". `train_temporal.py` applies no such filter
   and loads the fully imputed dataset. Methods, Results and the READMEs now describe
   what the code does.
2. **Macro-F1 convention stated.** 0.389 is over the five classes present in the 2025
   partition; Required Intervention has zero test support. The six-class value of 0.324
   is now reported as a sensitivity analysis. (0.3245 x 6/5 = 0.38937.)
3. **Random-split 0.629 caveated** in the abstract, Results and Discussion. Its own
   results file records that this pipeline fits encoders and scaler before splitting.
4. **Reference [15] removed.** "Chen H, Wang X, Liu Y, Zhang J, Li M. Drug-induced
   movement disorders in pediatric patients. Ther Innov Regul Sci. 2024;58(3):489-501"
   could not be located in PubMed across multiple searches, although that journal is
   PubMed-indexed. The clause citing it was rewritten; its two other uses (both about sex
   distribution) now cite [6] (Phan et al.), which genuinely supports the claim.
5. **Reference [14] was cited for the wrong claim.** Lai et al. is a general-population
   ARDS study (median age 55). The sentence no longer describes it as paediatric.
6. **Three verified references added**, with metadata confirmed against PubMed and the
   source PDF: Qin et al. (PLoS One 2026;21(6):e0349218 - the four-metric precedent, and
   `Adolsence Paper/3.pdf`), Cai et al. (JAMA Ophthalmol 2025;143(4):304-314), and
   Abdelaal et al. (Ophthalmology 2026;133(6):799-810).
7. **Semaglutide-NAION balanced.** The Discussion cited only Hathaway 2024. The 2025-26
   literature is more equivocal and is now cited alongside it.
8. **Reference [17] completed** with volume and issue: PLoS One 2025;20(12):e0328465.
9. **All references renumbered** by order of first appearance after those changes.
   37 references; sequence verified 1..37 in .tex, .pdf and .docx.
10. **Table 4 note corrected.** The old note said counts were at "report x drug level",
    which contradicted the arithmetic (observed categories + Missing = panel total). The
    note now explains that Table 4 is the observed distribution and that the ML dataset
    differs because missing outcomes were pseudo-labelled - which is what resolves the
    RI 343 vs 5 and DS 195 vs 114 discrepancies.
11. **Metformin suspect-role wording.** 55% + 45% = 100%, so "in the majority of these
    reports" was wrong; it is all of them.
12. **Fig 2 legend corrected.** It claimed to show "each study panel" but shows two. The
    denominator (reports, not events) and the non-additivity are now stated.
13. **EBGM prior disclosed as fixed** rather than estimated by maximum likelihood.
14. **S8 legend** now notes the 13 rounding-flagged pairs.
15. **Leakage wording in Methods.** "Excluded to prevent data leakage" overstated the
    case while `pt_term` was retained; the residual leakage is now stated there too.
16. **Drug-specific adverse event profiles shortened by 12.7%** (893 -> 780 words). Only
    duplicated interpretation and one content-free sentence were removed. Every N, ROR,
    confidence interval and four-metric concordance flag is retained, as are the metformin
    self-harm suspect-role caveat, the dapagliflozin death-outcome causal caveat and the
    insulin glargine secondary-suspect detail.

## Supporting information

- **S6**: `pt_term` was classified "Leakage Risk: Low - Retained", contradicting the
  manuscript's own Limitations. Reclassified as HIGH / partial target leakage, retained
  with disclosure, with a note giving the NO_PT and PT-lookup numbers.
- **S2, S3**: the "Location in V12" column header pointed at a version that is not being
  submitted. Now "Location in manuscript".
- S1, S4, S5, S7, S8, S9 unchanged.

## Word file

The V16 `.docx` had **diverged from the LaTeX**. Its abstract read "a primary
chronological temporal temporal Macro-F1" and, in both the abstract and the Results, it
**omitted the disclosure that the Preferred-Term lookup outperformed XGBoost** - the
single most important honesty statement in the paper. It also lacked the Table 4
explanatory note and the metformin suspect-role sentence.

The V17 `.docx` is generated from the corrected `.tex`, so the two cannot diverge again.
Math is converted to Unicode before conversion, so all five tables and every McNemar
p-value are preserved.

## Not changed, and why

- **Figures.** No content error was found. The only figure issue is font embedding, which
  cannot be fixed without Arial installed - see README item 2.
- **The ML component.** Retained in full, as instructed. The audit found no reason to
  remove it; its central weakness is disclosed more fully than in most published FAERS+ML
  work.
- **The Zenodo DOI.** Left as-is. It is the authors' record to publish; substituting a
  different identifier would be a guess.
- **Page count.** 25 -> 26 pages. The 113-word compression was outweighed by roughly 400
  words of required scientific qualification. Reaching 22 pages would mean deleting
  content the audit found necessary, which was explicitly out of scope. Page fill was
  checked: only the title page and the final page are sparse, so there is no layout
  whitespace to reclaim.


## Additional work this session (no package changes resulted)

### EPS font compliance — investigated, not fixed, reverted cleanly
Tested whether matplotlib's `ps.useafm` mode (renders EPS text through the base-14
PostScript Helvetica via bundled AFM metrics, no font embedded at all) could resolve
the Fig1/Fig3/Fig4/S1_Fig font-name issue without needing real Arial installed.

It does NOT work cleanly for these figures and was reverted rather than shipped:
- Plain text renders correctly as pure `/Helvetica` - verified byte-for-byte in the
  raw EPS PostScript stream.
- The `>=` and `->` characters these flowcharts use are outside base AFM Helvetica's
  encoding: rendered naively, `>=` silently became a `?` glyph and `->` vanished
  entirely - confirmed by inspecting the actual glyph names in the output. This
  would have been a *worse* defect than a font-naming issue: a scientific figure
  silently misreading "N >= 3" as "N ? 3".
- Routing those specific characters through mathtext (`$\geq$`, `$\rightarrow$`)
  fixes that, verified correct in isolation - but multi-line strings mixing plain
  text with mathtext, and matplotlib's own `LogFormatterSciNotation` (used for the
  forest plots' log-scale axis ticks), both leak **unembedded** references to
  `LiberationSans`/`DejaVuSans` regardless of `ps.useafm`. Confirmed these are bare
  name references with no embedded font program (no `/FontType 42`, no
  `/CharStrings`) - meaning the file would show missing glyphs on a system without
  that exact font, which is a worse and less consistent failure mode than the
  original single-font Liberation Sans embedding.

All four figures and `regen_figs.py` were reverted to their exact pre-session state
(byte-identical, re-verified by checksum) rather than ship this. The blocker
description in README item 2 is unchanged: this still needs a real Arial (or
Helvetica) TrueType install to regenerate cleanly with the original script's
existing font-detection logic.

### Reference audit extended
14 of 37 references now individually verified against PubMed/Consensus (up from 6
in the first pass), including all four disproportionality-method foundation papers
(Rothman 2004/ROR, Evans 2001/PRR, Bate 1998/BCPNN, DuMouchel 1999/MGPS), both
adolescent RCTs (Weghuber 2022 semaglutide, Kelly 2020 liraglutide), and every
specific numerical epidemiology claim checked (Mayer-Davis 2017's 4.8%/year type 2
diabetes incidence increase, confirmed word-for-word in the abstract). Zero further
errors found. One nuance worth knowing rather than an error: Wang et al. 2024 (Nat
Med, cited for "psychiatric effects including suicidal ideation reported with some
AOMs") is accurately cited for the existence of that regulatory concern, but the
paper's own finding was reassuring (lower, not higher, suicidal-ideation risk with
semaglutide) - the citation supports what it's cited for, but a reviewer who reads
it closely should not come away thinking it corroborates elevated risk.

The remaining ~23 references (government/organizational URLs, MedDRA documentation,
and well-established citations such as Chen & Guestrin's XGBoost paper and Efron &
Tibshirani's bootstrap text) were not individually re-verified this session.
