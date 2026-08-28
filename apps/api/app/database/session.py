"""Session management helpers for the PharmaTrybe database scaffold."""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy.orm import Session, sessionmaker

from app.database.connection import engine

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db_session() -> Generator[Session, None, None]:
    """Yield a database session for FastAPI dependency injection."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
