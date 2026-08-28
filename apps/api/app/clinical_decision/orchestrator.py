"""Clinical Decision Support System (CDSS) Orchestrator.

Main entry point for the clinical decision intelligence layer.

Orchestrates:
1. Receiving prediction plugin outputs (SOAR/ARMD)
2. Evaluating clinical rules
3. Retrieving guideline evidence
4. Analyzing stewardship
5. Fusing decision
6. Generating explanations
7. Creating audit trail

The orchestrator coordinates all components without performing prediction itself.
"""

import logging
from typing import Any, Dict, Optional
from datetime import datetime, timezone

from .contracts import RecommendationResult, RecommendationExplanation, AuditTrail
from .decision_fusion import DecisionFusionEngine
from .explainability import ExplainabilityEngine

logger = logging.getLogger(__name__)


class CDSSOrchestrator:
    """Orchestrates the complete CDSS pipeline.
    
    Responsibilities:
    - Validate inputs
    - Coordinate engines
    - Combine outputs
    - Handle errors
    - Maintain audit trail
    """

    def __init__(self):
        """Initialize CDSS orchestrator with engines."""
        self.decision_fusion_engine = DecisionFusionEngine()
        self.explainability_engine = ExplainabilityEngine()
        self.logger = logging.getLogger(__name__)

    def generate_recommendation(
        self,
        patient_id: str,
        patient_data: Dict[str, Any],
        prediction_results: Dict[str, float],  # antibiotic -> probability
        prediction_explanation: Optional[Dict[str, Any]] = None,  # SHAP output
        prediction_plugin_version: str = "0.1.0",
        model_versions: Optional[Dict[str, str]] = None,
        trace_id: str = "",
    ) -> Dict[str, Any]:
        """Generate a complete clinical recommendation.
        
        This is the core orchestration entry point for the CDSS.
        
        Responsibilities:
        - Fuse evidence from all sources via Decision Fusion Engine
        - Generate unified explanation
        - Create audit trail for reproducibility
        
        Note: Explainability generation (evidence ranking, recommendation trace,
        evidence attribution) is handled by the Recommendation API endpoint,
        NOT by this orchestrator. This preserves layer separation.
        
        Args:
            patient_id: Patient identifier
            patient_data: Clinical data (allergies, renal, etc.)
            prediction_results: Antibiotic predictions from SOAR/ARMD
            prediction_explanation: SHAP/ML explanation from prediction plugin
            prediction_plugin_version: Version of prediction plugin
            model_versions: Specific model versions
            trace_id: Distributed trace ID for logging
            
        Returns:
            Dict containing recommendation, explanation, and audit trail
            (Explainability enhancement components are added by API endpoint)
            
        Raises:
            ValueError: If inputs are invalid
            RuntimeError: If generation fails
        """
        try:
            # Validate inputs
            self._validate_inputs(patient_id, patient_data, prediction_results)
            
            self.logger.info(
                "Generating clinical recommendation",
                extra={
                    "patient_id": patient_id,
                    "antibiotic_count": len(prediction_results),
                    "trace_id": trace_id
                }
            )
            
            # Step 1: Fuse decision from all evidence sources
            recommendation = self.decision_fusion_engine.fuse_decision(
                patient_id=patient_id,
                patient_data=patient_data,
                prediction_results=prediction_results,
                model_info={
                    "version": prediction_plugin_version,
                    "plugin_version": prediction_plugin_version,
                },
            )
            
            # Step 2: Generate unified explanation
            explanation = self.explainability_engine.generate_explanation(
                recommendation=recommendation,
                prediction_explanation=prediction_explanation,
                trace_id=trace_id,
            )
            
            # Step 3: Create audit trail
            audit_trail = self.explainability_engine.generate_audit_trail(
                recommendation=recommendation,
                prediction_plugin_version=prediction_plugin_version,
                model_versions=model_versions or {},
                trace_id=trace_id,
            )
            
            # Assemble core response (Explainability enhancements added by API)
            response = {
                "status": "success",
                "patient_id": patient_id,
                "recommendation": recommendation.to_dict(),
                "explanation": explanation.to_dict(),
                "audit_trail": audit_trail.to_dict(),
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "trace_id": trace_id,
            }
            
            self.logger.info(
                "Recommendation generated successfully",
                extra={
                    "patient_id": patient_id,
                    "primary_recommendation": recommendation.primary_recommendation.antibiotic_name,
                    "confidence": recommendation.confidence.value,
                    "trace_id": trace_id
                }
            )
            
            return response
            
        except ValueError as e:
            self.logger.error(f"Invalid input: {e}", exc_info=True)
            return self._error_response("validation_error", str(e), patient_id, trace_id)
        except Exception as e:
            self.logger.error(f"Recommendation generation failed: {e}", exc_info=True)
            return self._error_response("internal_error", str(e), patient_id, trace_id)

    def _validate_inputs(
        self,
        patient_id: str,
        patient_data: Dict[str, Any],
        prediction_results: Dict[str, float],
    ) -> None:
        """Validate input data.
        
        Args:
            patient_id: Patient ID
            patient_data: Clinical data
            prediction_results: Predictions
            
        Raises:
            ValueError: If validation fails
        """
        if not patient_id or not isinstance(patient_id, str):
            raise ValueError("patient_id must be a non-empty string")
        
        if not isinstance(patient_data, dict):
            raise ValueError("patient_data must be a dict")
        
        if not prediction_results or not isinstance(prediction_results, dict):
            raise ValueError("prediction_results must be a non-empty dict")
        
        # Validate prediction values are between 0 and 1
        for ab, prob in prediction_results.items():
            if not isinstance(prob, (int, float)) or not (0 <= prob <= 1):
                raise ValueError(
                    f"Invalid prediction probability for {ab}: {prob} "
                    f"(must be between 0 and 1)"
                )

    def _error_response(
        self,
        error_type: str,
        error_message: str,
        patient_id: str = "",
        trace_id: str = "",
    ) -> Dict[str, Any]:
        """Create standardized error response.
        
        Args:
            error_type: Type of error
            error_message: Error message
            patient_id: Patient ID if available
            trace_id: Trace ID if available
            
        Returns:
            Error response dict
        """
        return {
            "status": "error",
            "error_type": error_type,
            "error_message": error_message,
            "patient_id": patient_id,
            "trace_id": trace_id,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
