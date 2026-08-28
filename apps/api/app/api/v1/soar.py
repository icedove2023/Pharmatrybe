"""SOAR/GSK router placeholder for the PharmaTrybe v1 API."""

from fastapi import APIRouter

router = APIRouter(prefix="/soar", tags=["soar"])


@router.get("", summary="SOAR/GSK service status")
async def soar_status() -> dict[str, str]:
    """Return a placeholder status payload for the SOAR/GSK service."""
    return {"service": "SOAR/GSK Engine", "status": "available"}
