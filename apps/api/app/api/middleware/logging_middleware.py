"""Logging middleware that records request lifecycle details."""

from datetime import datetime, timezone
from typing import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import get_logger

logger = get_logger("pharmatrybe.api.request")


class LoggingMiddleware(BaseHTTPMiddleware):
    """Log request lifecycle details after each response is generated."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        response = await call_next(request)

        processing_time_ms = getattr(request.state, "processing_time_ms", 0.0)
        logger.info(
            "request_completed request_id=%s method=%s path=%s status_code=%s processing_time_ms=%.2f client_ip=%s timestamp=%s",
            getattr(request.state, "request_id", "unknown"),
            request.method,
            request.url.path,
            response.status_code,
            processing_time_ms,
            getattr(request.state, "client_ip", "unknown"),
            datetime.now(timezone.utc).isoformat(),
        )
        return response
