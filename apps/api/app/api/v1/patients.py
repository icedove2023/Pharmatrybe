"""Account-owned patient directory and approved-task history endpoints."""

from datetime import datetime, timezone
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import AuthorizationContext, require_permission
from app.database.session import get_db_session
from app.models.patient_history import PatientHistoryEvent, PatientRecord
from app.schemas.api_response import ApiMetadata, ApiSuccess

router = APIRouter(prefix="/patients", tags=["patients"])


class ApprovedHistoryRequest(BaseModel):
    recommendation_id: str = Field(..., min_length=1)
    review_decision: str = Field(..., pattern="^(APPROVED|MODIFIED)$")
    selected_antibiotic: str | None = None
    clinical_notes: str | None = None
    patient_name: str | None = None
    demographics: dict[str, Any] = Field(default_factory=dict)


def _metadata(request_id: str) -> ApiMetadata:
    return ApiMetadata(request_id=request_id, timestamp=datetime.now(timezone.utc), api_version="v1", processing_time_ms=0.0)


@router.get("", response_model=ApiSuccess[list[dict[str, Any]]])
async def list_patients(context: Annotated[AuthorizationContext, Depends(require_permission("cases:view"))], db: Annotated[Session, Depends(get_db_session)], query: str | None = Query(default=None)) -> ApiSuccess[list[dict[str, Any]]]:
    records = list(db.scalars(select(PatientRecord).where(PatientRecord.owner_user_id == context.user_id, PatientRecord.hospital_id == context.hospital_id).order_by(PatientRecord.updated_at.desc())).all())
    normalized = query.strip().lower() if query else ""
    if normalized:
        records = [record for record in records if normalized in " ".join(filter(None, [record.id, record.name, record.sex])).lower()]
    data = [{"id": record.id, "name": record.name, "date_of_birth": record.date_of_birth, "sex": record.sex, "hospital_id": record.hospital_id, "demographics": record.demographics} for record in records]
    return ApiSuccess(metadata=_metadata("patients"), data=data)


@router.get("/{patient_id}", response_model=ApiSuccess[dict[str, Any] | None])
async def get_patient(patient_id: str, context: Annotated[AuthorizationContext, Depends(require_permission("cases:view"))], db: Annotated[Session, Depends(get_db_session)]) -> ApiSuccess[dict[str, Any] | None]:
    record = db.scalar(select(PatientRecord).where(PatientRecord.id == patient_id, PatientRecord.owner_user_id == context.user_id, PatientRecord.hospital_id == context.hospital_id))
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient record not found")
    return ApiSuccess(metadata=_metadata(patient_id), data={"id": record.id, "name": record.name, "date_of_birth": record.date_of_birth, "sex": record.sex, "hospital_id": record.hospital_id, "demographics": record.demographics})


@router.get("/{patient_id}/history", response_model=ApiSuccess[list[dict[str, Any]]])
async def get_patient_history(patient_id: str, context: Annotated[AuthorizationContext, Depends(require_permission("cases:view"))], db: Annotated[Session, Depends(get_db_session)]) -> ApiSuccess[list[dict[str, Any]]]:
    patient = db.scalar(select(PatientRecord).where(PatientRecord.id == patient_id, PatientRecord.owner_user_id == context.user_id, PatientRecord.hospital_id == context.hospital_id))
    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient record not found")
    events = db.scalars(select(PatientHistoryEvent).where(PatientHistoryEvent.patient_id == patient_id, PatientHistoryEvent.owner_user_id == context.user_id).order_by(PatientHistoryEvent.created_at.asc())).all()
    data = [{"id": str(event.id), "type": event.event_type, "timestamp": event.created_at.isoformat(), "user": context.user_id, "summary": event.summary, "payload": event.payload} for event in events]
    return ApiSuccess(metadata=_metadata(patient_id), data=data)


@router.post("/{patient_id}/history", response_model=ApiSuccess[dict[str, Any]], status_code=status.HTTP_201_CREATED)
async def create_approved_history(patient_id: str, payload: ApprovedHistoryRequest, context: Annotated[AuthorizationContext, Depends(require_permission("recommendations:request"))], db: Annotated[Session, Depends(get_db_session)]) -> ApiSuccess[dict[str, Any]]:
    patient = db.scalar(select(PatientRecord).where(PatientRecord.id == patient_id, PatientRecord.owner_user_id == context.user_id, PatientRecord.hospital_id == context.hospital_id))
    if patient is None:
        patient = PatientRecord(id=patient_id, owner_user_id=context.user_id, hospital_id=context.hospital_id, name=payload.patient_name, sex=str(payload.demographics.get("sex")) if payload.demographics.get("sex") else None, demographics=payload.demographics)
        db.add(patient)
    event = PatientHistoryEvent(patient_id=patient_id, owner_user_id=context.user_id, event_type="Clinician Action", summary=f"{payload.review_decision.title()} recommendation {payload.recommendation_id}.", payload=payload.model_dump(exclude_none=True))
    db.add(event)
    db.commit()
    db.refresh(event)
    return ApiSuccess(metadata=_metadata(patient_id), data={"id": str(event.id), "type": event.event_type, "timestamp": event.created_at.isoformat(), "user": context.user_id, "summary": event.summary, "payload": event.payload})
