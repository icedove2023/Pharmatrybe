from __future__ import annotations

import csv
import json
import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

import pytest

from app.plugins.base.plugin import BasePlugin
from app.plugins.base.prediction_plugin import DeploymentType, PredictionPlugin, PredictionRequest, PredictionResult
from app.plugins.prediction.soar.explainability_adapter import ExplainabilityAdapter


class FakeExplainAdapter(ExplainabilityAdapter):
    def explain(self, execution):
        return PredictionResult(
            predicted_class=execution.predicted_class,
            probabilities={"predicted_class": float(execution.probability or 0.0)},
            confidence=float(execution.probability or 0.0),
            model_name=execution.deployment_id,
            model_version="0.1.0",
            execution_time_ms=execution.execution_time_ms,
            metadata={"explanation": "stub"},
        )
from app.plugins.contracts.plugin_manifest import PluginManifest
from app.plugins.discovery.plugin_loader import PluginLoader
from app.plugins.discovery.plugin_manifest_reader import PluginManifestReader
from app.plugins.discovery.plugin_validator import PluginValidator
from app.plugins.manager.plugin_manager import PluginManager
from app.plugins.manager.plugin_registry import PluginRegistry
from app.plugins.prediction.soar.deployment_registry import DeploymentRegistry
from app.plugins.prediction.soar.deployment_scanner import DeploymentScanner
from app.plugins.prediction.soar.model_loader import ModelLoader
from app.plugins.prediction.soar.prediction_engine import PredictionEngine
from app.plugins.prediction.soar.explainability_adapter import ExplainabilityAdapter
from app.plugins.prediction.soar.runtime_context import SOARRuntimeContext
from app.plugins.prediction.soar.soar_prediction_plugin import SOARPredictionPlugin
from app.plugins.base.plugin import PluginType


def test_plugin_manifest_reader_loads_manifest_from_soar_package() -> None:
    manifest_path = Path(__file__).resolve().parents[1] / "app" / "plugins" / "prediction" / "soar" / "plugin.yaml"
    manifest = PluginManifestReader.load_from_file(manifest_path)

    assert isinstance(manifest, PluginManifest)
    assert manifest.plugin_id == "soar"
    assert manifest.entrypoint_module == "soar_prediction_plugin"
    assert manifest.entrypoint_class == "SOARPredictionPlugin"
    assert manifest.plugin_type == PluginType.PREDICTION
    assert manifest.deployment_type == DeploymentType.ARTIFACT


def test_plugin_manifest_reader_rejects_manifest_with_missing_fields(tmp_path: Path) -> None:
    manifest_path = tmp_path / "plugin.yaml"
    manifest_path.write_text("plugin_id: test_plugin\nplugin_name: Test Plugin\n")

    validator = PluginValidator()
    result = validator.validate_manifest_file(manifest_path, platform_version="1.0.0", sdk_version="1.0.0")

    assert not result.is_valid
    assert any("field required" in error or "plugin_version" in error for error in result.errors)
    assert any("minimum_platform_version" in error for error in result.errors)
    assert any("sdk_version" in error for error in result.errors)


def test_plugin_loader_discovers_nested_plugin_manifests() -> None:
    plugin_root = Path(__file__).resolve().parents[1] / "app" / "plugins"
    loader = PluginLoader(plugin_root, PluginRegistry(), PluginValidator(), platform_version="1.0.0", sdk_version="1.0.0")
    discovered = loader.discover_plugin_paths()

    assert any(str(path).endswith("plugins\\prediction\\soar") for path in discovered)
    assert any((path / "plugin.yaml").exists() for path in discovered)


def test_plugin_loader_rejects_invalid_manifest(tmp_path: Path) -> None:
    plugin_root = tmp_path / "plugins"
    plugin_dir = plugin_root / "invalid_plugin"
    plugin_dir.mkdir(parents=True)
    (plugin_dir / "plugin.yaml").write_text("plugin_id: bad\nplugin_name: Bad Plugin\n", encoding="utf-8")
    (plugin_dir / "bad_plugin.py").write_text("from app.plugins.base.plugin import BasePlugin\n\nclass BadPlugin(BasePlugin):\n    def plugin_id(self): return 'bad'\n", encoding="utf-8")

    loader = PluginLoader(plugin_root, PluginRegistry(), PluginValidator(), platform_version="1.0.0", sdk_version="1.0.0")
    results = loader.load_all_plugins()

    assert len(results) == 1
    assert not results[0].success
    assert results[0].errors


def test_plugin_registry_registers_and_retrieves_plugin() -> None:
    registry = PluginRegistry()

    @dataclass
    class DummyPlugin(PredictionPlugin):
        def plugin_id(self) -> str: return "dummy"
        def plugin_name(self) -> str: return "Dummy"
        def plugin_version(self) -> str: return "0.0.1"
        def plugin_type(self): return "prediction"
        def plugin_description(self) -> str: return "Dummy plugin"
        def author(self) -> str: return "Test"
        def capabilities(self) -> List[str]: return []
        def dependencies(self) -> List[str]: return []
        def deployment_type(self) -> DeploymentType: return DeploymentType.ARTIFACT
        def initialize(self) -> None: pass
        def shutdown(self) -> None: pass
        def configure(self, configuration: Dict[str, Any]) -> None: pass
        def validate(self) -> bool: return True
        def metadata(self): return PluginManifest(plugin_id="dummy", plugin_name="Dummy", plugin_version="0.0.1", plugin_type="prediction", deployment_type=DeploymentType.ARTIFACT, description="Dummy plugin", author="Test", entrypoint_module="dummy", entrypoint_class="DummyPlugin")
        def health(self): return None
        def load(self) -> None: pass
        def unload(self) -> None: pass
        def predict(self, request: PredictionRequest) -> PredictionResult: raise NotImplementedError
        def supports(self, request: PredictionRequest) -> bool: return False
        def input_schema(self) -> Dict[str, Any]: return {}
        def output_schema(self) -> Dict[str, Any]: return {}

    manifest = PluginManifest(
        plugin_id="dummy",
        plugin_name="Dummy Plugin",
        plugin_version="0.0.1",
        plugin_type="prediction",
        deployment_type=DeploymentType.ARTIFACT,
        description="Dummy plugin",
        author="Test",
        entrypoint_module="dummy_plugin",
        entrypoint_class="DummyPlugin",
    )

    plugin = DummyPlugin()
    registry.register_plugin(manifest, plugin)

    assert registry.get_plugin("dummy") is plugin
    assert registry.get_manifest("dummy") is manifest
    assert registry.get_metadata("dummy").plugin_id == "dummy"
    with pytest.raises(ValueError):
        registry.register_plugin(manifest, plugin)


def test_plugin_manager_loads_soar_plugin_via_manifest() -> None:
    plugin_root = Path(__file__).resolve().parents[1] / "app" / "plugins"
    manager = PluginManager(plugin_root, platform_version="1.0.0", sdk_version="1.0.0")
    load_results = manager.load_all_plugins()

    assert any(result.success for result in load_results)
    plugin = manager.retrieve_plugin("soar")
    assert plugin is not None
    assert plugin.plugin_id == "soar"
    assert isinstance(plugin, SOARPredictionPlugin)
    assert manager.retrieve_plugin_metadata("soar").plugin_id == "soar"
    assert manager.retrieve_plugin_health("soar") is not None


class DummyModel:
    feature_names_in_ = ["organism", "antimicrobial"]
    classes_ = ["S", "I", "R"]

    def predict(self, X):
        return [0]

    def predict_proba(self, X):
        return [[0.1, 0.2, 0.7]]


class DummyEncoder:
    def inverse_transform(self, values):
        return ["R"]


def test_soar_runtime_context_initializes_and_lazy_loads_models(tmp_path: Path, monkeypatch: Any) -> None:
    deployments_root = tmp_path / "deployments"
    deployment = deployments_root / "S__A"
    deployment.mkdir(parents=True)

    with open(deployment / "final_model.pkl", "wb") as file_obj:
        pickle.dump(DummyModel(), file_obj)
    with open(deployment / "label_encoder.pkl", "wb") as file_obj:
        pickle.dump(DummyEncoder(), file_obj)
    (deployment / "optimal_threshold.json").write_text(json.dumps({"threshold": 0.5}), encoding="utf-8")
    (deployment / "evaluation_metrics.csv").write_text("metric,value\naccuracy,0.99\n", encoding="utf-8")

    plugin = SOARPredictionPlugin()
    plugin.configure({"deployments_root": str(deployments_root)})

    loaded_count = {"count": 0}

    original_load = ModelLoader.load

    def counting_load(self, deployment_info):
        loaded_count["count"] += 1
        return original_load(self, deployment_info)

    monkeypatch.setattr(ModelLoader, "load", counting_load)

    fake_explain_adapter_called = {"called": False}

    class FakeExplainAdapter(ExplainabilityAdapter):
        def explain(self, execution):
            fake_explain_adapter_called["called"] = True
            return PredictionResult(
                predicted_class=execution.predicted_class,
                probabilities={"predicted_class": float(execution.probability or 0.0)},
                confidence=float(execution.probability or 0.0),
                model_name=execution.deployment_id,
                model_version="0.1.0",
                execution_time_ms=execution.execution_time_ms,
                metadata={"explanation": "stub"},
            )

    plugin._explainability_adapter = FakeExplainAdapter()
    plugin.initialize()

    assert plugin._runtime_context is not None
    assert plugin._runtime_context.runtime_metadata.plugin_id == "soar"
    assert not plugin._model_loader.is_loaded("S__A")

    request = PredictionRequest(payload={"organism": "S", "antimicrobial": "A"})
    result = plugin.predict(request)

    assert result.predicted_class == "R"
    assert fake_explain_adapter_called["called"]
    assert loaded_count["count"] == 1
    assert plugin._model_loader.is_loaded("S__A")

    plugin.predict(request)
    assert loaded_count["count"] == 1


def test_plugin_shutdown_unloads_models_and_keeps_registry(tmp_path: Path) -> None:
    deployments_root = tmp_path / "deployments"
    deployment = deployments_root / "S__A"
    deployment.mkdir(parents=True)
    (deployment / "final_model.pkl").write_bytes(pickle.dumps(object()))
    (deployment / "label_encoder.pkl").write_bytes(pickle.dumps(object()))
    (deployment / "optimal_threshold.json").write_text("{}", encoding="utf-8")
    (deployment / "evaluation_metrics.csv").write_text("metric,value\n", encoding="utf-8")

    plugin = SOARPredictionPlugin()
    plugin.configure({"deployments_root": str(deployments_root)})
    plugin._explainability_adapter = FakeExplainAdapter()  # type: ignore[name-defined]
    plugin.initialize()

    plugin.shutdown()
    assert plugin._runtime_context is None or not plugin._runtime_context._initialized
    assert not plugin._model_loader.loaded_models()
