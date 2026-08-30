from __future__ import annotations

from typing import Any, Dict, Iterable, List

from app.plugins.identity import canonical_plugin_id
from app.plugins.manager.plugin_manager import PluginManager
from app.plugins.schema.discovery import SchemaDiscoveryService


class PluginSchemaComposer:
    """Compose multiple plugin input schemas into a single contract."""

    def __init__(self, manager: PluginManager) -> None:
        self.discovery = SchemaDiscoveryService(manager)

    def compose(self, plugin_ids: Iterable[str]) -> Dict[str, Any]:
        plugin_list = list(plugin_ids)
        if not plugin_list:
            raise ValueError("At least one plugin identifier is required")

        resolved: List[tuple[str, Dict[str, Any]]] = []
        for raw_id in plugin_list:
            plugin_id = canonical_plugin_id(raw_id)
            try:
                schema = self.discovery.get_plugin_schema(plugin_id)
            except KeyError as exc:
                raise ValueError(f"Unknown plugin: {plugin_id}") from exc
            resolved.append((plugin_id, schema))

        merged_properties: Dict[str, Any] = {}
        field_provenance: Dict[str, Dict[str, Any]] = {}
        required_fields: set[str] = set()
        conflicts: List[Dict[str, Any]] = []

        for plugin_id, schema in resolved:
            properties = schema.get("properties") or {}
            if not isinstance(properties, dict):
                continue
            required = schema.get("required") or []
            if isinstance(required, list):
                required_fields.update(str(item) for item in required)

            for field_name, field_schema in properties.items():
                if not isinstance(field_schema, dict):
                    continue
                if field_name not in merged_properties:
                    merged_properties[field_name] = dict(field_schema)
                    field_provenance[field_name] = {
                        "owners": [plugin_id],
                        "types": [field_schema.get("type")],
                    }
                    continue

                current = merged_properties[field_name]
                current_type = current.get("type")
                new_type = field_schema.get("type")
                merged_type = self._merge_types(current_type, new_type)
                if merged_type is not None:
                    current["type"] = merged_type

                owners = field_provenance.setdefault(field_name, {"owners": [], "types": []})
                if plugin_id not in owners["owners"]:
                    owners["owners"].append(plugin_id)
                owners["types"] = sorted({str(item) for item in owners["types"] + [new_type] if item is not None})

                if self._are_incompatible_types(current_type, new_type):
                    conflicts.append({
                        "field": field_name,
                        "owners": owners["owners"],
                        "types": [current_type, new_type],
                    })

        merged_schema = {
            "type": "object",
            "properties": merged_properties,
            "required": sorted(required_fields),
            "additionalProperties": True,
        }

        return {
            "schema": merged_schema,
            "field_provenance": field_provenance,
            "conflicts": conflicts,
        }

    @staticmethod
    def _merge_types(current_type: Any, new_type: Any) -> Any:
        if current_type is None:
            return new_type
        if new_type is None:
            return current_type
        if current_type == new_type:
            return current_type
        if {str(current_type), str(new_type)} <= {"integer", "number"}:
            return "integer"
        return current_type

    @staticmethod
    def _are_incompatible_types(current_type: Any, new_type: Any) -> bool:
        if current_type is None or new_type is None:
            return False
        left, right = str(current_type), str(new_type)
        if {left, right} <= {"integer", "number"}:
            return False
        return left != right
