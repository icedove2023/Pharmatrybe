"""Exception helpers for PharmaTrybe API error responses."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import Request
from fastapi.exceptions import HTTPException as FastAPIHTTPException
from starlette.responses import JSONResponse

from app.schemas.api_response import ApiError, ApiFailure, ApiMetadata


class PharmaTrybeAPIException(Exception):
    """Base exception for backend bootstrap errors."""

    pass


def build_api_failure(
    request: Request,
    status_code: int,
    code: str,
    message: str,
    details: dict[str, Any] | None = None,
) -> JSONResponse:
    """Build a PharmaTrybe-standard failure response payload."""
    metadata = ApiMetadata(
        request_id=getattr(request.state, "request_id", "unknown"),
        timestamp=datetime.now(timezone.utc),
        api_version=getattr(request.state, "api_version", "v1"),
        processing_time_ms=float(getattr(request.state, "processing_time_ms", 0.0)),
    )
    error = ApiError(code=code, message=message, details=details or {})
    payload = ApiFailure(metadata=metadata, error=error).model_dump(mode="json")
    return JSONResponse(status_code=status_code, content=payload)


def map_http_exception_to_code(exc: FastAPIHTTPException) -> str:
    """Map FastAPI HTTP exceptions to the official PharmaTrybe error codes."""
    if isinstance(exc.detail, dict) and isinstance(exc.detail.get("code"), str):
        return exc.detail["code"]
    status_code = exc.status_code
    mapping = {
        400: "INVALID_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        409: "RESOURCE_ALREADY_EXISTS",
        422: "VALIDATION_ERROR",
        500: "INTERNAL_SERVER_ERROR",
        503: "SERVICE_UNAVAILABLE",
        504: "REQUEST_TIMEOUT",
    }
    return mapping.get(status_code, "INTERNAL_SERVER_ERROR")
