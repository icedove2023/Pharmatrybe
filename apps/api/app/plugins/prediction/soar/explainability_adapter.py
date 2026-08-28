from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import pandas as pd

from app.core.logging import get_logger
from app.plugins.base.prediction_plugin import PredictionResult
from app.plugins.prediction.soar.prediction_engine import PredictionExecution
from packages.prediction_framework.explainability import BaseExplainabilityAdapter

logger = get_logger(__name__)

try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:  # pragma: no cover
    shap = None  # type: ignore[assignment]
    SHAP_AVAILABLE = False


class ExplainabilityError(Exception):
    """Raised when an explanation cannot be generated."""


@dataclass(frozen=True)
class ExplainabilityResult:
    """Normalized explainability payload for prediction results."""

    positive_features: List[Dict[str, Any]]
    negative_features: List[Dict[str, Any]]
    feature_importance: Dict[str, float]
    feature_contributions: Dict[str, float]
    summary: str
    explanation_method: str
    visualizations: Dict[str, Any]
    metadata: Dict[str, Any]


class ExplainabilityAdapter(BaseExplainabilityAdapter):
    """Converts internal prediction execution context into standardized explainability output."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config=config)

    def explain(self, execution: PredictionExecution) -> PredictionResult:
        """Generate a PredictionResult containing explainability metadata."""
        deployment_id = execution.deployment_id
        logger.info("Generating explanation", extra={"deployment_id": deployment_id})

        if not SHAP_AVAILABLE:
            raise ExplainabilityError("SHAP library is not available for explainability generation.")

        try:
            explanation = self._generate_explanation(execution)
            result = self._build_prediction_result(execution, explanation)
            logger.info("PredictionResult created", extra={"deployment_id": deployment_id})
            return result
        except ExplainabilityError:
            logger.error("Explainability generation failed", extra={"deployment_id": deployment_id})
            raise
        except Exception as exc:
            logger.error(
                "Explainability generation failed",
                extra={"deployment_id": deployment_id, "error": str(exc)},
            )
            raise ExplainabilityError(f"Unexpected explainability failure: {exc}") from exc

    def _generate_explanation(self, execution: PredictionExecution) -> ExplainabilityResult:
        model = execution.loaded_model.model
        features = execution.processed_features

        explainer = self._build_explainer(model, features)
        shap_values = self._compute_shap_values(explainer, features)
        feature_names = self._get_feature_names(model, execution.request.payload)

        contributions = self._normalize_shap_values(shap_values, feature_names)
        positive, negative = self._extract_feature_impact(contributions)
        summary = self._build_summary(positive, negative)

        return ExplainabilityResult(
            positive_features=positive,
            negative_features=negative,
            feature_importance={name: abs(value) for name, value in contributions.items()},
            feature_contributions=contributions,
            summary=summary,
            explanation_method=type(explainer).__name__,
            visualizations={
                "waterfall": {"type": "waterfall", "features": contributions},
                "bar_plot": {"type": "bar", "features": contributions},
                "beeswarm": {"type": "beeswarm", "metadata": {"class": execution.predicted_class}},
                "force_plot": {"type": "force", "metadata": {"prediction": execution.predicted_class}},
            },
            metadata={
                "explainer_type": type(explainer).__name__,
                "shap_version": getattr(shap, "__version__", "unknown"),
            },
        )

    def _build_explainer(self, model: Any, features: List[Any]) -> Any:
        if hasattr(shap, "TreeExplainer") and self._is_tree_model(model):
            logger.info("SHAP TreeExplainer selected", extra={"model_type": type(model).__name__})
            return shap.TreeExplainer(model)

        if hasattr(shap, "KernelExplainer"):
            logger.info("SHAP KernelExplainer fallback selected", extra={"model_type": type(model).__name__})
            if isinstance(features, pd.DataFrame):
                feature_names = list(features.columns)
                background = features.to_numpy()

                def predict_proba(values: Any) -> Any:
                    frame = pd.DataFrame(values, columns=feature_names)
                    return model.predict_proba(frame)

                return shap.KernelExplainer(predict_proba, background)
            return shap.KernelExplainer(model.predict_proba, [features])

        raise ExplainabilityError("No compatible SHAP explainer available.")

    def _compute_shap_values(self, explainer: Any, features: List[Any]) -> List[float]:
        try:
            shap_values = explainer.shap_values([features])
            if isinstance(shap_values, list):
                shap_values = shap_values[0]
            if hasattr(shap_values, "tolist"):
                shap_values = shap_values.tolist()[0] if isinstance(shap_values[0], (list, tuple)) else shap_values.tolist()
            return list(shap_values)
        except Exception as exc:
            raise ExplainabilityError(f"SHAP value computation failed: {exc}") from exc

    def _get_feature_names(self, model: Any, payload: Dict[str, Any]) -> List[str]:
        if hasattr(model, "feature_names_in_"):
            return list(getattr(model, "feature_names_in_"))
        return sorted(payload.keys())

    def _normalize_shap_values(self, shap_values: List[float], feature_names: List[str]) -> Dict[str, float]:
        if len(shap_values) != len(feature_names):
            raise ExplainabilityError("SHAP values length does not match feature count.")
        return {name: float(value) for name, value in zip(feature_names, shap_values)}

    def _extract_feature_impact(self, contributions: Dict[str, float]) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        sorted_features = sorted(contributions.items(), key=lambda item: abs(item[1]), reverse=True)
        positive = [
            {"feature": name, "contribution": value}
            for name, value in sorted_features
            if value > 0
        ][:5]
        negative = [
            {"feature": name, "contribution": value}
            for name, value in sorted_features
            if value < 0
        ][:5]
        return positive, negative

    def _build_summary(self, positive: List[Dict[str, Any]], negative: List[Dict[str, Any]]) -> str:
        influencers: List[str] = []
        influencers.extend([entry["feature"] for entry in positive[:3]])
        influencers.extend([entry["feature"] for entry in negative[:2]])
        if not influencers:
            return "No dominant features were identified for this prediction."
        joined = ", ".join(influencers)
        return f"The prediction was primarily influenced by {joined}."

    def _build_prediction_result(self, execution: PredictionExecution, explanation: ExplainabilityResult) -> PredictionResult:
        probability = execution.probability if execution.probability is not None else 0.0
        confidence = float(probability)
        return PredictionResult(
            predicted_class=execution.predicted_class,
            probabilities={"predicted_class": float(probability)},
            confidence=confidence,
            model_name=execution.deployment_id,
            model_version="unknown",
            execution_time_ms=execution.execution_time_ms,
            metadata={
                **execution.metadata,
                "explanation": {
                    "positive_features": explanation.positive_features,
                    "negative_features": explanation.negative_features,
                    "feature_importance": explanation.feature_importance,
                    "feature_contributions": explanation.feature_contributions,
                    "summary": explanation.summary,
                    "explanation_method": explanation.explanation_method,
                    "visualizations": explanation.visualizations,
                    "metadata": explanation.metadata,
                },
            },
        )

    def _is_tree_model(self, model: Any) -> bool:
        return any(hasattr(model, attr) for attr in ["tree_", "estimators_"]) or type(model).__name__.endswith("Tree")
