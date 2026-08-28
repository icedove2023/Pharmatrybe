"""Patients capability boundary for the PharmaTrybe v1 API."""

from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/patients", tags=["patients"])


@router.get("", summary="Patients service status")
async def patients_status() -> dict[str, str]:
    """Report that longitudinal patient-directory storage is not exposed."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Longitudinal patient directory and history are not exposed; use clinical cases.",
    )
