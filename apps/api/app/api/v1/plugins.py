"""Governance API for tenant-scoped plugin registration and lifecycle management."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import AuthorizationContext, get_authorization_context
from app.database.session import get_db_session
from app.models.identity import Hospital
from app.models.plugin_governance import (
    GovernanceApprovalState,
    GovernanceStatus,
    GovernanceTrustLevel,
    GovernanceValidationState,
    PluginGovernanceRecord,
)
from app.services.plugin_governance import PluginGovernanceService
from app.plugins.security.artifact import ArtifactSecurityError, PluginArtifactService

router = APIRouter(prefix="/plugins", tags=["plugins"])


class PluginGovernanceSubmission(BaseModel):
    plugin_id: str = Field(..., min_length=1)
    plugin_name: str = Field(..., min_length=1)
    plugin_type: str = Field(..., description="knowledge or prediction")
    plugin_version: str = Field(..., min_length=1)
    plugin_origin: str = Field(default="external")
    owner: str = Field(..., min_length=1)
    publisher: str = Field(..., min_length=1)
    artifact_hash: str | None = None
    artifact_uri: str | None = None
    capabilities: list[str] = Field(default_factory=list)
    configuration: dict[str, Any] | None = None


class PluginGovernanceApproval(BaseModel):
    approved: bool = True


def _require_governance_permission(context: AuthorizationContext) -> None:
    if "HOSPITAL_ADMIN" not in context.roles or "plugins:configure" not in context.permissions:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Plugin governance permission required")


@router.get("", summary="List plugins in the current hospital governance registry")
async def list_hospital_plugins(
    db: Annotated[Session, Depends(get_db_session)],
    context: Annotated[AuthorizationContext, Depends(get_authorization_context)],
) -> dict[str, Any]:
    _require_governance_permission(context)
    service = PluginGovernanceService(db)
    records = service.list_for_hospital(context.hospital_id)
    return {"items": [
        {
            "plugin_id": record.plugin_id,
            "plugin_name": record.plugin_name,
            "plugin_type": record.plugin_type,
            "plugin_version": record.plugin_version,
            "status": record.status,
            "validation_state": record.validation_state,
            "approval_state": record.approval_state,
            "trust_level": record.trust_level,
            "hospital_id": record.hospital_id,
        }
        for record in records
    ]}


@router.post("", status_code=status.HTTP_201_CREATED, summary="Register a hospital plugin for governance review")
async def register_plugin(
    payload: PluginGovernanceSubmission,
    db: Annotated[Session, Depends(get_db_session)],
    context: Annotated[AuthorizationContext, Depends(get_authorization_context)],
) -> dict[str, Any]:
    _require_governance_permission(context)
    hospital = db.get(Hospital, context.hospital_id)
    if hospital is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hospital not found")

    service = PluginGovernanceService(db)
    record = service.register_plugin(
        hospital_id=context.hospital_id,
        plugin_id=payload.plugin_id,
        plugin_name=payload.plugin_name,
        plugin_type=payload.plugin_type,
        plugin_version=payload.plugin_version,
        plugin_origin=payload.plugin_origin,
        owner=payload.owner,
        publisher=payload.publisher,
        artifact_hash=payload.artifact_hash,
        artifact_uri=payload.artifact_uri,
        capabilities=payload.capabilities,
        submitted_by_user_id=context.user_id,
        configuration=payload.configuration,
    )
    return {
        "plugin_id": record.plugin_id,
        "status": record.status,
        "validation_state": record.validation_state,
        "approval_state": record.approval_state,
    }


@router.post("/upload", status_code=status.HTTP_201_CREATED, summary="Safely submit a plugin ZIP artifact")
async def upload_plugin(
    plugin_id: str,
    plugin_name: str,
    plugin_type: str,
    plugin_version: str,
    owner: str,
    publisher: str,
    db: Annotated[Session, Depends(get_db_session)],
    context: Annotated[AuthorizationContext, Depends(get_authorization_context)],
    artifact: UploadFile = File(...),
) -> dict[str, Any]:
    _require_governance_permission(context)
    if not artifact.filename or not artifact.filename.lower().endswith(".zip"):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="A ZIP plugin artifact is required")
    artifact_root = Path("var/plugin-artifacts") / context.hospital_id
    artifact_root.mkdir(parents=True, exist_ok=True)
    artifact_path = artifact_root / f"{plugin_id}-{plugin_version}.zip"
    with artifact_path.open("wb") as output:
        while chunk := await artifact.read(1024 * 1024):
            output.write(chunk)
    try:
        inspection = PluginArtifactService().inspect(artifact_path)
    except ArtifactSecurityError as exc:
        artifact_path.unlink(missing_ok=True)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    record = PluginGovernanceService(db).register_plugin(
        hospital_id=context.hospital_id,
        plugin_id=plugin_id,
        plugin_name=plugin_name,
        plugin_type=plugin_type,
        plugin_version=plugin_version,
        plugin_origin="external",
        owner=owner,
        publisher=publisher,
        artifact_hash=inspection.sha256,
        artifact_uri=str(artifact_path),
        artifact_size=inspection.size,
        submitted_by_user_id=context.user_id,
    )
    return {"plugin_id": record.plugin_id, "plugin_version": record.plugin_version, "artifact_hash": inspection.sha256, "status": record.status}


@router.post("/{plugin_id}/validate", summary="Validate a submitted hospital plugin")
async def validate_plugin(
    plugin_id: str,
    db: Annotated[Session, Depends(get_db_session)],
    context: Annotated[AuthorizationContext, Depends(get_authorization_context)],
) -> dict[str, Any]:
    _require_governance_permission(context)
    service = PluginGovernanceService(db)
    record = service.validate_plugin(plugin_id, hospital_id=context.hospital_id, validated_by_user_id=context.user_id)
    return {"plugin_id": record.plugin_id, "status": record.status, "validation_state": record.validation_state}


@router.post("/{plugin_id}/approve", summary="Approve a validated hospital plugin")
async def approve_plugin(
    plugin_id: str,
    db: Annotated[Session, Depends(get_db_session)],
    context: Annotated[AuthorizationContext, Depends(get_authorization_context)],
) -> dict[str, Any]:
    _require_governance_permission(context)
    service = PluginGovernanceService(db)
    record = service.approve_plugin(plugin_id, hospital_id=context.hospital_id, approved_by_user_id=context.user_id)
    return {"plugin_id": record.plugin_id, "status": record.status, "approval_state": record.approval_state}


@router.post("/{plugin_id}/activate", summary="Activate an approved hospital plugin")
async def activate_plugin(
    plugin_id: str,
    db: Annotated[Session, Depends(get_db_session)],
    context: Annotated[AuthorizationContext, Depends(get_authorization_context)],
) -> dict[str, Any]:
    _require_governance_permission(context)
    service = PluginGovernanceService(db)
    record = service.activate_plugin(plugin_id, hospital_id=context.hospital_id)
    return {"plugin_id": record.plugin_id, "status": record.status}


@router.post("/{plugin_id}/deactivate", summary="Disable an active hospital plugin")
async def deactivate_plugin(
    plugin_id: str,
    db: Annotated[Session, Depends(get_db_session)],
    context: Annotated[AuthorizationContext, Depends(get_authorization_context)],
) -> dict[str, Any]:
    _require_governance_permission(context)
    service = PluginGovernanceService(db)
    record = service.deactivate_plugin(plugin_id, hospital_id=context.hospital_id, actor_user_id=context.user_id)
    return {"plugin_id": record.plugin_id, "status": record.status}


@router.post("/{plugin_id}/revoke", summary="Revoke a hospital plugin")
async def revoke_plugin(
    plugin_id: str,
    db: Annotated[Session, Depends(get_db_session)],
    context: Annotated[AuthorizationContext, Depends(get_authorization_context)],
) -> dict[str, Any]:
    _require_governance_permission(context)
    service = PluginGovernanceService(db)
    record = service.revoke_plugin(plugin_id, hospital_id=context.hospital_id, actor_user_id=context.user_id)
    return {"plugin_id": record.plugin_id, "status": record.status}


@router.post("/{plugin_id}/reject", summary="Reject a hospital plugin")
async def reject_plugin(
    plugin_id: str,
    db: Annotated[Session, Depends(get_db_session)],
    context: Annotated[AuthorizationContext, Depends(get_authorization_context)],
) -> dict[str, Any]:
    _require_governance_permission(context)
    record = PluginGovernanceService(db).reject_plugin(plugin_id, hospital_id=context.hospital_id, actor_user_id=context.user_id)
    return {"plugin_id": record.plugin_id, "status": record.status}


@router.post("/{plugin_id}/quarantine", summary="Quarantine a hospital plugin")
async def quarantine_plugin(
    plugin_id: str,
    db: Annotated[Session, Depends(get_db_session)],
    context: Annotated[AuthorizationContext, Depends(get_authorization_context)],
) -> dict[str, Any]:
    _require_governance_permission(context)
    record = PluginGovernanceService(db).quarantine_plugin(plugin_id, hospital_id=context.hospital_id, actor_user_id=context.user_id)
    return {"plugin_id": record.plugin_id, "status": record.status}


@router.get("/{plugin_id}", summary="Fetch a single hospital plugin governance record")
async def get_plugin_record(
    plugin_id: str,
    db: Annotated[Session, Depends(get_db_session)],
    context: Annotated[AuthorizationContext, Depends(get_authorization_context)],
) -> dict[str, Any]:
    _require_governance_permission(context)
    service = PluginGovernanceService(db)
    record = service.get_record(plugin_id, hospital_id=context.hospital_id)
    return {
        "plugin_id": record.plugin_id,
        "plugin_name": record.plugin_name,
        "status": record.status,
        "validation_state": record.validation_state,
        "approval_state": record.approval_state,
        "trust_level": record.trust_level,
        "hospital_id": record.hospital_id,
        "audit_events": [
            {"action": event.action, "details": event.details, "created_at": event.created_at.isoformat()}
            for event in record.audit_events
        ],
    }
