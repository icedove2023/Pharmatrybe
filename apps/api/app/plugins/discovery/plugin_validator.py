from __future__ import annotations

import inspect
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import ValidationError

from app.plugins.base.plugin import BasePlugin, PluginMetadata
from app.plugins.contracts.plugin_manifest import PluginManifest
from app.plugins.discovery.plugin_manifest_reader import PluginManifestReader


@dataclass
class PluginValidationResult:
    """Structured result for plugin validation checks."""

    plugin_id: Optional[str] = None
    manifest_exists: bool = False
    manifest_valid: bool = False
    base_plugin_valid: bool = False
    metadata_valid: bool = False
    sdk_version_compatible: bool = False
    platform_version_compatible: bool = False
    dependencies_declared: bool = False
    configuration_schema_valid: bool = False
    errors: List[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        # Consider manifest-level validation for manifest file checks. Class
        # and instance validation run separate checks that set `base_plugin_valid`
        # and `metadata_valid`. For manifest-only validation we only require
        # manifest existence, manifest correctness, version compatibility,
        # declared dependencies and configuration schema, and no recorded
        # validation errors.
        manifest_ok = (
            self.manifest_exists
            and self.manifest_valid
            and self.sdk_version_compatible
            and self.platform_version_compatible
            and self.dependencies_declared
            and self.configuration_schema_valid
            and not self.errors
        )

        return manifest_ok

    def add_error(self, message: str) -> None:
        self.errors.append(message)


class PluginValidator:
    """Validates plugin manifests, classes, and instance metadata."""

    def validate_manifest_file(
        self,
        manifest_path: Path,
        platform_version: str,
        sdk_version: str,
    ) -> PluginValidationResult:
        """Validate a plugin manifest file."""
        result = PluginValidationResult()
        if not manifest_path.exists():
            result.add_error(f"Manifest file does not exist: {manifest_path}")
            return result

        result.manifest_exists = True
        raw_manifest: Optional[Dict[str, Any]] = None
        try:
            content = manifest_path.read_text(encoding="utf-8")
            raw_manifest = PluginManifestReader._parse_manifest_content(content, manifest_path.suffix.lower())
            manifest = PluginManifest(**raw_manifest)
            result.plugin_id = manifest.plugin_id
            self._validate_manifest(manifest, result)
            self._validate_version_compatibility(manifest, platform_version, sdk_version, result)
        except ValidationError as exc:
            for error in exc.errors():
                result.add_error(str(error))
            if raw_manifest is None:
                raw_manifest = {}
            if raw_manifest.get("minimum_platform_version") is None:
                result.add_error("minimum_platform_version is required.")
            if raw_manifest.get("sdk_version") is None:
                result.add_error("sdk_version is required.")
        except Exception as exc:
            result.add_error(str(exc))

        return result

    def validate_plugin_class(
        self,
        plugin_class: type[BasePlugin],
        manifest: PluginManifest,
        platform_version: str,
        sdk_version: str,
    ) -> PluginValidationResult:
        """Validate the plugin class implements the BasePlugin contract."""
        result = PluginValidationResult(plugin_id=manifest.plugin_id)
        if not issubclass(plugin_class, BasePlugin):
            result.add_error(f"Plugin class {plugin_class.__name__} does not inherit from BasePlugin.")
            return result

        if inspect.isabstract(plugin_class):
            result.add_error(f"Plugin class {plugin_class.__name__} still contains abstract methods.")
            return result

        result.manifest_exists = True
        result.manifest_valid = True
        result.base_plugin_valid = True
        self._validate_version_compatibility(manifest, platform_version, sdk_version, result)
        self._validate_dependencies(manifest, result)
        self._validate_configuration_schema(manifest, result)
        return result

    def validate_plugin_instance(
        self,
        plugin: BasePlugin,
        manifest: PluginManifest,
        platform_version: str,
        sdk_version: str,
    ) -> PluginValidationResult:
        """Validate a plugin instance against its manifest."""
        result = self.validate_plugin_class(plugin.__class__, manifest, platform_version, sdk_version)
        try:
            metadata = plugin.metadata()
            if not isinstance(metadata, PluginMetadata):
                result.add_error("Plugin metadata must be a PluginMetadata instance.")
            elif metadata.plugin_id != manifest.plugin_id:
                result.add_error("Plugin metadata.plugin_id does not match manifest.plugin_id.")
            else:
                result.metadata_valid = True
        except Exception as exc:
            result.add_error(f"Plugin metadata inspection failed: {exc}")

        return result

    def _validate_manifest(self, manifest: PluginManifest, result: PluginValidationResult) -> None:
        result.manifest_valid = True
        self._validate_dependencies(manifest, result)
        self._validate_configuration_schema(manifest, result)

    def _validate_dependencies(self, manifest: PluginManifest, result: PluginValidationResult) -> None:
        if manifest.dependencies is None:
            result.add_error("Plugin dependencies must be declared.")
            return
        if not isinstance(manifest.dependencies, list):
            result.add_error("Plugin dependencies must be a list.")
            return
        if not all(isinstance(dep, str) and dep.strip() for dep in manifest.dependencies):
            result.add_error("Each dependency must be a non-empty string.")
            return
        result.dependencies_declared = True

    def _validate_configuration_schema(self, manifest: PluginManifest, result: PluginValidationResult) -> None:
        schema = manifest.configuration_schema
        if schema is None:
            result.configuration_schema_valid = True
            return
        if not isinstance(schema, dict):
            result.add_error("Plugin configuration_schema must be an object.")
            return
        result.configuration_schema_valid = True

    def _validate_version_compatibility(
        self,
        manifest: PluginManifest,
        platform_version: str,
        sdk_version: str,
        result: PluginValidationResult,
    ) -> None:
        if manifest.minimum_platform_version is None:
            result.add_error("minimum_platform_version is required.")
        elif not self._is_version_compatible(platform_version, manifest.minimum_platform_version):
            result.add_error(
                f"Platform version {platform_version} is not compatible with required {manifest.minimum_platform_version}."
            )
        else:
            result.platform_version_compatible = True

        if manifest.sdk_version is None:
            result.add_error("sdk_version is required.")
        elif not self._is_version_compatible(sdk_version, manifest.sdk_version):
            result.add_error(f"SDK version {sdk_version} is not compatible with required {manifest.sdk_version}.")
        else:
            result.sdk_version_compatible = True

    @staticmethod
    def _is_version_compatible(current_version: str, required_version: str) -> bool:
        def normalize(version: str) -> tuple[int, ...]:
            return tuple(int(part) for part in version.split(".") if part.isdigit())

        return normalize(current_version) >= normalize(required_version)
