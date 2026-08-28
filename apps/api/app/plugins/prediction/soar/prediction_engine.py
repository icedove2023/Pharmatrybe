from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence

import pandas as pd

from app.core.logging import get_logger
from app.plugins.base.prediction_plugin import PredictionRequest
from app.plugins.prediction.soar.deployment_scanner import DeploymentInfo
from app.plugins.prediction.soar.model_loader import LoadedModel

logger = get_logger(__name__)


class PredictionError(Exception):
    """Raised when a prediction execution cannot be completed."""


@dataclass
class PredictionExecution:
    """Runtime execution context for a single prediction."""

    deployment_id: str
    deployment_info: DeploymentInfo
    loaded_model: LoadedModel
    request: PredictionRequest
    processed_features: Sequence[Any]
    raw_prediction: Any
    probability: Optional[float]
    predicted_class: Any
    threshold: float
    execution_time_ms: float
    metadata: Dict[str, Any]


class PredictionEngine:
    """Executes inference for a loaded SOAR deployment."""

    def predict(self, loaded_model: LoadedModel, request: PredictionRequest) -> PredictionExecution:
        """Execute a single prediction using the provided loaded model."""
        deployment_id = loaded_model.deployment_info.deployment_id
        logger.info("Prediction started", extra={"deployment_id": deployment_id})

        self._validate_request(request)
        start_time = time.perf_counter()

        try:
            features = self._preprocess(loaded_model, request)
            raw_prediction = self._perform_inference(loaded_model.model, features)
            probability = self._predict_probability(loaded_model.model, features, raw_prediction, loaded_model)
            threshold = self._extract_threshold(loaded_model)
            predicted_class = self._decode_prediction(raw_prediction, loaded_model)
            passed_threshold = self._apply_threshold(probability, threshold)
            execution_time_ms = self._measure_execution(start_time)

            metadata = {
                "passed_threshold": passed_threshold,
                "threshold": threshold,
                "probability": probability,
                "feature_count": len(features),
            }

            logger.info(
                "Prediction completed",
                extra={
                    "deployment_id": deployment_id,
                    "execution_time_ms": execution_time_ms,
                    "probability": probability,
                    "predicted_class": predicted_class,
                },
            )

            return PredictionExecution(
                deployment_id=deployment_id,
                deployment_info=loaded_model.deployment_info,
                loaded_model=loaded_model,
                request=request,
                processed_features=features,
                raw_prediction=raw_prediction,
                probability=probability,
                predicted_class=predicted_class,
                threshold=threshold,
                execution_time_ms=execution_time_ms,
                metadata=metadata,
            )
        except PredictionError:
            logger.error("Prediction failed", extra={"deployment_id": deployment_id})
            raise
        except Exception as exc:
            logger.error("Prediction failed", extra={"deployment_id": deployment_id, "error": str(exc)})
            raise PredictionError(f"Unexpected prediction failure: {exc}") from exc

    def _validate_request(self, request: PredictionRequest) -> None:
        if not isinstance(request, PredictionRequest):
            raise PredictionError("Invalid prediction request type.")
        if not isinstance(request.payload, dict) or not request.payload:
            raise PredictionError("Prediction request payload must be a non-empty dictionary.")

    def _preprocess(self, loaded_model: LoadedModel, request: PredictionRequest) -> List[Any]:
        payload = request.payload
        model = loaded_model.model

        if hasattr(model, "feature_names_in_"):
            expected_features = list(getattr(model, "feature_names_in_"))
            missing = [name for name in expected_features if name not in payload]
            if missing:
                raise PredictionError(f"Missing required feature fields: {missing}")
            return pd.DataFrame([{name: payload[name] for name in expected_features}])

        if hasattr(model, "n_features_in_"):
            expected_count = int(getattr(model, "n_features_in_"))
            if len(payload) != expected_count:
                raise PredictionError(
                    f"Payload contains {len(payload)} features, but model expects {expected_count}."
                )
            return [payload[name] for name in sorted(payload)]

        return [payload[name] for name in sorted(payload)]

    def _perform_inference(self, model: Any, features: Sequence[Any]) -> Any:
        try:
            model_input = features if isinstance(features, pd.DataFrame) else [features]
            if hasattr(model, "predict"):
                return model.predict(model_input)
            if hasattr(model, "predict_proba"):
                return model.predict_proba(model_input)
            raise PredictionError("Model does not expose a prediction interface.")
        except Exception as exc:
            raise PredictionError(f"Inference failed: {exc}") from exc

    def _predict_probability(self, model: Any, features: Sequence[Any], raw_prediction: Any, loaded_model: LoadedModel) -> Optional[float]:
        if hasattr(model, "predict_proba"):
            try:
                model_input = features if isinstance(features, pd.DataFrame) else [features]
                proba = model.predict_proba(model_input)
                if hasattr(model, "classes_"):
                    classes = list(getattr(model, "classes_"))
                    predicted = self._decode_prediction(raw_prediction, loaded_model)
                    if predicted in classes:
                        index = classes.index(predicted)
                    else:
                        index = int(predicted) if isinstance(predicted, (int, float)) else 0
                    return float(proba[0][index])
                return float(proba[0].max())
            except Exception as exc:
                raise PredictionError(f"Probability extraction failed: {exc}") from exc
        return None

    def _decode_prediction(self, raw_prediction: Any, loaded_model: LoadedModel) -> Any:
        if hasattr(loaded_model.label_encoder, "inverse_transform"):
            try:
                predictions = raw_prediction
                if hasattr(predictions, "tolist"):
                    predictions = predictions.tolist()
                if isinstance(predictions, list):
                    decoded = loaded_model.label_encoder.inverse_transform([predictions[0]])
                    return decoded[0]
                return loaded_model.label_encoder.inverse_transform([predictions])[0]
            except Exception:
                return raw_prediction
        if isinstance(raw_prediction, list):
            return raw_prediction[0] if raw_prediction else raw_prediction
        if hasattr(raw_prediction, "tolist"):
            values = raw_prediction.tolist()
            return values[0] if values else values
        return raw_prediction

    def _extract_threshold(self, loaded_model: LoadedModel) -> float:
        threshold_data = loaded_model.optimal_threshold
        if threshold_data is None:
            raise PredictionError("Missing optimal threshold data.")
        if isinstance(threshold_data, dict):
            if "threshold" in threshold_data:
                return float(threshold_data["threshold"])
            if "optimal_threshold" in threshold_data:
                return float(threshold_data["optimal_threshold"])
            if len(threshold_data) == 1:
                return float(next(iter(threshold_data.values())))
        raise PredictionError("Could not extract threshold from optimal_threshold artifact.")

    def _apply_threshold(self, probability: Optional[float], threshold: float) -> bool:
        if probability is None:
            raise PredictionError("Cannot apply threshold without probability.")
        return probability >= threshold

    def _measure_execution(self, start_time: float) -> float:
        return (time.perf_counter() - start_time) * 1000.0
