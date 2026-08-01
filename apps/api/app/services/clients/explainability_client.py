"""Placeholder service client for the Explainability Engine."""

from app.services.base.base_service import BaseService


class ExplainabilityClient(BaseService):
    """Architecture placeholder for Explainability Engine communication."""

    def __init__(self) -> None:
        super().__init__(name="Explainability", version="0.1.0", endpoint="")

    def explain(self) -> None:
        """Placeholder method for future explanation integration."""
        raise NotImplementedError("Explainability integration is not implemented in this phase")

    def health(self) -> None:
        """Placeholder method for future health checks."""
        raise NotImplementedError("Explainability health check is not implemented in this phase")
