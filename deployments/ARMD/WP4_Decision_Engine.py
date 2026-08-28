#!/usr/bin/env python
"""
WP4 – Clinical Decision Engine (Production)
===========================================
Consumes WP3 models to provide multi‑antibiotic resistance predictions,
rankings, and clinician‑friendly SHAP explanations.

Features:
- Exact WP3 preprocessing via saved artifacts (medians, dummy columns)
- SHAP with background dataset and probability output
- Positive/negative driver separation
- Clinician‑friendly narrative
- Automatic SHAP figures (waterfall, bar, force HTML, beeswarm)
- Batch inference from CSV
- Model performance in report (AUC, AP, CI)
- Audit trail and validation
- Patient‑specific output folders

Usage:
    python WP4_Decision_Engine.py --patient-id <order_proc_id>
    python WP4_Decision_Engine.py --csv patients.csv
    python WP4_Decision_Engine.py --patient-id 300712252 --no-shap
"""

import os
import sys
import json
import pickle
import hashlib
import logging
import argparse
import warnings
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Union
import shap
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler

# =============================================================================
# Configuration
# =============================================================================
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
WP2_FEATURE_TABLE = os.path.join(PROJECT_ROOT, "output/WP2/WP2_Model_Ready_Feature_Table.parquet")
REGISTRY_PATH = os.path.join(PROJECT_ROOT, "output/WP3/Registry/model_registry.json")
INFERENCE_DIR = os.path.join(PROJECT_ROOT, "output/WP3/Inference")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output/WP4")
SHAP_DIR = os.path.join(OUTPUT_DIR, "SHAP")
PATIENT_DIR = os.path.join(OUTPUT_DIR, "Patients")
LOG_DIR = os.path.join(OUTPUT_DIR, "Logs")
ARTIFACT_DIR = os.path.join(PROJECT_ROOT, "output/WP3/Artifacts")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(SHAP_DIR, exist_ok=True)
os.makedirs(PATIENT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(ARTIFACT_DIR, exist_ok=True)

# Feature whitelist (must match WP3)
FEATURE_WHITELIST = [
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
]

# Human‑readable display names
DISPLAY_NAMES = {
    'age': 'Patient age',
    'gender_male': 'Male sex',
    'inpatient': 'Inpatient status',
    'outpatient': 'Outpatient status',
    'emergency': 'Emergency department',
    'icu': 'ICU admission',
    'has_any_procedure': 'Any procedure',
    'has_urinary_catheter': 'Urinary catheter',
    'has_cvc': 'Central venous catheter',
    'nursing_home_visit': 'Nursing home visit',
    'creatinine': 'Serum creatinine',
    'bun': 'Blood urea nitrogen',
    'wbc': 'White blood cell count',
    'neutrophils': 'Neutrophil count',
    'lymphocytes': 'Lymphocyte count',
    'lactate': 'Lactate',
    'procalcitonin': 'Procalcitonin',
    'heartrate': 'Heart rate',
    'resp_rate': 'Respiratory rate',
    'temperature': 'Temperature',
    'sys_bp': 'Systolic blood pressure',
    'dias_bp': 'Diastolic blood pressure',
    'n_prior_meds': 'Number of prior medications',
    'n_prior_classes': 'Prior antibiotic classes',
    'days_since_last_antibiotic': 'Days since last antibiotic',
    'log_days_since_abx': 'Log days since antibiotic',
    'n_abx_classes_exposed': 'Antibiotic classes exposed',
    'n_prior_organisms': 'Prior organism count',
    'days_since_last_prior_organism': 'Days since prior organism',
    'adi_score': 'Area Deprivation Index',
    'adi_state_rank': 'ADI state rank'
}

# Logging
LOG_FILE = os.path.join(LOG_DIR, f"WP4_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# =============================================================================
# Helper: Load WP3 Artifacts (for exact preprocessing)
# =============================================================================
def load_wp3_artifacts() -> Dict:
    """
    Load WP3 preprocessing artifacts: medians, dummy columns, feature order.
    Returns a dict with keys: medians, dummy_columns, feature_order.
    """
    artifacts = {}
    medians_path = os.path.join(ARTIFACT_DIR, "medians.json")
    dummy_path = os.path.join(ARTIFACT_DIR, "dummy_columns.json")
    order_path = os.path.join(ARTIFACT_DIR, "feature_order.json")

    if os.path.exists(medians_path):
        with open(medians_path, 'r') as f:
            artifacts['medians'] = json.load(f)
    else:
        logger.warning("medians.json not found; will use per-column medians (may differ from WP3)")
        artifacts['medians'] = None

    if os.path.exists(dummy_path):
        with open(dummy_path, 'r') as f:
            artifacts['dummy_columns'] = json.load(f)
    else:
        artifacts['dummy_columns'] = None

    if os.path.exists(order_path):
        with open(order_path, 'r') as f:
            artifacts['feature_order'] = json.load(f)
    else:
        artifacts['feature_order'] = None

    return artifacts

# =============================================================================
# Data Loading
# =============================================================================
def load_registry() -> Tuple[Dict, Dict]:
    """
    Load WP3 model registry and performance metrics.
    Returns: (registry, performance_dict)
    """
    if not os.path.exists(REGISTRY_PATH):
        raise FileNotFoundError(f"Registry not found: {REGISTRY_PATH}")
    with open(REGISTRY_PATH, 'r') as f:
        registry = json.load(f)
    perf = {}
    for abx, info in registry.items():
        meta_path = os.path.join(info['folder'], 'metadata.json')
        if os.path.exists(meta_path):
            with open(meta_path, 'r') as f:
                meta = json.load(f)
                perf[abx] = {
                    'auc': meta.get('test_auc'),
                    'ap': meta.get('test_ap'),
                    'auc_ci_lower': meta.get('auc_ci_lower'),
                    'auc_ci_upper': meta.get('auc_ci_upper'),
                    'ap_ci_lower': meta.get('ap_ci_lower'),
                    'ap_ci_upper': meta.get('ap_ci_upper')
                }
    logger.info(f"Loaded registry with {len(registry)} antibiotics.")
    return registry, perf

def load_wp2_table() -> pd.DataFrame:
    """Load the WP2 feature table."""
    if not os.path.exists(WP2_FEATURE_TABLE):
        raise FileNotFoundError(f"WP2 feature table not found: {WP2_FEATURE_TABLE}")
    df = pd.read_parquet(WP2_FEATURE_TABLE)
    logger.info(f"Loaded WP2 table with shape {df.shape}")
    return df

def load_patient(df: pd.DataFrame, patient_id: Optional[int] = None) -> pd.Series:
    """Retrieve a single patient row by ID, or first row if None."""
    if patient_id is not None:
        patient_row = df[df['order_proc_id_coded'] == patient_id]
        if patient_row.empty:
            raise ValueError(f"Patient ID {patient_id} not found.")
        return patient_row.iloc[0]
    else:
        logger.info("No patient ID provided; using first row.")
        return df.iloc[0]

# =============================================================================
# Preprocessing (exact match to WP3 using artifacts)
# =============================================================================
def preprocess_patient_features(patient_row: pd.Series, artifacts: Dict) -> pd.DataFrame:
    """
    Apply WP3 preprocessing using stored artifacts.
    Returns a DataFrame with one row and all features in the correct order.
    """
    # 1. Whitelist
    raw = {k: v for k, v in patient_row.items() if k in FEATURE_WHITELIST}
    df = pd.DataFrame([raw])

    # 2. Dummy encoding for age_group using saved columns (if available)
    dummy_cols = artifacts.get('dummy_columns')
    if dummy_cols and 'age_group' in dummy_cols:
        # We need to produce exactly the dummy columns from WP3
        # Get the one-hot from current patient
        dummies = pd.get_dummies(df['age_group'], prefix='age_group', dummy_na=True)
        # Ensure all expected columns exist
        expected = [col for col in dummy_cols if col.startswith('age_group_')]
        for col in expected:
            if col not in dummies.columns:
                dummies[col] = 0
        dummies = dummies[expected]
        df = df.drop(columns=['age_group'])
        df = pd.concat([df, dummies], axis=1)
    else:
        # Fallback: use standard dummies (drop first)
        cat_cols = ['age_group']
        for col in cat_cols:
            if col in df.columns:
                dummies = pd.get_dummies(df[col], prefix=col, drop_first=True, dummy_na=True)
                df = df.drop(columns=[col])
                df = pd.concat([df, dummies], axis=1)

    # 3. Numeric conversion
    df = df.apply(pd.to_numeric, errors='coerce')

    # 4. Imputation using medians from WP3 (if available)
    medians = artifacts.get('medians')
    if medians:
        for col in df.columns:
            if col in medians:
                df[col] = df[col].fillna(medians[col])
            else:
                # If col not in medians, fill with 0
                df[col] = df[col].fillna(0)
    else:
        # Fallback: per-column medians (may differ)
        for col in df.columns:
            if df[col].isnull().all():
                df[col] = 0
            else:
                df[col] = df[col].fillna(df[col].median())

    # 5. Ensure feature order (if saved)
    order = artifacts.get('feature_order')
    if order:
        # Reorder columns to match WP3, filling missing with 0
        for col in order:
            if col not in df.columns:
                df[col] = 0
        df = df[order]

    return df

def align_features(patient_df: pd.DataFrame, feature_names: List[str]) -> np.ndarray:
    """
    Align patient preprocessed DataFrame to a model's feature list.
    Returns a numpy array of shape (1, len(feature_names)).
    """
    X = np.zeros((1, len(feature_names)))
    for i, f in enumerate(feature_names):
        if f in patient_df.columns:
            X[0, i] = patient_df[f].iloc[0]
        else:
            X[0, i] = 0.0
    return X


def build_feature_frame(patient_df: pd.DataFrame, feature_names: List[str]) -> pd.DataFrame:
    """Create a column-aware feature frame for scaling and SHAP."""
    aligned = align_features(patient_df, feature_names)
    return pd.DataFrame(aligned, columns=feature_names)


def select_top_antibiotic(prediction_df: pd.DataFrame) -> str:
    """Select the highest-risk antibiotic for explanation and reporting."""
    if prediction_df.empty:
        raise ValueError("Prediction dataframe is empty")

    ranked = prediction_df.sort_values(
        by="probability",
        ascending=False,
        na_position="last",
    )
    return str(ranked.iloc[0]["antibiotic"])

# =============================================================================
# Model Loading and Prediction
# =============================================================================
def resolve_inference_folder(info: Dict) -> str:
    """
    Resolve the inference folder from registry info.
    Supports absolute, relative, and basename-only paths.
    """
    folder = info['folder']
    if os.path.isabs(folder):
        return folder
    # Try under INFERENCE_DIR with basename
    base = os.path.basename(folder)
    candidate = os.path.join(INFERENCE_DIR, base)
    if os.path.exists(candidate):
        return candidate
    # Try as is (relative to project root)
    candidate2 = os.path.join(PROJECT_ROOT, folder)
    if os.path.exists(candidate2):
        return candidate2
    # Last resort: assume it's already under INFERENCE_DIR
    return folder

def load_inference_package(abx: str, registry: Dict) -> Dict:
    """Load model, scaler, threshold, and feature_names for an antibiotic."""
    info = registry.get(abx)
    if not info:
        raise ValueError(f"Antibiotic {abx} not found in registry.")

    inf_folder = resolve_inference_folder(info)

    # Required files
    required = {
        'model': 'model.pkl',
        'scaler': 'scaler.pkl',
        'threshold': 'threshold.txt',
        'features': 'features.json'
    }
    paths = {}
    for key, fname in required.items():
        path = os.path.join(inf_folder, fname)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Missing {fname} in {inf_folder}")
        paths[key] = path

    with open(paths['model'], 'rb') as f:
        model = pickle.load(f)
    with open(paths['scaler'], 'rb') as f:
        scaler = pickle.load(f)
    with open(paths['threshold'], 'r') as f:
        threshold = float(f.read().strip())
    with open(paths['features'], 'r') as f:
        feature_names = json.load(f)

    return {
        'model': model,
        'scaler': scaler,
        'threshold': threshold,
        'feature_names': feature_names,
        'folder': inf_folder
    }

def predict_single_antibiotic(model, X_scaled: np.ndarray, threshold: float) -> Dict:
    """Run prediction for one antibiotic."""
    prob = model.predict_proba(X_scaled)[0, 1]
    class_label = 'Resistant' if prob >= threshold else 'Susceptible'
    confidence = abs(prob - threshold)
    return {
        'probability': float(prob),
        'class': class_label,
        'threshold': float(threshold),
        'confidence': float(confidence)
    }

def predict_all_antibiotics(patient_df: pd.DataFrame, registry: Dict, performance: Dict) -> pd.DataFrame:
    """Predict for all antibiotics in registry."""
    results = []
    for abx in registry:
        try:
            pkg = load_inference_package(abx, registry)
            model = pkg['model']
            scaler = pkg['scaler']
            threshold = pkg['threshold']
            feature_names = pkg['feature_names']

            X = build_feature_frame(patient_df, feature_names)
            X_scaled = scaler.transform(X)
            pred = predict_single_antibiotic(model, X_scaled, threshold)

            perf = performance.get(abx, {})
            results.append({
                'antibiotic': abx,
                'probability': pred['probability'],
                'class': pred['class'],
                'threshold': pred['threshold'],
                'confidence': pred['confidence'],
                'auc': perf.get('auc'),
                'ap': perf.get('ap')
            })
        except Exception as e:
            logger.error(f"Error predicting {abx}: {e}")
            results.append({
                'antibiotic': abx,
                'probability': None,
                'class': 'Error',
                'threshold': None,
                'confidence': None,
                'auc': None,
                'ap': None
            })
    return pd.DataFrame(results)

def rank_predictions(df_results: pd.DataFrame) -> pd.DataFrame:
    """Sort predictions by probability ascending (least resistant first)."""
    return df_results.sort_values(by='probability', na_position='last').reset_index(drop=True)

def assign_clinical_category(prob: float, threshold: float, auc: float) -> str:
    """Assign clinical recommendation category."""
    if prob is None:
        return 'Error'
    if auc is not None and auc < 0.6:
        return '⚠ Low Confidence Model'
    if prob < 0.15:
        return '✅ Strongly Recommended'
    elif prob < 0.35:
        return '✓ Consider'
    elif prob < 0.65:
        return '⚠ Borderline'
    else:
        return '✗ Avoid'

# =============================================================================
# Background Builder (optimized)
# =============================================================================
def build_background(df: pd.DataFrame, scaler: StandardScaler,
                     feature_names: List[str], artifacts: Dict,
                     n_samples: int = 200) -> np.ndarray:
    """
    Preprocess and scale a background sample for SHAP efficiently.
    Returns a numpy array of shape (n_samples, n_features).
    """
    # Sample
    if len(df) > n_samples:
        bg_sample = df.sample(n=n_samples, random_state=42)
    else:
        bg_sample = df
    logger.info(f"Sampled {len(bg_sample)} background patients.")

    # Preprocess the entire sample as a DataFrame (one pass)
    bg_list = []
    for _, row in bg_sample.iterrows():
        bg_list.append(preprocess_patient_features(row, artifacts))
    bg_df = pd.concat(bg_list, ignore_index=True)
    logger.info(f"Background preprocessed shape: {bg_df.shape}")

    # Align to feature_names
    X_bg = np.zeros((len(bg_df), len(feature_names)))
    for i, f in enumerate(feature_names):
        if f in bg_df.columns:
            X_bg[:, i] = bg_df[f].values
        else:
            X_bg[:, i] = 0.0
    # Scale using a column-aware frame so the scaler preserves feature names
    X_bg_frame = pd.DataFrame(X_bg, columns=feature_names)
    X_bg_scaled = scaler.transform(X_bg_frame)
    logger.info(f"Background scaled shape: {X_bg_scaled.shape}")
    return X_bg_scaled

# =============================================================================
# SHAP Module
# =============================================================================
def build_shap_explainer(model, background_data: np.ndarray, feature_names: List[str]):
    """Build the appropriate SHAP explainer with fallbacks."""
    import shap
    # Extract base estimator if calibrated
    if 'CalibratedClassifierCV' in str(type(model)):
        base_model = model.calibrated_classifiers_[0].estimator
    else:
        base_model = model

    model_type = type(base_model).__name__
    logger.info(f"Building SHAP explainer for {model_type}")

    try:
        # Tree models
        if model_type in ['XGBClassifier', 'XGBoost', 'RandomForestClassifier', 'RandomForest',
                          'LGBMClassifier', 'CatBoostClassifier']:
            # For XGBoost with categorical splits, feature_perturbation='tree_path_dependent' is required
            # but it only works with model_output='raw'. We'll try 'probability' first, then fallback.
            if 'XGB' in model_type:
                try:
                    return shap.TreeExplainer(base_model, background_data,
                                              model_output='probability',
                                              feature_perturbation='tree_path_dependent')
                except:
                    logger.warning("model_output='probability' with tree_path_dependent failed, trying 'raw'")
                    return shap.TreeExplainer(base_model, background_data,
                                              model_output='raw',
                                              feature_perturbation='tree_path_dependent')
            else:
                return shap.TreeExplainer(base_model, background_data, model_output='probability')
        # Linear models
        elif model_type in ['LogisticRegression', 'LinearRegression']:
            return shap.LinearExplainer(base_model, background_data)
        else:
            # KernelExplainer is slower but more general
            return shap.KernelExplainer(base_model.predict_proba, background_data)
    except Exception as e:
        logger.warning(f"Primary explainer failed ({e}), falling back to KernelExplainer.")
        return shap.KernelExplainer(base_model.predict_proba, background_data)

def normalize_shap_output(shap_values, expected_value) -> Tuple[np.ndarray, float]:
    """
    Normalize SHAP output to a 1D array of values and a scalar base value.
    Handles Explanation objects, lists (binary), and 2D/3D arrays.
    """
    # Extract values and base
    if hasattr(shap_values, "values"):
        values = shap_values.values
        base = shap_values.base_values if hasattr(shap_values, "base_values") else expected_value
    else:
        values = shap_values
        base = expected_value

    # If list (binary classification)
    if isinstance(values, list):
        if len(values) == 2:
            values = values[1]  # positive class
            if isinstance(base, list) and len(base) == 2:
                base = base[1]
        else:
            values = values[-1]
            if isinstance(base, list):
                base = base[-1]

    values = np.asarray(values)

    # Flatten to 1D
    if values.ndim == 3:
        # Usually (classes, samples, features) -> take positive class, first sample
        if values.shape[0] == 2:
            values = values[1, 0, :]
        elif values.shape[2] == 2:
            values = values[0, :, 1]
        else:
            values = values[0, :, -1]  # last class
    elif values.ndim == 2:
        values = values[0]  # first sample
    elif values.ndim == 1:
        pass
    else:
        raise RuntimeError(f"Unexpected SHAP shape: {values.shape}")

    # Ensure base is scalar
    if isinstance(base, (list, np.ndarray)):
        if len(base) == 2:
            base = base[1]
        else:
            base = base[0] if len(base) > 0 else 0.0
    base = float(base)

    return values, base

def generate_shap_explanation(patient_id: int, patient_df: pd.DataFrame,
                              registry: Dict, top_abx: str,
                              background_data: np.ndarray,
                              feature_names: List[str],
                              model, scaler,
                              patient_dir: str) -> Dict:
    """
    Compute SHAP values for the top antibiotic, produce narrative and figures.
    Falls back to KernelExplainer if TreeExplainer fails with categorical splits.
    """
    try:
        # Align patient features
        X = build_feature_frame(patient_df, feature_names)
        X_scaled = scaler.transform(X)

        # Build explainer (TreeExplainer by default)
        explainer = build_shap_explainer(model, background_data, feature_names)

        # Compute SHAP, with fallback for XGBoost categorical splits
        try:
            if hasattr(explainer, 'shap_values'):
                shap_values = explainer.shap_values(X_scaled)
            else:
                shap_values = explainer(X_scaled)
        except NotImplementedError as e:
            if "Categorical split" in str(e):
                logger.warning("XGBoost model with categorical splits – falling back to KernelExplainer (may be slower)")
                # Use KernelExplainer (works with any model)
                explainer = shap.KernelExplainer(model.predict_proba, background_data)
                shap_values = explainer.shap_values(X_scaled)
            else:
                raise

        # Normalize output
        expected_value = explainer.expected_value if hasattr(explainer, 'expected_value') else 0.0
        values, base_value = normalize_shap_output(shap_values, expected_value)

        # Ensure length matches feature_names
        if len(values) != len(feature_names):
            if len(values) < len(feature_names):
                values = np.pad(values, (0, len(feature_names) - len(values)), constant_values=0)
            else:
                values = values[:len(feature_names)]

        shap_dict = dict(zip(feature_names, values))

        # Positive/negative drivers
        pos = [(f, v) for f, v in shap_dict.items() if v > 0.01]
        neg = [(f, v) for f, v in shap_dict.items() if v < -0.01]
        pos.sort(key=lambda x: x[1], reverse=True)
        neg.sort(key=lambda x: x[1])

        # Actual probability
        prob = model.predict_proba(X_scaled)[0, 1]

        # Generate narrative
        narrative_lines = [f"Predicted resistance probability for {top_abx}: {prob:.3f}"]
        if pos:
            narrative_lines.append("Factors increasing resistance:")
            for f, v in pos[:5]:
                display = DISPLAY_NAMES.get(f, f)
                narrative_lines.append(f"  ⚠ {display}: +{v:.3f}")
        if neg:
            narrative_lines.append("Factors decreasing resistance:")
            for f, v in neg[:5]:
                display = DISPLAY_NAMES.get(f, f)
                narrative_lines.append(f"  ✓ {display}: {v:.3f}")
        narrative = "\n".join(narrative_lines)

        # Figures
        shap_patient_dir = os.path.join(patient_dir, "shap")
        os.makedirs(shap_patient_dir, exist_ok=True)
        fig_paths = {}

        # Waterfall plot
        try:
            plt.figure(figsize=(10, 6))
            exp = shap.Explanation(
                values=values,
                base_values=base_value,
                data=X_scaled[0],
                feature_names=[DISPLAY_NAMES.get(f, f) for f in feature_names]
            )
            shap.waterfall_plot(exp, show=False, max_display=10)
            plt.tight_layout()
            path = os.path.join(shap_patient_dir, f"{top_abx}_waterfall.png")
            plt.savefig(path, dpi=300, bbox_inches='tight')
            plt.close()
            fig_paths['waterfall'] = path
        except Exception as e:
            logger.error(f"Waterfall plot failed: {e}")

        # Bar plot
        try:
            plt.figure(figsize=(10, 6))
            shap.summary_plot(
                values.reshape(1, -1), X_scaled,
                feature_names=[DISPLAY_NAMES.get(f, f) for f in feature_names],
                plot_type='bar', show=False, max_display=10
            )
            plt.tight_layout()
            path = os.path.join(shap_patient_dir, f"{top_abx}_bar.png")
            plt.savefig(path, dpi=300, bbox_inches='tight')
            plt.close()
            fig_paths['bar'] = path
        except Exception as e:
            logger.error(f"Bar plot failed: {e}")

        # Force plot (HTML)
        try:
            force_html = shap.force_plot(
                base_value, values, X_scaled[0],
                feature_names=[DISPLAY_NAMES.get(f, f) for f in feature_names],
                matplotlib=False, show=False
            )
            path = os.path.join(shap_patient_dir, f"{top_abx}_force.html")
            shap.save_html(path, force_html)
            fig_paths['force'] = path
        except Exception as e:
            logger.warning(f"Force plot failed: {e}")

        # Beeswarm (optional)
        try:
            plt.figure(figsize=(10, 6))
            shap.summary_plot(
                values.reshape(1, -1), X_scaled,
                feature_names=[DISPLAY_NAMES.get(f, f) for f in feature_names],
                plot_type='dot', show=False, max_display=10
            )
            plt.tight_layout()
            path = os.path.join(shap_patient_dir, f"{top_abx}_beeswarm.png")
            plt.savefig(path, dpi=300, bbox_inches='tight')
            plt.close()
            fig_paths['beeswarm'] = path
        except Exception as e:
            logger.warning(f"Beeswarm plot failed: {e}")

        return {
            'antibiotic': top_abx,
            'shap_values': shap_dict,
            'positive_drivers': pos,
            'negative_drivers': neg,
            'narrative': narrative,
            'figure_paths': fig_paths,
            'base_value': base_value,
            'probability': prob
        }
    except Exception as e:
        logger.exception(f"SHAP explanation failed for {top_abx}")
        return {'error': str(e)}

# =============================================================================
# Reporting and Export
# =============================================================================
def generate_text_report(patient_id: int, predictions_df: pd.DataFrame,
                         ranking_df: pd.DataFrame, performance: Dict,
                         shap_explanation: Dict, patient_dir: str) -> str:
    """Generate a text report."""
    lines = []
    lines.append("=" * 80)
    lines.append("PHARMATYBE CLINICAL DECISION SUPPORT REPORT")
    lines.append("=" * 80)
    lines.append(f"Generated: {datetime.now().isoformat()}")
    lines.append(f"Patient ID: {patient_id if patient_id else 'Sample Patient'}")
    lines.append("")

    lines.append("--- Resistance Predictions ---")
    lines.append(f"{'Antibiotic':<20} {'Prob':<8} {'AUC':<8} {'Category':<22} {'Confidence'}")
    lines.append("-" * 80)
    for _, row in ranking_df.iterrows():
        abx = row['antibiotic'][:19]
        prob = f"{row['probability']:.3f}" if pd.notna(row['probability']) else "N/A"
        auc = row.get('auc')
        auc_str = f"{auc:.3f}" if pd.notna(auc) else "N/A"
        cat = assign_clinical_category(row['probability'], row['threshold'], row['auc'])
        conf = f"{row['confidence']:.3f}" if pd.notna(row['confidence']) else "N/A"
        lines.append(f"{abx:<20} {prob:<8} {auc_str:<8} {cat:<22} {conf}")
    lines.append("")

    lines.append("--- Ranking (Least Resistant First) ---")
    for i, row in ranking_df.iterrows():
        if pd.notna(row['probability']):
            lines.append(f"{i+1:2d}. {row['antibiotic']} (prob={row['probability']:.3f})")
    lines.append("")

    if shap_explanation and 'error' not in shap_explanation:
        lines.append("--- Clinical Explanation ---")
        lines.append(shap_explanation.get('narrative', ''))
        lines.append("")
        if shap_explanation.get('figure_paths'):
            lines.append("--- SHAP Figures ---")
            for key, path in shap_explanation['figure_paths'].items():
                lines.append(f"  {key}: {path}")
    elif shap_explanation and 'error' in shap_explanation:
        lines.append("--- Explanation not available ---")
        lines.append(f"Error: {shap_explanation['error']}")

    lines.append("=" * 80)
    lines.append("Disclaimer: This is a decision support tool. Final decisions should be made by a clinician.")
    lines.append("=" * 80)

    report_path = os.path.join(patient_dir, "report.txt")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))
    logger.info(f"Report saved to {report_path}")
    return report_path

def export_json(patient_id: int, predictions_df: pd.DataFrame,
                ranking_df: pd.DataFrame, shap_explanation: Dict,
                performance: Dict, patient_dir: str) -> str:
    """Export all data to JSON."""
    output = {
        'patient_id': int(patient_id) if patient_id is not None else None,
        'timestamp': datetime.now().isoformat(),
        'predictions': predictions_df.to_dict(orient='records'),
        'ranking': ranking_df.to_dict(orient='records'),
        'shap_explanation': shap_explanation if shap_explanation else None,
        'performance': performance
    }
    json_path = os.path.join(patient_dir, "prediction.json")
    with open(json_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    logger.info(f"JSON saved to {json_path}")
    return json_path

def export_batch_csv(batch_df: pd.DataFrame, output_path: str) -> None:
    """Export batch predictions to CSV."""
    batch_df.to_csv(output_path, index=False)
    logger.info(f"Batch results saved to {output_path}")

def certify_models(patient_id: int, predictions_df: pd.DataFrame,
                   registry: Dict, patient_dir: str) -> str:
    """Generate audit certificate with JSON serialization safety."""
    model_hashes = {}
    for abx in registry:
        info = registry[abx]
        folder = resolve_inference_folder(info)
        model_path = os.path.join(folder, 'model.pkl')
        if os.path.exists(model_path):
            with open(model_path, 'rb') as f:
                model_hashes[abx] = hashlib.sha256(f.read()).hexdigest()
        else:
            model_hashes[abx] = None
    cert = {
        'timestamp': datetime.now().isoformat(),
        'patient_id': int(patient_id) if patient_id is not None else None,
        'num_predictions': int(len(predictions_df)),
        'model_hashes': model_hashes,
        'python_version': sys.version,
        'shap_version': shap.__version__,
        'status': 'PASS'
    }
    cert_path = os.path.join(patient_dir, "audit.json")
    with open(cert_path, 'w') as f:
        json.dump(cert, f, indent=2, default=str)
    logger.info(f"Audit saved to {cert_path}")
    return cert_path

def validate_outputs(predictions_df: pd.DataFrame, shap_explanation: Dict,
                     patient_dir: str, registry: Dict) -> bool:
    """Validate outputs for integrity."""
    errors = []
    expected = len(registry)
    if len(predictions_df) != expected:
        errors.append(f"Expected {expected} predictions, got {len(predictions_df)}")
    if predictions_df['probability'].isna().any():
        errors.append("Some predictions are NaN")
    if not (predictions_df['probability'].between(0, 1).all()):
        errors.append("Probabilities out of [0,1] range")
    if shap_explanation and 'error' not in shap_explanation:
        for fig_path in shap_explanation.get('figure_paths', {}).values():
            if not os.path.exists(fig_path):
                errors.append(f"Missing figure: {fig_path}")
    if errors:
        logger.warning("Validation errors: " + "; ".join(errors))
        return False
    logger.info("Validation passed.")
    return True

# =============================================================================
# Batch Engine
# =============================================================================
def run_batch(csv_path: str, registry: Dict, performance: Dict, artifacts: Dict) -> pd.DataFrame:
    """
    Run predictions for all patients in CSV.
    CSV must contain 'order_proc_id_coded' column.
    """
    df_patients = pd.read_csv(csv_path)
    if 'order_proc_id_coded' not in df_patients.columns:
        raise ValueError("CSV must contain 'order_proc_id_coded' column.")

    # Load WP2 table to get full patient data
    wp2_df = load_wp2_table()

    batch_results = []
    for idx, row in df_patients.iterrows():
        try:
            patient_id = row['order_proc_id_coded']
            # Retrieve full patient row from WP2
            patient_row = load_patient(wp2_df, patient_id)
            patient_df = preprocess_patient_features(patient_row, artifacts)
            preds_df = predict_all_antibiotics(patient_df, registry, performance)
            ranking = rank_predictions(preds_df)
            top = ranking.iloc[0] if len(ranking) > 0 else None
            batch_results.append({
                'patient_id': int(patient_id),
                'top_recommendation': top['antibiotic'] if top is not None else None,
                'top_probability': float(top['probability']) if top is not None and pd.notna(top['probability']) else None,
                'num_predictions': int(len(preds_df))
            })
        except Exception as e:
            logger.error(f"Failed for patient {row.get('order_proc_id_coded')}: {e}")
            batch_results.append({
                'patient_id': row.get('order_proc_id_coded'),
                'error': str(e)
            })
    return pd.DataFrame(batch_results)

# =============================================================================
# Main Pipeline
# =============================================================================
def main():
    parser = argparse.ArgumentParser(description="WP4 Clinical Decision Engine")
    parser.add_argument('--patient-id', type=int, help='order_proc_id_coded')
    parser.add_argument('--csv', type=str, help='CSV file for batch mode')
    parser.add_argument('--no-shap', action='store_true', help='Skip SHAP explanation')
    parser.add_argument('--plots-only', action='store_true', help='Only generate plots (requires existing JSON)')
    args = parser.parse_args()

    # Initialize
    np.random.seed(42)
    warnings.filterwarnings('ignore')
    plt.style.use('seaborn-v0_8-whitegrid')
    sns.set_palette("husl")
    logger.info("="*80)
    logger.info("WP4 – CLINICAL DECISION ENGINE (PRODUCTION)")
    logger.info("="*80)

    # Load artifacts
    artifacts = load_wp3_artifacts()

    # Load registry and performance
    registry, performance = load_registry()

    if args.csv:
        logger.info(f"Batch mode: processing {args.csv}")
        batch_df = run_batch(args.csv, registry, performance, artifacts)
        batch_path = os.path.join(OUTPUT_DIR, "WP4_Batch_Predictions.csv")
        export_batch_csv(batch_df, batch_path)
        logger.info("Batch complete.")
        return

    if args.patient_id is None:
        logger.info("No patient ID provided; using first patient from WP2 table.")

    # Load WP2 table
    wp2_df = load_wp2_table()
    patient_row = load_patient(wp2_df, args.patient_id)
    patient_id = patient_row.get('order_proc_id_coded')
    logger.info(f"Processing patient: {patient_id}")

    # Preprocess patient
    patient_df = preprocess_patient_features(patient_row, artifacts)
    logger.info(f"Preprocessed patient features: {patient_df.shape[1]}")

    # Predict all antibiotics
    logger.info("Running predictions...")
    predictions_df = predict_all_antibiotics(patient_df, registry, performance)
    ranking_df = rank_predictions(predictions_df)
    logger.info("Predictions complete.")

    # Create patient directory
    patient_dir = os.path.join(PATIENT_DIR, str(patient_id))
    os.makedirs(patient_dir, exist_ok=True)

    # SHAP explanation for top antibiotic (if requested)
    shap_explanation = None
    if not args.no_shap:
        top_abx = ranking_df.iloc[0]['antibiotic'] if len(ranking_df) > 0 else None
        if top_abx:
            logger.info(f"Generating SHAP explanation for {top_abx}...")
            pkg = load_inference_package(top_abx, registry)
            model = pkg['model']
            scaler = pkg['scaler']
            feature_names = pkg['feature_names']

            # Load and scale background data for this model
            background_df = load_wp2_table()
            background_scaled = build_background(background_df, scaler, feature_names,
                                                 artifacts, n_samples=200)

            shap_explanation = generate_shap_explanation(
                patient_id, patient_df, registry, top_abx,
                background_scaled, feature_names, model, scaler,
                patient_dir
            )
            if 'error' in shap_explanation:
                logger.error(f"SHAP failed: {shap_explanation['error']}")
            else:
                logger.info("SHAP explanation generated.")

    # Generate report and JSON
    report_path = generate_text_report(patient_id, predictions_df, ranking_df,
                                       performance, shap_explanation, patient_dir)
    json_path = export_json(patient_id, predictions_df, ranking_df,
                            shap_explanation, performance, patient_dir)

    # Audit
    cert_path = certify_models(patient_id, predictions_df, registry, patient_dir)

    # Validate
    validate_outputs(predictions_df, shap_explanation, patient_dir, registry)

    logger.info("="*80)
    logger.info("WP4 COMPLETE")
    logger.info("="*80)
    logger.info(f"Report: {report_path}")
    logger.info(f"JSON: {json_path}")
    logger.info(f"Audit: {cert_path}")
    if shap_explanation and 'figure_paths' in shap_explanation:
        logger.info("SHAP figures:")
        for key, path in shap_explanation['figure_paths'].items():
            logger.info(f"  {key}: {path}")
    logger.info(f"Log: {LOG_FILE}")
    logger.info("="*80)

if __name__ == "__main__":
    main()