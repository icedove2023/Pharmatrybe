from __future__ import annotations

from pathlib import Path

from app.plugins.discovery.plugin_loader import PluginLoader
from app.plugins.discovery.plugin_validator import PluginValidator
from app.plugins.manager.plugin_registry import PluginRegistry


def test_unapproved_filesystem_plugin_is_rejected_before_import(tmp_path: Path) -> None:
    plugin_dir = tmp_path / "external"
    plugin_dir.mkdir()
    (plugin_dir / "plugin.yaml").write_text(
        "\n".join(
            [
                "plugin_id: external",
                "plugin_name: External",
                "plugin_version: 1.0.0",
                "plugin_type: knowledge",
                "description: External plugin",
                "author: Hospital",
                "entrypoint_module: entrypoint",
                "entrypoint_class: ExternalPlugin",
                "dependencies: []",
                "minimum_platform_version: 1.0.0",
                "sdk_version: 1.0.0",
            ]
        ),
        encoding="utf-8",
    )
    (plugin_dir / "entrypoint.py").write_text("raise RuntimeError('must not import')\n", encoding="utf-8")

    registry = PluginRegistry(require_governance=True)
    loader = PluginLoader(
        plugin_dir,
        registry,
        PluginValidator(),
        platform_version="1.0.0",
        sdk_version="1.0.0",
    )

    result = loader.load_plugin(plugin_dir)

    assert result.success is False
    assert "governance-eligible" in result.errors[0]
    assert registry.get_plugin("external") is None
