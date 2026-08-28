"""Version route definitions."""

from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(tags=["version"])


@router.get("/version")
async def get_version() -> dict[str, str]:
    """Return the platform version payload."""
    return {
        "service": "Platform Version",
        "version": settings.app_version,
    }
