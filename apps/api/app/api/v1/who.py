"""WHO Knowledge Engine API endpoints for the PharmaTrybe v1 API."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from app.database.repositories.who_knowledge_repository import WHOKnowledgeRepository
from app.database.session import SessionLocal
from app.knowledge.router.default_router import build_default_router
from app.schemas.api_response import ApiMetadata, ApiSuccess
from app.services.who import WHOService, WHOServiceError

router = APIRouter(prefix="/who", tags=["who"])


def get_service() -> WHOService:
    session = SessionLocal()
    router = build_default_router(session)
    return WHOService(router=router)


def _build_metadata(request_id: str) -> ApiMetadata:
    return ApiMetadata(
        request_id=request_id,
        timestamp=datetime.now(timezone.utc),
        api_version="v1",
        processing_time_ms=0.0,
    )


def _serialize_model(entity: Any) -> Any:
    if entity is None:
        return None
    if isinstance(entity, list):
        return [_serialize_model(item) for item in entity]
    if hasattr(entity, "__dict__"):
        return {
            key: _serialize_model(value)
            for key, value in vars(entity).items()
            if not key.startswith("_")
        }
    return entity


@router.get("/diseases", summary="List supported diseases", response_model=ApiSuccess[list[dict[str, Any]]])
async def list_diseases(
    service: Annotated[WHOService, Depends(get_service)],
) -> ApiSuccess[list[dict[str, Any]]]:
    try:
        diseases = service.list_supported_diseases()
    except WHOServiceError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    return ApiSuccess(metadata=_build_metadata("list"), data=_serialize_model(diseases))


@router.get("/diseases/{disease_id}", summary="Get disease by id", response_model=ApiSuccess[dict[str, Any] | None])
async def get_disease(
    disease_id: Annotated[str, Path(..., description="Unique disease identifier")],
    service: Annotated[WHOService, Depends(get_service)],
) -> ApiSuccess[dict[str, Any] | None]:
    try:
        disease = service.get_disease_by_id(disease_id)
    except WHOServiceError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    return ApiSuccess(metadata=_build_metadata(disease_id), data=_serialize_model(disease))


@router.get("/search", summary="Search diseases", response_model=ApiSuccess[list[dict[str, Any]]])
async def search_diseases(
    q: Annotated[str, Query(..., description="Search query")],
    service: Annotated[WHOService, Depends(get_service)],
) -> ApiSuccess[list[dict[str, Any]]]:
    try:
        diseases = service.search_diseases(q)
    except WHOServiceError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    return ApiSuccess(metadata=_build_metadata("search"), data=_serialize_model(diseases))


@router.get("/guideline/{disease_id}", summary="Get complete guideline bundle", response_model=ApiSuccess[dict[str, Any] | None])
async def get_guideline(
    disease_id: Annotated[str, Path(..., description="Unique disease identifier")],
    service: Annotated[WHOService, Depends(get_service)],
) -> ApiSuccess[dict[str, Any] | None]:
    try:
        guideline = service.build_guideline_bundle(disease_id)
    except WHOServiceError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    return ApiSuccess(metadata=_build_metadata(disease_id), data=_serialize_model(guideline))


@router.get("/recommendations/{disease_id}", summary="Get disease recommendations", response_model=ApiSuccess[list[dict[str, Any]]])
async def get_recommendations(
    disease_id: Annotated[str, Path(..., description="Unique disease identifier")],
    service: Annotated[WHOService, Depends(get_service)],
) -> ApiSuccess[list[dict[str, Any]]]:
    try:
        recommendations = service.get_recommendations(disease_id)
    except WHOServiceError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    return ApiSuccess(metadata=_build_metadata(disease_id), data=_serialize_model(recommendations))


@router.get("/evidence/{disease_id}", summary="Get disease evidence", response_model=ApiSuccess[list[dict[str, Any]]])
async def get_evidence(
    disease_id: Annotated[str, Path(..., description="Unique disease identifier")],
    service: Annotated[WHOService, Depends(get_service)],
) -> ApiSuccess[list[dict[str, Any]]]:
    try:
        evidence = service.get_evidence(disease_id)
    except WHOServiceError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    return ApiSuccess(metadata=_build_metadata(disease_id), data=_serialize_model(evidence))


@router.get("/diagnostics/{disease_id}", summary="Get disease diagnostics", response_model=ApiSuccess[list[dict[str, Any]]])
async def get_diagnostics(
    disease_id: Annotated[str, Path(..., description="Unique disease identifier")],
    service: Annotated[WHOService, Depends(get_service)],
) -> ApiSuccess[list[dict[str, Any]]]:
    try:
        diagnostics = service.get_diagnostics(disease_id)
    except WHOServiceError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    return ApiSuccess(metadata=_build_metadata(disease_id), data=_serialize_model(diagnostics))


@router.get("/monitoring/{disease_id}", summary="Get disease monitoring", response_model=ApiSuccess[list[dict[str, Any]]])
async def get_monitoring(
    disease_id: Annotated[str, Path(..., description="Unique disease identifier")],
    service: Annotated[WHOService, Depends(get_service)],
) -> ApiSuccess[list[dict[str, Any]]]:
    try:
        monitoring = service.get_monitoring(disease_id)
    except WHOServiceError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    return ApiSuccess(metadata=_build_metadata(disease_id), data=_serialize_model(monitoring))


@router.get("/follow-up/{disease_id}", summary="Get disease follow-up", response_model=ApiSuccess[list[dict[str, Any]]])
async def get_follow_up(
    disease_id: Annotated[str, Path(..., description="Unique disease identifier")],
    service: Annotated[WHOService, Depends(get_service)],
) -> ApiSuccess[list[dict[str, Any]]]:
    try:
        follow_up = service.get_follow_up(disease_id)
    except WHOServiceError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    return ApiSuccess(metadata=_build_metadata(disease_id), data=_serialize_model(follow_up))


@router.get("/referral/{disease_id}", summary="Get disease referral", response_model=ApiSuccess[list[dict[str, Any]]])
async def get_referral(
    disease_id: Annotated[str, Path(..., description="Unique disease identifier")],
    service: Annotated[WHOService, Depends(get_service)],
) -> ApiSuccess[list[dict[str, Any]]]:
    try:
        referral = service.get_referral(disease_id)
    except WHOServiceError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    return ApiSuccess(metadata=_build_metadata(disease_id), data=_serialize_model(referral))


@router.get("/stewardship/{disease_id}", summary="Get disease stewardship", response_model=ApiSuccess[list[dict[str, Any]]])
async def get_stewardship(
    disease_id: Annotated[str, Path(..., description="Unique disease identifier")],
    service: Annotated[WHOService, Depends(get_service)],
) -> ApiSuccess[list[dict[str, Any]]]:
    try:
        stewardship = service.get_stewardship(disease_id)
    except WHOServiceError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    return ApiSuccess(metadata=_build_metadata(disease_id), data=_serialize_model(stewardship))


@router.get("/pathogens/{disease_id}", summary="Get disease pathogens", response_model=ApiSuccess[list[dict[str, Any]]])
async def get_pathogens(
    disease_id: Annotated[str, Path(..., description="Unique disease identifier")],
    service: Annotated[WHOService, Depends(get_service)],
) -> ApiSuccess[list[dict[str, Any]]]:
    try:
        pathogens = service.get_pathogens(disease_id)
    except WHOServiceError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    return ApiSuccess(metadata=_build_metadata(disease_id), data=_serialize_model(pathogens))
