"""
WP5 Module 2

Structured Explainability Schemas

Defines the API objects returned by the
Explainability Service.

These schemas are independent of SHAP internals.

WP4 computes SHAP.

WP5 exposes structured clinical explanations.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class ClinicalDriver(BaseModel):
    """
    One clinical factor contributing to a prediction.
    """

    feature: str = Field(
        ...,
        description="Clinical feature name",
    )

    display_name: Optional[str] = Field(
        None,
        description="Human readable feature name",
    )

    feature_value: Optional[str] = Field(
        None,
        description="Patient value for this feature",
    )

    shap_value: float = Field(
        ...,
        description="Raw SHAP contribution",
    )

    impact: str = Field(
        ...,
        description="Increase Resistance or Decrease Resistance",
    )

    magnitude: float = Field(
        ...,
        description="Absolute SHAP magnitude",
    )


class ExplainabilityPlots(BaseModel):
    """
    Generated explainability figures.
    """

    waterfall: Optional[str] = None

    bar: Optional[str] = None

    beeswarm: Optional[str] = None

    force: Optional[str] = None


class StructuredExplainability(BaseModel):
    """
    Structured explainability object returned by WP5.

    This object is consumed by

    • Decision Engine

    • Explainability Engine

    • Audit Engine

    • Frontend

    without exposing SHAP internals.
    """

    antibiotic: str = Field(
        ...,
        description="Antibiotic being explained",
    )

    model: str = Field(
        ...,
        description="Underlying prediction model",
    )

    expected_probability: Optional[float] = Field(
        None,
        description="Baseline probability before feature contributions",
    )

    predicted_probability: float = Field(
        ...,
        description="Final predicted resistance probability",
    )

    narrative: Optional[str] = Field(
        None,
        description="Automatically generated clinical explanation",
    )

    top_positive_drivers: List[ClinicalDriver] = Field(
        default_factory=list,
        description="Clinical factors increasing resistance",
    )

    top_negative_drivers: List[ClinicalDriver] = Field(
        default_factory=list,
        description="Clinical factors decreasing resistance",
    )

    plots: ExplainabilityPlots = Field(
        default_factory=ExplainabilityPlots
    )