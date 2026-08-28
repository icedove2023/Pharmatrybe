"""
WP5 Module 3

Clinical Risk Profile Schemas

Defines structured clinical risk information generated
from deterministic clinical rules.

These schemas contain NO machine learning logic.

They represent the clinical context accompanying an
ARMD prediction.

They are consumed by:

• Clinical Intelligence API
• Explainability Engine
• Decision Engine
• Audit Service
• Future PharmaTrybe Frontend
"""

from typing import List, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------
# Individual Risk Factor
# ---------------------------------------------------------------------
class RiskFactor(BaseModel):
    """
    Individual clinical risk factor.
    """

    factor: str
    value: str
    contribution: float
    direction: str
    
class ClinicalRiskFactor(BaseModel):
    """
    Represents one clinical factor contributing
    to the patient's overall AMR risk.
    """

    factor: str = Field(
        ...,
        description="Clinical risk factor."
    )

    status: str = Field(
        ...,
        description="Current patient status."
    )

    risk_level: str = Field(
        ...,
        description="Low / Moderate / High."
    )

    explanation: Optional[str] = Field(
        default=None,
        description="Human-readable explanation."
    )


# ---------------------------------------------------------------------
# Stewardship Alert
# ---------------------------------------------------------------------

class StewardshipAlert(BaseModel):
    """
    Stewardship message generated from the
    patient's clinical context.

    This is NOT an antibiotic recommendation.
    """

    priority: str = Field(
        ...,
        description="Routine / Review / Urgent"
    )

    message: str = Field(
        ...,
        description="Clinical stewardship message."
    )


# ---------------------------------------------------------------------
# Clinical Risk Profile
# ---------------------------------------------------------------------

class ClinicalRiskProfile(BaseModel):
    """
    Structured patient AMR risk profile.

    Generated entirely from deterministic
    clinical rules.

    No machine learning occurs here.
    """

    overall_risk: str = Field(
        ...,
        description="Overall antimicrobial resistance risk."
    )

    healthcare_exposure: str = Field(
        ...,
        description="Healthcare exposure level."
    )

    previous_antibiotic_exposure: str = Field(
        ...,
        description="Previous antibiotic exposure."
    )

    icu_exposure: str = Field(
        ...,
        description="ICU exposure status."
    )

    hospital_acquisition: str = Field(
        ...,
        description="Community / Healthcare / Hospital acquired."
    )

    recent_hospitalisation: str = Field(
        ...,
        description="Recent hospital admission."
    )

    mdr_risk: str = Field(
        ...,
        description="Likelihood of multidrug resistance."
    )

    stewardship: StewardshipAlert

    contributing_factors: List[ClinicalRiskFactor] = Field(
        default_factory=list,
        description="Clinical factors contributing to the overall risk."
    )