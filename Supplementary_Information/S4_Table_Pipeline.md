# S4 Table: The 13-stage dataset acquisition, cleaning and preparation pipeline.

This pipeline documents the deterministic steps applied to the raw FAERS ASCII files prior to machine learning analysis.

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
14. **Step 13: Quality Gate** – Displays a pipeline dashboard preview. Writes to PostgreSQL are locked until human approval.
