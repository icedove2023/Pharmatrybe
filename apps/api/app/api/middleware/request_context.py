"""Request context middleware that attaches request metadata to the request state."""

import time
import uuid
from typing import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Populate request-scoped metadata for every incoming request."""

    def __init__(self, app=None):
        # Allow tests to instantiate middleware without providing an ASGI
        # `app`. If an app is provided, initialize the BaseHTTPMiddleware.
        if app is not None:
            super().__init__(app)

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request.state.request_id = str(uuid.uuid4())
        request.state.request_start_time = time.perf_counter()
        request.state.processing_time_ms = 0.0
        request.state.api_version = "v1"
        request.state.client_ip = request.client.host if request.client else "unknown"
        request.state.user_id = "anonymous"
        request.state.user_role = "anonymous"

        response = await call_next(request)
        response.headers["X-Request-ID"] = request.state.request_id
        return response
