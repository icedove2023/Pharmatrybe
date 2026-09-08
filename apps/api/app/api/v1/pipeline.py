"""HTTP entry point for plugin-driven clinical intelligence orchestration."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Annotated, Any, Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.auth import AuthorizationContext, require_permission
from app.clinical_intelligence.pipeline import ClinicalIntelligencePipeline
from app.core.config import settings
from app.plugins.manager.plugin_manager import PluginManager
from app.plugins.manager.workflow_manager import ClinicalDecisionRequest, ExecutionMode, WorkflowManager
from app.plugins.identity import canonical_plugin_id

from .recommendations import ExplainabilityResponseContract, validate_explainability_response

router = APIRouter(prefix="/pipeline", tags=["pipeline"])


class PipelinePluginSelection(BaseModel):
    """A plugin selected by the clinician workflow."""

    plugin_id: str = Field(..., min_length=1)
    plugin_version: Optional[str] = None
    plugin_role: Optional[str] = None
    configuration: Optional[Dict[str, Any]] = None


class PipelineExecutionRequest(BaseModel):
    """Canonical request for one synchronous plugin-driven execution."""

    execution_mode: str = "sync"
    request_id: Optional[str] = None
    patient_id: str = Field(..., min_length=1)
    case_id: Optional[str] = None
    plugin_selection: List[PipelinePluginSelection] = Field(default_factory=list)
    input_payload: Dict[str, Any] = Field(default_factory=dict)
    routing_context: Dict[str, Any] = Field(default_factory=dict)
    response_mode: str = "full"


@lru_cache(maxsize=1)
def _pipeline_runtime() -> ClinicalIntelligencePipeline:
    """Load the governed internal plugin catalog once for API requests."""
    plugin_root = Path(__file__).resolve().parents[2] / "plugins"
    manager = PluginManager(
        plugin_root=plugin_root,
        platform_version=settings.app_version,
        sdk_version="0.1.0",
    )
    load_results = manager.load_all_plugins()
    failed = [result.plugin_id for result in load_results if not result.success]
    if failed:
        raise RuntimeError(f"Plugin runtime initialization failed for: {', '.join(failed)}")
    return ClinicalIntelligencePipeline(WorkflowManager(manager.registry))


def _patient_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Extract the assessment case while preserving direct payload compatibility."""
    case = payload.get("case")
    return case if isinstance(case, dict) else payload


@router.get("/schema")
async def get_pipeline_schema() -> Dict[str, Any]:
    """Expose the live plugin input contract for pipeline execution."""
    from app.plugins.manager.plugin_manager import PluginManager
    from app.plugins.schema.composer import PluginSchemaComposer

    plugin_root = Path(__file__).resolve().parents[2] / "plugins"
    manager = PluginManager(
        plugin_root=plugin_root,
        platform_version=settings.app_version,
        sdk_version="0.1.0",
    )
    manager.load_all_plugins()
    composer = PluginSchemaComposer(manager)
    composition = composer.compose([plugin.plugin_id for plugin in manager.list_plugins()])
    return {
        "plugin_ids": sorted([plugin.plugin_id for plugin in manager.list_plugins()]),
        "schema": composition["schema"],
        "composed_schema": composition["composed_schema"],
        "field_provenance": composition["field_provenance"],
        "conflicts": composition["conflicts"],
        "canonical_field_metadata": composition["canonical_field_metadata"],
        "canonical_plugin_mappings": composition["canonical_plugin_mappings"],
        "plugin_runtime_mappings": composition["plugin_runtime_mappings"],
    }


@router.post("/execute", response_model=ExplainabilityResponseContract)
async def execute_pipeline(
    request: PipelineExecutionRequest,
    _context: Annotated[AuthorizationContext, Depends(require_permission("recommendations:request"))],
) -> Dict[str, Any]:
    """Execute selected knowledge and prediction plugins and synthesize a recommendation."""
    if request.execution_mode != "sync":
        raise HTTPException(status_code=501, detail="Asynchronous pipeline execution is not exposed yet.")

    try:
        pipeline = _pipeline_runtime()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Plugin runtime is unavailable: {exc}") from exc

    selected_ids = [canonical_plugin_id(item.plugin_id) for item in request.plugin_selection]
    available_ids = {plugin.plugin_id for plugin in pipeline.workflow_manager.registry.list_plugins()} if pipeline.workflow_manager else set()
    unknown_ids = sorted(set(selected_ids) - available_ids)
    if unknown_ids:
        raise HTTPException(status_code=422, detail=f"Requested plugins are not available: {', '.join(unknown_ids)}")

    patient_data = _patient_payload(request.input_payload)
    request_context = dict(request.routing_context)
    if request.case_id:
        request_context.setdefault("case_id", request.case_id)

    plugin_request = ClinicalDecisionRequest(
        patient_id=request.patient_id,
        payload=patient_data,
        context=request_context or None,
        execution_mode=ExecutionMode.USER_SELECTED if selected_ids else ExecutionMode.AUTO,
        plugin_ids=selected_ids,
        request_id=request.request_id or str(uuid4()),
    )
    response = pipeline.process(plugin_request)
    if response.get("status") == "error":
        raise HTTPException(status_code=422, detail=response.get("error_message", "Pipeline execution failed."))

    audit = response.get("audit_trail") or {}
    trace_id = str(audit.get("trace_id") or plugin_request.request_id)
    recommendation = response.get("recommendation") or {}
    recommendation_id = audit.get("recommendation_id") or f"rec-{trace_id}"
    probabilities = {}
    context = response.get("clinical_decision_context") or {}
    for output in context.get("prediction_outputs", []):
        value = output.get("value", {}) if isinstance(output, dict) else {}
        if isinstance(value, dict):
            probabilities.update(value.get("probabilities", {}))

    explainability = pipeline.explainability_engine
    evidence_ranking = explainability.generate_evidence_ranking(
        recommendation=None,
        recommendation_id=recommendation_id,
        prediction_evidence=[{"confidence": probability, "description": f"Prediction for {antibiotic}"} for antibiotic, probability in probabilities.items()],
        guideline_evidence=[],
        rule_evidence=[],
        stewardship_evidence=[],
        patient_id=request.patient_id,
    )
    trace = explainability.generate_recommendation_trace(
        recommendation=None,
        recommendation_id=recommendation_id,
        trace_steps=[{
            "phase_name": "plugin_orchestration",
            "description": "Executed selected knowledge and prediction plugins",
            "inputs": {"plugin_selection": selected_ids},
            "outputs": {"plugin_metadata": context.get("plugin_metadata", [])},
            "duration_ms": 0,
        }],
        patient_id=request.patient_id,
    )
    canonical = {
        "status": "success",
        "patient_id": request.patient_id,
        "recommendation": recommendation,
        "confidence": recommendation.get("confidence", "unknown"),
        "evidence_ranking": evidence_ranking.to_dict() if hasattr(evidence_ranking, "to_dict") else evidence_ranking,
        "evidence_attribution": [],
        "recommendation_trace": trace.to_dict() if hasattr(trace, "to_dict") else trace,
        "audit_reference": {
            "recommendation_id": recommendation_id,
            "patient_id": request.patient_id,
            "timestamp": audit.get("timestamp"),
            "trace_id": trace_id,
            "plugin_selection": selected_ids,
        },
        "explanation": response.get("explanation") or {},
        "generated_at": audit.get("timestamp"),
        "trace_id": trace_id,
    }
    try:
        validate_explainability_response(canonical)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Pipeline explainability contract failed: {exc}") from exc
    return canonical
