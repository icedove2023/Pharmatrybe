"""
WP5 Engine Layer

Provides lightweight wrappers around the validated
WP4 Decision Engine.

No clinical reasoning should be implemented here.

Responsibilities
----------------
• Load patient records
• Preprocess patient features
• Execute inference
• Return structured prediction results
"""

from .preprocessor import Preprocessor
from .inference import InferenceEngine

__all__ = [
    "Preprocessor",
    "InferenceEngine",
]

from .preprocessor import Preprocessor
from .inference import InferenceEngine

__all__ = [
    "Preprocessor",
    "InferenceEngine",
]