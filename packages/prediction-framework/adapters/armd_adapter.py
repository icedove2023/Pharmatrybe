"""ARMD Adapter for Prediction Framework.

Non-invasive adapter that wraps WP4_Decision_Engine functions into the
unified ModelPackage and PredictionCore interfaces without modifying WP4.

The adapter acts as a bridge between legacy WP4 code and the plugin layer.
"""

import sys
import os
import json
import pickle
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import logging
import numpy as np
import pandas as pd

from packages.prediction_framework.contracts import (
    ModelPackage,
    PredictionRequest,
    PredictionExecution,
    PredictionStatus,
    ExplainabilityPayload,
    ExplainabilityDriver,
)

logger = logging.getLogger(__name__)


class ARMDAdapterError(Exception):
    """Raised when ARMD adapter operations fail."""
    pass


class ARMDAdapter:
    """Adapter for ARMD WP4_Decision_Engine.
    
    Provides a non-invasive wrapper around WP4 functions (load_registry,
    load_inference_package, predict_all_antibiotics, generate_shap_explanation)
    without modifying the legacy code.
    
    Usage:
        adapter = ARMDAdapter(wp4_root="/path/to/deployments/ARMD")
        adapter.initialize()
        model_package = adapter.load_model_package("ciprofloxacin")
        execution = adapter.predict(model_package, patient_data)
    """

    def __init__(self, wp4_root: Optional[str] = None):
        """Initialize adapter with WP4 deployment root.
        
        Args:
            wp4_root: Path to deployments/ARMD directory. If None, will use
                     standard workspace path detection.
        """
        if wp4_root is None:
            # Auto-detect workspace path
            wp4_root = self._detect_wp4_root()
        
        self.wp4_root = Path(wp4_root)
        if not self.wp4_root.exists():
            raise ARMDAdapterError(f"WP4 root not found: {wp4_root}")
        
        self._sys_path_added = False
        self._registry = None
        self._performance = None
        self._wp3_artifacts = None
        self._wp2_table = None
        self._logger = logger

    def _detect_wp4_root(self) -> str:
        """Auto-detect WP4 root from workspace."""
        candidates = [
            Path.cwd() / "deployments" / "ARMD",
            Path(__file__).resolve().parents[3] / "deployments" / "ARMD",
        ]
        for candidate in candidates:
            if candidate.exists():
                return str(candidate)
        raise ARMDAdapterError("Could not auto-detect WP4 root. Specify explicitly.")

    def _ensure_wp4_importable(self) -> None:
        """Add WP4 root to sys.path so we can import WP4_Decision_Engine."""
        if not self._sys_path_added:
            wp4_str = str(self.wp4_root)
            if wp4_str not in sys.path:
                sys.path.insert(0, wp4_str)
                self._sys_path_added = True
                self._logger.info(f"Added {wp4_str} to sys.path")

    def initialize(self) -> None:
        """Load registry, artifacts, and WP2 table."""
        self._ensure_wp4_importable()
        
        self._logger.info("Initializing ARMD adapter")
        
        # Import WP4 functions
        try:
            from WP4_Decision_Engine import (
                load_registry,
                load_wp3_artifacts,
                load_wp2_table,
            )
        except ImportError as e:
            raise ARMDAdapterError(f"Failed to import WP4 functions: {e}")
        
        # Load registry
        try:
            self._registry, self._performance = load_registry()
            self._normalize_registry_paths()
            self._logger.info(f"Loaded registry with {len(self._registry)} antibiotics")
        except Exception as e:
            raise ARMDAdapterError(f"Failed to load registry: {e}")
        
        # Load WP3 artifacts
        try:
            self._wp3_artifacts = load_wp3_artifacts()
            self._logger.info("Loaded WP3 preprocessing artifacts")
        except Exception as e:
            raise ARMDAdapterError(f"Failed to load WP3 artifacts: {e}")
        
        # Load WP2 table
        try:
            self._wp2_table = load_wp2_table()
            self._logger.info(f"Loaded WP2 table with shape {self._wp2_table.shape}")
        except Exception as e:
            self._logger.warning(f"Failed to load WP2 table (optional): {e}")
            self._wp2_table = None

    def _normalize_registry_paths(self) -> None:
        """Resolve registry paths against the active ARMD deployment root."""
        if not isinstance(self._registry, dict):
            return
        models_root = self.wp4_root / "output" / "WP3" / "Models"
        for antibiotic, info in self._registry.items():
            if not isinstance(info, dict):
                continue
            folder_name = re.sub(r"[^A-Za-z0-9]+", "_", str(antibiotic)).strip("_")
            folder = models_root / folder_name
            if folder.is_dir():
                info["folder"] = str(folder)

    def load_model_package(self, antibiotic: str) -> ModelPackage:
        """Load a model for a specific antibiotic as a ModelPackage.
        
        Args:
            antibiotic: Antibiotic name (e.g., "ciprofloxacin")
            
        Returns:
            ModelPackage with loaded model, scaler, threshold, feature_names
            
        Raises:
            ARMDAdapterError: If model cannot be loaded
        """
        if self._registry is None:
            raise ARMDAdapterError("Adapter not initialized. Call initialize() first.")
        
        self._ensure_wp4_importable()
        
        try:
            from WP4_Decision_Engine import load_inference_package
        except ImportError as e:
            raise ARMDAdapterError(f"Failed to import load_inference_package: {e}")
        
        try:
            pkg = load_inference_package(antibiotic, self._registry)
            
            metadata = self._performance.get(antibiotic, {})
            
            model_package = ModelPackage(
                id=antibiotic,
                model=pkg['model'],
                scaler=pkg['scaler'],
                threshold=pkg['threshold'],
                feature_names=pkg['feature_names'],
                artifacts={
                    'preprocessor': self._wp3_artifacts,
                    'inference_folder': pkg['folder'],
                },
                metadata={
                    'auc': metadata.get('auc'),
                    'ap': metadata.get('ap'),
                    'auc_ci': (metadata.get('auc_ci_lower'), metadata.get('auc_ci_upper')),
                    'ap_ci': (metadata.get('ap_ci_lower'), metadata.get('ap_ci_upper')),
                },
                loaded_timestamp=datetime.utcnow(),
            )
            
            self._logger.info(f"Loaded model package for {antibiotic}")
            return model_package
            
        except Exception as e:
            raise ARMDAdapterError(f"Failed to load model package for {antibiotic}: {e}")

    def preprocess_patient_features(self, patient_data: Dict[str, Any]) -> pd.DataFrame:
        """Preprocess patient data using WP3 artifacts for exact parity.
        
        Args:
            patient_data: Dictionary of patient features
            
        Returns:
            Preprocessed DataFrame with aligned columns
            
        Raises:
            ARMDAdapterError: If preprocessing fails
        """
        if self._wp3_artifacts is None:
            raise ARMDAdapterError("Artifacts not initialized. Call initialize() first.")
        
        self._ensure_wp4_importable()
        
        try:
            from WP4_Decision_Engine import preprocess_patient_features
        except ImportError as e:
            raise ARMDAdapterError(f"Failed to import preprocess_patient_features: {e}")
        
        try:
            # Convert dict to Series
            patient_series = pd.Series(patient_data)
            
            # Use WP4 preprocessing exactly
            preprocessed_df = preprocess_patient_features(patient_series, self._wp3_artifacts)
            
            self._logger.info(f"Preprocessed patient data to shape {preprocessed_df.shape}")
            return preprocessed_df
            
        except Exception as e:
            raise ARMDAdapterError(f"Preprocessing failed: {e}")

    def predict(
        self,
        model_package: ModelPackage,
        patient_data: Dict[str, Any],
    ) -> PredictionExecution:
        """Execute prediction using a model package.
        
        Args:
            model_package: Loaded ModelPackage
            patient_data: Patient features dictionary
            
        Returns:
            PredictionExecution with results
        """
        self._ensure_wp4_importable()
        
        try:
            from WP4_Decision_Engine import build_feature_frame
        except ImportError as e:
            raise ARMDAdapterError(f"Failed to import build_feature_frame: {e}")
        
        try:
            # Preprocess patient
            patient_df = self.preprocess_patient_features(patient_data)
            
            # Align features
            X = build_feature_frame(patient_df, model_package.feature_names)
            X_scaled = model_package.scaler.transform(X)
            
            # Predict
            prob = model_package.model.predict_proba(X_scaled)[0, 1]
            class_label = 'Resistant' if prob >= model_package.threshold else 'Susceptible'
            confidence = abs(prob - model_package.threshold)
            
            return PredictionExecution(
                status=PredictionStatus.SUCCESS,
                model_id=model_package.id,
                predictions={
                    'antibiotic': model_package.id,
                    'class': class_label,
                },
                probabilities={
                    'resistant': float(prob),
                    'susceptible': float(1.0 - prob),
                },
                selected_class=class_label,
                confidence=float(confidence),
                ranking=[(class_label, float(prob))],
                execution_metadata={
                    'threshold': float(model_package.threshold),
                    'model_type': type(model_package.model).__name__,
                },
            )
            
        except Exception as e:
            self._logger.error(f"Prediction failed: {e}", exc_info=True)
            return PredictionExecution(
                status=PredictionStatus.FAILED,
                model_id=model_package.id,
                error=str(e),
            )

    def predict_all_antibiotics(
        self,
        patient_data: Dict[str, Any],
    ) -> Dict[str, PredictionExecution]:
        """Predict for all registered antibiotics.
        
        Args:
            patient_data: Patient features dictionary
            
        Returns:
            Dictionary of antibiotic -> PredictionExecution
        """
        if self._registry is None:
            raise ARMDAdapterError("Adapter not initialized. Call initialize() first.")
        
        results = {}
        for antibiotic in self._registry.keys():
            try:
                model_package = self.load_model_package(antibiotic)
                execution = self.predict(model_package, patient_data)
                results[antibiotic] = execution
            except Exception as e:
                self._logger.error(f"Prediction for {antibiotic} failed: {e}")
                results[antibiotic] = PredictionExecution(
                    status=PredictionStatus.FAILED,
                    model_id=antibiotic,
                    error=str(e),
                )
        
        return results

    def explain(
        self,
        model_package: ModelPackage,
        patient_data: Dict[str, Any],
        prediction_execution: PredictionExecution,
    ) -> ExplainabilityPayload:
        """Generate SHAP explanation for a prediction.
        
        Args:
            model_package: Loaded ModelPackage
            patient_data: Patient features dictionary
            prediction_execution: The PredictionExecution to explain
            
        Returns:
            ExplainabilityPayload with SHAP drivers and narrative
        """
        self._ensure_wp4_importable()
        
        try:
            from WP4_Decision_Engine import (
                build_feature_frame,
                build_background,
                generate_shap_explanation,
                DISPLAY_NAMES,
            )
        except ImportError as e:
            raise ARMDAdapterError(f"Failed to import SHAP functions: {e}")
        
        try:
            # Preprocess patient
            patient_df = self.preprocess_patient_features(patient_data)
            
            # Build background (use subset of WP2 table if available)
            if self._wp2_table is not None:
                background_data = build_background(
                    self._wp2_table,
                    model_package.scaler,
                    model_package.feature_names,
                    self._wp3_artifacts,
                    n_samples=200,
                )
            else:
                # Fallback: use patient data as background (less ideal)
                X = build_feature_frame(patient_df, model_package.feature_names)
                background_data = model_package.scaler.transform(X)
            
            # Call WP4 SHAP function (returns dict with pos/neg drivers, narrative, figures)
            shap_result = generate_shap_explanation(
                patient_id=patient_data.get('patient_id', 'unknown'),
                patient_df=patient_df,
                registry=self._registry,
                top_abx=model_package.id,
                background_data=background_data,
                feature_names=model_package.feature_names,
                model=model_package.model,
                scaler=model_package.scaler,
                patient_dir="/tmp",  # Temporary; plugin can override
            )
            
            # Map WP4 output to ExplainabilityPayload
            pos_drivers = [
                ExplainabilityDriver(
                    feature_name=name,
                    display_name=DISPLAY_NAMES.get(name, name),
                    contribution=float(value),
                    feature_value=patient_df.get(name, [None])[0] if name in patient_df else None,
                )
                for name, value in shap_result.get('positive_drivers', [])
            ]
            
            neg_drivers = [
                ExplainabilityDriver(
                    feature_name=name,
                    display_name=DISPLAY_NAMES.get(name, name),
                    contribution=float(value),
                    feature_value=patient_df.get(name, [None])[0] if name in patient_df else None,
                )
                for name, value in shap_result.get('negative_drivers', [])
            ]
            
            return ExplainabilityPayload(
                prediction_id=f"{model_package.id}_{patient_data.get('patient_id', 'unknown')}",
                model_id=model_package.id,
                base_value=shap_result.get('base_value'),
                positive_drivers=pos_drivers,
                negative_drivers=neg_drivers,
                figure_paths=shap_result.get('figure_paths', {}),
                narrative=shap_result.get('narrative'),
                confidence_indicators={
                    'auc': model_package.metadata.get('auc'),
                    'ap': model_package.metadata.get('ap'),
                    'threshold': model_package.threshold,
                },
            )
            
        except Exception as e:
            self._logger.error(f"Explainability generation failed: {e}", exc_info=True)
            # Return minimal payload on error
            return ExplainabilityPayload(
                prediction_id=f"{model_package.id}_{patient_data.get('patient_id', 'unknown')}",
                model_id=model_package.id,
                narrative=f"Explanation failed: {str(e)}",
            )

    @property
    def registry(self) -> Optional[Dict]:
        """Access the loaded registry."""
        return self._registry

    @property
    def artifacts(self) -> Optional[Dict]:
        """Access the loaded WP3 artifacts."""
        return self._wp3_artifacts
