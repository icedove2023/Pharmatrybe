"""Clinical Decision Intelligence Layer Contracts & Data Models.

Defines unified contracts for clinical rules, guidelines, stewardship,
decisions, and recommendations shared across the CDSS.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
from enum import Enum


class RuleSeverity(str, Enum):
    """Severity level of a clinical rule finding."""
    CRITICAL = "critical"    # Must not use these antibiotics
    HIGH = "high"            # Strong contraindication
    MEDIUM = "medium"        # Moderate concern, consider alternatives
    LOW = "low"              # Minor concern, proceed with caution
    INFO = "info"            # Informational only


class RuleStatus(str, Enum):
    """Status of a clinical rule evaluation."""
    PASSED = "passed"        # Rule evaluated, no concerns
    TRIGGERED = "triggered"  # Rule triggered, finding applies
    SKIPPED = "skipped"      # Rule not applicable (e.g., no allergy data)
    ERROR = "error"          # Rule evaluation failed


class GuidelineCategory(str, Enum):
    """Clinical guideline category (WHO AWaRe model)."""
    ACCESS = "access"        # WHO Access: first-line antibiotics
    WATCH = "watch"          # WHO Watch: reserve for specific indications
    RESERVE = "reserve"      # WHO Reserve: last-resort antibiotics


class StewardshipDecision(str, Enum):
    """Stewardship recommendation type."""
    ESCALATE = "escalate"    # Use broader spectrum
    DE_ESCALATE = "de_escalate"  # Narrow to targeted therapy
    MAINTAIN = "maintain"    # Continue current approach
    AVOID = "avoid"          # Do not use
    MONITOR = "monitor"      # Use but monitor closely


class RecommendationConfidence(str, Enum):
    """Confidence level in a recommendation."""
    VERY_HIGH = "very_high"  # >90% confidence
    HIGH = "high"            # 70-90% confidence
    MODERATE = "moderate"    # 50-70% confidence
    LOW = "low"              # 30-50% confidence
    VERY_LOW = "very_low"    # <30% confidence


@dataclass
class ClinicalRuleResult:
    """Result of evaluating a single clinical rule.
    
    Represents the outcome of one rule evaluation (e.g., allergy check,
    renal impairment adjustment, drug interaction screening).
    
    Attributes:
        rule_id: Unique identifier for the rule
        rule_name: Human-readable rule name
        status: Evaluation status (passed, triggered, skipped, error)
        severity: Severity of finding if triggered
        message: Clinician-friendly message
        affected_drugs: List of antibiotics affected by this rule
        evidence: Supporting evidence or reference
        metadata: Additional rule-specific data
        evaluated_at: When the rule was evaluated
    """
    rule_id: str
    rule_name: str
    status: RuleStatus
    severity: RuleSeverity = RuleSeverity.LOW
    message: str = ""
    affected_drugs: List[str] = field(default_factory=list)
    evidence: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    evaluated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "status": self.status.value,
            "severity": self.severity.value,
            "message": self.message,
            "affected_drugs": self.affected_drugs,
            "evidence": self.evidence,
            "metadata": self.metadata,
            "evaluated_at": self.evaluated_at.isoformat(),
        }


@dataclass
class GuidelineReference:
    """Reference to guideline evidence.
    
    Links recommendations to authoritative clinical guidelines
    (WHO, NICE, IDSA, local protocols).
    
    Attributes:
        guideline_id: Unique guideline identifier
        guideline_name: Human-readable name
        category: Guideline category (WHO AWaRe)
        recommendation: Specific recommendation text
        source: Source of guideline (WHO, NICE, IDSA, etc.)
        url: URL to full guideline
        retrieved_at: When guideline data was retrieved
    """
    guideline_id: str
    guideline_name: str
    category: GuidelineCategory
    recommendation: str
    source: str = ""
    url: Optional[str] = None
    retrieved_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "guideline_id": self.guideline_id,
            "guideline_name": self.guideline_name,
            "category": self.category.value,
            "recommendation": self.recommendation,
            "source": self.source,
            "url": self.url,
            "retrieved_at": self.retrieved_at.isoformat(),
        }


@dataclass
class StewardshipFinding:
    """Result of stewardship analysis.
    
    Evaluates antimicrobial stewardship concerns such as spectrum,
    escalation, de-escalation, duplicate coverage, etc.
    
    Attributes:
        finding_id: Unique identifier
        decision: Stewardship decision type
        severity: Severity of concern
        message: Clinician-friendly message
        supporting_evidence: List of supporting facts
        recommended_action: Specific action (e.g., de-escalate to amoxicillin)
        metadata: Additional stewardship data
    """
    finding_id: str
    decision: StewardshipDecision
    severity: RuleSeverity
    message: str
    supporting_evidence: List[str] = field(default_factory=list)
    recommended_action: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "finding_id": self.finding_id,
            "decision": self.decision.value,
            "severity": self.severity.value,
            "message": self.message,
            "supporting_evidence": self.supporting_evidence,
            "recommended_action": self.recommended_action,
            "metadata": self.metadata,
        }


@dataclass
class RecommendedAntibiotic:
    """Recommendation for a single antibiotic.
    
    Attributes:
        antibiotic_name: Name of the antibiotic
        reason: Why this antibiotic is recommended
        guideline_category: WHO AWaRe category
        ranking: Position in recommendation list (1 = most recommended)
        confidence: Confidence level in recommendation
        alternative: Whether this is an alternative recommendation
        warnings: List of warnings (allergies, contraindications, etc.)
        dosage_notes: Dosage adjustment notes if needed
        duration_notes: Duration recommendation notes
    """
    antibiotic_name: str
    reason: str
    guideline_category: GuidelineCategory
    ranking: int = 1
    confidence: RecommendationConfidence = RecommendationConfidence.HIGH
    alternative: bool = False
    warnings: List[str] = field(default_factory=list)
    dosage_notes: Optional[str] = None
    duration_notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "antibiotic_name": self.antibiotic_name,
            "reason": self.reason,
            "guideline_category": self.guideline_category.value,
            "ranking": self.ranking,
            "confidence": self.confidence.value,
            "alternative": self.alternative,
            "warnings": self.warnings,
            "dosage_notes": self.dosage_notes,
            "duration_notes": self.duration_notes,
        }


@dataclass
class RecommendationResult:
    """Final clinical recommendation for a patient.
    
    Combines evidence from all sources (prediction, rules, guidelines,
    stewardship) into a single clinician-facing recommendation.
    
    Attributes:
        patient_id: Patient identifier
        primary_recommendation: Top-ranked antibiotic recommendation
        alternative_recommendations: Secondary recommendations
        clinical_rules: Rules that affected the recommendation
        guideline_references: Guidelines used
        stewardship_findings: Stewardship analysis results
        warnings: Critical warnings (allergies, contraindications)
        clinical_rationale: Narrative explanation
        confidence: Overall confidence in recommendation
        supporting_evidence: List of supporting evidence items
        generated_at: When recommendation was generated
        version: Recommendation version/model version
    """
    patient_id: str
    primary_recommendation: RecommendedAntibiotic
    alternative_recommendations: List[RecommendedAntibiotic] = field(default_factory=list)
    clinical_rules: List[ClinicalRuleResult] = field(default_factory=list)
    guideline_references: List[GuidelineReference] = field(default_factory=list)
    stewardship_findings: List[StewardshipFinding] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    clinical_rationale: str = ""
    confidence: RecommendationConfidence = RecommendationConfidence.HIGH
    supporting_evidence: List[str] = field(default_factory=list)
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    version: str = "0.1.0"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "patient_id": self.patient_id,
            "primary_recommendation": self.primary_recommendation.to_dict(),
            "alternative_recommendations": [r.to_dict() for r in self.alternative_recommendations],
            "clinical_rules": [r.to_dict() for r in self.clinical_rules],
            "guideline_references": [g.to_dict() for g in self.guideline_references],
            "stewardship_findings": [s.to_dict() for s in self.stewardship_findings],
            "warnings": self.warnings,
            "clinical_rationale": self.clinical_rationale,
            "confidence": self.confidence.value,
            "supporting_evidence": self.supporting_evidence,
            "generated_at": self.generated_at.isoformat(),
            "version": self.version,
        }


@dataclass
class ExplainabilityDriver:
    """Single feature contribution to explainability.
    
    Similar to SHAP drivers but encompasses all evidence types:
    prediction SHAP, rules, guidelines, stewardship.
    
    Attributes:
        evidence_type: Type of evidence (prediction, rule, guideline, stewardship)
        source: Source of the evidence
        contribution: How this evidence supports/opposes recommendation
        weight: Relative weight of this evidence
        explanation: Human-readable explanation
    """
    evidence_type: str  # 'prediction', 'rule', 'guideline', 'stewardship'
    source: str
    contribution: str  # 'supports', 'opposes', 'neutral'
    weight: float = 1.0
    explanation: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "evidence_type": self.evidence_type,
            "source": self.source,
            "contribution": self.contribution,
            "weight": self.weight,
            "explanation": self.explanation,
        }


@dataclass
class RecommendationExplanation:
    """Complete explanation for a clinical recommendation.
    
    Merges all evidence sources into a unified, auditable explanation
    that clinicians can review and understand.
    
    Attributes:
        recommendation_id: Reference to the recommendation
        patient_id: Patient identifier
        primary_antibiotic: Name of primary recommendation
        prediction_explanation: SHAP/ML model explanation
        rule_explanations: Which rules fired and how they affected decision
        guideline_explanations: Relevant guideline evidence
        stewardship_explanations: Stewardship rationale
        evidence_drivers: Ranked list of evidence sources
        warnings: Critical warnings in explainability context
        clinical_narrative: Clinician-friendly narrative
        generated_at: When explanation was generated
    """
    recommendation_id: str
    patient_id: str
    primary_antibiotic: str
    prediction_explanation: Dict[str, Any] = field(default_factory=dict)
    rule_explanations: List[str] = field(default_factory=list)
    guideline_explanations: List[str] = field(default_factory=list)
    stewardship_explanations: List[str] = field(default_factory=list)
    evidence_drivers: List[ExplainabilityDriver] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    clinical_narrative: str = ""
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "recommendation_id": self.recommendation_id,
            "patient_id": self.patient_id,
            "primary_antibiotic": self.primary_antibiotic,
            "prediction_explanation": self.prediction_explanation,
            "rule_explanations": self.rule_explanations,
            "guideline_explanations": self.guideline_explanations,
            "stewardship_explanations": self.stewardship_explanations,
            "evidence_drivers": [d.to_dict() for d in self.evidence_drivers],
            "warnings": self.warnings,
            "clinical_narrative": self.clinical_narrative,
            "generated_at": self.generated_at.isoformat(),
        }


@dataclass
class AuditTrail:
    """Complete traceability for a recommendation.
    
    Records all components used to generate a recommendation for
    reproducibility and accountability.
    
    Attributes:
        recommendation_id: Unique identifier for this recommendation
        patient_id: Patient identifier
        timestamp: When recommendation was generated
        prediction_plugin_version: SOAR/ARMD version used
        model_versions: Specific model versions
        rule_versions: Clinical rules engine version
        guideline_engine_version: Guideline engine version
        stewardship_engine_version: Stewardship engine version
        cdss_version: Clinical Decision Support System version
        algorithm_version: Overall algorithm version
        trace_id: Distributed trace ID for logging
        metadata: Additional audit metadata
    """
    recommendation_id: str
    patient_id: str
    timestamp: datetime
    prediction_plugin_version: str
    model_versions: Dict[str, str] = field(default_factory=dict)
    rule_versions: str = ""
    guideline_engine_version: str = ""
    stewardship_engine_version: str = ""
    cdss_version: str = "0.1.0"
    algorithm_version: str = "0.1.0"
    trace_id: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "recommendation_id": self.recommendation_id,
            "patient_id": self.patient_id,
            "timestamp": self.timestamp.isoformat(),
            "prediction_plugin_version": self.prediction_plugin_version,
            "model_versions": self.model_versions,
            "rule_versions": self.rule_versions,
            "guideline_engine_version": self.guideline_engine_version,
            "stewardship_engine_version": self.stewardship_engine_version,
            "cdss_version": self.cdss_version,
            "algorithm_version": self.algorithm_version,
            "trace_id": self.trace_id,
            "metadata": self.metadata,
        }
