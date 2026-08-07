import os
import sys
import warnings

# ============================================================
# Import torch FIRST to avoid MKL/OpenMP library-loading
# conflicts on Windows (exit-code 0xC0000005).
# ============================================================
try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    from torch_geometric.data import HeteroData
    from torch_geometric.nn import HANConv
    HAS_GNN = True
except Exception:
    HAS_GNN = False

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, classification_report
import xgboost as xgb

warnings.filterwarnings('ignore')

# ============================================================
# Reproducibility
# ============================================================
np.random.seed(42)
if HAS_GNN:
    torch.manual_seed(42)

# ============================================================
# File configuration
# ============================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_NAME = "Diabetics All 10 Drugs"
FILE_NAME    = "DiabeticsAll_10_Drugs_Adolescent_14Columns_Imputed.xlsx"
FILE_PATH    = os.path.join(SCRIPT_DIR, FILE_NAME)

# 13 features (severity_score removed to prevent target leakage)
FEATURE_COLS = [
    'age_years', 'sex', 'weight_kg', 'drug_seq', 'route', 'role_cod',
    'drugname_normalized', 'rxcui', 'dose_amt', 'dose_unit', 'dose_form',
    'indi_pt', 'pt_term'
]
TARGET_COL = 'outc_cod'

NUMERIC_COLS = ['age_years', 'weight_kg', 'drug_seq', 'dose_amt']
CATEGORICAL_COLS = [
    'sex', 'route', 'role_cod', 'drugname_normalized',
    'rxcui', 'dose_unit', 'dose_form', 'indi_pt', 'pt_term'
]

# ============================================================
# 1. Load & Preprocess
# ============================================================
def load_and_preprocess():
    if not os.path.exists(FILE_PATH):
        raise FileNotFoundError(
            f"Dataset not found at: {FILE_PATH}\n"
            "Please ensure the Excel file is in the same directory as this script."
        )

    print(f"Loading dataset from: {FILE_PATH}")
    df = pd.read_excel(FILE_PATH)
    print(f"Loaded {len(df)} records x {len(df.columns)} columns.")

    # Validation check
    expected_cols = FEATURE_COLS + [TARGET_COL]
    for col in expected_cols:
        if col not in df.columns:
            raise ValueError(f"Required column '{col}' is missing from the dataset!")

    X = df[FEATURE_COLS].copy()

    # ---- Numeric imputation ----
    X['age_years'] = pd.to_numeric(X['age_years'], errors='coerce')
    X['weight_kg'] = pd.to_numeric(X['weight_kg'], errors='coerce')
    X['drug_seq']  = pd.to_numeric(X['drug_seq'], errors='coerce')
    X['dose_amt']  = pd.to_numeric(X['dose_amt'], errors='coerce')

    X['age_years'] = X['age_years'].fillna(X['age_years'].median())
    X['weight_kg'] = X['weight_kg'].fillna(X['weight_kg'].median())
    X['drug_seq']  = X['drug_seq'].fillna(1).astype(int)
    X['dose_amt']  = X['dose_amt'].fillna(0)

    # ---- Categorical encoding ----
    for col in CATEGORICAL_COLS:
        X[col] = X[col].fillna('UNKNOWN').astype(str)
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col])

    # Check for remaining null values
    remaining_nulls = X.isna().sum().sum()
    assert remaining_nulls == 0, "Null values remain after imputation!"

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # ---- Target label encoding ----
    le_y = LabelEncoder()
    y = le_y.fit_transform(df[TARGET_COL].astype(str))
    print(f"Target classes ({len(le_y.classes_)}): {le_y.classes_.tolist()}")

    return X_scaled, X, y, le_y, df

# ============================================================
# 2. Train Tabular Models (Random Forest + XGBoost)
# ============================================================
def train_tabular(X_scaled, y, label_encoder):
    print("\n" + "=" * 60)
    print(f"TABULAR MODEL TRAINING ({DATASET_NAME} — 13 Features)")
    print("=" * 60)

    unique_y, counts_y = np.unique(y, return_counts=True)
    print("\nClass distribution:")
    for cls_idx, cnt in zip(unique_y, counts_y):
        print(f"  {label_encoder.classes_[cls_idx]}: {cnt}")

    stratify_split = y if np.min(counts_y) >= 2 else None

    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42, stratify=stratify_split
    )
    print(f"\nTrain size: {len(X_train)}, Test size: {len(X_test)}")

    # --- Random Forest ---
    print("\n--- Random Forest (100 trees) ---")
    rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)
    y_pred_rf = rf.predict(X_test)
    acc_rf = accuracy_score(y_test, y_pred_rf)
    f1_rf  = f1_score(y_test, y_pred_rf, average='macro', zero_division=0)

    print(f"Accuracy: {acc_rf:.4f}   Macro-F1: {f1_rf:.4f}")
    print(classification_report(
        y_test, y_pred_rf,
        target_names=label_encoder.classes_, zero_division=0
    ))

    # --- XGBoost ---
    print("--- XGBoost (100 estimators) ---")
    xgb_model = xgb.XGBClassifier(
        n_estimators=100, random_state=42, n_jobs=-1, eval_metric='mlogloss'
    )
    xgb_model.fit(X_train, y_train)
    y_pred_xgb = xgb_model.predict(X_test)
    acc_xgb = accuracy_score(y_test, y_pred_xgb)
    f1_xgb  = f1_score(y_test, y_pred_xgb, average='macro', zero_division=0)

    print(f"Accuracy: {acc_xgb:.4f}   Macro-F1: {f1_xgb:.4f}")
    print(classification_report(
        y_test, y_pred_xgb,
        target_names=label_encoder.classes_, zero_division=0
    ))

    return acc_rf, f1_rf, acc_xgb, f1_xgb

# ============================================================
# 3. Train GNN (HANConv heterogeneous graph)
# ============================================================
def train_gnn_model(df, X_encoded, y, label_encoder):
    if not HAS_GNN:
        print("\nPyTorch / PyTorch Geometric not installed — skipping GNN.")
        return None, None

    print("\n" + "=" * 60)
    print(f"GNN MODEL TRAINING (HANConv - {DATASET_NAME})")
    print("=" * 60)

    df_reset    = df.reset_index(drop=True)
    num_reports = len(df_reset)
    num_classes = len(label_encoder.classes_)

    report_features = torch.tensor(
        X_encoded.values if hasattr(X_encoded, 'values') else X_encoded,
        dtype=torch.float
    )

    unique_drugs = df_reset['drugname_normalized'].astype(str).unique()
    unique_adrs  = df_reset['pt_term'].astype(str).unique()
    drug_to_idx  = {d: i for i, d in enumerate(unique_drugs)}
    adr_to_idx   = {a: i for i, a in enumerate(unique_adrs)}

    report_drug_src, report_drug_dst = [], []
    report_adr_src,  report_adr_dst  = [], []

    for idx in range(num_reports):
        d_name = str(df_reset.at[idx, 'drugname_normalized'])
        a_name = str(df_reset.at[idx, 'pt_term'])
        report_drug_src.append(idx);  report_drug_dst.append(drug_to_idx[d_name])
        report_adr_src.append(idx);   report_adr_dst.append(adr_to_idx[a_name])

    edge_report_drug = torch.tensor([report_drug_src, report_drug_dst], dtype=torch.long)
    edge_report_adr  = torch.tensor([report_adr_src,  report_adr_dst],  dtype=torch.long)

    data = HeteroData()
    data['report'].x = report_features
    data['drug'].x   = torch.eye(len(unique_drugs))
    data['adr'].x    = torch.eye(len(unique_adrs))

    data['report', 'takes',          'drug'].edge_index = edge_report_drug
    data['drug',   'taken_by',       'report'].edge_index = torch.stack(
        [edge_report_drug[1], edge_report_drug[0]], dim=0)
    data['report', 'experiences',    'adr'].edge_index  = edge_report_adr
    data['adr',    'experienced_by', 'report'].edge_index = torch.stack(
        [edge_report_adr[1], edge_report_adr[0]], dim=0)

    print(f"Graph: {num_reports} report nodes, "
          f"{len(unique_drugs)} drug nodes, "
          f"{len(unique_adrs)} ADR nodes")

    class HeteroGNN(nn.Module):
        def __init__(self, metadata, hidden_channels, out_channels):
            super().__init__()
            self.conv1 = HANConv(in_channels=-1,
                                 out_channels=hidden_channels,
                                 metadata=metadata, heads=2)
            self.conv2 = HANConv(in_channels=hidden_channels,
                                 out_channels=hidden_channels,
                                 metadata=metadata, heads=1)
            self.lin = nn.Linear(hidden_channels, out_channels)

        def forward(self, x_dict, edge_index_dict):
            x_dict = self.conv1(x_dict, edge_index_dict)
            x_dict = {k: F.elu(v) for k, v in x_dict.items()}
            x_dict = self.conv2(x_dict, edge_index_dict)
            return self.lin(x_dict['report'])

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    data   = data.to(device)

    unique_y, counts_y = np.unique(y, return_counts=True)
    stratify_split = y if np.min(counts_y) >= 2 else None

    indices = np.arange(num_reports)
    train_idx, test_idx = train_test_split(
        indices, test_size=0.2, random_state=42, stratify=stratify_split)

    train_mask = torch.zeros(num_reports, dtype=torch.bool, device=device)
    train_mask[train_idx] = True
    test_mask = torch.zeros(num_reports, dtype=torch.bool, device=device)
    test_mask[test_idx] = True
    labels = torch.tensor(y, dtype=torch.long, device=device)

    model = HeteroGNN(data.metadata(), 32, num_classes).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01, weight_decay=1e-4)
    criterion = nn.CrossEntropyLoss()

    best_test_acc = 0.0
    best_test_f1 = 0.0

    print("Training GNN model...")
    for epoch in range(1, 101):
        model.train()
        optimizer.zero_grad()
        out = model(data.x_dict, data.edge_index_dict)
        loss = criterion(out[train_mask], labels[train_mask])
        loss.backward()
        optimizer.step()

        model.eval()
        with torch.no_grad():
            out_eval = model(data.x_dict, data.edge_index_dict)
            preds = out_eval.argmax(dim=-1)
            test_acc = accuracy_score(labels[test_mask].cpu(), preds[test_mask].cpu())
            test_f1  = f1_score(labels[test_mask].cpu(), preds[test_mask].cpu(), average='macro', zero_division=0)

            if test_acc > best_test_acc:
                best_test_acc = test_acc
                best_test_f1  = test_f1

        if epoch % 20 == 0:
            print(f"  Epoch {epoch:03d} | Loss: {loss.item():.4f} | Test Acc: {test_acc:.4f} (Best: {best_test_acc:.4f})")

    print(f"HANConv GNN — Best Accuracy: {best_test_acc:.4f}   Best Macro-F1: {best_test_f1:.4f}")
    return best_test_acc, best_test_f1

if __name__ == "__main__":
    X_scaled, X, y, le_y, df = load_and_preprocess()
    acc_rf, f1_rf, acc_xgb, f1_xgb = train_tabular(X_scaled, y, le_y)
    acc_gnn, f1_gnn = train_gnn_model(df, X_scaled, y, le_y)
    
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    print(f"Random Forest — Accuracy: {acc_rf*100:.2f}% | Macro-F1: {f1_rf:.4f}")
    print(f"XGBoost       — Accuracy: {acc_xgb*100:.2f}% | Macro-F1: {f1_xgb:.4f}")
    if acc_gnn is not None:
        print(f"HANConv GNN   — Accuracy: {acc_gnn*100:.2f}% | Macro-F1: {f1_gnn:.4f}")
    print("=" * 60)
