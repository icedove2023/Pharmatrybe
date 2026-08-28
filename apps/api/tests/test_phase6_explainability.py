"""Unit tests for Phase 6.1 Explainability Enhancements (Refactored).

Tests cover structured evidence provider functionality:
- Evidence Ranking
- Recommendation Trace
- Evidence Attribution

Removed (delegated to other components):
- Confidence Breakdown (delegated to Decision Fusion)
- Explainability Timeline (delegated to Audit Trail)
"""

import pytest
from datetime import datetime, timezone

from app.clinical_decision.explainability_enhancements import (
    EvidenceType, RankedEvidence, EvidenceRanking, EvidenceAttribution,
    RecommendationTraceStep, RecommendationTrace,
    EvidenceRankingEngine, RecommendationTraceEngine,
)


class TestRankedEvidence:
    """Tests for RankedEvidence class."""

    def test_ranked_evidence_creation(self):
        """Test creating a ranked evidence object."""
        evidence = RankedEvidence(
            evidence_id="pred_1",
            evidence_type=EvidenceType.PREDICTION,
            source_plugin="soar_plugin",
            description="High prediction confidence for amoxicillin",
            confidence_score=0.85,
            clinical_importance=0.9,
            rank=1,
            antibiotic_name="amoxicillin",
        )

        assert evidence.evidence_id == "pred_1"
        assert evidence.evidence_type == EvidenceType.PREDICTION
        assert evidence.source_plugin == "soar_plugin"
        assert evidence.rank == 1
        assert evidence.antibiotic_name == "amoxicillin"

    def test_ranked_evidence_composite_weight(self):
        """Test composite weight calculation."""
        evidence = RankedEvidence(
            evidence_id="test_1",
            evidence_type=EvidenceType.GUIDELINE,
            source_plugin="who",
            description="WHO guideline",
            confidence_score=0.8,
            clinical_importance=0.9,
        )

        # Expected: 0.8 * 0.9 = 0.72
        assert evidence.get_composite_weight() == pytest.approx(0.72, abs=0.01)

    def test_ranked_evidence_to_dict(self):
        """Test serialization of ranked evidence."""
        evidence = RankedEvidence(
            evidence_id="test_1",
            evidence_type=EvidenceType.CLINICAL_RULE,
            source_plugin="rules_engine",
            description="Allergy rule triggered",
            confidence_score=1.0,
            clinical_importance=0.95,
            rank=2,
        )

        result = evidence.to_dict()

        assert result["evidence_id"] == "test_1"
        assert result["evidence_type"] == "clinical_rule"
        assert result["source_plugin"] == "rules_engine"
        assert result["rank"] == 2
        assert "composite_weight" in result


class TestEvidenceRanking:
    """Tests for EvidenceRanking class."""

    def test_evidence_ranking_creation(self):
        """Test creating an evidence ranking."""
        evidence_list = [
            RankedEvidence(
                evidence_id="1",
                evidence_type=EvidenceType.PREDICTION,
                source_plugin="soar",
                description="Test",
                confidence_score=0.9,
                clinical_importance=0.9,
                rank=1,
            )
        ]

        ranking = EvidenceRanking(
            recommendation_id="rec_1",
            patient_id="pat_123",
            ranked_evidence=evidence_list,
        )

        assert ranking.recommendation_id == "rec_1"
        assert ranking.patient_id == "pat_123"
        assert len(ranking.ranked_evidence) == 1

    def test_evidence_ranking_to_dict(self):
        """Test serialization of evidence ranking."""
        evidence_list = [
            RankedEvidence(
                evidence_id="1",
                evidence_type=EvidenceType.PREDICTION,
                source_plugin="soar",
                description="Test",
                confidence_score=0.9,
                clinical_importance=0.9,
                rank=1,
            )
        ]

        ranking = EvidenceRanking(
            recommendation_id="rec_1",
            patient_id="pat_123",
            ranked_evidence=evidence_list,
        )

        result = ranking.to_dict()

        assert result["recommendation_id"] == "rec_1"
        assert result["patient_id"] == "pat_123"
        assert len(result["ranked_evidence"]) == 1
        assert "timestamp" in result


class TestEvidenceAttribution:
    """Tests for EvidenceAttribution class."""

    def test_evidence_attribution_creation(self):
        """Test creating evidence attribution."""
        attribution = EvidenceAttribution(
            attribution_id="attr_1",
            evidence_type=EvidenceType.PREDICTION,
            originating_plugin="soar_plugin",
            confidence=0.85,
            evidence_summary={"model": "SOAR", "version": "1.0"},
        )

        assert attribution.attribution_id == "attr_1"
        assert attribution.evidence_type == EvidenceType.PREDICTION
        assert attribution.originating_plugin == "soar_plugin"

    def test_evidence_attribution_to_dict(self):
        """Test serialization of evidence attribution."""
        attribution = EvidenceAttribution(
            attribution_id="attr_1",
            evidence_type=EvidenceType.GUIDELINE,
            originating_guideline="WHO_AWaRe",
            confidence=0.90,
            evidence_summary={"category": "Access", "recommendation": "First-line"},
        )

        result = attribution.to_dict()

        assert result["attribution_id"] == "attr_1"
        assert result["evidence_type"] == "guideline"
        assert result["originating_guideline"] == "WHO_AWaRe"
        assert result["confidence"] == 0.90


class TestRecommendationTraceStep:
    """Tests for RecommendationTraceStep class."""

    def test_trace_step_creation(self):
        """Test creating a recommendation trace step."""
        step = RecommendationTraceStep(
            step_number=1,
            phase_name="plugin_execution",
            description="Executed prediction plugins",
            duration_ms=150.5,
        )

        assert step.step_number == 1
        assert step.phase_name == "plugin_execution"
        assert step.duration_ms == 150.5

    def test_trace_step_to_dict(self):
        """Test serialization of trace step."""
        step = RecommendationTraceStep(
            step_number=3,
            phase_name="rule_evaluation",
            description="Evaluated clinical rules",
            inputs={"rule_count": 5},
            outputs={"triggered_rules": 2},
            duration_ms=50.0,
        )

        result = step.to_dict()

        assert result["step_number"] == 3
        assert result["phase_name"] == "rule_evaluation"
        assert result["inputs"]["rule_count"] == 5
        assert result["outputs"]["triggered_rules"] == 2


class TestRecommendationTrace:
    """Tests for RecommendationTrace class."""

    def test_recommendation_trace_creation(self):
        """Test creating a recommendation trace."""
        steps = [
            RecommendationTraceStep(
                step_number=1,
                phase_name="plugin_execution",
                description="Step 1",
                duration_ms=100.0,
            ),
            RecommendationTraceStep(
                step_number=2,
                phase_name="decision_fusion",
                description="Step 2",
                duration_ms=50.0,
            ),
        ]

        trace = RecommendationTrace(
            recommendation_id="rec_1",
            patient_id="pat_123",
            trace_steps=steps,
            total_duration_ms=150.0,
        )

        assert trace.recommendation_id == "rec_1"
        assert len(trace.trace_steps) == 2
        assert trace.total_duration_ms == 150.0

    def test_recommendation_trace_to_dict(self):
        """Test serialization of recommendation trace."""
        steps = [
            RecommendationTraceStep(
                step_number=1,
                phase_name="plugin_execution",
                description="Plugins executed",
                duration_ms=100.0,
            ),
        ]

        trace = RecommendationTrace(
            recommendation_id="rec_1",
            patient_id="pat_123",
            trace_steps=steps,
            total_duration_ms=100.0,
        )

        result = trace.to_dict()

        assert result["recommendation_id"] == "rec_1"
        assert len(result["trace_steps"]) == 1
        assert result["total_duration_ms"] == 100.0


class TestEvidenceRankingEngine:
    """Tests for EvidenceRankingEngine."""

    def test_ranking_evidence(self):
        """Test ranking evidence from multiple sources."""
        engine = EvidenceRankingEngine()

        prediction_evidence = [
            {"description": "High prediction", "confidence": 0.9, "source": "soar"}
        ]
        guideline_evidence = [
            {"recommendation": "WHO first-line", "evidence_level": 0.8}
        ]

        ranking = engine.rank_evidence(
            recommendation_id="rec_1",
            patient_id="pat_123",
            prediction_evidence=prediction_evidence,
            guideline_evidence=guideline_evidence,
            rule_evidence=[],
            stewardship_evidence=[],
        )

        assert ranking.recommendation_id == "rec_1"
        assert len(ranking.ranked_evidence) == 2
        # Verify ranking is sorted
        assert ranking.ranked_evidence[0].rank == 1
        assert ranking.ranked_evidence[1].rank == 2

    def test_ranking_sorts_by_weight(self):
        """Test that evidence is ranked by composite weight."""
        engine = EvidenceRankingEngine()

        # High confidence, high importance = high weight
        prediction_evidence = [
            {"description": "High pred", "confidence": 0.9, "source": "soar"}
        ]
        # Lower confidence guideline
        guideline_evidence = [
            {"recommendation": "Low guide", "evidence_level": 0.5}
        ]

        ranking = engine.rank_evidence(
            recommendation_id="rec_1",
            patient_id="pat_123",
            prediction_evidence=prediction_evidence,
            guideline_evidence=guideline_evidence,
            rule_evidence=[],
            stewardship_evidence=[],
        )

        # Prediction should rank higher
        assert ranking.ranked_evidence[0].evidence_type == EvidenceType.PREDICTION


class TestRecommendationTraceEngine:
    """Tests for RecommendationTraceEngine."""

    def test_build_trace(self):
        """Test building a recommendation trace."""
        engine = RecommendationTraceEngine()

        trace_steps = [
            {
                "phase_name": "plugin_execution",
                "description": "Executed plugins",
                "duration_ms": 100.0,
                "inputs": {"request": "input"},
                "outputs": {"predictions": []},
            },
            {
                "phase_name": "decision_fusion",
                "description": "Fused evidence",
                "duration_ms": 50.0,
                "inputs": {"evidence": []},
                "outputs": {"recommendation": "test"},
            },
        ]

        trace = engine.build_trace(
            recommendation_id="rec_1",
            patient_id="pat_123",
            trace_steps=trace_steps,
        )

        assert trace.recommendation_id == "rec_1"
        assert len(trace.trace_steps) == 2
        # Total duration = 100 + 50 = 150
        assert trace.total_duration_ms == pytest.approx(150.0, abs=0.01)


class TestPhase6Integration:
    """Integration tests for Phase 6.1 components."""

    def test_full_evidence_flow(self):
        """Test complete evidence flow from ranking to attribution."""
        ranking_engine = EvidenceRankingEngine()

        # Create evidence
        prediction_evidence = [
            {"description": "Prediction", "confidence": 0.85, "source": "soar"}
        ]
        guideline_evidence = [
            {"recommendation": "WHO", "evidence_level": 0.80}
        ]

        # Rank evidence
        ranking = ranking_engine.rank_evidence(
            recommendation_id="rec_1",
            patient_id="pat_123",
            prediction_evidence=prediction_evidence,
            guideline_evidence=guideline_evidence,
            rule_evidence=[],
            stewardship_evidence=[],
        )

        # Verify integrated flow
        assert ranking.recommendation_id == "rec_1"
        assert len(ranking.ranked_evidence) > 0

        # Create attribution for the top evidence
        top_evidence = ranking.ranked_evidence[0]
        attribution = EvidenceAttribution(
            attribution_id="attr_1",
            evidence_type=top_evidence.evidence_type,
            originating_plugin=top_evidence.source_plugin,
            confidence=top_evidence.confidence_score,
            evidence_summary={"rank": top_evidence.rank},
        )

        assert attribution.originating_plugin == top_evidence.source_plugin


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
