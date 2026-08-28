from __future__ import annotations

import fnmatch
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


@dataclass(frozen=True)
class Artifact:
    """Represents a discovered artifact inside a deployment package."""

    filename: str
    extension: str
    absolute_path: Path
    relative_path: Path
    size: int
    category: str
    hash: Optional[str] = None


class ArtifactCategoryConfig:
    """Configuration for artifact category classification."""

    DEFAULT_CATEGORIES: Dict[str, List[str]] = {
        "MODEL": [
            "final_model.pkl",
            "model.pkl",
            "*.model.pkl",
            ".onnx",
            ".pt",
            ".pth",
            ".pb",
            ".tflite",
            ".trt",
            ".joblib",
        ],
        "ENCODER": [
            "label_encoder.pkl",
            "encoder.pkl",
            "*.encoder.pkl",
        ],
        "PREPROCESSOR": [
            "preprocessing_pipeline.pkl",
            "scaler.pkl",
            "feature_encoder.pkl",
            "preprocessing.pkl",
        ],
        "METADATA": [
            "metadata.json",
            "organism_profile.json",
            "feature_dictionary.json",
            "model_metadata.json",
            "artifact_metadata.json",
            "README.md",
        ],
        "CONFIG": [
            "artifact_categories.yaml",
            "inference_config.yaml",
            ".yaml",
            ".yml",
        ],
        "THRESHOLD": ["optimal_threshold.json", "threshold.json"],
        "METRICS": ["evaluation_metrics.csv", "*.csv"],
        "SCHEMA": ["schema.json", "*.schema.json"],
        "OTHER": ["*"],
    }

    DEFAULT_CONFIG_FILE = Path(__file__).resolve().parent / "artifact_categories.yaml"

    def __init__(self, mapping: Optional[Dict[str, List[str]]] = None) -> None:
        mapping_to_use = mapping if mapping is not None else self.DEFAULT_CATEGORIES
        self._mapping: Dict[str, List[str]] = {
            category: [pattern.strip().lower() for pattern in patterns]
            for category, patterns in mapping_to_use.items()
        }
        if "OTHER" not in self._mapping:
            self._mapping["OTHER"] = ["*"]

    @classmethod
    def load_default(cls) -> "ArtifactCategoryConfig":
        if cls.DEFAULT_CONFIG_FILE.exists():
            return cls.load_from_file(cls.DEFAULT_CONFIG_FILE)
        return cls()

    @classmethod
    def load_from_file(cls, path: Path) -> "ArtifactCategoryConfig":
        if not path.exists():
            raise FileNotFoundError(f"Artifact category config not found: {path}")

        content = path.read_text(encoding="utf-8")
        if path.suffix.lower() in {".yaml", ".yml"}:
            mapping = cls._parse_simple_yaml(content)
        elif path.suffix.lower() == ".json":
            mapping = json.loads(content)
        else:
            raise ValueError(f"Unsupported artifact category config format: {path.suffix}")

        if not isinstance(mapping, dict):
            raise ValueError("Artifact category config must contain a mapping of categories to patterns.")

        normalized: Dict[str, List[str]] = {}
        for category, patterns in mapping.items():
            if isinstance(patterns, str):
                normalized[category] = [patterns]
            elif isinstance(patterns, list):
                normalized[category] = [str(pattern).strip() for pattern in patterns]
            else:
                raise ValueError(f"Invalid artifact patterns for category '{category}': {patterns}")

        return cls(normalized)

    def categories(self) -> List[str]:
        return list(self._mapping.keys())

    def patterns_for(self, category: str) -> List[str]:
        return self._mapping.get(category, [])

    def classify(self, filename: str, extension: str) -> str:
        filename_lower = filename.lower()
        extension_lower = extension.lower()

        for category in self.categories():
            patterns = self.patterns_for(category)
            for pattern in patterns:
                if self._matches_pattern(filename_lower, extension_lower, pattern):
                    return category
        return "OTHER"

    @staticmethod
    def _matches_pattern(filename: str, extension: str, pattern: str) -> bool:
        if pattern.startswith("."):
            if extension == pattern:
                return True
            return filename.endswith(pattern)

        if any(char in pattern for char in ["*", "?", "["]):
            return fnmatch.fnmatch(filename, pattern)

        return filename == pattern

    @staticmethod
    def _parse_simple_yaml(raw_text: str) -> Dict[str, Any]:
        lines = [line.rstrip() for line in raw_text.splitlines()]
        document: Dict[str, Any] = {}
        stack: List[Tuple[int, Any]] = [(0, document)]

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
                next_node: Any = [] if ArtifactCategoryConfig._next_line_is_list(lines, index) else {}
                parent[key] = next_node
                stack.append((indent, next_node))
                continue

            parent[key] = parse_scalar(value_text)

        return document

    @staticmethod
    def _next_line_is_list(lines: List[str], index: int) -> bool:
        for next_index in range(index + 1, len(lines)):
            next_line = lines[next_index].strip()
            if not next_line or next_line.startswith("#"):
                continue
            return next_line.startswith("- ")
        return False


class ArtifactRegistry:
    """Discovers and exposes artifacts within a deployment package."""

    def __init__(
        self,
        deployment_path: Path,
        artifacts: List[Artifact],
        category_config: ArtifactCategoryConfig,
    ) -> None:
        self.deployment_path = deployment_path
        self._artifacts = artifacts
        self.category_config = category_config
        self._artifacts_by_category: Dict[str, List[Artifact]] = self._group_by_category()

    @classmethod
    def from_deployment_path(
        cls,
        deployment_path: Path,
        category_config: Optional[ArtifactCategoryConfig] = None,
    ) -> "ArtifactRegistry":
        category_config = category_config or ArtifactCategoryConfig.load_default()
        artifacts: List[Artifact] = []

        for file_path in sorted(deployment_path.rglob("*")):
            if not file_path.is_file():
                continue
            relative_path = file_path.relative_to(deployment_path)
            artifacts.append(cls._build_artifact(file_path, relative_path, category_config))

        return cls(deployment_path=deployment_path, artifacts=artifacts, category_config=category_config)

    @staticmethod
    def _build_artifact(
        file_path: Path,
        relative_path: Path,
        category_config: ArtifactCategoryConfig,
    ) -> Artifact:
        filename = file_path.name
        extension = file_path.suffix.lower()
        category = category_config.classify(filename, extension)
        return Artifact(
            filename=filename,
            extension=extension,
            absolute_path=file_path.resolve(),
            relative_path=relative_path,
            size=file_path.stat().st_size,
            category=category,
        )

    def _group_by_category(self) -> Dict[str, List[Artifact]]:
        grouped: Dict[str, List[Artifact]] = {}
        for artifact in self._artifacts:
            grouped.setdefault(artifact.category, []).append(artifact)
        return grouped

    @property
    def artifacts(self) -> List[Artifact]:
        return list(self._artifacts)

    def artifacts_by_category(self, category: str) -> List[Artifact]:
        return list(self._artifacts_by_category.get(category, []))

    def find_first(self, category: str) -> Optional[Artifact]:
        artifacts = self.artifacts_by_category(category)
        return artifacts[0] if artifacts else None

    def find_by_filename(self, filename: str) -> Optional[Artifact]:
        normalized = filename.lower()
        for artifact in self._artifacts:
            if artifact.filename.lower() == normalized:
                return artifact
        return None

    def all_categories(self) -> List[str]:
        return list(self._artifacts_by_category.keys())
