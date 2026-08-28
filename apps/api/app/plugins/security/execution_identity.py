"""Immutable provenance snapshot for an admitted external plugin execution."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

from app.auth.tenant_context import TenantContext
from app.plugins.contracts.plugin_manifest import PluginManifest
from app.plugins.identity import canonical_plugin_id


def manifest_hash(manifest: PluginManifest) -> str:
    """Return a stable digest of the validated manifest identity."""
    encoded = json.dumps(manifest.model_dump(mode="json"), sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class ExecutionIdentity:
    """Immutable identity bound to one governance admission decision."""

    tenant_id: str
    canonical_plugin_id: str
    plugin_version: str
    governance_id: str
    artifact_hash: str
    manifest_hash: str
    entrypoint_module: str
    entrypoint_class: str
    plugin_type: str
    plugin_origin: str
    capabilities: tuple[str, ...]
    isolation_mode: str

    @classmethod
    def from_admission(cls, tenant: TenantContext, record, manifest: PluginManifest, isolation_mode: str) -> "ExecutionIdentity":
        """Snapshot governed and validated identity at admission time."""
        return cls(
            tenant_id=tenant.hospital_id,
            canonical_plugin_id=canonical_plugin_id(manifest.plugin_id),
            plugin_version=manifest.plugin_version,
            governance_id=record.id,
            artifact_hash=record.artifact_hash,
            manifest_hash=manifest_hash(manifest),
            entrypoint_module=manifest.entrypoint_module,
            entrypoint_class=manifest.entrypoint_class,
            plugin_type=manifest.plugin_type.value,
            plugin_origin=record.plugin_origin,
            capabilities=tuple(sorted(str(capability).strip().upper() for capability in record.capabilities or [])),
            isolation_mode=isolation_mode,
        )