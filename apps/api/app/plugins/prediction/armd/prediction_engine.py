"""ARMD Prediction Engine.

Orchestrates ARMD predictions using the ARMDAdapter,
mapping platform plugin requests to adapter calls.
"""

from __future__ import annotations

import logging
from typing import Optional, Dict, Any

from app.plugins.base.prediction_plugin import PredictionRequest, PredictionResult
from packages.prediction_framework.contracts import (
    PredictionStatus,
    PredictionResult as FrameworkPredictionResult,
)
from packages.prediction_framework.adapters import ARMDAdapterError
from .runtime_context import ARMDRuntimeContext

logger = logging.getLogger(__name__)


class ARMDPredictionEngine:
    """Executes ARMD predictions using loaded models via adapter.
    
    Converts platform PredictionRequest to adapter calls, handles
    errors gracefully, and returns standardized responses.
    """

    def __init__(self, runtime_context: ARMDRuntimeContext):
        """Initialize prediction engine.
        
        Args:
            runtime_context: ARMDRuntimeContext with initialized adapter
        """
        if not isinstance(runtime_context, ARMDRuntimeContext):
            raise TypeError("runtime_context must be ARMDRuntimeContext")
        
        self.runtime_context = runtime_context
        logger.info("ARMD Prediction Engine initialized")

    def predict(self, request: PredictionRequest) -> PredictionResult:
        """Execute prediction for a patient.
        
        Args:
            request: Platform PredictionRequest with patient data
            
        Returns:
            PredictionResult following platform contract
            
        Raises:
            RuntimeError: If adapter not initialized or prediction fails
        """
        logger.info(f"Processing prediction request for patient")
        
        # Validate preconditions
        if not self.runtime_context.validate():
            msg = "Runtime context not properly initialized"
            logger.error(msg)
            raise RuntimeError(msg)
        
        adapter = self.runtime_context.adapter
        if adapter is None:
            msg = "ARMD adapter not available"
            logger.error(msg)
            raise RuntimeError(msg)
        
        try:
            # Extract patient data from request
            # The request.data format depends on platform contract;
            # adapt as needed
            patient_data = request.payload
            
            # Predict for all antibiotics
            predictions = adapter.predict_all_antibiotics(patient_data)
            
            # Convert results to platform format
            # For now, return a simple aggregated result
            # In future, this should map to platform PredictionResult schema
            recommendation_list = []
            for antibiotic, execution in predictions.items():
                if execution.status == PredictionStatus.SUCCESS:
                    recommendation_list.append({
                        'antibiotic': antibiotic,
                        'probability': execution.confidence,
                        'class': execution.selected_class,
                        'confidence': execution.confidence,
                    })
            
            # Sort by probability (ascending = least resistant first)
            recommendation_list.sort(key=lambda x: x['probability'])
            
            # Map to platform PredictionResult
            # Note: This is a simplified mapping; the full implementation
            # should match the platform contract exactly
            result = PredictionResult(
                predicted_class=(recommendation_list[0].get('class', 'unknown') if recommendation_list else 'unknown'),
                probabilities={
                    item['antibiotic']: float(item['probability'])
                    for item in recommendation_list
                    if item.get('probability') is not None
                },
                confidence=float(recommendation_list[0].get('confidence', 0.0)) if recommendation_list else 0.0,
                model_name='ARMD WP4',
                model_version='0.1.0',
                execution_time_ms=0.0,
                metadata={'predictions': recommendation_list},
            )
            
            logger.info(f"Prediction completed successfully")
            return result
            
        except ARMDAdapterError as e:
            msg = f"Adapter error during prediction: {e}"
            logger.error(msg, exc_info=True)
            raise RuntimeError(msg) from e
        except Exception as e:
            msg = f"Unexpected error during prediction: {e}"
            logger.error(msg, exc_info=True)
            raise RuntimeError(msg) from e

    def predict_single_antibiotic(
        self,
        patient_data: Dict[str, Any],
        antibiotic: str,
    ) -> Dict[str, Any]:
        """Predict for a single antibiotic (convenience method).
        
        Args:
            patient_data: Patient features dictionary
            antibiotic: Antibiotic name (e.g., "ciprofloxacin")
            
        Returns:
            Dictionary with prediction results
        """
        logger.info(f"Predicting for {antibiotic}")
        
        if not self.runtime_context.validate():
            raise RuntimeError("Runtime context not initialized")
        
        adapter = self.runtime_context.adapter
        if adapter is None:
            raise RuntimeError("ARMD adapter not available")
        
        try:
            model_package = adapter.load_model_package(antibiotic)
            execution = adapter.predict(model_package, patient_data)
            
            return {
                'status': execution.status.value,
                'antibiotic': antibiotic,
                'class': execution.selected_class,
                'confidence': execution.confidence,
                'probabilities': execution.probabilities,
                'error': execution.error,
            }
            
        except Exception as e:
            logger.error(f"Single antibiotic prediction failed: {e}", exc_info=True)
            return {
                'status': 'failed',
                'antibiotic': antibiotic,
                'error': str(e),
            }

    def get_registry_info(self) -> Dict[str, Any]:
        """Get information about loaded models/registry.
        
        Returns:
            Dictionary with registry metadata
        """
        adapter = self.runtime_context.adapter
        if adapter is None or adapter.registry is None:
            return {'antibiotics': []}
        
        return {
            'antibiotics': list(adapter.registry.keys()),
            'count': len(adapter.registry),
        }
