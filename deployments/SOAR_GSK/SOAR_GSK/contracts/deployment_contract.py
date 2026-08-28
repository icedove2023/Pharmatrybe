#!/usr/bin/env python3
"""
Deployment Contract – Single Source of Truth
==============================================

Phase13C (recovery), Phase13D (reconstruction), and Phase13E (verification)
previously implemented independent, silently-diverging assumptions about:

  1. How a deployment fingerprint is computed.
  2. Which files a deployment package must contain, and at what path.
  3. How the model's pipeline topology is derived from `metadata.json`.

This module is the ONE place those three rules are defined. All three
phases import from here instead of re-implementing the logic locally.
Any change to the fingerprint algorithm, the required file list, or the
pipeline-topology extraction happens in exactly one place and is
immediately consistent across generation and verification.

CONTRACT_VERSION is bumped whenever a rule changes in a way that makes
older deployment packages non-conformant. Phase13E uses it to decide
whether a package needs migration rather than failing outright.
"""

from __future__ import annotations

import hashlib
from typing import Any, Dict, List, Optional

CONTRACT_VERSION = "1.0.0"


# ----------------------------------------------------------------------
#   1. Fingerprint contract
# ----------------------------------------------------------------------
#
# The combined deployment fingerprint MUST be reproducible from only the
# authoritative manifest (model hash + encoder hash) plus the deployment
# name, in this exact order. Anyone recomputing the fingerprint — during
# verification, migration, or audit — calls compute_combined_fingerprint()
# rather than re-deriving the hashing scheme.

def compute_combined_fingerprint(model_sha256: str, encoder_sha256: str, deployment_name: str) -> str:
    """Canonical fingerprint algorithm. Order matters: model, encoder, name."""
    if not model_sha256 and not encoder_sha256:
        return None
    h = hashlib.sha256()
    if model_sha256:
        h.update(model_sha256.encode())
    if encoder_sha256:
        h.update(encoder_sha256.encode())
    h.update(deployment_name.encode())
    return h.hexdigest()


# ----------------------------------------------------------------------
#   2. Package layout contract
# ----------------------------------------------------------------------
#
# Every artifact below MUST exist inside each individual deployment
# package directory (e.g. deployment_reconstructed/<name>/<file>). Batch-
# or run-level summaries (recovery_summary.json, phase13e_summary.json,
# etc.) are NOT part of the per-package contract and are intentionally
# excluded here.

REQUIRED_PACKAGE_FILES: List[str] = [
    'final_model.pkl',
    'label_encoder.pkl',
    'metadata.json',
    'feature_schema.json',
    'label_encoder.json',
    'model_card.json',
    'preprocessing_summary.json',
    'deployment_manifest.json',
    'deployment_fingerprint.json',
    'README.md',
    'VERSION.json',
    'deployment_info.json',
    'deployment_certificate.json',
    'reconstruction_metadata.json',
    'validation_report.json',
    'package_manifest.json',
]


# ----------------------------------------------------------------------
#   3. Pipeline topology contract
# ----------------------------------------------------------------------
#
# The model may be wrapped (CalibratedClassifierCV, etc.) an arbitrary
# number of levels deep before the actual sklearn/imblearn Pipeline is
# reached. Both the generator (Phase13C, when building
# preprocessing_summary.pipeline_order) and the verifier (Phase13E, when
# checking Level3) must derive the pipeline's *top-level step sequence*
# through the same wrapper-independent walk, so that a SMOTE step (or any
# other step) is never silently dropped by one side and expected by the
# other.

def extract_pipeline_topology(meta: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Recursively locate the first Pipeline node anywhere in the estimator
    tree (unwrapping CalibratedClassifierCV and similar wrappers) and
    return its direct children (top-level steps), each as the raw node
    dict produced by Phase13C's estimator inspector.

    This is wrapper-independent: it does not matter how many levels of
    wrapping sit above the Pipeline.
    """
    def find_pipeline(node: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        if not isinstance(node, dict):
            return None
        if node.get('type') == 'Pipeline':
            return node.get('children', [])
        for child in node.get('children', []) or []:
            result = find_pipeline(child)
            if result is not None:
                return result
        return None

    return find_pipeline(meta) or []


def pipeline_step_classes(meta: Dict[str, Any]) -> List[str]:
    """Top-level step class names of the pipeline, e.g.
    ['ColumnTransformer', 'SMOTE', 'XGBClassifier']."""
    return [step.get('class') for step in extract_pipeline_topology(meta)]


def column_transformer_step_names(meta: Dict[str, Any]) -> List[str]:
    """Names of the sub-transformers inside the pipeline's ColumnTransformer
    step (e.g. ['num', 'ohe', 'target_enc', 'bin']), independent of how many
    other steps (SMOTE, classifier, ...) follow it."""
    for step in extract_pipeline_topology(meta):
        if step.get('type') == 'ColumnTransformer' or step.get('class') == 'ColumnTransformer':
            return [child.get('name') for child in step.get('children', [])]
    return []


def build_pipeline_order(meta: Dict[str, Any]) -> List[str]:
    """Canonical, wrapper-independent 'pipeline_order' for
    preprocessing_summary.json: the ColumnTransformer's sub-transformer
    names, followed by every subsequent top-level pipeline step name
    (e.g. 'smote', the classifier step) in order. Used by Phase13C when
    writing preprocessing_summary.json so it matches what Phase13E's
    Level3 check expects.
    """
    order: List[str] = []
    steps = extract_pipeline_topology(meta)
    for step in steps:
        if step.get('type') == 'ColumnTransformer' or step.get('class') == 'ColumnTransformer':
            order.extend(child.get('name') for child in step.get('children', []))
        else:
            order.append(step.get('name'))
    return order


def compare_pipeline_topology(meta: Dict[str, Any], prep: Dict[str, Any]) -> List[str]:
    """Compare metadata.json's actual pipeline topology against
    preprocessing_summary.json's recorded pipeline_order, using the same
    wrapper-independent extraction on both sides. Returns a list of error
    strings (empty if consistent).

    This replaces the old two-step-only special case: it compares the
    ColumnTransformer's sub-transformer names against the corresponding
    prefix of prep_order, and the remaining top-level steps (SMOTE,
    classifier, ...) against the corresponding suffix — regardless of how
    many non-ColumnTransformer steps exist.
    """
    errors: List[str] = []

    ct_names = column_transformer_step_names(meta)
    expected_order = build_pipeline_order(meta)
    actual_order = prep.get('pipeline_order', [])

    if expected_order != actual_order:
        errors.append(
            f"pipeline_order mismatch: metadata-derived {expected_order}, "
            f"preprocessing_summary {actual_order}"
        )
        return errors

    # Cross-check that every ColumnTransformer sub-transformer's recorded
    # class in preprocessing_summary.transformers matches metadata.
    transformers = prep.get('transformers', {})
    steps = extract_pipeline_topology(meta)
    ct_step = next((s for s in steps if s.get('type') == 'ColumnTransformer' or s.get('class') == 'ColumnTransformer'), None)
    if ct_step:
        for child in ct_step.get('children', []):
            name = child.get('name')
            meta_cls = child.get('class')
            prep_cls = transformers.get(name, {}).get('class')
            if prep_cls and meta_cls != prep_cls:
                errors.append(f"Step '{name}' class mismatch: metadata '{meta_cls}', prep_summary '{prep_cls}'")
            elif not prep_cls:
                errors.append(f"Step '{name}' not found in preprocessing_summary.transformers")

    return errors


# ----------------------------------------------------------------------
#   4. Backend artifact contract (Phase13F)
# ----------------------------------------------------------------------
#
# The inference backend needs a superset of REQUIRED_PACKAGE_FILES: a few
# additional artifacts that Phase13C/13D never produced because they
# don't exist in the original training output (preprocessing_pipeline.pkl,
# calibration.pkl, shap_explainer.pkl, optimal_threshold.json,
# evaluation_metrics.csv). Phase13F is responsible for completing a
# package to this list — this constant is the one place both Phase13F and
# any future backend-compatibility check should read it from.

BACKEND_REQUIRED_ARTIFACTS: List[str] = REQUIRED_PACKAGE_FILES + [
    'preprocessing_pipeline.pkl',
    'calibration.pkl',
    'shap_explainer.pkl',
    'optimal_threshold.json',
    'evaluation_metrics.csv',
]


def contract_stamp() -> Dict[str, str]:
    """Stamp written into deployment_manifest.json / verification reports
    so it's always visible which contract version produced or checked a
    package."""
    return {'contract_version': CONTRACT_VERSION}
