from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from app.core.logging import get_logger
from app.plugins.base.prediction_plugin import DeploymentType, PredictionPlugin, PredictionRequest, PredictionResult
from app.plugins.base.plugin import PluginType, PluginMetadata, PluginHealth
from app.plugins.prediction.soar.artifact_registry import ArtifactCategoryConfig
from app.plugins.prediction.soar.deployment_registry import DeploymentRegistry
from app.plugins.prediction.soar.explainability_adapter import ExplainabilityAdapter
from app.plugins.prediction.soar.model_loader import ModelLoader
from app.plugins.prediction.soar.prediction_engine import PredictionEngine
from app.plugins.prediction.soar.runtime_context import SOARRuntimeContext
from app.plugins.prediction.soar.deployment_scanner import DeploymentInfo
from packages.prediction_framework.plugin import BasePredictionPlugin
from app.plugins.schema.clinical_registry import PLUGIN_SPECIFIC, UNRESOLVED

logger = get_logger(__name__)


class DeploymentSelectionError(ValueError):
    """Raised when a SOAR deployment cannot be selected deterministically."""


class SOARPredictionPlugin(BasePredictionPlugin):
    """Artifact-based prediction plugin implementation for SOAR."""

    def __init__(
        self,
        configuration: Optional[Dict[str, Any]] = None,
        deployment_registry: Optional[DeploymentRegistry] = None,
        model_loader: Optional[ModelLoader] = None,
        prediction_engine: Optional[PredictionEngine] = None,
        explainability_adapter: Optional[ExplainabilityAdapter] = None,
        runtime_context: Optional[SOARRuntimeContext] = None,
        logger: Optional[Any] = None,
    ) -> None:
        super().__init__(config=configuration)
        self._configuration = self.config
        self._logger = logger or get_logger(__name__)
        self._deployment_registry = deployment_registry
        self._model_loader = model_loader
        self._prediction_engine = prediction_engine or PredictionEngine()
        self._explainability_adapter = explainability_adapter or ExplainabilityAdapter()
        self._runtime_context = runtime_context
        self._initialized = False

    @property
    def plugin_id(self) -> str:
        return "soar"

    @property
    def plugin_name(self) -> str:
        return "SOAR Prediction Plugin"

    @property
    def plugin_version(self) -> str:
        return "0.1.0"

    @property
    def plugin_type(self) -> PluginType:
        return PluginType.PREDICTION

    @property
    def plugin_description(self) -> str:
        return "SOAR artifact-based prediction plugin."

    @property
    def author(self) -> str:
        return "PharmaTrybe"

    @property
    def capabilities(self) -> List[str]:
        return ["respiratory_prediction"]

    @property
    def dependencies(self) -> List[str]:
        return []

    @property
    def deployment_type(self) -> DeploymentType:
        return DeploymentType.ARTIFACT

    def initialize(self) -> None:
        if self._deployment_registry is None:
            self._deployment_registry = DeploymentRegistry(
                deployments_root=self._get_deployments_root_from_config()
            )

        if self._model_loader is None:
            self._model_loader = ModelLoader(
                category_config=self._load_category_config_from_config()
            )

        if self._runtime_context is None:
            self._runtime_context = SOARRuntimeContext(
                plugin_id=self.plugin_id,
                plugin_name=self.plugin_name,
                plugin_version=self.plugin_version,
                deployment_registry=self._deployment_registry,
                model_loader=self._model_loader,
                prediction_engine=self._prediction_engine,
                explainability_adapter=self._explainability_adapter,
                configuration=self._configuration,
                logger=self._logger,
            )
        self._runtime_context.initialize()
        self._initialized = True

    def shutdown(self) -> None:
        if self._runtime_context is not None:
            self._runtime_context.shutdown()
        self._initialized = False

    def configure(self, configuration: Dict[str, Any]) -> None:
        self._configuration = configuration or {}
        self._deployment_registry = DeploymentRegistry(
            deployments_root=self._get_deployments_root_from_config()
        )
        self._model_loader = ModelLoader(
            category_config=self._load_category_config_from_config()
        )
        if self._runtime_context is not None:
            self._runtime_context.deployment_registry = self._deployment_registry
            self._runtime_context.model_loader = self._model_loader
            self._runtime_context.reload_configuration(self._configuration)

    def validate(self) -> bool:
        if self._runtime_context is None or not self._initialized:
            return False
        runtime_health = self._runtime_context.health()
        if not runtime_health.healthy:
            return False
        return len(self._runtime_context.deployment_registry.get_all()) > 0

    def metadata(self) -> PluginMetadata:
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

    def _create_runtime_context(self) -> SOARRuntimeContext:
        self._deployment_registry = self._deployment_registry or DeploymentRegistry(
            deployments_root=self._get_deployments_root_from_config()
        )
        self._model_loader = self._model_loader or ModelLoader(
            category_config=self._load_category_config_from_config()
        )
        self._runtime_context = SOARRuntimeContext(
            plugin_id=self.plugin_id,
            plugin_name=self.plugin_name,
            plugin_version=self.plugin_version,
            deployment_registry=self._deployment_registry,
            model_loader=self._model_loader,
            prediction_engine=self._prediction_engine,
            explainability_adapter=self._explainability_adapter,
            configuration=self._configuration,
            logger=self._logger,
        )
        return self._runtime_context

    def _create_prediction_result(self, runtime_result: Any) -> PredictionResult:
        if hasattr(runtime_result, 'predicted_class'):
            return PredictionResult(
                predicted_class=getattr(runtime_result, 'predicted_class'),
                probabilities={"predicted_class": float(getattr(runtime_result, 'probability', 0.0) or 0.0)},
                confidence=float(getattr(runtime_result, 'probability', 0.0) or 0.0),
                model_name=getattr(runtime_result, 'deployment_id', self.plugin_name),
                model_version=self.plugin_version,
                execution_time_ms=float(getattr(runtime_result, 'execution_time_ms', 0.0)),
                metadata=getattr(runtime_result, 'metadata', {}) or {},
            )
        return PredictionResult(
            predicted_class="unknown",
            probabilities={},
            confidence=0.0,
            model_name=self.plugin_name,
            model_version=self.plugin_version,
            execution_time_ms=0.0,
            metadata={},
        )

    def health(self) -> PluginHealth:
        if self._runtime_context is None:
            return PluginHealth(
                healthy=False,
                status="uninitialized",
                message="Runtime context has not been initialized.",
                timestamp=__import__("datetime").datetime.utcnow(),
            )

        runtime_health = self._runtime_context.health()
        deployment_count = len(self._runtime_context.deployment_registry.get_all())
        loaded_model_count = len(self._runtime_context.model_loader.loaded_models())
        status = "healthy" if runtime_health.healthy else "degraded"
        message = (
            f"Runtime initialized. deployments={deployment_count}, loaded_models={loaded_model_count}."
            if runtime_health.healthy
            else "Runtime has degraded components."
        )
        return PluginHealth(
            healthy=runtime_health.healthy,
            status=status,
            message=message,
            timestamp=runtime_health.timestamp,
        )

    def load(self) -> None:
        self.initialize()

    def unload(self) -> None:
        self.shutdown()

    def predict(self, request: PredictionRequest) -> PredictionResult:
        if not self.supports(request):
            raise ValueError("Request not supported by SOARPredictionPlugin.")
        if self._runtime_context is None:
            raise RuntimeError("Runtime context is not initialized.")

        deployment = self._select_deployment(request)
        # Use cached loaded model if available to avoid redundant loads
        deployment_id = deployment.deployment_id
        if self._model_loader.is_loaded(deployment_id):
            loaded_model = self._model_loader.get(deployment_id)
        else:
            loaded_model = self._model_loader.load(deployment)
        execution = self._prediction_engine.predict(loaded_model, request)
        return self._explainability_adapter.explain(execution)

    def supports(self, request: PredictionRequest) -> bool:
        if not isinstance(request, PredictionRequest):
            return False
        if not isinstance(request.payload, dict) or not request.payload:
            return False

        if self._runtime_context is None:
            return False

        has_match_key = any(
            key in request.payload for key in [
                "organism",
                "antimicrobial",
                "pathogen",
                "antibiotic",
                "infection_site",
            ]
        )
        if has_match_key:
            return isinstance((request.context or {}).get("deployment_id"), str)

        return isinstance((request.context or {}).get("deployment_id"), str)

    def input_schema(self) -> Dict[str, Any]:
        return {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": "SOAR deployment-specific prediction input",
            "anyOf": [
                {"type": "object", "properties": {
                    "Age": {"type": "number"}, "YearCollected": {"type": "number"},
                    "Region": {"type": "string"}, "BodyLocation_Group": {"type": "string"},
                    "Country": {"type": "string"}, "Beta_Lactamase_enc": {"type": "number"},
                }, "required": ["Age", "YearCollected", "Region", "BodyLocation_Group", "Country"], "additionalProperties": False},
                {"type": "object", "properties": {
                    "Age": {"type": "number"}, "YearCollected": {"type": "number"},
                    "Region": {"type": "string"}, "BodyLocation_Group": {"type": "string"},
                    "Country": {"type": "string"}, "Beta_Lactamase_enc": {"type": "number"},
                }, "required": ["Age", "YearCollected", "Region", "BodyLocation_Group", "Country", "Beta_Lactamase_enc"], "additionalProperties": False},
            ],
            "unevaluatedProperties": False,
            "x-contract-kind": "prediction_input",
            "x-contract-version": "0.1.0",
            "x-deployment-contracts": [
                {"deployment_variant": "base", "required": ["Age", "YearCollected", "Region", "BodyLocation_Group", "Country"]},
                {"deployment_variant": "beta_lactamase", "required": ["Age", "YearCollected", "Region", "BodyLocation_Group", "Country", "Beta_Lactamase_enc"]},
            ],
            "x-ui-inputs": [],
            "x-platform-inputs": ["Age", "YearCollected", "Region", "BodyLocation_Group", "Country", "Beta_Lactamase_enc"],
            "x-deployment-selection": {"owner": "explicit_caller_routing_boundary", "selection_fields": ["deployment_id"], "frontend_visible": False},
            "x-plugin-runtime-mappings": {
                "Age": {"classification": "CONFIRMED", "source": "artifact feature_schema.json", "transformation": "passthrough to model preprocessing", "frontend_visible": False},
                "YearCollected": {"classification": "CONFIRMED", "source": "artifact feature_schema.json", "transformation": "passthrough to model preprocessing", "frontend_visible": False},
                "Region": {"classification": "TRANSFORMED", "source": "artifact feature_schema.json", "transformation": "one-hot encoding", "frontend_visible": False},
                "BodyLocation_Group": {"classification": "TRANSFORMED", "source": "artifact feature_schema.json", "transformation": "one-hot encoding", "frontend_visible": False},
                "Country": {"classification": "TRANSFORMED", "source": "artifact feature_schema.json", "transformation": "target encoding", "frontend_visible": False},
                "Beta_Lactamase_enc": {"classification": "TRANSFORMED", "source": "artifact feature_schema.json", "transformation": "passthrough/bin; deployment-specific", "frontend_visible": False},
                "pathogen": {"classification": UNRESOLVED, "source": "plugin support routing only", "frontend_visible": False},
                "organism": {"classification": PLUGIN_SPECIFIC, "source": "deployment scanner and selection logic", "frontend_visible": False},
                "antimicrobial": {"classification": PLUGIN_SPECIFIC, "source": "deployment scanner and selection logic", "frontend_visible": False},
            },
        }

    def output_schema(self) -> Dict[str, Any]:
        return {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": "SOAR prediction output",
            "type": "object",
            "properties": {
                "predicted_class": {"type": "string"},
                "probability": {"type": "number"},
                "confidence": {"type": "number"},
                "deployment_id": {"type": "string"},
                "metadata": {"type": "object", "additionalProperties": True},
            },
            "required": ["predicted_class", "probability"],
            "additionalProperties": True,
        }

    def _select_deployment(self, request: PredictionRequest) -> DeploymentInfo:
        context = request.context or {}
        deployment_id = context.get("deployment_id")
        if not isinstance(deployment_id, str) or not deployment_id.strip():
            raise DeploymentSelectionError("SOAR requires an explicit context.deployment_id; implicit fallback is disabled.")
        deployment = self._runtime_context.deployment_registry.get_by_id(deployment_id.strip())
        if deployment is None or deployment.status != "valid":
            raise DeploymentSelectionError(f"SOAR deployment is not available: {deployment_id}")
        return deployment

    def _get_deployments_root_from_config(self) -> Optional[Path]:
        root = self._configuration.get("deployments_root")
        if isinstance(root, str) and root:
            return Path(root)
        return None

    def _load_category_config_from_config(self) -> Optional[ArtifactCategoryConfig]:
        category_mapping = self._configuration.get("artifact_categories")
        if isinstance(category_mapping, dict):
            return ArtifactCategoryConfig(mapping=category_mapping)
        return None
