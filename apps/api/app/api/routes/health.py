"""Health-check route definitions."""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Return the backend health status payload."""
    return {"service": "Platform Health", "status": "available"}
