from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
from typing import List, Optional, Tuple

from app.plugins.prediction.soar.artifact_registry import ArtifactRegistry


@dataclass(frozen=True)
class DeploymentInfo:
    """Metadata for a discovered SOAR deployment."""

    deployment_id: str
    organism: Optional[str]
    antimicrobial: Optional[str]
    deployment_path: Path
    artifact_registry: ArtifactRegistry
    status: str
    feature_names: Tuple[str, ...] = ()


class DeploymentScanner:
    """Scans deployed SOAR models without loading any artifacts."""

    def __init__(self, deployments_root: Optional[Path] = None) -> None:
        if deployments_root is not None:
            self.deployments_root = deployments_root
        else:
            repository_root = Path(__file__).resolve().parents[6]
            supplied_deployment = repository_root / "deployments" / "SOAR_GSK" / "SOAR_GSK" / "deployment"
            self.deployments_root = (
                supplied_deployment
                if supplied_deployment.is_dir()
                else repository_root / "deployments" / "SOAR_GSK"
            )

    def scan(self) -> List[DeploymentInfo]:
        """Discover SOAR deployment folders and return their metadata."""
        if not self.deployments_root.exists() or not self.deployments_root.is_dir():
            return []

        deployments: List[DeploymentInfo] = []
        for child in sorted(self.deployments_root.iterdir()):
            if not child.is_dir():
                continue
            metadata_path = self._metadata_deployment_path(child)
            if not metadata_path or not (metadata_path / "deployment_info.json").exists() or not (metadata_path / "feature_schema.json").exists():
                continue
            deployments.append(self._inspect_deployment_folder(child, metadata_path))

        return deployments

    def _inspect_deployment_folder(self, deployment_path: Path, metadata_path: Path) -> DeploymentInfo:
        artifact_registry = ArtifactRegistry.from_deployment_path(deployment_path)
        if artifact_registry.find_first("MODEL") is None:
            return DeploymentInfo(
                deployment_id=deployment_path.name,
                organism=None,
                antimicrobial=None,
                deployment_path=deployment_path,
                artifact_registry=artifact_registry,
                status="invalid",
            )
        organism, antimicrobial = self._read_identity(metadata_path)
        feature_schema = json.loads((metadata_path / "feature_schema.json").read_text(encoding="utf-8"))
        feature_names = tuple(str(item["name"]) for item in feature_schema.get("features", []) if isinstance(item, dict) and item.get("name"))
        status = self._determine_status(artifact_registry, organism, antimicrobial, feature_names)
        return DeploymentInfo(
            deployment_id=deployment_path.name,
            organism=organism,
            antimicrobial=antimicrobial,
            deployment_path=deployment_path,
            artifact_registry=artifact_registry,
            status=status,
            feature_names=feature_names,
        )

    def _determine_status(
        self,
        artifact_registry: ArtifactRegistry,
        organism: Optional[str],
        antimicrobial: Optional[str],
        feature_names: Tuple[str, ...],
    ) -> str:
        if artifact_registry.find_first("MODEL") and organism and antimicrobial and feature_names:
            return "valid"
        return "empty"

    def _metadata_deployment_path(self, deployment_path: Path) -> Optional[Path]:
        if (deployment_path / "deployment_info.json").exists() and (deployment_path / "feature_schema.json").exists():
            return deployment_path

        sibling_metadata = self.deployments_root.parent.parent / deployment_path.name
        if sibling_metadata.is_dir():
            return sibling_metadata
        return None

    @staticmethod
    def _read_identity(deployment_path: Path) -> Tuple[Optional[str], Optional[str]]:
        data = json.loads((deployment_path / "deployment_info.json").read_text(encoding="utf-8"))
        species = data.get("species")
        antibiotic = data.get("antibiotic")
        return (str(species).strip() if species else None, str(antibiotic).strip() if antibiotic else None)
