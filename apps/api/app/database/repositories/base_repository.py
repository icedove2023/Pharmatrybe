"""Abstract repository base class for future PharmaTrybe database integrations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from sqlalchemy.orm import Session

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """Abstract placeholder repository for future persistence implementations."""

    def __init__(self, session: Session) -> None:
        self.session = session

    @abstractmethod
    def create(self, entity: T) -> T:
        """Create an entity placeholder."""
        raise NotImplementedError("Create is not implemented in the repository scaffold")

    @abstractmethod
    def get_by_id(self, entity_id: int) -> T | None:
        """Fetch an entity by identifier placeholder."""
        raise NotImplementedError("Get by id is not implemented in the repository scaffold")

    @abstractmethod
    def get_all(self) -> list[T]:
        """Fetch all entities placeholder."""
        raise NotImplementedError("Get all is not implemented in the repository scaffold")

    @abstractmethod
    def update(self, entity_id: int, **kwargs: Any) -> T | None:
        """Update an entity placeholder."""
        raise NotImplementedError("Update is not implemented in the repository scaffold")

    @abstractmethod
    def delete(self, entity_id: int) -> None:
        """Delete an entity placeholder."""
        raise NotImplementedError("Delete is not implemented in the repository scaffold")
