"""
Phase 2 Experiment Suite — Peer Review Methodological Improvements
==================================================================
Tasks 2.1–2.3: Baseline Comparisons, Temporal Validation, Leakage-Safe Imputation

Runs on the 48-column Obesity All dataset (N=11,701) which contains source_quarter
for temporal splitting and severity indicators for rule-based baselines.

Output: Console summary tables + CSV results for manuscript integration.
"""

import sys, os, warnings, time
sys.stdout.reconfigure(encoding='utf-8')
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (accuracy_score, f1_score, classification_report, 
                             precision_score, recall_score)
from sklearn.dummy import DummyClassifier
import xgboost as xgb

# ─── Configuration ───
import argparse

_ap = argparse.ArgumentParser(description="Phase 2 baseline / temporal / leakage-safe imputation suite.")
_ap.add_argument("--data", default=os.environ.get("OBESITY_48COL",
                 "ObesityAll_14_Drugs_Adolescent_48cols.xlsx"),
                 help="Path to the 48-column obesity dataset. NOT distributed with this "
                      "repository; supply your own copy.")
_ap.add_argument("--out", default=os.environ.get("PHASE2_OUT", "phase2_results"),
                 help="Directory for CSV outputs (created if absent).")
_args = _ap.parse_args()

DATA_48COL = _args.data
OUT_DIR = _args.out

if not os.path.exists(DATA_48COL):
    sys.exit(f"Input dataset not found: {DATA_48COL}\n"
             "ObesityAll_14_Drugs_Adolescent_48cols.xlsx is not shipped with this "
             "repository. Rebuild it from the FAERS quarterly ASCII files using the "
             "pipeline specification in S4 Table, then pass it with --data.")

os.makedirs(OUT_DIR, exist_ok=True)

FEATURE_COLS_13 = [
    'age_years', 'sex', 'weight_kg', 'drug_seq', 'route', 'role_cod',
    'drugname_normalized', 'rxcui', 'dose_amt', 'dose_unit', 'dose_form',
    'indi_pt', 'pt_term'
]

SEED = 42
np.random.seed(SEED)


def load_and_impute(df, compute_mapping_on=None):
    """
    Two-stage imputation.
    If compute_mapping_on is provided, the pt_term→mode mapping is computed
    on that subset only (leakage-safe). Otherwise, computed on non-missing rows of df.
    """
    df = df.copy()
    if 'severity_score' in df.columns:
        df['severity_score'] = df['severity_score'].fillna(0)
    
    # Stage 1: pt_term mode mapping
    if compute_mapping_on is not None:
        base = compute_mapping_on.dropna(subset=['outc_cod'])
    else:
        base = df.dropna(subset=['outc_cod'])
    
    pt_term_mode = base.groupby('pt_term')['outc_cod'].agg(
        lambda x: x.mode().iloc[0] if len(x) > 0 else None
    )
    
    missing_mask = df['outc_cod'].isna()
    imputed_pt = 0
    imputed_sev = 0
    
    for idx in df[missing_mask].index:
        pt = df.at[idx, 'pt_term']
        if pt in pt_term_mode.index and pd.notna(pt_term_mode[pt]):
            df.at[idx, 'outc_cod'] = pt_term_mode[pt]
            imputed_pt += 1
    
    # Stage 2: severity fallback
    still_missing = df['outc_cod'].isna()
    for idx in df[still_missing].index:
        is_fatal = df.at[idx, 'is_fatal'] if 'is_fatal' in df.columns else 0
        sev = df.at[idx, 'severity_score'] if 'severity_score' in df.columns else 0
        is_serious = df.at[idx, 'is_serious'] if 'is_serious' in df.columns else 0
        
        if is_fatal == 1:
            df.at[idx, 'outc_cod'] = 'DE'
        elif pd.notna(sev) and sev >= 4:
            df.at[idx, 'outc_cod'] = 'LT'
        elif pd.notna(sev) and sev >= 3:
            df.at[idx, 'outc_cod'] = 'HO'
        elif is_serious == 1:
            df.at[idx, 'outc_cod'] = 'OT'
        else:
            df.at[idx, 'outc_cod'] = 'OT'
        imputed_sev += 1
    
    return df, imputed_pt, imputed_sev


def prepare_features(df, feature_cols):
    """Encode features and return X as numpy array."""
    X = df[feature_cols].copy()
    
    # Fill missing numeric
    for col in ['age_years', 'weight_kg', 'drug_seq', 'dose_amt']:
        if col in X.columns:
            X[col] = X[col].fillna(X[col].median())
    if 'severity_score' in X.columns:
        X['severity_score'] = X['severity_score'].fillna(0)
    
    # Encode categoricals
    cat_cols = [c for c in ['sex', 'route', 'role_cod', 'drugname_normalized', 
                            'rxcui', 'dose_unit', 'dose_form', 'indi_pt', 'pt_term'] 
                if c in X.columns]
    for col in cat_cols:
        X[col] = X[col].astype(str).fillna('UNKNOWN')
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col])
    
    return X.values


def seriousness_rule_baseline(df):
    """Deterministic rule-based predictor using seriousness indicators."""
    predictions = []
    for _, row in df.iterrows():
        is_fatal = row.get('is_fatal', 0)
        sev = row.get('severity_score', 0)
        is_serious = row.get('is_serious', 0)
        
        if is_fatal == 1:
            predictions.append('DE')
        elif pd.notna(sev) and sev >= 6:
            predictions.append('LT')
        elif pd.notna(sev) and sev >= 5:
            predictions.append('HO')
        elif pd.notna(sev) and sev >= 4:
            predictions.append('DS')
        elif is_serious == 1:
            predictions.append('OT')
        else:
            predictions.append('OT')
    return predictions


def eval_metrics(y_true, y_pred, label_names=None):
    """Return dict of metrics."""
    return {
        'Accuracy': accuracy_score(y_true, y_pred),
        'Macro-F1': f1_score(y_true, y_pred, average='macro', zero_division=0),
        'Weighted-F1': f1_score(y_true, y_pred, average='weighted', zero_division=0),
        'Macro-Precision': precision_score(y_true, y_pred, average='macro', zero_division=0),
        'Macro-Recall': recall_score(y_true, y_pred, average='macro', zero_division=0),
    }


# ═════════════════════════════════════════════════════════════════
# LOAD DATA
# ═════════════════════════════════════════════════════════════════
print("=" * 70)
print("  PHASE 2 EXPERIMENT SUITE — Obesity All Cohort (N=11,701)")
print("=" * 70)

df_raw = pd.read_excel(DATA_48COL, header=1)
print(f"\nLoaded: {len(df_raw)} rows, {len(df_raw.columns)} columns")
print(f"Quarter range: {sorted(df_raw['source_quarter'].dropna().unique())}")
print(f"Missing outc_cod: {df_raw['outc_cod'].isna().sum()} ({df_raw['outc_cod'].isna().mean()*100:.1f}%)")


# ═════════════════════════════════════════════════════════════════
# TASK 2.1 — BASELINE COMPARISONS (Random 80/20 split)
# ═════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("  TASK 2.1: BASELINE COMPARISONS (Random 80/20 Split)")
print("=" * 70)

# Impute (current approach — full dataset mapping)
df_imputed, n_pt, n_sev = load_and_impute(df_raw)
print(f"Imputed: {n_pt} by pt_term mode, {n_sev} by severity fallback")

le_y = LabelEncoder()
df_imputed['y'] = le_y.fit_transform(df_imputed['outc_cod'])
class_names = list(le_y.classes_)
print(f"Classes: {class_names}")

# Prepare 13-feature (leakage-aware) dataset
X_13 = prepare_features(df_imputed, FEATURE_COLS_13)
y = df_imputed['y'].values

# Scale
scaler = StandardScaler()
X_13_scaled = scaler.fit_transform(X_13)

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X_13_scaled, y, test_size=0.2, random_state=SEED, stratify=y
)

print(f"Train: {len(X_train)}, Test: {len(X_test)}")

# ── Models ──
results_baseline = {}

# 1. Majority-class
print("\n  [1/6] Majority-class predictor...")
dummy = DummyClassifier(strategy='most_frequent', random_state=SEED)
dummy.fit(X_train, y_train)
y_pred_dummy = dummy.predict(X_test)
results_baseline['Majority Class'] = eval_metrics(y_test, y_pred_dummy, class_names)

# 2. Multinomial Logistic Regression (sklearn >= 1.7 removed multi_class param)
print("  [2/6] Multinomial Logistic Regression...")
lr = LogisticRegression(max_iter=1000, random_state=SEED, n_jobs=-1)
lr.fit(X_train, y_train)
y_pred_lr = lr.predict(X_test)
results_baseline['Logistic Regression'] = eval_metrics(y_test, y_pred_lr, class_names)

# 3. Simple Decision Tree
print("  [3/6] Decision Tree (max_depth=3)...")
dt = DecisionTreeClassifier(max_depth=3, random_state=SEED)
dt.fit(X_train, y_train)
y_pred_dt = dt.predict(X_test)
results_baseline['Decision Tree (d=3)'] = eval_metrics(y_test, y_pred_dt, class_names)

# 4. Seriousness-indicator rules
print("  [4/6] Seriousness-indicator rules...")
_, test_indices = train_test_split(
    np.arange(len(df_imputed)), test_size=0.2, random_state=SEED, stratify=y
)
df_test_rules = df_imputed.iloc[test_indices]
y_pred_rules = seriousness_rule_baseline(df_test_rules)
y_pred_rules_enc = le_y.transform(y_pred_rules)
results_baseline['Seriousness Rules'] = eval_metrics(y_test, y_pred_rules_enc, class_names)

# 5. Random Forest (existing baseline)
print("  [5/6] Random Forest (n=100)...")
rf = RandomForestClassifier(n_estimators=100, random_state=SEED, n_jobs=-1)
rf.fit(X_train, y_train)
y_pred_rf = rf.predict(X_test)
results_baseline['Random Forest'] = eval_metrics(y_test, y_pred_rf, class_names)

# 6. XGBoost (existing primary model)
print("  [6/6] XGBoost (n=100)...")
xgb_model = xgb.XGBClassifier(n_estimators=100, random_state=SEED, n_jobs=-1, 
                                eval_metric='mlogloss', verbosity=0)
xgb_model.fit(X_train, y_train)
y_pred_xgb = xgb_model.predict(X_test)
results_baseline['XGBoost'] = eval_metrics(y_test, y_pred_xgb, class_names)

# ── Print Results ──
print("\n" + "─" * 85)
print(f"  {'Model':<25} {'Accuracy':>10} {'Macro-F1':>10} {'Wt-F1':>10} {'M-Prec':>10} {'M-Recall':>10}")
print("─" * 85)
for model, metrics in results_baseline.items():
    print(f"  {model:<25} {metrics['Accuracy']:10.4f} {metrics['Macro-F1']:10.4f} "
          f"{metrics['Weighted-F1']:10.4f} {metrics['Macro-Precision']:10.4f} {metrics['Macro-Recall']:10.4f}")
print("─" * 85)

# Per-class classification reports for XGBoost and best baseline
print("\n  XGBoost Per-Class Report:")
print(classification_report(y_test, y_pred_xgb, target_names=class_names, zero_division=0))

print("  Logistic Regression Per-Class Report:")
print(classification_report(y_test, y_pred_lr, target_names=class_names, zero_division=0))

# Save
baseline_df = pd.DataFrame(results_baseline).T
baseline_df.index.name = 'Model'
baseline_df.to_csv(os.path.join(OUT_DIR, 'task2_1_baseline_comparison.csv'))
print(f"\nSaved: {os.path.join(OUT_DIR, 'task2_1_baseline_comparison.csv')}")


# ═════════════════════════════════════════════════════════════════
# TASK 2.2 — TEMPORAL VALIDATION
# ═════════════════════════════════════════════════════════════════
print("\n\n" + "=" * 70)
print("  TASK 2.2: TEMPORAL VALIDATION (Train 2021-23 / Val 2024 / Test 2025)")
print("=" * 70)

df_raw['quarter_year'] = df_raw['source_quarter'].str[:4].astype(int)

train_mask = df_raw['quarter_year'] <= 2023
val_mask = df_raw['quarter_year'] == 2024
test_mask = df_raw['quarter_year'] == 2025

print(f"  Train (2021-2023): {train_mask.sum()} rows")
print(f"  Val   (2024):      {val_mask.sum()} rows")
print(f"  Test  (2025):      {test_mask.sum()} rows")

df_train_raw = df_raw[train_mask].copy()
df_val_raw = df_raw[val_mask].copy()
df_test_raw = df_raw[test_mask].copy()

# LEAKAGE-SAFE: compute imputation mapping on TRAIN ONLY
df_train_imp, n_pt_t, n_sev_t = load_and_impute(df_train_raw)
print(f"  Train imputed: {n_pt_t} by pt_term, {n_sev_t} by severity")

# Apply train-only mapping to val and test
df_val_imp, n_pt_v, n_sev_v = load_and_impute(df_val_raw, compute_mapping_on=df_train_raw)
df_test_imp, n_pt_te, n_sev_te = load_and_impute(df_test_raw, compute_mapping_on=df_train_raw)

print(f"  Val imputed: {n_pt_v} by pt_term, {n_sev_v} by severity (remaining NaN: {df_val_imp['outc_cod'].isna().sum()})")
print(f"  Test imputed: {n_pt_te} by pt_term, {n_sev_te} by severity (remaining NaN: {df_test_imp['outc_cod'].isna().sum()})")

# Encode labels
all_labels = pd.concat([df_train_imp['outc_cod'], df_val_imp['outc_cod'], df_test_imp['outc_cod']]).dropna()
le_temp = LabelEncoder()
le_temp.fit(all_labels)
temp_classes = list(le_temp.classes_)
print(f"  Temporal classes: {temp_classes}")

# Drop any remaining NaN in outc_cod (should be 0 but just in case)
for df_part in [df_train_imp, df_val_imp, df_test_imp]:
    df_part.dropna(subset=['outc_cod'], inplace=True)

df_train_imp['y'] = le_temp.transform(df_train_imp['outc_cod'])
df_val_imp['y'] = le_temp.transform(df_val_imp['outc_cod'])
df_test_imp['y'] = le_temp.transform(df_test_imp['outc_cod'])

# Prepare features (13 features, no severity_score)
X_train_t = prepare_features(df_train_imp, FEATURE_COLS_13)
X_val_t = prepare_features(df_val_imp, FEATURE_COLS_13)
X_test_t = prepare_features(df_test_imp, FEATURE_COLS_13)

y_train_t = df_train_imp['y'].values
y_val_t = df_val_imp['y'].values
y_test_t = df_test_imp['y'].values

# Scale (fit on train only)
scaler_t = StandardScaler()
X_train_t = scaler_t.fit_transform(X_train_t)
X_val_t = scaler_t.transform(X_val_t)
X_test_t = scaler_t.transform(X_test_t)

# Also evaluate OBSERVED-ONLY labels (rows where outc_cod was originally present in raw test)
df_test_raw_aligned = df_raw[test_mask].copy()
df_test_raw_aligned = df_test_raw_aligned.loc[df_test_imp.index]  # align indices
obs_test_mask = df_test_raw_aligned['outc_cod'].notna().values

# ── Train and evaluate ──
temporal_results = {}
models_temporal = {
    'Majority Class': DummyClassifier(strategy='most_frequent', random_state=SEED),
    'Logistic Regression': LogisticRegression(max_iter=1000, random_state=SEED, n_jobs=-1),
    'Decision Tree (d=3)': DecisionTreeClassifier(max_depth=3, random_state=SEED),
    'Random Forest': RandomForestClassifier(n_estimators=100, random_state=SEED, n_jobs=-1),
    'XGBoost': xgb.XGBClassifier(n_estimators=100, random_state=SEED, n_jobs=-1, eval_metric='mlogloss', verbosity=0),
}

for name, model in models_temporal.items():
    print(f"\n  Training {name}...")
    t0 = time.time()
    model.fit(X_train_t, y_train_t)
    train_time = time.time() - t0
    
    # Val
    y_pred_val = model.predict(X_val_t)
    val_metrics = eval_metrics(y_val_t, y_pred_val)
    
    # Test (all labels — blended)
    y_pred_test = model.predict(X_test_t)
    test_metrics = eval_metrics(y_test_t, y_pred_test)
    
    # Test (observed-only)
    if obs_test_mask.sum() > 0:
        obs_metrics = eval_metrics(y_test_t[obs_test_mask], y_pred_test[obs_test_mask])
    else:
        obs_metrics = {'Accuracy': float('nan'), 'Macro-F1': float('nan')}
    
    temporal_results[name] = {
        'Train Time (s)': round(train_time, 2),
        'Val Accuracy': val_metrics['Accuracy'],
        'Val Macro-F1': val_metrics['Macro-F1'],
        'Test Blended Acc': test_metrics['Accuracy'],
        'Test Blended F1': test_metrics['Macro-F1'],
        'Test Observed Acc': obs_metrics['Accuracy'],
        'Test Observed F1': obs_metrics.get('Macro-F1', float('nan')),
    }

# ── Print Results ──
print("\n" + "─" * 100)
print(f"  {'Model':<25} {'Time':>6} {'Val Acc':>9} {'Val F1':>9} {'Test Blend':>11} {'Test F1':>9} {'Test Obs':>10} {'Obs F1':>9}")
print("─" * 100)
for model, m in temporal_results.items():
    print(f"  {model:<25} {m['Train Time (s)']:6.2f} {m['Val Accuracy']:9.4f} {m['Val Macro-F1']:9.4f} "
          f"{m['Test Blended Acc']:11.4f} {m['Test Blended F1']:9.4f} "
          f"{m['Test Observed Acc']:10.4f} {m['Test Observed F1']:9.4f}")
print("─" * 100)

# XGBoost temporal per-class report
xgb_temp = models_temporal['XGBoost']
y_pred_xgb_temp = xgb_temp.predict(X_test_t)
print("\n  XGBoost Temporal Test Per-Class Report:")
print(classification_report(y_test_t, y_pred_xgb_temp, labels=np.arange(len(temp_classes)), target_names=temp_classes, zero_division=0))

temp_df = pd.DataFrame(temporal_results).T
temp_df.index.name = 'Model'
temp_df.to_csv(os.path.join(OUT_DIR, 'task2_2_temporal_validation.csv'))
print(f"\nSaved: {os.path.join(OUT_DIR, 'task2_2_temporal_validation.csv')}")


# ═════════════════════════════════════════════════════════════════
# TASK 2.3 — LEAKAGE-SAFE IMPUTATION (5-fold CV)
# ═════════════════════════════════════════════════════════════════
print("\n\n" + "=" * 70)
print("  TASK 2.3: LEAKAGE-SAFE vs FULL-DATASET IMPUTATION (5-Fold CV)")
print("=" * 70)

skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)

# Full-dataset imputation for reference
df_full_imp, _, _ = load_and_impute(df_raw.copy())
le_cv = LabelEncoder()
df_full_imp['y'] = le_cv.fit_transform(df_full_imp['outc_cod'])
y_full = df_full_imp['y'].values

leakage_results = {'Full-Dataset Mapping': [], 'Fold-Internal Mapping': []}

for fold_idx, (train_idx, test_idx) in enumerate(skf.split(np.zeros(len(y_full)), y_full)):
    print(f"\n  Fold {fold_idx+1}/5...")
    
    # ── Approach 1: Full-dataset mapping (current, leakage-prone) ──
    X_fold = prepare_features(df_full_imp, FEATURE_COLS_13)
    sc = StandardScaler()
    X_fold_train = sc.fit_transform(X_fold[train_idx])
    X_fold_test = sc.transform(X_fold[test_idx])
    
    xgb_full = xgb.XGBClassifier(n_estimators=100, random_state=SEED, n_jobs=-1, 
                                   eval_metric='mlogloss', verbosity=0)
    xgb_full.fit(X_fold_train, y_full[train_idx])
    y_pred_full = xgb_full.predict(X_fold_test)
    
    leakage_results['Full-Dataset Mapping'].append({
        'Accuracy': accuracy_score(y_full[test_idx], y_pred_full),
        'Macro-F1': f1_score(y_full[test_idx], y_pred_full, average='macro', zero_division=0)
    })
    
    # ── Approach 2: Fold-internal mapping (leakage-safe) ──
    df_raw_copy = df_raw.copy()
    df_train_fold = df_raw_copy.iloc[train_idx].copy()
    df_test_fold = df_raw_copy.iloc[test_idx].copy()
    
    # Impute train with train-only mapping
    df_train_imp_fold, _, _ = load_and_impute(df_train_fold)
    # Impute test with train-only mapping  
    df_test_imp_fold, _, _ = load_and_impute(df_test_fold, compute_mapping_on=df_train_fold)
    
    le_fold = LabelEncoder()
    all_fold_labels = pd.concat([df_train_imp_fold['outc_cod'], df_test_imp_fold['outc_cod']]).dropna()
    le_fold.fit(all_fold_labels)
    
    y_train_fold = le_fold.transform(df_train_imp_fold['outc_cod'])
    y_test_fold = le_fold.transform(df_test_imp_fold['outc_cod'])
    
    X_train_fold = prepare_features(df_train_imp_fold, FEATURE_COLS_13)
    X_test_fold = prepare_features(df_test_imp_fold, FEATURE_COLS_13)
    
    sc2 = StandardScaler()
    X_train_fold = sc2.fit_transform(X_train_fold)
    X_test_fold = sc2.transform(X_test_fold)
    
    xgb_safe = xgb.XGBClassifier(n_estimators=100, random_state=SEED, n_jobs=-1, 
                                   eval_metric='mlogloss', verbosity=0)
    xgb_safe.fit(X_train_fold, y_train_fold)
    y_pred_safe = xgb_safe.predict(X_test_fold)
    
    leakage_results['Fold-Internal Mapping'].append({
        'Accuracy': accuracy_score(y_test_fold, y_pred_safe),
        'Macro-F1': f1_score(y_test_fold, y_pred_safe, average='macro', zero_division=0)
    })

# ── Summarize ──
print("\n" + "─" * 75)
print(f"  {'Approach':<30} {'Mean Acc':>10} {'Std Acc':>10} {'Mean F1':>10} {'Std F1':>10}")
print("─" * 75)
leakage_summary = {}
for approach, folds in leakage_results.items():
    accs = [f['Accuracy'] for f in folds]
    f1s = [f['Macro-F1'] for f in folds]
    print(f"  {approach:<30} {np.mean(accs):10.4f} {np.std(accs):10.4f} "
          f"{np.mean(f1s):10.4f} {np.std(f1s):10.4f}")
    leakage_summary[approach] = {
        'Mean Accuracy': np.mean(accs), 'Std Accuracy': np.std(accs),
        'Mean Macro-F1': np.mean(f1s), 'Std Macro-F1': np.std(f1s)
    }

gap_acc = leakage_summary['Full-Dataset Mapping']['Mean Accuracy'] - leakage_summary['Fold-Internal Mapping']['Mean Accuracy']
gap_f1 = leakage_summary['Full-Dataset Mapping']['Mean Macro-F1'] - leakage_summary['Fold-Internal Mapping']['Mean Macro-F1']
print("─" * 75)
print(f"  Leakage inflation:           {gap_acc:10.4f}                {gap_f1:10.4f}")
print("─" * 75)

leak_df = pd.DataFrame(leakage_summary).T
leak_df.index.name = 'Approach'
leak_df.to_csv(os.path.join(OUT_DIR, 'task2_3_leakage_comparison.csv'))
print(f"\nSaved: {os.path.join(OUT_DIR, 'task2_3_leakage_comparison.csv')}")


print("\n\n" + "=" * 70)
print("  PHASE 2 TASKS 2.1–2.3 COMPLETE")
print("=" * 70)
print(f"  Results saved to: {OUT_DIR}")
