"""PharmaTrybe Prediction Framework — Contracts & Data Models.

Defines unified data contracts for prediction requests, results, and 
model metadata shared across SOAR and ARMD prediction plugins.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from enum import Enum
import json


class PredictionStatus(str, Enum):
    """Prediction execution status."""
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"
    SKIPPED = "skipped"


class ClinicalCategory(str, Enum):
    """Clinical risk/recommendation categories (from ARMD)."""
    AVOID = "avoid"
    CAUTION = "caution"
    RECOMMENDED = "recommended"
    PREFERRED = "preferred"


@dataclass
class ModelPackage:
    """Unified representation of a loaded prediction model and its artifacts.
    
    This contract wraps both SOAR artifact-based and ARMD WP4-based models
    into a consistent interface that adapters can populate.
    
    Attributes:
        id: Deployment/model identifier (e.g., antibiotic name, model UUID)
        model: The actual model object (sklearn, XGBoost, etc.)
        scaler: Optional preprocessing scaler
        threshold: Decision threshold for binary classification
        feature_names: List of feature names expected by the model
        artifacts: Dictionary of raw artifact objects (encoder, preprocessor, metadata)
        metadata: Deployment metadata (version, AUC, confidence, etc.)
        loaded_timestamp: When the model was loaded
    """
    id: str
    model: Any
    scaler: Optional[Any] = None
    threshold: Optional[float] = None
    feature_names: List[str] = field(default_factory=list)
    artifacts: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    loaded_timestamp: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary (excluding model objects)."""
        return {
            "id": self.id,
            "threshold": self.threshold,
            "feature_names": self.feature_names,
            "metadata": self.metadata,
            "loaded_timestamp": self.loaded_timestamp.isoformat() if self.loaded_timestamp else None,
        }


@dataclass
class PredictionRequest:
    """Standard prediction request contract.
    
    Adapters convert plugin-specific request formats into this unified format.
    
    Attributes:
        patient_id: Unique patient identifier
        patient_data: Raw patient feature dictionary
        deployment_ids: Which models/deployments to use
        include_explainability: Request SHAP/explanation output
        metadata: Additional request metadata
    """
    patient_id: str
    patient_data: Dict[str, Any]
    deployment_ids: Optional[List[str]] = None
    include_explainability: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PredictionExecution:
    """Intermediate representation of executed prediction.
    
    Contains raw inference outputs before final formatting/ranking.
    
    Attributes:
        status: Execution status
        model_id: Which model was executed
        predictions: Dict of antibiotic/class -> probability
        probabilities: Raw model output probabilities
        selected_class: Top-ranked prediction
        confidence: Confidence/probability of selected class
        ranking: Ordered list of (class, probability) tuples
        error: Error message if status is FAILED
        execution_metadata: Timing, feature alignment, etc.
    """
    status: PredictionStatus
    model_id: str
    predictions: Dict[str, Any] = field(default_factory=dict)
    probabilities: Dict[str, float] = field(default_factory=dict)
    selected_class: Optional[str] = None
    confidence: Optional[float] = None
    ranking: List[tuple] = field(default_factory=list)
    error: Optional[str] = None
    execution_metadata: Dict[str, Any] = field(default_factory=dict)
    executed_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "status": self.status.value if isinstance(self.status, Enum) else self.status,
            "model_id": self.model_id,
            "predictions": self.predictions,
            "probabilities": self.probabilities,
            "selected_class": self.selected_class,
            "confidence": self.confidence,
            "ranking": self.ranking,
            "error": self.error,
            "executed_at": self.executed_at.isoformat(),
            "execution_metadata": self.execution_metadata,
        }


@dataclass
class ExplainabilityDriver:
    """A single feature contribution to prediction (from SHAP)."""
    feature_name: str
    display_name: str
    contribution: float
    feature_value: Optional[float] = None
    base_value: Optional[float] = None


@dataclass
class ExplainabilityPayload:
    """Normalized explainability output contract.
    
    Maps SHAP outputs and narrative generation into a unified format
    consumed by the Clinical Decision Engine.
    
    Attributes:
        prediction_id: Reference to the prediction
        model_id: Which model was explained
        base_value: SHAP expected value (model average)
        positive_drivers: Features that increase probability
        negative_drivers: Features that decrease probability
        figure_paths: Optional paths to SHAP visualizations
        narrative: Clinician-friendly narrative explanation
        confidence_indicators: Supporting metrics
    """
    prediction_id: str
    model_id: str
    base_value: Optional[float] = None
    positive_drivers: List[ExplainabilityDriver] = field(default_factory=list)
    negative_drivers: List[ExplainabilityDriver] = field(default_factory=list)
    figure_paths: Dict[str, str] = field(default_factory=dict)
    narrative: Optional[str] = None
    confidence_indicators: Dict[str, Any] = field(default_factory=dict)
    generated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "prediction_id": self.prediction_id,
            "model_id": self.model_id,
            "base_value": self.base_value,
            "positive_drivers": [asdict(d) for d in self.positive_drivers],
            "negative_drivers": [asdict(d) for d in self.negative_drivers],
            "figure_paths": self.figure_paths,
            "narrative": self.narrative,
            "confidence_indicators": self.confidence_indicators,
            "generated_at": self.generated_at.isoformat(),
        }


@dataclass
class RiskProfileData:
    """Clinical risk profile for a patient (ARMD domain-specific)."""
    patient_id: str
    risk_level: str  # e.g., "HIGH", "MEDIUM", "LOW"
    risk_factors: List[str] = field(default_factory=list)
    stewardship_alerts: List[str] = field(default_factory=list)
    recommendations: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    generated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PredictionResult:
    """Final prediction result contract — the API-facing response.
    
    Combines execution, explainability, risk profile, and ranking into
    the format returned to clinicians.
    
    Attributes:
        patient_id: Patient identifier
        prediction_execution: Core prediction output
        explainability: SHAP and narrative explanation
        risk_profile: Clinical risk assessment
        recommendations: Ranked antibiotics with clinical categories
        metadata: Versioning, plugin info, timing
    """
    patient_id: str
    prediction_execution: PredictionExecution
    explainability: Optional[ExplainabilityPayload] = None
    risk_profile: Optional[RiskProfileData] = None
    recommendations: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    generated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "patient_id": self.patient_id,
            "prediction_execution": self.prediction_execution.to_dict(),
            "explainability": self.explainability.to_dict() if self.explainability else None,
            "risk_profile": asdict(self.risk_profile) if self.risk_profile else None,
            "recommendations": self.recommendations,
            "metadata": self.metadata,
            "generated_at": self.generated_at.isoformat(),
        }

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=2, default=str)
