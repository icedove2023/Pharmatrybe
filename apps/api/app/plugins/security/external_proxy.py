"""Common plugin-contract proxies backed by isolated execution."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.plugins.base.knowledge_plugin import KnowledgePlugin
from app.plugins.base.plugin import PluginHealth, PluginMetadata, PluginType
from app.plugins.base.prediction_plugin import DeploymentType, PredictionPlugin, PredictionRequest, PredictionResult
from app.plugins.security.isolated_executor import IsolatedPluginExecutor
from app.plugins.security.artifact import PluginArtifactService
from app.auth.tenant_context import TenantContext
from app.plugins.security.execution_identity import ExecutionIdentity, manifest_hash


def _execute_isolated(executor, module_path, class_name, payload, context, operation):
    """Submit execution through the provider contract when available."""
    execute_request = getattr(executor, "execute_request", None)
    if execute_request is not None:
        return execute_request(
            {
                "module_path": str(module_path),
                "class_name": class_name,
                "payload": payload,
                "context": context,
                "operation": operation,
            },
            getattr(executor, "policy", None),
        )
    return executor.execute(module_path, class_name, payload, context, operation)


class ExternalPredictionProxy(PredictionPlugin):
    """Parent-process prediction contract proxy for an external plugin."""

    def __init__(self, manifest, module_path, executor: IsolatedPluginExecutor, artifact_hash: str, tenant_context: TenantContext, capabilities: list[str], governance_service=None, artifact_path=None, execution_identity: ExecutionIdentity | None = None):
        self.manifest = manifest
        self.module_path = module_path
        self.executor = executor
        self.artifact_hash = artifact_hash
        self.tenant_context = tenant_context
        self.granted_capabilities = capabilities
        self.governance_service = governance_service
        self.artifact_path = artifact_path
        self.execution_identity = execution_identity

    @property
    def plugin_id(self) -> str: return self.execution_identity.canonical_plugin_id if self.execution_identity else self.manifest.plugin_id
    @property
    def plugin_name(self) -> str: return self.manifest.plugin_name
    @property
    def plugin_version(self) -> str: return self.execution_identity.plugin_version if self.execution_identity else self.manifest.plugin_version
    @property
    def plugin_type(self) -> PluginType: return PluginType.PREDICTION
    @property
    def plugin_description(self) -> str: return self.manifest.description
    @property
    def author(self) -> str: return self.manifest.author
    @property
    def capabilities(self) -> list[str]: return list(self.execution_identity.capabilities if self.execution_identity else self.granted_capabilities)
    @property
    def dependencies(self) -> list[str]: return list(self.manifest.dependencies)
    @property
    def deployment_type(self) -> DeploymentType: return self.manifest.deployment_type or DeploymentType.ARTIFACT

    def initialize(self) -> None: pass
    def shutdown(self) -> None: pass
    def configure(self, configuration: dict[str, Any]) -> None: pass
    def validate(self) -> bool: return True
    def load(self) -> None: pass
    def unload(self) -> None: pass
    def supports(self, request: PredictionRequest) -> bool: return True
    def input_schema(self) -> dict[str, Any]: return {}
    def output_schema(self) -> dict[str, Any]: return {}

    def metadata(self) -> PluginMetadata:
        return PluginMetadata(self.plugin_id, self.plugin_name, self.plugin_version, self.plugin_type, self.plugin_description, self.author, self.capabilities, self.dependencies)

    def health(self) -> PluginHealth:
        return PluginHealth(True, "isolated", "External plugin proxy", datetime.now(timezone.utc))

    def predict(self, request: PredictionRequest) -> PredictionResult:
        self.runtime_guard(self.tenant_context)
        class_name = self.execution_identity.entrypoint_class if self.execution_identity else self.manifest.entrypoint_class
        value = _execute_isolated(self.executor, self.module_path, class_name, request.payload, request.context, "predict")
        if not isinstance(value, dict) or not {"predicted_class", "probabilities", "confidence", "model_name", "model_version", "execution_time_ms"}.issubset(value):
            raise ValueError("External prediction response does not match PredictionResult")
        if not 0 <= float(value["confidence"]) <= 1:
            raise ValueError("External prediction confidence is outside [0, 1]")
        return PredictionResult(**value)

    def runtime_guard(self, request_tenant: TenantContext | None = None) -> None:
        if request_tenant is not None and request_tenant != self.tenant_context:
            request_tenant.require_same_hospital(self.tenant_context.hospital_id)
        if self.governance_service is None or self.artifact_path is None:
            raise RuntimeError("External plugin governance context is unavailable")
        record = self.governance_service.get_record(self.plugin_id, hospital_id=self.tenant_context.hospital_id)
        self.tenant_context.require_same_hospital(record.hospital_id)
        if self.execution_identity is None:
            raise RuntimeError("External execution identity is unavailable")
        if (
            record.id != self.execution_identity.governance_id
            or record.plugin_id != self.execution_identity.canonical_plugin_id
            or record.plugin_type != self.execution_identity.plugin_type
            or record.plugin_origin != self.execution_identity.plugin_origin
            or record.artifact_hospital_id != self.execution_identity.tenant_id
        ):
            raise RuntimeError("External governance identity changed")
        if manifest_hash(self.manifest) != self.execution_identity.manifest_hash:
            raise RuntimeError("External manifest identity changed")
        governed_capabilities = tuple(sorted(str(capability).strip().upper() for capability in record.capabilities or []))
        if governed_capabilities != self.execution_identity.capabilities:
            raise RuntimeError("External capability identity changed")
        if not self.governance_service.is_runtime_eligible(self.plugin_id, hospital_id=self.tenant_context.hospital_id):
            raise RuntimeError("External plugin is no longer runtime-eligible")
        if "NETWORK_ACCESS" in self.granted_capabilities:
            raise RuntimeError("External network capability has no approved isolation mechanism")
        inspection = PluginArtifactService().inspect(self.artifact_path)
        if inspection.sha256 != self.execution_identity.artifact_hash or record.artifact_hash != self.execution_identity.artifact_hash or record.plugin_version != self.execution_identity.plugin_version:
            raise RuntimeError("External plugin artifact identity changed")


class ExternalKnowledgeProxy(KnowledgePlugin):
    """Parent-process knowledge contract proxy for an external plugin."""

    def __init__(self, manifest, module_path, executor: IsolatedPluginExecutor, artifact_hash: str, tenant_context: TenantContext, capabilities: list[str], governance_service=None, artifact_path=None, execution_identity: ExecutionIdentity | None = None):
        self.manifest = manifest
        self.module_path = module_path
        self.executor = executor
        self.artifact_hash = artifact_hash
        self.tenant_context = tenant_context
        self.granted_capabilities = capabilities
        self.governance_service = governance_service
        self.artifact_path = artifact_path
        self.execution_identity = execution_identity

    @property
    def plugin_id(self) -> str: return self.execution_identity.canonical_plugin_id if self.execution_identity else self.manifest.plugin_id
    @property
    def plugin_name(self) -> str: return self.manifest.plugin_name
    @property
    def plugin_version(self) -> str: return self.execution_identity.plugin_version if self.execution_identity else self.manifest.plugin_version
    @property
    def plugin_type(self) -> PluginType: return PluginType.KNOWLEDGE
    @property
    def plugin_description(self) -> str: return self.manifest.description
    @property
    def author(self) -> str: return self.manifest.author
    @property
    def capabilities(self) -> list[str]: return list(self.execution_identity.capabilities if self.execution_identity else self.granted_capabilities)
    @property
    def dependencies(self) -> list[str]: return list(self.manifest.dependencies)

    def initialize(self) -> None: pass
    def shutdown(self) -> None: pass
    def configure(self, configuration: dict[str, Any]) -> None: pass
    def validate(self) -> bool: return True
    def connect(self) -> None: pass
    def disconnect(self) -> None: pass
    def supported_domains(self) -> list[str]: return list(self.manifest.supported_domains)
    def knowledge_version(self) -> str: return self.plugin_version

    def metadata(self) -> PluginMetadata:
        return PluginMetadata(self.plugin_id, self.plugin_name, self.plugin_version, self.plugin_type, self.plugin_description, self.author, self.capabilities, self.dependencies)

    def health(self) -> PluginHealth:
        return PluginHealth(True, "isolated", "External plugin proxy", datetime.now(timezone.utc))

    def search(self, query: str, filters: dict[str, Any] | None = None) -> Any:
        self.runtime_guard(self.tenant_context)
        class_name = self.execution_identity.entrypoint_class if self.execution_identity else self.manifest.entrypoint_class
        return _execute_isolated(self.executor, self.module_path, class_name, query, filters, "search")

    def query(self, criteria: dict[str, Any]) -> Any:
        self.runtime_guard(self.tenant_context)
        class_name = self.execution_identity.entrypoint_class if self.execution_identity else self.manifest.entrypoint_class
        return _execute_isolated(self.executor, self.module_path, class_name, criteria, None, "query")

    def runtime_guard(self, request_tenant: TenantContext | None = None) -> None:
        if request_tenant is not None and request_tenant != self.tenant_context:
            request_tenant.require_same_hospital(self.tenant_context.hospital_id)
        if self.governance_service is None or self.artifact_path is None:
            raise RuntimeError("External plugin governance context is unavailable")
        record = self.governance_service.get_record(self.plugin_id, hospital_id=self.tenant_context.hospital_id)
        self.tenant_context.require_same_hospital(record.hospital_id)
        if self.execution_identity is None:
            raise RuntimeError("External execution identity is unavailable")
        if (
            record.id != self.execution_identity.governance_id
            or record.plugin_id != self.execution_identity.canonical_plugin_id
            or record.plugin_type != self.execution_identity.plugin_type
            or record.plugin_origin != self.execution_identity.plugin_origin
            or record.artifact_hospital_id != self.execution_identity.tenant_id
        ):
            raise RuntimeError("External governance identity changed")
        if manifest_hash(self.manifest) != self.execution_identity.manifest_hash:
            raise RuntimeError("External manifest identity changed")
        governed_capabilities = tuple(sorted(str(capability).strip().upper() for capability in record.capabilities or []))
        if governed_capabilities != self.execution_identity.capabilities:
            raise RuntimeError("External capability identity changed")
        if not self.governance_service.is_runtime_eligible(self.plugin_id, hospital_id=self.tenant_context.hospital_id):
            raise RuntimeError("External plugin is no longer runtime-eligible")
        if "NETWORK_ACCESS" in self.granted_capabilities:
            raise RuntimeError("External network capability has no approved isolation mechanism")
        inspection = PluginArtifactService().inspect(self.artifact_path)
        if inspection.sha256 != self.execution_identity.artifact_hash or record.artifact_hash != self.execution_identity.artifact_hash or record.plugin_version != self.execution_identity.plugin_version:
            raise RuntimeError("External plugin artifact identity changed")
