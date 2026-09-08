"""Narrow canonical-to-plugin request adapters.

Adapters preserve plugin-specific ownership. They do not infer clinical
mappings or manufacture missing model inputs.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from app.plugins.base.prediction_plugin import PredictionRequest


class AdapterValidationError(ValueError):
    """Raised when canonical request data cannot satisfy a plugin boundary."""


def adapt_prediction_request(
    plugin_id: str,
    payload: Dict[str, Any],
    context: Optional[Dict[str, Any]],
) -> PredictionRequest:
    """Adapt a canonical prediction request without clinical inference."""
    if not isinstance(payload, dict) or not payload:
        raise AdapterValidationError("Prediction payload must be a non-empty object.")

    if plugin_id == "soar":
        deployment_id = (context or {}).get("deployment_id")
        if not isinstance(deployment_id, str) or not deployment_id.strip():
            raise AdapterValidationError(
                "SOAR requires an explicit caller-provided context.deployment_id."
            )
        return PredictionRequest(
            payload=payload,
            context={"deployment_id": deployment_id.strip()},
        )

    return PredictionRequest(payload=payload, context=context)
