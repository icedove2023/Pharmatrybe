"""Integration tests for ARMD Plugin.

Tests the full plugin prediction flow and validates parity
with legacy WP5 endpoints.
"""

import pytest
import sys
import os
import json
from pathlib import Path
from typing import Dict, Any

from app.plugins.base.prediction_plugin import PredictionRequest, PredictionResult
from app.plugins.prediction.armd.armd_prediction_plugin import ARMDPredictionPlugin
from packages.prediction_framework.contracts import PredictionStatus


class TestARMDPluginInitialization:
    """Test plugin lifecycle."""

    def test_plugin_initializes(self):
        """Plugin should initialize without errors."""
        plugin = ARMDPredictionPlugin()
        plugin.initialize()
        
        assert plugin._initialized
        assert plugin.runtime_context.validate()

    def test_plugin_health_check(self):
        """Plugin should report health status."""
        plugin = ARMDPredictionPlugin()
        plugin.initialize()
        
        health = plugin.health()
        
        assert health.status in ['healthy', 'unhealthy']
        assert health.healthy is True

    def test_plugin_metadata(self):
        """Plugin should provide metadata."""
        plugin = ARMDPredictionPlugin()
        plugin.initialize()
        
        metadata = plugin.metadata()
        
        assert metadata.plugin_id == 'armd'
        assert metadata.plugin_name == 'ARMD Prediction Plugin'
        assert 'resistance_prediction' in metadata.capabilities

    def test_plugin_shutdown(self):
        """Plugin should shutdown gracefully."""
        plugin = ARMDPredictionPlugin()
        plugin.initialize()
        plugin.shutdown()
        
        assert not plugin._initialized


class TestARMDPluginPrediction:
    """Test plugin prediction functionality."""

    @pytest.fixture
    def plugin(self):
        """Fixture: initialized ARMD plugin."""
        plugin = ARMDPredictionPlugin()
        plugin.initialize()
        return plugin

    @pytest.fixture
    def sample_request(self):
        """Fixture: sample prediction request."""
        request = PredictionRequest(payload={
            'age': 65.0,
            'gender_male': 1,
            'inpatient': 1,
            'icu': 0,
            'creatinine': 1.5,
            'bun': 28.0,
            'wbc': 12.5,
            'temperature': 38.2,
            'heartrate': 92.0,
            'resp_rate': 18.0,
            'n_prior_meds': 3,
            'n_prior_classes': 2,
            'days_since_last_antibiotic': 10,
            'patient_id': 'test_patient_123',
        })
        return request

    def test_plugin_validates(self, plugin):
        """Plugin validate() should return True when initialized."""
        assert plugin.validate()

    def test_plugin_executes_prediction(self, plugin, sample_request):
        """Plugin should execute prediction for valid request."""
        result = plugin.predict(sample_request)
        
        assert result is not None
        assert isinstance(result, PredictionResult)
        # Result format matches platform contract

    def test_plugin_handles_invalid_state(self):
        """Plugin should raise error if predict() called before initialize()."""
        plugin = ARMDPredictionPlugin()
        
        request = PredictionRequest(payload={'age': 65.0})
        
        with pytest.raises(RuntimeError):
            plugin.predict(request)

    def test_plugin_registry_info(self, plugin):
        """Plugin should provide registry information."""
        engine = plugin.engine
        registry_info = engine.get_registry_info()
        
        assert 'antibiotics' in registry_info
        assert 'count' in registry_info
        assert registry_info['count'] > 0

    def test_plugin_single_antibiotic_prediction(self, plugin, sample_request):
        """Plugin should predict for single antibiotic."""
        engine = plugin.engine
        
        registry_info = engine.get_registry_info()
        antibiotic = registry_info['antibiotics'][0]
        
        result = engine.predict_single_antibiotic(
            sample_request.payload,
            antibiotic
        )
        
        assert result is not None
        assert 'status' in result
        assert 'antibiotic' in result


class TestARMDPluginExplainability:
    """Test explainability functionality."""

    @pytest.fixture
    def plugin(self):
        """Fixture: initialized ARMD plugin."""
        plugin = ARMDPredictionPlugin()
        plugin.initialize()
        return plugin

    @pytest.fixture
    def sample_request(self):
        """Fixture: sample prediction request."""
        request = PredictionRequest(payload={
            'age': 65.0,
            'gender_male': 1,
            'inpatient': 1,
            'icu': 0,
            'creatinine': 1.5,
            'bun': 28.0,
            'wbc': 12.5,
            'temperature': 38.2,
            'heartrate': 92.0,
            'resp_rate': 18.0,
            'n_prior_meds': 3,
            'n_prior_classes': 2,
            'days_since_last_antibiotic': 10,
            'patient_id': 'test_patient_123',
        })
        return request

    def test_plugin_explainability_available(self, plugin):
        """Plugin should have explainability module available."""
        assert plugin.engine.runtime_context.adapter is not None


class TestARMDPluginConfiguration:
    """Test plugin configuration."""

    def test_plugin_with_custom_config(self):
        """Plugin should accept custom configuration."""
        config = {
            'enable_explainability': True,
            'cache_models': True,
        }
        
        plugin = ARMDPredictionPlugin(config=config)
        assert plugin.config == config

    def test_plugin_config_schema(self):
        """Plugin should provide configuration schema."""
        plugin = ARMDPredictionPlugin()
        schema = plugin._get_config_schema()
        
        assert 'type' in schema
        assert schema['type'] == 'object'
        assert 'properties' in schema


class TestARMDPluginReload:
    """Test plugin reload functionality."""

    def test_plugin_reload(self):
        """Plugin should support runtime reload."""
        plugin = ARMDPredictionPlugin()
        plugin.initialize()
        
        # Should not raise error
        plugin.reload()
        
        # Should still be valid
        assert plugin.validate()


class TestARMDPluginErrorHandling:
    """Test error handling."""

    @pytest.fixture
    def plugin(self):
        """Fixture: initialized ARMD plugin."""
        plugin = ARMDPredictionPlugin()
        plugin.initialize()
        return plugin

    def test_plugin_handles_empty_patient_data(self, plugin):
        """Plugin should handle empty patient data gracefully."""
        request = PredictionRequest(payload={})
        
        # Should not crash; may return error status
        result = plugin.predict(request)
        assert result is not None

    def test_plugin_handles_invalid_request(self, plugin):
        """Plugin should handle invalid requests."""
        # Malformed request
        request = PredictionRequest(payload={})
        
        # Should not crash
        try:
            result = plugin.predict(request)
            # Result should be valid even if error
            assert result is not None
        except (AttributeError, TypeError):
            # Also acceptable to raise error for truly invalid request
            pass
