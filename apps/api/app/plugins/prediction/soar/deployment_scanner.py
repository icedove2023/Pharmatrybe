from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
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
            deployments.append(self._inspect_deployment_folder(child))

        return deployments

    def _inspect_deployment_folder(self, deployment_path: Path) -> DeploymentInfo:
        artifact_registry = ArtifactRegistry.from_deployment_path(deployment_path)
        organism, antimicrobial = self._parse_deployment_id(deployment_path.name)
        status = self._determine_status(artifact_registry)
        return DeploymentInfo(
            deployment_id=deployment_path.name,
            organism=organism,
            antimicrobial=antimicrobial,
            deployment_path=deployment_path,
            artifact_registry=artifact_registry,
            status=status,
        )

    def _determine_status(self, artifact_registry: ArtifactRegistry) -> str:
        if artifact_registry.artifacts:
            return "valid"
        return "empty"

    def _parse_deployment_id(self, deployment_id: str) -> Tuple[Optional[str], Optional[str]]:
        separators = ["__", "-", "_"]
        for separator in separators:
            if separator in deployment_id:
                parts = deployment_id.split(separator)
                if len(parts) >= 2:
                    return parts[0].strip() or None, parts[1].strip() or None
        return None, None
