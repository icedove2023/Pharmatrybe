"""Administrative capability boundary for the PharmaTrybe v1 API."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth import AuthorizationContext, require_permission

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("", summary="Administrative service status")
async def admin_status(
    _context: Annotated[AuthorizationContext, Depends(require_permission("professionals:manage"))],
) -> dict[str, str]:
    """Report that administration data endpoints are not exposed."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Administration data, audit retrieval, telemetry, and policy APIs are not exposed.",
    )
