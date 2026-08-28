"""Base class for prediction plugins implementing the platform interface.

Provides a generic implementation of PredictionPlugin interface that delegates
to a runtime context. Plugin-specific implementations inherit from this class
and only need to define plugin metadata and override _create_runtime_context().
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Any, Dict, List, Optional
import logging

from app.plugins.base.prediction_plugin import (
    PredictionPlugin,
    PredictionRequest,
    PredictionResult,
    DeploymentType,
)
from app.plugins.base.plugin import PluginType, PluginMetadata, PluginHealth

from .runtime import PredictionPluginRuntimeContext, PluginRuntimeHealth

logger = logging.getLogger(__name__)


class BasePredictionPlugin(PredictionPlugin):
    """Base implementation of PredictionPlugin interface.
    
    Provides common plugin lifecycle management (initialize, shutdown, validate,
    health, reload, metadata) by delegating to a PredictionPluginRuntimeContext.
    
    Subclasses need to:
    1. Define plugin metadata properties (plugin_id, plugin_name, etc.)
    2. Override _create_runtime_context() to instantiate their runtime context
    3. Override _create_prediction_result() to map runtime results to platform format
    
    The predict() method is implemented generically and delegates to the
    runtime context's predict() capability (which subclasses define).
    
    Example subclass:
        class MyPredictionPlugin(BasePredictionPlugin):
            @property
            def plugin_id(self) -> str:
                return "my_plugin"
            
            @property
            def plugin_name(self) -> str:
                return "My Prediction Plugin"
            
            def _create_runtime_context(self) -> PredictionPluginRuntimeContext:
                return MyRuntimeContext(
                    plugin_id=self.plugin_id,
                    plugin_name=self.plugin_name,
                    plugin_version=self.plugin_version,
                    config=self.config,
                )
            
            def predict(self, request: PredictionRequest) -> PredictionResult:
                runtime_result = self._runtime_context.predict(request)
                return self._create_prediction_result(runtime_result)
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize base prediction plugin.
        
        Args:
            config: Plugin configuration dictionary (optional)
        """
        super().__init__()
        self.config = config or {}
        self._runtime_context: Optional[PredictionPluginRuntimeContext] = None
        self._initialized = False
        logger.info(f"Plugin {self.plugin_id} instantiated")

    @property
    @abstractmethod
    def plugin_id(self) -> str:
        """Unique plugin identifier."""
        pass

    @property
    @abstractmethod
    def plugin_name(self) -> str:
        """Human-readable plugin name."""
        pass

    @property
    def plugin_version(self) -> str:
        """Plugin version string. Override if needed."""
        return "0.1.0"

    @property
    def plugin_type(self) -> PluginType:
        """Plugin type. Override if implementing non-PREDICTION plugins."""
        return PluginType.PREDICTION

    @property
    @abstractmethod
    def plugin_description(self) -> str:
        """Human-readable plugin description."""
        pass

    @property
    def author(self) -> str:
        """Plugin author. Override if needed."""
        return "PharmaTrybe"

    @property
    @abstractmethod
    def capabilities(self) -> List[str]:
        """List of plugin capabilities (e.g., ['prediction', 'explainability'])."""
        pass

    @property
    def deployment_type(self) -> DeploymentType:
        """Deployment type (ARTIFACT, API, etc.). Override if needed."""
        return DeploymentType.ARTIFACT

    def initialize(self) -> None:
        """Initialize plugin: create runtime context and call its initialize().
        
        After this method completes, the plugin should be ready to accept
        prediction requests.
        
        Raises:
            RuntimeError: If initialization fails
        """
        logger.info(f"Plugin {self.plugin_id} initialization starting")

        try:
            # Create plugin-specific runtime context
            self._runtime_context = self._create_runtime_context()

            # Initialize the runtime context
            self._runtime_context.initialize()

            self._initialized = True
            logger.info(f"Plugin {self.plugin_id} initialization complete")

        except Exception as e:
            self._initialized = False
            logger.error(f"Plugin {self.plugin_id} initialization failed", exc_info=True)
            raise

    def shutdown(self) -> None:
        """Shutdown plugin and release resources.
        
        Calls shutdown() on the runtime context if available.
        """
        logger.info(f"Plugin {self.plugin_id} shutdown starting")

        try:
            if self._runtime_context:
                self._runtime_context.shutdown()
            self._initialized = False
            logger.info(f"Plugin {self.plugin_id} shutdown complete")
        except Exception as e:
            logger.error(f"Plugin {self.plugin_id} shutdown error", exc_info=True)

    def validate(self) -> bool:
        """Check if plugin is ready to accept prediction requests.
        
        Returns:
            True if plugin is initialized and runtime context validates successfully
        """
        if not self._initialized or not self._runtime_context:
            return False

        return self._runtime_context.validate()

    def health(self) -> PluginHealth:
        """Get plugin health status.
        
        Returns:
            PluginHealth with status, errors, and metadata
        """
        if not self._runtime_context:
            return PluginHealth(
                plugin_id=self.plugin_id,
                status="unhealthy",
                initialized=False,
                errors=["Runtime context not initialized"],
                timestamp=None,
                metadata={},
            )

        runtime_health: PluginRuntimeHealth = self._runtime_context.health()

        return PluginHealth(
            plugin_id=self.plugin_id,
            status="healthy" if runtime_health.healthy else "unhealthy",
            initialized=runtime_health.initialized,
            errors=runtime_health.errors,
            timestamp=runtime_health.timestamp,
            metadata=runtime_health.metadata or {},
        )

    @abstractmethod
    def predict(self, request: PredictionRequest) -> PredictionResult:
        """Execute prediction for a patient.
        
        Subclasses should override this to:
        1. Validate that plugin is initialized
        2. Call runtime_context.predict() or similar
        3. Map runtime result to PredictionResult using _create_prediction_result()
        
        Args:
            request: Platform PredictionRequest
            
        Returns:
            PredictionResult following platform contract
            
        Raises:
            RuntimeError: If plugin not initialized or prediction fails
        """
        pass

    def reload(self) -> None:
        """Reload plugin configuration and state without restart.
        
        Useful for picking up newly deployed models without restarting.
        Delegates to runtime context's reload() method.
        """
        logger.info(f"Plugin {self.plugin_id} reload starting")

        try:
            if self._runtime_context:
                self._runtime_context.reload()
            logger.info(f"Plugin {self.plugin_id} reload complete")
        except Exception as e:
            logger.error(f"Plugin {self.plugin_id} reload failed", exc_info=True)
            raise

    def metadata(self) -> PluginMetadata:
        """Get plugin metadata describing capabilities, version, etc.
        
        Returns:
            PluginMetadata with plugin information
        """
        return PluginMetadata(
            plugin_id=self.plugin_id,
            name=self.plugin_name,
            version=self.plugin_version,
            plugin_type=self.plugin_type,
            description=self.plugin_description,
            author=self.author,
            capabilities=self.capabilities,
            dependencies=[],
            configuration_schema=self._get_configuration_schema(),
            extra_metadata={
                "deployment_type": self.deployment_type.value,
            },
        )

    def _get_configuration_schema(self) -> Dict[str, Any]:
        """Get configuration schema for this plugin.
        
        Can be overridden by subclasses to provide plugin-specific
        configuration validation schema (JSON Schema format).
        
        Returns:
            Configuration schema dictionary (default: empty object)
        """
        return {"type": "object", "additionalProperties": True}

    # Abstract methods for subclasses

    @abstractmethod
    def _create_runtime_context(self) -> PredictionPluginRuntimeContext:
        """Create and return plugin-specific runtime context.
        
        Called by initialize(). Subclass should instantiate and return
        their specific runtime context implementation.
        
        Returns:
            Initialized (but not yet started) runtime context
        """
        pass

    @abstractmethod
    def _create_prediction_result(self, runtime_result: Any) -> PredictionResult:
        """Map plugin-specific runtime result to platform PredictionResult.
        
        Called by predict(). Subclass should convert internal representation
        to the platform's expected PredictionResult format.
        
        Args:
            runtime_result: Plugin's internal prediction result
            
        Returns:
            PredictionResult matching platform contract
        """
        pass

    # Utility properties

    @property
    def runtime_context(self) -> Optional[PredictionPluginRuntimeContext]:
        """Access the runtime context (if initialized)."""
        return self._runtime_context
