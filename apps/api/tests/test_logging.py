from __future__ import annotations

import logging
from unittest.mock import MagicMock, patch
from starlette.requests import Request
from starlette.responses import Response
from types import SimpleNamespace

from app.logging.logger import StructuredLoggerAdapter, configure_logging, get_logger
from app.logging.audit import build_audit_event
from app.logging.request_logger import build_request_log_context, log_request


def test_structured_logger_adapter_formats_extra_fields():
    adapter = StructuredLoggerAdapter(logging.getLogger("test"), {})
    msg, kwargs = adapter.process("message", {"extra": {"key": "value"}})

    assert "key=value" in msg
    assert kwargs["extra"] == {}


def test_structured_logger_adapter_leaves_message_intact_without_extra():
    adapter = StructuredLoggerAdapter(logging.getLogger("test"), {})
    msg, kwargs = adapter.process("message", {})

    assert msg == "message"
    assert kwargs == {}


def test_configure_logging_sets_root_logger(monkeypatch):
    root_logger = MagicMock()
    root_logger.handlers = MagicMock()

    stream_handler = MagicMock()
    formatter = MagicMock()

    monkeypatch.setattr("app.logging.logger.logging.getLogger", lambda name=None: root_logger)
    monkeypatch.setattr("app.logging.logger.logging.StreamHandler", lambda: stream_handler)
    monkeypatch.setattr("app.logging.logger.logging.Formatter", lambda fmt: formatter)
    monkeypatch.setattr("app.logging.logger.settings", MagicMock(log_level="INFO"))

    configure_logging()

    root_logger.handlers.clear.assert_called_once()
    root_logger.setLevel.assert_called_once()
    stream_handler.setFormatter.assert_called_once_with(formatter)
    root_logger.addHandler.assert_called_once_with(stream_handler)


def test_get_logger_returns_structured_adapter():
    logger = get_logger("pharmatrybe.api.test")

    assert isinstance(logger, StructuredLoggerAdapter)


def test_build_audit_event_creates_audit_log():
    event = build_audit_event(
        request_id="req-123",
        user_id="user-123",
        user_role="clinician",
        action="TEST_ACTION",
        resource="resource",
        resource_id="1",
        status=logging.INFO,
        details={"source": "unit-test"},
    )

    assert event.request_id == "req-123"
    assert event.user_id == "user-123"
    assert event.action == "TEST_ACTION"
    assert event.details["source"] == "unit-test"


def test_build_request_log_context_returns_expected_fields():
    request = MagicMock()
    request.state = SimpleNamespace(request_id="req-123", processing_time_ms=10.0, client_ip="1.2.3.4", user_id="user-123", user_role="clinician")
    request.method = "GET"
    request.url = SimpleNamespace(path="/test")
    response = Response(status_code=200)

    context = build_request_log_context(request, response)

    assert context["request_id"] == "req-123"
    assert context["status_code"] == 200
    assert context["client_ip"] == "1.2.3.4"
    assert context["user_id"] == "user-123"


def test_log_request_calls_logger_info(monkeypatch):
    request = MagicMock()
    request.state = SimpleNamespace(request_id="req-123", processing_time_ms=10.0, client_ip="1.2.3.4", user_id="user-123", user_role="clinician")
    request.method = "GET"
    request.url = SimpleNamespace(path="/test")
    response = Response(status_code=200)

    logger_mock = MagicMock()
    monkeypatch.setattr("app.logging.request_logger.logger", logger_mock)

    log_request(request, response)

    logger_mock.info.assert_called_once()
