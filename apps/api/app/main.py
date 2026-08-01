"""Main FastAPI application for the PharmaTrybe backend bootstrap."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.api.routes.health import router as health_router
from app.api.routes.version import router as version_router
from app.core.config import settings
from app.core.logging import configure_logging


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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)

app.include_router(health_router)
app.include_router(version_router)


@app.get("/", tags=["platform"])
async def root() -> dict[str, str]:
    """Return the public platform status payload."""
    return {
        "platform": "PharmaTrybe",
        "status": "running",
        "version": settings.app_version,
    }
