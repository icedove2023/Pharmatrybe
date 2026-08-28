"""Container isolation adapter for production external plugin execution."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any

from app.plugins.security.isolation_policy import EnforcementDecision, IsolationPolicy, IsolationRuntime


class ContainerIsolationRuntime(IsolationRuntime):
    """Docker-compatible adapter that exposes only verified enforcement claims."""

    runtime_name = "container"

    def __init__(self, image: str, executable: str = "docker") -> None:
        self.image = image
        self.executable = executable

    def can_enforce(self, policy: IsolationPolicy) -> EnforcementDecision:
        try:
            policy.validate()
        except ValueError as exc:
            return EnforcementDecision(False, self.runtime_name, str(exc))
        if shutil.which(self.executable) is None:
            return EnforcementDecision(False, self.runtime_name, "Container runtime executable is unavailable")
        try:
            daemon = subprocess.run([self.executable, "info"], capture_output=True, timeout=2, check=False)
        except (OSError, subprocess.TimeoutExpired):
            return EnforcementDecision(False, self.runtime_name, "Container runtime daemon is unavailable")
        if daemon.returncode != 0:
            return EnforcementDecision(False, self.runtime_name, "Container runtime daemon is unavailable")
        if policy.network_mode.value != "denied" or policy.allow_network:
            return EnforcementDecision(False, self.runtime_name, "Network allowlisting is not configured")
        return EnforcementDecision(
            True,
            self.runtime_name,
            cpu_enforced=True,
            memory_enforced=True,
            network_enforced=True,
            filesystem_enforced=True,
            identity_enforced=True,
        )

    def build_command(self, request: dict[str, Any], policy: IsolationPolicy) -> list[str]:
        """Build a resource-restricted container command without executing it."""
        decision = self.can_enforce(policy)
        if not decision.enforceable:
            raise RuntimeError(decision.reason or "Isolation policy is unavailable")
        artifact = Path(str(request["artifact_path"])).resolve()
        return [
            self.executable,
            "run",
            "--rm",
            "--read-only",
            "--network=none",
            "--cpus", str(policy.cpu_limit_cores),
            "--memory", str(policy.memory_limit_bytes),
            "--pids-limit", "32",
            "--cap-drop", "ALL",
            "--security-opt", "no-new-privileges:true",
            "--user", policy.execution_identity,
            "--mount", f"type=bind,src={artifact},dst=/plugin/artifact.zip,readonly",
            self.image,
            "python", "-m", "pharmatrybe_plugin_worker",
        ]

    def execute(self, request: dict[str, Any], policy: IsolationPolicy) -> dict:
        """Execute a prevalidated request only when container enforcement is available."""
        command = self.build_command(request, policy)
        completed = subprocess.run(command, capture_output=True, text=True, timeout=policy.timeout_seconds, check=False)
        if completed.returncode != 0:
            raise RuntimeError("Container plugin execution failed")
        return {"stdout": completed.stdout, "stderr": completed.stderr}
