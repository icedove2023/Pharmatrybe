from __future__ import annotations

import logging
from typing import Any, Dict, Iterable, List, Optional

from app.clinical_decision.decision_fusion import DecisionFusionEngine
from app.clinical_decision.explainability import ExplainabilityEngine
from app.clinical_decision.rules import ClinicalRulesEngine
from app.plugins.manager.workflow_manager import (
    ClinicalDecisionRequest,
    ClinicalDecisionContext,
    PluginExecutionResult,
    WorkflowManager,
)

from .response_formatter import ResponseFormatter


class ClinicalIntelligencePipeline:
    """
    Pure orchestration layer for clinical decision intelligence.

    Responsibilities:
    - Receive ClinicalDecisionContext from WorkflowManager
    - Evaluate clinical rules against prediction-derived candidates
    - Fuse evidence from predictions, rules, and knowledge
    - Generate recommendations
    - Produce explanations and audit trails

    Does NOT:
    - Generate or invent antibiotic candidates
    - Execute plugins
    - Create default treatment options
    - Perform prediction

    All candidate antibiotics originate exclusively from Prediction Plugins.
    """

    def __init__(self, workflow_manager: Optional[WorkflowManager] = None) -> None:
        self.workflow_manager = workflow_manager
        self.rules_engine = ClinicalRulesEngine()
        self.decision_fusion_engine = DecisionFusionEngine()
        self.explainability_engine = ExplainabilityEngine()
        self.response_formatter = ResponseFormatter()
        self.logger = logging.getLogger(__name__)

    def process(self, request: ClinicalDecisionRequest) -> Dict[str, Any]:
        """
        Execute the clinical intelligence pipeline.

        Flow:
        1. Orchestrate plugins via WorkflowManager → ClinicalDecisionContext
        2. Extract candidate antibiotics from Prediction Plugin outputs
        3. Evaluate clinical rules against candidates and patient data
        4. Fuse evidence from all sources (predictions, rules, knowledge)
        5. Generate recommendation from fused evidence
        6. Generate explanation and audit trail
        7. Format final response

        Args:
            request: ClinicalDecisionRequest with patient data and execution parameters

        Returns:
            Dict with status, recommendation, explanation, audit trail, and context
        """
        try:
            # Step 1: Orchestrate plugin execution to get decision context
            if self.workflow_manager is None:
                return self._error_response(
                    request.patient_id,
                    "WorkflowManager not configured",
                )

            execution_results = self.workflow_manager.execute(request)
            context = self.workflow_manager.get_context(request, execution_results)

            # Step 2: Extract candidate antibiotics from Prediction Plugin outputs only
            candidate_antibiotics = self._extract_candidates_from_predictions(context)

            if not candidate_antibiotics:
                return self._error_response(
                    request.patient_id,
                    "No antibiotic predictions available from Prediction Plugins. "
                    "Candidates must originate from SOAR/ARMD predictions only.",
                )

            # Step 3: Evaluate clinical rules
            patient_data = request.payload or {}
            clinical_rule_results = self.rules_engine.evaluate_all(
                patient_data, candidate_antibiotics
            )

            # Step 4: Fuse evidence from all sources
            prediction_probs = self._extract_prediction_probabilities(context)
            recommendation = self.decision_fusion_engine.fuse_decision(
                patient_id=request.patient_id,
                patient_data=patient_data,
                prediction_results=prediction_probs,
                model_info={"version": "0.1.0"},
            )

            # Step 5: Generate explanation
            explanation = self.explainability_engine.generate_explanation(
                recommendation=recommendation,
                trace_id=str(request.request_id or "pipeline"),
            )

            # Step 6: Generate audit trail
            audit_trail = self.explainability_engine.generate_audit_trail(
                recommendation=recommendation,
                prediction_plugin_version="0.1.0",
                model_versions={},
                trace_id=str(request.request_id or "pipeline"),
            )

            # Step 7: Format response
            response = self.response_formatter.format(
                patient_id=request.patient_id,
                recommendation=recommendation.to_dict(),
                explanation=explanation.to_dict(),
                audit_trail=audit_trail.to_dict(),
                status="success",
                clinical_decision_context={
                    "prediction_outputs": context.prediction_outputs,
                    "knowledge_outputs": context.knowledge_outputs,
                    "plugin_metadata": context.plugin_metadata,
                    "execution_metadata": context.execution_metadata,
                    "candidate_antibiotics": candidate_antibiotics,
                },
                clinical_rule_results=[item.to_dict() for item in clinical_rule_results],
            )

            self.logger.info(
                "Clinical intelligence pipeline completed",
                extra={
                    "patient_id": request.patient_id,
                    "candidate_count": len(candidate_antibiotics),
                    "recommendation": recommendation.primary_recommendation.antibiotic_name,
                },
            )

            return response

        except Exception as exc:
            self.logger.exception("Clinical intelligence pipeline failed")
            return self._error_response(request.patient_id, str(exc))

    def _coerce_prediction_payload(self, prediction_output: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize plugin output into the expected probability payload."""
        value = prediction_output.get("value", {})

        if isinstance(value, dict):
            return value

        if hasattr(value, "probabilities") and isinstance(value.probabilities, dict):
            return {"probabilities": value.probabilities}

        raw_output = getattr(value, "raw_output", None)
        if isinstance(raw_output, dict):
            return raw_output

        return {}

    def _extract_candidates_from_predictions(self, context: ClinicalDecisionContext) -> List[str]:
        """
        Extract antibiotic candidates from Prediction Plugin outputs.

        This is the ONLY source of candidate antibiotics.

        Args:
            context: ClinicalDecisionContext with plugin outputs

        Returns:
            List of antibiotic names from predictions (or empty list if none)

        Raises:
            No exceptions; returns empty list if no predictions found
        """
        candidates = set()

        for prediction_output in context.prediction_outputs:
            payload = self._coerce_prediction_payload(prediction_output)
            probs = payload.get("probabilities", {})

            if isinstance(probs, dict):
                for antibiotic_name in probs.keys():
                    if antibiotic_name and str(antibiotic_name).strip():
                        candidates.add(str(antibiotic_name).strip())

        return sorted(list(candidates))

    def _extract_prediction_probabilities(self, context: ClinicalDecisionContext) -> Dict[str, float]:
        """
        Extract antibiotic probabilities from Prediction Plugin outputs.

        Args:
            context: ClinicalDecisionContext with plugin outputs

        Returns:
            Dict mapping antibiotic name → probability
        """
        probabilities: Dict[str, float] = {}

        for prediction_output in context.prediction_outputs:
            payload = self._coerce_prediction_payload(prediction_output)
            probs = payload.get("probabilities", {})

            if isinstance(probs, dict):
                for antibiotic_name, prob in probs.items():
                    if antibiotic_name and str(antibiotic_name).strip():
                        try:
                            probabilities[str(antibiotic_name).strip()] = float(prob)
                        except (ValueError, TypeError):
                            pass

        return probabilities

    def _error_response(self, patient_id: str, error_message: str) -> Dict[str, Any]:
        """
        Return a structured error response.

        Args:
            patient_id: Patient identifier
            error_message: Error description

        Returns:
            Error response dict
        """
        self.logger.error(f"Pipeline error for patient {patient_id}: {error_message}")
        return self.response_formatter.format(
            patient_id=patient_id,
            recommendation={},
            explanation={"clinical_narrative": "Recommendation could not be generated"},
            audit_trail={},
            status="error",
            clinical_decision_context={},
            clinical_rule_results=[],
            error_message=error_message,
        )
