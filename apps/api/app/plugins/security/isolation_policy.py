"""Explicit deployment isolation policy and capability decisions."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class IsolationLevel(str, Enum):
    DEVELOPMENT_SUBPROCESS = "development-subprocess"
    CONTAINER = "container"


class NetworkMode(str, Enum):
    DENIED = "denied"
    ALLOWLISTED = "allowlisted"


class FilesystemMode(str, Enum):
    TEMPORARY_ARTIFACT = "temporary-artifact"
    CONTAINER_READ_ONLY = "container-read-only"


@dataclass(frozen=True)
class IsolationPolicy:
    """Platform-owned limits and isolation requirements for external execution."""

    cpu_limit_seconds: float = 1.0
    cpu_limit_cores: float = 0.5
    memory_limit_bytes: int = 256 * 1024 * 1024
    timeout_seconds: float = 5.0
    max_request_bytes: int = 1_000_000
    max_stdout_bytes: int = 1_000_000
    max_stderr_bytes: int = 1_000_000
    max_result_bytes: int = 1_000_000
    network_mode: NetworkMode = NetworkMode.DENIED
    filesystem_mode: FilesystemMode = FilesystemMode.CONTAINER_READ_ONLY
    execution_identity: str = "pharmatrybe-plugin"
    isolation_level: IsolationLevel = IsolationLevel.CONTAINER
    allow_network: bool = False

    def validate(self) -> None:
        """Reject unsafe or internally inconsistent platform policies."""
        if self.cpu_limit_seconds <= 0 or self.cpu_limit_cores <= 0 or self.memory_limit_bytes <= 0 or self.timeout_seconds <= 0:
            raise ValueError("Isolation resource limits must be positive")
        if self.allow_network and self.network_mode is not NetworkMode.ALLOWLISTED:
            raise ValueError("Network access requires an allowlisted network mode")
        if self.network_mode is NetworkMode.ALLOWLISTED and not self.allow_network:
            raise ValueError("Allowlisted network mode must be explicitly enabled")
        if not self.execution_identity or self.execution_identity.lower() in {"root", "administrator", "system"}:
            raise ValueError("External plugins require a restricted execution identity")


@dataclass(frozen=True)
class EnforcementDecision:
    """Auditable result of asking a runtime whether it can enforce a policy."""

    enforceable: bool
    runtime: str
    reason: str | None = None
    cpu_enforced: bool = False
    memory_enforced: bool = False
    network_enforced: bool = False
    filesystem_enforced: bool = False
    identity_enforced: bool = False


class IsolationRuntime:
    """Interface for deployment runtimes that enforce external plugin policy."""

    runtime_name = "unknown"

    def can_enforce(self, policy: IsolationPolicy) -> EnforcementDecision:
        raise NotImplementedError

    def execute(self, request: dict, policy: IsolationPolicy) -> dict:
        raise NotImplementedError
