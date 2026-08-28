"""Official PharmaTrybe role definitions for backend authentication scaffolding."""

from __future__ import annotations

from enum import Enum


class PharmaTrybeRole(str, Enum):
    """Official role values used by PharmaTrybe backend authentication scaffolding."""

    CLINICIAN = "Clinician"
    LABORATORY_SCIENTIST = "Laboratory Scientist"
    STEWARDSHIP_TEAM = "Stewardship Team"
    ADMINISTRATOR = "Administrator"


def normalize_role(value: str | PharmaTrybeRole | None) -> PharmaTrybeRole | None:
    """Normalize a role value into the official PharmaTrybe role enum."""
    if value is None:
        return None
    if isinstance(value, PharmaTrybeRole):
        return value

    normalized_value = str(value).strip()
    for role in PharmaTrybeRole:
        if role.value.lower() == normalized_value.lower():
            return role

    return None
