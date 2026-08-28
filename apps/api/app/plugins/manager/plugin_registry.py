from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional

from app.plugins.base.plugin import BasePlugin, PluginHealth, PluginMetadata, PluginType
from app.plugins.contracts.plugin_manifest import PluginManifest
from app.auth.tenant_context import TenantContext
from app.plugins.identity import canonical_plugin_id, is_internal_plugin


@dataclass
class PluginRegistryEntry:
    """Entry stored in the plugin registry."""

    manifest: PluginManifest
    plugin: BasePlugin
    owner_hospital_id: str | None = None
    enabled: bool = True


class PluginRegistry:
    """In-memory catalog of registered PharmaTrybe plugins."""

    def __init__(self, governance_service=None, *, require_governance: bool = False) -> None:
        self._entries: Dict[str, PluginRegistryEntry] = {}
        self._tenant_entries: Dict[tuple[str, str], PluginRegistryEntry] = {}
        self.governance_service = governance_service
        self.require_governance = require_governance

    def register_plugin(
        self,
        manifest: PluginManifest,
        plugin: BasePlugin,
        enabled: bool = True,
        owner_hospital_id: str | None = None,
    ) -> None:
        """Register a plugin in the registry."""
        canonical_id = canonical_plugin_id(manifest.plugin_id)
        if is_internal_plugin(canonical_id):
            owner_hospital_id = None
        elif self.governance_service is not None and not owner_hospital_id:
            raise ValueError("Hospital ownership is required for governed plugins")
        if owner_hospital_id is None:
            key = canonical_id
            duplicate = key in self._entries
        else:
            key = (canonical_id, owner_hospital_id)
            duplicate = key in self._tenant_entries
        if duplicate:
            raise ValueError(f"Plugin already registered: {canonical_id}")
        manifest.plugin_id = canonical_id
        entry = PluginRegistryEntry(
            manifest=manifest,
            plugin=plugin,
            owner_hospital_id=owner_hospital_id,
            enabled=enabled,
        )
        if owner_hospital_id is None:
            self._entries[key] = entry
        else:
            self._tenant_entries[key] = entry

    def unregister_plugin(self, plugin_id: str) -> None:
        """Remove a plugin from the registry."""
        canonical_id = canonical_plugin_id(plugin_id)
        self._entries.pop(canonical_id, None)
        for key in [key for key in self._tenant_entries if key[0] == canonical_id]:
            self._tenant_entries.pop(key, None)

    def get_plugin(self, plugin_id: str) -> Optional[BasePlugin]:
        """Return the plugin instance for the given plugin ID."""
        entry = self._entries.get(canonical_plugin_id(plugin_id))
        return entry.plugin if entry else None

    def get_manifest(self, plugin_id: str) -> Optional[PluginManifest]:
        """Return the manifest for the given plugin ID."""
        entry = self._entries.get(canonical_plugin_id(plugin_id))
        return entry.manifest if entry else None

    def get_metadata(self, plugin_id: str) -> Optional[PluginMetadata]:
        """Return structured metadata for a registered plugin."""
        plugin = self.get_plugin(plugin_id)
        if plugin is None:
            return None
        return plugin.metadata()

    def get_health(self, plugin_id: str) -> Optional[PluginHealth]:
        """Return the health status for a registered plugin."""
        plugin = self.get_plugin(plugin_id)
        if plugin is None:
            return None
        return plugin.health()

    def list_plugins(self) -> List[BasePlugin]:
        """Return all registered plugin instances."""
        return [entry.plugin for entry in self._all_entries()]

    def list_manifests(self) -> List[PluginManifest]:
        """Return all registered plugin manifests."""
        return [entry.manifest for entry in self._all_entries()]

    def group_plugins_by_type(self) -> Dict[PluginType, List[BasePlugin]]:
        """Group registered plugins by their type."""
        grouped: Dict[PluginType, List[BasePlugin]] = {}
        for entry in self._all_entries():
            grouped.setdefault(entry.manifest.plugin_type, []).append(entry.plugin)
        return grouped

    def enable_plugin(self, plugin_id: str) -> None:
        """Enable a registered plugin."""
        entry = self._entries.get(plugin_id)
        if entry is None:
            raise KeyError(f"Plugin not registered: {plugin_id}")
        entry.enabled = True

    def disable_plugin(self, plugin_id: str) -> None:
        """Disable a registered plugin."""
        entry = self._entries.get(plugin_id)
        if entry is None:
            raise KeyError(f"Plugin not registered: {plugin_id}")
        entry.enabled = False

    def is_enabled(self, plugin_id: str) -> bool:
        """Return whether a registered plugin is enabled."""
        entry = self._entries.get(plugin_id)
        return bool(entry and entry.enabled)

    def is_runtime_eligible(self, plugin_id: str, hospital_id: str | None = None) -> bool:
        """Return whether a plugin is eligible to execute under the governance boundary."""
        if self.governance_service is not None:
            return self.governance_service.is_runtime_eligible(plugin_id, hospital_id=hospital_id)
        return not self.require_governance and is_internal_plugin(plugin_id)

    def resolve_plugin(self, tenant_context: TenantContext, plugin_id: str) -> Optional[BasePlugin]:
        """Resolve a plugin only within the authenticated tenant or system scope."""
        canonical_id = canonical_plugin_id(plugin_id)
        if is_internal_plugin(canonical_id):
            if not tenant_context.system_owned:
                return None
            entry = self._entries.get(canonical_id)
        else:
            if tenant_context.system_owned:
                raise ValueError("TENANT_CONTEXT_REQUIRED")
            entry = self._tenant_entries.get((canonical_id, tenant_context.hospital_id))
        plugin = entry.plugin if entry else None
        if plugin is None:
            return None
        if is_internal_plugin(canonical_id):
            return plugin
        if self.governance_service is None:
            raise ValueError("TENANT_CONTEXT_REQUIRED")
        if not self.governance_service.is_runtime_eligible(canonical_id, hospital_id=tenant_context.hospital_id):
            raise ValueError("TENANT_MISMATCH")
        return plugin

    def get_plugin_for_tenant(self, tenant_context: TenantContext, plugin_id: str) -> Optional[BasePlugin]:
        """Return a tenant-owned entry for bounded denial auditing only."""
        canonical_id = canonical_plugin_id(plugin_id)
        if is_internal_plugin(canonical_id):
            return self._entries.get(canonical_id).plugin if tenant_context.system_owned and canonical_id in self._entries else None
        if tenant_context.system_owned:
            return None
        entry = self._tenant_entries.get((canonical_id, tenant_context.hospital_id))
        return entry.plugin if entry else None

    def is_hospital_owned(self, plugin: BasePlugin) -> bool:
        """Return whether an instance belongs to a hospital-scoped registry entry."""
        return any(entry.plugin is plugin for entry in self._tenant_entries.values())

    def can_admit_manifest(self, plugin_id: str, *, hospital_id: str | None = None) -> bool:
        """Check admission before plugin code is imported or initialized."""
        if self.governance_service is not None:
            return self.governance_service.is_runtime_eligible(plugin_id, hospital_id=hospital_id)
        return is_internal_plugin(plugin_id)

    def list_runtime_plugins(self, hospital_id: str | None = None) -> List[BasePlugin]:
        """Return only plugins currently eligible for runtime execution."""
        selected = []
        for entry in self._all_entries():
            if not entry.enabled:
                continue
            if self.governance_service is not None:
                if not self.governance_service.is_runtime_eligible(entry.manifest.plugin_id, hospital_id=hospital_id):
                    continue
            selected.append(entry.plugin)
        return selected

    def _all_entries(self) -> Iterable[PluginRegistryEntry]:
        """Return legacy and tenant-scoped entries for internal routing only."""
        return (*self._entries.values(), *self._tenant_entries.values())

    def _routing_entries(self) -> Dict[tuple[str, str | None], PluginRegistryEntry]:
        """Expose a collision-safe view to the routing policy."""
        entries = {(plugin_id, None): entry for plugin_id, entry in self._entries.items()}
        entries.update(self._tenant_entries)
        return entries
