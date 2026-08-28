from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from app.plugins.base.plugin import BasePlugin, PluginHealth, PluginMetadata, PluginType
from app.plugins.discovery.plugin_loader import PluginLoader, PluginLoadResult
from app.plugins.discovery.plugin_validator import PluginValidator
from app.plugins.manager.plugin_registry import PluginRegistry
from app.plugins.security.isolated_executor import IsolatedPluginExecutor
from app.auth.tenant_context import TenantContext


class PluginManager:
    """Orchestrates discovery, validation, loading, and management of plugins."""

    def __init__(
        self,
        plugin_root: Path,
        platform_version: str,
        sdk_version: str,
        governance_service=None,
        hospital_id: str | None = None,
        tenant_context: TenantContext | None = None,
    ) -> None:
        if hospital_id is not None:
            if tenant_context is None or hospital_id != tenant_context.hospital_id:
                raise ValueError("TENANT_MISMATCH")
        if governance_service is not None and tenant_context is None:
            raise ValueError("TenantContext is required for governed plugin runtime")
        resolved_tenant = tenant_context or TenantContext.system()
        self.registry = PluginRegistry(governance_service, require_governance=True)
        self.validator = PluginValidator()
        self.loader = PluginLoader(
            plugin_root,
            self.registry,
            self.validator,
            platform_version,
            sdk_version,
            resolved_tenant,
            IsolatedPluginExecutor(),
        )

    def load_all_plugins(self) -> List[PluginLoadResult]:
        """Load every plugin discovered in the configured plugin root."""
        return self.loader.load_all_plugins()

    def enable_plugin(self, plugin_id: str) -> None:
        """Enable a registered plugin."""
        self.registry.enable_plugin(plugin_id)

    def disable_plugin(self, plugin_id: str) -> None:
        """Disable a registered plugin."""
        self.registry.disable_plugin(plugin_id)

    def reload_plugin(self, plugin_id: str) -> PluginLoadResult:
        """Reload a registered plugin by unloading and loading it again."""
        plugin_path = self.loader.get_plugin_path(plugin_id)
        if plugin_path is None:
            raise KeyError(f"Plugin path not available for reload: {plugin_id}")

        self.unload_plugin(plugin_id)
        return self.loader.load_plugin(plugin_path)

    def unload_plugin(self, plugin_id: str) -> None:
        """Unload a registered plugin."""
        plugin = self.registry.get_plugin(plugin_id)
        if plugin is None:
            raise KeyError(f"Plugin not registered: {plugin_id}")

        plugin.shutdown()
        self.registry.unregister_plugin(plugin_id)

    def retrieve_plugin(self, plugin_id: str) -> Optional[BasePlugin]:
        """Return the plugin instance for the given ID."""
        return self.registry.get_plugin(plugin_id)

    def retrieve_plugin_metadata(self, plugin_id: str) -> Optional[PluginMetadata]:
        """Return structured metadata for a registered plugin."""
        plugin = self.registry.get_plugin(plugin_id)
        if plugin is None:
            return None
        return plugin.metadata()

    def retrieve_plugin_health(self, plugin_id: str) -> Optional[PluginHealth]:
        """Return the current health status for a registered plugin."""
        plugin = self.registry.get_plugin(plugin_id)
        if plugin is None:
            return None
        return plugin.health()

    def list_plugins(self) -> List[BasePlugin]:
        """Return all registered plugins."""
        return self.registry.list_plugins()

    def group_plugins_by_type(self) -> Dict[PluginType, List[BasePlugin]]:
        """Return registered plugins grouped by category."""
        return self.registry.group_plugins_by_type()
