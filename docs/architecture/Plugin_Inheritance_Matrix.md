# Plugin Inheritance Matrix

## Class Inheritance Summary

| Component | Parent base | Status | Notes |
|---|---|---:|---|
| SOARRuntimeContext | PredictionPluginRuntimeContext | PASS | Inherits shared runtime lifecycle and error tracking |
| ARMDRuntimeContext | PredictionPluginRuntimeContext | PASS | Inherits shared runtime lifecycle and error tracking |
| SOARPredictionPlugin | BasePredictionPlugin | PASS | Retains SOAR-specific initialization and runtime wiring |
| ARMDPredictionPlugin | BasePredictionPlugin | PASS | Retains ARMD-specific initialization and runtime wiring |
| ExplainabilityAdapter | BaseExplainabilityAdapter | PASS | Keeps SOAR SHAP explanation behavior intact |
| ARMDExplainability | BaseExplainabilityAdapter | PASS | Keeps ARMD explanation mapping intact |

## Interface Compatibility Matrix

| Plugin | Platform interface | Base framework class | Static compatibility |
|---|---|---|---:|
| SOAR | PredictionPlugin | BasePredictionPlugin | PASS |
| ARMD | PredictionPlugin | BasePredictionPlugin | PASS |
| SOAR runtime | Runtime lifecycle contract | PredictionPluginRuntimeContext | PASS |
| ARMD runtime | Runtime lifecycle contract | PredictionPluginRuntimeContext | PASS |
| SOAR explainability | explain() adapter contract | BaseExplainabilityAdapter | PASS |
| ARMD explainability | explain() adapter contract | BaseExplainabilityAdapter | PASS |

## Inheritance Principles Maintained

- No architecture redesign was introduced.
- Plugin-specific logic remains in the plugin module.
- Shared lifecycle code remains centralized in the framework package.
- Clinical inference logic remains outside the framework base classes.
