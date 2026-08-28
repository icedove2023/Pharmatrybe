from __future__ import annotations

import time
from datetime import datetime, timezone
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from app.plugins.base.knowledge_plugin import KnowledgePlugin
from app.plugins.base.plugin import BasePlugin, PluginType
from app.plugins.base.prediction_plugin import PredictionPlugin, PredictionRequest
from app.plugins.manager.plugin_registry import PluginRegistry
from app.plugins.manager.plugin_routing_policy import PluginRoutingPolicy
from app.auth.tenant_context import TenantContext


class ExecutionMode(str, Enum):
    """Selection strategy for plugin execution."""

    AUTO = "auto"
    PREDICTION_ONLY = "prediction_only"
    KNOWLEDGE_ONLY = "knowledge_only"
    HYBRID = "hybrid"
    AUTOMATIC = "automatic"
    USER_SELECTED = "user_selected"
    WORKFLOW_SELECTED = "workflow_selected"


@dataclass(frozen=True)
class ClinicalDecisionRequest:
    """Normalized runtime request for the plugin orchestration layer."""

    patient_id: str
    payload: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None
    hospital_id: Optional[str] = None
    tenant_context: Optional[TenantContext] = None
    execution_mode: ExecutionMode = ExecutionMode.AUTO
    plugin_ids: List[str] = field(default_factory=list)
    plugin_types: List[PluginType] = field(default_factory=list)
    prediction_plugins: List[str] = field(default_factory=list)
    knowledge_plugins: List[str] = field(default_factory=list)
    workflow_name: Optional[str] = None
    request_id: Optional[str] = None

    def selected_plugin_ids(self) -> List[str]:
        """Return the explicit plugin IDs requested by the caller."""
        ids = list(self.plugin_ids)
        ids.extend(self.prediction_plugins)
        ids.extend(self.knowledge_plugins)
        return ids

    def resolved_tenant_context(self) -> TenantContext | None:
        """Return the explicit tenant context, rejecting conflicting legacy IDs."""
        if self.tenant_context is not None:
            if self.hospital_id is not None and self.hospital_id != self.tenant_context.hospital_id:
                raise ValueError("TENANT_MISMATCH")
            return self.tenant_context
        return None


@dataclass
class ClinicalDecisionContext:
    """Shared context created by the plugin orchestrator for downstream engines."""

    patient_id: str
    prediction_outputs: List[Dict[str, Any]] = field(default_factory=list)
    knowledge_outputs: List[Dict[str, Any]] = field(default_factory=list)
    plugin_metadata: List[Dict[str, Any]] = field(default_factory=list)
    execution_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PluginExecutionResult:
    """Outcome for a single plugin execution within the workflow."""

    plugin_id: str
    plugin_name: str
    plugin_type: PluginType
    success: bool
    result: Any = None
    error: Optional[str] = None
    execution_time_ms: float = 0.0
    evidence: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class WorkflowManager:
    """Thin orchestration layer between workflow requests and plugin execution."""

    def __init__(self, registry: PluginRegistry) -> None:
        self.registry = registry
        self.routing_policy = PluginRoutingPolicy()

    def execute(self, request: ClinicalDecisionRequest) -> List[PluginExecutionResult]:
        """Execute the selected plugins for a clinical decision request."""
        selected_plugins = self._select_plugins(request)
        results = [self._execute_plugin(plugin, request) for plugin in selected_plugins]
        selected_ids = {plugin.plugin_id for plugin in selected_plugins}
        requested_ids = set(request.selected_plugin_ids())
        for plugin_id in requested_ids - selected_ids:
            tenant_context = request.resolved_tenant_context()
            if tenant_context is None:
                continue
            try:
                plugin = self.registry.resolve_plugin(tenant_context, plugin_id)
            except ValueError:
                plugin = self.registry.get_plugin_for_tenant(tenant_context, plugin_id)
            if plugin is None:
                continue
            denied_result = PluginExecutionResult(
                plugin_id=plugin_id,
                plugin_name=getattr(plugin, "plugin_name", plugin_id),
                plugin_type=getattr(plugin, "plugin_type", PluginType.PREDICTION),
                success=False,
                error="Plugin is not runtime-eligible for this request",
                metadata={"patient_id": request.patient_id, "request_id": request.request_id},
            )
            self._record_execution(plugin, request, denied_result, time.perf_counter())
            results.append(denied_result)
        return results

    def get_context(self, request: ClinicalDecisionRequest, results: List[PluginExecutionResult]) -> ClinicalDecisionContext:
        """Build a decision context from the collected plugin outputs."""
        prediction_outputs = []
        knowledge_outputs = []
        plugin_metadata = []
        for result in results:
            plugin_metadata.append({
                "plugin_id": result.plugin_id,
                "plugin_name": result.plugin_name,
                "plugin_type": result.plugin_type.value,
                "success": result.success,
            })
            if result.plugin_type == PluginType.PREDICTION and result.success and result.result is not None:
                prediction_outputs.append({
                    "plugin_id": result.plugin_id,
                    "plugin_name": result.plugin_name,
                    "value": result.result,
                })
            elif result.plugin_type == PluginType.KNOWLEDGE and result.success and result.result is not None:
                knowledge_outputs.append({
                    "plugin_id": result.plugin_id,
                    "plugin_name": result.plugin_name,
                    "value": result.result,
                })

        return ClinicalDecisionContext(
            patient_id=request.patient_id,
            prediction_outputs=prediction_outputs,
            knowledge_outputs=knowledge_outputs,
            plugin_metadata=plugin_metadata,
            execution_metadata={
                "execution_mode": request.execution_mode.value,
                "request_id": request.request_id,
                "workflow_name": request.workflow_name,
            },
        )

    def _select_plugins(self, request: ClinicalDecisionRequest) -> List[BasePlugin]:
        selected = self.routing_policy.route(request, self.registry)
        if not selected:
            return []
        tenant_context = request.resolved_tenant_context()
        if tenant_context is not None:
            resolved = []
            for plugin in selected:
                try:
                    tenant_plugin = self.registry.resolve_plugin(tenant_context, getattr(plugin, "plugin_id", ""))
                except ValueError:
                    tenant_plugin = None
                if tenant_plugin is not None and self.registry.is_runtime_eligible(
                    tenant_plugin.plugin_id, hospital_id=tenant_context.hospital_id
                ):
                    resolved.append(tenant_plugin)
            selected = resolved
        else:
            selected = [plugin for plugin in selected if not self.registry.is_hospital_owned(plugin)]
        return selected

    def _execute_plugin(self, plugin: BasePlugin, request: ClinicalDecisionRequest) -> PluginExecutionResult:
        start = time.perf_counter()
        plugin_type = plugin.plugin_type if hasattr(plugin, "plugin_type") else PluginType.PREDICTION
        plugin_name = plugin.plugin_name if hasattr(plugin, "plugin_name") else plugin.__class__.__name__

        try:
            if hasattr(plugin, "runtime_guard"):
                tenant_context = request.resolved_tenant_context()
                if tenant_context is None:
                    raise ValueError("TENANT_CONTEXT_REQUIRED")
                plugin.runtime_guard(tenant_context)
            if isinstance(plugin, PredictionPlugin):
                prediction_request = PredictionRequest(payload=request.payload, context=request.context)
                if hasattr(plugin, "supports") and not plugin.supports(prediction_request):
                    raise ValueError(f"Plugin {plugin.plugin_id} does not support the request.")
                result = plugin.predict(prediction_request)
                evidence = {"prediction": result.__dict__ if hasattr(result, "__dict__") else str(result)}
            elif isinstance(plugin, KnowledgePlugin):
                query_value = request.payload.get("query") if isinstance(request.payload, dict) else str(request.payload)
                filters = request.context or {}
                if hasattr(plugin, "search"):
                    result = plugin.search(query_value or "", filters)
                else:
                    result = plugin.query(request.payload)
                evidence = {"knowledge": result}
            else:
                if hasattr(plugin, "execute"):
                    result = plugin.execute(request.payload, request.context)
                elif hasattr(plugin, "run"):
                    result = plugin.run(request.payload, request.context)
                else:
                    result = {"status": "not_supported", "plugin_id": plugin.plugin_id}
                evidence = {"plugin_output": result}

            elapsed_ms = (time.perf_counter() - start) * 1000.0
            execution_result = PluginExecutionResult(
                plugin_id=plugin.plugin_id,
                plugin_name=plugin_name,
                plugin_type=plugin_type,
                success=True,
                result=result,
                execution_time_ms=elapsed_ms,
                evidence=evidence,
                metadata={"patient_id": request.patient_id, "request_id": request.request_id, **self._plugin_provenance(plugin)},
            )
            self._record_execution(plugin, request, execution_result, start)
            return execution_result
        except Exception as exc:
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            execution_result = PluginExecutionResult(
                plugin_id=getattr(plugin, "plugin_id", plugin.__class__.__name__),
                plugin_name=plugin_name,
                plugin_type=plugin_type,
                success=False,
                error=str(exc),
                execution_time_ms=elapsed_ms,
                metadata={"patient_id": request.patient_id, "request_id": request.request_id, **self._plugin_provenance(plugin)},
            )
            self._record_execution(plugin, request, execution_result, start)
            return execution_result

    def _record_execution(self, plugin: BasePlugin, request: ClinicalDecisionRequest, result: PluginExecutionResult, start: float) -> None:
        """Persist bounded external execution provenance when a DB service is available."""
        service = getattr(self.registry, "governance_service", None)
        if service is None or not hasattr(plugin, "artifact_hash"):
            return
        now = datetime.now(timezone.utc)
        tenant_context = request.resolved_tenant_context()
        if tenant_context is None:
            raise ValueError("TENANT_CONTEXT_REQUIRED")
        tenant_context.require_same_hospital(plugin.tenant_context.hospital_id)
        record = service.get_record(plugin.plugin_id, hospital_id=tenant_context.hospital_id)
        service.record_execution(
            hospital_id=tenant_context.hospital_id,
            authenticated_user_id=tenant_context.authenticated_user_id,
            professional_id=tenant_context.professional_id,
            plugin_id=plugin.plugin_id,
            plugin_version=plugin.plugin_version,
            artifact_hash=plugin.artifact_hash,
            governance_record_id=record.id,
            execution_mode="isolated",
            isolation_mode="subprocess-restricted-environment",
            isolation_level="development-subprocess",
            cpu_enforced=False,
            memory_enforced=False,
            network_enforced=False,
            filesystem_enforced=False,
            identity_enforced=False,
            resource_policy_status="DEVELOPMENT_ONLY",
            trust_level=record.trust_level,
            requested_capabilities=list(getattr(plugin, "capabilities", [])),
            decision="ALLOW" if result.success else "DENY",
            execution_status="SUCCESS" if result.success else "FAILURE",
            started_at=datetime.fromtimestamp(time.time() - result.execution_time_ms / 1000, tz=timezone.utc),
            completed_at=now,
            duration_ms=result.execution_time_ms,
            timed_out=bool(result.error and "timed out" in result.error.lower()),
            denial_reason=None if result.success else result.error,
            failure_reason=None if result.success else result.error,
        )

    @staticmethod
    def _plugin_provenance(plugin: BasePlugin) -> Dict[str, Any]:
        """Return non-sensitive governance provenance for execution tracing."""
        if not hasattr(plugin, "artifact_hash"):
            return {"execution_mode": "internal"}
        return {
            "execution_mode": "isolated",
            "plugin_version": getattr(plugin, "plugin_version", None),
            "artifact_hash": getattr(plugin, "artifact_hash", None),
            "hospital_id": getattr(plugin, "hospital_id", None),
        }
