"""
Prediction schema.

Represents one antibiotic prediction.
"""

from typing import Optional

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class AntibioticPrediction(BaseModel):
    """
    Prediction for one antibiotic.
    """

    model_config = ConfigDict(extra="forbid")

    antibiotic: str = Field(
        ...,
        description="Antibiotic name."
    )

    probability: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Probability of resistance."
    )

    classification: str = Field(
        ...,
        description="Predicted class."
    )

    threshold: Optional[float] = Field(
        default=None,
        description="Decision threshold."
    )

    confidence: Optional[float] = Field(
        default=None,
        description="Distance from threshold."
    )

    model_auc: Optional[float] = Field(
        default=None,
        description="Validation ROC-AUC."
    )

    model_average_precision: Optional[float] = Field(
        default=None,
        description="Validation Average Precision."
    )