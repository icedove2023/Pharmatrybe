from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class PluginType(Enum):
    """Enumeration of supported PharmaTrybe plugin categories."""

    PREDICTION = "prediction"
    KNOWLEDGE = "knowledge"
    RISK = "risk"
    RULES = "rules"
    REPORTING = "reporting"
    INTEGRATION = "integration"


@dataclass(frozen=True)
class PluginMetadata:
    """Structured metadata for a PharmaTrybe plugin."""

    plugin_id: str
    plugin_name: str
    plugin_version: str
    plugin_type: PluginType
    description: str
    author: str
    capabilities: List[str]
    dependencies: List[str]


@dataclass(frozen=True)
class PluginHealth:
    """Structured health information for a PharmaTrybe plugin."""

    healthy: bool
    status: str
    message: Optional[str]
    timestamp: datetime


class BasePlugin(ABC):
    """Base plugin interface for all PharmaTrybe plugins.

    The BasePlugin defines the minimum lifecycle, configuration, metadata,
    validation, and health contract that every plugin implementation must
    provide. Plugins inherit from this base class and are managed by the
    Plugin Manager and Plugin Loader.
    """

    @property
    @abstractmethod
    def plugin_id(self) -> str:
        """Unique plugin identifier."""
        raise NotImplementedError

    @property
    @abstractmethod
    def plugin_name(self) -> str:
        """Human-readable plugin name."""
        raise NotImplementedError

    @property
    @abstractmethod
    def plugin_version(self) -> str:
        """Plugin version string."""
        raise NotImplementedError

    @property
    @abstractmethod
    def plugin_type(self) -> PluginType:
        """Plugin category type."""
        raise NotImplementedError

    @property
    @abstractmethod
    def plugin_description(self) -> str:
        """Plugin description."""
        raise NotImplementedError

    @property
    @abstractmethod
    def author(self) -> str:
        """Plugin author or owner."""
        raise NotImplementedError

    @property
    @abstractmethod
    def capabilities(self) -> List[str]:
        """Plugin capabilities exposed to the platform."""
        raise NotImplementedError

    @property
    @abstractmethod
    def dependencies(self) -> List[str]:
        """Plugin dependencies declared by the plugin."""
        raise NotImplementedError

    @abstractmethod
    def initialize(self) -> None:
        """Initialize plugin resources.

        This method is called once after the plugin has been instantiated and
        its configuration has been loaded. Implementations should perform any
        startup tasks required before the plugin is ready to serve evidence or
        receive requests.
        """
        raise NotImplementedError

    @abstractmethod
    def shutdown(self) -> None:
        """Shutdown plugin resources.

        This method is called during platform or plugin teardown. Implementations
        should release resources, close external connections, and perform any
        cleanup needed for safe shutdown.
        """
        raise NotImplementedError

    @abstractmethod
    def configure(self, configuration: Dict[str, Any]) -> None:
        """Configure the plugin with platform-provided settings.

        Parameters:
            configuration: A dictionary containing plugin-specific configuration
                values such as endpoints, credentials, timeouts, or deployment
                settings.
        """
        raise NotImplementedError

    @abstractmethod
    def validate(self) -> bool:
        """Validate plugin readiness and configuration.

        Returns:
            True when the plugin is valid and ready for use.

        Raises:
            Exception: If validation fails due to missing configuration,
                incompatible dependencies, or other plugin-specific issues.
        """
        raise NotImplementedError

    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Return structured plugin metadata."""
        raise NotImplementedError

    @abstractmethod
    def health(self) -> PluginHealth:
        """Return structured plugin health status."""
        raise NotImplementedError
