from __future__ import annotations

import jsonschema
from pathlib import Path

from app.plugins.manager.plugin_manager import PluginManager
from app.plugins.schema.discovery import SchemaDiscoveryService
from app.plugins.schema.composer import PluginSchemaComposer


def _manager() -> PluginManager:
    plugin_root = Path(__file__).resolve().parents[1] / "app" / "plugins"
    manager = PluginManager(plugin_root=plugin_root, platform_version="0.1.0", sdk_version="0.1.0")
    manager.load_all_plugins()
    return manager


def test_soar_armd_who_schemas_are_available() -> None:
    manager = _manager()
    discovery = SchemaDiscoveryService(manager)
    names = {plugin_id for plugin_id in ["soar", "armd", "who_knowledge"]}
    available = {item["plugin_id"] for item in discovery.get_available_plugin_schemas()}
    assert names.issubset(available)


def test_each_schema_is_valid_json_schema() -> None:
    manager = _manager()
    discovery = SchemaDiscoveryService(manager)
    for plugin_id in ["soar", "armd", "who_knowledge"]:
        schema = discovery.get_plugin_schema(plugin_id)
        jsonschema.Draft202012Validator.check_schema(schema)


def test_plugin_schema_composition_deduplicates_and_tracks_provenance() -> None:
    manager = _manager()
    composer = PluginSchemaComposer(manager)
    result = composer.compose(["soar", "armd"])
    assert result["schema"]["type"] == "object"
    assert "infection_site" in result["field_provenance"]
    assert {"soar", "armd"}.issubset(set(result["field_provenance"]["infection_site"]["owners"]))
    assert result["schema"]["properties"]["infection_site"]["type"] == "string"


def test_conflict_detection_works_for_incompatible_field_types() -> None:
    manager = _manager()
    composer = PluginSchemaComposer(manager)
    result = composer.compose(["soar", "armd"])
    assert "conflicts" in result


def test_unknown_plugin_and_empty_selection_are_rejected() -> None:
    manager = _manager()
    composer = PluginSchemaComposer(manager)
    try:
        composer.compose(["does_not_exist"])
        assert False, "Unknown plugin should raise"
    except ValueError:
        pass

    try:
        composer.compose([])
        assert False, "Empty selection should raise"
    except ValueError:
        pass


def test_plugin_input_schema_endpoint_contract() -> None:
    manager = _manager()
    discovery = SchemaDiscoveryService(manager)
    schemas = discovery.get_available_plugin_schemas()
    assert schemas and all("plugin_id" in item for item in schemas)
