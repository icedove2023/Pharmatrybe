"""SQLAlchemy engine and connection configuration for PharmaTrybe backend."""

from __future__ import annotations

from sqlalchemy import Engine, create_engine
from sqlalchemy.pool import QueuePool

from app.core.config import settings


def get_engine() -> Engine:
    """Create a SQLAlchemy engine using the central settings object."""
    if not settings.database_url:
        raise RuntimeError(
            "DATABASE_URL is required. Configure it with the linked Supabase database URL; "
            "the API must not fall back to an empty in-memory database."
        )
    database_url = settings.database_url
    return create_engine(
        database_url,
        pool_pre_ping=True,
        poolclass=QueuePool,
        pool_size=5,
        max_overflow=10,
        echo=settings.debug,
    )


engine = get_engine()
