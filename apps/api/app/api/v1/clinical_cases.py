"""Clinical case API endpoints for the PharmaTrybe v1 API."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from app.auth import AuthorizationContext, deny_by_default, require_permission
from app.database.repositories.clinical_case_repository import ClinicalCaseRepository
from app.database.session import SessionLocal
from app.schemas.api_response import ApiMetadata, ApiSuccess
from app.schemas.clinical_case import ClinicalCaseRequest, ClinicalCaseResource, ClinicalCaseResponse
from app.services.clinical_case.clinical_case_service import ClinicalCaseService, ClinicalCaseServiceError

router = APIRouter(prefix="/clinical-cases", tags=["clinical_cases"])


def get_service() -> ClinicalCaseService:
    """Reject persistence until a mapped clinical-case entity exists."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Clinical case persistence is not exposed until its database entity is implemented.",
    )


@router.post("", response_model=ClinicalCaseResponse, status_code=status.HTTP_201_CREATED)
async def create_clinical_case(
    payload: ClinicalCaseRequest,
    service: Annotated[ClinicalCaseService, Depends(get_service)],
    _context: Annotated[AuthorizationContext, Depends(require_permission("cases:create"))],
) -> ClinicalCaseResponse:
    """Create a new clinical case resource."""
    try:
        return service.create_case(payload)
    except ClinicalCaseServiceError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.get("/{case_id}", response_model=ApiSuccess[ClinicalCaseResource | None])
async def get_clinical_case(
    case_id: Annotated[int, Path(..., description="Unique clinical case identifier")],
    service: Annotated[ClinicalCaseService, Depends(get_service)],
    _context: Annotated[AuthorizationContext, Depends(require_permission("cases:view"))],
) -> ApiSuccess[ClinicalCaseResource | None]:
    """Return a single clinical case resource by identifier."""
    try:
        resource = service.get_case(case_id)
    except ClinicalCaseServiceError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    return ApiSuccess(
        metadata=ApiMetadata(
            request_id=str(case_id),
            timestamp=datetime.now(timezone.utc),
            api_version="v1",
            processing_time_ms=0.0,
        ),
        data=resource,
    )


@router.get("", response_model=ApiSuccess[list[ClinicalCaseResource]])
async def list_clinical_cases(
    service: Annotated[ClinicalCaseService, Depends(get_service)],
    _context: Annotated[AuthorizationContext, Depends(require_permission("cases:view"))],
    skip: int = Query(default=0, ge=0),
    limit: int | None = Query(default=None, ge=1),
) -> ApiSuccess[list[ClinicalCaseResource]]:
    """Return a paged list of clinical case resources."""
    try:
        resources = service.list_cases(skip=skip, limit=limit)
    except ClinicalCaseServiceError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    return ApiSuccess(
        metadata=ApiMetadata(
            request_id="list",
            timestamp=datetime.now(timezone.utc),
            api_version="v1",
            processing_time_ms=0.0,
        ),
        data=resources,
    )


@router.put("/{case_id}", response_model=ApiSuccess[ClinicalCaseResource | None])
async def update_clinical_case(
    case_id: Annotated[int, Path(..., description="Unique clinical case identifier")],
    payload: dict[str, object],
    service: Annotated[ClinicalCaseService, Depends(get_service)],
    _context: Annotated[AuthorizationContext, Depends(require_permission("cases:update"))],
) -> ApiSuccess[ClinicalCaseResource | None]:
    """Update a clinical case resource using a partial payload."""
    try:
        resource = service.update_case(case_id, **payload)
    except ClinicalCaseServiceError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    return ApiSuccess(
        metadata=ApiMetadata(
            request_id=str(case_id),
            timestamp=datetime.now(timezone.utc),
            api_version="v1",
            processing_time_ms=0.0,
        ),
        data=resource,
    )


@router.delete("/{case_id}", response_model=ApiSuccess[dict[str, bool]])
async def delete_clinical_case(
    case_id: Annotated[int, Path(..., description="Unique clinical case identifier")],
    service: Annotated[ClinicalCaseService, Depends(get_service)],
    _context: Annotated[None, Depends(deny_by_default)],
) -> ApiSuccess[dict[str, bool]]:
    """Delete a clinical case resource by identifier."""
    try:
        service.delete_case(case_id)
    except ClinicalCaseServiceError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    return ApiSuccess(
        metadata=ApiMetadata(
            request_id=str(case_id),
            timestamp=datetime.now(timezone.utc),
            api_version="v1",
            processing_time_ms=0.0,
        ),
        data={"deleted": True},
    )
