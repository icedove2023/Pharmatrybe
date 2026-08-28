"""
Prediction Service

This service orchestrates the complete ARMD
prediction workflow.

Responsibilities
----------------
1. Load patient
2. Preprocess
3. Predict
4. Generate structured explainability
5. Generate clinical risk profile
6. Convert predictions into API schema

Business logic belongs here.

Machine learning remains inside WP4.
"""

from __future__ import annotations
from datetime import datetime

import pandas as pd

from ..engine import InferenceEngine
from ..engine import Preprocessor

from ..schemas import (
    PredictionRequest,
    PredictionResponse,
    AntibioticPrediction,
)

from .explainability_service import ExplainabilityService
from .risk_profile_service import RiskProfileService


class PredictionService:
    """
    Clinical Intelligence Service.

    WP5 orchestrates the validated WP4 Decision Engine
    while exposing structured outputs for PharmaTrybe.
    """

    ENGINE_VERSION = "WP4 Production"

    def __init__(self):

        self.preprocessor = Preprocessor()

        self.inference = InferenceEngine()

        self.explainability = ExplainabilityService()

        self.risk_profile = RiskProfileService()

    # -----------------------------------------------------
    # PUBLIC
    # -----------------------------------------------------

    def predict(
        self,
        request: PredictionRequest,
    ) -> PredictionResponse:
        """
        Execute the complete prediction workflow.
        """

        # -------------------------------------------------
        # Load patient
        # -------------------------------------------------

        patient = self._load_patient(request)

        # -------------------------------------------------
        # Preprocess
        # -------------------------------------------------

        patient_features = self.preprocessor.preprocess(patient)

        # -------------------------------------------------
        # Inference
        # -------------------------------------------------

        prediction_df = self.inference.predict(
            patient_features,
            request.requested_antibiotics,
        )

        predictions = self._build_predictions(
            prediction_df
        )

        # -------------------------------------------------
        # Structured Explainability
        # -------------------------------------------------

        shap_result = self.inference.generate_shap(
            patient_id=request.patient_id,
            patient_features=patient_features,
            prediction_df=prediction_df,
)

        explainability = self.explainability.generate(
            patient_features=patient_features,
            prediction_df=prediction_df,
            patient=(
                request.patient_data
                if request.patient_data is not None
                else patient
            ),
            shap_result=shap_result,
            
                    )

        # -------------------------------------------------
        # Clinical Risk Profile
        # -------------------------------------------------

        clinical_risk_profile = self.risk_profile.generate(

            patient=(
                request.patient_data
                if request.patient_data is not None
                else patient
            ),

            
        )

        # -------------------------------------------------
        # Response
        # -------------------------------------------------

        response = PredictionResponse(

            patient_id=(
                request.patient_id
                if request.patient_id is not None
                else -1
            ),

            generated_at=datetime.utcnow(),

            engine_version=self.ENGINE_VERSION,

            total_models=len(predictions),

            predictions=predictions,

            explainability=explainability,

            clinical_risk_profile=clinical_risk_profile,

            stewardship_summary=None,

            audit=None,
        )

        return response

    # -----------------------------------------------------
    # PRIVATE
    # -----------------------------------------------------

    def _load_patient(
        self,
        request: PredictionRequest,
    ):
        """
        Resolve patient source.
        """

        if request.patient_data is not None:

            return request.patient_data

        return self.preprocessor.load_patient(
            request.patient_id
        )

    def _build_predictions(
        self,
        prediction_df: pd.DataFrame,
    ):
        """
        Convert prediction dataframe into
        API prediction objects.
        """

        results = []

        for _, row in prediction_df.iterrows():

            prediction = AntibioticPrediction(

                antibiotic=row["antibiotic"],

                probability=float(row["probability"]),

                classification=row["class"],

                threshold=float(row["threshold"]),

                confidence=float(row["confidence"]),

                model_auc=(
                    float(row["auc"])
                    if pd.notna(row.get("auc"))
                    else None
                ),

                model_average_precision=(
                    float(row["ap"])
                    if pd.notna(row.get("ap"))
                    else None
                ),
            )

            results.append(prediction)

        return results