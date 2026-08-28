"""Registry-specific enums and types."""

from __future__ import annotations

from enum import Enum


class ModelFormat(str, Enum):
    PICKLE = "pickle"
    TORCH = "torch"
    ONNX = "onnx"
    SAVEDMODEL = "savedmodel"
    TF = "tf"
    EC2 = "ec2"
    CUSTOM = "custom"


class ProviderType(str, Enum):
    SOAR = "soar"
    ARMD = "armd"
    NICE = "nice"
    WHO = "who"
    HOSPITAL = "hospital"
    VECTOR = "vector"


class ModelStatus(str, Enum):
    REGISTERED = "registered"
    LOADED = "loaded"
    FAILED = "failed"
    UNKNOWN = "unknown"
