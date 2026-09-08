"""Unit tests for Clinical Decision Support System.

Tests cover:
- Clinical Rules Engine
- Guideline Engine
- Stewardship Engine
- Decision Fusion Engine
- Explainability Engine
- CDSS Orchestrator
"""

import pytest
from datetime import datetime, timezone
from typing import Dict, Any

# Import components (adjust paths as needed for your environment)
import sys
import os

# Add the api app to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.clinical_decision.contracts import (
    ClinicalRuleResult, RuleStatus, RuleSeverity, 
    GuidelineReference, GuidelineCategory, RecommendedAntibiotic,
    RecommendationConfidence
)


class TestClinicalRulesEngine:
    """Test suite for Clinical Rules Engine."""

    def test_allergy_rule_no_allergies(self):
        """Test allergy rule when patient has no allergies."""
        from app.clinical_decision.rules import AllergyRule
        
        rule = AllergyRule()
        patient_data = {"allergies": []}
        antibiotics = ["penicillin", "amoxicillin"]
        
        result = rule.evaluate(patient_data, antibiotics)
        
        assert result.status == RuleStatus.PASSED
        assert result.severity == RuleSeverity.INFO

    def test_allergy_rule_with_allergy(self):
        """Test allergy rule when patient has relevant allergy."""
        from app.clinical_decision.rules import AllergyRule
        
        rule = AllergyRule()
        patient_data = {"allergies": ["penicillin"]}
        antibiotics = ["amoxicillin", "cephalexin"]
        
        result = rule.evaluate(patient_data, antibiotics)
        
        assert result.status == RuleStatus.TRIGGERED
        assert result.severity == RuleSeverity.CRITICAL
        assert "amoxicillin" in result.affected_drugs

    def test_renal_impairment_rule_normal(self):
        """Test renal impairment rule with normal kidney function."""
        from app.clinical_decision.rules import RenalImpairmentRule
        
        rule = RenalImpairmentRule()
        patient_data = {"egfr": 75}
        antibiotics = ["gentamicin", "cephalexin"]
        
        result = rule.evaluate(patient_data, antibiotics)
        
        assert result.status == RuleStatus.PASSED

    def test_renal_impairment_rule_impaired(self):
        """Test renal impairment rule with impaired kidney function."""
        from app.clinical_decision.rules import RenalImpairmentRule
        
        rule = RenalImpairmentRule()
        patient_data = {"egfr": 25}
        antibiotics = ["gentamicin", "cephalexin"]
        
        result = rule.evaluate(patient_data, antibiotics)
        
        assert result.status == RuleStatus.TRIGGERED
        assert result.severity == RuleSeverity.HIGH
        assert "gentamicin" in result.affected_drugs

    def test_pregnancy_rule_not_pregnant(self):
        """Test pregnancy rule when patient not pregnant."""
        from app.clinical_decision.rules import PregnancyRule
        
        rule = PregnancyRule()
        patient_data = {"is_pregnant": False, "is_lactating": False}
        antibiotics = ["penicillin"]
        
        result = rule.evaluate(patient_data, antibiotics)
        
        assert result.status == RuleStatus.PASSED

    def test_pregnancy_rule_pregnant(self):
        """Test pregnancy rule when patient is pregnant."""
        from app.clinical_decision.rules import PregnancyRule
        
        rule = PregnancyRule()
        patient_data = {"is_pregnant": True, "is_lactating": False}
        antibiotics = ["doxycycline", "penicillin"]
        
        result = rule.evaluate(patient_data, antibiotics)
        
        assert result.status == RuleStatus.TRIGGERED
        assert result.severity == RuleSeverity.HIGH
        assert "doxycycline" in result.affected_drugs

    def test_rules_engine_evaluates_all(self):
        """Test rules engine evaluates all registered rules."""
        from app.clinical_decision.rules import ClinicalRulesEngine
        
        engine = ClinicalRulesEngine()
        patient_data = {
            "allergies": ["penicillin"],
            "egfr": 45,
            "is_pregnant": False,
            "is_lactating": False,
        }
        antibiotics = ["amoxicillin", "cephalexin", "gentamicin"]
        
        results = engine.evaluate_all(patient_data, antibiotics)
        
        # Should have evaluated at least 3 rules
        assert len(results) >= 3
        
        # At least one should be triggered (allergy rule)
        triggered = [r for r in results if r.status == RuleStatus.TRIGGERED]
        assert len(triggered) > 0


class TestGuidelineEngine:
    """Test suite for Guideline Engine."""

    def test_guideline_engine_initialization(self):
        """Test guideline engine loads guidelines."""
        from app.clinical_decision.guideline_engine import GuidelineEngine
        
        engine = GuidelineEngine()
        
        # Should have loaded placeholder guidelines
        guidelines = engine.get_all_guidelines()
        assert len(guidelines) > 0

    def test_get_guideline_by_antibiotic(self):
        """Test retrieving guideline by antibiotic name."""
        from app.clinical_decision.guideline_engine import GuidelineEngine
        
        engine = GuidelineEngine()
        guideline = engine.get_guideline_by_antibiotic("amoxicillin")
        
        assert guideline is not None
        assert "amoxicillin" in guideline.guideline_id.lower()
        assert guideline.category in [
            GuidelineCategory.ACCESS,
            GuidelineCategory.WATCH,
            GuidelineCategory.RESERVE
        ]

    def test_query_guidelines(self):
        """Test querying guidelines by text."""
        from app.clinical_decision.guideline_engine import GuidelineEngine
        
        engine = GuidelineEngine()
        results = engine.query_guidelines("WHO")
        
        assert len(results) > 0
        assert all("WHO" in g.source for g in results)


class TestStewardshipEngine:
    """Test suite for Stewardship Engine."""

    def test_stewardship_analysis_broad_spectrum(self):
        """Test stewardship analysis of broad-spectrum antibiotic."""
        from app.clinical_decision.stewardship import StewardshipEngine
        
        engine = StewardshipEngine()
        patient_data = {"severity": "low", "immunocompromised": False}
        
        findings = engine.analyze_stewardship(
            patient_data,
            "ceftazidime",
            ["cephalexin"]
        )
        
        assert len(findings) > 0
        # Should flag broad-spectrum concern
        assert any(f.finding_id == "spectrum_concern" for f in findings)

    def test_stewardship_analysis_restricted(self):
        """Test stewardship analysis of restricted antibiotic."""
        from app.clinical_decision.stewardship import StewardshipEngine
        
        engine = StewardshipEngine()
        patient_data = {"severity": "high"}
        
        findings = engine.analyze_stewardship(
            patient_data,
            "carbapenem",
            []
        )
        
        assert len(findings) > 0
        assert any(f.finding_id == "restricted_use" for f in findings)


class TestDecisionFusionEngine:
    """Test suite for Decision Fusion Engine."""

    def test_fusion_basic_recommendation(self):
        """Test basic recommendation fusion."""
        from app.clinical_decision.decision_fusion import DecisionFusionEngine
        
        engine = DecisionFusionEngine()
        patient_data = {
            "allergies": [],
            "egfr": 75,
            "is_pregnant": False,
            "is_lactating": False,
        }
        prediction_results = {
            "amoxicillin": 0.8,
            "cephalexin": 0.7,
        }
        
        recommendation = engine.fuse_decision(
            patient_id="P001",
            patient_data=patient_data,
            prediction_results=prediction_results,
            model_info={"version": "0.1.0"}
        )
        
        assert recommendation.patient_id == "P001"
        assert recommendation.primary_recommendation is not None
        assert len(recommendation.alternative_recommendations) >= 0

    def test_fusion_handles_contraindications(self):
        """Test fusion handles contraindications correctly."""
        from app.clinical_decision.decision_fusion import DecisionFusionEngine
        
        engine = DecisionFusionEngine()
        patient_data = {
            "allergies": ["penicillin"],  # Contraindication
            "egfr": 75,
            "is_pregnant": False,
            "is_lactating": False,
        }
        prediction_results = {
            "amoxicillin": 0.9,  # High confidence but contraindicated
            "cephalexin": 0.7,
        }
        
        recommendation = engine.fuse_decision(
            patient_id="P002",
            patient_data=patient_data,
            prediction_results=prediction_results,
            model_info={"version": "0.1.0"}
        )
        
        # Should prefer cephalexin over amoxicillin
        assert recommendation.primary_recommendation.antibiotic_name != "amoxicillin"


class TestExplainabilityEngine:
    """Test suite for Explainability Engine."""

    def test_generate_explanation(self):
        """Test explanation generation."""
        from app.clinical_decision.explainability import ExplainabilityEngine
        from app.clinical_decision.decision_fusion import DecisionFusionEngine
        
        fusion_engine = DecisionFusionEngine()
        explain_engine = ExplainabilityEngine()
        
        patient_data = {
            "allergies": [],
            "egfr": 75,
            "is_pregnant": False,
            "is_lactating": False,
        }
        prediction_results = {"amoxicillin": 0.8, "cephalexin": 0.7}
        
        recommendation = fusion_engine.fuse_decision(
            patient_id="P001",
            patient_data=patient_data,
            prediction_results=prediction_results,
            model_info={"version": "0.1.0"}
        )
        
        explanation = explain_engine.generate_explanation(
            recommendation,
            prediction_explanation={"feature_importance": {"organism": 0.6}}
        )
        
        assert explanation.patient_id == recommendation.patient_id
        assert explanation.primary_antibiotic is not None
        assert len(explanation.evidence_drivers) > 0

    def test_generate_audit_trail(self):
        """Test audit trail generation."""
        from app.clinical_decision.explainability import ExplainabilityEngine
        from app.clinical_decision.decision_fusion import DecisionFusionEngine
        
        fusion_engine = DecisionFusionEngine()
        explain_engine = ExplainabilityEngine()
        
        patient_data = {
            "allergies": [],
            "egfr": 75,
            "is_pregnant": False,
            "is_lactating": False,
        }
        recommendation = fusion_engine.fuse_decision(
            patient_id="P001",
            patient_data=patient_data,
            prediction_results={"amoxicillin": 0.8},
            model_info={"version": "0.1.0"}
        )
        
        audit_trail = explain_engine.generate_audit_trail(
            recommendation,
            prediction_plugin_version="0.1.0",
            model_versions={"soar": "1.0.0"}
        )
        
        assert audit_trail.patient_id == recommendation.patient_id
        assert audit_trail.prediction_plugin_version == "0.1.0"
        assert "soar" in audit_trail.model_versions


class TestCDSSOrchestrator:
    """Test suite for CDSS Orchestrator."""

    def test_orchestrator_generates_recommendation(self):
        """Test orchestrator generates complete recommendation."""
        from app.clinical_decision.orchestrator import CDSSOrchestrator
        
        orchestrator = CDSSOrchestrator()
        patient_data = {
            "allergies": [],
            "egfr": 75,
            "is_pregnant": False,
            "is_lactating": False,
        }
        
        response = orchestrator.generate_recommendation(
            patient_id="P001",
            patient_data=patient_data,
            prediction_results={"amoxicillin": 0.8, "cephalexin": 0.7},
            prediction_explanation={"feature": 0.5},
            prediction_plugin_version="0.1.0",
        )
        
        assert response["status"] == "success"
        assert "recommendation" in response
        assert "explanation" in response
        assert "audit_trail" in response

    def test_orchestrator_validates_inputs(self):
        """Test orchestrator validates input data."""
        from app.clinical_decision.orchestrator import CDSSOrchestrator
        
        orchestrator = CDSSOrchestrator()
        
        # Invalid patient ID
        response = orchestrator.generate_recommendation(
            patient_id="",
            patient_data={},
            prediction_results={"amoxicillin": 0.8},
        )
        
        assert response["status"] == "error"
        assert response["error_type"] == "validation_error"

    def test_orchestrator_handles_invalid_predictions(self):
        """Test orchestrator handles invalid prediction values."""
        from app.clinical_decision.orchestrator import CDSSOrchestrator
        
        orchestrator = CDSSOrchestrator()
        
        # Invalid probability (> 1)
        response = orchestrator.generate_recommendation(
            patient_id="P001",
            patient_data={"allergies": []},
            prediction_results={"amoxicillin": 1.5},  # Invalid
        )
        
        assert response["status"] == "error"
        assert response["error_type"] == "validation_error"


if __name__ == "__main__":
    # Run tests with pytest
    # pytest tests/test_clinical_decision.py -v
    print("Tests should be run with pytest:")
    print("  pytest apps/api/tests/test_clinical_decision.py -v")
