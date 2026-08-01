"""Placeholder service client for the WHO Knowledge component."""

from app.services.base.base_service import BaseService


class WHOClient(BaseService):
    """Architecture placeholder for WHO Knowledge service communication."""

    def __init__(self) -> None:
        super().__init__(name="WHO", version="0.1.0", endpoint="")

    def lookup(self) -> None:
        """Placeholder method for future WHO knowledge lookup integration."""
        raise NotImplementedError("WHO knowledge lookup is not implemented in this phase")

    def health(self) -> None:
        """Placeholder method for future health checks."""
        raise NotImplementedError("WHO health check is not implemented in this phase")
