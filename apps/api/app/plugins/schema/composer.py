from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Iterable, List

from app.plugins.identity import canonical_plugin_id
from app.plugins.manager.plugin_manager import PluginManager
from app.plugins.schema.discovery import SchemaDiscoveryService
from app.plugins.schema.clinical_registry import canonical_field_metadata, canonical_plugin_mappings


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
        runtime_mappings: Dict[str, Any] = {}

        for plugin_id, schema in resolved:
            runtime_mappings[plugin_id] = schema.get("x-plugin-runtime-mappings", {})
            properties = self._schema_properties(schema)
            if not isinstance(properties, dict):
                continue
            required = self._schema_required(schema)

            for field_name, field_schema in properties.items():
                if not isinstance(field_schema, dict):
                    continue
                current = merged_properties.get(field_name)
                output_name = field_name if current is None or self._fields_compatible(current, field_schema) else f"{plugin_id}__{field_name}"
                if current is not None and output_name != field_name:
                    conflicts.append(self._conflict(field_name, plugin_id, current, field_schema, field_provenance))
                if output_name not in merged_properties:
                    merged_properties[output_name] = deepcopy(field_schema)
                    field_provenance[output_name] = self._provenance(plugin_id, field_name, field_schema)
                else:
                    owners = field_provenance[output_name]["owners"]
                    if plugin_id not in owners:
                        owners.append(plugin_id)
                    field_provenance[output_name]["field_names"].append(field_name)
                if isinstance(required, list) and field_name in required:
                    required_fields.add(output_name)

        merged_schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "properties": merged_properties,
            "required": sorted(required_fields),
            "additionalProperties": True,
        }
        field_provenance["__plugin_contract__"] = {
            "owners": [plugin_id for plugin_id, _ in resolved],
            "field_names": [],
            "canonical_field_id": None,
            "mapping_classification": "PLUGIN_CONTRACT",
            "types": [],
        }

        return {
            "schema": merged_schema,
            "composed_schema": merged_schema,
            "field_provenance": field_provenance,
            "conflicts": conflicts,
            "canonical_field_metadata": canonical_field_metadata(),
            "plugin_runtime_mappings": runtime_mappings,
            "canonical_plugin_mappings": canonical_plugin_mappings(),
        }

    @staticmethod
    def _provenance(plugin_id: str, field_name: str, field_schema: Dict[str, Any]) -> Dict[str, Any]:
        return {"owners": [plugin_id], "field_names": [field_name], "canonical_field_id": field_schema.get("x-canonical-field-id"), "mapping_classification": field_schema.get("x-mapping-classification"), "types": [field_schema.get("type")]}

    @staticmethod
    def _schema_properties(schema: Dict[str, Any]) -> Dict[str, Any]:
        properties = schema.get("properties")
        if isinstance(properties, dict) and properties:
            return properties
        variants = schema.get("oneOf") or schema.get("anyOf")
        if not isinstance(variants, list):
            return {}
        merged: Dict[str, Any] = {}
        for variant in variants:
            if isinstance(variant, dict) and isinstance(variant.get("properties"), dict):
                merged.update(variant["properties"])
        return merged

    @staticmethod
    def _schema_required(schema: Dict[str, Any]) -> List[str]:
        required = schema.get("required")
        if isinstance(required, list):
            return [str(item) for item in required]
        variants = schema.get("oneOf") or schema.get("anyOf")
        if not isinstance(variants, list):
            return []
        required_sets = [set(item.get("required", [])) for item in variants if isinstance(item, dict) and isinstance(item.get("required"), list)]
        return sorted(set.intersection(*required_sets)) if required_sets else []

    @classmethod
    def _fields_compatible(cls, left: Dict[str, Any], right: Dict[str, Any]) -> bool:
        if not left.get("x-canonical-field-id") or left.get("x-canonical-field-id") != right.get("x-canonical-field-id"):
            return False
        if left.get("type") != right.get("type") or left.get("x-unit") != right.get("x-unit") or left.get("enum") != right.get("enum") or left.get("x-clinical-semantics") != right.get("x-clinical-semantics"):
            return False
        left_class = left.get("x-mapping-classification")
        right_class = right.get("x-mapping-classification")
        if left_class in {"SEMANTIC_CONFLICT", "PLUGIN_SPECIFIC", "UNRESOLVED"} or right_class in {"SEMANTIC_CONFLICT", "PLUGIN_SPECIFIC", "UNRESOLVED"}:
            return False
        return left_class == right_class or {left_class, right_class} <= {"SAFE_TO_SHARE", "SHARE_WITH_TRANSFORMATION"}

    @staticmethod
    def _conflict(field_name: str, plugin_id: str, existing: Dict[str, Any], new: Dict[str, Any], provenance: Dict[str, Any]) -> Dict[str, Any]:
        return {"field": field_name, "namespaced_field": f"{plugin_id}__{field_name}", "owners": provenance.get(field_name, {}).get("owners", []) + [plugin_id], "reason": "Same property name failed canonical identity, type, unit, enum, or clinical mapping compatibility.", "existing": {"canonical_field_id": existing.get("x-canonical-field-id"), "type": existing.get("type"), "classification": existing.get("x-mapping-classification")}, "incoming": {"canonical_field_id": new.get("x-canonical-field-id"), "type": new.get("type"), "classification": new.get("x-mapping-classification")}}
