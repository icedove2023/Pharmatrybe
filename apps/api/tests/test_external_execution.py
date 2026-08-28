from __future__ import annotations

import zipfile
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.database.base import Base
from app.models.identity import Hospital
from app.models.plugin_governance import GovernanceStatus, PluginExecutionAudit
from app.plugins.base.plugin import PluginType
from app.plugins.manager.plugin_manager import PluginManager
from app.plugins.manager.workflow_manager import ClinicalDecisionRequest, ExecutionMode, WorkflowManager
from app.plugins.security.artifact import PluginArtifactService
from app.services.plugin_governance import PluginGovernanceService
from app.auth.tenant_context import TenantContext
from app.plugins.security.isolated_executor import IsolatedExecutionLimits, IsolatedPluginExecutor, PluginExecutionSecurityError


PLUGIN_SOURCE = '''
from app.plugins.base.plugin import BasePlugin, PluginHealth, PluginMetadata, PluginType
from app.plugins.base.prediction_plugin import DeploymentType, PredictionPlugin, PredictionRequest, PredictionResult
from datetime import datetime, timezone

class ExternalPrediction(PredictionPlugin):
    @property
    def plugin_id(self): return "external_prediction"
    @property
    def plugin_name(self): return "External Prediction"
    @property
    def plugin_version(self): return "1.0.0"
    @property
    def plugin_type(self): return PluginType.PREDICTION
    @property
    def plugin_description(self): return "test"
    @property
    def author(self): return "test"
    @property
    def capabilities(self): return ["READ_AMR_DATA"]
    @property
    def dependencies(self): return []
    @property
    def deployment_type(self): return DeploymentType.ARTIFACT
    def initialize(self): pass
    def shutdown(self): pass
    def configure(self, configuration): pass
    def validate(self): return True
    def load(self): pass
    def unload(self): pass
    def supports(self, request): return True
    def input_schema(self): return {}
    def output_schema(self): return {}
    def metadata(self): return PluginMetadata(self.plugin_id, self.plugin_name, self.plugin_version, self.plugin_type, self.plugin_description, self.author, self.capabilities, self.dependencies)
    def health(self): return PluginHealth(True, "ok", "ok", datetime.now(timezone.utc))
    def predict(self, request): return PredictionResult("R", {"R": 0.9}, 0.9, self.plugin_name, self.plugin_version, 1.0, {"isolated": True})
'''


def test_approved_external_plugin_executes_in_child_and_rechecks_governance(tmp_path: Path) -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine, tables=[Hospital.__table__])
    from app.models.plugin_governance import PluginGovernanceAuditEvent, PluginGovernanceRecord
    Base.metadata.create_all(engine, tables=[PluginGovernanceRecord.__table__, PluginGovernanceAuditEvent.__table__, PluginExecutionAudit.__table__])
    session = Session(engine)
    session.add(Hospital(id="h-1", name="Hospital"))
    session.commit()

    plugin_dir = tmp_path / "external_prediction"
    plugin_dir.mkdir()
    manifest = """plugin_id: external_prediction
plugin_name: External Prediction
plugin_version: 1.0.0
plugin_type: prediction
description: test
author: test
entrypoint_module: entrypoint
entrypoint_class: ExternalPrediction
capabilities:
  - READ_AMR_DATA
dependencies: []
minimum_platform_version: 1.0.0
sdk_version: 1.0.0
"""
    (plugin_dir / "plugin.yaml").write_text(manifest, encoding="utf-8")
    (plugin_dir / "entrypoint.py").write_text(PLUGIN_SOURCE, encoding="utf-8")
    artifact = tmp_path / "external_prediction.zip"
    with zipfile.ZipFile(artifact, "w") as archive:
        archive.write(plugin_dir / "plugin.yaml", "plugin.yaml")
        archive.write(plugin_dir / "entrypoint.py", "entrypoint.py")
    digest = PluginArtifactService().inspect(artifact).sha256

    governance = PluginGovernanceService(session)
    governance.register_plugin(
        hospital_id="h-1", plugin_id="external_prediction", plugin_name="External Prediction",
        plugin_type="prediction", plugin_version="1.0.0", plugin_origin="external",
        owner="Hospital", publisher="Hospital", artifact_hash=digest, artifact_uri=str(artifact),
        capabilities=["READ_AMR_DATA"], submitted_by_user_id="admin",
    )
    governance.validate_plugin("external_prediction", hospital_id="h-1")
    governance.approve_plugin("external_prediction", hospital_id="h-1", approved_by_user_id="admin")
    governance.activate_plugin("external_prediction", hospital_id="h-1")

    tenant = TenantContext(hospital_id="h-1", authenticated_user_id="admin", professional_id="professional-1")
    manager = PluginManager(plugin_dir, "1.0.0", "1.0.0", governance_service=governance, tenant_context=tenant)
    loaded = manager.load_all_plugins()
    assert loaded[0].success is True
    workflow = WorkflowManager(manager.registry)
    result = workflow.execute(ClinicalDecisionRequest("p-1", {"organism": "test"}, tenant_context=tenant, execution_mode=ExecutionMode.USER_SELECTED, plugin_ids=["external_prediction"]))
    assert result[0].success is True
    assert result[0].metadata["request_id"] is None
    assert session.query(PluginExecutionAudit).count() == 1

    proxy = manager.registry.resolve_plugin(tenant, "external_prediction")
    proxy.manifest.plugin_version = "9.9.9"
    identity_blocked = workflow.execute(ClinicalDecisionRequest(
        "p-1", {"organism": "test"}, tenant_context=tenant,
        execution_mode=ExecutionMode.USER_SELECTED, plugin_ids=["external_prediction"],
    ))
    assert identity_blocked[0].success is False
    assert "manifest identity" in identity_blocked[0].error
    proxy.manifest.plugin_version = "1.0.0"

    record = governance.get_record("external_prediction", hospital_id="h-1")
    record.capabilities = ["READ_AMR_DATA", "FILE_WRITE"]
    session.commit()
    capability_blocked = workflow.execute(ClinicalDecisionRequest(
        "p-1", {"organism": "test"}, tenant_context=tenant,
        execution_mode=ExecutionMode.USER_SELECTED, plugin_ids=["external_prediction"],
    ))
    assert capability_blocked[0].success is False
    assert "capability identity" in capability_blocked[0].error
    record.capabilities = ["READ_AMR_DATA"]
    session.commit()

    original_artifact = artifact.read_bytes()
    artifact.write_bytes(original_artifact + b"tampered")
    artifact_blocked = workflow.execute(ClinicalDecisionRequest(
        "p-1", {"organism": "test"}, tenant_context=tenant,
        execution_mode=ExecutionMode.USER_SELECTED, plugin_ids=["external_prediction"],
    ))
    assert artifact_blocked[0].success is False
    assert "artifact identity" in artifact_blocked[0].error
    artifact.write_bytes(original_artifact)

    governance.revoke_plugin("external_prediction", hospital_id="h-1", actor_user_id="admin")
    blocked = workflow.execute(ClinicalDecisionRequest("p-1", {"organism": "test"}, tenant_context=tenant, execution_mode=ExecutionMode.USER_SELECTED, plugin_ids=["external_prediction"]))
    assert blocked[0].success is False
    assert "runtime-eligible" in blocked[0].error
    assert session.query(PluginExecutionAudit).count() == 5
    assert session.query(PluginExecutionAudit).order_by(PluginExecutionAudit.completed_at.desc()).first().decision == "DENY"


def test_isolated_executor_timeout_terminates_child(tmp_path: Path) -> None:
    module = tmp_path / "slow.py"
    module.write_text("import time\ndef run(payload, context):\n    time.sleep(1)\n    return {}\n", encoding="utf-8")
    executor = IsolatedPluginExecutor(IsolatedExecutionLimits(timeout_seconds=0.05))
    try:
        executor.execute(module, "Slow", {}, {}, "execute")
    except PluginExecutionSecurityError as exc:
        assert "timed out" in str(exc)
    else:
        raise AssertionError("Expected isolated execution timeout")


def test_isolated_executor_does_not_inherit_parent_secret(tmp_path: Path, monkeypatch) -> None:
    module = tmp_path / "environment.py"
    module.write_text("import os\nclass EnvironmentPlugin:\n    def initialize(self): pass\n    def run(self, payload, context): return os.getenv('R9_SENTINEL_SECRET', 'missing')\n", encoding="utf-8")
    monkeypatch.setenv("R9_SENTINEL_SECRET", "must-not-cross-boundary")
    result = IsolatedPluginExecutor().execute(module, "EnvironmentPlugin", {}, {}, "execute")
    assert result == "missing"
