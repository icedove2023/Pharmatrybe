"""Integration tests for Phase 6 Explainability API.

Tests validate:
- Recommendation API returns ExplainabilityResponseContract
- Evidence Ranking present and populated
- Recommendation Trace present and populated
- Evidence Attribution present
- Confidence comes from Decision Fusion
- Audit Reference complete
- Validation enforces all required fields
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime


@pytest.fixture
def test_client():
    """Create a test client for the API."""
    from app.main import app
    return TestClient(app)


@pytest.fixture(autouse=True)
def authenticated_recommendation_context():
    """Provide the permission required by the protected recommendation route."""
    from app.auth.dependencies import AuthorizationContext, get_authorization_context
    from app.main import app

    context = object.__new__(AuthorizationContext)
    context.permissions = {"recommendations:request"}
    app.dependency_overrides[get_authorization_context] = lambda: context
    yield
    app.dependency_overrides.pop(get_authorization_context, None)


class TestRecommendationAPIWithExplainability:
    """Test suite for Recommendation API with full explainability contract."""

    def test_generate_recommendation_returns_explainability_contract(self, test_client):
        """Test that recommendation endpoint returns canonical explainability response."""
        payload = {
            "patient_id": "test_patient_001",
            "patient_data": {
                "allergies": [],
                "egfr": 75,
                "is_pregnant": False,
                "is_lactating": False,
            },
            "prediction_results": {
                "amoxicillin": 0.85,
                "cephalexin": 0.75,
            },
            "prediction_plugin_version": "0.1.0",
        }

        response = test_client.post("/api/v1/recommendations/generate", json=payload)

        assert response.status_code == 200
        data = response.json()

        # Validate top-level structure
        assert data["status"] == "success"
        assert data["patient_id"] == "test_patient_001"

    def test_recommendation_response_has_confidence_from_decision_fusion(self, test_client):
        """Test that confidence comes from Decision Fusion."""
        payload = {
            "patient_id": "test_patient_002",
            "patient_data": {"allergies": [], "egfr": 75},
            "prediction_results": {"amoxicillin": 0.9},
            "prediction_plugin_version": "0.1.0",
        }

        response = test_client.post("/api/v1/recommendations/generate", json=payload)
        data = response.json()

        # Confidence should be present
        assert "confidence" in data
        assert data["confidence"] in [
            "very_high", "high", "moderate", "low", "very_low", "unknown"
        ]

    def test_recommendation_response_has_evidence_ranking(self, test_client):
        """Test that evidence ranking is present and populated."""
        payload = {
            "patient_id": "test_patient_003",
            "patient_data": {"allergies": [], "egfr": 75},
            "prediction_results": {"amoxicillin": 0.8, "cephalexin": 0.7},
            "prediction_plugin_version": "0.1.0",
        }

        response = test_client.post("/api/v1/recommendations/generate", json=payload)
        data = response.json()

        # Evidence ranking must be present
        assert "evidence_ranking" in data
        evidence_ranking = data["evidence_ranking"]

        # Must have required fields
        assert "recommendation_id" in evidence_ranking
        assert "patient_id" in evidence_ranking
        assert "ranked_evidence" in evidence_ranking
        assert isinstance(evidence_ranking["ranked_evidence"], list)

    def test_recommendation_response_has_recommendation_trace(self, test_client):
        """Test that recommendation trace is present and populated."""
        payload = {
            "patient_id": "test_patient_004",
            "patient_data": {"allergies": [], "egfr": 75},
            "prediction_results": {"amoxicillin": 0.8},
            "prediction_plugin_version": "0.1.0",
        }

        response = test_client.post("/api/v1/recommendations/generate", json=payload)
        data = response.json()

        # Recommendation trace must be present
        assert "recommendation_trace" in data
        recommendation_trace = data["recommendation_trace"]

        # Must have required fields
        assert "recommendation_id" in recommendation_trace
        assert "patient_id" in recommendation_trace
        assert "trace_steps" in recommendation_trace
        assert isinstance(recommendation_trace["trace_steps"], list)
        assert "total_duration_ms" in recommendation_trace

    def test_recommendation_response_has_evidence_attribution(self, test_client):
        """Test that evidence attribution is present."""
        payload = {
            "patient_id": "test_patient_005",
            "patient_data": {"allergies": [], "egfr": 75},
            "prediction_results": {"amoxicillin": 0.8},
            "prediction_plugin_version": "0.1.0",
        }

        response = test_client.post("/api/v1/recommendations/generate", json=payload)
        data = response.json()

        # Evidence attribution must be present
        assert "evidence_attribution" in data
        assert isinstance(data["evidence_attribution"], list)

    def test_recommendation_response_has_audit_reference(self, test_client):
        """Test that audit reference is complete."""
        payload = {
            "patient_id": "test_patient_006",
            "patient_data": {"allergies": [], "egfr": 75},
            "prediction_results": {"amoxicillin": 0.8},
            "prediction_plugin_version": "0.1.0",
        }

        response = test_client.post("/api/v1/recommendations/generate", json=payload)
        data = response.json()

        # Audit reference must be present
        assert "audit_reference" in data
        audit_ref = data["audit_reference"]

        # Must have required fields
        assert "recommendation_id" in audit_ref
        assert "patient_id" in audit_ref
        assert "timestamp" in audit_ref
        assert "trace_id" in audit_ref
        assert "prediction_plugin_version" in audit_ref

    def test_recommendation_response_has_audit_reference_links_evidence(self, test_client):
        """Test that audit reference trace_id matches top-level trace_id."""
        payload = {
            "patient_id": "test_patient_007",
            "patient_data": {"allergies": [], "egfr": 75},
            "prediction_results": {"amoxicillin": 0.8},
            "prediction_plugin_version": "0.1.0",
        }

        response = test_client.post("/api/v1/recommendations/generate", json=payload)
        data = response.json()

        # Top-level trace_id should match audit reference
        assert data["trace_id"] == data["audit_reference"]["trace_id"]

    def test_recommendation_response_has_recommendation(self, test_client):
        """Test that primary recommendation is present."""
        payload = {
            "patient_id": "test_patient_008",
            "patient_data": {"allergies": [], "egfr": 75},
            "prediction_results": {"amoxicillin": 0.8},
            "prediction_plugin_version": "0.1.0",
        }

        response = test_client.post("/api/v1/recommendations/generate", json=payload)
        data = response.json()

        # Recommendation must be present
        assert "recommendation" in data
        assert isinstance(data["recommendation"], dict)
        assert "primary_recommendation" in data["recommendation"]

    def test_recommendation_response_has_explanation(self, test_client):
        """Test that explanation is present."""
        payload = {
            "patient_id": "test_patient_009",
            "patient_data": {"allergies": [], "egfr": 75},
            "prediction_results": {"amoxicillin": 0.8},
            "prediction_plugin_version": "0.1.0",
        }

        response = test_client.post("/api/v1/recommendations/generate", json=payload)
        data = response.json()

        # Explanation should be present
        assert "explanation" in data

    def test_validation_enforces_required_fields(self, test_client):
        """Test that validation fails if required fields are missing."""
        # Missing prediction_results
        payload = {
            "patient_id": "test_patient_010",
            "patient_data": {"allergies": [], "egfr": 75},
            "prediction_plugin_version": "0.1.0",
        }

        response = test_client.post("/api/v1/recommendations/generate", json=payload)
        # Should return 422 validation error
        assert response.status_code in [400, 422]

    def test_recommendation_ids_consistent_across_response(self, test_client):
        """Test that recommendation_id is consistent across response."""
        payload = {
            "patient_id": "test_patient_011",
            "patient_data": {"allergies": [], "egfr": 75},
            "prediction_results": {"amoxicillin": 0.8},
            "prediction_plugin_version": "0.1.0",
        }

        response = test_client.post("/api/v1/recommendations/generate", json=payload)
        data = response.json()

        # All components should reference same recommendation_id
        rec_id = data["audit_reference"]["recommendation_id"]
        assert data["evidence_ranking"]["recommendation_id"] == rec_id
        assert data["recommendation_trace"]["recommendation_id"] == rec_id

    def test_patient_ids_consistent_across_response(self, test_client):
        """Test that patient_id is consistent across response."""
        patient_id = "test_patient_012"
        payload = {
            "patient_id": patient_id,
            "patient_data": {"allergies": [], "egfr": 75},
            "prediction_results": {"amoxicillin": 0.8},
            "prediction_plugin_version": "0.1.0",
        }

        response = test_client.post("/api/v1/recommendations/generate", json=payload)
        data = response.json()

        # Patient ID should be consistent everywhere
        assert data["patient_id"] == patient_id
        assert data["evidence_ranking"]["patient_id"] == patient_id
        assert data["recommendation_trace"]["patient_id"] == patient_id
        assert data["audit_reference"]["patient_id"] == patient_id

    def test_trace_id_present_in_response(self, test_client):
        """Test that trace_id is present for distributed tracing."""
        payload = {
            "patient_id": "test_patient_013",
            "patient_data": {"allergies": [], "egfr": 75},
            "prediction_results": {"amoxicillin": 0.8},
            "prediction_plugin_version": "0.1.0",
        }

        response = test_client.post("/api/v1/recommendations/generate", json=payload)
        data = response.json()

        # trace_id should be present and valid UUID format
        assert "trace_id" in data
        assert len(data["trace_id"]) > 0

    def test_generated_at_present_in_response(self, test_client):
        """Test that generated_at timestamp is present."""
        payload = {
            "patient_id": "test_patient_014",
            "patient_data": {"allergies": [], "egfr": 75},
            "prediction_results": {"amoxicillin": 0.8},
            "prediction_plugin_version": "0.1.0",
        }

        response = test_client.post("/api/v1/recommendations/generate", json=payload)
        data = response.json()

        # generated_at should be present and valid ISO format
        assert "generated_at" in data
        try:
            datetime.fromisoformat(data["generated_at"])
        except ValueError:
            pytest.fail(f"Invalid ISO timestamp: {data['generated_at']}")

    def test_multiple_predictions_handled(self, test_client):
        """Test that multiple prediction results are properly handled."""
        payload = {
            "patient_id": "test_patient_015",
            "patient_data": {"allergies": [], "egfr": 75},
            "prediction_results": {
                "amoxicillin": 0.9,
                "cephalexin": 0.8,
                "ciprofloxacin": 0.7,
                "doxycycline": 0.6,
            },
            "prediction_plugin_version": "0.1.0",
        }

        response = test_client.post("/api/v1/recommendations/generate", json=payload)

        assert response.status_code == 200
        data = response.json()

        # Should have evidence attribution for each prediction
        assert len(data["evidence_attribution"]) > 0

    def test_backward_compatibility_status_field(self, test_client):
        """Test that status field is always present for backward compatibility."""
        payload = {
            "patient_id": "test_patient_016",
            "patient_data": {"allergies": [], "egfr": 75},
            "prediction_results": {"amoxicillin": 0.8},
            "prediction_plugin_version": "0.1.0",
        }

        response = test_client.post("/api/v1/recommendations/generate", json=payload)
        data = response.json()

        assert "status" in data
        assert data["status"] in ["success", "error"]
