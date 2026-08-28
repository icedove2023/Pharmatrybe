from __future__ import annotations

from dataclasses import dataclass, field
from importlib import import_module
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import tempfile
from typing import Any, Dict, List, Optional

from app.plugins.base.plugin import BasePlugin
from app.plugins.contracts.plugin_manifest import PluginManifest
from app.plugins.discovery.plugin_manifest_reader import PluginManifestReader
from app.plugins.manager.plugin_registry import PluginRegistry
from app.plugins.discovery.plugin_validator import PluginValidator, PluginValidationResult
from app.plugins.security.artifact import ArtifactSecurityError, PluginArtifactService
from app.plugins.security.external_proxy import ExternalKnowledgeProxy, ExternalPredictionProxy
from app.plugins.security.isolated_executor import IsolatedPluginExecutor
from app.auth.tenant_context import TenantContext
from app.plugins.identity import canonical_plugin_id, is_internal_plugin
from app.plugins.security.execution_identity import ExecutionIdentity


@dataclass
class PluginLoadResult:
    """Result of attempting to load a plugin."""

    plugin_id: str
    success: bool = False
    errors: List[str] = field(default_factory=list)


class PluginLoader:
    """Discovers, validates, and loads PharmaTrybe plugins."""

    MANIFEST_FILENAMES = ["plugin.yaml", "plugin.yml", "plugin.json", "*_plugin_manifest.yml"]

    def __init__(
        self,
        plugin_root: Path,
        registry: PluginRegistry,
        validator: PluginValidator,
        platform_version: str,
        sdk_version: str,
        tenant_context: TenantContext | None = None,
        external_executor=None,
    ) -> None:
        self.plugin_root = plugin_root
        self.registry = registry
        self.validator = validator
        self.platform_version = platform_version
        self.sdk_version = sdk_version
        self.tenant_context = tenant_context
        self.external_executor = external_executor
        self.artifact_service = PluginArtifactService()
        self._artifact_directories: list[tempfile.TemporaryDirectory[str]] = []
        self._plugin_paths: Dict[str, Path] = {}

    def discover_plugin_paths(self) -> List[Path]:
        """Discover plugin directories containing a manifest."""
        if not self.plugin_root.exists() or not self.plugin_root.is_dir():
            return []

        candidate_paths: List[Path] = []
        if any((self.plugin_root / candidate).exists() for candidate in self.MANIFEST_FILENAMES):
            candidate_paths.append(self.plugin_root)

        for candidate in self.plugin_root.rglob("*"):
            if not candidate.is_dir():
                continue
            if any((candidate / manifest).exists() for manifest in self.MANIFEST_FILENAMES):
                candidate_paths.append(candidate)

        return candidate_paths

    def load_all_plugins(self) -> List[PluginLoadResult]:
        """Attempt to load every discovered plugin."""
        results: List[PluginLoadResult] = []
        for plugin_path in self.discover_plugin_paths():
            result = self.load_plugin(plugin_path)
            results.append(result)
        return results

    def load_plugin(self, plugin_path: Path) -> PluginLoadResult:
        """Load a single plugin from a plugin directory."""
        result = PluginLoadResult(plugin_id=plugin_path.name)
        manifest_path = self._find_manifest_path(plugin_path)
        if manifest_path is None:
            result.errors.append(f"No manifest found in plugin directory: {plugin_path}")
            return result

        try:
            manifest = PluginManifestReader.load_from_file(manifest_path)
        except Exception as exc:
            result.errors.append(str(exc))
            return result

        if self.tenant_context is None and not is_internal_plugin(manifest.plugin_id):
            result.errors.append("Plugin is not governance-eligible: tenant context is required for external plugin admission")
            return result
        hospital_id = None if self.tenant_context is None or self.tenant_context.system_owned else self.tenant_context.hospital_id
        if not self.registry.can_admit_manifest(manifest.plugin_id, hospital_id=hospital_id):
            result.errors.append("Plugin is not governance-eligible for runtime")
            return result
        validation = self.validator.validate_manifest_file(manifest_path, self.platform_version, self.sdk_version)
        if not validation.is_valid:
            result.errors.extend(validation.errors)
            return result

        is_internal = is_internal_plugin(manifest.plugin_id)
        if is_internal and (self.tenant_context is None or not self.tenant_context.system_owned):
            result.errors.append("Internal plugin admission requires explicit system context")
            return result
        if not is_internal:
            if self.external_executor is None:
                result.errors.append("External plugin runtime isolation is unavailable")
                return result
            try:
                governance_record = self.registry.governance_service.get_record(manifest.plugin_id, hospital_id=self.tenant_context.hospital_id)
                self.tenant_context.require_same_hospital(governance_record.hospital_id)
                if governance_record.artifact_hospital_id != self.tenant_context.hospital_id:
                    result.errors.append("Artifact tenant does not match the authenticated tenant")
                    return result
                artifact_path = Path(governance_record.artifact_uri or plugin_path)
                inspection = self.artifact_service.inspect(artifact_path)
                if inspection.sha256 != governance_record.artifact_hash or governance_record.plugin_version != manifest.plugin_version:
                    result.errors.append("Governed artifact identity does not match the discovered plugin")
                    return result
                artifact_directory = tempfile.TemporaryDirectory(prefix=f"plugin-{manifest.plugin_id}-")
                self._artifact_directories.append(artifact_directory)
                extracted_path = Path(artifact_directory.name)
                self.artifact_service.extract(artifact_path, extracted_path)
                extracted_manifest_path = self._find_manifest_path(extracted_path)
                if extracted_manifest_path is None:
                    result.errors.append("Governed artifact does not contain a manifest")
                    return result
                extracted_manifest = PluginManifestReader.load_from_file(extracted_manifest_path)
                if extracted_manifest.model_dump() != manifest.model_dump():
                    result.errors.append("Governed artifact manifest does not match the discovered manifest")
                    return result
                manifest_capabilities = tuple(sorted(str(capability).strip().upper() for capability in manifest.capabilities))
                governed_capabilities = tuple(sorted(str(capability).strip().upper() for capability in governance_record.capabilities or []))
                if manifest_capabilities != governed_capabilities:
                    result.errors.append("Governed capabilities do not match the plugin manifest")
                    return result
                if governance_record.plugin_id != canonical_plugin_id(manifest.plugin_id):
                    result.errors.append("Governed plugin identity does not match the manifest")
                    return result
                if governance_record.plugin_type != manifest.plugin_type.value:
                    result.errors.append("Governed plugin type does not match the manifest")
                    return result
                if governance_record.plugin_origin.lower() != "external":
                    result.errors.append("Governed plugin origin is not external")
                    return result
                execution_identity = ExecutionIdentity.from_admission(
                    self.tenant_context,
                    governance_record,
                    extracted_manifest,
                    getattr(self.external_executor, "runtime_name", "unknown"),
                )
                proxy_type = ExternalPredictionProxy if manifest.plugin_type.value == "prediction" else ExternalKnowledgeProxy
                plugin_instance = proxy_type(
                    manifest,
                    extracted_path / Path(*manifest.entrypoint_module.split(".")).with_suffix(".py"),
                    self.external_executor,
                    inspection.sha256,
                    self.tenant_context,
                    list(governance_record.capabilities or []),
                    self.registry.governance_service,
                    artifact_path,
                    execution_identity,
                )
            except (ArtifactSecurityError, KeyError, OSError, ValueError) as exc:
                result.errors.append(f"External plugin admission failed: {exc}")
                return result
        else:
            try:
                plugin_class = self._resolve_plugin_class(plugin_path, manifest)
            except Exception as exc:
                result.errors.append(f"Failed to import plugin entrypoint: {exc}")
                return result

            try:
                plugin_instance = plugin_class()
            except Exception as exc:
                result.errors.append(f"Failed to instantiate plugin class: {exc}")
                return result

            class_validation = self.validator.validate_plugin_class(plugin_class, manifest, self.platform_version, self.sdk_version)
            if not class_validation.is_valid:
                result.errors.extend(class_validation.errors)
                return result

        instance_validation = self.validator.validate_plugin_instance(plugin_instance, manifest, self.platform_version, self.sdk_version)
        if not instance_validation.is_valid:
            result.errors.extend(instance_validation.errors)
            return result

        if is_internal:
            try:
                plugin_instance.initialize()
            except Exception as exc:
                result.errors.append(f"Failed to initialize plugin: {exc}")
                return result

        try:
            owner_hospital_id = None if is_internal else self.tenant_context.hospital_id
            self.registry.register_plugin(manifest, plugin_instance, owner_hospital_id=owner_hospital_id)
        except Exception as exc:
            result.errors.append(f"Failed to register plugin: {exc}")
            return result

        self._plugin_paths[manifest.plugin_id] = plugin_path
        result.plugin_id = manifest.plugin_id
        result.success = True
        return result

    def get_plugin_path(self, plugin_id: str) -> Optional[Path]:
        """Return the filesystem path for a loaded plugin."""
        return self._plugin_paths.get(plugin_id)

    def _find_manifest_path(self, plugin_path: Path) -> Optional[Path]:
        for filename in self.MANIFEST_FILENAMES:
            if "*" in filename:
                matches = sorted(plugin_path.glob(filename))
                if matches:
                    return matches[0]
                continue
            candidate = plugin_path / filename
            if candidate.exists():
                return candidate
        return None

    def _resolve_plugin_class(self, plugin_path: Path, manifest: PluginManifest) -> type[BasePlugin]:
        module_reference = manifest.entrypoint_module
        module_file = self._resolve_module_path(plugin_path, module_reference)
        if not module_file.exists():
            raise FileNotFoundError(f"Entrypoint module not found: {module_file}")

        # Construct a package-style module name when possible so the loaded
        # class identity matches imports elsewhere in the application. For
        # files inside the workspace (e.g., app/plugins/...), build a dotted
        # module path relative to the current working directory.
        try:
            resolved = module_file.resolve()
            parts = resolved.parts
            # Prefer creating a module name starting at the first 'app' segment
            # so paths like '.../apps/api/app/...' map to 'app.*' package names.
            if "app" in parts:
                idx = parts.index("app")
                module_name = ".".join(parts[idx:])
                if module_name.endswith(".py"):
                    module_name = module_name[:-3]
            else:
                rel = resolved.relative_to(Path.cwd())
                module_name = ".".join(rel.with_suffix("").parts)
        except Exception:
            module_name = f"pharmatrybe_plugin_{manifest.plugin_id}"

        if module_name.startswith("app."):
            module = import_module(module_name)
            plugin_class = getattr(module, manifest.entrypoint_class, None)
            if plugin_class is None:
                raise AttributeError(f"Entrypoint class {manifest.entrypoint_class} not found in module {module_file}")
            if not issubclass(plugin_class, BasePlugin):
                raise TypeError(f"Entrypoint class {manifest.entrypoint_class} is not a BasePlugin subclass.")
            return plugin_class

        spec = spec_from_file_location(module_name, module_file)
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not construct module spec for {module_file}")

        import sys

        # If the module is already loaded under the desired name, reuse it
        # to ensure class identity (isinstance checks) remains consistent.
        if module_name in sys.modules:
            module = sys.modules[module_name]
        else:
            module = module_from_spec(spec)
            # Register prior to execution so relative imports inside the
            # module resolve to the correct module object.
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

        plugin_class = getattr(module, manifest.entrypoint_class, None)
        if plugin_class is None:
            raise AttributeError(f"Entrypoint class {manifest.entrypoint_class} not found in module {module_file}")
        if not issubclass(plugin_class, BasePlugin):
            raise TypeError(f"Entrypoint class {manifest.entrypoint_class} is not a BasePlugin subclass.")

        return plugin_class

    @staticmethod
    def _resolve_module_path(plugin_path: Path, module_reference: str) -> Path:
        candidate = Path(module_reference)
        if candidate.suffix == ".py":
            return plugin_path / candidate

        relative_path = Path(*module_reference.split("."))
        return plugin_path / relative_path.with_suffix(".py")
