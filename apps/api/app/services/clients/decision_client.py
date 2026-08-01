"""Placeholder service client for the Clinical Decision Engine."""

from app.services.base.base_service import BaseService


class DecisionEngineClient(BaseService):
    """Architecture placeholder for Clinical Decision Engine communication."""

    def __init__(self) -> None:
        super().__init__(name="Decision Engine", version="0.1.0", endpoint="")

    def recommend(self) -> None:
        """Placeholder method for future recommendation integration."""
        raise NotImplementedError("Decision engine recommendation is not implemented in this phase")

    def health(self) -> None:
        """Placeholder method for future health checks."""
        raise NotImplementedError("Decision engine health check is not implemented in this phase")
