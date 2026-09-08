"""Explicit read-only WHO knowledge database session factory."""

from __future__ import annotations

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings


def get_who_engine() -> Engine:
    """Create the WHO engine from the dedicated WHO database setting."""
    if not settings.who_database_url:
        raise RuntimeError("WHO_DATABASE_URL is required for WHO knowledge access")
    return create_engine(
        settings.who_database_url,
        pool_pre_ping=True,
        pool_size=2,
        max_overflow=4,
        echo=settings.debug,
    )


WHO_ENGINE = get_who_engine()
WHO_SESSION_LOCAL = sessionmaker(autocommit=False, autoflush=False, bind=WHO_ENGINE)


def get_who_session() -> Session:
    """Return a session bound only to the configured WHO database."""
    return WHO_SESSION_LOCAL()
