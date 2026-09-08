from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.plugins.base.knowledge_plugin import KnowledgePlugin
from app.plugins.base.plugin import BasePlugin, PluginHealth, PluginMetadata, PluginType
from app.plugins.base.prediction_plugin import DeploymentType, PredictionPlugin, PredictionRequest, PredictionResult
from app.plugins.manager.plugin_registry import PluginRegistry
from app.plugins.manager.workflow_manager import ExecutionMode, ClinicalDecisionRequest, PluginExecutionResult, WorkflowManager


class DummyPredictionPlugin(PredictionPlugin):
    def __init__(self, plugin_id: str = "dummy_prediction") -> None:
        self._plugin_id = plugin_id
        self.received_request: Optional[PredictionRequest] = None

    @property
    def plugin_id(self) -> str:
        return self._plugin_id

    @property
    def plugin_name(self) -> str:
        return "Dummy Prediction"

    @property
    def plugin_version(self) -> str:
        return "0.1.0"

    @property
    def plugin_type(self) -> PluginType:
        return PluginType.PREDICTION

    @property
    def plugin_description(self) -> str:
        return "Dummy prediction plugin"

    @property
    def author(self) -> str:
        return "Test Author"

    @property
    def capabilities(self) -> List[str]:
        return ["prediction"]

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
        self.received_request = request
        return PredictionResult(
            predicted_class="R",
            probabilities={"S": 0.1, "I": 0.2, "R": 0.7},
            confidence=0.7,
            model_name=self.plugin_name,
            model_version=self.plugin_version,
            execution_time_ms=10.0,
            metadata={"plugin_id": self.plugin_id},
        )

    def supports(self, request: PredictionRequest) -> bool:
        return True

    def input_schema(self) -> Dict[str, Any]:
        return {}

    def output_schema(self) -> Dict[str, Any]:
        return {}


class DummyKnowledgePlugin(KnowledgePlugin):
    def __init__(self, plugin_id: str = "dummy_knowledge") -> None:
        self._plugin_id = plugin_id

    @property
    def plugin_id(self) -> str:
        return self._plugin_id

    @property
    def plugin_name(self) -> str:
        return "Dummy Knowledge"

    @property
    def plugin_version(self) -> str:
        return "0.1.0"

    @property
    def plugin_type(self) -> PluginType:
        return PluginType.KNOWLEDGE

    @property
    def plugin_description(self) -> str:
        return "Dummy knowledge plugin"

    @property
    def author(self) -> str:
        return "Test Author"

    @property
    def capabilities(self) -> List[str]:
        return ["guidelines"]

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
        return [{"source": "dummy", "summary": "Use narrow therapy"}]

    def query(self, criteria: Dict[str, Any]) -> Dict[str, Any]:
        return {"source": "dummy", "summary": "Use narrow therapy"}

    def supported_domains(self) -> List[str]:
        return ["antimicrobial"]

    def knowledge_version(self) -> str:
        return "0.1.0"


def test_workflow_manager_executes_selected_plugins() -> None:
    registry = PluginRegistry()
    prediction_plugin = DummyPredictionPlugin()
    knowledge_plugin = DummyKnowledgePlugin()

    registry.register_plugin(
        type("Manifest", (), {"plugin_id": prediction_plugin.plugin_id, "plugin_type": PluginType.PREDICTION})(),
        prediction_plugin,
    )
    registry.register_plugin(
        type("Manifest", (), {"plugin_id": knowledge_plugin.plugin_id, "plugin_type": PluginType.KNOWLEDGE})(),
        knowledge_plugin,
    )

    request = ClinicalDecisionRequest(
        patient_id="patient-1",
        execution_mode=ExecutionMode.USER_SELECTED,
        plugin_ids=[prediction_plugin.plugin_id],
        payload={"organism": "Acinetobacter baumannii"},
        context={"domain": "respiratory"},
    )

    workflow_manager = WorkflowManager(registry=registry)
    results = workflow_manager.execute(request)

    assert len(results) == 1
    assert results[0].plugin_id == prediction_plugin.plugin_id
    assert results[0].success is True
    assert isinstance(results[0].result, PredictionResult)


def test_workflow_manager_propagates_soar_payload_and_deployment_context() -> None:
    registry = PluginRegistry()
    prediction_plugin = DummyPredictionPlugin("soar")
    registry.register_plugin(
        type("Manifest", (), {"plugin_id": prediction_plugin.plugin_id, "plugin_type": PluginType.PREDICTION})(),
        prediction_plugin,
    )
    payload = {
        "Age": 60,
        "YearCollected": 2025,
        "Region": "region-a",
        "BodyLocation_Group": "respiratory",
        "Country": "country-a",
        "Beta_Lactamase_enc": 0,
    }
    context = {"deployment_id": "Ceftriaxone_Haemophilus_influenzae"}

    results = WorkflowManager(registry=registry).execute(ClinicalDecisionRequest(
        patient_id="patient-soar",
        execution_mode=ExecutionMode.USER_SELECTED,
        plugin_ids=["soar"],
        payload=payload,
        context=context,
    ))

    assert results[0].success is True
    assert prediction_plugin.received_request is not None
    assert prediction_plugin.received_request.payload is payload
    assert prediction_plugin.received_request.context == context


def test_workflow_manager_rejects_missing_soar_deployment_context() -> None:
    registry = PluginRegistry()
    prediction_plugin = DummyPredictionPlugin("soar")
    registry.register_plugin(
        type("Manifest", (), {"plugin_id": prediction_plugin.plugin_id, "plugin_type": PluginType.PREDICTION})(),
        prediction_plugin,
    )

    results = WorkflowManager(registry=registry).execute(ClinicalDecisionRequest(
        patient_id="patient-soar",
        execution_mode=ExecutionMode.USER_SELECTED,
        plugin_ids=["soar"],
        payload={"Age": 60},
    ))

    assert results[0].success is False
    assert "deployment_id" in (results[0].error or "")
    assert prediction_plugin.received_request is None


def test_workflow_manager_handles_graceful_degradation() -> None:
    registry = PluginRegistry()
    plugin = DummyPredictionPlugin("broken_prediction")
    registry.register_plugin(
        type("Manifest", (), {"plugin_id": plugin.plugin_id, "plugin_type": PluginType.PREDICTION})(),
        plugin,
    )

    workflow_manager = WorkflowManager(registry=registry)
    request = ClinicalDecisionRequest(
        patient_id="patient-2",
        execution_mode=ExecutionMode.AUTOMATIC,
        plugin_types=[PluginType.PREDICTION],
        payload={"organism": "Acinetobacter baumannii"},
    )

    results = workflow_manager.execute(request)
    assert results
    assert any(result.plugin_id == "broken_prediction" for result in results)
    assert all(result.success is True for result in results)
