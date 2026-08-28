"""Shared exception classes for prediction plugins.

Provides a hierarchy of exceptions that plugins can use to signal different
types of errors. Enables consistent error handling across all prediction plugins.
"""


class PredictionPluginError(Exception):
    """Base exception for all prediction plugin errors."""
    pass


class PluginInitializationError(PredictionPluginError):
    """Raised when plugin initialization fails.
    
    Indicates that one of the following failed:
    - Plugin configuration validation
    - Registry/deployment scanner initialization
    - Model loading
    - Dependency injection setup
    """
    pass


class PluginValidationError(PredictionPluginError):
    """Raised when plugin validation fails.
    
    Indicates that the plugin is not ready to accept predictions:
    - Registry is empty
    - Models are not loaded
    - Dependencies are unavailable
    """
    pass


class PredictionExecutionError(PredictionPluginError):
    """Raised when prediction execution fails.
    
    Indicates that a single prediction request cannot be completed:
    - Request validation failed (missing required fields)
    - Model inference failed
    - Feature preprocessing failed
    - Probability extraction failed
    """
    pass


class ExplainabilityError(PredictionPluginError):
    """Raised when explainability generation fails.
    
    Indicates that explanation cannot be generated:
    - SHAP library unavailable
    - Feature contribution computation failed
    - Narrative generation failed
    - Visualization generation failed
    
    Note: Explainability errors should trigger graceful degradation
    (return minimal payload) rather than failing the entire prediction.
    """
    pass


class PreprocessingError(PredictionPluginError):
    """Raised when feature preprocessing fails.
    
    Indicates that patient data cannot be converted to model-ready features:
    - Missing required features
    - Feature type mismatch
    - Scaling/encoding failed
    - Missing value imputation failed
    """
    pass


class ArtifactLoadError(PredictionPluginError):
    """Raised when model or preprocessing artifacts cannot be loaded.
    
    Indicates that a required artifact (model, encoder, scaler, etc.) cannot
    be found or loaded from storage.
    """
    pass


class RegistryError(PredictionPluginError):
    """Raised when deployment/model registry operations fail.
    
    Indicates that the registry (list of available deployments/models)
    cannot be initialized or accessed.
    """
    pass
