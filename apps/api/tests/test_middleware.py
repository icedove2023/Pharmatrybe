from __future__ import annotations

import asyncio
from types import SimpleNamespace
from unittest.mock import MagicMock

from starlette.responses import Response

from app.api.middleware.request_context import RequestContextMiddleware
from app.api.middleware.security_headers import SecurityHeadersMiddleware
from app.api.middleware.timing import TimingMiddleware
from app.api.middleware.logging_middleware import LoggingMiddleware
import app.logging.request_logger as request_logger_module
import app.api.middleware.logging_middleware as logging_middleware_module


def _make_request() -> SimpleNamespace:
    request = SimpleNamespace()
    request.state = SimpleNamespace()
    request.client = SimpleNamespace(host="1.2.3.4")
    request.url = SimpleNamespace(path="/test")
    request.method = "GET"
    return request


async def _call_next(response: Response):
    return response


def test_request_context_middleware_populates_request_state_and_header():
    request = _make_request()
    response = Response()
    middleware = RequestContextMiddleware()

    result = asyncio.run(middleware.dispatch(request, lambda req: _call_next(response)))

    assert hasattr(request.state, "request_id")
    assert request.state.user_id == "anonymous"
    assert request.state.user_role == "anonymous"
    assert result.headers["X-Request-ID"] == request.state.request_id


def test_timing_middleware_sets_process_time_header():
    request = _make_request()
    request.state.request_start_time = 0.0
    response = Response()
    middleware = TimingMiddleware()

    result = asyncio.run(middleware.dispatch(request, lambda req: _call_next(response)))

    assert "X-Process-Time" in result.headers
    assert isinstance(request.state.processing_time_ms, float)


def test_security_headers_middleware_adds_expected_headers():
    request = _make_request()
    response = Response()
    middleware = SecurityHeadersMiddleware()

    result = asyncio.run(middleware.dispatch(request, lambda req: _call_next(response)))

    assert result.headers["X-Content-Type-Options"] == "nosniff"
    assert result.headers["X-Frame-Options"] == "DENY"
    assert result.headers["Referrer-Policy"] == "no-referrer"
    assert result.headers["X-XSS-Protection"] == "1; mode=block"


def test_logging_middleware_executes_request_logging_and_audit(monkeypatch):
    request = _make_request()
    request.state = SimpleNamespace(request_id="req-123", user_id="user-123", user_role="clinician", processing_time_ms=5.0)
    response = Response(status_code=200)

    logger_mock = MagicMock()
    monkeypatch.setattr(request_logger_module, "logger", logger_mock)

    audit_mock = MagicMock()
    monkeypatch.setattr(logging_middleware_module, "audit_service", audit_mock)

    middleware = LoggingMiddleware()
    result = asyncio.run(middleware.dispatch(request, lambda req: _call_next(response)))

    logger_mock.info.assert_called_once()
    audit_mock.log_event.assert_called_once()
    assert result is response


def test_middleware_order_functions_correctly():
    request = _make_request()
    response = Response(status_code=200)

    logger_mock = MagicMock()
    request_logger_module.logger = logger_mock
    logging_middleware_module.audit_service = MagicMock()

    request_context = RequestContextMiddleware()
    timing = TimingMiddleware()
    security = SecurityHeadersMiddleware()
    logging_middleware = LoggingMiddleware()

    async def final_handler(req):
        return response

    async def security_handler(req):
        return await security.dispatch(req, final_handler)

    async def timing_handler(req):
        return await timing.dispatch(req, security_handler)

    async def request_context_handler(req):
        return await request_context.dispatch(req, timing_handler)

    result = asyncio.run(logging_middleware.dispatch(request, request_context_handler))

    assert result.headers["X-Request-ID"] == request.state.request_id
    assert "X-Process-Time" in result.headers
    assert result.headers["X-Content-Type-Options"] == "nosniff"
    logger_mock.info.assert_called_once()
    logging_middleware_module.audit_service.log_event.assert_called_once()
