"""Safe inspection and extraction of untrusted plugin ZIP artifacts."""

from __future__ import annotations

import hashlib
import os
import stat
import zipfile
from dataclasses import dataclass
from pathlib import Path


class ArtifactSecurityError(ValueError):
    """Raised when an external plugin artifact violates package policy."""


@dataclass(frozen=True)
class ArtifactInspection:
    """Server-derived identity and size information for an artifact."""

    sha256: str
    size: int
    member_count: int


class PluginArtifactService:
    """Inspect and extract plugin ZIP files without executing their contents."""

    def __init__(self, *, max_members: int = 256, max_uncompressed_size: int = 50 * 1024 * 1024) -> None:
        self.max_members = max_members
        self.max_uncompressed_size = max_uncompressed_size

    def inspect(self, artifact_path: Path) -> ArtifactInspection:
        """Hash and validate archive members before any extraction occurs."""
        if not artifact_path.is_file():
            raise ArtifactSecurityError("Plugin artifact does not exist")
        digest = hashlib.sha256()
        with artifact_path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)

        try:
            with zipfile.ZipFile(artifact_path) as archive:
                members = archive.infolist()
                if len(members) > self.max_members:
                    raise ArtifactSecurityError("Plugin archive contains too many members")
                total_size = 0
                for member in members:
                    self._validate_member(member)
                    total_size += member.file_size
                    if total_size > self.max_uncompressed_size:
                        raise ArtifactSecurityError("Plugin archive exceeds the uncompressed size limit")
        except zipfile.BadZipFile as exc:
            raise ArtifactSecurityError("Plugin artifact is not a valid ZIP archive") from exc

        return ArtifactInspection(digest.hexdigest(), artifact_path.stat().st_size, len(members))

    def extract(self, artifact_path: Path, destination: Path) -> ArtifactInspection:
        """Inspect and safely extract an archive into a controlled directory."""
        inspection = self.inspect(artifact_path)
        destination = destination.resolve()
        destination.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(artifact_path) as archive:
            for member in archive.infolist():
                target = (destination / member.filename).resolve()
                if os.path.commonpath((str(destination), str(target))) != str(destination):
                    raise ArtifactSecurityError("Plugin archive path escapes its controlled directory")
                if member.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(member) as source, target.open("wb") as output:
                    while chunk := source.read(1024 * 1024):
                        output.write(chunk)
        return inspection

    @staticmethod
    def _validate_member(member: zipfile.ZipInfo) -> None:
        name = member.filename.replace("\\", "/")
        path = Path(name)
        if path.is_absolute() or name.startswith("/") or any(part == ".." for part in path.parts):
            raise ArtifactSecurityError("Plugin archive contains a traversal path")
        if len(name) > 512:
            raise ArtifactSecurityError("Plugin archive member name is too long")
        mode = (member.external_attr >> 16) & 0xFFFF
        if stat.S_ISLNK(mode):
            raise ArtifactSecurityError("Plugin archive symlinks are not permitted")
        if member.file_size < 0:
            raise ArtifactSecurityError("Plugin archive contains an invalid member size")
