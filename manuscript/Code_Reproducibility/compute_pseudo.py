import os, sys, warnings
warnings.filterwarnings('ignore')
import pandas as pd
import numpy as np
from sklearn.metrics import f1_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
import xgboost as xgb

df = pd.read_excel(r"E:\Adverse drugs Project 2\Research paper latex\FAERS_Pediatric_ML_Dataset.xlsx")

# Filter adolescent
if 'age_years' in df.columns:
    df = df[(df['age_years'] >= 12) & (df['age_years'] <= 17)]

df_21_23 = df[df['source_quarter'].str.startswith(('2021', '2022', '2023'), na=False)].copy()
df_25 = df[df['source_quarter'].str.startswith('2025', na=False)].copy()

# Test set is ALWAYS observed only
df_test = df_25.dropna(subset=['outc_cod']).copy()

EXCLUDE = ['primaryid', 'caseid', 'caseversion', 'source_quarter', 'event_dt', 'fda_dt', 'drugname_original', 'therapy_start_dt', 'therapy_end_dt', 'outc_cod']

def prep_and_train(df_train_in, df_test_in):
    X_tr = df_train_in.drop(columns=[c for c in EXCLUDE if c in df_train_in.columns])
    X_te = df_test_in.drop(columns=[c for c in EXCLUDE if c in df_test_in.columns])
    
    cat_cols = X_tr.select_dtypes(include=['object', 'category']).columns
    num_cols = X_tr.select_dtypes(exclude=['object', 'category']).columns
    
    for c in num_cols:
        med = X_tr[c].median()
        X_tr[c] = X_tr[c].fillna(med)
        X_te[c] = X_te[c].fillna(med)
        
    for c in cat_cols:
        X_tr[c] = X_tr[c].fillna('UNKNOWN').astype(str)
        X_te[c] = X_te[c].fillna('UNKNOWN').astype(str)
        le = LabelEncoder()
        le.fit(pd.concat([X_tr[c], X_te[c]]))
        X_tr[c] = le.transform(X_tr[c])
        X_te[c] = le.transform(X_te[c])
        
    X_tr = StandardScaler().fit_transform(X_tr)
    X_te = StandardScaler().fit_transform(X_te)
    
    le_y = LabelEncoder()
    # Fit LE on union of labels to ensure all classes are known
    le_y.fit(pd.concat([df_train_in['outc_cod'], df_test_in['outc_cod']]).astype(str))
    
    y_tr = le_y.transform(df_train_in['outc_cod'].astype(str))
    y_te = le_y.transform(df_test_in['outc_cod'].astype(str))
    
    xgb_m = xgb.XGBClassifier(n_estimators=100, random_state=42, n_jobs=-1, eval_metric='mlogloss')
    xgb_m.fit(X_tr, y_tr)
    y_pred = xgb_m.predict(X_te)
    
    return f1_score(y_te, y_pred, average='macro', zero_division=0)

# 1. Observed Only
df_train_obs = df_21_23.dropna(subset=['outc_cod']).copy()
f1_obs = prep_and_train(df_train_obs, df_test)

# 2. Observed + Stage 1
df_train_s1 = df_21_23.copy()
# compute mode per pt_term on OBSERVED ONLY
pt_modes = df_train_obs.groupby('pt_term')['outc_cod'].apply(lambda x: x.mode()[0] if not x.mode().empty else np.nan)
df_train_s1['outc_cod'] = df_train_s1.apply(
    lambda row: pt_modes.get(row['pt_term'], np.nan) if pd.isna(row['outc_cod']) else row['outc_cod'],
    axis=1
)
df_train_s1 = df_train_s1.dropna(subset=['outc_cod'])
f1_s1 = prep_and_train(df_train_s1, df_test)

# 3. Observed + Stage 1 + Stage 2
df_train_s2 = df_21_23.copy()
df_train_s2['outc_cod'] = df_train_s2.apply(
    lambda row: pt_modes.get(row['pt_term'], np.nan) if pd.isna(row['outc_cod']) else row['outc_cod'],
    axis=1
)
overall_mode = df_train_obs['outc_cod'].mode()[0]
df_train_s2['outc_cod'] = df_train_s2['outc_cod'].fillna(overall_mode)
f1_s2 = prep_and_train(df_train_s2, df_test)

print("--- 3.7 Effect of Pseudo-Labeling ---")
print(f"Observed labels only: {f1_obs:.4f}")
print(f"Observed + Stage 1 pseudo-label: {f1_s1:.4f}")
print(f"Observed + Stage 1 + Stage 2: {f1_s2:.4f}")

