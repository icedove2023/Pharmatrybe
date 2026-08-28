"""
WP5 Clinical Intelligence API

FastAPI application entrypoint.

Responsibilities
----------------
• Expose REST API
• Dependency Injection
• Application lifecycle
• API routing

Business logic lives inside Services.
Inference remains inside WP4.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
import uvicorn

from .api.routes import router
from .utils.logging_config import setup_logging

# Configure application logger
logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup / Shutdown lifecycle.
    """

    logger.info("=" * 80)
    logger.info("Starting WP5 Clinical Intelligence API")
    logger.info("=" * 80)

    yield

    logger.info("=" * 80)
    logger.info("Stopping WP5 Clinical Intelligence API")
    logger.info("=" * 80)


app = FastAPI(
    title="ARMD Clinical Intelligence API",
    description=(
        "Clinical Intelligence Service built on top of the "
        "validated WP4 Antimicrobial Resistance Decision Engine."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(router)


@app.get("/", tags=["System"])
async def root():
    """Root endpoint."""
    return {
        "service": "ARMD Clinical Intelligence API",
        "version": app.version,
        "status": "running",
    }


@app.get("/health", tags=["System"])
async def health():
    """Health check."""
    return {
        "status": "healthy"
    }


if __name__ == "__main__":
    uvicorn.run(
        "WP5_Clinical_Intelligence.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )