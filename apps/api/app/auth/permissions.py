"""Reusable permission helpers for the PharmaTrybe authentication scaffold."""

from __future__ import annotations

from enum import Enum
from typing import Any, Callable, TypeVar
from functools import wraps

F = TypeVar("F", bound=Callable[..., Any])


class Permission(str, Enum):
    """Placeholder permission constants for future route protection."""

    READ_API = "read_api"
    MANAGE_USERS = "manage_users"
    REVIEW_STEWARDSHIP = "review_stewardship"


def require_permission(permission: Permission):
    """Attach a required permission marker to a callable."""

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any):
            return func(*args, **kwargs)

        setattr(wrapper, "_required_permission", permission.value)
        return wrapper  # type: ignore[return-value]

    return decorator


def get_required_permission(func: Callable[..., Any]) -> str | None:
    """Return the permission marker attached to a callable, if present."""
    return getattr(func, "_required_permission", None)
