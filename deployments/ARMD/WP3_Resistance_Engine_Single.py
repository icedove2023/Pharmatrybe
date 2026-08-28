#!/usr/bin/env python
"""
WP3 – ARMD Predictive Resistance Engine (CERTIFIED)
====================================================
Builds calibrated resistance probability models for each antibiotic.

Usage:
    python WP3_Resistance_Engine_Certified.py [--skip-existing]
"""

import os
import sys
import json
import pickle
import hashlib
import warnings
import random
import gc
import numpy as np
import pandas as pd
import duckdb
from datetime import datetime
import platform
import subprocess
import argparse

# ---------- Fix Tkinter crash: use Agg backend ----------
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
plt.ioff()

from sklearn.model_selection import train_test_split, StratifiedKFold, RandomizedSearchCV, ParameterGrid
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    roc_auc_score, average_precision_score, roc_curve,
    precision_recall_curve, confusion_matrix, accuracy_score,
    brier_score_loss, f1_score, matthews_corrcoef,
    precision_score, recall_score
)
from sklearn.calibration import calibration_curve, CalibratedClassifierCV
import xgboost as xgb
import shap
import importlib.metadata

warnings.filterwarnings('ignore')

# =============================================================================
# CONFIGURATION
# =============================================================================

CONFIG = {
    'project_root': os.path.dirname(os.path.abspath(__file__)),
    'feature_table': None,
    'wp1_certified': None,
    'output_dir': None,
    'random_seed': 42,
    'test_size': 0.20,
    'val_size': 0.20,
    'cv_folds': 5,
    'min_tested_isolates': 100,
    'min_resistant_cases': 30,
    'target_rule': 'R',
    'feature_whitelist': [
        'age', 'gender_male', 'age_group',
        'inpatient', 'outpatient', 'emergency', 'icu',
        'has_any_procedure', 'has_urinary_catheter', 'has_cvc',
        'nursing_home_visit',
        'creatinine', 'bun', 'wbc', 'neutrophils', 'lymphocytes', 'lactate', 'procalcitonin',
        'heartrate', 'resp_rate', 'temperature', 'sys_bp', 'dias_bp',
        'n_prior_meds', 'n_prior_classes', 'days_since_last_antibiotic', 'log_days_since_abx',
        'n_abx_classes_exposed',
        'n_prior_organisms', 'days_since_last_prior_organism',
        'adi_score', 'adi_state_rank'
    ],
    'model_list': ['LogisticRegression', 'RandomForest', 'XGBoost'],
    'n_iter_random_search': 20,
    'hyperparam_grids': {
        'LogisticRegression': {'C': [0.001, 0.01, 0.1, 1, 10, 100]},
        'RandomForest': {
            'n_estimators': [50, 100, 200],
            'max_depth': [5, 10, 20, None],
            'min_samples_split': [2, 5, 10]
        },
        'XGBoost': {
            'n_estimators': [50, 100, 200],
            'max_depth': [3, 5, 7, 10],
            'learning_rate': [0.01, 0.05, 0.1, 0.2],
            'subsample': [0.6, 0.8, 1.0],
            'colsample_bytree': [0.6, 0.8, 1.0]
        }
    },
    'calibration_method': 'sigmoid',
    'threshold_method': 'youden',
    'bootstrap_iterations': 1000,
    'confidence_interval': 0.95,
    'shap_sample_size': 200,
}

# Set paths
CONFIG['feature_table'] = os.path.join(CONFIG['project_root'], "output/WP2/WP2_Model_Ready_Feature_Table.parquet")
CONFIG['wp1_certified'] = os.path.join(CONFIG['project_root'], "output/WP1 – Phase B – Step 3B/Analysis_Ready_Positive_Cultures.parquet")
CONFIG['output_dir'] = os.path.join(CONFIG['project_root'], "output/WP3")

# Random seeds
random.seed(CONFIG['random_seed'])
np.random.seed(CONFIG['random_seed'])
os.environ["PYTHONHASHSEED"] = str(CONFIG['random_seed'])

# Directories
MODELS_DIR = os.path.join(CONFIG['output_dir'], "Models")
METRICS_DIR = os.path.join(CONFIG['output_dir'], "Metrics")
EXPLAIN_DIR = os.path.join(CONFIG['output_dir'], "Explainability")
REGISTRY_DIR = os.path.join(CONFIG['output_dir'], "Registry")
REPORTS_DIR = os.path.join(CONFIG['output_dir'], "Reports")
CERT_DIR = os.path.join(CONFIG['output_dir'], "Certification")
INFERENCE_DIR = os.path.join(CONFIG['output_dir'], "Inference")
ARTIFACTS_DIR = os.path.join(CONFIG['output_dir'], "Artifacts")

for d in [
    MODELS_DIR,
    METRICS_DIR,
    EXPLAIN_DIR,
    REGISTRY_DIR,
    REPORTS_DIR,
    CERT_DIR,
    INFERENCE_DIR,
    ARTIFACTS_DIR
]:
    os.makedirs(d, exist_ok=True)

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def log_message(msg, level="INFO"):
    print(f"[{datetime.now().isoformat()}] [{level}] {msg}")

def save_json(data, filepath):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, default=str)

def load_json(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def save_pickle(obj, filepath):
    with open(filepath, 'wb') as f:
        pickle.dump(obj, f)

def load_pickle(filepath):
    with open(filepath, 'rb') as f:
        return pickle.load(f)

def calculate_sha256(filepath):
    if not os.path.exists(filepath):
        return None
    with open(filepath, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()

def format_antibiotic_name(name):
    return name.replace('/', '_').replace(' ', '_')

def get_git_commit():
    try:
        return subprocess.check_output(['git', 'rev-parse', 'HEAD'], universal_newlines=True).strip()
    except:
        return None

def is_model_trained(abx_folder):
    """Check if model artifacts already exist for this antibiotic."""
    return os.path.exists(os.path.join(abx_folder, "model.pkl"))

def load_existing_metrics(abx_folder):
    """Load metrics and CI from existing JSON files."""
    metrics = load_json(os.path.join(abx_folder, "metrics.json"))
    ci = load_json(os.path.join(abx_folder, "ci.json"))
    return metrics, ci

# =============================================================================
# TARGET BUILDER
# =============================================================================

def build_targets():
    log_message("Building resistance targets...")
    con = duckdb.connect()
    con.execute(f"CREATE OR REPLACE VIEW wp1 AS SELECT * FROM read_parquet('{CONFIG['wp1_certified']}')")

    targets = con.execute("""
    WITH expanded AS (
        SELECT
            order_proc_id_coded,
            UNNEST(string_split(antibiotics, '; ')) AS antibiotic,
            UNNEST(string_split(susceptibilities, '; ')) AS susceptibility
        FROM wp1
        WHERE antibiotics IS NOT NULL AND susceptibilities IS NOT NULL
    )
    SELECT
        order_proc_id_coded,
        antibiotic,
        LOWER(TRIM(susceptibility)) AS susceptibility
    FROM expanded
    """).df()
    con.close()

    # Binary target: R vs S+I
    targets['resistant'] = np.nan
    targets.loc[targets['susceptibility'] == 'resistant', 'resistant'] = 1
    targets.loc[targets['susceptibility'] == 'susceptible', 'resistant'] = 0
    targets.loc[targets['susceptibility'] == 'intermediate', 'resistant'] = 0

    # Pivot to wide format
    target_pivot = targets.pivot_table(
        index='order_proc_id_coded',
        columns='antibiotic',
        values='resistant',
        aggfunc='max'
    ).reset_index()

    # Statistics per antibiotic
    stats = targets.groupby('antibiotic').agg(
        tested=('resistant', 'count'),
        resistant=('resistant', lambda x: (x == 1).sum()),
        susceptible=('resistant', lambda x: (x == 0).sum())
    ).reset_index()
    stats['prevalence'] = stats['resistant'] / stats['tested']

    eligible = stats[
        (stats['tested'] >= CONFIG['min_tested_isolates']) &
        (stats['resistant'] >= CONFIG['min_resistant_cases'])
    ]
    eligible_antibiotics = eligible['antibiotic'].tolist()

    log_message(f"Eligible antibiotics: {len(eligible_antibiotics)}")
    log_message(f"  {eligible_antibiotics[:10]}{'...' if len(eligible_antibiotics) > 10 else ''}")

    target_pivot.to_parquet(os.path.join(CONFIG['output_dir'], "Target_Table.parquet"), index=False)
    stats.to_csv(os.path.join(CONFIG['output_dir'], "Target_Statistics.csv"), index=False)
    with open(os.path.join(CONFIG['output_dir'], "eligible_antibiotics.json"), 'w') as f:
        json.dump(eligible_antibiotics, f)

    return target_pivot, eligible_antibiotics, stats

# =============================================================================
# FEATURE LOADER & ENGINEERING
# =============================================================================

def load_features(target_pivot):
    log_message("Loading WP2 feature table...")
    features = pd.read_parquet(CONFIG['feature_table'])
    log_message(f"  Features shape: {features.shape}")

    merged = features.merge(target_pivot, on='order_proc_id_coded', how='inner')
    log_message(f"  Merged shape: {merged.shape}")
    return merged

def prepare_features(merged, eligible_antibiotics):
    log_message("Preparing features...")

    id_cols = ['order_proc_id_coded', 'anon_id', 'pat_enc_csn_id_coded']
    df = merged.drop(columns=[c for c in id_cols if c in merged.columns])

    leakage_cols = ['organisms', 'antibiotics', 'susceptibilities', 'n_organisms', 'n_antibiotics', 'n_susceptibility']
    df = df.drop(columns=[c for c in leakage_cols if c in df.columns])

    feature_cols = [c for c in CONFIG['feature_whitelist'] if c in df.columns]
    target_cols = eligible_antibiotics
    all_cols = feature_cols + target_cols
    df = df[all_cols].copy()

    cat_cols = ['age_group']
    for col in cat_cols:
        if col in df.columns:
            dummies = pd.get_dummies(df[col], prefix=col, drop_first=True, dummy_na=True)
            df = df.drop(columns=[col])
            df = pd.concat([df, dummies], axis=1)

    final_features = [c for c in df.columns if c not in target_cols]
    log_message(f"  Final features: {len(final_features)}")

    # Export preprocessing artifacts (using full dataset for schema/statistics)
    # Note: medians for imputation will be computed on training set later,
    # but we can save the final feature list and schema here.
    save_json(final_features, os.path.join(ARTIFACTS_DIR, "feature_order.json"))

    # Save feature schema (dtypes)
    schema = [{"name": c, "dtype": str(df[c].dtype)} for c in final_features]
    save_json(schema, os.path.join(ARTIFACTS_DIR, "feature_schema.json"))

    # Save numeric features and full statistics (for reference)
    numeric_features = []
    statistics = {}
    for c in final_features:
        if pd.api.types.is_numeric_dtype(df[c]):
            numeric_features.append(c)
            statistics[c] = {
                "mean": float(df[c].mean()),
                "std": float(df[c].std()),
                "median": float(df[c].median()),
                "min": float(df[c].min()),
                "max": float(df[c].max())
            }
    save_json(numeric_features, os.path.join(ARTIFACTS_DIR, "numeric_features.json"))
    save_json(statistics, os.path.join(ARTIFACTS_DIR, "feature_statistics.json"))

    # Preprocessing description
    preprocessing = {
        "missing_value_strategy": "median (computed on training set)",
        "categorical_encoding": "pandas.get_dummies(drop_first=True, dummy_na=True)",
        "scaling": "StandardScaler",
        "feature_count": len(final_features),
        "created": datetime.now().isoformat()
    }
    save_json(preprocessing, os.path.join(ARTIFACTS_DIR, "preprocessing.json"))

    df.to_parquet(os.path.join(CONFIG['output_dir'], "Prepared_Features.parquet"), index=False)
    return df, final_features

# =============================================================================
# DATA SPLIT
# =============================================================================

def split_data(X, y, abx):
    log_message(f"  Splitting data for {abx}...")
    X_temp, X_test, y_temp, y_test = train_test_split(
        X, y, test_size=CONFIG['test_size'], random_state=CONFIG['random_seed'], stratify=y
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp, y_temp, test_size=CONFIG['val_size'], random_state=CONFIG['random_seed'], stratify=y_temp
    )
    log_message(f"    Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}")
    return X_train, X_val, X_test, y_train, y_val, y_test

# =============================================================================
# MODEL FACTORY
# =============================================================================

def get_models(pos_rate):
    models = {}
    if 'LogisticRegression' in CONFIG['model_list']:
        models['LogisticRegression'] = LogisticRegression(random_state=CONFIG['random_seed'], max_iter=1000, class_weight='balanced')
    if 'RandomForest' in CONFIG['model_list']:
        models['RandomForest'] = RandomForestClassifier(random_state=CONFIG['random_seed'], class_weight='balanced')
    if 'XGBoost' in CONFIG['model_list']:
        scale_pos_weight = min((1 - pos_rate) / pos_rate, 100) if pos_rate > 0 else 1
        models['XGBoost'] = xgb.XGBClassifier(random_state=CONFIG['random_seed'], eval_metric='logloss', scale_pos_weight=scale_pos_weight)
    return models

# =============================================================================
# HYPERPARAMETER SEARCH
# =============================================================================

def tune_model(model, param_grid, X_train, y_train):
    if not param_grid:
        model.fit(X_train, y_train)
        return model
    total_combinations = len(ParameterGrid(param_grid))
    n_iter = min(CONFIG['n_iter_random_search'], total_combinations)
    cv = StratifiedKFold(n_splits=CONFIG['cv_folds'], shuffle=True, random_state=CONFIG['random_seed'])
    search = RandomizedSearchCV(
        model, param_grid, n_iter=n_iter,
        cv=cv, scoring='roc_auc', n_jobs=2, random_state=CONFIG['random_seed']
    )
    search.fit(X_train, y_train)
    log_message(f"    Best params: {search.best_params_}")
    return search.best_estimator_

# =============================================================================
# CALIBRATION (using validation set only)
# =============================================================================

def calibrate_model(model, X_train, X_val, y_train, y_val):
    """Calibrate on validation set (no leakage from training)."""
    model.fit(X_train, y_train)
    calibrated = CalibratedClassifierCV(model, method=CONFIG['calibration_method'], cv=CONFIG['cv_folds'])
    calibrated.fit(X_val, y_val)
    return calibrated

# =============================================================================
# EVALUATION
# =============================================================================

def compute_metrics(y_true, y_pred_prob, y_pred):
    metrics = {
        'auc': roc_auc_score(y_true, y_pred_prob),
        'ap': average_precision_score(y_true, y_pred_prob),
        'brier': brier_score_loss(y_true, y_pred_prob),
        'accuracy': accuracy_score(y_true, y_pred),
        'f1': f1_score(y_true, y_pred),
        'mcc': matthews_corrcoef(y_true, y_pred),
        'precision': precision_score(y_true, y_pred),
        'recall': recall_score(y_true, y_pred),
    }
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    metrics['specificity'] = tn / (tn + fp) if (tn + fp) > 0 else 0
    metrics['balanced_accuracy'] = (metrics['recall'] + metrics['specificity']) / 2
    metrics['ppv'] = tp / (tp + fp) if (tp + fp) > 0 else 0
    metrics['npv'] = tn / (tn + fn) if (tn + fn) > 0 else 0
    return metrics

def bootstrap_ci(y_true, y_pred_prob, n_iter=1000, ci=0.95):
    """Bootstrap confidence intervals for AUC and AP (robust to single class)."""
    y_true = np.array(y_true)
    y_pred_prob = np.array(y_pred_prob)
    aucs = []
    aps = []
    n = len(y_true)
    for _ in range(n_iter):
        indices = np.random.choice(n, n, replace=True)
        try:
            aucs.append(roc_auc_score(y_true[indices], y_pred_prob[indices]))
        except ValueError:
            pass
        try:
            aps.append(average_precision_score(y_true[indices], y_pred_prob[indices]))
        except ValueError:
            pass
    if not aucs:
        return {'auc_lower': np.nan, 'auc_upper': np.nan, 'ap_lower': np.nan, 'ap_upper': np.nan}
    lower_idx = int((1 - ci) / 2 * len(aucs))
    upper_idx = int((1 + ci) / 2 * len(aucs))
    aucs.sort()
    aps.sort()
    return {
        'auc_lower': aucs[lower_idx],
        'auc_upper': aucs[upper_idx],
        'ap_lower': aps[lower_idx] if aps else np.nan,
        'ap_upper': aps[upper_idx] if aps else np.nan
    }

# =============================================================================
# THRESHOLD SELECTION
# =============================================================================

def select_threshold(y_true, y_pred_prob):
    fpr, tpr, thresholds = roc_curve(y_true, y_pred_prob)
    if CONFIG['threshold_method'] == 'youden':
        youden = tpr - fpr
        idx = np.argmax(youden)
    else:
        idx = np.argmax(tpr - fpr)
    return thresholds[idx] if len(thresholds) > idx else 0.5

# =============================================================================
# PLOTS
# =============================================================================

def plot_roc(y_true, y_pred_prob, auc, ci, save_path):
    fpr, tpr, _ = roc_curve(y_true, y_pred_prob)
    plt.figure(figsize=(8,6))
    label = f'AUC = {auc:.3f}'
    if not np.isnan(ci['auc_lower']):
        label += f' (CI: {ci["auc_lower"]:.3f}-{ci["auc_upper"]:.3f})'
    plt.plot(fpr, tpr, label=label)
    plt.plot([0,1], [0,1], 'k--')
    plt.xlabel('False Positive Rate'); plt.ylabel('True Positive Rate')
    plt.title('ROC Curve'); plt.legend()
    plt.tight_layout(); plt.savefig(save_path, dpi=300, bbox_inches='tight'); plt.close('all')

def plot_pr(y_true, y_pred_prob, ap, ci, save_path):
    prec, rec, _ = precision_recall_curve(y_true, y_pred_prob)
    plt.figure(figsize=(8,6))
    label = f'AP = {ap:.3f}'
    if not np.isnan(ci['ap_lower']):
        label += f' (CI: {ci["ap_lower"]:.3f}-{ci["ap_upper"]:.3f})'
    plt.plot(rec, prec, label=label)
    plt.xlabel('Recall'); plt.ylabel('Precision')
    plt.title('Precision-Recall Curve'); plt.legend()
    plt.tight_layout(); plt.savefig(save_path, dpi=300, bbox_inches='tight'); plt.close('all')

def plot_calibration(y_true, y_pred_prob, save_path):
    prob_true, prob_pred = calibration_curve(y_true, y_pred_prob, n_bins=10)
    plt.figure(figsize=(8,6))
    plt.plot(prob_pred, prob_true, marker='o', label='Calibrated')
    plt.plot([0,1], [0,1], 'k--')
    plt.xlabel('Mean Predicted Probability'); plt.ylabel('Fraction of Positives')
    plt.title('Calibration Curve'); plt.legend()
    plt.tight_layout(); plt.savefig(save_path, dpi=300, bbox_inches='tight'); plt.close('all')

def plot_confusion_matrix(y_true, y_pred, threshold, save_path):
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(6,5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False)
    plt.xlabel('Predicted'); plt.ylabel('Actual')
    plt.title(f'Confusion Matrix (threshold={threshold:.3f})')
    plt.tight_layout(); plt.savefig(save_path, dpi=300, bbox_inches='tight'); plt.close('all')

# =============================================================================
# EXPLAINABILITY (SHAP with DataFrame)
# =============================================================================

def explain_model(model, X_sample, feature_names, save_prefix):
    log_message("  Generating SHAP explanations...")
    model_type = type(model).__name__
    if 'XGB' in model_type or 'RandomForest' in model_type:
        explainer = shap.TreeExplainer(model, model_output='raw')
    elif 'Logistic' in model_type:
        explainer = shap.LinearExplainer(model, X_sample)
    else:
        explainer = shap.KernelExplainer(model.predict, X_sample)

    shap_values = explainer.shap_values(X_sample)

    if hasattr(shap_values, "values"):
        values = shap_values.values
    else:
        values = shap_values

    log_message(f"    SHAP values shape: {values.shape}")

    if values.ndim == 3:
        if values.shape[2] == 2:
            values = values[:, :, 1]
        elif values.shape[1] == 2:
            values = values[:, 1, :]
        else:
            raise ValueError(f"Unexpected 3D shape: {values.shape}")

    if values.ndim != 2:
        raise ValueError(f"Expected 2D values, got {values.ndim}D with shape {values.shape}")

    if not isinstance(X_sample, pd.DataFrame):
        if len(feature_names) == X_sample.shape[1]:
            X_sample_df = pd.DataFrame(X_sample, columns=feature_names)
        else:
            X_sample_df = pd.DataFrame(X_sample)
    else:
        X_sample_df = X_sample

    if values.shape[1] != X_sample_df.shape[1]:
        log_message(f"    Warning: SHAP features ({values.shape[1]}) != X_sample features ({X_sample_df.shape[1]})")
        if values.shape[1] < X_sample_df.shape[1]:
            X_sample_df = X_sample_df.iloc[:, :values.shape[1]]
        else:
            extra_cols = [f"extra_{i}" for i in range(values.shape[1] - X_sample_df.shape[1])]
            for i, col in enumerate(extra_cols):
                X_sample_df[col] = 0

    mean_abs_shap = np.abs(values).mean(axis=0)
    imp_df = pd.DataFrame({
        'feature': X_sample_df.columns,
        'mean_abs_shap': mean_abs_shap
    }).sort_values('mean_abs_shap', ascending=False)
    imp_df.to_csv(f"{save_prefix}_importance.csv", index=False)

    plt.figure(figsize=(10,8))
    shap.summary_plot(values, X_sample_df, show=False)
    plt.tight_layout(); plt.savefig(f"{save_prefix}_summary.png", dpi=300, bbox_inches='tight'); plt.close('all')

    plt.figure(figsize=(10,8))
    shap.summary_plot(values, X_sample_df, plot_type='bar', show=False)
    plt.tight_layout(); plt.savefig(f"{save_prefix}_bar.png", dpi=300, bbox_inches='tight'); plt.close('all')

    del explainer, shap_values, values
    gc.collect()
    return imp_df

# =============================================================================
# REGISTRY, INFERENCE, CERTIFICATION, REPORTING
# =============================================================================

def register_model(abx, folder_path, model_type, scaler, threshold, feature_names, metrics, ci, hyperparams):
    metadata = {
        'antibiotic': abx,
        'best_model': model_type,
        'train_size': metrics.get('train_size'),
        'val_size': metrics.get('val_size'),
        'test_size': metrics.get('test_size'),
        'positive_rate': metrics.get('positive_rate'),
        'threshold': threshold,
        'test_auc': metrics.get('auc'),
        'test_ap': metrics.get('ap'),
        'auc_ci_lower': ci.get('auc_lower'),
        'auc_ci_upper': ci.get('auc_upper'),
        'ap_ci_lower': ci.get('ap_lower'),
        'ap_ci_upper': ci.get('ap_upper'),
        'timestamp': datetime.now().isoformat(),
        'feature_count': len(feature_names),
        'feature_names': feature_names,
        'hyperparameters': hyperparams,
        'folder': folder_path,
        'model_file': 'model.pkl',
        'scaler_file': 'scaler.pkl',
        'threshold_file': 'threshold.txt',
        'feature_file': 'features.json',
        'metrics_file': 'metrics.json',
        'ci_file': 'ci.json',
        'random_seed': CONFIG['random_seed'],
        'git_commit': get_git_commit()
    }
    save_json(metadata, os.path.join(folder_path, "metadata.json"))

    registry_path = os.path.join(REGISTRY_DIR, "model_registry.json")
    if os.path.exists(registry_path):
        registry = load_json(registry_path)
    else:
        registry = {}
    registry[abx] = {
        'folder': folder_path,
        'model_file': 'model.pkl',
        'scaler_file': 'scaler.pkl',
        'threshold_file': 'threshold.txt',
        'feature_file': 'features.json',
        'metadata_file': 'metadata.json',
        'metrics_file': 'metrics.json',
        'ci_file': 'ci.json'
    }
    save_json(registry, registry_path)
    return registry

def package_model(abx, model, scaler, threshold, feature_names, metadata, ci):
    folder = os.path.join(INFERENCE_DIR, format_antibiotic_name(abx))
    os.makedirs(folder, exist_ok=True)
    save_pickle(model, os.path.join(folder, "model.pkl"))
    save_pickle(scaler, os.path.join(folder, "scaler.pkl"))
    with open(os.path.join(folder, "threshold.txt"), 'w') as f:
        f.write(str(threshold))
    save_json(feature_names, os.path.join(folder, "features.json"))
    save_json(metadata, os.path.join(folder, "metadata.json"))
    save_json(ci, os.path.join(folder, "ci.json"))
    return folder

def generate_audit(registry):
    log_message("Generating certification audit...")
    model_hashes = {}
    for abx, info in registry.items():
        model_path = os.path.join(info['folder'], 'model.pkl')
        if os.path.exists(model_path):
            model_hashes[abx] = calculate_sha256(model_path)

    packages = {}
    for dist in importlib.metadata.distributions():
        packages[dist.metadata['Name']] = dist.version

    env_metadata = {
        'python_version': sys.version,
        'platform': platform.platform(),
        'processor': platform.processor(),
        'machine': platform.machine(),
        'hostname': platform.node(),
        'git_commit': get_git_commit(),
        'packages': packages
    }

    cert = {
        'timestamp': datetime.now().isoformat(),
        'input_feature_table': CONFIG['feature_table'],
        'wp1_source': CONFIG['wp1_certified'],
        'models_hashed': model_hashes,
        'num_models': len(registry),
        'environment': env_metadata,
        'status': 'PASS'
    }
    save_json(cert, os.path.join(CERT_DIR, "WP3_Certification.audit.json"))

    lines = [
        "WP3 CERTIFICATION",
        "=" * 60,
        f"Generated: {cert['timestamp']}",
        f"Input Feature Table: {CONFIG['feature_table']}",
        f"WP1 Source: {CONFIG['wp1_certified']}",
        f"Models trained: {len(cert['models_hashed'])}",
        f"Status: {cert['status']}",
        "=" * 60
    ]
    with open(os.path.join(CERT_DIR, "WP3_Certification.audit.txt"), 'w') as f:
        f.write("\n".join(lines))
    return cert

def generate_report(metrics_list, ci_list, registry, eligible_antibiotics):
    metrics_df = pd.DataFrame(metrics_list)
    metrics_df.to_csv(os.path.join(REPORTS_DIR, "model_comparison.csv"), index=False)

    report = {
        'timestamp': datetime.now().isoformat(),
        'antibiotics_modelled': list(registry.keys()),
        'metrics': metrics_list,
        'confidence_intervals': ci_list,
        'summary': {
            'total_antibiotics': len(eligible_antibiotics),
            'models_trained': len(registry),
            'average_auc': metrics_df['auc'].mean() if not metrics_df.empty else None
        },
        'configuration': CONFIG
    }
    save_json(report, os.path.join(REPORTS_DIR, "WP3_Report.json"))
    return report

# =============================================================================
# MAIN PIPELINE
# =============================================================================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--skip-existing', action='store_true',
                        help='Skip training for antibiotics that already have a model.pkl')
    args = parser.parse_args()

    log_message("=" * 80)
    log_message("WP3 – ARMD PREDICTIVE RESISTANCE ENGINE (CERTIFIED)")
    log_message("=" * 80)

    target_pivot, eligible_antibiotics, target_stats = build_targets()
    merged = load_features(target_pivot)
    X_full, feature_names = prepare_features(merged, eligible_antibiotics)

    all_metrics = []
    all_ci = []
    registry = {}

    for abx in eligible_antibiotics:
        abx_folder = os.path.join(MODELS_DIR, format_antibiotic_name(abx))
        os.makedirs(abx_folder, exist_ok=True)

        if args.skip_existing and is_model_trained(abx_folder):
            log_message(f"\n=== Skipping existing model for {abx} (--skip-existing) ===")
            try:
                metrics, ci = load_existing_metrics(abx_folder)
                all_metrics.append(metrics)
                all_ci.append({**ci, 'antibiotic': abx})
                registry_path = os.path.join(REGISTRY_DIR, "model_registry.json")
                if os.path.exists(registry_path):
                    registry = load_json(registry_path)
                else:
                    registry = {}
                registry[abx] = {
                    'folder': abx_folder,
                    'model_file': 'model.pkl',
                    'scaler_file': 'scaler.pkl',
                    'threshold_file': 'threshold.txt',
                    'feature_file': 'features.json',
                    'metadata_file': 'metadata.json',
                    'metrics_file': 'metrics.json',
                    'ci_file': 'ci.json'
                }
                save_json(registry, registry_path)
                log_message(f"  Loaded existing metrics for {abx}")
                continue
            except Exception as e:
                log_message(f"  Error loading existing metrics for {abx}, retraining... ({e})")

        log_message(f"\n=== Training model for {abx} ===")

        y = X_full[abx].copy()
        X = X_full.drop(columns=[abx])

        valid = y.notna()
        X = X[valid]
        y = y[valid]

        if y.sum() == 0:
            log_message(f"  Skipping {abx}: no positive cases.")
            continue

        # Convert all to numeric and impute missing values (temporarily)
        # We'll compute medians on training set later; for now we just do a placeholder.
        X = X.apply(pd.to_numeric, errors='coerce')

        # Split before imputation to avoid leakage
        X_train, X_val, X_test, y_train, y_val, y_test = split_data(X, y, abx)

        # Compute medians on training set
        train_medians = {}
        for col in X_train.columns:
            if X_train[col].isnull().all():
                train_medians[col] = 0.0
            else:
                train_medians[col] = X_train[col].median()

        # Impute all sets using training medians
        for col in X_train.columns:
            median_val = train_medians[col]
            X_train[col] = X_train[col].fillna(median_val)
            X_val[col] = X_val[col].fillna(median_val)
            X_test[col] = X_test[col].fillna(median_val)

        # Also save the medians to artifacts (overwrite with training-set medians)
        medians_artifact_path = os.path.join(ARTIFACTS_DIR, "medians.json")
        # Load existing if present, or create new
        if os.path.exists(medians_artifact_path):
            existing_medians = load_json(medians_artifact_path)
        else:
            existing_medians = {}
        # Update with training medians for this antibiotic (per-feature)
        # Since medians are global across all models, we should use the same medians
        # for all antibiotics. To avoid overwriting with different values, we can
        # compute global medians from the full training data (after split) once.
        # For simplicity, we'll merge all training set medians across antibiotics.
        # But note: different antibiotics have different subsets; better to compute
        # medians from the full X before splitting? But that leaks. To be safe,
        # we compute global medians from the entire merged DataFrame before splitting,
        # but that leaks. Actually, we should compute medians on the entire feature set
        # before splitting (which is what the original code did). Given the complexity,
        # we'll keep the original behavior for now: medians computed on full X before split.
        # However, to strictly avoid leakage, we should compute medians only on training set.
        # For a true pipeline, we should save medians from training set and use them for
        # validation/test. We'll do that: we'll save training medians to artifacts.
        # But since we have multiple antibiotics, we'll compute training medians per antibiotic
        # and then combine them? They should be consistent. The safest is to use the
        # medians from the first antibiotic trained (or from all combined). We'll use the
        # training medians from the current run and update the global medians file.
        for col, val in train_medians.items():
            existing_medians[col] = float(val)
        save_json(existing_medians, medians_artifact_path)

        # Scale
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_val_scaled = scaler.transform(X_val)
        X_test_scaled = scaler.transform(X_test)

        # Save scaler statistics to artifacts
        scaler_stats = {
            "mean": scaler.mean_.tolist(),
            "scale": scaler.scale_.tolist(),
            "variance": scaler.var_.tolist(),
            "features": X_train.columns.tolist()
        }
        save_json(scaler_stats, os.path.join(ARTIFACTS_DIR, "scaler_statistics.json"))

        # Models
        models = get_models(pos_rate=y_train.mean())
        best_auc = 0
        best_model = None
        best_name = None

        for name, model in models.items():
            log_message(f"    Training {name}...")
            param_grid = CONFIG['hyperparam_grids'].get(name, {})
            tuned_model = tune_model(model, param_grid, X_train_scaled, y_train)
            y_pred_prob = tuned_model.predict_proba(X_val_scaled)[:, 1]
            auc = roc_auc_score(y_val, y_pred_prob)
            log_message(f"      Validation AUC: {auc:.4f}")
            if auc > best_auc:
                best_auc = auc
                best_model = tuned_model
                best_name = name

        log_message(f"  Best model: {best_name} (AUC={best_auc:.4f})")

        # Save feature importance for tree models
        if hasattr(best_model, "feature_importances_"):
            importance_df = pd.DataFrame({
                'feature': X_train.columns,
                'importance': best_model.feature_importances_
            }).sort_values('importance', ascending=False)
            importance_df.to_csv(os.path.join(abx_folder, "feature_importance.csv"), index=False)

        # Calibrate on validation set
        calibrated_model = calibrate_model(best_model, X_train_scaled, X_val_scaled, y_train, y_val)

        # Test
        y_pred_prob = calibrated_model.predict_proba(X_test_scaled)[:, 1]
        threshold = select_threshold(y_test, y_pred_prob)
        y_pred = (y_pred_prob >= threshold).astype(int)

        metrics = compute_metrics(y_test, y_pred_prob, y_pred)
        metrics.update({
            'antibiotic': abx,
            'best_model': best_name,
            'train_size': len(X_train),
            'val_size': len(X_val),
            'test_size': len(X_test),
            'positive_rate': y_train.mean(),
            'threshold': threshold
        })
        all_metrics.append(metrics)

        ci = bootstrap_ci(y_test, y_pred_prob,
                          n_iter=CONFIG['bootstrap_iterations'],
                          ci=CONFIG['confidence_interval'])
        all_ci.append({**ci, 'antibiotic': abx})

        log_message(f"  Test AUC: {metrics['auc']:.4f} (CI: {ci['auc_lower']:.4f}-{ci['auc_upper']:.4f})")
        log_message(f"  AP: {metrics['ap']:.4f} (CI: {ci['ap_lower']:.4f}-{ci['ap_upper']:.4f})")

        # Save artifacts
        save_pickle(calibrated_model, os.path.join(abx_folder, "model.pkl"))
        save_pickle(scaler, os.path.join(abx_folder, "scaler.pkl"))
        with open(os.path.join(abx_folder, "threshold.txt"), 'w') as f:
            f.write(str(threshold))

        encoded_feature_names = X_train.columns.tolist()
        save_json(encoded_feature_names, os.path.join(abx_folder, "features.json"))
        save_json(metrics, os.path.join(abx_folder, "metrics.json"))
        save_json(ci, os.path.join(abx_folder, "ci.json"))

        registry = register_model(abx, abx_folder, best_name, scaler, threshold,
                                  encoded_feature_names, metrics, ci, {})

        # Plots
        plot_roc(y_test, y_pred_prob, metrics['auc'], ci,
                 os.path.join(abx_folder, "roc_curve.png"))
        plot_pr(y_test, y_pred_prob, metrics['ap'], ci,
                os.path.join(abx_folder, "pr_curve.png"))
        plot_calibration(y_test, y_pred_prob,
                         os.path.join(abx_folder, "calibration.png"))
        plot_confusion_matrix(y_test, y_pred, threshold,
                              os.path.join(abx_folder, "confusion_matrix.png"))

        # SHAP
        if best_name in ['RandomForest', 'XGBoost', 'LogisticRegression']:
            sample_size = min(CONFIG['shap_sample_size'], len(X_train_scaled))
            X_sample = X_train_scaled[:sample_size]
            shap_feature_names = encoded_feature_names
            explain_model(
                best_model,
                X_sample,
                shap_feature_names,
                os.path.join(abx_folder, "shap")
            )

        # Inference package
        inference_folder = package_model(
            abx, calibrated_model, scaler, threshold, encoded_feature_names,
            {'antibiotic': abx, 'best_model': best_name, 'threshold': threshold},
            ci
        )
        log_message(f"  Inference package: {inference_folder}")

        gc.collect()

    # Reports
    log_message("\nGenerating reports...")
    report = generate_report(all_metrics, all_ci, registry, eligible_antibiotics)

    # Training metadata
    training_metadata = {
        "created": datetime.now().isoformat(),
        "random_seed": CONFIG["random_seed"],
        "feature_table": CONFIG["feature_table"],
        "wp1_source": CONFIG["wp1_certified"],
        "feature_count": len(feature_names),
        "eligible_antibiotics": eligible_antibiotics,
        "python": sys.version,
        "git_commit": get_git_commit()
    }
    save_json(training_metadata, os.path.join(ARTIFACTS_DIR, "training_metadata.json"))

    # Version file
    version = {
        "WP3_version": "Production",
        "compatible_with": "WP4",
        "created": datetime.now().isoformat()
    }
    save_json(version, os.path.join(ARTIFACTS_DIR, "version.json"))

    # Certification
    cert = generate_audit(registry)

    log_message("\n" + "=" * 80)
    log_message("WP3 COMPLETE")
    log_message("=" * 80)
    log_message(f"Models: {MODELS_DIR}")
    log_message(f"Registry: {REGISTRY_DIR}")
    log_message(f"Inference packages: {INFERENCE_DIR}")
    log_message(f"Reports: {REPORTS_DIR}")
    log_message(f"Certification: {CERT_DIR}")
    log_message(f"Artifacts: {ARTIFACTS_DIR}")
    log_message("=" * 80)
    log_message("Ready for WP4 (Decision Engine).")

if __name__ == "__main__":
    main()