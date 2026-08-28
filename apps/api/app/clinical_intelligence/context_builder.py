from __future__ import annotations

from typing import Any, Iterable, List

from app.plugins.manager.workflow_manager import ClinicalDecisionContext, ClinicalDecisionRequest, PluginExecutionResult


class ClinicalContextBuilder:
    """Builds the normalized decision context consumed by the clinical pipeline."""

    def build(
        self,
        request: ClinicalDecisionRequest,
        execution_results: Iterable[PluginExecutionResult],
        workflow_manager: Any | None = None,
    ) -> ClinicalDecisionContext:
        manager = workflow_manager or getattr(request, "workflow_manager", None)
        if manager is not None and hasattr(manager, "get_context"):
            return manager.get_context(request, list(execution_results))
        results = list(execution_results)
        return ClinicalDecisionContext(
            patient_id=request.patient_id,
            prediction_outputs=[self._as_prediction_output(item) for item in results if getattr(item, "plugin_type", None).value == "prediction"],
            knowledge_outputs=[self._as_knowledge_output(item) for item in results if getattr(item, "plugin_type", None).value == "knowledge"],
            plugin_metadata=[
                {
                    "plugin_id": item.plugin_id,
                    "plugin_name": item.plugin_name,
                    "plugin_type": getattr(item.plugin_type, "value", str(item.plugin_type)),
                    "success": item.success,
                }
                for item in results
            ],
            execution_metadata={
                "execution_mode": getattr(request.execution_mode, "value", str(request.execution_mode)),
                "request_id": request.request_id,
                "workflow_name": request.workflow_name,
            },
        )

    def _as_prediction_output(self, result: PluginExecutionResult) -> dict[str, Any]:
        payload = result.result if result.result is not None else {}
        if isinstance(payload, dict):
            return {"plugin_id": result.plugin_id, "plugin_name": result.plugin_name, "value": payload}
        return {"plugin_id": result.plugin_id, "plugin_name": result.plugin_name, "value": {"result": payload}}

    def _as_knowledge_output(self, result: PluginExecutionResult) -> dict[str, Any]:
        payload = result.result if result.result is not None else {}
        if isinstance(payload, dict):
            return {"plugin_id": result.plugin_id, "plugin_name": result.plugin_name, "value": payload}
        return {"plugin_id": result.plugin_id, "plugin_name": result.plugin_name, "value": {"result": payload}}
