"""Logging middleware that records request lifecycle details."""

from typing import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.logging.request_logger import log_request
from app.services.audit.audit_service import AuditService
from app.models.audit_log import AuditStatus


audit_service = AuditService()


class LoggingMiddleware(BaseHTTPMiddleware):
    """Log request lifecycle details after each response is generated."""

    def __init__(self, app=None):
        if app is not None:
            super().__init__(app)

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        response = await call_next(request)

        log_request(request, response)
        audit_service.log_event(
            request_id=getattr(request.state, "request_id", "unknown"),
            user_id=getattr(request.state, "user_id", "anonymous"),
            user_role=getattr(request.state, "user_role", "anonymous"),
            action="REQUEST_COMPLETED",
            resource="http_request",
            resource_id=f"{request.method}:{request.url.path}",
            status=(
                AuditStatus.SUCCESS
                if response.status_code < 400
                else AuditStatus.FAILURE
            ),
            details={
                "status_code": response.status_code,
                "processing_time_ms": getattr(request.state, "processing_time_ms", 0.0),
                "client_ip": getattr(request.state, "client_ip", "unknown"),
            },
        )
        return response
