"""Versioned version route definitions for the PharmaTrybe v1 API."""

from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(prefix="/version", tags=["version"])


@router.get("", summary="Version endpoint")
async def version_status() -> dict[str, str]:
    """Return the versioned platform version payload."""
    return {"service": "Platform Version", "status": "available", "version": settings.app_version}
