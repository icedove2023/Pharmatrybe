from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from app.database.repositories.clinical_case_repository import RepositoryError
from app.schemas.clinical_case import ClinicalCaseResource, ClinicalCaseRequest
from app.services.clinical_case.clinical_case_service import ClinicalCaseService, ClinicalCaseServiceError


def test_create_case_calls_repository_and_returns_response(sample_clinical_case_request: ClinicalCaseRequest):
    repository = MagicMock()
    service = ClinicalCaseService(repository)

    result = service.create_case(sample_clinical_case_request)

    repository.create.assert_called_once_with(sample_clinical_case_request.model_dump())
    assert isinstance(result, object)
    assert result.data.clinical_case.request_id == sample_clinical_case_request.request_id


def test_get_case_returns_resource(sample_clinical_case_payload: dict[str, object]):
    repository = MagicMock()
    repository.get_by_id.return_value = sample_clinical_case_payload
    service = ClinicalCaseService(repository)

    result = service.get_case(1)

    repository.get_by_id.assert_called_once_with(1)
    assert isinstance(result, ClinicalCaseResource)
    assert str(result.clinical_case.request_id) == sample_clinical_case_payload["request_id"]
    assert result.status == "retrieved"


def test_get_case_returns_none_when_missing():
    repository = MagicMock()
    repository.get_by_id.return_value = None
    service = ClinicalCaseService(repository)

    result = service.get_case(1)

    assert result is None
    repository.get_by_id.assert_called_once_with(1)


def test_list_cases_returns_resource_list(sample_clinical_case_payload: dict[str, object]):
    repository = MagicMock()
    repository.list.return_value = [sample_clinical_case_payload]
    service = ClinicalCaseService(repository)

    results = service.list_cases(skip=0, limit=10)

    repository.list.assert_called_once_with(skip=0, limit=10)
    assert len(results) == 1
    assert isinstance(results[0], ClinicalCaseResource)


def test_update_case_returns_updated_resource(sample_clinical_case_payload: dict[str, object]):
    repository = MagicMock()
    repository.update.return_value = sample_clinical_case_payload
    service = ClinicalCaseService(repository)

    result = service.update_case(1, resistance_status="predicted")

    repository.update.assert_called_once_with(1, resistance_status="predicted")
    assert isinstance(result, ClinicalCaseResource)
    assert result.status == "updated"


def test_delete_case_calls_repository():
    repository = MagicMock()
    service = ClinicalCaseService(repository)

    service.delete_case(1)

    repository.delete.assert_called_once_with(1)


def test_create_case_raises_service_error_on_repository_failure(sample_clinical_case_request: ClinicalCaseRequest):
    repository = MagicMock()
    repository.create.side_effect = RepositoryError("database failure")
    service = ClinicalCaseService(repository)

    with pytest.raises(ClinicalCaseServiceError):
        service.create_case(sample_clinical_case_request)


def test_get_case_raises_service_error_on_repository_failure():
    repository = MagicMock()
    repository.get_by_id.side_effect = RepositoryError("database failure")
    service = ClinicalCaseService(repository)

    with pytest.raises(ClinicalCaseServiceError):
        service.get_case(1)
