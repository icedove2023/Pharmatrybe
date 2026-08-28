"""
Database integration package for the PharmaTrybe backend.

This package exposes only the database infrastructure.
Repository modules are intentionally NOT imported here to avoid
circular import dependencies.
"""

from app.database.base import AuditBaseModel, Base
from app.database.connection import engine
from app.database.health import check_database_health
from app.database.mixins import (
    AuditMixin,
    SoftDeleteMixin,
    TimestampMixin,
    UUIDMixin,
)
from app.database.session import SessionLocal, get_db_session

__all__ = [
    "AuditBaseModel",
    "AuditMixin",
    "Base",
    "SessionLocal",
    "SoftDeleteMixin",
    "TimestampMixin",
    "UUIDMixin",
    "engine",
    "get_db_session",
    "check_database_health",
]