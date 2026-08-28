"""
Clinical Intelligence API

Version 1

Endpoints expose the validated WP4 Decision Engine.

The router performs only:

    • Validation
    • Dependency Injection
    • Response Formatting

Business logic remains inside PredictionService.
"""

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from ..schemas import (
    PredictionRequest,
    PredictionResponse,
)

from ..services import PredictionService

from .dependencies import get_prediction_service

router = APIRouter(
    prefix="/v1/armd",
    tags=["ARMD Clinical Intelligence"],
)


# --------------------------------------------------------
# Prediction Endpoint
# --------------------------------------------------------

@router.post(
    "/predict",
    response_model=PredictionResponse,
    summary="Predict antimicrobial resistance",
    description=(
        "Run the validated ARMD WP4 prediction "
        "pipeline for a patient."
    ),
)
async def predict_patient(
    request: PredictionRequest,
    service: PredictionService = Depends(
        get_prediction_service
    ),
):
    """
    Predict resistance probabilities
    for one patient.
    """

    try:

        response = service.predict(request)

        return response
    except Exception as e:
                import traceback
                traceback.print_exc()
    except FileNotFoundError as exc:
    
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    except Exception as exc:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {exc}",
        )


# --------------------------------------------------------
# Health
# --------------------------------------------------------

@router.get(
    "/health",
    summary="Service Health",
)
async def health():
    """
    Health endpoint.
    """

    return {

        "service": "ARMD Clinical Intelligence",

        "status": "healthy",

        "version": "1.0.0",

    }


# --------------------------------------------------------
# Metadata
# --------------------------------------------------------

@router.get(
    "/info",
    summary="Service Information",
)
async def info():
    """
    Basic API metadata.
    """

    return {

        "name":
            "ARMD Clinical Intelligence API",

        "engine":
            "WP4 Decision Engine",

        "api_version":
            "1.0.0",

        "prediction_type":
            "Hospital Antimicrobial Resistance",

        "architecture":
            "PharmaTrybe",

    }