from __future__ import annotations

from pathlib import Path

from app.plugins.security.container_runtime import ContainerIsolationRuntime
from app.plugins.security.isolation_policy import IsolationLevel, IsolationPolicy, NetworkMode
from app.plugins.security.isolated_executor import IsolatedPluginExecutor, PluginExecutionSecurityError


def test_development_executor_does_not_claim_production_resource_isolation() -> None:
    executor = IsolatedPluginExecutor()
    decision = executor.can_enforce(IsolationPolicy())
    assert decision.enforceable is False
    assert "deployment runtime" in (decision.reason or "")


def test_container_runtime_propagates_resource_and_security_policy() -> None:
    policy = IsolationPolicy(
        isolation_level=IsolationLevel.CONTAINER,
        network_mode=NetworkMode.DENIED,
        execution_identity="pharmatrybe-plugin",
    )
    runtime = ContainerIsolationRuntime("pharmatrybe/plugin-runtime", executable="docker-not-installed")
    decision = runtime.can_enforce(policy)
    assert decision.enforceable is False
    try:
        runtime.build_command({"artifact_path": Path("artifact.zip")}, policy)
    except RuntimeError as exc:
        assert "unavailable" in str(exc).lower()
    else:
        raise AssertionError("Unavailable container runtime must fail closed")


def test_network_access_policy_is_invalid_without_allowlist() -> None:
    try:
        IsolationPolicy(allow_network=True).validate()
    except ValueError as exc:
        assert "allowlisted" in str(exc)
    else:
        raise AssertionError("Network access without allowlisting must be rejected")
