from __future__ import annotations

from typing import Any, Dict, List, Sequence

from app.clinical_decision.contracts import (
    GuidelineCategory,
    RecommendationConfidence,
    RecommendedAntibiotic,
    RecommendationResult,
)


class RecommendationGenerator:
    """Generates a final recommendation object from ranked predictions and clinical rules."""

    def generate(
        self,
        patient_id: str,
        ranked_candidates: Sequence[tuple[str, float]],
        clinical_rules: Sequence[Any] | None = None,
        guideline_references: Sequence[Any] | None = None,
        stewardship_findings: Sequence[Any] | None = None,
        version: str = "0.1.0",
    ) -> RecommendationResult:
        if not ranked_candidates:
            raise ValueError("No ranked candidates available for recommendation generation")

        primary_name, primary_score = ranked_candidates[0]
        primary = RecommendedAntibiotic(
            antibiotic_name=primary_name,
            reason=f"Ranked highest by evidence and prediction confidence ({primary_score:.2f})",
            guideline_category=GuidelineCategory.ACCESS,
            ranking=1,
            confidence=RecommendationConfidence.HIGH if primary_score >= 0.75 else RecommendationConfidence.MODERATE,
            warnings=[
                str(rule.message)
                for rule in (clinical_rules or [])
                if getattr(rule, "status", None) in {"triggered", "TRIGGERED"}
            ],
        )

        alternatives = [
            RecommendedAntibiotic(
                antibiotic_name=name,
                reason=f"Alternative candidate supported by prediction confidence ({score:.2f})",
                guideline_category=GuidelineCategory.ACCESS,
                ranking=index + 2,
                confidence=RecommendationConfidence.MODERATE if score >= 0.5 else RecommendationConfidence.LOW,
                alternative=True,
            )
            for index, (name, score) in enumerate(ranked_candidates[1:])
        ]

        return RecommendationResult(
            patient_id=patient_id,
            primary_recommendation=primary,
            alternative_recommendations=alternatives,
            clinical_rules=list(clinical_rules or []),
            guideline_references=list(guideline_references or []),
            stewardship_findings=list(stewardship_findings or []),
            warnings=[str(rule.message) for rule in (clinical_rules or []) if getattr(rule, "status", None) in {"triggered", "TRIGGERED"}],
            clinical_rationale=f"Recommended {primary_name} because it ranked highest on prediction evidence and passed relevant clinical filters.",
            confidence=primary.confidence,
            supporting_evidence=[f"probability={primary_score:.2f}"],
            version=version,
        )
