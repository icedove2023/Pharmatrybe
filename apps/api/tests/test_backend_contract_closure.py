from __future__ import annotations

import json

import pytest

from app.api.v1.pipeline import PipelineExecutionRequest
from app.core.exceptions import map_exception_to_code
from app.plugins.adapters import AdapterValidationError, adapt_prediction_request
from app.plugins.prediction.soar.soar_prediction_plugin import DeploymentSelectionError


def test_canonical_pipeline_request_preserves_explicit_routing_context() -> None:
    request = PipelineExecutionRequest(
        request_id="request-1",
        patient_id="patient-1",
        case_id="case-1",
        routing_context={"deployment_id": "Ceftriaxone_Haemophilus_influenzae"},
        input_payload={"Age": 60},
    )

    assert request.request_id == "request-1"
    assert request.routing_context["deployment_id"] == "Ceftriaxone_Haemophilus_influenzae"
    assert request.input_payload == {"Age": 60}


def test_soar_adapter_requires_explicit_deployment_id() -> None:
    with pytest.raises(AdapterValidationError, match="deployment_id"):
        adapt_prediction_request("soar", {"Age": 60}, None)


def test_soar_adapter_preserves_payload_and_validates_routing_context() -> None:
    payload = {"Age": 60, "YearCollected": 2025}
    request = adapt_prediction_request(
        "soar",
        payload,
        {"deployment_id": "Ceftriaxone_Haemophilus_influenzae", "ignored": "value"},
    )

    assert request.payload is payload
    assert request.context == {"deployment_id": "Ceftriaxone_Haemophilus_influenzae"}


def test_typed_failures_have_stable_public_error_codes() -> None:
    assert map_exception_to_code(DeploymentSelectionError("missing")) == "SOAR_DEPLOYMENT_SELECTION_ERROR"
    assert map_exception_to_code(AdapterValidationError("invalid")) == "PLUGIN_INPUT_VALIDATION_ERROR"


def test_contract_artifacts_are_present() -> None:
    from pathlib import Path

    root = Path(__file__).resolve().parents[3]
    assert (root / "docs/contracts/BACKEND_CONTRACT_DECISION_REGISTER.md").exists()
    assert (root / "docs/contracts/SOAR_DEPLOYMENT_SELECTION_CONTRACT_v1.0.0.md").exists()
    assert (root / "docs/contracts/CLINICAL_ADAPTATION_BOUNDARY_v1.0.0.md").exists()
