"""Explainability Engine.

Merges evidence from all sources into unified, auditable explanations.

Sources:
- SHAP outputs from prediction plugins
- Clinical rule results
- Guideline evidence
- Stewardship findings
- Patient-specific clinical factors

Phase 6.1 Enhancement (Refactored):
- Evidence Ranking: Rank evidence by confidence × importance
- Recommendation Trace: Record structured execution steps
- Evidence Attribution: Track exact origin of evidence

Note: Confidence calculation is delegated to Decision Fusion Engine.
Timeline rendering is delegated to Audit Trail.
Explainability Engine is a pure structured data provider, not a
calculator or renderer.
"""

from typing import Any, Dict, List, Optional
import logging
from datetime import datetime, timezone

from .contracts import (
    RecommendationExplanation, RecommendationResult, ExplainabilityDriver,
    AuditTrail
)
from .explainability_enhancements import (
    EvidenceRankingEngine, RecommendationTraceEngine,
    EvidenceRanking, RecommendationTrace, EvidenceAttribution, EvidenceType
)

logger = logging.getLogger(__name__)


class ExplainabilityEngine:
    """Engine for generating unified explanations.
    
    Responsible for:
    - Merging evidence outputs with clinical findings
    - Building coherent narratives
    - Providing structured evidence for ranking
    - Creating audit trails
    - Generating clinician-friendly explanations
    
    Phase 6.1 Methods (Refactored):
    - generate_evidence_ranking() — Rank evidence by composite weight
    - generate_recommendation_trace() — Structured execution trace
    - generate_evidence_attribution() — Track evidence sources
    
    Non-Responsibility: Confidence calculation.
    The Decision Fusion Engine produces recommendation confidence.
    Explainability consumes and exposes it via attribution, never computes it.
    """

    def __init__(self):
        """Initialize explainability engine."""
        self.logger = logging.getLogger(__name__)
        self.evidence_ranking_engine = EvidenceRankingEngine()
        self.trace_engine = RecommendationTraceEngine()

    def generate_explanation(
        self,
        recommendation: RecommendationResult,
        prediction_explanation: Optional[Dict[str, Any]] = None,
        trace_id: str = "",
    ) -> RecommendationExplanation:
        """Generate unified explanation for a recommendation.
        
        Args:
            recommendation: RecommendationResult to explain
            prediction_explanation: SHAP or other prediction explanation
            trace_id: Distributed trace ID for audit
            
        Returns:
            RecommendationExplanation with merged evidence
        """
        try:
            self.logger.info(
                "Generating explanation",
                extra={
                    "patient_id": recommendation.patient_id,
                    "primary_recommendation": recommendation.primary_recommendation.antibiotic_name
                }
            )
            
            # Build explanations from each source
            rule_explanations = self._build_rule_explanations(recommendation.clinical_rules)
            guideline_explanations = self._build_guideline_explanations(
                recommendation.guideline_references,
                recommendation.primary_recommendation.antibiotic_name
            )
            stewardship_explanations = self._build_stewardship_explanations(
                recommendation.stewardship_findings
            )
            
            # Build evidence drivers (ranked evidence)
            evidence_drivers = self._build_evidence_drivers(
                recommendation,
                prediction_explanation,
                rule_explanations,
                guideline_explanations,
                stewardship_explanations
            )
            
            # Sort by weight (importance)
            evidence_drivers.sort(key=lambda x: x.weight, reverse=True)
            
            # Generate clinical narrative
            clinical_narrative = self._build_clinical_narrative(
                recommendation,
                rule_explanations,
                stewardship_explanations,
                guideline_explanations
            )
            
            # Create explanation object
            explanation = RecommendationExplanation(
                recommendation_id=self._generate_recommendation_id(recommendation),
                patient_id=recommendation.patient_id,
                primary_antibiotic=recommendation.primary_recommendation.antibiotic_name,
                prediction_explanation=prediction_explanation or {},
                rule_explanations=rule_explanations,
                guideline_explanations=guideline_explanations,
                stewardship_explanations=stewardship_explanations,
                evidence_drivers=evidence_drivers,
                warnings=recommendation.warnings,
                clinical_narrative=clinical_narrative,
            )
            
            self.logger.info(
                "Explanation generated",
                extra={
                    "patient_id": recommendation.patient_id,
                    "evidence_drivers_count": len(evidence_drivers)
                }
            )
            
            return explanation
            
        except Exception as e:
            self.logger.error(f"Explanation generation failed: {e}", exc_info=True)
            raise

    def generate_audit_trail(
        self,
        recommendation: RecommendationResult,
        prediction_plugin_version: str,
        model_versions: Dict[str, str],
        trace_id: str = "",
    ) -> AuditTrail:
        """Generate audit trail for recommendation.
        
        Args:
            recommendation: RecommendationResult
            prediction_plugin_version: SOAR/ARMD version
            model_versions: Individual model versions
            trace_id: Distributed trace ID
            
        Returns:
            AuditTrail for reproducibility
        """
        return AuditTrail(
            recommendation_id=self._generate_recommendation_id(recommendation),
            patient_id=recommendation.patient_id,
            timestamp=recommendation.generated_at,
            prediction_plugin_version=prediction_plugin_version,
            model_versions=model_versions,
            rule_versions="0.1.0",  # Clinical rules version
            guideline_engine_version="0.1.0",
            stewardship_engine_version="0.1.0",
            cdss_version="0.1.0",
            algorithm_version=recommendation.version,
            trace_id=trace_id,
            metadata={
                "primary_recommendation": recommendation.primary_recommendation.antibiotic_name,
                "confidence": recommendation.confidence.value,
                "alternatives_count": len(recommendation.alternative_recommendations),
                "rules_triggered": len([r for r in recommendation.clinical_rules 
                                       if r.status.value == "triggered"]),
                "warnings_count": len(recommendation.warnings),
            }
        )

    # ========================================================================
    # Phase 6.1: Explainability Enhancement Methods
    # ========================================================================

    def generate_evidence_ranking(
        self,
        recommendation: Optional[RecommendationResult],
        recommendation_id: str,
        prediction_evidence: Optional[List[Dict[str, Any]]] = None,
        guideline_evidence: Optional[List[Dict[str, Any]]] = None,
        rule_evidence: Optional[List[Dict[str, Any]]] = None,
        stewardship_evidence: Optional[List[Dict[str, Any]]] = None,
        patient_id: Optional[str] = None,
    ) -> EvidenceRanking:
        """Generate ranked list of evidence by confidence and importance.
        
        Phase 6.1: Evidence Ranking
        
        Orders all evidence (prediction, guideline, rule, stewardship) by
        composite weight (confidence × clinical importance), providing
        transparent ranking of decision drivers.
        
        Args:
            recommendation: RecommendationResult to analyze (optional for API usage)
            recommendation_id: Unique recommendation identifier
            prediction_evidence: Evidence from prediction plugins
            guideline_evidence: Evidence from knowledge plugins
            rule_evidence: Evidence from clinical rules engine
            stewardship_evidence: Evidence from stewardship analysis
            
        Returns:
            EvidenceRanking with sorted evidence by importance
        """
        try:
            pid = patient_id or (recommendation.patient_id if recommendation else "unknown")
            self.logger.info(
                "Generating evidence ranking",
                extra={"patient_id": pid}
            )

            ranking = self.evidence_ranking_engine.rank_evidence(
                recommendation_id=recommendation_id,
                patient_id=pid,
                prediction_evidence=prediction_evidence or [],
                guideline_evidence=guideline_evidence or [],
                rule_evidence=rule_evidence or [],
                stewardship_evidence=stewardship_evidence or [],
            )

            self.logger.info(
                "Evidence ranking generated",
                extra={
                    "patient_id": pid,
                    "evidence_count": len(ranking.ranked_evidence)
                }
            )
            return ranking

        except Exception as e:
            self.logger.error(f"Evidence ranking failed: {e}", exc_info=True)
            raise

    def generate_recommendation_trace(
        self,
        recommendation: Optional[RecommendationResult],
        recommendation_id: str,
        trace_steps: Optional[List[Dict[str, Any]]] = None,
        patient_id: Optional[str] = None,
    ) -> RecommendationTrace:
        """Generate structured recommendation reasoning trace.
        
        Phase 6.1: Recommendation Trace
        
        Records execution steps through the recommendation pipeline as
        structured data. No rendering or presentation logic.
        
        Args:
            recommendation: RecommendationResult to analyze (optional for API usage)
            recommendation_id: Unique recommendation identifier
            trace_steps: Ordered steps in recommendation pipeline
            
        Returns:
            RecommendationTrace with structured step data
        """
        try:
            pid = patient_id or (recommendation.patient_id if recommendation else "unknown")
            self.logger.info(
                "Generating recommendation trace",
                extra={"patient_id": pid}
            )

            trace = self.trace_engine.build_trace(
                recommendation_id=recommendation_id,
                patient_id=pid,
                trace_steps=trace_steps or [],
            )

            self.logger.info(
                "Recommendation trace generated",
                extra={
                    "patient_id": pid,
                    "steps": len(trace.trace_steps),
                    "total_duration_ms": trace.total_duration_ms
                }
            )
            return trace

        except Exception as e:
            self.logger.error(f"Recommendation trace failed: {e}", exc_info=True)
            raise

    def generate_evidence_attribution(
        self,
        evidence_type,  # Can be str or EvidenceType enum
        originating_plugin: Optional[str] = None,
        originating_rule: Optional[str] = None,
        originating_guideline: Optional[str] = None,
        confidence: float = 0.0,
        evidence_summary: Optional[Dict[str, Any]] = None,
    ) -> EvidenceAttribution:
        """Generate structured evidence attribution.
        
        Phase 6.1: Evidence Attribution
        
        Records exactly where each piece of evidence came from,
        ensuring complete traceability without free-text reasoning.
        
        Args:
            evidence_type: Type of evidence (prediction, guideline, rule, etc.)
            originating_plugin: Which plugin generated this evidence
            originating_rule: Which rule (if from clinical rules)
            originating_guideline: Which guideline (if from knowledge)
            confidence: Confidence in this evidence (0-1)
            evidence_summary: Structured summary of evidence
            
        Returns:
            EvidenceAttribution with source tracking
        """
        try:
            # Convert string to EvidenceType enum if needed
            if isinstance(evidence_type, str):
                try:
                    evidence_type_enum = EvidenceType[evidence_type.upper()]
                except KeyError:
                    # Fallback to PREDICTION if type not recognized
                    evidence_type_enum = EvidenceType.PREDICTION
            else:
                evidence_type_enum = evidence_type
            
            type_str = evidence_type_enum.value if hasattr(evidence_type_enum, 'value') else str(evidence_type_enum).lower()
            attribution_id = f"attr_{type_str}_{datetime.now(timezone.utc).timestamp()}"

            return EvidenceAttribution(
                attribution_id=attribution_id,
                evidence_type=evidence_type_enum,
                originating_plugin=originating_plugin,
                originating_rule=originating_rule,
                originating_guideline=originating_guideline,
                confidence=confidence,
                evidence_summary=evidence_summary or {},
            )

        except Exception as e:
            self.logger.error(f"Evidence attribution failed: {e}", exc_info=True)
            raise

    def _build_rule_explanations(self, clinical_rules: List) -> List[str]:
        """Build rule-based explanations.
        
        Args:
            clinical_rules: Clinical rule results
            
        Returns:
            List of rule explanation strings
        """
        explanations = []
        
        for rule in clinical_rules:
            if rule.status.value == "triggered":
                msg = f"{rule.rule_name}: {rule.message}"
                if rule.affected_drugs:
                    msg += f" (affected: {', '.join(rule.affected_drugs)})"
                explanations.append(msg)
        
        return explanations

    def _build_guideline_explanations(
        self,
        guidelines: List,
        primary_antibiotic: str
    ) -> List[str]:
        """Build guideline-based explanations.
        
        Args:
            guidelines: GuidelineReference objects
            primary_antibiotic: Primary recommendation
            
        Returns:
            List of guideline explanation strings
        """
        explanations = []
        
        for guideline in guidelines:
            if guideline.guideline_id.endswith(primary_antibiotic.lower()) or \
               primary_antibiotic.lower() in guideline.guideline_id:
                msg = f"{guideline.guideline_name}: {guideline.category.value} category. "
                msg += guideline.recommendation
                explanations.append(msg)
        
        return explanations

    def _build_stewardship_explanations(self, stewardship_findings: List) -> List[str]:
        """Build stewardship-based explanations.
        
        Args:
            stewardship_findings: StewardshipFinding objects
            
        Returns:
            List of stewardship explanation strings
        """
        explanations = []
        
        for finding in stewardship_findings:
            msg = f"{finding.decision.value.upper()}: {finding.message}"
            if finding.recommended_action:
                msg += f" Recommendation: {finding.recommended_action}"
            explanations.append(msg)
        
        return explanations

    def _build_evidence_drivers(
        self,
        recommendation: RecommendationResult,
        prediction_explanation: Optional[Dict[str, Any]],
        rule_explanations: List[str],
        guideline_explanations: List[str],
        stewardship_explanations: List[str],
    ) -> List[ExplainabilityDriver]:
        """Build ranked evidence drivers.
        
        Args:
            recommendation: RecommendationResult
            prediction_explanation: SHAP output
            rule_explanations: Rule explanation strings
            guideline_explanations: Guideline explanation strings
            stewardship_explanations: Stewardship explanation strings
            
        Returns:
            List of ExplainabilityDriver ranked by importance
        """
        drivers = []
        
        # Prediction drivers (highest weight)
        if prediction_explanation:
            drivers.append(ExplainabilityDriver(
                evidence_type="prediction",
                source="SOAR/ARMD",
                contribution="supports",
                weight=1.0,
                explanation="Machine learning prediction confidence"
            ))
        
        # Guideline drivers
        for i, explanation in enumerate(guideline_explanations):
            drivers.append(ExplainabilityDriver(
                evidence_type="guideline",
                source="WHO/Clinical Guidelines",
                contribution="supports",
                weight=0.8 - (i * 0.1),  # Decrease weight for secondary guidelines
                explanation=explanation
            ))
        
        # Rule drivers
        triggered_rules = [r for r in recommendation.clinical_rules 
                          if r.status.value == "triggered"]
        for rule in triggered_rules:
            contribution = "opposes" if rule.severity.value in ["critical", "high"] else "neutral"
            weight = 0.7 if rule.severity.value in ["critical", "high"] else 0.3
            
            drivers.append(ExplainabilityDriver(
                evidence_type="rule",
                source=rule.rule_name,
                contribution=contribution,
                weight=weight,
                explanation=rule.message
            ))
        
        # Stewardship drivers
        for explanation in stewardship_explanations:
            drivers.append(ExplainabilityDriver(
                evidence_type="stewardship",
                source="Antimicrobial Stewardship",
                contribution="neutral",
                weight=0.5,
                explanation=explanation
            ))
        
        return drivers

    def _build_clinical_narrative(
        self,
        recommendation: RecommendationResult,
        rule_explanations: List[str],
        stewardship_explanations: List[str],
        guideline_explanations: List[str],
    ) -> str:
        """Build clinician-friendly narrative.
        
        Args:
            recommendation: RecommendationResult
            rule_explanations: Rule explanations
            stewardship_explanations: Stewardship explanations
            guideline_explanations: Guideline explanations
            
        Returns:
            Narrative explanation string
        """
        lines = []
        
        primary = recommendation.primary_recommendation
        lines.append(f"RECOMMENDED: {primary.antibiotic_name}")
        lines.append(f"Confidence: {primary.confidence.value}")
        lines.append(f"Guideline Category: {primary.guideline_category.value}")
        lines.append("")
        
        # Clinical reasoning
        lines.append("CLINICAL REASONING:")
        lines.append(f"  • {primary.reason}")
        
        if rule_explanations:
            lines.append("")
            lines.append("Clinical Rules Affecting Recommendation:")
            for explanation in rule_explanations:
                lines.append(f"  • {explanation}")
        
        if guideline_explanations:
            lines.append("")
            lines.append("Guideline Evidence:")
            for explanation in guideline_explanations:
                lines.append(f"  • {explanation}")
        
        if stewardship_explanations:
            lines.append("")
            lines.append("Stewardship Considerations:")
            for explanation in stewardship_explanations:
                lines.append(f"  • {explanation}")
        
        if recommendation.warnings:
            lines.append("")
            lines.append("⚠️ WARNINGS:")
            for warning in recommendation.warnings:
                lines.append(f"  • {warning}")
        
        if recommendation.alternative_recommendations:
            lines.append("")
            lines.append("ALTERNATIVES:")
            for alt in recommendation.alternative_recommendations:
                lines.append(f"  • {alt.antibiotic_name} ({alt.confidence.value} confidence)")
        
        lines.append("")
        lines.append("Clinician review and judgment are essential before prescribing.")
        
        return "\n".join(lines)

    @staticmethod
    def _generate_recommendation_id(recommendation: RecommendationResult) -> str:
        """Generate unique recommendation ID.
        
        Args:
            recommendation: RecommendationResult
            
        Returns:
            Unique ID
        """
        timestamp = recommendation.generated_at.strftime("%Y%m%d%H%M%S%f")[:14]
        return f"REC-{recommendation.patient_id}-{timestamp}"
