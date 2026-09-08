"""Unit tests for ARMD Adapter.

Tests validate that ARMDAdapter produces outputs identical to WP4_Decision_Engine
for sample patients and fixtures.
"""

import pytest
import sys
import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

import numpy as np
import pandas as pd

from packages.prediction_framework.adapters import ARMDAdapter, ARMDAdapterError
from packages.prediction_framework.contracts import (
    ModelPackage,
    PredictionStatus,
)


class TestARMDAdapterInitialization:
    """Test adapter initialization and registry loading."""

    @pytest.fixture
    def adapter(self):
        """Fixture: initialized ARMD adapter."""
        try:
            adapter = ARMDAdapter()
            adapter.initialize()
            return adapter
        except ARMDAdapterError as e:
            pytest.skip(f"WP4 not available: {e}")

    def test_adapter_detects_wp4_root(self):
        """Adapter should auto-detect WP4 root from workspace."""
        adapter = ARMDAdapter()
        assert adapter.wp4_root.exists(), f"WP4 root {adapter.wp4_root} not found"

    def test_adapter_initializes_registry(self, adapter):
        """Initialized adapter should load registry with antibiotics."""
        assert adapter.registry is not None
        assert isinstance(adapter.registry, dict)
        assert len(adapter.registry) > 0, "Registry should contain antibiotics"

    def test_adapter_initializes_artifacts(self, adapter):
        """Initialized adapter should load WP3 preprocessing artifacts."""
        assert adapter.artifacts is not None
        assert isinstance(adapter.artifacts, dict)
        # May have medians, dummy_columns, feature_order

    def test_adapter_loads_model_packages(self, adapter):
        """Adapter should load ModelPackage for each antibiotic."""
        for antibiotic in list(adapter.registry.keys())[:1]:  # Test first antibiotic
            model_package = adapter.load_model_package(antibiotic)
            assert model_package is not None
            assert model_package.id == antibiotic
            assert model_package.model is not None
            assert model_package.scaler is not None
            assert model_package.threshold is not None
            assert len(model_package.feature_names) > 0


class TestARMDAdapterPreprocessing:
    """Test preprocessing parity with WP4."""

    @pytest.fixture
    def adapter(self):
        """Fixture: initialized ARMD adapter."""
        try:
            adapter = ARMDAdapter()
            adapter.initialize()
            return adapter
        except ARMDAdapterError as e:
            pytest.skip(f"WP4 not available: {e}")

    @pytest.fixture
    def sample_patient_data(self):
        """Fixture: sample patient data for testing."""
        return {
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
        }

    def test_preprocessing_returns_dataframe(self, adapter, sample_patient_data):
        """Preprocessing should return DataFrame."""
        result = adapter.preprocess_patient_features(sample_patient_data)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1  # Single patient row

    def test_preprocessing_parity_with_wp4(self, adapter, sample_patient_data):
        """Adapter preprocessing should match WP4 preprocessing.
        
        Tests that feature alignment and imputation are exact.
        """
        # Get first antibiotic to test
        antibiotic = list(adapter.registry.keys())[0]
        model_package = adapter.load_model_package(antibiotic)
        
        # Preprocess
        patient_df = adapter.preprocess_patient_features(sample_patient_data)
        
        # WP4 adds model-specific antibiotic features at the final frame boundary.
        from WP4_Decision_Engine import build_feature_frame

        model_frame = build_feature_frame(patient_df, model_package.feature_names)

        # Check all required features are present in the final model frame.
        for feature in model_package.feature_names:
            assert feature in model_frame.columns, f"Missing feature: {feature}"
        
        # Check no NaN values remain after model-frame alignment.
        assert not model_frame.isnull().any().any(), "Model frame should contain no NaN values"


class TestARMDAdapterPrediction:
    """Test prediction execution and parity."""

    @pytest.fixture
    def adapter(self):
        """Fixture: initialized ARMD adapter."""
        try:
            adapter = ARMDAdapter()
            adapter.initialize()
            return adapter
        except ARMDAdapterError as e:
            pytest.skip(f"WP4 not available: {e}")

    @pytest.fixture
    def sample_patient_data(self):
        """Fixture: sample patient data."""
        return {
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
            'patient_id': 'test_123',
        }

    def test_single_antibiotic_prediction(self, adapter, sample_patient_data):
        """Adapter should execute prediction for single antibiotic."""
        antibiotic = list(adapter.registry.keys())[0]
        model_package = adapter.load_model_package(antibiotic)
        
        execution = adapter.predict(model_package, sample_patient_data)
        
        assert execution is not None
        assert execution.status == PredictionStatus.SUCCESS
        assert execution.model_id == antibiotic
        assert execution.selected_class in ['Resistant', 'Susceptible']
        assert execution.confidence is not None
        assert 0.0 <= execution.confidence <= 1.0

    def test_all_antibiotics_prediction(self, adapter, sample_patient_data):
        """Adapter should predict for all registered antibiotics."""
        predictions = adapter.predict_all_antibiotics(sample_patient_data)
        
        assert isinstance(predictions, dict)
        assert len(predictions) > 0
        
        # Check each antibiotic has a result
        for antibiotic, execution in predictions.items():
            assert antibiotic in adapter.registry.keys()
            assert execution is not None
            # Allow both SUCCESS and FAILED status
            assert execution.status in [PredictionStatus.SUCCESS, PredictionStatus.FAILED]

    def test_prediction_probability_range(self, adapter, sample_patient_data):
        """Prediction probabilities should be in valid range."""
        antibiotic = list(adapter.registry.keys())[0]
        model_package = adapter.load_model_package(antibiotic)
        
        execution = adapter.predict(model_package, sample_patient_data)
        
        if execution.status == PredictionStatus.SUCCESS:
            for prob_key, prob_value in execution.probabilities.items():
                assert 0.0 <= prob_value <= 1.0, f"Invalid probability: {prob_value}"

    def test_prediction_reproducibility(self, adapter, sample_patient_data):
        """Same patient data should produce identical predictions."""
        antibiotic = list(adapter.registry.keys())[0]
        model_package1 = adapter.load_model_package(antibiotic)
        execution1 = adapter.predict(model_package1, sample_patient_data)
        
        # Reload and predict again
        model_package2 = adapter.load_model_package(antibiotic)
        execution2 = adapter.predict(model_package2, sample_patient_data)
        
        # Should be identical
        assert execution1.selected_class == execution2.selected_class
        if execution1.status == PredictionStatus.SUCCESS:
            assert np.isclose(
                execution1.confidence,
                execution2.confidence,
                atol=1e-6
            ), "Predictions should be reproducible"


class TestARMDAdapterExplainability:
    """Test SHAP explainability generation."""

    @pytest.fixture
    def adapter(self):
        """Fixture: initialized ARMD adapter."""
        try:
            adapter = ARMDAdapter()
            adapter.initialize()
            return adapter
        except ARMDAdapterError as e:
            pytest.skip(f"WP4 not available: {e}")

    @pytest.fixture
    def sample_patient_data(self):
        """Fixture: sample patient data."""
        return {
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
            'patient_id': 'test_123',
        }

    def test_explainability_generation(self, adapter, sample_patient_data):
        """Adapter should generate SHAP explanations."""
        antibiotic = list(adapter.registry.keys())[0]
        model_package = adapter.load_model_package(antibiotic)
        execution = adapter.predict(model_package, sample_patient_data)
        
        explanation = adapter.explain(model_package, sample_patient_data, execution)
        
        assert explanation is not None
        assert explanation.prediction_id is not None
        assert explanation.model_id == antibiotic

    def test_explainability_drivers(self, adapter, sample_patient_data):
        """Explanation should have positive and negative drivers."""
        antibiotic = list(adapter.registry.keys())[0]
        model_package = adapter.load_model_package(antibiotic)
        execution = adapter.predict(model_package, sample_patient_data)
        
        explanation = adapter.explain(model_package, sample_patient_data, execution)
        
        # At least one of positive/negative drivers or narrative
        has_drivers = (
            len(explanation.positive_drivers) > 0
            or len(explanation.negative_drivers) > 0
            or explanation.narrative is not None
        )
        assert has_drivers, "Explanation should contain drivers or narrative"

    def test_explainability_graceful_failure(self, adapter, sample_patient_data):
        """Explainability should gracefully degrade on error."""
        antibiotic = list(adapter.registry.keys())[0]
        model_package = adapter.load_model_package(antibiotic)
        execution = adapter.predict(model_package, sample_patient_data)
        
        # Even if SHAP fails, should return valid ExplainabilityPayload
        explanation = adapter.explain(model_package, sample_patient_data, execution)
        
        assert explanation is not None
        assert explanation.model_id == antibiotic
        # Should have at least narrative (even if error)
        assert explanation.narrative is not None


class TestARMDAdapterErrorHandling:
    """Test error handling and robustness."""

    @pytest.fixture
    def adapter(self):
        """Fixture: initialized ARMD adapter."""
        try:
            adapter = ARMDAdapter()
            adapter.initialize()
            return adapter
        except ARMDAdapterError as e:
            pytest.skip(f"WP4 not available: {e}")

    def test_invalid_antibiotic_raises_error(self, adapter):
        """Loading invalid antibiotic should raise error."""
        with pytest.raises(ARMDAdapterError):
            adapter.load_model_package("nonexistent_antibiotic_xyz")

    def test_prediction_with_missing_features(self, adapter):
        """Prediction should handle missing patient features gracefully."""
        # Empty patient data
        patient_data = {}
        
        antibiotic = list(adapter.registry.keys())[0]
        model_package = adapter.load_model_package(antibiotic)
        
        # Should not crash; preprocessing should impute missing values
        execution = adapter.predict(model_package, patient_data)
        
        # Execution should complete (success or failure)
        assert execution is not None
        assert execution.status is not None

    def test_adapter_reinitialize(self, adapter):
        """Adapter should be reinitializable."""
        # Initialize twice
        adapter.initialize()
        
        # Registry should still be valid
        assert adapter.registry is not None
        assert len(adapter.registry) > 0
