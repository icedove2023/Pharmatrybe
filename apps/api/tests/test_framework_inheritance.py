from __future__ import annotations

from app.plugins.base.prediction_plugin import PredictionPlugin
from app.plugins.prediction.armd.armd_prediction_plugin import ARMDPredictionPlugin
from app.plugins.prediction.armd.explainability import ARMDExplainability
from app.plugins.prediction.armd.runtime_context import ARMDRuntimeContext
from app.plugins.prediction.soar.explainability_adapter import ExplainabilityAdapter
from app.plugins.prediction.soar.runtime_context import SOARRuntimeContext
from app.plugins.prediction.soar.soar_prediction_plugin import SOARPredictionPlugin
from packages.prediction_framework.explainability import BaseExplainabilityAdapter
from packages.prediction_framework.plugin import BasePredictionPlugin
from packages.prediction_framework.runtime import PredictionPluginRuntimeContext


def test_prediction_framework_inheritance_contracts() -> None:
    assert issubclass(SOARRuntimeContext, PredictionPluginRuntimeContext)
    assert issubclass(ARMDRuntimeContext, PredictionPluginRuntimeContext)
    assert issubclass(SOARPredictionPlugin, BasePredictionPlugin)
    assert issubclass(ARMDPredictionPlugin, BasePredictionPlugin)
    assert issubclass(ExplainabilityAdapter, BaseExplainabilityAdapter)
    assert issubclass(ARMDExplainability, BaseExplainabilityAdapter)
    assert issubclass(SOARPredictionPlugin, PredictionPlugin)
    assert issubclass(ARMDPredictionPlugin, PredictionPlugin)
