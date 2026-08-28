"""Versioned health route definitions for the PharmaTrybe v1 API."""

from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", summary="Health endpoint")
async def health_status() -> dict[str, str]:
    """Return the versioned health status payload."""
    return {"service": "Platform Health", "status": "available"}
