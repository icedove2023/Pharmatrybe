from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from app.plugins.prediction.soar.deployment_scanner import DeploymentInfo, DeploymentScanner


class DeploymentRegistry:
    """In-memory registry for discovered SOAR deployments."""

    def __init__(self, deployments_root: Optional[Path] = None) -> None:
        self._scanner = DeploymentScanner(deployments_root)
        self._deployments: Dict[str, DeploymentInfo] = {}
        self._initialized = False

    def initialize(self) -> None:
        """Scan the filesystem once and cache discovered deployments."""
        if self._initialized:
            return
        self._deployments = {deployment.deployment_id: deployment for deployment in self._scanner.scan()}
        self._initialized = True

    def get_by_id(self, deployment_id: str) -> Optional[DeploymentInfo]:
        """Return deployment metadata by deployment ID."""
        self.initialize()
        return self._deployments.get(deployment_id)

    def get_by_antimicrobial(self, antimicrobial: str) -> List[DeploymentInfo]:
        """Return deployments for a specific antimicrobial."""
        self.initialize()
        return [d for d in self._deployments.values() if d.antimicrobial == antimicrobial]

    def get_by_organism(self, organism: str) -> List[DeploymentInfo]:
        """Return deployments for a specific organism."""
        self.initialize()
        return [d for d in self._deployments.values() if d.organism == organism]

    def get_all(self) -> List[DeploymentInfo]:
        """Return all discovered deployments."""
        self.initialize()
        return list(self._deployments.values())
