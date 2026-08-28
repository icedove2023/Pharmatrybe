from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.schemas.clinical_case import (
    Acquisition,
    ClinicalCaseRequest,
    ClinicalCaseDemographics,
    ClinicalCasePresentation,
    ResistanceStatus,
    Severity,
    Sex,
)


def test_valid_clinical_case_request(sample_clinical_case_payload: dict[str, Any]):
    model = ClinicalCaseRequest.model_validate(sample_clinical_case_payload)

    assert model.request_id
    assert model.presentation.severity == Severity.MODERATE
    assert model.demographics.sex == Sex.FEMALE
    assert model.resistance_status == ResistanceStatus.NONE


def test_missing_required_fields_rejected():
    payload = {"request_id": str(uuid4())}

    with pytest.raises(ValidationError):
        ClinicalCaseRequest.model_validate(payload)


def test_enum_validation_rejected(sample_clinical_case_payload: dict[str, Any]):
    payload = sample_clinical_case_payload.copy()
    payload["demographics"] = payload["demographics"].copy()
    payload["presentation"] = payload["presentation"].copy()
    payload["demographics"]["sex"] = "invalid"
    payload["presentation"]["severity"] = "wrong"
    payload["presentation"]["acquisition"] = "unknown"
    payload["resistance_status"] = "broken"

    with pytest.raises(ValidationError):
        ClinicalCaseRequest.model_validate(payload)


def test_age_validation_rejected(sample_clinical_case_payload: dict[str, Any]):
    payload = sample_clinical_case_payload.copy()
    payload["demographics"] = payload["demographics"].copy()
    payload["demographics"]["age"] = -5

    with pytest.raises(ValidationError):
        ClinicalCaseRequest.model_validate(payload)


def test_weight_validation_rejected(sample_clinical_case_payload: dict[str, Any]):
    payload = sample_clinical_case_payload.copy()
    payload["demographics"] = payload["demographics"].copy()
    payload["demographics"]["weight"] = 0.0

    with pytest.raises(ValidationError):
        ClinicalCaseRequest.model_validate(payload)


def test_schema_serialization_roundtrip(sample_clinical_case_payload: dict[str, Any]):
    model = ClinicalCaseRequest.model_validate(sample_clinical_case_payload)
    serialized = model.model_dump(mode="json")

    assert serialized["request_id"] == str(model.request_id)
    assert serialized["presentation"]["severity"] == model.presentation.severity.value
    assert serialized["demographics"]["sex"] == model.demographics.sex.value
    expected_timestamp = model.timestamp.isoformat()
    if expected_timestamp.endswith("+00:00"):
        expected_timestamp = expected_timestamp[:-6] + "Z"
    assert serialized["timestamp"] == expected_timestamp
