"""Decision Fusion Engine.

Combines evidence from multiple sources into unified clinical recommendations.

Sources include:
- SOAR/ARMD prediction outputs
- Clinical rules (allergies, renal, pregnancy, etc.)
- Guideline evidence (WHO AWaRe)
- Stewardship analysis
- Patient-specific clinical factors

The engine synthesizes this evidence without performing prediction itself.
"""

from typing import Any, Dict, List, Optional
import logging
from datetime import datetime, timezone

from .contracts import (
    RecommendationResult, RecommendedAntibiotic, ClinicalRuleResult,
    GuidelineReference, StewardshipFinding, RecommendationConfidence,
    GuidelineCategory, RuleSeverity, RuleStatus
)
from .rules import ClinicalRulesEngine
from .guideline_engine import GuidelineEngine
from .stewardship import StewardshipEngine

logger = logging.getLogger(__name__)


class DecisionFusionEngine:
    """Fuses evidence from multiple sources into recommendations.
    
    Responsible for:
    - Receiving predictions from SOAR/ARMD
    - Evaluating clinical rules
    - Retrieving guideline evidence
    - Analyzing stewardship implications
    - Ranking recommendations based on all evidence
    - Identifying warnings and contraindications
    """

    def __init__(self):
        """Initialize decision fusion engine with sub-engines."""
        self.rules_engine = ClinicalRulesEngine()
        self.guideline_engine = GuidelineEngine()
        self.stewardship_engine = StewardshipEngine()
        self.logger = logging.getLogger(__name__)

    def fuse_decision(
        self,
        patient_id: str,
        patient_data: Dict[str, Any],
        prediction_results: Dict[str, float],  # antibiotic -> probability
        model_info: Dict[str, str],
    ) -> RecommendationResult:
        """Fuse all evidence sources into a recommendation.
        
        Args:
            patient_id: Patient identifier
            patient_data: Clinical data (allergies, renal, etc.)
            prediction_results: Antibiotic predictions from SOAR/ARMD (probabilities)
            model_info: Model version and plugin information
            
        Returns:
            RecommendationResult with fused evidence
        """
        try:
            # Extract antibiotics from predictions
            antibiotics = list(prediction_results.keys())
            
            self.logger.info(
                "Fusing decision",
                extra={"patient_id": patient_id, "antibiotic_count": len(antibiotics)}
            )
            
            # Evaluate all clinical rules
            clinical_rules = self.rules_engine.evaluate_all(patient_data, antibiotics)
            
            # Identify which antibiotics are contraindicated by rules
            contraindicated = self._identify_contraindicated(clinical_rules)
            
            # Retrieve guideline evidence
            guideline_refs = self._get_guideline_references(antibiotics)
            
            # Rank antibiotics based on evidence
            ranked = self._rank_antibiotics(
                antibiotics,
                prediction_results,
                contraindicated,
                guideline_refs,
                clinical_rules
            )
            
            if not ranked:
                # Fallback if no suitable antibiotics
                ranked = self._create_fallback_recommendation(antibiotics, contraindicated)
            
            # Primary recommendation
            primary = ranked[0] if ranked else self._create_default_recommendation(antibiotics[0])
            
            # Alternative recommendations
            alternatives = ranked[1:] if len(ranked) > 1 else []
            
            # Analyze stewardship implications
            stewardship_findings = self.stewardship_engine.analyze_stewardship(
                patient_data,
                primary.antibiotic_name,
                [a.antibiotic_name for a in alternatives]
            )
            
            # Gather warnings
            warnings = self._gather_warnings(clinical_rules, contraindicated, primary)
            
            # Build recommendation
            recommendation = RecommendationResult(
                patient_id=patient_id,
                primary_recommendation=primary,
                alternative_recommendations=alternatives,
                clinical_rules=clinical_rules,
                guideline_references=guideline_refs,
                stewardship_findings=stewardship_findings,
                warnings=warnings,
                clinical_rationale=self._build_rationale(
                    primary,
                    clinical_rules,
                    stewardship_findings,
                    model_info
                ),
                confidence=primary.confidence,
                supporting_evidence=self._gather_supporting_evidence(
                    prediction_results,
                    clinical_rules,
                    guideline_refs
                ),
                version=model_info.get("version", "0.1.0"),
            )
            
            self.logger.info(
                "Decision fusion complete",
                extra={
                    "patient_id": patient_id,
                    "primary_recommendation": primary.antibiotic_name,
                    "alternatives_count": len(alternatives),
                    "warnings_count": len(warnings)
                }
            )
            
            return recommendation
            
        except Exception as e:
            self.logger.error(f"Decision fusion failed: {e}", exc_info=True)
            raise

    def _identify_contraindicated(self, clinical_rules: List[ClinicalRuleResult]) -> set:
        """Identify antibiotics contraindicated by clinical rules.
        
        Args:
            clinical_rules: List of rule evaluation results
            
        Returns:
            Set of contraindicated antibiotic names
        """
        contraindicated = set()
        
        for rule in clinical_rules:
            # Critical/High severity triggered rules contraindicate antibiotics
            if (rule.status == RuleStatus.TRIGGERED and 
                rule.severity in [RuleSeverity.CRITICAL, RuleSeverity.HIGH]):
                contraindicated.update(rule.affected_drugs)
        
        return contraindicated

    def _get_guideline_references(self, antibiotics: List[str]) -> List[GuidelineReference]:
        """Get guideline references for antibiotics.
        
        Args:
            antibiotics: Antibiotic names
            
        Returns:
            List of GuidelineReferences
        """
        references = []
        for ab in antibiotics:
            ref = self.guideline_engine.get_guideline_by_antibiotic(ab)
            if ref:
                references.append(ref)
        return references

    def _rank_antibiotics(
        self,
        antibiotics: List[str],
        prediction_results: Dict[str, float],
        contraindicated: set,
        guidelines: List[GuidelineReference],
        rules: List[ClinicalRuleResult],
    ) -> List[RecommendedAntibiotic]:
        """Rank antibiotics based on all evidence.
        
        Ranking considers:
        1. Contraindications (exclude)
        2. Clinical rules (adjust confidence)
        3. Prediction probabilities (weight)
        4. Guideline category (prefer ACCESS > WATCH > RESERVE)
        
        Args:
            antibiotics: Candidate antibiotics
            prediction_results: Prediction probabilities
            contraindicated: Contraindicated drugs
            guidelines: Guideline references
            rules: Clinical rule results
            
        Returns:
            Ranked list of RecommendedAntibiotic
        """
        scored = []
        
        for ab in antibiotics:
            if ab in contraindicated:
                continue  # Skip contraindicated
            
            # Base score from prediction
            pred_prob = prediction_results.get(ab, 0.0)
            score = pred_prob
            
            # Guideline category bonus
            guideline = self.guideline_engine.get_guideline_by_antibiotic(ab)
            if guideline:
                if guideline.category == GuidelineCategory.ACCESS:
                    score += 0.2  # Prefer ACCESS
                elif guideline.category == GuidelineCategory.WATCH:
                    score += 0.0  # Neutral
                elif guideline.category == GuidelineCategory.RESERVE:
                    score -= 0.1  # Discourage RESERVE
            
            # Rule adjustments
            for rule in rules:
                if rule.status == RuleStatus.TRIGGERED:
                    if ab in rule.affected_drugs:
                        if rule.severity == RuleSeverity.MEDIUM:
                            score -= 0.05
                        elif rule.severity == RuleSeverity.LOW:
                            score -= 0.02
            
            scored.append((ab, score, guideline))
        
        # Sort by score descending
        scored.sort(key=lambda x: x[1], reverse=True)
        
        # Convert to RecommendedAntibiotic objects
        ranked = []
        for i, (ab, score, guideline) in enumerate(scored):
            confidence = self._score_to_confidence(score)
            reason = self._build_reason(ab, score, guideline)
            
            ranked.append(RecommendedAntibiotic(
                antibiotic_name=ab,
                reason=reason,
                guideline_category=guideline.category if guideline else GuidelineCategory.ACCESS,
                ranking=i + 1,
                confidence=confidence,
                alternative=i > 0,
            ))
        
        return ranked

    def _score_to_confidence(self, score: float) -> RecommendationConfidence:
        """Convert numeric score to confidence level.
        
        Args:
            score: Score between 0 and 1
            
        Returns:
            RecommendationConfidence level
        """
        if score >= 0.9:
            return RecommendationConfidence.VERY_HIGH
        elif score >= 0.7:
            return RecommendationConfidence.HIGH
        elif score >= 0.5:
            return RecommendationConfidence.MODERATE
        elif score >= 0.3:
            return RecommendationConfidence.LOW
        else:
            return RecommendationConfidence.VERY_LOW

    def _build_reason(
        self,
        antibiotic: str,
        score: float,
        guideline: Optional[GuidelineReference]
    ) -> str:
        """Build reason text for recommendation.
        
        Args:
            antibiotic: Antibiotic name
            score: Score value
            guideline: Guideline reference if available
            
        Returns:
            Reason text
        """
        parts = []
        
        parts.append(f"{antibiotic} is predicted to be effective")
        
        if guideline:
            if guideline.category == GuidelineCategory.ACCESS:
                parts.append("WHO Access category (first-line)")
            elif guideline.category == GuidelineCategory.WATCH:
                parts.append("WHO Watch category (reserve use)")
            elif guideline.category == GuidelineCategory.RESERVE:
                parts.append("WHO Reserve category (last-resort)")
        
        confidence_pct = int(score * 100)
        parts.append(f"({confidence_pct}% confidence)")
        
        return ". ".join(parts)

    def _create_fallback_recommendation(
        self,
        antibiotics: List[str],
        contraindicated: set
    ) -> List[RecommendedAntibiotic]:
        """Create fallback recommendation when no suitable antibiotics.
        
        Args:
            antibiotics: All candidate antibiotics
            contraindicated: Contraindicated drugs
            
        Returns:
            Fallback ranked list
        """
        self.logger.warning("All antibiotics contraindicated or unsuitable. Using fallback.")
        
        result = []
        for i, ab in enumerate(antibiotics):
            result.append(RecommendedAntibiotic(
                antibiotic_name=ab,
                reason=f"All options have contraindications. {ab} least risky.",
                guideline_category=GuidelineCategory.RESERVE,
                ranking=i + 1,
                confidence=RecommendationConfidence.LOW,
                alternative=i > 0,
                warnings=[f"Contraindications exist. Clinician review required."]
            ))
        
        return result

    def _create_default_recommendation(self, antibiotic: str) -> RecommendedAntibiotic:
        """Create default recommendation.
        
        Args:
            antibiotic: Antibiotic name
            
        Returns:
            Default RecommendedAntibiotic
        """
        return RecommendedAntibiotic(
            antibiotic_name=antibiotic,
            reason="Default recommendation",
            guideline_category=GuidelineCategory.ACCESS,
            ranking=1,
            confidence=RecommendationConfidence.MODERATE,
            alternative=False,
        )

    def _gather_warnings(
        self,
        clinical_rules: List[ClinicalRuleResult],
        contraindicated: set,
        primary: RecommendedAntibiotic
    ) -> List[str]:
        """Gather all warnings for clinician.
        
        Args:
            clinical_rules: Rule results
            contraindicated: Contraindicated drugs
            primary: Primary recommendation
            
        Returns:
            List of warning messages
        """
        warnings = []
        
        # Add contraindications as warnings
        if contraindicated:
            if primary.antibiotic_name in contraindicated:
                warnings.append(f"⚠️ {primary.antibiotic_name} has contraindications. Clinician review required.")
        
        # Add critical rule messages
        for rule in clinical_rules:
            if rule.status == RuleStatus.TRIGGERED and rule.severity == RuleSeverity.CRITICAL:
                warnings.append(f"⚠️ CRITICAL: {rule.message}")
        
        return warnings

    def _build_rationale(
        self,
        primary: RecommendedAntibiotic,
        clinical_rules: List[ClinicalRuleResult],
        stewardship_findings: List[StewardshipFinding],
        model_info: Dict[str, str],
    ) -> str:
        """Build clinical rationale narrative.
        
        Args:
            primary: Primary recommendation
            clinical_rules: Rule results
            stewardship_findings: Stewardship analysis
            model_info: Model information
            
        Returns:
            Narrative explanation
        """
        parts = []
        
        parts.append(f"Primary recommendation: {primary.antibiotic_name}")
        parts.append(f"Confidence: {primary.confidence.value}")
        parts.append(f"Guideline category: {primary.guideline_category.value}")
        
        triggered_rules = [r for r in clinical_rules if r.status == RuleStatus.TRIGGERED]
        if triggered_rules:
            parts.append(f"Clinical rules ({len(triggered_rules)} triggered):")
            for rule in triggered_rules:
                parts.append(f"  - {rule.rule_name}: {rule.message}")
        
        if stewardship_findings:
            parts.append("Stewardship considerations:")
            for finding in stewardship_findings:
                parts.append(f"  - {finding.message}")
        
        return "\n".join(parts)

    def _gather_supporting_evidence(
        self,
        prediction_results: Dict[str, float],
        clinical_rules: List[ClinicalRuleResult],
        guidelines: List[GuidelineReference],
    ) -> List[str]:
        """Gather all supporting evidence.
        
        Args:
            prediction_results: Prediction probabilities
            clinical_rules: Rule results
            guidelines: Guideline references
            
        Returns:
            List of evidence statements
        """
        evidence = []
        
        # Prediction evidence
        for ab, prob in prediction_results.items():
            evidence.append(f"Prediction: {ab} (confidence: {prob:.1%})")
        
        # Rule evidence
        for rule in clinical_rules:
            if rule.status == RuleStatus.TRIGGERED:
                evidence.append(f"Rule: {rule.rule_name} - {rule.message}")
        
        # Guideline evidence
        for guideline in guidelines:
            evidence.append(f"Guideline: {guideline.guideline_name}")
        
        return evidence
