"""Clinical Decision Support System API Endpoints.

Exposes FastAPI endpoints for:
- Generating recommendations
- Retrieving explanations
- Accessing audit trails
- Clinical review interface
"""

from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field
from typing import Any, Dict, Optional, List
from datetime import datetime
import logging
import uuid

from ..clinical_decision.orchestrator import CDSSOrchestrator

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/recommendation", tags=["Clinical Decision Support"])

# Initialize CDSS
cdss = CDSSOrchestrator()


# ============================================================================
# Pydantic Models for API
# ============================================================================

class PatientData(BaseModel):
    """Patient clinical data."""
    allergies: List[str] = Field(default=[], description="Known drug allergies")
    egfr: Optional[float] = Field(None, description="eGFR (mL/min/1.73m²)")
    is_pregnant: bool = Field(False, description="Patient is pregnant")
    is_lactating: bool = Field(False, description="Patient is lactating")
    severity: str = Field("medium", description="Clinical severity (low/medium/high)")
    immunocompromised: bool = Field(False, description="Patient is immunocompromised")


class PredictionInput(BaseModel):
    """Prediction results from SOAR/ARMD."""
    antibiotic: str = Field(..., description="Antibiotic name")
    probability: float = Field(..., ge=0, le=1, description="Prediction probability (0-1)")


class RecommendationRequest(BaseModel):
    """Request for clinical recommendation.
    
    Example:
    {
        "patient_id": "P12345",
        "patient_data": {
            "allergies": ["penicillin"],
            "egfr": 60,
            "is_pregnant": false,
            "is_lactating": false,
            "severity": "high"
        },
        "predictions": [
            {"antibiotic": "amoxicillin", "probability": 0.85},
            {"antibiotic": "cephalexin", "probability": 0.75}
        ],
        "prediction_plugin": {
            "name": "SOAR",
            "version": "0.1.0",
            "models": {
                "soar_model": "v1.0.0"
            }
        }
    }
    """
    patient_id: str = Field(..., description="Patient identifier")
    patient_data: PatientData = Field(..., description="Clinical data")
    predictions: List[PredictionInput] = Field(..., description="Predictions from plugins")
    prediction_plugin: Dict[str, Any] = Field(
        default={},
        description="Plugin metadata (name, version, models)"
    )
    prediction_explanation: Optional[Dict[str, Any]] = Field(
        None,
        description="SHAP or other explanation from prediction plugin"
    )


class RecommendationResponse(BaseModel):
    """Response with clinical recommendation."""
    status: str
    patient_id: str
    recommendation: Dict[str, Any]
    explanation: Dict[str, Any]
    audit_trail: Dict[str, Any]
    generated_at: str
    trace_id: str


class ExplanationRequest(BaseModel):
    """Request for detailed explanation."""
    recommendation_id: str = Field(..., description="Recommendation ID")
    include_shap: bool = Field(True, description="Include SHAP explanation")
    include_rules: bool = Field(True, description="Include rule explanations")
    include_guidelines: bool = Field(True, description="Include guideline evidence")
    include_stewardship: bool = Field(True, description="Include stewardship analysis")


class ClinicalReviewRequest(BaseModel):
    """Clinical review of a recommendation.
    
    Clinicians can record their review decision.
    """
    recommendation_id: str = Field(..., description="Recommendation ID")
    clinician_id: str = Field(..., description="Clinician identifier")
    review_decision: str = Field(..., description="APPROVED, MODIFIED, REJECTED")
    selected_antibiotic: Optional[str] = Field(None, description="Antibiotic selected by clinician")
    clinical_notes: Optional[str] = Field(None, description="Clinician notes")
    reason_for_deviation: Optional[str] = Field(None, description="If deviating from recommendation")


# ============================================================================
# API Endpoints
# ============================================================================

@router.post(
    "/",
    response_model=RecommendationResponse,
    summary="Generate Clinical Recommendation",
    description="Generates a clinical recommendation based on patient data and predictions"
)
async def generate_recommendation(request: RecommendationRequest) -> Dict[str, Any]:
    """Generate a clinical recommendation.
    
    This is the main CDSS endpoint. It takes patient data and prediction results,
    then produces a complete clinical recommendation with evidence and explanation.
    
    Args:
        request: RecommendationRequest with patient data and predictions
        
    Returns:
        RecommendationResponse with recommendation, explanation, audit trail
        
    Raises:
        HTTPException: If generation fails
    """
    try:
        # Generate trace ID for logging
        trace_id = str(uuid.uuid4())
        
        logger.info(
            "Recommendation request received",
            extra={
                "patient_id": request.patient_id,
                "trace_id": trace_id,
                "predictions_count": len(request.predictions)
            }
        )
        
        # Convert predictions to dict
        prediction_results = {
            p.antibiotic: p.probability for p in request.predictions
        }
        
        # Get plugin version
        plugin_version = request.prediction_plugin.get("version", "0.1.0")
        model_versions = request.prediction_plugin.get("models", {})
        
        # Generate recommendation
        response = cdss.generate_recommendation(
            patient_id=request.patient_id,
            patient_data=request.patient_data.dict(),
            prediction_results=prediction_results,
            prediction_explanation=request.prediction_explanation,
            prediction_plugin_version=plugin_version,
            model_versions=model_versions,
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
        
        logger.info(
            "Recommendation generated successfully",
            extra={
                "patient_id": request.patient_id,
                "primary_recommendation": response["recommendation"].get("primary_recommendation", {}).get("antibiotic_name"),
                "trace_id": trace_id
            }
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error generating recommendation"
        )


@router.post(
    "/explanation",
    summary="Get Detailed Explanation",
    description="Retrieves detailed explanation for a recommendation"
)
async def get_explanation(request: ExplanationRequest) -> Dict[str, Any]:
    """Get detailed explanation for a recommendation.
    
    Args:
        request: ExplanationRequest
        
    Returns:
        Explanation with evidence breakdown
    """
    try:
        logger.info(f"Explanation request for {request.recommendation_id}")
        
        # In production, this would retrieve from database
        return {
            "status": "success",
            "recommendation_id": request.recommendation_id,
            "message": "Explanation functionality implemented in v0.2.0",
            "guidance": "Use POST / endpoint to get full explanation with recommendation"
        }
        
    except Exception as e:
        logger.error(f"Explanation retrieval failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Error retrieving explanation"
        )


@router.post(
    "/clinical-review",
    summary="Record Clinical Review",
    description="Records clinician's review and decision for a recommendation"
)
async def clinical_review(request: ClinicalReviewRequest) -> Dict[str, Any]:
    """Record clinical review decision.
    
    Allows clinicians to record their decision: approved, modified, or rejected.
    
    Args:
        request: ClinicalReviewRequest
        
    Returns:
        Confirmation of review recorded
    """
    try:
        logger.info(
            "Clinical review recorded",
            extra={
                "recommendation_id": request.recommendation_id,
                "clinician_id": request.clinician_id,
                "decision": request.review_decision
            }
        )
        
        # In production, this would persist to database for audit trail
        return {
            "status": "success",
            "recommendation_id": request.recommendation_id,
            "review_decision": request.review_decision,
            "clinician_id": request.clinician_id,
            "recorded_at": datetime.utcnow().isoformat(),
            "message": "Clinical review recorded successfully"
        }
        
    except Exception as e:
        logger.error(f"Clinical review recording failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Error recording clinical review"
        )


@router.get(
    "/health",
    summary="CDSS Health Check",
    description="Check if CDSS is operational"
)
async def health_check() -> Dict[str, str]:
    """Health check endpoint.
    
    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "component": "clinical-decision-support-system",
        "version": "0.1.0"
    }


# ============================================================================
# Error Handlers
# ============================================================================

@router.post("/error-test")
async def error_test() -> Dict[str, str]:
    """Endpoint for testing error handling."""
    raise HTTPException(
        status_code=400,
        detail="This is a test error"
    )
