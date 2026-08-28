"""ARMD Explainability Adapter.

Maps WP4 SHAP output to structured explainability using the
ExplainabilityPayload contract.
"""

from __future__ import annotations

import logging
from typing import Dict, Any, Optional

from packages.prediction_framework.contracts import (
    ModelPackage,
    PredictionExecution,
    ExplainabilityPayload,
)
from packages.prediction_framework.adapters import ARMDAdapter, ARMDAdapterError
from packages.prediction_framework.explainability import BaseExplainabilityAdapter

logger = logging.getLogger(__name__)


class ARMDExplainability(BaseExplainabilityAdapter):
    """Generates SHAP-based explanations for ARMD predictions.
    
    Maps WP4 SHAP computation results into structured
    explainability payloads for clinician consumption.
    """

    def __init__(self, adapter: Optional[ARMDAdapter] = None, config: Optional[Dict[str, Any]] = None):
        """Initialize explainability adapter.
        
        Args:
            adapter: ARMDAdapter instance (should be initialized)
            config: Configuration dict (optional)
        """
        super().__init__(config=config)
        self.adapter = adapter
        self.config = config or {}

    def explain(
        self,
        model_package: ModelPackage,
        patient_data: Dict[str, Any],
        prediction_execution: PredictionExecution,
    ) -> ExplainabilityPayload:
        """Generate SHAP explanation for a prediction.
        
        Args:
            model_package: Loaded ModelPackage
            patient_data: Patient features dictionary
            prediction_execution: The prediction to explain
            
        Returns:
            ExplainabilityPayload with SHAP drivers and narrative
            
        Raises:
            RuntimeError: If adapter not initialized or explainability fails
        """
        if self.adapter is None:
            raise RuntimeError("Adapter not initialized")
        
        try:
            return self.adapter.explain(model_package, patient_data, prediction_execution)
        except ARMDAdapterError as e:
            logger.error(f"Explainability generation failed: {e}", exc_info=True)
            # Return minimal payload on error (graceful degradation)
            return ExplainabilityPayload(
                prediction_id=f"{model_package.id}_{patient_data.get('patient_id', 'unknown')}",
                model_id=model_package.id,
                narrative=f"Explanation generation failed: {str(e)}",
            )
        except Exception as e:
            logger.error(f"Unexpected error in explainability: {e}", exc_info=True)
            return ExplainabilityPayload(
                prediction_id=f"{model_package.id}_{patient_data.get('patient_id', 'unknown')}",
                model_id=model_package.id,
                narrative=f"Explanation error: {str(e)}",
            )
