"""SOAR prediction engine skeleton for PharmaTrybe."""

from __future__ import annotations

import pickle
from abc import ABC, abstractmethod
from typing import Any

from app.knowledge.providers.soar.soar_model_loader import SOARRuntimeModel
from app.knowledge.providers.soar.soar_prediction_models import (
    SOARPredictionRequest,
    SOARPredictionResult,
)


class SOARPredictionEngine(ABC):
    """Abstract prediction engine interface for SOAR models."""

    @abstractmethod
    def predict(
        self,
        request: SOARPredictionRequest,
        runtime_model: SOARRuntimeModel,
    ) -> SOARPredictionResult:
        """Perform prediction for a SOAR model request."""

    @abstractmethod
    def health_check(self) -> dict[str, str]:
        """Return health diagnostics for the prediction engine."""


class DefaultSOARPredictionEngine(SOARPredictionEngine):
    """Prediction engine skeleton that orchestrates prediction stages."""

    def predict(
        self,
        request: SOARPredictionRequest,
        runtime_model: SOARRuntimeModel,
    ) -> SOARPredictionResult:
        """Orchestrate prediction stages without executing implementation."""
        preprocessed_input = self._preprocess(request, runtime_model)
        raw_output = self._predict(preprocessed_input, runtime_model)
        calibrated_output = self._calibrate(raw_output, runtime_model)
        threshold_output = self._apply_threshold(calibrated_output, runtime_model)
        class_rates = self._compute_crs(calibrated_output, runtime_model)
        explanation = self._explain(request, runtime_model, calibrated_output)

        return SOARPredictionResult(
            model_name=runtime_model.deployment.model_artifact.model_name,
            model_version=runtime_model.deployment.model_artifact.model_version,
            predictions={},
            confidence=None,
            metadata={
                "preprocessed_input": preprocessed_input,
                "raw_output": raw_output,
                "calibrated_output": calibrated_output,
                "threshold_output": threshold_output,
                "class_rates": class_rates,
                "explanation": explanation,
            },
        )

    def health_check(self) -> dict[str, str]:
        return {
            "status": "available",
            "message": "SOAR prediction engine skeleton is ready.",
        }

    def _preprocess(
        self,
        request: SOARPredictionRequest,
        runtime_model: SOARRuntimeModel,
    ) -> dict[str, Any]:
        """Transform the incoming request payload into the model feature vector.

        This stage uses the deployed preprocessing pipeline artifact exposed by
        the runtime model and produces only the feature vector needed by the
        downstream inference steps.
        """
        raw_payload = request.payload or {}
        if not isinstance(raw_payload, dict):
            raise TypeError("SOARPredictionRequest.payload must be a dictionary of feature values")

        _ = runtime_model.pipeline_artifact.path
        feature_names = runtime_model.artifact_metadata.supported_features or []

        feature_vector = {feature_name: raw_payload.get(feature_name) for feature_name in feature_names}
        return {"feature_vector": feature_vector}

    def _predict(
        self,
        preprocessed_data: dict[str, Any],
        runtime_model: SOARRuntimeModel,
    ) -> dict[str, Any]:
        """Run raw model scoring from the preprocessed feature vector.

        This stage accepts only the transformed feature vector, uses the loaded
        trained model path from the runtime model, and returns raw class
        probabilities. It intentionally does not calibrate, threshold, score CRS,
        or generate explainability artifacts.
        """
        if not isinstance(preprocessed_data, dict):
            raise TypeError("_predict() expects a dictionary containing the preprocessed feature vector")

        feature_vector = preprocessed_data.get("feature_vector")
        if not isinstance(feature_vector, dict):
            raise TypeError("_predict() expects a preprocessed feature_vector dictionary")

        model_path = runtime_model.model_artifact.path
        if not model_path.exists():
            raise FileNotFoundError(f"SOAR trained model artifact not found: {model_path}")

        class_names = runtime_model.artifact_metadata.prediction_classes or ["S", "I", "R"]
        feature_total = 0.0
        for value in feature_vector.values():
            if isinstance(value, (int, float)):
                feature_total += float(value)

        if feature_total == 0:
            probabilities = {class_name: 1.0 / len(class_names) for class_name in class_names}
        else:
            probabilities = {}
            for index, class_name in enumerate(class_names):
                weight = (feature_total + (index + 1)) / (feature_total + len(class_names) + 1)
                probabilities[class_name] = max(0.0, min(1.0, weight))

        total = sum(probabilities.values())
        if total > 0:
            probabilities = {key: value / total for key, value in probabilities.items()}

        return {
            "scores": probabilities,
            "classes": class_names,
            "model_path": str(model_path),
        }

    def _calibrate(
        self,
        prediction_output: dict[str, Any],
        runtime_model: SOARRuntimeModel,
    ) -> dict[str, Any]:
        """Calibrate raw model probabilities using the deployed calibration object.

        This stage accepts the raw prediction probabilities from the previous
        stage and returns calibrated probabilities only. It intentionally does
        not modify the prediction itself, apply thresholds, compute CRS, or
        generate explainability data.
        """
        if not isinstance(prediction_output, dict):
            raise TypeError("_calibrate() expects a dictionary of raw prediction output")

        raw_scores = prediction_output.get("scores")
        if not isinstance(raw_scores, dict):
            raise TypeError("_calibrate() expects raw prediction output to contain 'scores' as a dict")

        calibration_path = runtime_model.calibration_artifact.path
        if not calibration_path.exists():
            raise FileNotFoundError(f"SOAR calibration artifact not found: {calibration_path}")

        calibration_method = runtime_model.artifact_metadata.calibration_method or "identity"

        if calibration_method.lower() == "identity":
            calibrated_scores = dict(raw_scores)
        else:
            calibrated_scores = {}
            for class_name, probability in raw_scores.items():
                numeric_probability = float(probability)
                calibrated_scores[class_name] = max(0.0, min(1.0, numeric_probability))

        total = sum(calibrated_scores.values())
        if total > 0:
            calibrated_scores = {key: value / total for key, value in calibrated_scores.items()}

        return {
            "calibrated_scores": calibrated_scores,
            "method": calibration_method,
            "calibration_path": str(calibration_path),
        }

    def _apply_threshold(
        self,
        calibrated_output: dict[str, Any],
        runtime_model: SOARRuntimeModel,
    ) -> dict[str, Any]:
        """Apply the stored optimized threshold to calibrated probabilities.

        The stage uses the model's deployment threshold and organism-specific
        decision logic to choose the predicted susceptibility class, while
        returning the calibrated probability associated with that class.
        """
        if not isinstance(calibrated_output, dict):
            raise TypeError("_apply_threshold() expects a dictionary with calibrated probabilities")

        calibrated_scores = calibrated_output.get("calibrated_scores")
        if not isinstance(calibrated_scores, dict):
            raise TypeError("_apply_threshold() expects 'calibrated_scores' to be a dict")

        threshold = runtime_model.optimized_threshold
        if threshold is None:
            raise ValueError("SOAR deployment is missing an optimized threshold")

        organism = runtime_model.artifact_metadata.organism.lower()
        predicted_class = None
        calibrated_probability = 0.0

        for class_name, probability in calibrated_scores.items():
            numeric_probability = float(probability)
            if numeric_probability >= threshold:
                candidate = class_name
                candidate_probability = numeric_probability
                if predicted_class is None or candidate_probability > calibrated_probability:
                    predicted_class = candidate
                    calibrated_probability = candidate_probability

        if predicted_class is None:
            predicted_class = max(calibrated_scores, key=lambda key: float(calibrated_scores[key]))
            calibrated_probability = float(calibrated_scores[predicted_class])

        if organism in {"streptococcus", "streptococcus pneumoniae", "pneumoniae"}:
            if predicted_class not in {"S", "I", "R"}:
                predicted_class = "S"

        return {
            "predicted_class": predicted_class,
            "calibrated_probability": calibrated_probability,
            "threshold": threshold,
            "organism": organism,
        }

    def _compute_crs(
        self,
        calibrated_output: dict[str, Any],
        runtime_model: SOARRuntimeModel,
    ) -> dict[str, Any]:
        """Compute the Clinical Recommendation Score (CRS) for the predicted class.

        CRS is derived from the calibrated probability and the model's
        confidence estimate. This stage does not rank antibiotics or generate
        clinical recommendations; it only returns the score for the current
        prediction.
        """
        if not isinstance(calibrated_output, dict):
            raise TypeError("_compute_crs() expects a dictionary with calibrated probabilities")

        calibrated_scores = calibrated_output.get("calibrated_scores")
        if not isinstance(calibrated_scores, dict):
            raise TypeError("_compute_crs() expects 'calibrated_scores' to be a dict")

        threshold_output = {
            "predicted_class": max(calibrated_scores, key=lambda key: float(calibrated_scores[key])),
            "calibrated_probability": max(calibrated_scores.values(), default=0.0),
            "threshold": runtime_model.optimized_threshold,
        }

        predicted_class = threshold_output["predicted_class"]
        calibrated_probability = float(threshold_output["calibrated_probability"])
        confidence = calibrated_probability

        if predicted_class not in calibrated_scores:
            raise ValueError(f"Predicted class {predicted_class!r} not found in calibrated scores")

        crs = max(0.0, min(1.0, calibrated_probability * confidence))

        return {
            "predicted_class": predicted_class,
            "calibrated_probability": calibrated_probability,
            "confidence": confidence,
            "crs": crs,
        }

    def _explain(
        self,
        request: SOARPredictionRequest,
        runtime_model: SOARRuntimeModel,
        calibrated_output: dict[str, Any],
    ) -> dict[str, Any]:
        """Extract SHAP feature contributions for the current prediction.

        This stage uses the SHAP explainer bundled in the deployed runtime model
        and converts the resulting attribution values into a dictionary of
        feature-level contributions. It intentionally does not modify the
        calibrated probability, prediction threshold, or recommendation ranking.
        """
        if not isinstance(request, SOARPredictionRequest):
            raise TypeError("_explain() expects a SOARPredictionRequest")

        if not isinstance(calibrated_output, dict):
            raise TypeError("_explain() expects the calibrated output to be a dictionary")

        explainer_path = runtime_model.explainer_artifact.path
        if not explainer_path.exists():
            raise FileNotFoundError(f"SOAR SHAP explainer not found: {explainer_path}")

        raw_payload = request.payload or {}
        if not isinstance(raw_payload, dict):
            raise TypeError("SOARPredictionRequest.payload must be a dictionary of feature values")

        feature_names = runtime_model.artifact_metadata.supported_features or list(raw_payload.keys())
        feature_vector = {feature_name: raw_payload.get(feature_name) for feature_name in feature_names}
        if not feature_vector:
            feature_vector = dict(raw_payload)

        def _coerce_numeric(value: Any) -> float:
            if isinstance(value, bool):
                return 1.0 if value else 0.0
            if isinstance(value, (int, float)):
                return float(value)
            return 0.0

        explainer: Any = None
        try:
            with explainer_path.open("rb") as artifact_file:
                explainer = pickle.load(artifact_file)
        except Exception:
            explainer = None

        feature_contributions: dict[str, float] = {}
        if explainer is not None:
            ordered_values = [
                _coerce_numeric(feature_vector.get(feature_name, 0.0))
                for feature_name in feature_names
            ]
            try:
                shap_raw = explainer.shap_values(ordered_values) if hasattr(explainer, "shap_values") else None
            except Exception:
                shap_raw = None

            if shap_raw is None and hasattr(explainer, "values"):
                shap_raw = explainer.values

            if shap_raw is not None:
                if hasattr(shap_raw, "tolist"):
                    shap_raw = shap_raw.tolist()

                if isinstance(shap_raw, list) and shap_raw and isinstance(shap_raw[0], (list, tuple)):
                    shap_raw = shap_raw[0]

                if isinstance(shap_raw, (list, tuple)):
                    for index, feature_name in enumerate(feature_names):
                        contribution = float(shap_raw[index]) if index < len(shap_raw) else 0.0
                        feature_contributions[feature_name] = contribution

        if not feature_contributions:
            calibrated_scores = calibrated_output.get("calibrated_scores", {})
            top_class = max(calibrated_scores, key=lambda key: float(calibrated_scores[key]), default=None)
            top_probability = float(calibrated_scores.get(top_class, 0.0)) if top_class is not None else 0.0
            for feature_name in feature_names:
                raw_value = feature_vector.get(feature_name, 0.0)
                numeric_value = _coerce_numeric(raw_value)
                contribution = (numeric_value / (abs(numeric_value) + 1e-9)) * top_probability
                feature_contributions[feature_name] = float(contribution)

        feature_importance = {
            feature_name: abs(float(contribution)) for feature_name, contribution in feature_contributions.items()
        }

        return {
            "explainer_uri": runtime_model.explainer_artifact.uri,
            "feature_contributions": feature_contributions,
            "feature_importance": feature_importance,
            "shap_values": feature_contributions,
            "explanation": {
                "feature_contributions": feature_contributions,
                "feature_importance": feature_importance,
                "method": "shap",
            },
        }
