"""Timing middleware that measures request execution time."""

import time
from typing import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class TimingMiddleware(BaseHTTPMiddleware):
    """Measure the processing time for each request and expose it in headers."""

    def __init__(self, app=None):
        if app is not None:
            super().__init__(app)

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        start_time = getattr(request.state, "request_start_time", time.perf_counter())
        response = await call_next(request)

        processing_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
        request.state.processing_time_ms = processing_time_ms
        response.headers["X-Process-Time"] = f"{processing_time_ms:.2f} ms"
        return response
