from __future__ import annotations

from typing import Any, Dict, Optional


class ResponseFormatter:
    """Formats the final CDSS response for API and downstream callers."""

    def format(
        self,
        patient_id: str,
        recommendation: Dict[str, Any],
        explanation: Optional[Dict[str, Any]],
        audit_trail: Optional[Dict[str, Any]],
        status: str = "success",
        clinical_decision_context: Optional[Dict[str, Any]] = None,
        clinical_rule_results: Optional[list[dict[str, Any]]] = None,
        error_message: Optional[str] = None,
    ) -> Dict[str, Any]:
        response = {
            "status": status,
            "patient_id": patient_id,
            "recommendation": recommendation or {},
            "explanation": explanation or {"clinical_narrative": "No explanation available"},
            "audit_trail": audit_trail or {},
            "clinical_decision_context": clinical_decision_context or {},
            "clinical_rule_results": clinical_rule_results or [],
        }
        if error_message:
            response["error_message"] = error_message
        return response
