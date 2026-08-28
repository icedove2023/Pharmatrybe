"""Subprocess boundary for external plugin execution."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import Any

from app.plugins.security.isolation_policy import EnforcementDecision, IsolationLevel, IsolationPolicy, IsolationRuntime


class PluginExecutionSecurityError(RuntimeError):
    """Raised when isolated execution cannot complete safely."""


@dataclass(frozen=True)
class IsolatedExecutionLimits:
    """Limits enforced by the parent process."""

    timeout_seconds: float = 5.0
    max_result_bytes: int = 1_000_000
    max_request_bytes: int = 1_000_000
    max_stdout_bytes: int = 1_000_000
    max_stderr_bytes: int = 1_000_000


class IsolatedPluginExecutor(IsolationRuntime):
    """Execute external plugin entrypoints in a short-lived child process."""

    runtime_name = "python-subprocess"

    def execute_request(self, request: dict[str, Any], policy: IsolationPolicy) -> Any:
        """Execute a provider request while preserving the JSON subprocess boundary."""
        return self.execute(
            Path(request["module_path"]),
            str(request["class_name"]),
            request.get("payload"),
            request.get("context"),
            str(request.get("operation", "execute")),
            request.get("environment"),
        )

    def __init__(self, limits: IsolatedExecutionLimits | None = None, policy: IsolationPolicy | None = None) -> None:
        self.limits = limits or IsolatedExecutionLimits()
        self.policy = policy or IsolationPolicy(
            timeout_seconds=self.limits.timeout_seconds,
            max_request_bytes=self.limits.max_request_bytes,
            max_stdout_bytes=self.limits.max_stdout_bytes,
            max_stderr_bytes=self.limits.max_stderr_bytes,
            max_result_bytes=self.limits.max_result_bytes,
            isolation_level=IsolationLevel.DEVELOPMENT_SUBPROCESS,
            filesystem_mode="temporary-artifact",
        )

    def can_enforce(self, policy: IsolationPolicy | None = None) -> EnforcementDecision:
        """Report the guarantees this development subprocess can actually provide."""
        requested = policy or self.policy
        try:
            requested.validate()
        except ValueError as exc:
            return EnforcementDecision(False, self.runtime_name, str(exc))
        if requested.isolation_level is not IsolationLevel.DEVELOPMENT_SUBPROCESS:
            return EnforcementDecision(False, self.runtime_name, "Production isolation requires a deployment runtime")
        if requested.allow_network:
            return EnforcementDecision(False, self.runtime_name, "Network isolation is unavailable")
        return EnforcementDecision(
            True,
            self.runtime_name,
            "Development-only subprocess boundary; CPU, memory, network, and OS filesystem limits are not enforced",
        )

    def execute(
        self,
        module_path: Path,
        class_name: str,
        payload: Any,
        context: dict[str, Any] | None = None,
        operation: str = "execute",
        allowed_environment: dict[str, str] | None = None,
    ) -> Any:
        """Run an external entrypoint with timeout and bounded serialized output."""
        decision = self.can_enforce()
        if not decision.enforceable:
            raise PluginExecutionSecurityError(decision.reason or "Isolation policy is unavailable")
        with tempfile.TemporaryDirectory(prefix="pharmatrybe-plugin-") as working_directory:
            request = json.dumps({"module_path": str(module_path), "class_name": class_name, "operation": operation, "payload": payload, "context": context, "environment": allowed_environment or {}})
            if len(request.encode("utf-8")) > self.limits.max_request_bytes:
                raise PluginExecutionSecurityError("External plugin request exceeded the input limit")
            child_environment = dict(allowed_environment or {})
            child_environment.setdefault("PYTHONPATH", str(Path(__file__).parents[3]))
            process = subprocess.Popen(
                [sys.executable, "-m", "app.plugins.security.worker"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=working_directory,
                env=child_environment,
                text=True,
            )
            try:
                stdout, stderr = process.communicate(request, timeout=self.limits.timeout_seconds)
            except subprocess.TimeoutExpired:
                process.kill()
                process.communicate()
                raise PluginExecutionSecurityError("External plugin execution timed out")
            if process.returncode != 0:
                raise PluginExecutionSecurityError("External plugin execution failed")
            if len(stdout.encode("utf-8")) > self.limits.max_stdout_bytes:
                raise PluginExecutionSecurityError("External plugin stdout exceeded the output limit")
            if len(stderr.encode("utf-8")) > self.limits.max_stderr_bytes:
                raise PluginExecutionSecurityError("External plugin stderr exceeded the output limit")
            try:
                result = json.loads(stdout)
            except json.JSONDecodeError as exc:
                raise PluginExecutionSecurityError("External plugin returned malformed output") from exc
        if len(repr(result).encode("utf-8")) > self.limits.max_result_bytes:
            raise PluginExecutionSecurityError("External plugin result exceeded the output limit")
        if not isinstance(result, dict) or not result.get("success"):
            raise PluginExecutionSecurityError("External plugin execution failed")
        return result.get("result")
