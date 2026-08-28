"""Audit log schema for the PharmaTrybe backend."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class AuditStatus(str, Enum):
    """Enumerated status codes for audit events."""

    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    WARNING = "WARNING"
    INFO = "INFO"


class AuditLog(BaseModel):
    """Structured audit record representation."""

    event_id: str = Field(..., description="Unique audit event identifier")
    request_id: str = Field(..., description="Correlation identifier for the request lifecycle")
    timestamp: datetime = Field(..., description="UTC timestamp when the audit event was created")
    user_id: str | None = Field(default=None, description="Authenticated user identifier")
    hospital_id: str | None = Field(default=None, description="Resolved hospital tenant identifier")
    user_role: str | None = Field(default=None, description="Authenticated user role")
    action: str = Field(..., description="Audit event action")
    resource: str | None = Field(default=None, description="Audited resource type")
    resource_id: str | None = Field(default=None, description="Target resource identifier")
    status: AuditStatus = Field(..., description="Outcome status of the audit event")
    details: dict[str, Any] | None = Field(default=None, description="Additional structured event details")
    source_service: str | None = Field(default=None, description="Originating service or component")
