from __future__ import annotations

from typing import Any, Iterable

from app.plugins.base.plugin import BasePlugin, PluginType
from app.plugins.manager.plugin_registry import PluginRegistry
from app.plugins.identity import canonical_plugin_id


class PluginRoutingPolicy:
    """Routing rules for plugin selection without any clinical reasoning.

    The policy decides which registered plugins are relevant for a request based
    on request domain metadata and plugin capabilities. It only routes execution;
    it never evaluates patient risk, contraindications, or treatment logic.
    """

    def route(self, request: Any, registry: PluginRegistry) -> list[BasePlugin]:
        """Return the plugin instances selected for the request."""
        execution_mode = getattr(request, "execution_mode", None)
        plugin_ids = list(getattr(request, "plugin_ids", []) or [])
        prediction_plugins = list(getattr(request, "prediction_plugins", []) or [])
        knowledge_plugins = list(getattr(request, "knowledge_plugins", []) or [])
        plugin_types = list(getattr(request, "plugin_types", []) or [])

        selected_ids: set[str] = set()
        selected_ids.update(plugin_ids)
        selected_ids.update(prediction_plugins)
        selected_ids.update(knowledge_plugins)

        entries = registry._routing_entries()
        if execution_mode in {"HYBRID", "hybrid"}:
            return self._select_explicit(entries, selected_ids, prediction_plugins, knowledge_plugins)

        if execution_mode in {"PREDICTION_ONLY", "prediction_only"}:
            return self._filter_by_type(entries, PluginType.PREDICTION, selected_ids)

        if execution_mode in {"KNOWLEDGE_ONLY", "knowledge_only"}:
            return self._filter_by_type(entries, PluginType.KNOWLEDGE, selected_ids)

        if execution_mode in {"AUTO", "AUTOMATIC", "automatic"} or execution_mode is None:
            return self._route_automatic(request, entries, selected_ids, plugin_types)

        if execution_mode in {"USER_SELECTED", "user_selected"}:
            return self._filter_by_ids(entries, selected_ids or list(entries.keys()))

        if execution_mode in {"WORKFLOW_SELECTED", "workflow_selected"}:
            return self._filter_by_types(entries, plugin_types or [PluginType.PREDICTION, PluginType.KNOWLEDGE])

        return self._route_automatic(request, entries, selected_ids, plugin_types)

    def _route_automatic(self, request: Any, entries: dict[str, Any], selected_ids: set[str], plugin_types: list[PluginType]) -> list[BasePlugin]:
        domain = self._infer_domain(request)
        if domain:
            prediction_candidates = self._select_by_domain(entries, PluginType.PREDICTION, domain)
            knowledge_candidates = self._select_by_domain(entries, PluginType.KNOWLEDGE, domain)
            if prediction_candidates or knowledge_candidates:
                return prediction_candidates + knowledge_candidates

        if plugin_types:
            return self._filter_by_types(entries, plugin_types)

        prediction_candidates = self._filter_by_type(entries, PluginType.PREDICTION, selected_ids)
        knowledge_candidates = self._filter_by_type(entries, PluginType.KNOWLEDGE, selected_ids)
        if prediction_candidates or knowledge_candidates:
            return prediction_candidates + knowledge_candidates

        return [entry.plugin for entry in entries.values() if entry.enabled]

    def _select_explicit(
        self,
        entries: dict[str, Any],
        selected_ids: set[str],
        prediction_plugins: list[str],
        knowledge_plugins: list[str],
    ) -> list[BasePlugin]:
        explicit_ids = set(prediction_plugins) | set(knowledge_plugins)
        ids_to_run = selected_ids if selected_ids else explicit_ids
        return self._filter_by_ids(entries, ids_to_run)

    def _filter_by_type(self, entries: dict[str, Any], plugin_type: PluginType, selected_ids: set[str] | None = None) -> list[BasePlugin]:
        selected = []
        for entry in entries.values():
            if not entry.enabled:
                continue
            if selected_ids and canonical_plugin_id(entry.manifest.plugin_id) not in {
                canonical_plugin_id(plugin_id) for plugin_id in selected_ids
            }:
                continue
            if entry.manifest.plugin_type == plugin_type:
                selected.append(entry.plugin)
        return selected

    def _filter_by_types(self, entries: dict[str, Any], plugin_types: Iterable[PluginType]) -> list[BasePlugin]:
        types = set(plugin_types)
        selected = []
        for entry in entries.values():
            if not entry.enabled:
                continue
            if entry.manifest.plugin_type in types:
                selected.append(entry.plugin)
        return selected

    def _filter_by_ids(self, entries: dict[str, Any], plugin_ids: Iterable[str]) -> list[BasePlugin]:
        requested = {canonical_plugin_id(plugin_id) for plugin_id in plugin_ids}
        selected = []
        for entry in entries.values():
            if not entry.enabled:
                continue
            if requested and canonical_plugin_id(entry.manifest.plugin_id) not in requested:
                continue
            selected.append(entry.plugin)
        return selected

    def _select_by_domain(self, entries: dict[str, Any], plugin_type: PluginType, domain: str) -> list[BasePlugin]:
        normalized_domain = domain.lower().replace("_", " ").strip()
        matches: list[BasePlugin] = []
        for entry in entries.values():
            if not entry.enabled:
                continue
            if entry.manifest.plugin_type != plugin_type:
                continue
            manifest = entry.manifest
            supported_domains = [str(item).lower() for item in manifest.supported_domains]
            capabilities = [str(item).lower() for item in manifest.capabilities]
            if normalized_domain in supported_domains:
                matches.append(entry.plugin)
                continue
            if normalized_domain in capabilities:
                matches.append(entry.plugin)
        return matches

    def _infer_domain(self, request: Any) -> str | None:
        payload = getattr(request, "payload", {}) or {}
        context = getattr(request, "context", {}) or {}
        values = []
        if isinstance(payload, dict):
            values.extend([
                payload.get("domain"),
                payload.get("infection_type"),
                payload.get("clinical_context"),
                payload.get("infection"),
                payload.get("diagnosis"),
            ])
        if isinstance(context, dict):
            values.extend([
                context.get("domain"),
                context.get("infection_type"),
                context.get("clinical_context"),
            ])
        for value in values:
            if isinstance(value, str) and value.strip():
                return value.strip()
        return None
