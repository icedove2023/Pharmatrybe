"""Reusable SQLAlchemy mixins for PharmaTrybe ORM scaffolding."""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column


class UUIDMixin:
    """Mixin providing a UUID column for future ORM models."""

    __abstract__ = True

    uuid: Mapped[str] = mapped_column(
        String(36),
        default=lambda: str(uuid4()),
        nullable=False,
        unique=True,
        index=True,
    )


class TimestampMixin:
    """Mixin providing lifecycle timestamps for future ORM models."""

    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class AuditMixin:
    """Placeholder mixin for future audit metadata fields."""

    __abstract__ = True


class SoftDeleteMixin:
    """Placeholder mixin for future soft-delete support."""

    __abstract__ = True
