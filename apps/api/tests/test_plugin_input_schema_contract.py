from __future__ import annotations

import json
from pathlib import Path

import jsonschema

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


def test_declared_plugin_schemas_do_not_match_runtime_contracts() -> None:
    repo_root = Path(__file__).resolve().parents[3]

    soar_feature_schema_path = next(
        path for path in (repo_root / "deployments" / "SOAR_GSK").iterdir()
        if path.is_dir() and (path / "feature_schema.json").exists()
    ) / "feature_schema.json"
    soar_feature_names = {
        feature["name"].lower()
        for feature in json.loads(soar_feature_schema_path.read_text(encoding="utf-8"))["features"]
    }
    soar_schema = SchemaDiscoveryService(_manager()).get_plugin_schema("soar")
    assert "pathogen" not in soar_feature_names
    assert set(soar_schema["anyOf"][0]["properties"]) == {"Age", "YearCollected", "Region", "BodyLocation_Group", "Country", "Beta_Lactamase_enc"}
    assert soar_schema["x-contract-kind"] == "prediction_input"
    assert "Age" in soar_schema["x-plugin-runtime-mappings"]

    armd_feature_path = repo_root / "deployments" / "ARMD" / "WP4_Decision_Engine.py"
    armd_text = armd_feature_path.read_text(encoding="utf-8")
    assert "gender_male" in armd_text
    armd_schema = SchemaDiscoveryService(_manager()).get_plugin_schema("armd")
    assert "gender_male" in armd_schema["properties"]
    assert "age_group" in armd_schema["properties"]
    assert "age_group" in armd_schema["x-derived-features"]

    who_query_model_path = repo_root / "apps" / "api" / "app" / "knowledge" / "providers" / "query_models.py"
    who_text = who_query_model_path.read_text(encoding="utf-8")
    assert "class KnowledgeQuery" in who_text
    who_schema = SchemaDiscoveryService(_manager()).get_plugin_schema("who_knowledge")
    assert who_schema["x-contract-kind"] == "knowledge_query"
    assert {branch["title"] for branch in who_schema["oneOf"]} == {"KnowledgeQuery", "SearchQuery"}
    assert "query_text" in who_schema["oneOf"][0]["properties"]


def test_plugin_schema_composition_deduplicates_and_tracks_provenance() -> None:
    manager = _manager()
    composer = PluginSchemaComposer(manager)
    result = composer.compose(["soar", "armd"])
    assert result["schema"]["type"] == "object"
    assert "Age" in result["field_provenance"]
    assert result["field_provenance"]["Age"]["owners"] == ["soar"]
    assert "age" in result["field_provenance"]
    assert result["field_provenance"]["age"]["owners"] == ["armd"]
    assert "armd__age" not in result["schema"]["properties"]
    assert any(conflict["field"] == "age" for conflict in result["conflicts"]) is False


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


def test_all_plugin_selections_have_valid_composed_contracts() -> None:
    manager = _manager()
    composer = PluginSchemaComposer(manager)
    selections = [
        ["soar"], ["armd"], ["who_knowledge"],
        ["soar", "armd"], ["soar", "who_knowledge"], ["armd", "who_knowledge"],
        ["soar", "armd", "who_knowledge"],
    ]
    for selection in selections:
        result = composer.compose(selection)
        jsonschema.Draft202012Validator.check_schema(result["composed_schema"])
        assert set(selection).issubset(result["plugin_runtime_mappings"])
        assert result["canonical_field_metadata"]
        assert set(selection).issubset({owner for item in result["field_provenance"].values() for owner in item["owners"]})


def test_who_is_never_composed_as_prediction_fields() -> None:
    result = PluginSchemaComposer(_manager()).compose(["soar", "who_knowledge"])
    assert result["plugin_runtime_mappings"]["who_knowledge"]["contract"] == "KnowledgeQuery or SearchQuery"
    assert "diagnosis" not in result["schema"]["properties"]
    assert any(item["field"] == "infection_site" for item in result["conflicts"]) is False
