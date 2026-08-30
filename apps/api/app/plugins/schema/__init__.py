"""Schema discovery and composition for plugin input contracts."""

from .composer import PluginSchemaComposer
from .discovery import SchemaDiscoveryService

__all__ = ["SchemaDiscoveryService", "PluginSchemaComposer"]
