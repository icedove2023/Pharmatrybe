from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional

from .plugin import BasePlugin


class DeploymentType(Enum):
    """Deployment mechanism used by a prediction plugin."""

    ARTIFACT = "artifact"
    API = "api"


@dataclass(frozen=True)
class PredictionRequest:
    """Generic clinical prediction request for prediction plugins."""

    payload: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None


@dataclass(frozen=True)
class PredictionResult:
    """Structured result returned by prediction plugins."""

    predicted_class: str
    probabilities: Dict[str, float]
    confidence: float
    model_name: str
    model_version: str
    execution_time_ms: float
    metadata: Optional[Dict[str, Any]] = None
    raw_output: Optional[Dict[str, Any]] = None


class PredictionPlugin(BasePlugin, ABC):
    """Abstract base class for PharmaTrybe prediction plugins.

    PredictionPlugin defines the contract for both artifact-based and API-based
    prediction implementations. The platform interacts with prediction plugins
    through this interface, ensuring that decision fusion remains agnostic to
    the underlying deployment mechanism.
    """

    @property
    @abstractmethod
    def deployment_type(self) -> DeploymentType:
        """Read-only deployment type for this prediction plugin."""
        raise NotImplementedError

    @abstractmethod
    def load(self) -> None:
        """Load or prepare the prediction resource.

        This method is responsible for any initialization of model artifacts,
        external client sessions, or other resources required to perform
        predictions.
        """
        raise NotImplementedError

    @abstractmethod
    def unload(self) -> None:
        """Release prediction resources.

        Implementations should clean up loaded models, close connections, and
        free any resources allocated during load().
        """
        raise NotImplementedError

    @abstractmethod
    def predict(self, request: PredictionRequest) -> PredictionResult:
        """Perform a prediction for the given request."""
        raise NotImplementedError

    @abstractmethod
    def supports(self, request: PredictionRequest) -> bool:
        """Return whether this plugin can process the given request."""
        raise NotImplementedError

    @abstractmethod
    def input_schema(self) -> Dict[str, Any]:
        """Return the expected clinical input schema for prediction requests."""
        raise NotImplementedError

    @abstractmethod
    def output_schema(self) -> Dict[str, Any]:
        """Return the prediction output schema."""
        raise NotImplementedError
