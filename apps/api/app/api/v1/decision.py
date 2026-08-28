"""Decision engine router placeholder for the PharmaTrybe v1 API."""

from fastapi import APIRouter

router = APIRouter(prefix="/decision", tags=["decision"])


@router.get("", summary="Decision engine service status")
async def decision_status() -> dict[str, str]:
    """Return a placeholder status payload for the decision engine service."""
    return {"service": "Clinical Decision Engine", "status": "available"}
