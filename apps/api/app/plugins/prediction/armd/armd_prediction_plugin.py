"""ARMD Prediction Plugin Entrypoint.

Implements the platform PredictionPlugin interface using ARMD adapters.
Manages plugin lifecycle and coordinates prediction execution.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from app.plugins.base.prediction_plugin import (
    PredictionPlugin,
    PredictionRequest,
    PredictionResult,
    DeploymentType,
)
from app.plugins.base.plugin import PluginType, PluginMetadata, PluginHealth

from .runtime_context import ARMDRuntimeContext, RuntimeHealth
from .prediction_engine import ARMDPredictionEngine
from packages.prediction_framework.plugin import BasePredictionPlugin
from app.plugins.schema.clinical_registry import (
    PLUGIN_SPECIFIC,
)

logger = logging.getLogger(__name__)


class ARMDPredictionPlugin(BasePredictionPlugin):
    """ARMD Prediction Plugin for PharmaTrybe.
    
    Artifact-based prediction plugin that wraps WP4_Decision_Engine
    using the ARMDAdapter, providing resistance predictions for
    multiple antibiotics with SHAP-based explainability.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize ARMD plugin.
        
        Args:
            config: Plugin configuration dict (optional)
                   - wp4_root: Path to deployments/ARMD
                   - enable_explainability: Whether to generate SHAP explanations
        """
        super().__init__(config=config)
        self.config = self.config or {}
        self._runtime_context = ARMDRuntimeContext(config=self.config)
        self.engine = ARMDPredictionEngine(self._runtime_context)
        self._initialized = False
        logger.info("ARMD Prediction Plugin initialized")

    @property
    def plugin_id(self) -> str:
        return "armd"

    @property
    def plugin_name(self) -> str:
        return "ARMD Prediction Plugin"

    @property
    def plugin_version(self) -> str:
        return "0.1.0"

    @property
    def plugin_type(self) -> PluginType:
        return PluginType.PREDICTION

    @property
    def plugin_description(self) -> str:
        return "ARMD resistance prediction plugin using WP4 models and SHAP explainability"

    @property
    def author(self) -> str:
        return "PharmaTrybe"

    @property
    def capabilities(self) -> List[str]:
        return ["resistance_prediction", "antibiotic_ranking", "shap_explainability"]

    @property
    def dependencies(self) -> List[str]:
        return []

    @property
    def deployment_type(self) -> DeploymentType:
        return DeploymentType.ARTIFACT

    def initialize(self) -> None:
        """Initialize plugin: load adapter, registry, and artifacts.
        
        Raises:
            RuntimeError: If initialization fails
        """
        logger.info("Initializing ARMD Prediction Plugin")
        try:
            self.runtime_context.initialize()
            self._initialized = True
            logger.info("ARMD Prediction Plugin initialization complete")
        except Exception as e:
            logger.error(f"Plugin initialization failed: {e}", exc_info=True)
            raise

    def configure(self, configuration: Dict[str, Any]) -> None:
        """Apply runtime configuration before initialization."""
        self.config = configuration or {}
        self._runtime_context = ARMDRuntimeContext(config=self.config)
        self.engine = ARMDPredictionEngine(self._runtime_context)

    def load(self) -> None:
        """Load the ARMD runtime and its model artifacts."""
        self.initialize()

    def shutdown(self) -> None:
        """Shutdown plugin and release resources."""
        logger.info("Shutting down ARMD Prediction Plugin")
        self.runtime_context.shutdown()
        self._initialized = False

    def unload(self) -> None:
        """Release the ARMD runtime resources."""
        self.shutdown()

    def validate(self) -> bool:
        """Check if plugin is ready to accept predictions.
        
        Returns:
            True if adapter is initialized with at least one model
        """
        if not self._initialized:
            return False
        
        return self.runtime_context.validate()

    def health(self) -> PluginHealth:
        """Get plugin health status.
        
        Returns:
            PluginHealth with component statuses and errors
        """
        runtime_health: RuntimeHealth = self.runtime_context.health()
        
        return PluginHealth(
            healthy=runtime_health.healthy,
            status="healthy" if runtime_health.healthy else "unhealthy",
            message=(
                "ARMD runtime is initialized."
                if runtime_health.healthy
                else "; ".join(runtime_health.errors) or "ARMD runtime is unavailable."
            ),
            timestamp=runtime_health.timestamp,
        )

    def predict(self, request: PredictionRequest) -> PredictionResult:
        """Execute prediction for patient.
        
        Args:
            request: Platform PredictionRequest
            
        Returns:
            PredictionResult with predictions and optional explainability
            
        Raises:
            RuntimeError: If plugin not initialized or prediction fails
        """
        if not self.validate():
            raise RuntimeError("Plugin not properly initialized")
        
        return self.engine.predict(request)

    def supports(self, request: PredictionRequest) -> bool:
        """Return whether the request contains ARMD-compatible patient data."""
        return isinstance(request, PredictionRequest) and bool(request.payload)

    def input_schema(self) -> Dict[str, Any]:
        """Return the ARMD input schema for patient and resistance-risk context."""
        return {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": "ARMD prediction input",
            "type": "object",
            "properties": {field: {"type": "string" if field == "age_group" else "number"} for field in [
                "age", "gender_male", "age_group", "inpatient", "outpatient", "emergency", "icu",
                "has_any_procedure", "has_urinary_catheter", "has_cvc", "nursing_home_visit",
                "creatinine", "bun", "wbc", "neutrophils", "lymphocytes", "lactate", "procalcitonin",
                "heartrate", "resp_rate", "temperature", "sys_bp", "dias_bp", "n_prior_meds",
                "n_prior_classes", "days_since_last_antibiotic", "log_days_since_abx", "n_abx_classes_exposed",
                "n_prior_organisms", "days_since_last_prior_organism", "adi_score", "adi_state_rank",
            ]},
            "required": [],
            "additionalProperties": True,
            "x-contract-kind": "prediction_input",
            "x-ui-inputs": ["age", "gender_male", "inpatient", "outpatient", "emergency", "icu", "has_any_procedure", "has_urinary_catheter", "has_cvc", "nursing_home_visit", "creatinine", "bun", "wbc", "neutrophils", "lymphocytes", "lactate", "procalcitonin", "heartrate", "resp_rate", "temperature", "sys_bp", "dias_bp", "n_prior_meds", "n_prior_classes", "days_since_last_antibiotic", "n_abx_classes_exposed", "n_prior_organisms", "days_since_last_prior_organism", "adi_score", "adi_state_rank"],
            "x-derived-features": ["age_group", "log_days_since_abx", "age_group_19-30", "age_group_31-50", "age_group_51-65", "age_group_66-80", "age_group_80+", "age_group_nan"],
            "x-runtime-feature-whitelist": ["age", "gender_male", "age_group", "inpatient", "outpatient", "emergency", "icu", "has_any_procedure", "has_urinary_catheter", "has_cvc", "nursing_home_visit", "creatinine", "bun", "wbc", "neutrophils", "lymphocytes", "lactate", "procalcitonin", "heartrate", "resp_rate", "temperature", "sys_bp", "dias_bp", "n_prior_meds", "n_prior_classes", "days_since_last_antibiotic", "log_days_since_abx", "n_abx_classes_exposed", "n_prior_organisms", "days_since_last_prior_organism", "adi_score", "adi_state_rank"],
            "x-plugin-runtime-mappings": {"age": {"runtime_features": ["age", "age_group_*"], "classification": "TRANSFORMED"}, "age_group": {"runtime_features": ["age_group_*"], "classification": "DERIVED"}, "log_days_since_abx": {"runtime_features": ["log_days_since_abx"], "classification": "DERIVED"}, "model_features": {"classification": "MODEL_INTERNAL", "feature_count": 56, "source": "per-antibiotic model metadata"}, "prior_antibiotics": {"classification": PLUGIN_SPECIFIC, "runtime_features": ["n_prior_meds", "n_prior_classes", "days_since_last_antibiotic", "log_days_since_abx", "n_abx_classes_exposed"]}},
        }

    def output_schema(self) -> Dict[str, Any]:
        """Return the ARMD output schema placeholder."""
        return {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": "ARMD prediction output",
            "type": "object",
            "properties": {
                "predicted_class": {"type": "string"},
                "probabilities": {"type": "object", "additionalProperties": {"type": "number"}},
                "confidence": {"type": "number"},
                "model_name": {"type": "string"},
                "model_version": {"type": "string"},
                "execution_time_ms": {"type": "number"},
            },
            "required": ["predicted_class", "confidence"],
            "additionalProperties": True,
        }

    def reload(self) -> None:
        """Reload plugin configuration and registry.
        
        Useful for picking up newly deployed models without restart.
        """
        logger.info("Reloading ARMD plugin")
        self.runtime_context.reload()

    def metadata(self) -> PluginMetadata:
        """Get plugin metadata.
        
        Returns:
            PluginMetadata describing plugin capabilities and version
        """
        adapter = self.runtime_context.adapter
        antibiotic_count = 0
        if adapter and adapter.registry:
            antibiotic_count = len(adapter.registry)
        
        return PluginMetadata(
            plugin_id=self.plugin_id,
            plugin_name=self.plugin_name,
            plugin_version=self.plugin_version,
            plugin_type=self.plugin_type,
            description=self.plugin_description,
            author=self.author,
            capabilities=self.capabilities,
            dependencies=self.dependencies,
        )

    def _get_config_schema(self) -> Dict[str, Any]:
        """Get plugin configuration schema.
        
        Returns:
            JSON Schema for configuration validation
        """
        return {
            'type': 'object',
            'properties': {
                'wp4_root': {
                    'type': 'string',
                    'description': 'Path to deployments/ARMD directory',
                },
                'enable_explainability': {
                    'type': 'boolean',
                    'description': 'Generate SHAP explanations (may increase latency)',
                    'default': True,
                },
                'cache_models': {
                    'type': 'boolean',
                    'description': 'Cache loaded models in memory',
                    'default': True,
                },
            },
            'additionalProperties': False,
        }

    def _create_runtime_context(self) -> ARMDRuntimeContext:
        self._runtime_context = ARMDRuntimeContext(config=self.config)
        return self._runtime_context

    def _create_prediction_result(self, runtime_result: Any) -> PredictionResult:
        if hasattr(runtime_result, 'prediction_execution'):
            return runtime_result
        return PredictionResult(
            predicted_class='unknown',
            probabilities={},
            confidence=0.0,
            model_name=self.plugin_name,
            model_version=self.plugin_version,
            execution_time_ms=0.0,
            metadata={},
        )
