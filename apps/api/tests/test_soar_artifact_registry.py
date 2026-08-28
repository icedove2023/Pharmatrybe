from __future__ import annotations

import csv
import json
import pickle
from pathlib import Path
from typing import Any

from app.plugins.prediction.soar.artifact_registry import ArtifactRegistry
from app.plugins.prediction.soar.deployment_scanner import DeploymentInfo, DeploymentScanner
from app.plugins.prediction.soar.model_loader import LoadedModel, ModelLoader


def test_artifact_registry_discovers_and_classifies(tmp_path: Path) -> None:
    deployment_path = tmp_path / "deploymentA"
    deployment_path.mkdir()

    (deployment_path / "final_model.pkl").write_bytes(pickle.dumps({"value": 1}))
    (deployment_path / "label_encoder.pkl").write_bytes(pickle.dumps(["S", "I", "R"]))
    (deployment_path / "config.yaml").write_text("threshold: 0.5\n", encoding="utf-8")
    (deployment_path / "feature_dictionary.json").write_text(json.dumps({"features": ["a", "b"]}), encoding="utf-8")
    (deployment_path / "evaluation_metrics.csv").write_text("metric,value\naccuracy,0.92\n", encoding="utf-8")

    registry = ArtifactRegistry.from_deployment_path(deployment_path)

    assert registry.find_first("MODEL") is not None
    assert registry.find_first("MODEL").filename == "final_model.pkl"
    assert registry.find_first("ENCODER").filename == "label_encoder.pkl"
    assert registry.find_first("CONFIG").filename == "config.yaml"
    assert registry.find_by_filename("feature_dictionary.json").category == "METADATA"
    assert registry.find_first("METRICS").filename == "evaluation_metrics.csv"


def test_model_loader_loads_lazy_artifacts(tmp_path: Path) -> None:
    deployment_path = tmp_path / "deploymentB"
    deployment_path.mkdir()
    model_payload = {"a": 1}
    encoder_payload = ["S", "I", "R"]
    threshold_payload = {"threshold": 0.55}

    (deployment_path / "final_model.pkl").write_bytes(pickle.dumps(model_payload))
    (deployment_path / "label_encoder.pkl").write_bytes(pickle.dumps(encoder_payload))
    (deployment_path / "optimal_threshold.json").write_text(json.dumps(threshold_payload), encoding="utf-8")
    (deployment_path / "evaluation_metrics.csv").write_text("metric,value\naccuracy,0.95\n", encoding="utf-8")

    artifact_registry = ArtifactRegistry.from_deployment_path(deployment_path)
    deployment_info = DeploymentInfo(
        deployment_id="deploymentB",
        organism=None,
        antimicrobial=None,
        deployment_path=deployment_path,
        artifact_registry=artifact_registry,
        status="valid",
    )

    loader = ModelLoader()
    loaded_model = loader.load(deployment_info)

    assert loader.is_loaded("deploymentB")
    assert loaded_model.artifact_registry is artifact_registry
    assert loader.load_model("deploymentB") == model_payload
    assert loader.load_encoder("deploymentB") == encoder_payload
    assert loader.load_threshold("deploymentB") == threshold_payload
    metrics_artifact = loader.get_artifact("deploymentB", "METRICS")
    assert metrics_artifact is not None
    assert loader.load_artifact(metrics_artifact) == [{"metric": "accuracy", "value": "0.95"}]


def test_deployment_scanner_discovers_deployment(tmp_path: Path) -> None:
    deployment_path = tmp_path / "S__A"
    deployment_path.mkdir()
    (deployment_path / "final_model.pkl").write_bytes(pickle.dumps({"value": 2}))

    scanner = DeploymentScanner(deployments_root=tmp_path)
    deployments = scanner.scan()

    assert len(deployments) == 1
    assert deployments[0].deployment_id == "S__A"
    assert deployments[0].organism == "S"
    assert deployments[0].antimicrobial == "A"
    assert deployments[0].status == "valid"
