from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.core.logging import get_logger
from app.plugins.prediction.soar.deployment_registry import DeploymentRegistry
from app.plugins.prediction.soar.explainability_adapter import ExplainabilityAdapter
from app.plugins.prediction.soar.model_loader import ModelLoader
from app.plugins.prediction.soar.prediction_engine import PredictionEngine
from packages.prediction_framework.runtime import PredictionPluginRuntimeContext

logger = get_logger(__name__)


@dataclass(frozen=True)
class RuntimeMetadata:
    """Structured runtime metadata for the SOAR plugin context."""

    plugin_id: str
    plugin_name: str
    plugin_version: str
    deployment_count: int
    loaded_models: int
    startup_time: Optional[datetime]
    uptime_seconds: float
    created_at: datetime


@dataclass(frozen=True)
class RuntimeHealth:
    """Structured health status for the SOAR plugin runtime."""

    registry_ready: bool
    loader_ready: bool
    prediction_ready: bool
    explainability_ready: bool
    configuration_ready: bool
    healthy: bool
    errors: List[str]
    timestamp: datetime


class SOARRuntimeContext(PredictionPluginRuntimeContext):
    """Dependency container for SOAR runtime services."""

    def __init__(
        self,
        plugin_id: str,
        plugin_name: str,
        plugin_version: str,
        deployment_registry: DeploymentRegistry,
        model_loader: ModelLoader,
        prediction_engine: PredictionEngine,
        explainability_adapter: ExplainabilityAdapter,
        configuration: Optional[Dict[str, Any]] = None,
        logger: Optional[Any] = None,
        cache: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            plugin_id=plugin_id,
            plugin_name=plugin_name,
            plugin_version=plugin_version,
            logger=logger or get_logger(__name__),
        )
        self.configuration = configuration or {}
        self.deployment_registry = deployment_registry
        self.model_loader = model_loader
        self.prediction_engine = prediction_engine
        self.explainability_adapter = explainability_adapter
        self.logger = logger or self.logger
        self.cache = cache or {}
        self.created_at = datetime.now(timezone.utc)
        self._startup_time: Optional[datetime] = None
        self.runtime_metadata = self._build_runtime_metadata()

    def _on_initialize(self) -> None:
        self.deployment_registry.initialize()
        self._startup_time = datetime.now(timezone.utc)
        self.runtime_metadata = self._build_runtime_metadata()

    def _on_shutdown(self) -> None:
        try:
            self.model_loader.unload_all()
        except Exception as exc:
            self._record_error(f"Model loader shutdown failed: {exc}")
            self.logger.error(
                "Model loader shutdown failed",
                extra={"plugin_id": self.plugin_id, "error": str(exc)},
            )
        self.cache.clear()
        self.runtime_metadata = self._build_runtime_metadata()

    def _on_validate(self) -> bool:
        try:
            self.deployment_registry.get_all()
            return True
        except Exception as exc:
            self._record_error(f"Registry health check failed: {exc}")
            return False

    def _on_health(self) -> Dict[str, Any]:
        return {
            "registry_ready": self._is_registry_ready(),
            "loader_ready": self.model_loader is not None,
            "prediction_ready": self.prediction_engine is not None,
            "explainability_ready": self.explainability_adapter is not None,
            "configuration_ready": isinstance(self.configuration, dict),
        }

    def _on_reload(self) -> None:
        self._refresh_registry()
        self.runtime_metadata = self._build_runtime_metadata()

    def initialize(self) -> None:
        """Initialize SOAR runtime services and prepare the plugin context."""
        self.logger.info(
            "Runtime starting",
            extra={"plugin_id": self.plugin_id, "plugin_name": self.plugin_name},
        )
        self._clear_errors()

        self.deployment_registry.initialize()
        self.logger.info(
            "Registry initialized",
            extra={"plugin_id": self.plugin_id, "deployment_count": len(self.deployment_registry.get_all())},
        )

        self._startup_time = datetime.now(timezone.utc)
        self.runtime_metadata = self._build_runtime_metadata()
        self._initialized = True

        self.logger.info(
            "Prediction engine ready",
            extra={"plugin_id": self.plugin_id, "engine": type(self.prediction_engine).__name__},
        )
        self.logger.info(
            "Explainability ready",
            extra={"plugin_id": self.plugin_id, "adapter": type(self.explainability_adapter).__name__},
        )
        self.logger.info(
            "Runtime initialized",
            extra={"plugin_id": self.plugin_id, "plugin_version": self.plugin_version},
        )

    def shutdown(self) -> None:
        """Shutdown the runtime and release allocated resources."""
        self.logger.info(
            "Runtime shutdown",
            extra={"plugin_id": self.plugin_id, "plugin_name": self.plugin_name},
        )

        try:
            self.model_loader.unload_all()
        except Exception as exc:
            self._record_error(f"Model loader shutdown failed: {exc}")
            self.logger.error(
                "Model loader shutdown failed",
                extra={"plugin_id": self.plugin_id, "error": str(exc)},
            )

        self.cache.clear()
        self._initialized = False
        self._startup_time = None
        self.runtime_metadata = self._build_runtime_metadata()

    def health(self) -> RuntimeHealth:
        """Return the current runtime health status."""
        health = self._build_health()
        self.logger.info(
            "Runtime health checked",
            extra={"plugin_id": self.plugin_id, "healthy": health.healthy, "errors": health.errors},
        )
        return health

    def reload(self, configuration: Optional[Dict[str, Any]] = None) -> None:
        """Reload the runtime, refresh registry, and optionally reload configuration."""
        self.logger.info(
            "Runtime reload started",
            extra={"plugin_id": self.plugin_id},
        )

        if configuration is not None:
            self.reload_configuration(configuration)

        self._refresh_registry()
        self.runtime_metadata = self._build_runtime_metadata()

        self.logger.info(
            "Runtime reload completed",
            extra={"plugin_id": self.plugin_id, "deployment_count": len(self.deployment_registry.get_all())},
        )

    def reload_configuration(self, configuration: Optional[Dict[str, Any]] = None) -> None:
        """Reload plugin configuration without modifying runtime services."""
        self.logger.info(
            "Reloading configuration",
            extra={"plugin_id": self.plugin_id},
        )
        if configuration is None:
            return

        self.configuration = configuration
        self.runtime_metadata = self._build_runtime_metadata()

    def _build_runtime_metadata(self) -> RuntimeMetadata:
        return RuntimeMetadata(
            plugin_id=self.plugin_id,
            plugin_name=self.plugin_name,
            plugin_version=self.plugin_version,
            deployment_count=len(self.deployment_registry.get_all()) if self._initialized else 0,
            loaded_models=len(self.model_loader.loaded_models()),
            startup_time=self._startup_time,
            uptime_seconds=self._calculate_uptime_seconds(),
            created_at=self.created_at,
        )

    def _build_health(self) -> RuntimeHealth:
        registry_ready = self._is_registry_ready()
        loader_ready = self.model_loader is not None
        prediction_ready = self.prediction_engine is not None
        explainability_ready = self.explainability_adapter is not None
        configuration_ready = isinstance(self.configuration, dict)
        errors = list(self._errors)
        healthy = all([registry_ready, loader_ready, prediction_ready, explainability_ready, configuration_ready]) and not errors

        return RuntimeHealth(
            registry_ready=registry_ready,
            loader_ready=loader_ready,
            prediction_ready=prediction_ready,
            explainability_ready=explainability_ready,
            configuration_ready=configuration_ready,
            healthy=healthy,
            errors=errors,
            timestamp=datetime.now(timezone.utc),
        )

    def _refresh_registry(self) -> None:
        if hasattr(self.deployment_registry, "_initialized"):
            setattr(self.deployment_registry, "_initialized", False)
        self.deployment_registry.initialize()

    def _is_registry_ready(self) -> bool:
        try:
            self.deployment_registry.get_all()
            return True
        except Exception as exc:
            self._record_error(f"Registry health check failed: {exc}")
            return False

    def _calculate_uptime_seconds(self) -> float:
        if self._startup_time is None:
            return 0.0
        return (datetime.now(timezone.utc) - self._startup_time).total_seconds()

    def _clear_errors(self) -> None:
        self._errors = []

    def _record_error(self, message: str) -> None:
        self._errors.append(message)
