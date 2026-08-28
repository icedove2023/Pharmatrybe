from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

from app.plugins.security.artifact import ArtifactSecurityError, PluginArtifactService


def test_artifact_service_hashes_and_extracts_valid_zip(tmp_path: Path) -> None:
    archive_path = tmp_path / "plugin.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("plugin.yaml", "plugin_id: example\n")
        archive.writestr("entrypoint.py", "value = 1\n")

    service = PluginArtifactService()
    inspection = service.inspect(archive_path)
    destination = tmp_path / "extracted"
    extracted = service.extract(archive_path, destination)

    assert inspection.sha256 == extracted.sha256
    assert (destination / "plugin.yaml").exists()
    assert len(inspection.sha256) == 64


def test_artifact_service_rejects_path_traversal(tmp_path: Path) -> None:
    archive_path = tmp_path / "unsafe.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("../outside.py", "unsafe = True\n")

    with pytest.raises(ArtifactSecurityError):
        PluginArtifactService().inspect(archive_path)
