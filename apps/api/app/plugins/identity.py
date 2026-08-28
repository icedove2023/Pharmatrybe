"""Canonical plugin identifiers and explicit legacy normalization."""

from __future__ import annotations

CANONICAL_INTERNAL_PLUGIN_IDS = frozenset({"soar", "armd", "who_knowledge"})
INTERNAL_PLUGIN_ALIASES = {
    "SOAR": "soar",
    "ARMD": "armd",
    "WHO": "who_knowledge",
    "WHO_KNOWLEDGE": "who_knowledge",
}


def canonical_plugin_id(plugin_id: str) -> str:
    """Normalize a known legacy identifier at the runtime boundary."""
    normalized = plugin_id.strip()
    return INTERNAL_PLUGIN_ALIASES.get(normalized.upper(), normalized)


def is_internal_plugin(plugin_id: str) -> bool:
    """Return whether an identifier is one of the platform-owned plugins."""
    return canonical_plugin_id(plugin_id) in CANONICAL_INTERNAL_PLUGIN_IDS
