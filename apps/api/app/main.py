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
from app.api.routes.health import router as health_router
from app.api.routes.version import router as version_router
from app.core.config import settings
from app.core.exceptions import build_api_failure, map_http_exception_to_code
from app.core.logging import configure_logging, get_logger

logger = get_logger("pharmatrybe.api.main")


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


@app.exception_handler(FastAPIHTTPException)
async def http_exception_handler(request: Request, exc: FastAPIHTTPException):
    """Convert FastAPI HTTP exceptions into PharmaTrybe standard failure payloads."""
    code = map_http_exception_to_code(exc)
    detail = exc.detail if isinstance(exc.detail, str) else "The request could not be processed."
    return build_api_failure(request, exc.status_code, code, detail)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Convert request validation failures into PharmaTrybe standard error responses."""
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
