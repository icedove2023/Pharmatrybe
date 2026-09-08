from __future__ import annotations

from pathlib import Path

import pytest

from app.plugins.base.prediction_plugin import PredictionRequest
from app.plugins.prediction.soar.deployment_registry import DeploymentRegistry
from app.plugins.prediction.soar.model_loader import ModelLoader
from app.plugins.prediction.soar.prediction_engine import PredictionEngine


SOAR_DEPLOYMENTS = (
    "Cefixime_Haemophilus_influenzae",
    "Cefotaxime_Haemophilus_influenzae",
    "Cefpodoxime_Haemophilus_influenzae",
    "Ceftibuten_Haemophilus_influenzae",
    "Ceftriaxone_Haemophilus_influenzae",
    "Doxycycline_Streptococcus_pneumoniae",
    "Levofloxacin_Haemophilus_influenzae",
    "Tetracycline_Haemophilus_influenzae",
    "Tetracycline_Streptococcus_pneumoniae",
    "Trimethoprim_Sulfa_Haemophilus_influenzae",
)


@pytest.mark.parametrize("deployment_id", SOAR_DEPLOYMENTS)
def test_active_soar_deployment_executes_real_model(deployment_id: str) -> None:
    """Execute each active SOAR artifact with explicitly labelled synthetic data."""
    root = Path(__file__).resolve().parents[3] / "deployments" / "SOAR_GSK" / "SOAR_GSK" / "deployment"
    registry = DeploymentRegistry(root)
    deployment = registry.get_by_id(deployment_id)

    assert deployment is not None
    assert deployment.status == "valid"
    assert deployment.deployment_id == deployment_id

    payload = {
        "Age": 47,
        "YearCollected": 2019,
        "Region": "Europe",
        "BodyLocation_Group": "Blood",
        "Country": "Italy",
    }
    if "Beta_Lactamase_enc" in deployment.feature_names:
        payload["Beta_Lactamase_enc"] = 1

    loaded_model = ModelLoader().load(deployment)
    execution = PredictionEngine().predict(
        loaded_model,
        PredictionRequest(
            payload=payload,
            context={"deployment_id": deployment_id, "test_classification": "SYNTHETIC_TEST_DATA"},
        ),
    )

    assert execution.deployment_id == deployment_id
    assert execution.predicted_class in {"S", "I", "R"}
    assert execution.probability is not None
    assert 0.0 <= execution.probability <= 1.0
    assert execution.threshold >= 0.0
    assert execution.metadata["feature_count"] == 1
    assert len(execution.processed_features.columns) == len(deployment.feature_names)


@pytest.mark.parametrize("encoded_status", [0, 1])
def test_active_soar_haemophilus_executes_both_beta_lactamase_statuses(encoded_status: int) -> None:
    """Verify both controlled beta-lactamase encodings reach real inference."""
    root = Path(__file__).resolve().parents[3] / "deployments" / "SOAR_GSK" / "SOAR_GSK" / "deployment"
    deployment_id = "Ceftriaxone_Haemophilus_influenzae"
    deployment = DeploymentRegistry(root).get_by_id(deployment_id)
    assert deployment is not None

    payload = {
        "Age": 47,
        "YearCollected": 2019,
        "Region": "Europe",
        "BodyLocation_Group": "Blood",
        "Country": "Italy",
        "Beta_Lactamase_enc": encoded_status,
    }
    execution = PredictionEngine().predict(
        ModelLoader().load(deployment),
        PredictionRequest(
            payload=payload,
            context={"deployment_id": deployment_id, "test_classification": "SYNTHETIC_TEST_DATA"},
        ),
    )

    assert execution.predicted_class in {"S", "I", "R"}
    assert execution.probability is not None