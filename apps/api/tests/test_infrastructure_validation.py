"""Infrastructure validation tests for Knowledge Plugin system.

Tests verify that the existing Knowledge Plugin infrastructure (registry,
routing, workflow manager, and lifecycle) is working correctly.

This is verification-only; no plugin implementations are tested.
"""

import pytest
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from app.plugins.base.plugin import BasePlugin, PluginType, PluginMetadata, PluginHealth
from app.plugins.base.knowledge_plugin import KnowledgePlugin
from app.plugins.manager.plugin_registry import PluginRegistry, PluginRegistryEntry
from app.plugins.manager.plugin_routing_policy import PluginRoutingPolicy
from app.plugins.manager.workflow_manager import (
    WorkflowManager,
    ClinicalDecisionRequest,
    ExecutionMode,
    PluginExecutionResult,
)
from app.plugins.contracts.plugin_manifest import PluginManifest
from app.auth.tenant_context import TenantContext


# ============================================================================
# Mock Infrastructure Components for Testing
# ============================================================================


@dataclass
class MockKnowledgePlugin(KnowledgePlugin):
    """Minimal knowledge plugin for infrastructure testing."""

    _plugin_id: str = "test_knowledge"
    _domains: List[str] = None
    _connected: bool = False
    _initialized: bool = False

    def __post_init__(self):
        if self._domains is None:
            self._domains = ["respiratory", "gastrointestinal"]

    @property
    def plugin_id(self) -> str:
        return self._plugin_id

    @property
    def plugin_name(self) -> str:
        return "Test Knowledge Plugin"

    @property
    def plugin_version(self) -> str:
        return "0.1.0"

    @property
    def plugin_type(self) -> PluginType:
        return PluginType.KNOWLEDGE

    @property
    def plugin_description(self) -> str:
        return "Mock knowledge plugin for testing"

    @property
    def author(self) -> str:
        return "Test Team"

    @property
    def capabilities(self) -> List[str]:
        return ["test_capability"]

    @property
    def dependencies(self) -> List[str]:
        return []

    def initialize(self) -> None:
        self._initialized = True

    def shutdown(self) -> None:
        self._initialized = False

    def configure(self, configuration: Dict[str, Any]) -> None:
        pass

    def validate(self) -> bool:
        return self._initialized and self._connected

    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id=self.plugin_id,
            plugin_name=self.plugin_name,
            plugin_version=self.plugin_version,
            plugin_type=self.plugin_type,
            description=self.plugin_description,
            author=self.author,
            capabilities=self.capabilities,
            dependencies=self.dependencies,
        )

    def health(self) -> PluginHealth:
        from datetime import datetime, timezone

        return PluginHealth(
            healthy=self._initialized,
            status="healthy" if self._initialized else "unhealthy",
            message="Mock plugin healthy" if self._initialized else "Not initialized",
            timestamp=datetime.now(timezone.utc),
        )

    def connect(self) -> None:
        self._connected = True

    def disconnect(self) -> None:
        self._connected = False

    def search(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        if not self._connected:
            raise ConnectionError("Not connected")
        return [{"source": "test", "entity_id": "e1", "entity_name": f"Result for {query}"}]

    def query(self, criteria: Dict[str, Any]) -> Dict[str, Any]:
        if not self._connected:
            raise ConnectionError("Not connected")
        return {"source": "test", "entity_id": "e1"}

    def supported_domains(self) -> List[str]:
        return self._domains

    def knowledge_version(self) -> str:
        return "TEST 1.0"


# ============================================================================
# Test Suite 1: Plugin Registry
# ============================================================================


class TestPluginRegistry:
    """Verify plugin registry functions correctly."""

    def test_registry_initialization(self) -> None:
        """Plugin registry initializes with empty entries."""
        registry = PluginRegistry()
        assert registry._entries == {}
        assert registry.list_plugins() == []

    def test_registry_register_plugin(self) -> None:
        """Plugin registry successfully registers a plugin."""
        registry = PluginRegistry()
        plugin = MockKnowledgePlugin()
        manifest = PluginManifest(
            plugin_id="test",
            plugin_name="Test",
            plugin_version="0.1.0",
            plugin_type="knowledge",
            description="Test plugin",
            author="Test",
            entrypoint_module="test",
            entrypoint_class="TestPlugin",
            supported_domains=["respiratory"],
            capabilities=["test"],
            dependencies=[],
        )

        registry.register_plugin(manifest, plugin)

        assert "test" in registry._entries
        assert registry.get_plugin("test") is plugin
        assert registry.get_manifest("test") is manifest

    def test_registry_duplicate_registration_fails(self) -> None:
        """Plugin registry rejects duplicate plugin IDs."""
        registry = PluginRegistry()
        plugin = MockKnowledgePlugin()
        manifest = PluginManifest(
            plugin_id="test",
            plugin_name="Test",
            plugin_version="0.1.0",
            plugin_type="knowledge",
            description="Test",
            author="Test",
            entrypoint_module="test",
            entrypoint_class="TestPlugin",
            supported_domains=[],
            capabilities=[],
            dependencies=[],
        )

        registry.register_plugin(manifest, plugin)

        with pytest.raises(ValueError, match="Plugin already registered"):
            registry.register_plugin(manifest, plugin)

    def test_tenant_scoped_registry_keeps_same_ids_isolated(self) -> None:
        """Identical hospital-owned IDs resolve only within their owner tenant."""
        class GovernanceStub:
            def is_runtime_eligible(self, plugin_id: str, hospital_id: str | None = None) -> bool:
                return hospital_id in {"hospital-a", "hospital-b"}

        registry = PluginRegistry(governance_service=GovernanceStub())
        manifest_a = PluginManifest(
            plugin_id="clinical-plugin", plugin_name="A", plugin_version="1.0.0",
            plugin_type="knowledge", description="A", author="A",
            entrypoint_module="plugin", entrypoint_class="Plugin",
            supported_domains=[], capabilities=[], dependencies=[],
        )
        manifest_b = manifest_a.model_copy(update={"plugin_name": "B"})
        plugin_a = MockKnowledgePlugin(_plugin_id="clinical-plugin")
        plugin_b = MockKnowledgePlugin(_plugin_id="clinical-plugin")
        registry.register_plugin(manifest_a, plugin_a, owner_hospital_id="hospital-a")
        registry.register_plugin(manifest_b, plugin_b, owner_hospital_id="hospital-b")

        tenant_a = TenantContext(hospital_id="hospital-a", authenticated_user_id="user-a")
        tenant_b = TenantContext(hospital_id="hospital-b", authenticated_user_id="user-b")
        assert registry.resolve_plugin(tenant_a, "clinical-plugin") is plugin_a
        assert registry.resolve_plugin(tenant_b, "clinical-plugin") is plugin_b
        assert registry.get_plugin("clinical-plugin") is None

    def test_internal_plugins_require_explicit_system_context(self) -> None:
        registry = PluginRegistry()
        plugin = MockKnowledgePlugin(_plugin_id="soar")
        manifest = PluginManifest(
            plugin_id="SOAR", plugin_name="SOAR", plugin_version="1.0.0",
            plugin_type="knowledge", description="SOAR", author="Platform",
            entrypoint_module="plugin", entrypoint_class="Plugin",
            supported_domains=[], capabilities=[], dependencies=[],
        )
        registry.register_plugin(manifest, plugin)

        hospital = TenantContext(hospital_id="hospital-a", authenticated_user_id="user-a")
        assert registry.resolve_plugin(hospital, "SOAR") is None
        assert registry.resolve_plugin(TenantContext.system(), "SOAR") is plugin

    def test_registry_unregister_plugin(self) -> None:
        """Plugin registry successfully unregisters a plugin."""
        registry = PluginRegistry()
        plugin = MockKnowledgePlugin()
        manifest = PluginManifest(
            plugin_id="test",
            plugin_name="Test",
            plugin_version="0.1.0",
            plugin_type="knowledge",
            description="Test",
            author="Test",
            entrypoint_module="test",
            entrypoint_class="TestPlugin",
            supported_domains=[],
            capabilities=[],
            dependencies=[],
        )

        registry.register_plugin(manifest, plugin)
        registry.unregister_plugin("test")

        assert "test" not in registry._entries
        assert registry.get_plugin("test") is None

    def test_registry_metadata_retrieval(self) -> None:
        """Plugin registry retrieves metadata correctly."""
        registry = PluginRegistry()
        plugin = MockKnowledgePlugin(_plugin_id="test")
        manifest = PluginManifest(
            plugin_id="test",
            plugin_name="Test Plugin",
            plugin_version="0.1.0",
            plugin_type="knowledge",
            description="Test",
            author="Test Author",
            entrypoint_module="test",
            entrypoint_class="TestPlugin",
            supported_domains=["respiratory"],
            capabilities=["test_cap"],
            dependencies=["dep1"],
        )

        registry.register_plugin(manifest, plugin)
        metadata = registry.get_metadata("test")

        assert metadata is not None
        assert metadata.plugin_id == "test"
        assert metadata.plugin_name == "Test Knowledge Plugin"
        assert metadata.author == "Test Team"  # From plugin.author property

    def test_registry_health_retrieval(self) -> None:
        """Plugin registry retrieves health status correctly."""
        registry = PluginRegistry()
        plugin = MockKnowledgePlugin(_plugin_id="test")
        manifest = PluginManifest(
            plugin_id="test",
            plugin_name="Test",
            plugin_version="0.1.0",
            plugin_type="knowledge",
            description="Test",
            author="Test",
            entrypoint_module="test",
            entrypoint_class="TestPlugin",
            supported_domains=[],
            capabilities=[],
            dependencies=[],
        )

        registry.register_plugin(manifest, plugin)
        plugin.initialize()

        health = registry.get_health("test")

        assert health is not None
        assert health.healthy is True
        assert health.status == "healthy"

    def test_registry_enable_disable_plugin(self) -> None:
        """Plugin registry enables and disables plugins."""
        registry = PluginRegistry()
        plugin = MockKnowledgePlugin()
        manifest = PluginManifest(
            plugin_id="test",
            plugin_name="Test",
            plugin_version="0.1.0",
            plugin_type="knowledge",
            description="Test",
            author="Test",
            entrypoint_module="test",
            entrypoint_class="TestPlugin",
            supported_domains=[],
            capabilities=[],
            dependencies=[],
        )

        registry.register_plugin(manifest, plugin, enabled=True)
        assert registry.is_enabled("test") is True

        registry.disable_plugin("test")
        assert registry.is_enabled("test") is False

        registry.enable_plugin("test")
        assert registry.is_enabled("test") is True

    def test_registry_list_plugins(self) -> None:
        """Plugin registry lists all registered plugins."""
        registry = PluginRegistry()

        for i in range(3):
            plugin = MockKnowledgePlugin(_plugin_id=f"test_{i}")
            manifest = PluginManifest(
                plugin_id=f"test_{i}",
                plugin_name=f"Test {i}",
                plugin_version="0.1.0",
                plugin_type="knowledge",
                description="Test",
                author="Test",
                entrypoint_module="test",
                entrypoint_class="TestPlugin",
                supported_domains=[],
                capabilities=[],
                dependencies=[],
            )
            registry.register_plugin(manifest, plugin)

        plugins = registry.list_plugins()
        assert len(plugins) == 3

    def test_registry_group_plugins_by_type(self) -> None:
        """Plugin registry groups plugins by type."""
        registry = PluginRegistry()

        plugin = MockKnowledgePlugin()
        manifest = PluginManifest(
            plugin_id="test",
            plugin_name="Test",
            plugin_version="0.1.0",
            plugin_type="knowledge",
            description="Test",
            author="Test",
            entrypoint_module="test",
            entrypoint_class="TestPlugin",
            supported_domains=[],
            capabilities=[],
            dependencies=[],
        )

        registry.register_plugin(manifest, plugin)

        grouped = registry.group_plugins_by_type()

        assert PluginType.KNOWLEDGE in grouped
        assert plugin in grouped[PluginType.KNOWLEDGE]


# ============================================================================
# Test Suite 2: Plugin Routing Policy
# ============================================================================


class TestPluginRoutingPolicy:
    """Verify plugin routing policy selects plugins correctly."""

    def test_routing_auto_mode_by_domain(self) -> None:
        """Routing policy AUTO mode selects by domain."""
        registry = PluginRegistry()
        plugin = MockKnowledgePlugin(_plugin_id="test", _domains=["respiratory"])
        manifest = PluginManifest(
            plugin_id="test",
            plugin_name="Test",
            plugin_version="0.1.0",
            plugin_type="knowledge",
            description="Test",
            author="Test",
            entrypoint_module="test",
            entrypoint_class="TestPlugin",
            supported_domains=["respiratory"],
            capabilities=[],
            dependencies=[],
        )

        registry.register_plugin(manifest, plugin)

        request = type("Request", (), {
            "execution_mode": ExecutionMode.AUTO,
            "payload": {"domain": "respiratory"},
            "context": None,
        })()

        policy = PluginRoutingPolicy()
        selected = policy.route(request, registry)

        assert plugin in selected

    def test_routing_auto_mode_domain_mismatch_fallback(self) -> None:
        """Routing policy AUTO mode falls back to all enabled plugins if domain mismatch."""
        registry = PluginRegistry()
        plugin = MockKnowledgePlugin(_plugin_id="test", _domains=["respiratory"])
        manifest = PluginManifest(
            plugin_id="test",
            plugin_name="Test",
            plugin_version="0.1.0",
            plugin_type="knowledge",
            description="Test",
            author="Test",
            entrypoint_module="test",
            entrypoint_class="TestPlugin",
            supported_domains=["respiratory"],
            capabilities=[],
            dependencies=[],
        )

        registry.register_plugin(manifest, plugin, enabled=True)

        # Request with domain that doesn't match any plugin
        request = type("Request", (), {
            "execution_mode": ExecutionMode.AUTO,
            "payload": {"domain": "cardiac"},  # Mismatch - no plugins support this
            "context": None,
        })()

        policy = PluginRoutingPolicy()
        selected = policy.route(request, registry)

        # AUTO mode falls back to all enabled plugins when domain has no matches
        assert plugin in selected

    def test_routing_knowledge_only_mode(self) -> None:
        """Routing policy KNOWLEDGE_ONLY selects all knowledge plugins."""
        registry = PluginRegistry()
        plugin = MockKnowledgePlugin(_plugin_id="test")
        manifest = PluginManifest(
            plugin_id="test",
            plugin_name="Test",
            plugin_version="0.1.0",
            plugin_type="knowledge",
            description="Test",
            author="Test",
            entrypoint_module="test",
            entrypoint_class="TestPlugin",
            supported_domains=[],
            capabilities=[],
            dependencies=[],
        )

        registry.register_plugin(manifest, plugin)

        request = type("Request", (), {
            "execution_mode": ExecutionMode.KNOWLEDGE_ONLY,
            "payload": {},
            "context": None,
        })()

        policy = PluginRoutingPolicy()
        selected = policy.route(request, registry)

        assert plugin in selected

    def test_routing_user_selected_mode(self) -> None:
        """Routing policy USER_SELECTED filters by plugin IDs."""
        registry = PluginRegistry()
        plugin1 = MockKnowledgePlugin(_plugin_id="test_1")
        plugin2 = MockKnowledgePlugin(_plugin_id="test_2")

        for i, plugin in enumerate([plugin1, plugin2], start=1):
            manifest = PluginManifest(
                plugin_id=f"test_{i}",
                plugin_name=f"Test {i}",
                plugin_version="0.1.0",
                plugin_type="knowledge",
                description="Test",
                author="Test",
                entrypoint_module="test",
                entrypoint_class="TestPlugin",
                supported_domains=[],
                capabilities=[],
                dependencies=[],
            )
            registry.register_plugin(manifest, plugin)

        request = type("Request", (), {
            "execution_mode": ExecutionMode.USER_SELECTED,
            "plugin_ids": ["test_1"],
            "payload": {},
            "context": None,
        })()

        policy = PluginRoutingPolicy()
        selected = policy.route(request, registry)

        assert plugin1 in selected
        assert plugin2 not in selected

    def test_routing_respects_enabled_flag(self) -> None:
        """Routing policy excludes disabled plugins."""
        registry = PluginRegistry()
        plugin = MockKnowledgePlugin(_plugin_id="test")
        manifest = PluginManifest(
            plugin_id="test",
            plugin_name="Test",
            plugin_version="0.1.0",
            plugin_type="knowledge",
            description="Test",
            author="Test",
            entrypoint_module="test",
            entrypoint_class="TestPlugin",
            supported_domains=["respiratory"],
            capabilities=[],
            dependencies=[],
        )

        registry.register_plugin(manifest, plugin, enabled=False)

        request = type("Request", (), {
            "execution_mode": ExecutionMode.AUTO,
            "payload": {"domain": "respiratory"},
            "context": None,
        })()

        policy = PluginRoutingPolicy()
        selected = policy.route(request, registry)

        assert plugin not in selected


# ============================================================================
# Test Suite 3: Workflow Manager
# ============================================================================


class TestWorkflowManager:
    """Verify workflow manager executes plugins correctly."""

    def test_workflow_selects_plugins(self) -> None:
        """Workflow manager selects plugins via routing policy."""
        registry = PluginRegistry()
        plugin = MockKnowledgePlugin(_plugin_id="test")
        plugin.initialize()
        plugin.connect()

        manifest = PluginManifest(
            plugin_id="test",
            plugin_name="Test",
            plugin_version="0.1.0",
            plugin_type="knowledge",
            description="Test",
            author="Test",
            entrypoint_module="test",
            entrypoint_class="TestPlugin",
            supported_domains=["respiratory"],
            capabilities=[],
            dependencies=[],
        )

        registry.register_plugin(manifest, plugin)

        manager = WorkflowManager(registry)
        request = ClinicalDecisionRequest(
            patient_id="p1",
            payload={"query": "test"},
            context={"domain": "respiratory"},
            execution_mode=ExecutionMode.AUTO,
        )

        results = manager.execute(request)

        assert len(results) > 0
        assert any(r.plugin_id == "test" for r in results)

    def test_workflow_execution_success(self) -> None:
        """Workflow manager marks successful executions."""
        registry = PluginRegistry()
        plugin = MockKnowledgePlugin(_plugin_id="test")
        plugin.initialize()
        plugin.connect()

        manifest = PluginManifest(
            plugin_id="test",
            plugin_name="Test",
            plugin_version="0.1.0",
            plugin_type="knowledge",
            description="Test",
            author="Test",
            entrypoint_module="test",
            entrypoint_class="TestPlugin",
            supported_domains=["respiratory"],
            capabilities=[],
            dependencies=[],
        )

        registry.register_plugin(manifest, plugin)

        manager = WorkflowManager(registry)
        request = ClinicalDecisionRequest(
            patient_id="p1",
            payload={"query": "test"},
            context={"domain": "respiratory"},
            execution_mode=ExecutionMode.AUTO,
        )

        results = manager.execute(request)
        test_result = next((r for r in results if r.plugin_id == "test"), None)

        assert test_result is not None
        assert test_result.success is True
        assert test_result.result is not None

    def test_workflow_execution_failure_isolation(self) -> None:
        """Workflow manager isolates plugin failures."""

        class FailingPlugin(MockKnowledgePlugin):
            def search(self, query: str, filters: Optional[Dict[str, Any]] = None):
                raise RuntimeError("Intentional failure")

        registry = PluginRegistry()
        plugin = FailingPlugin(_plugin_id="test")
        plugin.initialize()
        plugin.connect()

        manifest = PluginManifest(
            plugin_id="test",
            plugin_name="Test",
            plugin_version="0.1.0",
            plugin_type="knowledge",
            description="Test",
            author="Test",
            entrypoint_module="test",
            entrypoint_class="TestPlugin",
            supported_domains=["respiratory"],
            capabilities=[],
            dependencies=[],
        )

        registry.register_plugin(manifest, plugin)

        manager = WorkflowManager(registry)
        request = ClinicalDecisionRequest(
            patient_id="p1",
            payload={"query": "test"},
            context={"domain": "respiratory"},
            execution_mode=ExecutionMode.AUTO,
        )

        results = manager.execute(request)
        test_result = next((r for r in results if r.plugin_id == "test"), None)

        assert test_result is not None
        assert test_result.success is False
        assert test_result.error is not None

    def test_workflow_builds_decision_context(self) -> None:
        """Workflow manager builds clinical decision context."""
        registry = PluginRegistry()
        plugin = MockKnowledgePlugin(_plugin_id="test")
        plugin.initialize()
        plugin.connect()

        manifest = PluginManifest(
            plugin_id="test",
            plugin_name="Test",
            plugin_version="0.1.0",
            plugin_type="knowledge",
            description="Test",
            author="Test",
            entrypoint_module="test",
            entrypoint_class="TestPlugin",
            supported_domains=["respiratory"],
            capabilities=[],
            dependencies=[],
        )

        registry.register_plugin(manifest, plugin)

        manager = WorkflowManager(registry)
        request = ClinicalDecisionRequest(
            patient_id="p1",
            payload={"query": "test"},
            context={"domain": "respiratory"},
            execution_mode=ExecutionMode.AUTO,
        )

        results = manager.execute(request)
        context = manager.get_context(request, results)

        assert context.patient_id == "p1"
        assert len(context.knowledge_outputs) > 0
        assert context.knowledge_outputs[0]["plugin_id"] == "test"


# ============================================================================
# Test Suite 4: Plugin Lifecycle
# ============================================================================


class TestPluginLifecycle:
    """Verify plugin lifecycle management works correctly."""

    def test_plugin_initialization(self) -> None:
        """Plugin initializes and transitions to initialized state."""
        plugin = MockKnowledgePlugin()

        assert plugin.validate() is False  # Not connected

        plugin.initialize()

        assert plugin.validate() is False  # Connected but not initialized+connected
        plugin.connect()

        assert plugin.validate() is True

    def test_plugin_health_before_init(self) -> None:
        """Plugin health indicates uninitialized state."""
        plugin = MockKnowledgePlugin()

        health = plugin.health()

        assert health.healthy is False
        assert health.status == "unhealthy"

    def test_plugin_health_after_init(self) -> None:
        """Plugin health indicates healthy state after initialization."""
        plugin = MockKnowledgePlugin()
        plugin.initialize()

        health = plugin.health()

        assert health.healthy is True
        assert health.status == "healthy"

    def test_plugin_shutdown(self) -> None:
        """Plugin shuts down cleanly."""
        plugin = MockKnowledgePlugin()
        plugin.initialize()
        plugin.connect()

        assert plugin.validate() is True

        plugin.disconnect()
        plugin.shutdown()

        assert plugin.validate() is False

    def test_plugin_metadata_availability(self) -> None:
        """Plugin metadata is always available."""
        plugin = MockKnowledgePlugin()

        # Before initialization
        metadata = plugin.metadata()
        assert metadata.plugin_id == "test_knowledge"
        assert metadata.plugin_name == "Test Knowledge Plugin"

        # After initialization
        plugin.initialize()
        metadata = plugin.metadata()
        assert metadata.plugin_id == "test_knowledge"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
