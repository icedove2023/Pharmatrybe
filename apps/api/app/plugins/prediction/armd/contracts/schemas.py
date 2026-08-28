"""ARMD Plugin Request/Response Contracts.

Maps ARMD-specific API schemas to platform plugin contracts.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional
from datetime import datetime


@dataclass
class ARMDPatientData:
    """ARMD patient input format."""
    patient_id: str
    features: Dict[str, Any]
    include_explainability: bool = False


@dataclass
class ARMDPredictionResult:
    """Single antibiotic prediction."""
    antibiotic: str
    probability: float
    class_label: str
    confidence: float
    auc: Optional[float] = None
    ap: Optional[float] = None
    threshold: Optional[float] = None


@dataclass
class ARMDExplainabilityResult:
    """SHAP-based explainability."""
    antibiotic: str
    base_value: Optional[float]
    positive_drivers: List[Dict[str, Any]] = field(default_factory=list)
    negative_drivers: List[Dict[str, Any]] = field(default_factory=list)
    narrative: Optional[str] = None
    figure_paths: Dict[str, str] = field(default_factory=dict)
    confidence_indicators: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ARMDClinicalRiskProfile:
    """Clinical risk profile (ARMD-specific extension)."""
    patient_id: str
    risk_level: str  # HIGH, MEDIUM, LOW
    risk_factors: List[str] = field(default_factory=list)
    stewardship_alerts: List[str] = field(default_factory=list)
    recommendations: Dict[str, str] = field(default_factory=dict)


@dataclass
class ARMDResponse:
    """Complete ARMD prediction response."""
    patient_id: str
    predictions: List[ARMDPredictionResult] = field(default_factory=list)
    explainability: Optional[ARMDExplainabilityResult] = None
    risk_profile: Optional[ARMDClinicalRiskProfile] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    generated_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return asdict(self, dict_factory=dict)

