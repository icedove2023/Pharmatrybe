"""Base class for explainability adapters.

Provides a generic interface that prediction plugins can use to generate
explanations. Implementations convert plugin-specific explanation formats
into the unified ExplainabilityPayload contract.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import logging

from .contracts import ExplainabilityPayload

logger = logging.getLogger(__name__)


class BaseExplainabilityAdapter(ABC):
    """Base class for explainability adapters.
    
    Provides a generic interface for generating predictions explanations.
    Subclasses implement plugin-specific explanation generation and map
    results to the unified ExplainabilityPayload contract.
    
    Key responsibilities:
    - Accept plugin-specific execution context
    - Generate explanation (using SHAP, decision trees, etc.)
    - Map to ExplainabilityPayload contract
    - Handle errors gracefully (return minimal payload if explanation fails)
    
    Subclass contract:
    - Override explain() to implement explanation generation
    - Return ExplainabilityPayload or minimal payload on error
    - Use graceful degradation (don't fail prediction if explanation fails)
    
    Example subclass:
        class MyExplainabilityAdapter(BaseExplainabilityAdapter):
            def explain(self, execution_context: Any) -> ExplainabilityPayload:
                # Generate explanation
                drivers = self._compute_shap_values(...)
                narrative = self._generate_narrative(drivers)
                
                return ExplainabilityPayload(
                    prediction_id=execution_context.id,
                    model_id=execution_context.model_id,
                    positive_drivers=drivers['positive'],
                    negative_drivers=drivers['negative'],
                    narrative=narrative,
                )
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize explainability adapter.
        
        Args:
            config: Configuration dictionary (optional)
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)

    @abstractmethod
    def explain(self, execution_context: Any) -> ExplainabilityPayload:
        """Generate explanation for a prediction execution.
        
        Subclasses should override this to implement their specific
        explanation generation logic.
        
        Args:
            execution_context: Plugin-specific execution context
                (e.g., PredictionExecution, ARMDExecution, etc.)
            
        Returns:
            ExplainabilityPayload with explanation data
            
        Raises:
            ExplainabilityError or similar: If explanation cannot be generated
        """
        pass

    def _create_minimal_payload(
        self,
        prediction_id: str,
        model_id: str,
        error_message: str,
    ) -> ExplainabilityPayload:
        """Create minimal explainability payload on error.
        
        Used for graceful degradation when explanation generation fails.
        Returns a minimal payload that allows the prediction to succeed
        even if explanation fails.
        
        Args:
            prediction_id: Identifier for the prediction
            model_id: Identifier for the model used
            error_message: Error message to include in narrative
            
        Returns:
            Minimal ExplainabilityPayload
        """
        return ExplainabilityPayload(
            prediction_id=prediction_id,
            model_id=model_id,
            narrative=f"Explanation unavailable: {error_message}",
            confidence_indicators={
                "explanation_available": False,
                "error": error_message,
            },
        )

    def _safe_explain(
        self,
        execution_context: Any,
        fallback_prediction_id: Optional[str] = None,
        fallback_model_id: Optional[str] = None,
    ) -> ExplainabilityPayload:
        """Safely generate explanation with graceful degradation.
        
        Wraps explain() method to catch errors and return minimal payload
        instead of failing. Useful for plugins that want to allow predictions
        to succeed even if explanation generation fails.
        
        Args:
            execution_context: Plugin-specific execution context
            fallback_prediction_id: ID to use if explain() fails
            fallback_model_id: Model ID to use if explain() fails
            
        Returns:
            ExplainabilityPayload (full or minimal)
        """
        try:
            return self.explain(execution_context)
        except Exception as e:
            self.logger.error(
                "Explanation generation failed, using minimal payload",
                exc_info=True,
            )
            
            pred_id = fallback_prediction_id or "unknown"
            model_id = fallback_model_id or "unknown"
            error_msg = str(e)
            
            return self._create_minimal_payload(
                prediction_id=pred_id,
                model_id=model_id,
                error_message=error_msg,
            )
