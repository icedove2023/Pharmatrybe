from __future__ import annotations

from typing import Any, Dict, List

from app.plugins.identity import canonical_plugin_id
from app.plugins.manager.plugin_manager import PluginManager


class SchemaDiscoveryService:
    """Resolve plugin input schemas from the live plugin registry."""

    def __init__(self, manager: PluginManager) -> None:
        self.manager = manager

    def get_available_plugin_schemas(self) -> List[Dict[str, Any]]:
        """Return schemas for all currently loaded plugins."""
        items: List[Dict[str, Any]] = []
        for plugin in sorted(self.manager.list_plugins(), key=lambda item: item.plugin_id):
            schema = self.get_plugin_schema(plugin.plugin_id)
            items.append({
                "plugin_id": plugin.plugin_id,
                "plugin_name": plugin.plugin_name,
                "schema": schema,
            })
        return items

    def get_plugin_schema(self, plugin_id: str) -> Dict[str, Any]:
        """Return a valid JSON Schema for a single plugin."""
        normalized = canonical_plugin_id(plugin_id)
        plugin = self.manager.retrieve_plugin(normalized)
        if plugin is None:
            raise KeyError(f"Plugin not registered: {normalized}")
        schema = plugin.input_schema()
        if not isinstance(schema, dict):
            raise ValueError(f"Plugin {normalized} did not return a JSON Schema object")
        normalized_schema = self._normalize_schema(schema)
        normalized_schema.setdefault("$schema", "https://json-schema.org/draft/2020-12/schema")
        return normalized_schema

    @staticmethod
    def _normalize_schema(schema: Dict[str, Any]) -> Dict[str, Any]:
        normalized = dict(schema)
        if "type" not in normalized:
            normalized["type"] = "object"
        if normalized.get("type") == "object":
            properties = normalized.get("properties")
            if not isinstance(properties, dict):
                normalized["properties"] = {}
            normalized.setdefault("additionalProperties", True)
        return normalized
