"""ARMD plugin audit placeholders.

Architecture-only: collect or validate runtime/component registration
for certification. No legacy WP4/WP5 code included.
"""

from pathlib import Path


def audit_structure():
    """Return a dict describing the ARMD plugin structure (placeholder)."""
    base = Path(__file__).parent
    return {p.name: str(p) for p in sorted(base.iterdir())}
