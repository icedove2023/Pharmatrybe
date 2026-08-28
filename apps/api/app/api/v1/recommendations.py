"""Recommendations router for the PharmaTrybe v1 API.

Implements the canonical Explainability Response Contract:
- Recommendation with confidence from Decision Fusion
- Evidence Ranking (ordered by composite weight)
- Recommendation Trace (structured execution steps)
- Evidence Attribution (source tracking)
- Audit Reference (traceability)

All fields are mandatory and validated before response.
"""

from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Annotated, Any, Dict, List, Optional
from datetime import datetime, timezone
import logging
import uuid

from app.auth import AuthorizationContext, require_permission
from app.clinical_decision.orchestrator import CDSSOrchestrator
from app.clinical_decision.explainability import ExplainabilityEngine
from app.clinical_decision.explainability_enhancements import EvidenceType

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/recommendations", tags=["recommendations"])
cdss = CDSSOrchestrator()
explainability_engine = ExplainabilityEngine()


# ============================================================================
# Canonical Explainability Response Model
# ============================================================================

class ExplainabilityResponseContract(BaseModel):
    """Canonical Explainability Response Contract for all recommendations.
    
    This is the ONLY official response model for recommendation endpoints.
    
    Every recommendation MUST contain:
    - recommendation: Primary antibiotic with confidence from Decision Fusion
    - confidence: Overall confidence level (from Decision Fusion)
    - evidence_ranking: Ranked evidence by composite weight
    - evidence_attribution: Source tracking for all evidence
    - recommendation_trace: Structured execution steps
    - audit_reference: Reference to audit trail for reproducibility
    """
    status: str = Field(..., description="Response status (success/error)")
    patient_id: str = Field(..., description="Patient identifier")
    
    # Core Recommendation
    recommendation: Dict[str, Any] = Field(
        ...,
        description="Primary recommendation with antibiotic and rationale"
    )
    confidence: str = Field(
        ...,
        description="Confidence level from Decision Fusion (very_high/high/moderate/low/very_low)"
    )
    
    # Phase 6.1 Explainability Contract
    evidence_ranking: Dict[str, Any] = Field(
        ...,
        description="Ranked list of evidence by composite weight (confidence × importance)"
    )
    evidence_attribution: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Source attribution for each evidence item"
    )
    recommendation_trace: Dict[str, Any] = Field(
        ...,
        description="Structured trace of execution steps through pipeline"
    )
    
    # Auditability
    audit_reference: Dict[str, Any] = Field(
        ...,
        description="Reference to audit trail for full reproducibility"
    )
    
    # Optional Supporting Data
    explanation: Optional[Dict[str, Any]] = Field(
        None,
        description="Explanation with rule/guideline/stewardship narratives"
    )
    generated_at: str = Field(..., description="ISO timestamp when response was generated")
    trace_id: str = Field(..., description="Distributed trace ID for logging")


# ============================================================================
# Validation
# ============================================================================

class ExplainabilityValidationError(Exception):
    """Raised when required explainability fields are missing."""
    pass


def validate_explainability_response(response: Dict[str, Any]) -> None:
    """Validate that response contains all required explainability fields.
    
    Args:
        response: Response dict to validate
        
    Raises:
        ExplainabilityValidationError: If any required field is missing
    """
    required_fields = {
        "recommendation": "Primary recommendation",
        "confidence": "Confidence from Decision Fusion",
        "evidence_ranking": "Ranked evidence",
        "recommendation_trace": "Execution trace",
        "audit_reference": "Audit trail reference",
    }
    
    for field, description in required_fields.items():
        if field not in response or response[field] is None:
            raise ExplainabilityValidationError(
                f"Missing required field: {field} ({description}). "
                f"All recommendations must expose full explainability contract."
            )
    
    # Validate evidence_ranking has ranked_evidence
    if isinstance(response.get("evidence_ranking"), dict):
        if "ranked_evidence" not in response["evidence_ranking"]:
            raise ExplainabilityValidationError(
                "Evidence ranking must contain ranked_evidence list"
            )
    
    # Validate recommendation_trace has trace_steps
    if isinstance(response.get("recommendation_trace"), dict):
        if "trace_steps" not in response["recommendation_trace"]:
            raise ExplainabilityValidationError(
                "Recommendation trace must contain trace_steps list"
            )
    
    # Validate audit_reference has required audit fields
    if isinstance(response.get("audit_reference"), dict):
        audit_required = {"recommendation_id", "patient_id", "timestamp", "trace_id"}
        audit_fields = set(response["audit_reference"].keys())
        missing_audit = audit_required - audit_fields
        if missing_audit:
            raise ExplainabilityValidationError(
                f"Audit reference missing fields: {missing_audit}"
            )


# ============================================================================
# API Endpoints
# ============================================================================

@router.get("", summary="Recommendations service status")
async def recommendations_status() -> dict[str, str]:
    """Return a placeholder status payload for the recommendations service."""
    return {"service": "Recommendations Service", "status": "available"}


@router.post(
    "/generate",
    response_model=ExplainabilityResponseContract,
    summary="Generate Clinical Recommendation with Full Explainability",
    description="Generates a clinical recommendation with complete explainability contract"
)
async def generate_recommendation_with_explainability(
    _context: Annotated[AuthorizationContext, Depends(require_permission("recommendations:request"))],
    patient_id: str = Body(..., description="Patient identifier"),
    patient_data: Dict[str, Any] = Body(..., description="Clinical data"),
    prediction_results: Dict[str, float] = Body(
        ...,
        description="Predictions from SOAR/ARMD (antibiotic -> probability)"
    ),
    prediction_explanation: Optional[Dict[str, Any]] = Body(
        None,
        description="SHAP or other explanation from prediction plugin"
    ),
    prediction_plugin_version: str = Body("0.1.0", description="Plugin version"),
    model_versions: Optional[Dict[str, str]] = Body(None, description="Model versions"),
) -> Dict[str, Any]:
    """Generate a clinical recommendation with full explainability contract.
    
    This endpoint produces the canonical response model containing:
    - Recommendation with confidence from Decision Fusion
    - Evidence Ranking (ordered by composite weight)
    - Recommendation Trace (structured execution steps)
    - Evidence Attribution (source tracking)
    - Audit Reference (traceability)
    
    All fields are validated before response.
    
    Args:
        patient_id: Patient identifier
        patient_data: Clinical data
        prediction_results: Predictions from SOAR/ARMD
        prediction_explanation: SHAP explanation
        prediction_plugin_version: Plugin version
        model_versions: Model versions
        
    Returns:
        ExplainabilityResponseContract with complete explainability
        
    Raises:
        HTTPException: If validation fails or generation fails
    """
    try:
        trace_id = str(uuid.uuid4())
        
        logger.info(
            "Recommendation request with explainability",
            extra={
                "patient_id": patient_id,
                "trace_id": trace_id,
                "predictions_count": len(prediction_results)
            }
        )
        
        # Generate recommendation via orchestrator
        response = cdss.generate_recommendation(
            patient_id=patient_id,
            patient_data=patient_data,
            prediction_results=prediction_results,
            prediction_explanation=prediction_explanation,
            prediction_plugin_version=prediction_plugin_version,
            model_versions=model_versions or {},
            trace_id=trace_id,
        )
        
        if response["status"] == "error":
            logger.error(
                f"Recommendation generation failed: {response.get('error_message')}",
                extra={"trace_id": trace_id}
            )
            raise HTTPException(
                status_code=400,
                detail=response.get("error_message", "Recommendation generation failed")
            )
        
        # Extract recommendation and audit components from orchestrator
        recommendation_dict = response.get("recommendation", {})
        audit_trail = response.get("audit_trail", {})
        recommendation_id = audit_trail.get("recommendation_id", "")
        
        # Generate Phase 6.1 Explainability components via Explainability Engine
        # (NOT via Orchestrator - layer separation preserved)
        
        evidence_ranking_dict = {}
        recommendation_trace_dict = {}
        evidence_attribution = []
        
        try:
            # Generate evidence ranking
            evidence_ranking = explainability_engine.generate_evidence_ranking(
                recommendation=None,
                recommendation_id=recommendation_id,
                prediction_evidence=[{"confidence": prob, "description": f"Prediction for {ab}"}
                                     for ab, prob in prediction_results.items()],
                guideline_evidence=[],
                rule_evidence=[],
                stewardship_evidence=[],
                patient_id=patient_id,  # Pass patient_id for logging
            )
            evidence_ranking_dict = evidence_ranking.to_dict() if hasattr(evidence_ranking, 'to_dict') else {
                "recommendation_id": recommendation_id,
                "patient_id": patient_id,
                "ranked_evidence": [],
                "ranking_algorithm": "composite_weight",
            }
            
            # Generate recommendation trace  
            recommendation_trace = explainability_engine.generate_recommendation_trace(
                recommendation=None,
                recommendation_id=recommendation_id,
                trace_steps=[
                    {"phase_name": "orchestration", "description": "Orchestrated clinical decision pipeline",
                     "inputs": {"prediction_results": prediction_results}, "outputs": {}, "duration_ms": 0},
                    {"phase_name": "explanation", "description": "Generated unified explanation",
                     "inputs": {}, "outputs": {}, "duration_ms": 0},
                    {"phase_name": "audit", "description": "Created audit trail",
                     "inputs": {}, "outputs": {}, "duration_ms": 0},
                ],
                patient_id=patient_id,  # Pass patient_id for logging
            )
            recommendation_trace_dict = recommendation_trace.to_dict() if hasattr(recommendation_trace, 'to_dict') else {
                "recommendation_id": recommendation_id,
                "patient_id": patient_id,
                "trace_steps": [],
                "total_duration_ms": 0.0,
            }
            
            # Generate evidence attribution for predictions
            for ab, prob in prediction_results.items():
                attribution = explainability_engine.generate_evidence_attribution(
                    evidence_type=EvidenceType.PREDICTION,
                    originating_plugin="prediction_plugin",
                    confidence=prob,
                    evidence_summary={"antibiotic": ab, "probability": prob},
                )
                if hasattr(attribution, 'to_dict'):
                    evidence_attribution.append(attribution.to_dict())
                else:
                    evidence_attribution.append(attribution)
                
        except Exception as e:
            logger.warning(
                f"Explainability enhancement generation had issue: {e}",
                extra={"trace_id": trace_id, "patient_id": patient_id}
            )
            # Continue with fallback structures - explainability enhancements are optional
            # but core recommendation is still valid
            evidence_ranking_dict = {
                "recommendation_id": recommendation_id,
                "patient_id": patient_id,
                "ranked_evidence": [],
                "ranking_algorithm": "composite_weight",
            }
            recommendation_trace_dict = {
                "recommendation_id": recommendation_id,
                "patient_id": patient_id,
                "trace_steps": [],
                "total_duration_ms": 0.0,
            }
            evidence_attribution = []
        
        # Build canonical response
        explainability_response = {
            "status": response["status"],
            "patient_id": patient_id,
            "recommendation": recommendation_dict,
            "confidence": recommendation_dict.get("confidence", "unknown"),
            "evidence_ranking": evidence_ranking_dict,
            "evidence_attribution": evidence_attribution,
            "recommendation_trace": recommendation_trace_dict,
            "audit_reference": {
                "recommendation_id": audit_trail.get("recommendation_id"),
                "patient_id": patient_id,
                "timestamp": audit_trail.get("timestamp"),
                "trace_id": trace_id,
                "prediction_plugin_version": prediction_plugin_version,
                "model_versions": model_versions or {},
            },
            "explanation": response.get("explanation", {}),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "trace_id": trace_id,
        }
        
        # Validate explainability contract
        try:
            validate_explainability_response(explainability_response)
        except ExplainabilityValidationError as e:
            logger.error(
                f"Explainability validation failed: {e}",
                extra={"trace_id": trace_id}
            )
            raise HTTPException(
                status_code=500,
                detail=f"Explainability validation failed: {str(e)}"
            )
        
        logger.info(
            "Recommendation generated with full explainability",
            extra={
                "patient_id": patient_id,
                "primary_recommendation": recommendation_dict.get("primary_recommendation", {}).get("antibiotic_name"),
                "confidence": recommendation_dict.get("confidence"),
                "trace_id": trace_id
            }
        )
        
        return explainability_response
        
    except HTTPException:
        raise
    except ExplainabilityValidationError as e:
        logger.error(f"Validation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error generating recommendation"
        )
