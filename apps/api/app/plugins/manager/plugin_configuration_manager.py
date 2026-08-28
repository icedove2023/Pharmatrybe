from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Dict, Optional

from pydantic import BaseModel, ValidationError, create_model

from app.plugins.contracts.plugin_manifest import PluginManifest


@dataclass
class PluginConfiguration:
    """Validated plugin configuration for runtime use."""

    plugin_id: str
    configuration: Dict[str, Any]


class PluginConfigurationManager:
    """Manages loading and validating plugin configuration."""

    def __init__(self) -> None:
        self._configurations: Dict[str, PluginConfiguration] = {}

    def load_configuration(
        self,
        plugin_manifest: PluginManifest,
        configuration: Optional[Dict[str, Any]] = None,
    ) -> PluginConfiguration:
        """Load and validate plugin configuration using the manifest schema."""
        if configuration is None:
            configuration = {}

        validated = self._validate_configuration(plugin_manifest, configuration)
        config = PluginConfiguration(plugin_id=plugin_manifest.plugin_id, configuration=validated)
        self._configurations[plugin_manifest.plugin_id] = config
        return config

    def get_configuration(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        """Return the validated configuration for a plugin."""
        entry = self._configurations.get(plugin_id)
        return deepcopy(entry.configuration) if entry else None

    def unload_configuration(self, plugin_id: str) -> None:
        """Remove the configuration for a plugin."""
        self._configurations.pop(plugin_id, None)

    def _validate_configuration(self, plugin_manifest: PluginManifest, configuration: Dict[str, Any]) -> Dict[str, Any]:
        schema = plugin_manifest.configuration_schema
        if schema is None:
            return deepcopy(configuration)

        model = self._build_validation_model(plugin_manifest.plugin_id, schema)
        try:
            validated = model(**configuration)
        except ValidationError as exc:
            raise ValueError(f"Plugin configuration validation failed: {exc}") from exc
        return validated.model_dump()

    def _build_validation_model(self, plugin_id: str, schema: Dict[str, Any]) -> type[BaseModel]:
        fields: Dict[str, tuple[Any, Any]] = {}
        for key, value in schema.items():
            if isinstance(value, dict) and "default" in value and "type" in value:
                field_type = value["type"]
                default_value = value["default"]
            else:
                field_type = Any
                default_value = ...
            fields[key] = (field_type, default_value)
        return create_model(f"PluginConfig_{plugin_id}", **fields)
