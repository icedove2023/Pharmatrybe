"""Service layer helpers for the PharmaTrybe clinical case resource.

This module provides a thin orchestration boundary around the repository and the
Pydantic schemas without introducing endpoint logic or clinical reasoning.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.database.repositories.clinical_case_repository import ClinicalCaseRepository, RepositoryError
from app.schemas.api_response import ApiMetadata, ApiSuccess
from app.schemas.clinical_case import ClinicalCaseRequest, ClinicalCaseResource, ClinicalCaseResponse


class ClinicalCaseServiceError(RuntimeError):
    """Raised when the clinical case service cannot complete its operation."""


class ClinicalCaseService:
    """Service wrapper for basic CRUD interactions with clinical case schemas."""

    def __init__(self, repository: ClinicalCaseRepository | None = None) -> None:
        """Initialize the service with a repository instance."""
        self.repository = repository

    def _build_metadata(self, request_id: str, *, processing_time_ms: float = 0.0) -> ApiMetadata:
        """Create response metadata using the standard PharmaTrybe envelope."""
        return ApiMetadata(
            request_id=request_id,
            timestamp=datetime.now(timezone.utc),
            api_version="v1",
            processing_time_ms=processing_time_ms,
        )

    def create_case(self, payload: ClinicalCaseRequest) -> ClinicalCaseResponse:
        """Create a clinical case resource using the repository layer."""
        if self.repository is None:
            raise ClinicalCaseServiceError("No repository configured for the clinical case service")

        try:
            self.repository.create(payload.model_dump())
        except RepositoryError as exc:
            raise ClinicalCaseServiceError(str(exc)) from exc

        return ClinicalCaseResponse(
            metadata=self._build_metadata(str(payload.request_id)),
            data=ClinicalCaseResource(clinical_case=payload, status="created"),
        )

    def get_case(self, case_id: int) -> ClinicalCaseResource | None:
        """Return a clinical case resource by identifier when present."""
        if self.repository is None:
            raise ClinicalCaseServiceError("No repository configured for the clinical case service")

        try:
            entity = self.repository.get_by_id(case_id)
        except RepositoryError as exc:
            raise ClinicalCaseServiceError(str(exc)) from exc

        if entity is None:
            return None

        return ClinicalCaseResource(clinical_case=ClinicalCaseRequest.model_validate(entity), status="retrieved")

    def list_cases(self, *, skip: int = 0, limit: int | None = None) -> list[ClinicalCaseResource]:
        """Return a list of clinical case resources."""
        if self.repository is None:
            raise ClinicalCaseServiceError("No repository configured for the clinical case service")

        try:
            entities = self.repository.list(skip=skip, limit=limit)
        except RepositoryError as exc:
            raise ClinicalCaseServiceError(str(exc)) from exc

        return [
            ClinicalCaseResource(clinical_case=ClinicalCaseRequest.model_validate(entity), status="retrieved")
            for entity in entities
        ]

    def update_case(self, case_id: int, **kwargs: Any) -> ClinicalCaseResource | None:
        """Update a clinical case resource using keyword values."""
        if self.repository is None:
            raise ClinicalCaseServiceError("No repository configured for the clinical case service")

        try:
            entity = self.repository.update(case_id, **kwargs)
        except RepositoryError as exc:
            raise ClinicalCaseServiceError(str(exc)) from exc

        if entity is None:
            return None

        return ClinicalCaseResource(clinical_case=ClinicalCaseRequest.model_validate(entity), status="updated")

    def delete_case(self, case_id: int) -> None:
        """Delete a clinical case resource by identifier."""
        if self.repository is None:
            raise ClinicalCaseServiceError("No repository configured for the clinical case service")

        try:
            self.repository.delete(case_id)
        except RepositoryError as exc:
            raise ClinicalCaseServiceError(str(exc)) from exc
