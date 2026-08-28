"""Main FastAPI application for the PharmaTrybe backend bootstrap."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException as FastAPIHTTPException, RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.api.middleware.logging_middleware import LoggingMiddleware
from app.api.middleware.request_context import RequestContextMiddleware
from app.api.middleware.security_headers import SecurityHeadersMiddleware
from app.api.middleware.timing import TimingMiddleware
from app.api.router import router as api_router
from app.api.routes.health import router as health_router
from app.api.routes.version import router as version_router
from app.core.config import settings
from app.core.exceptions import build_api_failure, map_http_exception_to_code
from app.core.logging import configure_logging, get_logger
from app.models.audit_log import AuditStatus
from app.services.audit.audit_service import AuditService

logger = get_logger("pharmatrybe.api.main")
audit_service = AuditService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan hooks for startup and shutdown."""
    configure_logging()
    yield


app = FastAPI(
    title=settings.app_name,
    description="Explainable Artificial Intelligence Clinical Decision Support Backend for Antimicrobial Stewardship.",
    version=settings.app_version,
    lifespan=lifespan,
)

app.add_middleware(RequestContextMiddleware)
app.add_middleware(TimingMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

app.include_router(health_router)
app.include_router(version_router)
app.include_router(api_router, prefix="/api/v1")


@app.exception_handler(FastAPIHTTPException)
async def http_exception_handler(request: Request, exc: FastAPIHTTPException):
    """Convert FastAPI HTTP exceptions into PharmaTrybe standard failure payloads."""
    code = map_http_exception_to_code(exc)
    detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail.get("message", "The request could not be processed.")) if isinstance(exc.detail, dict) else "The request could not be processed."
    details = exc.detail.get("details", {}) if isinstance(exc.detail, dict) else {}

    if exc.status_code in (401, 403):
        audit_service.log_error(
            request_id=getattr(request.state, "request_id", "unknown"),
            user_id=getattr(request.state, "user_id", "anonymous"),
            user_role=getattr(request.state, "user_role", "anonymous"),
            action="FAILED_AUTHORIZATION",
            resource="http_request",
            resource_id=request.url.path,
            error_message=str(detail),
            details={"status_code": exc.status_code},
        )

    return build_api_failure(request, exc.status_code, code, detail, details)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Convert request validation failures into PharmaTrybe standard error responses."""
    audit_service.log_error(
        request_id=getattr(request.state, "request_id", "unknown"),
        user_id=getattr(request.state, "user_id", "anonymous"),
        user_role=getattr(request.state, "user_role", "anonymous"),
        action="VALIDATION_ERROR",
        resource="http_request",
        resource_id=request.url.path,
        error_message="Request validation failed.",
        details={"errors": exc.errors()},
    )
    return build_api_failure(
        request,
        422,
        "VALIDATION_ERROR",
        "Request validation failed.",
        {"errors": exc.errors()},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Convert unexpected exceptions into PharmaTrybe standard internal error responses."""
    logger.exception("Unhandled exception occurred", exc_info=exc)
    audit_service.log_error(
        request_id=getattr(request.state, "request_id", "unknown"),
        user_id=getattr(request.state, "user_id", "anonymous"),
        user_role=getattr(request.state, "user_role", "anonymous"),
        action="INTERNAL_SERVER_ERROR",
        resource="http_request",
        resource_id=request.url.path,
        error_message=str(exc),
        details={"exception_type": type(exc).__name__},
    )
    return build_api_failure(
        request,
        500,
        "INTERNAL_SERVER_ERROR",
        "An unexpected server error occurred.",
    )


@app.get("/", tags=["platform"])
async def root() -> dict[str, str]:
    """Return the public platform status payload."""
    return {
        "platform": "PharmaTrybe",
        "status": "running",
        "version": settings.app_version,
    }
