"""Placeholder service client for the SOAR/GSK component."""

from app.services.base.base_service import BaseService


class SOARClient(BaseService):
    """Architecture placeholder for SOAR/GSK service communication."""

    def __init__(self) -> None:
        super().__init__(name="SOAR", version="0.1.0", endpoint="")

    def predict(self) -> None:
        """Placeholder method for future prediction integration."""
        raise NotImplementedError("SOAR prediction is not implemented in this phase")

    def health(self) -> None:
        """Placeholder method for future health checks."""
        raise NotImplementedError("SOAR health check is not implemented in this phase")
