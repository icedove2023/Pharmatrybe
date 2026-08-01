"""Placeholder service client for the ARMD component."""

from app.services.base.base_service import BaseService


class ARMDClient(BaseService):
    """Architecture placeholder for ARMD service communication."""

    def __init__(self) -> None:
        super().__init__(name="ARMD", version="0.1.0", endpoint="")

    def predict(self) -> None:
        """Placeholder method for future prediction integration."""
        raise NotImplementedError("ARMD prediction is not implemented in this phase")

    def health(self) -> None:
        """Placeholder method for future health checks."""
        raise NotImplementedError("ARMD health check is not implemented in this phase")
