from __future__ import annotations

from typing import Any, Dict, Iterable, List


class EvidenceMerger:
    """Merges plugin evidence with clinical rule findings for downstream use."""

    def merge(self, context: Any, clinical_rule_results: Iterable[Any] | None = None) -> Dict[str, Any]:
        rule_results = list(clinical_rule_results or [])
        merged = {
            "prediction_outputs": getattr(context, "prediction_outputs", []),
            "knowledge_outputs": getattr(context, "knowledge_outputs", []),
            "plugin_metadata": getattr(context, "plugin_metadata", []),
            "execution_metadata": getattr(context, "execution_metadata", {}),
            "clinical_rule_results": [self._serialize_rule(item) for item in rule_results],
        }
        return merged

    def _serialize_rule(self, item: Any) -> Dict[str, Any]:
        if hasattr(item, "to_dict"):
            return item.to_dict()
        if isinstance(item, dict):
            return item
        return {"value": str(item)}
