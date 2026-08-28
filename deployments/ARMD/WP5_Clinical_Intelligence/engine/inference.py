"""
WP5 Inference Engine

Wraps the validated WP4 prediction engine.

This module performs NO machine learning itself.

It simply orchestrates calls into WP4.
"""

from __future__ import annotations

import pandas as pd

from WP4_Decision_Engine import (
    load_registry,
    predict_all_antibiotics,
    rank_predictions,
    load_wp3_artifacts,
    load_wp2_table,
    load_inference_package,
    build_background,
    generate_shap_explanation,
    select_top_antibiotic,
)


class InferenceEngine:
    """
    Executes ARMD inference using WP4.
    """

    def __init__(self):

        self.registry, self.performance = load_registry()

        self.artifacts = load_wp3_artifacts()

    # ---------------------------------------------------------
    # Prediction
    # ---------------------------------------------------------

    def predict(
        self,
        patient_features: pd.DataFrame,
        requested_antibiotics: list[str] | None = None,
    ) -> pd.DataFrame:
        """
        Predict resistance for antibiotics.
        """

        predictions = predict_all_antibiotics(
            patient_features,
            self.registry,
            self.performance,
        )

        if requested_antibiotics:

            predictions = predictions[
                predictions["antibiotic"].isin(
                    requested_antibiotics
                )
            ]

        return rank_predictions(predictions)

    # ---------------------------------------------------------
    # SHAP
    # ---------------------------------------------------------

    def generate_shap(
        self,
        patient_id: int | None,
        patient_features: pd.DataFrame,
        prediction_df: pd.DataFrame,
        
    ) -> dict:
        """
        Generate SHAP explanation using the
        validated WP4 implementation.
        """
        if prediction_df.empty:
            return {}

        # Top-risk antibiotic (highest predicted resistance)
        top_abx = select_top_antibiotic(prediction_df)

        # Load the exact inference package
        pkg = load_inference_package(
            top_abx,
            self.registry,
        )

        model = pkg["model"]
        scaler = pkg["scaler"]
        feature_names = pkg["feature_names"]

        # Build background dataset
        background_df = load_wp2_table()

        background_scaled = build_background(
            background_df,
            scaler,
            feature_names,
            self.artifacts,
            n_samples=200,
        )

        # No report output needed inside API
        patient_dir = "."

        return generate_shap_explanation(
            patient_id=patient_id or -1,
            patient_df=patient_features,
            registry=self.registry,
            top_abx=top_abx,
            background_data=background_scaled,
            feature_names=feature_names,
            model=model,
            scaler=scaler,
            patient_dir=patient_dir,
        )