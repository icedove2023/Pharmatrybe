"""Request logging helpers for PharmaTrybe."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import Request
from starlette.responses import Response

from app.logging.logger import get_logger

logger = get_logger("pharmatrybe.api.request")


def _extract_user_context(request: Request) -> dict[str, str]:
    return {
        "user_id": getattr(request.state, "user_id", "anonymous") or "anonymous",
        "user_role": getattr(request.state, "user_role", "anonymous") or "anonymous",
    }


def build_request_log_context(request: Request, response: Response) -> dict[str, Any]:
    """Build a structured context payload for outgoing request logs."""
    user_context = _extract_user_context(request)
    return {
        "request_id": getattr(request.state, "request_id", "unknown"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "method": request.method,
        "endpoint": request.url.path,
        "status_code": response.status_code,
        "processing_time_ms": getattr(request.state, "processing_time_ms", 0.0),
        "client_ip": getattr(request.state, "client_ip", "unknown"),
        "user_id": user_context["user_id"],
        "user_role": user_context["user_role"],
    }


def log_request(request: Request, response: Response) -> None:
    """Emit a structured log message for a completed request."""
    logger.info("request.completed", extra=build_request_log_context(request, response))
