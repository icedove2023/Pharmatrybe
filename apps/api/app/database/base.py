"""Shared SQLAlchemy base model definitions for PharmaTrybe persistence scaffolding."""

from __future__ import annotations

from sqlalchemy import Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.database.mixins import TimestampMixin, UUIDMixin


class Base(DeclarativeBase):
    """Declarative base for future PharmaTrybe ORM models."""


class AuditBaseModel(Base, UUIDMixin, TimestampMixin):
    """Abstract base model with common lifecycle columns and reusable mixins."""

    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
