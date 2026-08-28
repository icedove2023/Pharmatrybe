"""ARMD Plugin Runtime Context.

Manages the ARMD adapter lifecycle, health checks, and provides
dependency injection for the prediction engine.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

from packages.prediction_framework.adapters import ARMDAdapter, ARMDAdapterError
from packages.prediction_framework.runtime import PredictionPluginRuntimeContext

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RuntimeHealth:
    """Health status of ARMD plugin runtime."""
    adapter_ready: bool
    registry_loaded: bool
    artifacts_loaded: bool
    healthy: bool
    errors: List[str]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class ARMDRuntimeContext(PredictionPluginRuntimeContext):
    """Dependency container and lifecycle manager for ARMD prediction plugin.
    
    Initializes and manages the ARMDAdapter, performs health checks,
    and provides access to loaded models and registries.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize runtime context.
        
        Args:
            config: Configuration dict (optional). Can contain:
                   - wp4_root: Path to deployments/ARMD
                   - enable_explainability: Whether to generate SHAP explanations
                   - cache_models: Whether to cache loaded models (default: True)
        """
        super().__init__(
            plugin_id="armd",
            plugin_name="ARMD Prediction Plugin",
            plugin_version="0.1.0",
            logger=logger,
        )
        self.config = config or {}
        self._adapter: Optional[ARMDAdapter] = None
        self._startup_time: Optional[datetime] = None
        logger.info("ARMD Runtime Context initialized")

    def _on_initialize(self) -> None:
        wp4_root = self.config.get('wp4_root')
        self._adapter = ARMDAdapter(wp4_root=wp4_root)
        self._adapter.initialize()
        if self._adapter.registry is None or len(self._adapter.registry) == 0:
            raise RuntimeError("Registry empty or not loaded")
        if self._adapter.artifacts is None:
            raise RuntimeError("Preprocessing artifacts not loaded")
        self._startup_time = datetime.now(timezone.utc)

    def _on_shutdown(self) -> None:
        self._adapter = None
        self._startup_time = None

    def _on_validate(self) -> bool:
        registry = self._adapter.registry if self._adapter is not None else None
        return registry is not None and len(registry) > 0

    def _on_health(self) -> Dict[str, Any]:
        return {
            'adapter_ready': self._adapter is not None,
            'registry_loaded': self._adapter is not None and self._adapter.registry is not None and len(self._adapter.registry) > 0,
            'artifacts_loaded': self._adapter is not None and self._adapter.artifacts is not None,
        }

    def _on_reload(self) -> None:
        if self._adapter:
            self._adapter.initialize()

    def initialize(self) -> None:
        """Initialize ARMD adapter and load registry/artifacts.
        
        Raises:
            RuntimeError: If adapter initialization fails
        """
        logger.info("Starting ARMD runtime initialization")
        self._clear_errors()
        
        try:
            wp4_root = self.config.get('wp4_root')
            self._adapter = ARMDAdapter(wp4_root=wp4_root)
            self._adapter.initialize()
            
            if self._adapter.registry is None or len(self._adapter.registry) == 0:
                raise RuntimeError("Registry empty or not loaded")
            
            if self._adapter.artifacts is None:
                raise RuntimeError("Preprocessing artifacts not loaded")
            
            self._startup_time = datetime.now(timezone.utc)
            self._initialized = True
            
            logger.info(
                f"ARMD runtime initialized with {len(self._adapter.registry)} antibiotics"
            )
            
        except ARMDAdapterError as e:
            msg = f"Adapter initialization failed: {e}"
            self._record_error(msg)
            logger.error(msg, exc_info=True)
            raise RuntimeError(msg) from e
        except Exception as e:
            msg = f"Unexpected error during initialization: {e}"
            self._record_error(msg)
            logger.error(msg, exc_info=True)
            raise RuntimeError(msg) from e

    def shutdown(self) -> None:
        """Shutdown runtime and release resources."""
        logger.info("Shutting down ARMD runtime")
        if self._adapter:
            # Clear cached models if needed
            self._adapter = None
        self._initialized = False
        self._startup_time = None

    def validate(self) -> bool:
        """Check if runtime is ready to accept predictions.
        
        Returns:
            True if adapter is initialized and registry is not empty
        """
        if not self._initialized or self._adapter is None:
            return False
        
        registry = self._adapter.registry
        return registry is not None and len(registry) > 0

    def health(self) -> RuntimeHealth:
        """Get current health status of the runtime.
        
        Returns:
            RuntimeHealth dataclass with component statuses
        """
        adapter_ready = self._adapter is not None
        registry_loaded = (
            self._adapter is not None
            and self._adapter.registry is not None
            and len(self._adapter.registry) > 0
        )
        artifacts_loaded = (
            self._adapter is not None
            and self._adapter.artifacts is not None
        )
        healthy = self._initialized and registry_loaded and artifacts_loaded
        
        status = RuntimeHealth(
            adapter_ready=adapter_ready,
            registry_loaded=registry_loaded,
            artifacts_loaded=artifacts_loaded,
            healthy=healthy,
            errors=self._errors.copy(),
        )
        
        logger.info(f"Health check: {status.healthy}")
        return status

    def reload(self) -> None:
        """Reload adapter and refresh registry.
        
        Useful for picking up newly deployed models without restart.
        """
        logger.info("Reloading ARMD runtime")
        if self._adapter:
            self._adapter.initialize()

    def _clear_errors(self) -> None:
        """Clear the error log."""
        self._errors.clear()

    def _record_error(self, message: str) -> None:
        """Record an error message."""
        self._errors.append(message)
        if len(self._errors) > 100:
            # Keep last 100 errors
            self._errors = self._errors[-100:]

    @property
    def adapter(self) -> Optional[ARMDAdapter]:
        """Access the initialized adapter (if available)."""
        return self._adapter

    @property
    def initialized(self) -> bool:
        """Check if runtime is initialized."""
        return self._initialized

    @property
    def uptime_seconds(self) -> float:
        """Get runtime uptime in seconds."""
        if self._startup_time is None:
            return 0.0
        return (datetime.now(timezone.utc) - self._startup_time).total_seconds()
