"""ARMD router placeholder for the PharmaTrybe v1 API."""

from fastapi import APIRouter

router = APIRouter(prefix="/armd", tags=["armd"])


@router.get("", summary="ARMD service status")
async def armd_status() -> dict[str, str]:
    """Return a placeholder status payload for the ARMD service."""
    return {"service": "ARMD Engine", "status": "available"}
