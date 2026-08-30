from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

from app.plugins.contracts.plugin_manifest import PluginManifest


class PluginManifestReader:
    """Loads and deserializes plugin manifest files."""

    SUPPORTED_FILENAMES = ["plugin.yaml", "plugin.yml", "plugin.json", "*_plugin_manifest.yml"]

    @classmethod
    def load_from_plugin_directory(cls, plugin_directory: Path) -> PluginManifest:
        """Load a plugin manifest from a plugin directory."""
        manifest_path = cls._find_manifest_path(plugin_directory)
        if manifest_path is None:
            raise FileNotFoundError(f"No plugin manifest found in directory: {plugin_directory}")
        return cls.load_from_file(manifest_path)

    @classmethod
    def load_from_file(cls, manifest_path: Path) -> PluginManifest:
        """Load a plugin manifest from a YAML or JSON file."""
        if not manifest_path.exists():
            raise FileNotFoundError(f"Plugin manifest not found: {manifest_path}")

        content = manifest_path.read_text(encoding="utf-8")
        raw_manifest = cls._parse_manifest_content(content, manifest_path.suffix.lower())

        # Ensure enum-like fields are converted to their Enum types so Pydantic
        # constructs the fields correctly instead of leaving them as raw strings.
        from app.plugins.base.prediction_plugin import DeploymentType
        from app.plugins.base.plugin import PluginType

        if isinstance(raw_manifest, dict):
            if "deployment_type" in raw_manifest and isinstance(raw_manifest["deployment_type"], str):
                try:
                    raw_manifest["deployment_type"] = DeploymentType(raw_manifest["deployment_type"])
                except Exception:
                    # leave as-is; validation will report problems later
                    pass
            if "plugin_type" in raw_manifest and isinstance(raw_manifest["plugin_type"], str):
                try:
                    raw_manifest["plugin_type"] = PluginType(raw_manifest["plugin_type"])
                except Exception:
                    pass

        return PluginManifest(**raw_manifest)

    @classmethod
    def _find_manifest_path(cls, plugin_directory: Path) -> Optional[Path]:
        for filename in cls.SUPPORTED_FILENAMES:
            if "*" in filename:
                matches = sorted(plugin_directory.glob(filename))
                if matches:
                    return matches[0]
                continue
            candidate = plugin_directory / filename
            if candidate.exists():
                return candidate
        return None

    @classmethod
    def _parse_manifest_content(cls, content: str, extension: str) -> Dict[str, Any]:
        if extension in {".yaml", ".yml"}:
            return cls._parse_simple_yaml(content)
        if extension == ".json":
            return json.loads(content)
        raise ValueError(f"Unsupported manifest file format: {extension}")

    @staticmethod
    def _parse_simple_yaml(raw_text: str) -> Dict[str, Any]:
        lines = [line.rstrip() for line in raw_text.splitlines()]
        document: Dict[str, Any] = {}
        stack: list[tuple[int, Any]] = [(0, document)]

        def parse_scalar(value: str) -> Any:
            value = value.strip()
            if value in {"null", "None", "none", "~"}:
                return None
            if value.lower() in {"true", "false"}:
                return value.lower() == "true"
            if value.startswith("[") and value.endswith("]"):
                inner = value[1:-1].strip()
                if not inner:
                    return []
                return [item.strip() for item in inner.split(",")]
            if value.startswith("{") and value.endswith("}"):
                inner = value[1:-1].strip()
                if not inner:
                    return {}
                result: Dict[str, Any] = {}
                for entry in inner.split(","):
                    if ":" not in entry:
                        continue
                    key, raw_entry_value = entry.split(":", 1)
                    result[key.strip().strip('"\'')] = parse_scalar(raw_entry_value.strip())
                return result
            if value.startswith("\"") and value.endswith("\""):
                return value[1:-1]
            if value.startswith("'") and value.endswith("'"):
                return value[1:-1]
            if value.isdigit():
                return int(value)
            try:
                return float(value)
            except ValueError:
                return value

        for index, raw_line in enumerate(lines):
            line = raw_line.split("#", 1)[0].rstrip()
            if not line:
                continue

            indent = len(raw_line) - len(raw_line.lstrip(" "))
            while len(stack) > 1 and stack[-1][0] >= indent:
                stack.pop()
            parent = stack[-1][1]
            content = line.lstrip(" ")

            if content.startswith("- "):
                if not isinstance(parent, list):
                    raise ValueError("Invalid YAML list structure")
                parent.append(parse_scalar(content[2:].strip()))
                continue

            if ":" not in content:
                raise ValueError(f"Unsupported YAML content: {content}")

            key, raw_value = content.split(":", 1)
            key = key.strip()
            value_text = raw_value.strip()

            if value_text == "":
                next_index = index
                next_node: Any = [] if PluginManifestReader._next_line_is_list(lines, next_index) else {}
                parent[key] = next_node
                stack.append((indent, next_node))
                continue

            parent[key] = parse_scalar(value_text)

        return document

    @staticmethod
    def _next_line_is_list(lines: list[str], index: int) -> bool:
        for next_index in range(index + 1, len(lines)):
            next_line = lines[next_index].strip()
            if not next_line or next_line.startswith("#"):
                continue
            return next_line.startswith("- ")
        return False
