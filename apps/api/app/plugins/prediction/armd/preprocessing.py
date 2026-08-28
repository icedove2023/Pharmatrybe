"""ARMD Preprocessing Adapter.

Wraps WP4 preprocessing to provide exact WP3 parity using artifacts.
"""

from __future__ import annotations

import logging
from typing import Dict, Any, Optional

import pandas as pd
from packages.prediction_framework.adapters import ARMDAdapter, ARMDAdapterError

logger = logging.getLogger(__name__)


class ARMDPreprocessing:
    """Preprocesses patient data using WP4/WP3 artifacts.
    
    Ensures exact feature alignment and missing value imputation
    for model inference.
    """

    def __init__(self, adapter: Optional[ARMDAdapter] = None, config: Optional[Dict[str, Any]] = None):
        """Initialize preprocessing.
        
        Args:
            adapter: ARMDAdapter instance (should be initialized)
            config: Configuration dictionary (unused but kept for compatibility)
        """
        self.adapter = adapter
        self.config = config or {}

    def transform(self, patient_data: Dict[str, Any]) -> pd.DataFrame:
        """Transform raw patient data into model-ready features.
        
        Args:
            patient_data: Dictionary of patient features
            
        Returns:
            Preprocessed DataFrame with aligned columns
            
        Raises:
            RuntimeError: If adapter not initialized or preprocessing fails
        """
        if self.adapter is None:
            raise RuntimeError("Adapter not initialized")
        
        try:
            return self.adapter.preprocess_patient_features(patient_data)
        except ARMDAdapterError as e:
            logger.error(f"Preprocessing failed: {e}", exc_info=True)
            raise RuntimeError(f"Preprocessing failed: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error in preprocessing: {e}", exc_info=True)
            raise RuntimeError(f"Preprocessing error: {e}") from e
