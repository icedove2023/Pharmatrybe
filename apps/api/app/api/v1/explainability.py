"""Explainability router placeholder for the PharmaTrybe v1 API."""

from fastapi import APIRouter

router = APIRouter(prefix="/explainability", tags=["explainability"])


@router.get("", summary="Explainability service status")
async def explainability_status() -> dict[str, str]:
    """Return a placeholder status payload for the explainability service."""
    return {"service": "Explainability Engine", "status": "available"}
