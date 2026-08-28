"""Phase 6.1 Explainability Enhancements — Structured Evidence Provider.

Extends the Explainability Engine to provide structured evidence from all sources
in a transparent, auditable manner.

Core Responsibilities:
- Evidence Ranking: Order evidence by importance using source confidence
- Evidence Attribution: Track exact origin of each evidence piece
- Recommendation Trace: Record structured execution steps

Non-Responsibilities (removed in refactor):
- Confidence calculation (delegated to Decision Fusion Engine)
- Timeline rendering (delegated to Audit Trail)
- Presentation concerns (ASCII diagrams, formatting)

All components consume outputs from existing architecture without modification.
No independent computation of clinical confidence or weighting schemes.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class EvidenceType(str, Enum):
    """Type of evidence contributing to recommendation."""
    PREDICTION = "prediction"              # From prediction plugin
    GUIDELINE = "guideline"                # From knowledge plugin
    CLINICAL_RULE = "clinical_rule"        # From rules engine
    STEWARDSHIP = "stewardship"            # From stewardship analysis


@dataclass
class RankedEvidence:
    """Single piece of evidence ranked by confidence and importance.
    
    Represents one evidence source with its confidence and clinical importance.
    Ranked by composite weight (confidence × clinical_importance).
    
    Attributes:
        evidence_id: Unique identifier within ranking
        evidence_type: Type of evidence (prediction, guideline, rule, stewardship)
        source_plugin: Name of plugin or component that generated this
        description: Human-readable summary
        confidence_score: Confidence in this evidence (0.0-1.0) from source
        clinical_importance: Clinical importance weight (0.0-1.0)
        rank: Position in ranked list (1 = highest weight)
        supporting_data: Structured data from source
        antibiotic_name: Which antibiotic this evidence supports (optional)
    """
    evidence_id: str
    evidence_type: EvidenceType
    source_plugin: str
    description: str
    confidence_score: float  # 0.0 to 1.0 from source
    clinical_importance: float  # 0.0 to 1.0 weight
    rank: int = 1
    supporting_data: Dict[str, Any] = field(default_factory=dict)
    antibiotic_name: Optional[str] = None

    def get_composite_weight(self) -> float:
        """Get composite weight (confidence × clinical importance)."""
        return self.confidence_score * self.clinical_importance

    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "evidence_id": self.evidence_id,
            "evidence_type": self.evidence_type.value,
            "source_plugin": self.source_plugin,
            "description": self.description,
            "confidence_score": self.confidence_score,
            "clinical_importance": self.clinical_importance,
            "rank": self.rank,
            "composite_weight": self.get_composite_weight(),
            "antibiotic_name": self.antibiotic_name,
            "supporting_data": self.supporting_data,
        }


@dataclass
class EvidenceRanking:
    """Ranked list of evidence for a recommendation.
    
    Provides transparent ranking of all evidence sources ordered by
    composite weight (confidence × clinical_importance).
    
    Attributes:
        recommendation_id: Reference to the recommendation
        patient_id: Patient identifier
        ranked_evidence: Sorted list of RankedEvidence items
        ranking_algorithm: Description of ranking method used
        timestamp: When ranking was generated
    """
    recommendation_id: str
    patient_id: str
    ranked_evidence: List[RankedEvidence] = field(default_factory=list)
    ranking_algorithm: str = "composite_weight (confidence × clinical_importance)"
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "recommendation_id": self.recommendation_id,
            "patient_id": self.patient_id,
            "ranked_evidence": [e.to_dict() for e in self.ranked_evidence],
            "ranking_algorithm": self.ranking_algorithm,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class EvidenceAttribution:
    """Structured attribution for a single piece of evidence.
    
    Records exactly where each evidence item originated from.
    Enables complete traceability without narrative explanations.
    
    Attributes:
        attribution_id: Unique identifier
        evidence_type: Type of evidence
        originating_plugin: Which plugin generated this (if from plugin)
        originating_rule: Which rule triggered (if from rules engine)
        originating_guideline: Which guideline (if from knowledge plugin)
        confidence: Confidence score (0.0-1.0) from source
        evidence_summary: Structured data from the source
        metadata: Additional attribution details
    """
    attribution_id: str
    evidence_type: EvidenceType
    originating_plugin: Optional[str] = None
    originating_rule: Optional[str] = None
    originating_guideline: Optional[str] = None
    confidence: float = 0.0
    evidence_summary: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "attribution_id": self.attribution_id,
            "evidence_type": self.evidence_type.value,
            "originating_plugin": self.originating_plugin,
            "originating_rule": self.originating_rule,
            "originating_guideline": self.originating_guideline,
            "confidence": self.confidence,
            "evidence_summary": self.evidence_summary,
            "metadata": self.metadata,
        }


@dataclass
class RecommendationTraceStep:
    """Single step in the recommendation generation process.
    
    Records execution of one phase with timing and I/O.
    Used to build complete trace of reasoning process.
    
    Attributes:
        step_number: Sequence number (1, 2, 3, ...)
        phase_name: Name of phase (e.g., 'plugin_execution')
        description: What happened in this step
        inputs: Input data to this step (structured)
        outputs: Output generated by this step (structured)
        duration_ms: How long this step took
        timestamp: When step executed
    """
    step_number: int
    phase_name: str
    description: str
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    duration_ms: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "step_number": self.step_number,
            "phase_name": self.phase_name,
            "description": self.description,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "duration_ms": self.duration_ms,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class RecommendationTrace:
    """Structured trace of recommendation generation.
    
    Records execution steps through the recommendation pipeline.
    Purely structured data — no rendering or presentation logic.
    
    Timeline details (ordering, execution event recording) are
    managed by AuditTrail, not by Explainability.
    
    Attributes:
        recommendation_id: Reference to the recommendation
        patient_id: Patient identifier
        trace_steps: Ordered list of execution steps
        total_duration_ms: Sum of all step durations
        timestamp: When trace was generated
    """
    recommendation_id: str
    patient_id: str
    trace_steps: List[RecommendationTraceStep] = field(default_factory=list)
    total_duration_ms: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "recommendation_id": self.recommendation_id,
            "patient_id": self.patient_id,
            "trace_steps": [step.to_dict() for step in self.trace_steps],
            "total_duration_ms": self.total_duration_ms,
            "timestamp": self.timestamp.isoformat(),
        }


class EvidenceRankingEngine:
    """Engine for ranking evidence by composite weight.
    
    Takes evidence from all sources and ranks by confidence × importance.
    Used to provide transparent ranking of decision drivers.
    """

    def rank_evidence(
        self,
        recommendation_id: str,
        patient_id: str,
        prediction_evidence: List[Dict[str, Any]],
        guideline_evidence: List[Dict[str, Any]],
        rule_evidence: List[Dict[str, Any]],
        stewardship_evidence: List[Dict[str, Any]],
    ) -> EvidenceRanking:
        """Rank all evidence sources for a recommendation.
        
        Args:
            recommendation_id: Reference to recommendation
            patient_id: Patient ID
            prediction_evidence: List of prediction evidence items
            guideline_evidence: List of guideline evidence items
            rule_evidence: List of rule evidence items
            stewardship_evidence: List of stewardship evidence items
            
        Returns:
            EvidenceRanking with evidence sorted by composite weight
        """
        ranked_evidence = []

        # Process prediction evidence
        for i, evidence in enumerate(prediction_evidence):
            ranked_evidence.append(RankedEvidence(
                evidence_id=f"pred_{i}",
                evidence_type=EvidenceType.PREDICTION,
                source_plugin=evidence.get("source", "prediction_plugin"),
                description=evidence.get("description", "Prediction model output"),
                confidence_score=evidence.get("confidence", 0.5),
                clinical_importance=0.9,  # Predictions are highly important
                supporting_data=evidence,
            ))

        # Process guideline evidence
        for i, evidence in enumerate(guideline_evidence):
            ranked_evidence.append(RankedEvidence(
                evidence_id=f"guide_{i}",
                evidence_type=EvidenceType.GUIDELINE,
                source_plugin=evidence.get("source", "knowledge_plugin"),
                description=evidence.get("recommendation", "WHO/Clinical guideline"),
                confidence_score=evidence.get("evidence_level", 0.8),
                clinical_importance=0.85,  # Guidelines are important
                supporting_data=evidence,
            ))

        # Process rule evidence
        for i, evidence in enumerate(rule_evidence):
            ranked_evidence.append(RankedEvidence(
                evidence_id=f"rule_{i}",
                evidence_type=EvidenceType.CLINICAL_RULE,
                source_plugin="rules_engine",
                description=evidence.get("message", "Clinical rule evaluation"),
                confidence_score=1.0,  # Rules are deterministic
                clinical_importance=evidence.get("severity_weight", 0.7),
                supporting_data=evidence,
            ))

        # Process stewardship evidence
        for i, evidence in enumerate(stewardship_evidence):
            ranked_evidence.append(RankedEvidence(
                evidence_id=f"stew_{i}",
                evidence_type=EvidenceType.STEWARDSHIP,
                source_plugin="stewardship_engine",
                description=evidence.get("message", "Stewardship analysis"),
                confidence_score=evidence.get("confidence", 0.7),
                clinical_importance=0.6,  # Stewardship is supportive
                supporting_data=evidence,
            ))

        # Sort by composite weight
        ranked_evidence.sort(
            key=lambda x: x.get_composite_weight(),
            reverse=True
        )

        # Assign ranks
        for i, evidence in enumerate(ranked_evidence, 1):
            evidence.rank = i

        return EvidenceRanking(
            recommendation_id=recommendation_id,
            patient_id=patient_id,
            ranked_evidence=ranked_evidence,
        )


class RecommendationTraceEngine:
    """Engine for recording recommendation trace steps.
    
    Builds structured trace of recommendation generation without
    rendering or presentation logic.
    """

    def build_trace(
        self,
        recommendation_id: str,
        patient_id: str,
        trace_steps: List[Dict[str, Any]],
    ) -> RecommendationTrace:
        """Build recommendation trace from structured step data.
        
        Args:
            recommendation_id: Reference to recommendation
            patient_id: Patient ID
            trace_steps: List of step data dicts
            
        Returns:
            RecommendationTrace with structured step data
        """
        steps = []
        total_duration = 0.0

        for i, step_data in enumerate(trace_steps, 1):
            duration = step_data.get("duration_ms", 0.0)
            total_duration += duration

            step = RecommendationTraceStep(
                step_number=i,
                phase_name=step_data.get("phase_name", "unknown"),
                description=step_data.get("description", ""),
                inputs=step_data.get("inputs", {}),
                outputs=step_data.get("outputs", {}),
                duration_ms=duration,
                timestamp=step_data.get("timestamp", datetime.now(timezone.utc)),
            )
            steps.append(step)

        return RecommendationTrace(
            recommendation_id=recommendation_id,
            patient_id=patient_id,
            trace_steps=steps,
            total_duration_ms=total_duration,
        )
