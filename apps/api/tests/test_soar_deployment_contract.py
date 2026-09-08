from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest
import jsonschema

from app.plugins.base.prediction_plugin import PredictionRequest
from app.plugins.prediction.soar.deployment_registry import DeploymentRegistry
from app.plugins.prediction.soar.deployment_scanner import DeploymentScanner
from app.plugins.prediction.soar.prediction_engine import PredictionEngine, PredictionError
from app.plugins.prediction.soar.soar_prediction_plugin import DeploymentSelectionError, SOARPredictionPlugin


ROOT = Path(__file__).resolve().parents[3]
SOAR_ROOT = ROOT / "deployments" / "SOAR_GSK"


def test_inventory_contains_only_artifact_backed_deployments() -> None:
    deployments = DeploymentScanner(SOAR_ROOT).scan()
    assert len(deployments) == 10
    assert all(deployment.feature_names for deployment in deployments)
    assert all(deployment.organism and deployment.antimicrobial for deployment in deployments)
    assert {len(deployment.feature_names) for deployment in deployments} == {5, 6}


def test_runtime_artifact_root_uses_adjacent_authoritative_metadata() -> None:
    runtime_root = SOAR_ROOT / "SOAR_GSK" / "deployment"
    deployments = DeploymentScanner(runtime_root).scan()

    assert len(deployments) == 10
    assert all(deployment.status == "valid" for deployment in deployments)
    trimethoprim = next(
        deployment for deployment in deployments
        if deployment.deployment_id == "Trimethoprim_Sulfa_Haemophilus_influenzae"
    )
    assert trimethoprim.organism == "Haemophilus influenzae"
    assert trimethoprim.antimicrobial == "Trimethoprim_Sulfa"


def test_identity_comes_from_deployment_metadata() -> None:
    deployment = DeploymentScanner(SOAR_ROOT).scan()[0]
    assert deployment.organism in {"Haemophilus influenzae", "Streptococcus pneumoniae"}
    assert deployment.antimicrobial
    assert "_" not in deployment.organism


def test_registry_identity_matches_authoritative_artifact_metadata() -> None:
    registry = DeploymentRegistry(SOAR_ROOT)
    deployment = registry.get_by_id("Trimethoprim_Sulfa_Haemophilus_influenzae")

    assert deployment is not None
    assert deployment.antimicrobial == "Trimethoprim_Sulfa"
    assert deployment.organism == "Haemophilus influenzae"
    assert deployment.deployment_id == deployment.deployment_path.name


def test_selection_requires_explicit_deployment_id() -> None:
    plugin = SOARPredictionPlugin(deployment_registry=DeploymentRegistry(SOAR_ROOT))
    plugin._runtime_context = SimpleNamespace(deployment_registry=plugin._deployment_registry)
    with pytest.raises(DeploymentSelectionError, match="explicit context.deployment_id"):
        plugin._select_deployment(PredictionRequest(payload={"Age": 60}))


def test_selection_by_deployment_id_is_deterministic() -> None:
    registry = DeploymentRegistry(SOAR_ROOT)
    registry.initialize()
    expected = registry.get_all()[0]
    plugin = SOARPredictionPlugin(deployment_registry=registry)
    plugin._runtime_context = SimpleNamespace(deployment_registry=registry)
    selected = plugin._select_deployment(PredictionRequest(payload={}, context={"deployment_id": expected.deployment_id}))
    assert selected.deployment_id == expected.deployment_id


def test_unknown_deployment_fails_without_fallback() -> None:
    registry = DeploymentRegistry(SOAR_ROOT)
    registry.initialize()
    plugin = SOARPredictionPlugin(deployment_registry=registry)
    plugin._runtime_context = SimpleNamespace(deployment_registry=registry)
    with pytest.raises(DeploymentSelectionError, match="not available"):
        plugin._select_deployment(PredictionRequest(payload={}, context={"deployment_id": "missing"}))


def test_schema_exposes_distinct_deployment_variants() -> None:
    schema = SOARPredictionPlugin().input_schema()
    jsonschema.Draft202012Validator.check_schema(schema)
    assert schema["x-deployment-selection"]["frontend_visible"] is False
    assert schema["x-ui-inputs"] == []
    assert len(schema["anyOf"]) == 2
    jsonschema.Draft202012Validator(schema).validate({"Age": 1, "YearCollected": 2025, "Region": "r", "BodyLocation_Group": "b", "Country": "c"})
    jsonschema.Draft202012Validator(schema).validate({"Age": 1, "YearCollected": 2025, "Region": "r", "BodyLocation_Group": "b", "Country": "c", "Beta_Lactamase_enc": 0})


def test_prediction_engine_enforces_real_artifact_features() -> None:
    model = SimpleNamespace(feature_names_in_=["Age", "Country"])
    loaded = SimpleNamespace(model=model)
    with pytest.raises(PredictionError, match="Missing required feature fields"):
        PredictionEngine()._preprocess(loaded, PredictionRequest(payload={"Age": 60}))
