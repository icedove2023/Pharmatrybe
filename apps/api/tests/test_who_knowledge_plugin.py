"""Tests for WHO Knowledge Plugin.

Tests focus on:
- Plugin initialization and lifecycle
- Database connection and health
- Search and query operations
- Structured output format
- Error handling and graceful degradation
"""

import os

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from app.plugins.knowledge.who_knowledge_plugin import (
    WHOKnowledgePlugin,
    WHOKnowledgeResult,
)
from app.plugins.base.plugin import PluginType, PluginMetadata


class TestWHOKnowledgePluginProperties:
    """Test WHO Plugin properties and metadata."""

    def test_plugin_id(self):
        """Test plugin ID is correct."""
        plugin = WHOKnowledgePlugin(db_session=Mock())
        assert plugin.plugin_id == "who_knowledge"

    def test_plugin_name(self):
        """Test plugin name is correct."""
        plugin = WHOKnowledgePlugin(db_session=Mock())
        assert plugin.plugin_name == "WHO Knowledge Base"

    def test_plugin_version(self):
        """Test plugin version is correct."""
        plugin = WHOKnowledgePlugin(db_session=Mock())
        assert plugin.plugin_version == "0.1.0"

    def test_plugin_type_is_knowledge(self):
        """Test plugin type is KNOWLEDGE."""
        plugin = WHOKnowledgePlugin(db_session=Mock())
        assert plugin.plugin_type == PluginType.KNOWLEDGE

    def test_plugin_description(self):
        """Test plugin has description."""
        plugin = WHOKnowledgePlugin(db_session=Mock())
        assert len(plugin.plugin_description) > 0
        assert "WHO" in plugin.plugin_description

    def test_author(self):
        """Test plugin has author."""
        plugin = WHOKnowledgePlugin(db_session=Mock())
        assert "WHO" in plugin.author

    def test_capabilities(self):
        """Test plugin exposes required capabilities."""
        plugin = WHOKnowledgePlugin(db_session=Mock())
        capabilities = plugin.capabilities
        assert "disease_guidelines" in capabilities
        assert "antibiotic_classification" in capabilities
        assert "treatment_recommendations" in capabilities

    def test_dependencies(self):
        """Test plugin declares dependencies."""
        plugin = WHOKnowledgePlugin(db_session=Mock())
        assert len(plugin.dependencies) > 0
        assert any("python" in dep.lower() for dep in plugin.dependencies)


class TestWHOKnowledgePluginLifecycle:
    """Test WHO Plugin lifecycle methods."""

    def test_initialize(self):
        """Test plugin initialization."""
        plugin = WHOKnowledgePlugin(db_session=Mock())
        plugin.initialize()
        # Should not raise
        assert plugin._initialization_time is not None

    def test_shutdown(self):
        """Test plugin shutdown."""
        session = Mock()
        plugin = WHOKnowledgePlugin(db_session=session)
        plugin.initialize()
        plugin.shutdown()
        # Should not raise
        assert plugin._repository is None

    def test_configure(self):
        """Test plugin configuration."""
        plugin = WHOKnowledgePlugin(db_session=Mock())
        config: Dict[str, Any] = {}
        plugin.configure(config)
        # Should not raise

    def test_validate_without_connection(self):
        """Test validate returns False before connect."""
        plugin = WHOKnowledgePlugin(db_session=Mock())
        plugin.initialize()
        assert plugin.validate() is False

    def test_validate_with_connection(self):
        """Test validate returns True after connect."""
        # Create mock repository and provider
        mock_repo = Mock()
        mock_provider = Mock()
        mock_provider.metadata.return_value = Mock()
        
        session = Mock()
        plugin = WHOKnowledgePlugin(db_session=session)
        plugin.initialize()
        
        # Manually set as connected for testing
        plugin._repository = mock_repo
        plugin._provider = mock_provider
        plugin._is_connected = True
        
        assert plugin.validate() is True

    def test_metadata(self):
        """Test metadata returns PluginMetadata."""
        plugin = WHOKnowledgePlugin(db_session=Mock())
        metadata = plugin.metadata()
        
        assert isinstance(metadata, PluginMetadata)
        assert metadata.plugin_id == "who_knowledge"
        assert metadata.plugin_type == PluginType.KNOWLEDGE


class TestWHOKnowledgePluginConnection:
    """Test WHO Plugin connection management."""

    def test_connect_without_session_uses_configured_who_database(self):
        """Test connect uses the explicit WHO database session by default."""
        plugin = WHOKnowledgePlugin(db_session=None)
        plugin.initialize()
        plugin.connect()
        assert plugin._is_connected is True

    @pytest.mark.skipif(
        os.getenv("RUN_WHO_DB_INTEGRATION_TESTS", "false").lower() != "true",
        reason="WHO database integration tests require an explicitly enabled database",
    )
    def test_default_plugin_search_uses_populated_who_database(self):
        """Test the default plugin path reaches the configured WHO database."""
        plugin = WHOKnowledgePlugin()
        plugin.initialize()
        plugin.connect()
        results = plugin.search("pneumonia")
        assert results
        assert any(item["result_type"] == "disease" for item in results)

    def test_default_session_is_bound_to_who_engine(self):
        """Test default plugin sessions are bound to WHO_DATABASE_URL."""
        from app.database.who_connection import WHO_ENGINE

        plugin = WHOKnowledgePlugin()
        assert plugin._session.bind is WHO_ENGINE

    def test_missing_who_database_configuration_fails_clearly(self, monkeypatch):
        """Test missing WHO database configuration is rejected explicitly."""
        from app.database import who_connection

        monkeypatch.setattr(who_connection.settings, "who_database_url", "")
        with pytest.raises(RuntimeError, match="WHO_DATABASE_URL is required"):
            who_connection.get_who_engine()

    def test_connect_with_session(self):
        """Test connect succeeds with mock session."""
        session = Mock()
        plugin = WHOKnowledgePlugin(db_session=session)
        plugin.initialize()
        
        # Mock the repository and provider creation
        with patch("app.plugins.knowledge.who_knowledge_plugin.WHOKnowledgeRepository") as mock_repo_class, \
             patch("app.plugins.knowledge.who_knowledge_plugin.WHOProvider") as mock_provider_class:
            
            mock_repo_instance = Mock()
            mock_provider_instance = Mock()
            mock_provider_instance.metadata.return_value = Mock()
            
            mock_repo_class.return_value = mock_repo_instance
            mock_provider_class.return_value = mock_provider_instance
            
            plugin.connect()
            
            assert plugin._is_connected is True
            assert plugin._repository == mock_repo_instance
            assert plugin._provider == mock_provider_instance

    def test_disconnect(self):
        """Test disconnect cleans up resources."""
        session = Mock()
        plugin = WHOKnowledgePlugin(db_session=session)
        plugin.initialize()
        
        # Set up as connected
        plugin._repository = Mock()
        plugin._provider = Mock()
        plugin._is_connected = True
        
        plugin.disconnect()
        
        assert plugin._is_connected is False
        assert plugin._repository is None
        assert plugin._provider is None


class TestWHOKnowledgePluginHealth:
    """Test WHO Plugin health checks."""

    def test_health_disconnected(self):
        """Test health status when disconnected."""
        plugin = WHOKnowledgePlugin(db_session=Mock())
        plugin.initialize()
        
        health = plugin.health()
        assert health.healthy is False
        assert "disconnected" in health.status.lower()

    def test_health_connected(self):
        """Test health status when connected."""
        plugin = WHOKnowledgePlugin(db_session=Mock())
        plugin.initialize()
        
        # Set up as connected
        plugin._repository = Mock()
        plugin._provider = Mock()
        plugin._is_connected = True
        
        health = plugin.health()
        assert health.healthy is True
        assert "connected" in health.status.lower()


class TestWHOKnowledgePluginSearch:
    """Test WHO Plugin search operations."""

    def test_search_empty_query(self):
        """Test search with empty query returns empty list."""
        plugin = WHOKnowledgePlugin(db_session=Mock())
        results = plugin.search("")
        assert results == []

    def test_search_without_connection(self):
        """Test search raises if not connected."""
        plugin = WHOKnowledgePlugin(db_session=Mock())
        plugin.initialize()
        
        with pytest.raises(ConnectionError):
            plugin.search("pneumonia")

    def test_search_disease(self):
        """Test search for diseases."""
        session = Mock()
        plugin = WHOKnowledgePlugin(db_session=session)
        plugin.initialize()
        
        # Mock repository and provider
        mock_disease = Mock()
        mock_disease.disease_id = "d1"
        mock_disease.name = "Pneumonia"
        mock_disease.description = "Respiratory infection"
        mock_disease.care_level = "primary"
        mock_disease.chapter_number = 5
        
        plugin._repository = Mock()
        plugin._repository.search_diseases.return_value = [mock_disease]
        plugin._repository.list_drugs.return_value = []
        
        plugin._provider = Mock()
        plugin._provider.metadata.return_value = Mock()
        plugin._is_connected = True
        
        results = plugin.search("pneumonia")
        
        assert len(results) > 0
        assert results[0]["entity_name"] == "Pneumonia"
        assert results[0]["result_type"] == "disease"
        assert results[0]["entity_id"] == "d1"

    def test_search_drug(self):
        """Test search for drugs."""
        session = Mock()
        plugin = WHOKnowledgePlugin(db_session=session)
        plugin.initialize()
        
        # Mock drug
        mock_drug = Mock()
        mock_drug.drug_id = "amoxicillin"
        mock_drug.generic_name = "Amoxicillin"
        mock_drug.aware_group = "Access"
        mock_drug.antibiotic_class = "Beta-lactam"
        mock_drug.route = "Oral"
        mock_drug.notes = "First-line antibiotic"
        
        plugin._repository = Mock()
        plugin._repository.search_diseases.return_value = []
        plugin._repository.list_drugs.return_value = [mock_drug]
        
        plugin._provider = Mock()
        plugin._provider.metadata.return_value = Mock()
        plugin._is_connected = True
        
        results = plugin.search("amoxicillin")
        
        assert any(r["result_type"] == "drug" for r in results)


class TestWHOKnowledgePluginQuery:
    """Test WHO Plugin query operations."""

    def test_query_empty_criteria(self):
        """Test query with empty criteria returns empty dict."""
        plugin = WHOKnowledgePlugin(db_session=Mock())
        result = plugin.query({})
        assert result == {}

    def test_query_without_connection(self):
        """Test query raises if not connected."""
        plugin = WHOKnowledgePlugin(db_session=Mock())
        plugin.initialize()
        
        with pytest.raises(ConnectionError):
            plugin.query({"disease_id": "d1"})

    def test_query_disease_by_id(self):
        """Test query disease by ID."""
        session = Mock()
        plugin = WHOKnowledgePlugin(db_session=session)
        plugin.initialize()
        
        # Mock disease
        mock_disease = Mock()
        mock_disease.disease_id = "d1"
        mock_disease.name = "Pneumonia"
        mock_disease.description = "Community-acquired pneumonia"
        mock_disease.care_level = "primary"
        mock_disease.recommendations = []
        
        plugin._repository = Mock()
        plugin._repository.get_disease_by_id.return_value = mock_disease
        plugin._repository.get_complete_guideline.return_value = mock_disease
        
        plugin._provider = Mock()
        plugin._provider.metadata.return_value = Mock()
        plugin._is_connected = True
        
        result = plugin.query({"disease_id": "d1"})
        
        assert result["entity_id"] == "d1"
        assert result["entity_name"] == "Pneumonia"
        assert result["result_type"] == "disease_guideline"

    def test_query_drug_by_name(self):
        """Test query drug by name."""
        session = Mock()
        plugin = WHOKnowledgePlugin(db_session=session)
        plugin.initialize()
        
        # Mock drug
        mock_drug = Mock()
        mock_drug.drug_id = "amoxicillin"
        mock_drug.generic_name = "Amoxicillin"
        mock_drug.aware_group = "Access"
        mock_drug.antibiotic_class = "Beta-lactam"
        
        plugin._repository = Mock()
        plugin._repository.get_drug_by_name.return_value = mock_drug
        
        plugin._provider = Mock()
        plugin._provider.metadata.return_value = Mock()
        plugin._is_connected = True
        
        result = plugin.query({"drug_name": "Amoxicillin"})
        
        assert result["entity_id"] == "amoxicillin"
        assert result["entity_name"] == "Amoxicillin"
        assert result["result_type"] == "drug_guideline"
        assert result["guideline_category"] == "Access"

    def test_query_no_match(self):
        """Test query returns empty dict when no match."""
        session = Mock()
        plugin = WHOKnowledgePlugin(db_session=session)
        plugin.initialize()
        
        plugin._repository = Mock()
        plugin._repository.get_disease_by_id.return_value = None
        
        plugin._provider = Mock()
        plugin._provider.metadata.return_value = Mock()
        plugin._is_connected = True
        
        result = plugin.query({"disease_id": "nonexistent"})
        assert result == {}


class TestWHOKnowledgePluginDomains:
    """Test WHO Plugin domain support."""

    def test_supported_domains(self):
        """Test plugin declares supported domains."""
        plugin = WHOKnowledgePlugin(db_session=Mock())
        domains = plugin.supported_domains()
        
        assert "respiratory" in domains
        assert "general" in domains
        assert len(domains) > 0

    def test_knowledge_version(self):
        """Test knowledge version."""
        plugin = WHOKnowledgePlugin(db_session=Mock())
        version = plugin.knowledge_version()
        
        assert "WHO" in version
        assert "2023" in version


class TestWHOKnowledgeResult:
    """Test WHOKnowledgeResult data class."""

    def test_result_to_dict(self):
        """Test converting result to dictionary."""
        result = WHOKnowledgeResult(
            entity_id="d1",
            entity_name="Pneumonia",
            entity_description="Community-acquired pneumonia",
            clinical_recommendation="Start empirical therapy",
            evidence_level="HIGH",
        )
        
        result_dict = result.to_dict()
        
        assert result_dict["entity_id"] == "d1"
        assert result_dict["entity_name"] == "Pneumonia"
        assert result_dict["evidence_level"] == "HIGH"
        assert result_dict["source"] == "WHO"

    def test_result_serializable(self):
        """Test result is JSON serializable."""
        import json
        
        result = WHOKnowledgeResult(
            entity_id="d1",
            entity_name="Pneumonia",
            metadata={"key": "value"},
        )
        
        result_dict = result.to_dict()
        json_str = json.dumps(result_dict)
        
        assert json_str is not None


class TestWHOKnowledgePluginExplain:
    """Test WHO Plugin explain operations."""

    def test_explain_disease(self):
        """Test explain for a disease."""
        session = Mock()
        plugin = WHOKnowledgePlugin(db_session=session)
        plugin.initialize()
        
        # Mock disease with evidence and recommendations
        mock_evidence = Mock()
        mock_evidence.evidence_id = "e1"
        mock_evidence.text = "Evidence statement"
        mock_evidence.type = "clinical"
        mock_evidence.source = "WHO"
        
        mock_rec = Mock()
        mock_rec.recommendation_id = "r1"
        mock_rec.drug_id = "amoxicillin"
        mock_rec.population = "adults"
        mock_rec.severity = "mild"
        
        mock_disease = Mock()
        mock_disease.disease_id = "d1"
        mock_disease.name = "Pneumonia"
        mock_disease.description = "Community-acquired pneumonia"
        mock_disease.evidence = [mock_evidence]
        mock_disease.recommendations = [mock_rec]
        
        plugin._repository = Mock()
        plugin._repository.get_complete_guideline.return_value = mock_disease
        
        plugin._provider = Mock()
        plugin._provider.metadata.return_value = Mock()
        plugin._is_connected = True
        
        explanation = plugin.explain("d1", entity_type="disease")
        
        assert explanation["entity_id"] == "d1"
        assert explanation["entity_name"] == "Pneumonia"
        assert len(explanation["evidence"]) > 0
        assert len(explanation["recommendations"]) > 0


class TestWHOKnowledgePluginIntegration:
    """Integration tests for WHO Plugin."""

    def test_full_lifecycle(self):
        """Test complete plugin lifecycle."""
        session = Mock()
        plugin = WHOKnowledgePlugin(db_session=session)
        
        # Initialize
        plugin.initialize()
        assert plugin._initialization_time is not None
        
        # Get metadata
        metadata = plugin.metadata()
        assert metadata.plugin_id == "who_knowledge"
        
        # Check health before connection
        health = plugin.health()
        assert health.healthy is False
        
        # Shutdown
        plugin.shutdown()
        assert plugin._repository is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
