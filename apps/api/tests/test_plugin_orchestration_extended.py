from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.plugins.base.knowledge_plugin import KnowledgePlugin
from app.plugins.base.plugin import PluginHealth, PluginMetadata, PluginType
from app.plugins.base.prediction_plugin import DeploymentType, PredictionPlugin, PredictionRequest, PredictionResult
from app.plugins.manager.plugin_registry import PluginRegistry
from app.plugins.manager.plugin_routing_policy import PluginRoutingPolicy
from app.plugins.manager.workflow_manager import ClinicalDecisionContext, ClinicalDecisionRequest, ExecutionMode, WorkflowManager


class DummyPredictionPlugin(PredictionPlugin):
    def __init__(self, plugin_id: str, plugin_name: str = "Dummy Prediction") -> None:
        self._plugin_id = plugin_id
        self._plugin_name = plugin_name

    @property
    def plugin_id(self) -> str:
        return self._plugin_id

    @property
    def plugin_name(self) -> str:
        return self._plugin_name

    @property
    def plugin_version(self) -> str:
        return "0.1.0"

    @property
    def plugin_type(self) -> PluginType:
        return PluginType.PREDICTION

    @property
    def plugin_description(self) -> str:
        return "dummy"

    @property
    def author(self) -> str:
        return "test"

    @property
    def capabilities(self) -> List[str]:
        return ["respiratory_prediction"]

    @property
    def dependencies(self) -> List[str]:
        return []

    @property
    def deployment_type(self) -> DeploymentType:
        return DeploymentType.ARTIFACT

    def initialize(self) -> None:
        pass

    def shutdown(self) -> None:
        pass

    def configure(self, configuration: Dict[str, Any]) -> None:
        pass

    def validate(self) -> bool:
        return True

    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id=self.plugin_id,
            plugin_name=self.plugin_name,
            plugin_version=self.plugin_version,
            plugin_type=self.plugin_type,
            description=self.plugin_description,
            author=self.author,
            capabilities=self.capabilities,
            dependencies=self.dependencies,
        )

    def health(self) -> PluginHealth:
        return PluginHealth(healthy=True, status="ok", message="healthy", timestamp=None)  # type: ignore[arg-type]

    def load(self) -> None:
        pass

    def unload(self) -> None:
        pass

    def predict(self, request: PredictionRequest) -> PredictionResult:
        return PredictionResult(
            predicted_class="R",
            probabilities={"S": 0.1, "R": 0.9},
            confidence=0.9,
            model_name=self.plugin_name,
            model_version=self.plugin_version,
            execution_time_ms=1.0,
            metadata={"source": self.plugin_id},
        )

    def supports(self, request: PredictionRequest) -> bool:
        return True

    def input_schema(self) -> Dict[str, Any]:
        return {}

    def output_schema(self) -> Dict[str, Any]:
        return {}


class DummyKnowledgePlugin(KnowledgePlugin):
    def __init__(self, plugin_id: str, plugin_name: str = "Dummy Knowledge") -> None:
        self._plugin_id = plugin_id
        self._plugin_name = plugin_name

    @property
    def plugin_id(self) -> str:
        return self._plugin_id

    @property
    def plugin_name(self) -> str:
        return self._plugin_name

    @property
    def plugin_version(self) -> str:
        return "0.1.0"

    @property
    def plugin_type(self) -> PluginType:
        return PluginType.KNOWLEDGE

    @property
    def plugin_description(self) -> str:
        return "dummy"

    @property
    def author(self) -> str:
        return "test"

    @property
    def capabilities(self) -> List[str]:
        return ["guideline"]

    @property
    def dependencies(self) -> List[str]:
        return []

    def initialize(self) -> None:
        pass

    def shutdown(self) -> None:
        pass

    def configure(self, configuration: Dict[str, Any]) -> None:
        pass

    def validate(self) -> bool:
        return True

    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id=self.plugin_id,
            plugin_name=self.plugin_name,
            plugin_version=self.plugin_version,
            plugin_type=self.plugin_type,
            description=self.plugin_description,
            author=self.author,
            capabilities=self.capabilities,
            dependencies=self.dependencies,
        )

    def health(self) -> PluginHealth:
        return PluginHealth(healthy=True, status="ok", message="healthy", timestamp=None)  # type: ignore[arg-type]

    def connect(self) -> None:
        pass

    def disconnect(self) -> None:
        pass

    def search(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        return [{"query": query, "source": self.plugin_id}]

    def query(self, criteria: Dict[str, Any]) -> Dict[str, Any]:
        return {"criteria": criteria, "source": self.plugin_id}

    def supported_domains(self) -> List[str]:
        return ["respiratory"]

    def knowledge_version(self) -> str:
        return "0.1.0"


def _register_plugins(registry: PluginRegistry, prediction_ids: Optional[List[str]] = None, knowledge_ids: Optional[List[str]] = None) -> None:
    prediction_ids = prediction_ids or ["SOAR", "ARMD"]
    knowledge_ids = knowledge_ids or ["WHO", "NICE", "Hospital Guideline"]

    for plugin_id in prediction_ids:
        registry.register_plugin(
            type("Manifest", (), {"plugin_id": plugin_id, "plugin_type": PluginType.PREDICTION, "supported_domains": ["respiratory"], "capabilities": ["respiratory_prediction"], "enabled": True})(),
            DummyPredictionPlugin(plugin_id, plugin_id),
        )

    for plugin_id in knowledge_ids:
        registry.register_plugin(
            type("Manifest", (), {"plugin_id": plugin_id, "plugin_type": PluginType.KNOWLEDGE, "supported_domains": ["respiratory"], "capabilities": ["guideline"], "enabled": True})(),
            DummyKnowledgePlugin(plugin_id, plugin_id),
        )


def test_auto_routing_selects_prediction_and_knowledge_plugins() -> None:
    registry = PluginRegistry()
    _register_plugins(registry)
    request = ClinicalDecisionRequest(
        patient_id="p-1",
        payload={"domain": "respiratory"},
        context={"domain": "respiratory"},
        execution_mode=ExecutionMode.AUTO,
    )

    manager = WorkflowManager(registry)
    selected = manager._select_plugins(request)

    assert any(plugin.plugin_id == "SOAR" for plugin in selected)
    assert any(plugin.plugin_type == PluginType.KNOWLEDGE for plugin in selected)


def test_prediction_only_mode_skips_knowledge() -> None:
    registry = PluginRegistry()
    _register_plugins(registry)
    request = ClinicalDecisionRequest(
        patient_id="p-2",
        payload={"domain": "respiratory"},
        execution_mode=ExecutionMode.PREDICTION_ONLY,
    )

    manager = WorkflowManager(registry)
    selected = manager._select_plugins(request)

    assert all(plugin.plugin_type == PluginType.PREDICTION for plugin in selected)


def test_knowledge_only_mode_skips_prediction() -> None:
    registry = PluginRegistry()
    _register_plugins(registry)
    request = ClinicalDecisionRequest(
        patient_id="p-3",
        payload={"domain": "respiratory"},
        execution_mode=ExecutionMode.KNOWLEDGE_ONLY,
    )

    manager = WorkflowManager(registry)
    selected = manager._select_plugins(request)

    assert all(plugin.plugin_type == PluginType.KNOWLEDGE for plugin in selected)


def test_hybrid_mode_uses_explicit_plugin_selection() -> None:
    registry = PluginRegistry()
    _register_plugins(registry)
    request = ClinicalDecisionRequest(
        patient_id="p-4",
        payload={"domain": "respiratory"},
        execution_mode=ExecutionMode.HYBRID,
        prediction_plugins=["SOAR"],
        knowledge_plugins=["WHO"],
    )

    manager = WorkflowManager(registry)
    selected = manager._select_plugins(request)

    assert {plugin.plugin_id for plugin in selected} == {"SOAR", "WHO"}


def test_manual_plugin_selection_executes_exactly_requested_ids() -> None:
    registry = PluginRegistry()
    _register_plugins(registry)
    request = ClinicalDecisionRequest(
        patient_id="p-5",
        payload={"domain": "respiratory"},
        execution_mode=ExecutionMode.USER_SELECTED,
        plugin_ids=["SOAR", "WHO"],
    )

    manager = WorkflowManager(registry)
    selected = manager._select_plugins(request)

    assert [plugin.plugin_id for plugin in selected] == ["SOAR", "WHO"]


def test_routing_policy_routes_by_domain_without_clinical_logic() -> None:
    registry = PluginRegistry()
    _register_plugins(registry)
    request = ClinicalDecisionRequest(
        patient_id="p-6",
        payload={"infection_type": "respiratory"},
        execution_mode=ExecutionMode.AUTO,
    )

    policy = PluginRoutingPolicy()
    selected = policy.route(request, registry)
    assert any(plugin.plugin_id == "SOAR" for plugin in selected)
    assert any(plugin.plugin_type == PluginType.KNOWLEDGE for plugin in selected)


def test_missing_plugin_is_handled_gracefully() -> None:
    registry = PluginRegistry()
    _register_plugins(registry)
    request = ClinicalDecisionRequest(
        patient_id="p-7",
        payload={"domain": "respiratory"},
        execution_mode=ExecutionMode.USER_SELECTED,
        plugin_ids=["DOES_NOT_EXIST"],
    )

    manager = WorkflowManager(registry)
    selected = manager._select_plugins(request)

    assert selected == []


def test_plugin_failure_isolation_keeps_other_plugins() -> None:
    registry = PluginRegistry()
    _register_plugins(registry, prediction_ids=["SOAR"], knowledge_ids=["WHO"])

    class FailingPlugin(DummyPredictionPlugin):
        def predict(self, request: PredictionRequest) -> PredictionResult:
            raise RuntimeError("plugin failure")

    registry.register_plugin(
        type("Manifest", (), {"plugin_id": "BROKEN", "plugin_type": PluginType.PREDICTION, "supported_domains": ["respiratory"], "capabilities": ["respiratory_prediction"], "enabled": True})(),
        FailingPlugin("BROKEN"),
    )

    request = ClinicalDecisionRequest(
        patient_id="p-8",
        payload={"domain": "respiratory"},
        execution_mode=ExecutionMode.AUTO,
    )

    manager = WorkflowManager(registry)
    results = manager.execute(request)

    assert any(result.success for result in results)
    assert any(result.plugin_id == "BROKEN" and not result.success for result in results)


def test_clinical_decision_context_contains_only_orchestration_data() -> None:
    request = ClinicalDecisionRequest(
        patient_id="p-9",
        payload={"domain": "respiratory"},
        execution_mode=ExecutionMode.AUTO,
    )

    context = ClinicalDecisionContext(
        patient_id=request.patient_id,
        prediction_outputs=[{"plugin_id": "SOAR", "value": {"confidence": 0.9}}],
        knowledge_outputs=[{"plugin_id": "WHO", "value": {"summary": "guideline"}}],
        plugin_metadata=[{"plugin_id": "SOAR", "plugin_type": "prediction"}],
        execution_metadata={"execution_mode": request.execution_mode.value},
    )

    assert context.patient_id == "p-9"
    assert context.prediction_outputs
    assert context.knowledge_outputs
    assert "recommendation" not in context.execution_metadata


def test_plugin_discovery_uses_registry_only() -> None:
    registry = PluginRegistry()
    _register_plugins(registry)
    plugins = registry.list_plugins()

    assert len(plugins) >= 5
    assert any(getattr(plugin, "plugin_id", None) == "SOAR" for plugin in plugins)
    assert any(getattr(plugin, "plugin_id", None) == "WHO" for plugin in plugins)
