"""Standard response models for all PharmaTrybe API services.

These schemas provide a consistent success and failure envelope for the FastAPI
backend and for future service integrations. They are intentionally reusable and
contain no business logic.
"""

from __future__ import annotations

from datetime import datetime
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ApiMetadata(BaseModel):
    """Common metadata attached to every PharmaTrybe API response."""

    request_id: str = Field(..., description="Correlation identifier for the request")
    timestamp: datetime = Field(..., description="UTC timestamp for the response")
    api_version: str = Field(default="v1", description="Version of the PharmaTrybe API contract")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")


class ApiError(BaseModel):
    """Standard error payload for failed PharmaTrybe API responses."""

    code: str = Field(..., description="Stable machine-readable error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[dict] = Field(default=None, description="Optional structured error details")


class ApiSuccess(BaseModel, Generic[T]):
    """Standard success envelope for successful PharmaTrybe API responses."""

    success: bool = Field(default=True, description="Indicates that the operation succeeded")
    metadata: ApiMetadata
    data: T


class ApiFailure(BaseModel):
    """Standard failure envelope for failed PharmaTrybe API responses."""

    success: bool = Field(default=False, description="Indicates that the operation failed")
    metadata: ApiMetadata
    error: ApiError
