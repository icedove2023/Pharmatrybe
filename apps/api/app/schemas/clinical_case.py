"""Pydantic schemas for the PharmaTrybe Clinical Case resource.

These schemas define the request and response contracts for the clinical case
resource without introducing any persistence, service, or endpoint logic.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, UUID4

from app.schemas.api_response import ApiMetadata, ApiSuccess


class Sex(str, Enum):
    """Allowed sex values for a clinical case."""

    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class Severity(str, Enum):
    """Allowed clinical severity values."""

    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"


class Acquisition(str, Enum):
    """Allowed acquisition settings for the case."""

    COMMUNITY = "community"
    HOSPITAL = "hospital"
    ICU = "icu"


class ResistanceStatus(str, Enum):
    """Allowed orchestration resistance status values."""

    NONE = "none"
    PREDICTED = "predicted"
    CONFIRMED = "confirmed"


class ClinicalCaseDemographics(BaseModel):
    """Demographic details for the clinical case."""

    model_config = ConfigDict(extra="forbid")

    age: int = Field(..., ge=0, le=120, description="Patient age in years")
    sex: Sex = Field(..., description="Biological sex for the patient")
    weight: float | None = Field(default=None, gt=0, description="Weight in kilograms")
    pregnancy_status: bool | None = Field(default=None, description="Whether the patient is pregnant")
    ethnicity: str | None = Field(default=None, description="Optional ethnicity field")


class ClinicalCasePresentation(BaseModel):
    """Clinical presentation details for the case."""

    model_config = ConfigDict(extra="forbid")

    syndrome: str = Field(..., min_length=1, description="Clinical syndrome being assessed")
    severity: Severity = Field(..., description="Current severity category")
    acquisition: Acquisition = Field(..., description="Setting in which the infection was acquired")
    symptoms: list[str] = Field(default_factory=list, description="Observed symptoms")
    duration_days: int | None = Field(default=None, ge=0, description="Duration of symptoms in days")


class ClinicalCaseRiskFactors(BaseModel):
    """Clinical risk factors relevant to the case."""

    model_config = ConfigDict(extra="forbid")

    allergy_beta_lactam: bool | None = Field(default=None)
    allergy_macrolide: bool | None = Field(default=None)
    renal_impairment: bool | None = Field(default=None)
    hepatic_impairment: bool | None = Field(default=None)
    immunocompromised: bool | None = Field(default=None)
    pregnancy: bool | None = Field(default=None)


class ClinicalCaseLaboratory(BaseModel):
    """Clinical laboratory information available at initial assessment."""

    model_config = ConfigDict(extra="forbid")

    culture_available: bool | None = Field(default=None)
    specimen_type: str | None = Field(default=None, min_length=1)
    organism: str | None = Field(default=None, min_length=1)
    susceptibility_available: bool | None = Field(default=None)


class ClinicalCaseSoarInputs(BaseModel):
    """SOAR/GSK-oriented clinical inputs."""

    model_config = ConfigDict(extra="forbid")

    respiratory_diagnosis: str | None = Field(default=None, min_length=1)
    curb65: int | None = Field(default=None, ge=0)
    qsofa: int | None = Field(default=None, ge=0)
    oxygen_requirement: bool | None = Field(default=None)
    previous_respiratory_infection: bool | None = Field(default=None)


class ClinicalCaseArmdInputs(BaseModel):
    """ARMD-oriented clinical inputs."""

    model_config = ConfigDict(extra="forbid")

    previous_antibiotics: list[str] = Field(default_factory=list)
    antibiotic_classes: list[str] = Field(default_factory=list)
    previous_mdro: bool | None = Field(default=None)
    previous_organisms: list[str] = Field(default_factory=list)
    previous_resistance: list[str] = Field(default_factory=list)
    icu_history: bool | None = Field(default=None)
    recent_hospitalization: bool | None = Field(default=None)
    recent_procedure: bool | None = Field(default=None)
    urinary_catheter: bool | None = Field(default=None)
    central_line: bool | None = Field(default=None)
    nursing_home: bool | None = Field(default=None)


class ClinicalCaseVitals(BaseModel):
    """Routine vital signs for the case."""

    model_config = ConfigDict(extra="forbid")

    temperature: float | None = Field(default=None)
    heart_rate: int | None = Field(default=None, ge=0)
    respiratory_rate: int | None = Field(default=None, ge=0)
    systolic_bp: int | None = Field(default=None, ge=0)
    diastolic_bp: int | None = Field(default=None, ge=0)
    oxygen_saturation: float | None = Field(default=None, ge=0)


class ClinicalCaseBiomarkers(BaseModel):
    """Laboratory biomarker values for the case."""

    model_config = ConfigDict(extra="forbid")

    wbc: float | None = Field(default=None)
    neutrophils: float | None = Field(default=None)
    lymphocytes: float | None = Field(default=None)
    creatinine: float | None = Field(default=None)
    bun: float | None = Field(default=None)
    lactate: float | None = Field(default=None)
    procalcitonin: float | None = Field(default=None)
    crp: float | None = Field(default=None)


class ClinicalCaseUserMetadata(BaseModel):
    """Metadata describing the clinician and location that initiated the case."""

    model_config = ConfigDict(extra="forbid")

    clinician_id: str | None = Field(default=None, min_length=1)
    facility_id: str | None = Field(default=None, min_length=1)
    department: str | None = Field(default=None, min_length=1)
    country: str | None = Field(default=None, min_length=1)


class ClinicalCaseRoutingMetadata(BaseModel):
    """Routing flags for downstream services."""

    model_config = ConfigDict(extra="forbid")

    use_soar: bool = Field(default=True)
    use_armd: bool = Field(default=True)
    use_who: bool = Field(default=True)


class ClinicalCaseRequest(BaseModel):
    """Request payload for a clinical case resource."""

    model_config = ConfigDict(extra="forbid")

    request_id: UUID4 = Field(..., description="Unique request identifier")
    case_id: UUID4 = Field(..., description="Unique clinical case identifier")
    timestamp: datetime = Field(..., description="Request creation timestamp")
    schema_version: str = Field(default="1.0.0", min_length=1, description="Clinical schema version")
    demographics: ClinicalCaseDemographics = Field(..., description="Patient demographic information")
    presentation: ClinicalCasePresentation = Field(..., description="Clinical presentation details")
    risk_factors: ClinicalCaseRiskFactors | None = Field(default=None, description="Relevant clinical risk factors")
    laboratory: ClinicalCaseLaboratory | None = Field(default=None, description="Initial laboratory information")
    soar_inputs: ClinicalCaseSoarInputs | None = Field(default=None, description="SOAR/GSK-oriented inputs")
    armd_inputs: ClinicalCaseArmdInputs | None = Field(default=None, description="ARMD-oriented inputs")
    vitals: ClinicalCaseVitals | None = Field(default=None, description="Routine vital signs")
    biomarkers: ClinicalCaseBiomarkers | None = Field(default=None, description="Laboratory biomarker values")
    user_metadata: ClinicalCaseUserMetadata | None = Field(default=None, description="User and facility metadata")
    routing_metadata: ClinicalCaseRoutingMetadata | None = Field(default=None, description="Service routing metadata")
    resistance_status: ResistanceStatus = Field(..., description="Orchestration switch for resistance handling")


class ClinicalCaseResource(BaseModel):
    """Clinical case payload returned in a PharmaTrybe API response."""

    model_config = ConfigDict(extra="forbid")

    clinical_case: ClinicalCaseRequest = Field(..., description="The clinical case payload")
    status: str = Field(default="received", description="Processing status for the resource")


class ClinicalCaseResponse(ApiSuccess[ClinicalCaseResource]):
    """Standard response envelope for the clinical case resource."""

    pass
