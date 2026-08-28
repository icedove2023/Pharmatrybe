"""Shared prediction plugin runtime context and lifecycle management.

Provides a generic base class for managing plugin initialization, health checks,
error tracking, and uptime metrics. Plugin-specific implementations inherit from
this base to manage their own runtime state.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PluginRuntimeHealth:
    """Structured health status for a prediction plugin runtime.
    
    This is a plugin-agnostic health contract that all prediction plugins
    should implement to provide uniform health monitoring.
    
    Attributes:
        healthy: Overall health status
        initialized: Whether plugin has completed initialization
        errors: List of accumulated error messages (last N errors)
        timestamp: When this health status was captured
        metadata: Plugin-specific health metadata (optional)
    """
    healthy: bool
    initialized: bool
    errors: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)


class PredictionPluginRuntimeContext(ABC):
    """Base runtime context for prediction plugins.
    
    Provides generic lifecycle management, error tracking, health checks,
    and uptime metrics. Plugin-specific implementations inherit from this
    class and override abstract methods to provide plugin-specific behavior.
    
    Key responsibilities:
    - Initialize plugin dependencies in correct order
    - Shutdown and cleanup resources
    - Track runtime health and errors
    - Measure uptime
    - Provide logging integration
    
    Subclass contract:
    - Override _on_initialize() to load plugin-specific dependencies
    - Override _on_validate() to check plugin readiness
    - Override _on_shutdown() to cleanup plugin-specific resources
    - Call super().initialize(), super().validate(), super().shutdown()
    """

    def __init__(
        self,
        plugin_id: str,
        plugin_name: str,
        plugin_version: str,
        logger: Optional[Any] = None,
    ):
        """Initialize runtime context.
        
        Args:
            plugin_id: Unique plugin identifier (e.g., 'soar', 'armd')
            plugin_name: Human-readable plugin name
            plugin_version: Plugin version string
            logger: Optional logger instance (uses module logger if None)
        """
        self.plugin_id = plugin_id
        self.plugin_name = plugin_name
        self.plugin_version = plugin_version
        self.logger = logger or logging.getLogger(__name__)
        self._initialized = False
        self._startup_time: Optional[datetime] = None
        self._errors: List[str] = []

    def initialize(self) -> None:
        """Initialize plugin runtime.
        
        Calls _on_initialize() for subclass-specific initialization,
        then sets _initialized flag and startup time.
        
        Subclasses should override _on_initialize() to load their
        specific dependencies.
        
        Raises:
            RuntimeError: If initialization fails (from subclass)
        """
        self.logger.info(
            "Runtime initialization starting",
            extra={"plugin_id": self.plugin_id, "plugin_name": self.plugin_name},
        )
        self._clear_errors()

        try:
            # Call subclass-specific initialization
            self._on_initialize()

            # Mark as initialized
            self._startup_time = datetime.now(timezone.utc)
            self._initialized = True

            self.logger.info(
                "Runtime initialization complete",
                extra={"plugin_id": self.plugin_id, "uptime_ms": 0},
            )
        except Exception as e:
            msg = f"Runtime initialization failed: {str(e)}"
            self._record_error(msg)
            self.logger.error(msg, exc_info=True)
            raise

    def shutdown(self) -> None:
        """Shutdown plugin runtime and release resources.
        
        Calls _on_shutdown() for subclass-specific cleanup,
        then clears startup time and initialized flag.
        """
        self.logger.info(
            "Runtime shutdown starting",
            extra={"plugin_id": self.plugin_id},
        )

        try:
            # Call subclass-specific shutdown
            self._on_shutdown()

            # Clear state
            self._initialized = False
            self._startup_time = None

            self.logger.info("Runtime shutdown complete", extra={"plugin_id": self.plugin_id})
        except Exception as e:
            msg = f"Runtime shutdown error: {str(e)}"
            self._record_error(msg)
            self.logger.error(msg, exc_info=True)

    def validate(self) -> bool:
        """Check if plugin runtime is ready to accept requests.
        
        Returns True if:
        - Plugin has been initialized
        - _on_validate() returns True (subclass-specific checks)
        
        Subclasses should override _on_validate() to implement
        plugin-specific readiness checks.
        
        Returns:
            True if plugin is ready; False otherwise
        """
        if not self._initialized:
            return False

        try:
            return self._on_validate()
        except Exception as e:
            self.logger.error(
                "Validation check failed",
                extra={"plugin_id": self.plugin_id, "error": str(e)},
            )
            return False

    def health(self) -> PluginRuntimeHealth:
        """Get current health status of the plugin runtime.
        
        Returns a structured health report combining generic status
        (healthy, initialized, errors, timestamp) with plugin-specific
        metadata from _on_health().
        
        Returns:
            PluginRuntimeHealth dataclass with current status
        """
        # Get plugin-specific health metadata
        plugin_metadata = {}
        try:
            plugin_metadata = self._on_health() or {}
        except Exception as e:
            self.logger.error("Health metadata collection failed", exc_info=True)

        # Combine with generic health info
        overall_healthy = self._initialized and len(self._errors) == 0

        return PluginRuntimeHealth(
            healthy=overall_healthy,
            initialized=self._initialized,
            errors=self._errors.copy(),
            timestamp=datetime.now(timezone.utc),
            metadata=plugin_metadata,
        )

    def reload(self) -> None:
        """Reload plugin configuration and state without full restart.
        
        Default implementation calls _on_reload(). Subclasses should
        override _on_reload() to implement reload behavior
        (e.g., refresh registry, reload models, etc.)
        """
        self.logger.info("Runtime reload starting", extra={"plugin_id": self.plugin_id})

        try:
            self._on_reload()
            self.logger.info("Runtime reload complete", extra={"plugin_id": self.plugin_id})
        except Exception as e:
            msg = f"Runtime reload failed: {str(e)}"
            self._record_error(msg)
            self.logger.error(msg, exc_info=True)
            raise

    # Abstract methods for subclasses to override

    @abstractmethod
    def _on_initialize(self) -> None:
        """Plugin-specific initialization logic.
        
        Called by initialize(). Subclass should load all dependencies,
        registries, models, etc. here.
        
        Raises:
            RuntimeError: If initialization cannot complete
        """
        pass

    @abstractmethod
    def _on_shutdown(self) -> None:
        """Plugin-specific shutdown logic.
        
        Called by shutdown(). Subclass should cleanup resources,
        close connections, etc. here.
        """
        pass

    @abstractmethod
    def _on_validate(self) -> bool:
        """Plugin-specific validation logic.
        
        Called by validate(). Subclass should check whether all
        required components are ready (registry loaded, models available, etc.)
        
        Returns:
            True if plugin is ready; False otherwise
        """
        pass

    def _on_health(self) -> Dict[str, Any]:
        """Plugin-specific health metadata.
        
        Called by health(). Subclass can return additional metadata
        that will be included in the health status (e.g., number of
        loaded models, registry size, etc.)
        
        Returns:
            Dictionary of plugin-specific health metrics (default: empty dict)
        """
        return {}

    def _on_reload(self) -> None:
        """Plugin-specific reload logic.
        
        Called by reload(). Subclass can refresh registry, reload models, etc.
        Default implementation does nothing.
        """
        pass

    # Error tracking utilities

    def _clear_errors(self) -> None:
        """Clear the error log."""
        self._errors.clear()

    def _record_error(self, message: str) -> None:
        """Record an error message.
        
        Maintains a rolling list of errors (last 100).
        
        Args:
            message: Error message to record
        """
        self._errors.append(message)
        if len(self._errors) > 100:
            # Keep only last 100 errors
            self._errors = self._errors[-100:]

    # Uptime tracking

    @property
    def uptime_seconds(self) -> float:
        """Get runtime uptime in seconds.
        
        Returns:
            Uptime in seconds; 0.0 if not yet initialized
        """
        if self._startup_time is None:
            return 0.0
        return (datetime.now(timezone.utc) - self._startup_time).total_seconds()

    @property
    def initialized(self) -> bool:
        """Check if runtime is fully initialized.
        
        Returns:
            True if initialize() has been called and completed successfully
        """
        return self._initialized
