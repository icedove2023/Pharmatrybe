"""Repository helpers for the PharmaTrybe clinical case resource.

This repository layer stays strictly within the existing database abstraction and
provides standard CRUD operations for a future SQLAlchemy-backed clinical case
entity without introducing business rules or endpoint logic.
"""

from __future__ import annotations

from typing import Any, TypeVar

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select

from app.database.repositories.base_repository import BaseRepository

ModelT = TypeVar("ModelT")


class RepositoryError(RuntimeError):
    """Raised when a repository operation cannot be completed safely."""


class ClinicalCaseRepository(BaseRepository[ModelT]):
    """Repository wrapper for CRUD operations on clinical case entities."""

    def __init__(self, session: Session, entity_type: type[ModelT] | None = None) -> None:
        """Initialize the repository with a session and an optional entity type."""
        super().__init__(session)
        self.entity_type = entity_type

    def create(self, entity: ModelT) -> ModelT:
        """Persist a new clinical case entity and return the saved instance."""
        try:
            self.session.add(entity)
            self.session.commit()
            self.session.refresh(entity)
            return entity
        except SQLAlchemyError as exc:
            self.session.rollback()
            raise RepositoryError(f"Unable to create clinical case entity: {exc}") from exc

    def get_by_id(self, entity_id: int) -> ModelT | None:
        """Return a clinical case entity by identifier, if present."""
        if self.entity_type is None:
            raise RepositoryError("No entity type has been configured for the repository")

        try:
            return self.session.get(self.entity_type, entity_id)
        except SQLAlchemyError as exc:
            raise RepositoryError(f"Unable to fetch clinical case entity {entity_id}: {exc}") from exc

    def list(self, *, skip: int = 0, limit: int | None = None) -> list[ModelT]:
        """Return a paged list of clinical case entities."""
        if self.entity_type is None:
            raise RepositoryError("No entity type has been configured for the repository")

        try:
            statement = select(self.entity_type)
            if skip:
                statement = statement.offset(skip)
            if limit is not None:
                statement = statement.limit(limit)
            return list(self.session.scalars(statement).all())
        except SQLAlchemyError as exc:
            raise RepositoryError(f"Unable to list clinical case entities: {exc}") from exc

    def get_all(self) -> list[ModelT]:
        """Return all clinical case entities."""
        return self.list()

    def update(self, entity_id: int, **kwargs: Any) -> ModelT | None:
        """Update a clinical case entity using keyword arguments."""
        if self.entity_type is None:
            raise RepositoryError("No entity type has been configured for the repository")

        entity = self.get_by_id(entity_id)
        if entity is None:
            return None

        try:
            for key, value in kwargs.items():
                setattr(entity, key, value)
            self.session.add(entity)
            self.session.commit()
            self.session.refresh(entity)
            return entity
        except SQLAlchemyError as exc:
            self.session.rollback()
            raise RepositoryError(f"Unable to update clinical case entity {entity_id}: {exc}") from exc

    def delete(self, entity_id: int) -> None:
        """Delete a clinical case entity by identifier."""
        entity = self.get_by_id(entity_id)
        if entity is None:
            return

        try:
            self.session.delete(entity)
            self.session.commit()
        except SQLAlchemyError as exc:
            self.session.rollback()
            raise RepositoryError(f"Unable to delete clinical case entity {entity_id}: {exc}") from exc
