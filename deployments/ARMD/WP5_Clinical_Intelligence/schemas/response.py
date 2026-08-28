"""
Prediction response schema.
"""
from .structuredexplainability import StructuredExplainability
from datetime import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field

from .prediction import AntibioticPrediction

from .clinical_risk_profile import ClinicalRiskProfile

class PredictionResponse(BaseModel):
    """
    Standard response returned by
    the Clinical Intelligence API.
    """

    model_config = ConfigDict(extra="forbid")

    patient_id: int = Field(
        ...,
        description="Patient identifier."
    )

    generated_at: datetime = Field(
        ...,
        description="Prediction timestamp."
    )

    engine_version: str = Field(
        ...,
        description="ARMD engine version."
    )

    total_models: int = Field(
        ...,
        description="Number of antibiotic models evaluated."
    )

    predictions: List[AntibioticPrediction]

    #
    # Reserved for WP5 Module 2
    #

    explainability: Optional[StructuredExplainability] = None

    #
    # Reserved for WP5 Module 3
    #

    clinical_risk_profile: Optional[ClinicalRiskProfile] = None

    #
    # Reserved for WP5 Module 4
    #

    stewardship_summary: Optional[Dict[str, Any]] = None

    #
    # Reserved for WP5 Module 5+
    #

    audit: Optional[Dict[str, Any]] = None