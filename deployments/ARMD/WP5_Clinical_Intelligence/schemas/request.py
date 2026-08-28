"""
Prediction request schema.

Defines the input accepted by the Clinical
Intelligence API.
"""

from typing import Dict
from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class PredictionRequest(BaseModel):
    """
    Request body for ARMD prediction.

    Either

        patient_id

    OR

        patient_data

    may be supplied.

    If both are supplied,
    patient_data takes precedence.
    """

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "patient_id": 300712252,
                "requested_antibiotics": [
                    "Ciprofloxacin",
                    "Amikacin"
                ]
            }
        }
    )

    patient_id: Optional[int] = Field(
        default=None,
        description="Patient identifier from WP2."
    )

    patient_data: Optional[Dict] = Field(
        default=None,
        description="Optional raw patient record."
    )

    requested_antibiotics: Optional[List[str]] = Field(
        default=None,
        description="Restrict predictions to selected antibiotics."
    )