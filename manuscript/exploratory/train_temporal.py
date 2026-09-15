#!/usr/bin/env python3
"""
Temporal (chronological) evaluation of case-level outcome triage on the
adolescent FAERS obesity-related panel.

WHAT THIS SCRIPT IS FOR
-----------------------
The manuscript describes a chronological evaluation -- train 2021Q1-2023Q4,
validate on 2024, test on 2025 -- with training-only preprocessing, a set of
baseline classifiers, McNemar's test and bootstrap confidence intervals.
No code implementing that existed in the package. This script implements it,
end to end, from the one dataset that carries a time column:

    Obesity Drugs & Diabetic Drugs & MEDRA/15 Columns Model with Source Quarter.zip
        -> ObesityAll_14_Drugs_Adolescent_14Columns_Imputed.xlsx  (has source_quarter)

Whatever numbers this script prints ARE the reproducible numbers. It does not
target, back-calculate, or tune towards any previously reported value.

WHAT IT DOES
------------
1. Chronological split on source_quarter (no shuffling, no stratification).
2. Preprocessing fitted on TRAIN ONLY. Label encoders, medians and the scaler
   are learned from the training quarters and then applied unchanged to
   validation and test. Categories unseen in training map to a reserved
   "<UNSEEN>" index rather than leaking a new level into the encoder.
3. Models: majority-class, logistic regression, decision tree, random forest
   and gradient boosting (XGBoost where available).
4. Two feature sets, to quantify the pt_term circularity:
      FULL  - all 13 features, including pt_term
      NO_PT - the same 12 features with pt_term removed
   The shipped outcome column was imputed from pt_term for the ~50% of reports
   with no recorded outcome, so pt_term is partly the source of the target.
5. A PT-only lookup baseline: predict each report's outcome as the majority
   outcome of its Preferred Term in the TRAINING data. This is the baseline
   that matters. If it rivals the model, the model is largely re-learning the
   imputation rule.
6. McNemar's test (chi-square with continuity correction, exact binomial when
   b+c is small) for the gradient-boosted model against every baseline.
7. Bootstrap percentile CIs (1,000 resamples) for Macro-F1.
8. A separate random-split replication (80/20, stratified, seed 42) to settle
   which random-split figure is authoritative.

USAGE
-----
    python code/train_temporal.py                 # from the package root
    python code/train_temporal.py --boot 1000

Outputs code/results_temporal.json and prints a summary table.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import warnings
import zipfile

import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

warnings.filterwarnings("ignore")
SEED = 42
np.random.seed(SEED)

# --------------------------------------------------------------- gradient booster
try:
    import xgboost as xgb
    HAS_XGB = True
    BOOSTER_NAME = f"XGBoost {xgb.__version__}"
except Exception:
    from sklearn.ensemble import HistGradientBoostingClassifier
    HAS_XGB = False
    BOOSTER_NAME = "HistGradientBoosting (sklearn) -- XGBoost NOT INSTALLED"
    print("=" * 78)
    print("WARNING: xgboost is not installed in this environment.")
    print("Falling back to sklearn HistGradientBoostingClassifier so the pipeline")
    print("still runs. The reported gradient-boosting numbers are therefore NOT")
    print("XGBoost numbers. Install xgboost and re-run before quoting them.")
    print("=" * 78)

FEATURES_FULL = ["age_years", "sex", "weight_kg", "drug_seq", "route", "role_cod",
                 "drugname_normalized", "rxcui", "dose_amt", "dose_unit",
                 "dose_form", "indi_pt", "pt_term"]
FEATURES_NOPT = [c for c in FEATURES_FULL if c != "pt_term"]
NUMERIC = ["age_years", "weight_kg", "drug_seq", "dose_amt"]
TARGET = "outc_cod"
UNSEEN = "<UNSEEN>"


# --------------------------------------------------------------- data
def load(root: str) -> pd.DataFrame:
    """Load the only dataset in the package that carries a time column."""
    zpath = os.path.join(root, "Obesity Drugs & Diabetic Drugs & MEDRA",
                         "15 Columns Model with Source Quarter.zip")
    inner = ("15 Columns Model with Source Quarter/"
             "ObesityAll_14_Drugs_Adolescent_14Columns_Imputed.xlsx")
    if not os.path.exists(zpath):
        raise FileNotFoundError(f"Dataset archive not found: {zpath}")
    with zipfile.ZipFile(zpath) as z:
        with z.open(inner) as fh:
            df = pd.read_excel(fh)
    if "source_quarter" not in df.columns:
        raise ValueError("source_quarter column absent -- a temporal split is "
                         "impossible from this file.")
    df["year"] = df["source_quarter"].astype(str).str.slice(0, 4).astype(int)
    return df


def chrono_split(df: pd.DataFrame):
    tr = df[df.year.between(2021, 2023)].copy()
    va = df[df.year == 2024].copy()
    te = df[df.year == 2025].copy()
    return tr, va, te


def fit_preprocessor(train: pd.DataFrame, feats: list[str]):
    """Learn every transform from the training rows only."""
    cats = [c for c in feats if c not in NUMERIC]
    maps, medians = {}, {}
    for c in cats:
        vals = train[c].fillna("UNKNOWN").astype(str)
        levels = [UNSEEN] + sorted(vals.unique().tolist())
        maps[c] = {v: i for i, v in enumerate(levels)}
    for c in NUMERIC:
        medians[c] = pd.to_numeric(train[c], errors="coerce").median()
    return {"maps": maps, "medians": medians, "cats": cats, "feats": feats}


def apply_preprocessor(pp, frame: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(index=frame.index)
    for c in NUMERIC:
        if c not in pp["feats"]:
            continue
        v = pd.to_numeric(frame[c], errors="coerce")
        fill = pp["medians"][c]
        out[c] = v.fillna(0 if c == "dose_amt" else fill)
    for c in pp["cats"]:
        v = frame[c].fillna("UNKNOWN").astype(str)
        out[c] = v.map(pp["maps"][c]).fillna(pp["maps"][c][UNSEEN]).astype(int)
    return out[pp["feats"]]


# --------------------------------------------------------------- metrics
def macro_f1(y, p):
    return float(f1_score(y, p, average="macro", zero_division=0))


def boot_ci(y, p, n=1000, seed=SEED):
    rng = np.random.default_rng(seed)
    y, p = np.asarray(y), np.asarray(p)
    idx = np.arange(len(y))
    vals = []
    for _ in range(n):
        s = rng.choice(idx, size=len(idx), replace=True)
        if len(np.unique(y[s])) < 2:
            continue
        vals.append(macro_f1(y[s], p[s]))
    if not vals:
        return (float("nan"), float("nan"))
    return (float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5)))


def mcnemar(y, p1, p2):
    """p1 = model under test, p2 = comparator. b = p1 right & p2 wrong."""
    y, p1, p2 = np.asarray(y), np.asarray(p1), np.asarray(p2)
    c1, c2 = (p1 == y), (p2 == y)
    b = int(np.sum(c1 & ~c2))
    c = int(np.sum(~c1 & c2))
    n = b + c
    if n == 0:
        return dict(b=b, c=c, stat=None, p=None, test="undefined (b+c=0)")
    if n < 25:
        from scipy.stats import binomtest
        p = binomtest(b, n, 0.5).pvalue
        return dict(b=b, c=c, stat=None, p=float(p), test="exact binomial")
    from scipy.stats import chi2
    stat = (abs(b - c) - 1) ** 2 / n
    return dict(b=b, c=c, stat=float(stat), p=float(chi2.sf(stat, 1)),
                test="chi-square (continuity corrected)")


def make_booster():
    if HAS_XGB:
        return xgb.XGBClassifier(n_estimators=100, random_state=SEED, n_jobs=-1,
                                 eval_metric="mlogloss")
    from sklearn.ensemble import HistGradientBoostingClassifier
    return HistGradientBoostingClassifier(max_iter=100, random_state=SEED)


def models():
    return {
        "Majority class": DummyClassifier(strategy="most_frequent"),
        "Logistic regression": LogisticRegression(max_iter=2000, random_state=SEED),
        "Decision tree": DecisionTreeClassifier(random_state=SEED),
        "Random forest": RandomForestClassifier(n_estimators=100, random_state=SEED, n_jobs=-1),
        "Gradient boosting": make_booster(),
    }


def pt_lookup(train, target_frame):
    """Majority outcome per Preferred Term, learned on TRAIN, applied elsewhere."""
    maj = train.groupby("pt_term")[TARGET].agg(lambda s: s.value_counts().idxmax())
    fallback = train[TARGET].value_counts().idxmax()
    return target_frame["pt_term"].map(maj).fillna(fallback).values


# --------------------------------------------------------------- runs
def run_featureset(tr, va, te, feats, label, boot):
    pp = fit_preprocessor(tr, feats)
    Xtr, Xva, Xte = (apply_preprocessor(pp, f) for f in (tr, va, te))
    sc = StandardScaler().fit(Xtr)                       # TRAIN ONLY
    Xtr_s, Xva_s, Xte_s = sc.transform(Xtr), sc.transform(Xva), sc.transform(Xte)

    classes = sorted(tr[TARGET].astype(str).unique())
    cmap = {c: i for i, c in enumerate(classes)}
    ytr = tr[TARGET].astype(str).map(cmap).values
    yva = va[TARGET].astype(str).map(cmap).fillna(-1).astype(int).values
    yte = te[TARGET].astype(str).map(cmap).fillna(-1).astype(int).values

    out, preds = {}, {}
    for name, m in models().items():
        m.fit(Xtr_s, ytr)
        pv, pt_ = m.predict(Xva_s), m.predict(Xte_s)
        preds[name] = pt_
        lo, hi = boot_ci(yte, pt_, boot)
        out[name] = dict(val_macro_f1=macro_f1(yva, pv),
                         test_macro_f1=macro_f1(yte, pt_),
                         test_macro_f1_ci95=[lo, hi])
    return dict(features=feats, n_features=len(feats), label=label,
                classes=classes, results=out), preds, yte, classes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--boot", type=int, default=1000)
    a = ap.parse_args()
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    df = load(root)
    tr, va, te = chrono_split(df)
    print(f"\n[booster] {BOOSTER_NAME}")
    print(f"[data] total={len(df)}  train 2021-2023={len(tr)}  "
          f"val 2024={len(va)}  test 2025={len(te)}")
    print(f"[data] train quarters: {sorted(tr.source_quarter.unique())[0]} .. "
          f"{sorted(tr.source_quarter.unique())[-1]}")
    print("[data] test outcome distribution:",
          te[TARGET].value_counts().to_dict())

    report = {"booster": BOOSTER_NAME, "xgboost_available": HAS_XGB,
              "seed": SEED, "n_total": len(df), "n_train": len(tr),
              "n_val": len(va), "n_test": len(te),
              "train_years": "2021-2023", "val_year": 2024, "test_year": 2025}

    full, preds_full, yte, classes = run_featureset(tr, va, te, FEATURES_FULL, "FULL (13 feats, incl. pt_term)", a.boot)
    nopt, preds_nopt, _, _ = run_featureset(tr, va, te, FEATURES_NOPT, "NO_PT (12 feats, pt_term removed)", a.boot)
    report["temporal_FULL"] = full
    report["temporal_NO_PT"] = nopt

    # PT-only lookup baseline
    cmap = {c: i for i, c in enumerate(classes)}
    pt_pred = pd.Series(pt_lookup(tr, te)).astype(str).map(cmap).fillna(-1).astype(int).values
    lo, hi = boot_ci(yte, pt_pred, a.boot)
    report["pt_only_lookup"] = dict(test_macro_f1=macro_f1(yte, pt_pred),
                                    test_macro_f1_ci95=[lo, hi])
    preds_full["PT-only lookup"] = pt_pred

    # McNemar: gradient booster (FULL) vs everything else
    gb = preds_full["Gradient boosting"]
    report["mcnemar_vs_gradient_boosting"] = {
        k: mcnemar(yte, gb, v) for k, v in preds_full.items() if k != "Gradient boosting"}
    report["mcnemar_vs_gradient_boosting"]["Gradient boosting (NO_PT)"] = mcnemar(
        yte, gb, preds_nopt["Gradient boosting"])

    # per-class detail for the headline model
    report["per_class_gradient_boosting_FULL"] = classification_report(
        yte, gb, labels=list(range(len(classes))), target_names=classes, zero_division=0, output_dict=True)
    report["confusion_gradient_boosting_FULL"] = confusion_matrix(yte, gb).tolist()

    # ---- random-split replication, to settle 0.635 vs 0.625
    pp = fit_preprocessor(df, FEATURES_FULL)
    X = apply_preprocessor(pp, df)
    y = df[TARGET].astype(str).map({c: i for i, c in enumerate(sorted(df[TARGET].astype(str).unique()))}).values
    Xa, Xb, ya, yb = train_test_split(StandardScaler().fit_transform(X), y,
                                      test_size=0.2, random_state=SEED, stratify=y)
    rnd = {}
    for name, m in models().items():
        m.fit(Xa, ya)
        rnd[name] = macro_f1(yb, m.predict(Xb))
    report["random_split_fit_on_all_like_shipped_script"] = rnd
    report["random_split_note"] = (
        "Replicates the shipped script exactly, INCLUDING its preprocessing "
        "leakage (encoders/scaler fitted on the full dataset before splitting). "
        "Reported only to adjudicate the 0.635 vs 0.625 discrepancy, not as a "
        "recommended result.")

    with open(os.path.join(root, "code", "results_temporal.json"), "w") as fh:
        json.dump(report, fh, indent=2)

    # ---- summary
    print("\n" + "=" * 78)
    print("TEMPORAL EVALUATION  (train 2021-2023 | validate 2024 | test 2025)")
    print("=" * 78)
    print(f"{'model':26s}{'val F1':>10s}{'test F1':>10s}{'95% CI':>20s}")
    for tag, blk in (("FULL", full), ("NO_PT", nopt)):
        print(f"-- feature set: {blk['label']}")
        for k, v in blk["results"].items():
            ci = v["test_macro_f1_ci95"]
            print(f"  {k:24s}{v['val_macro_f1']:10.4f}{v['test_macro_f1']:10.4f}"
                  f"{f'[{ci[0]:.3f}, {ci[1]:.3f}]':>20s}")
    p = report["pt_only_lookup"]
    pci = p["test_macro_f1_ci95"]
    print(f"  {'PT-only lookup baseline':24s}{'--':>10s}{p['test_macro_f1']:10.4f}"
          f"{'[%.3f, %.3f]' % (pci[0], pci[1]):>20s}")
    print("\nMcNemar vs gradient boosting (FULL):")
    for k, v in report["mcnemar_vs_gradient_boosting"].items():
        pv = "n/a" if v["p"] is None else f"{v['p']:.3e}"
        print(f"  {k:30s} b={v['b']:5d} c={v['c']:5d}  p={pv:>12s}  [{v['test']}]")
    print("\nRandom-split replication (shipped-script conditions):")
    for k, v in rnd.items():
        print(f"  {k:26s}{v:10.4f}")
    print("\n[written] code/results_temporal.json")


if __name__ == "__main__":
    main()
