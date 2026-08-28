from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.plugins.base.plugin import PluginType
from app.plugins.base.prediction_plugin import DeploymentType


class PluginManifest(BaseModel):
    """Structured plugin manifest representation."""

    plugin_id: str = Field(...)
    plugin_name: str = Field(...)
    plugin_version: str = Field(...)
    plugin_type: PluginType = Field(...)
    deployment_type: Optional[DeploymentType] = Field(default=None)
    description: str = Field(...)
    author: str = Field(...)
    organization: Optional[str] = Field(default=None)
    entrypoint_module: str = Field(...)
    entrypoint_class: str = Field(...)
    capabilities: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    supported_domains: List[str] = Field(default_factory=list)
    configuration_schema: Optional[Dict[str, Any]] = Field(default=None)
    minimum_platform_version: Optional[str] = Field(default=None)
    sdk_version: Optional[str] = Field(default=None)

    class Config:
        allow_population_by_field_name = True
