"""Immutable tenant identity contract for governed runtime operations."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class TenantContext:
    """Authenticated tenant context; callers cannot mutate or select its tenant."""

    hospital_id: str
    authenticated_user_id: str | None = None
    professional_id: str | None = None
    role: str | None = None
    permissions: frozenset[str] = field(default_factory=frozenset)
    system_owned: bool = False

    def __post_init__(self) -> None:
        if not self.hospital_id:
            raise ValueError("TenantContext requires a hospital_id")
        if self.system_owned and self.hospital_id != "__system__":
            raise ValueError("System tenant context must use the system hospital identifier")
        if not self.system_owned and not self.authenticated_user_id:
            raise ValueError("TenantContext requires an authenticated user")

    @classmethod
    def system(cls) -> "TenantContext":
        """Create the explicit context reserved for platform-owned plugins."""
        return cls(hospital_id="__system__", system_owned=True)

    def require_same_hospital(self, hospital_id: str) -> None:
        """Reject a resource that is not owned by this authenticated tenant."""
        if self.system_owned or hospital_id != self.hospital_id:
            raise ValueError("TENANT_MISMATCH")
