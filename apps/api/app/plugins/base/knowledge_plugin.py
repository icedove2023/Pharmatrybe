from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from .plugin import BasePlugin


class KnowledgePlugin(BasePlugin, ABC):
    """Abstract base class for PharmaTrybe knowledge plugins.

    KnowledgePlugin defines the contract for structured clinical knowledge
    sources. The platform interacts with knowledge plugins through this interface
    without requiring knowledge of the underlying storage or API technology.
    """

    @abstractmethod
    def connect(self) -> None:
        """Connect to the knowledge source.

        Implementations may establish database connections, open API sessions,
        or prepare any resources required to query the knowledge source.
        """
        raise NotImplementedError

    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from the knowledge source.

        Implementations should close database connections, API sessions, and
        clean up any resources acquired in connect().
        """
        raise NotImplementedError

    @abstractmethod
    def search(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search the knowledge source with a text query.

        Parameters:
            query: The search text.
            filters: Optional filtering criteria.

        Returns:
            A list of structured knowledge results.
        """
        raise NotImplementedError

    @abstractmethod
    def query(self, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Query the knowledge source with structured criteria."""
        raise NotImplementedError

    @abstractmethod
    def validate(self) -> bool:
        """Validate the knowledge source and connection state."""
        raise NotImplementedError

    @abstractmethod
    def supported_domains(self) -> List[str]:
        """Return the clinical domains supported by this knowledge plugin."""
        raise NotImplementedError

    @abstractmethod
    def knowledge_version(self) -> str:
        """Return the version of the underlying knowledge data."""
        raise NotImplementedError
