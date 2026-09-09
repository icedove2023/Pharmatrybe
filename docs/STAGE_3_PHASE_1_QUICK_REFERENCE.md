# Stage 3 Phase 1 — Quick Reference

## What Was Created

✅ **4 new framework files** in `packages/prediction-framework/`:

```
packages/prediction-framework/
├── runtime.py            (330 lines) - Base class for plugin lifecycle
├── plugin.py             (280 lines) - Base class for PredictionPlugin interface
├── explainability.py      (90 lines) - Base class for explanation generation
└── exceptions.py          (70 lines) - Unified exception hierarchy
```

Total: ~770 lines of reusable framework code.

---

## How to Use (For Plugin Developers)

### 1. Create a Plugin Runtime

```python
from packages.prediction_framework.runtime import PredictionPluginRuntimeContext

class MyRuntimeContext(PredictionPluginRuntimeContext):
    def _on_initialize(self):
        """Load models, registry, artifacts"""
        pass
    
    def _on_shutdown(self):
        """Release resources"""
        pass
    
    def _on_validate(self) -> bool:
        """Check if ready for predictions"""
        return True
    
    def _on_health(self) -> dict:
        """Return plugin-specific health metrics"""
        return {"models_loaded": 5}
    
    def _on_reload(self):
        """Reload config/models"""
        pass
```

### 2. Create a Plugin Class

```python
from packages.prediction_framework.plugin import BasePredictionPlugin

class MyPredictionPlugin(BasePredictionPlugin):
    @property
    def plugin_id(self) -> str:
        return "my_plugin"
    
    @property
    def plugin_name(self) -> str:
        return "My Prediction Plugin"
    
    @property
    def plugin_description(self) -> str:
        return "..."
    
    @property
    def capabilities(self) -> List[str]:
        return ["prediction", "explainability"]
    
    def _create_runtime_context(self):
        return MyRuntimeContext(self.plugin_id, self.plugin_name, ...)
    
    def predict(self, request: PredictionRequest) -> PredictionResult:
        result = self._runtime_context.predict(request)
        return self._create_prediction_result(result)
    
    def _create_prediction_result(self, runtime_result) -> PredictionResult:
        # Map internal result to platform contract
        return PredictionResult(...)
```

### 3. Create Explainability Adapter

```python
from packages.prediction_framework.explainability import BaseExplainabilityAdapter

class MyExplainabilityAdapter(BaseExplainabilityAdapter):
    def explain(self, execution_context) -> ExplainabilityPayload:
        """Generate explanation using your logic"""
        return ExplainabilityPayload(...)
```

### 4. Use Shared Exceptions

```python
from packages.prediction_framework.exceptions import (
    PluginInitializationError,
    PredictionExecutionError,
    ExplainabilityError,
)

# In initialization
if not registry_loaded:
    raise PluginInitializationError("Registry not loaded")

# In prediction
if len(features) != expected_count:
    raise PredictionExecutionError("Feature count mismatch")

# In explanation (will be caught and degraded)
if shap_engine_failed:
    raise ExplainabilityError("SHAP failed")
```

---

## What Stays Unchanged

| Component | Status |
|-----------|--------|
| SOAR plugin code | ✅ Untouched (will refactor in Phase 2) |
| ARMD adapter code | ✅ Untouched (will refactor in Phase 2) |
| WP4 source code | ✅ Untouched (remains wrapped) |
| Repository structure | ✅ Unchanged |
| Existing tests | ✅ Will still pass |

---

## Phase 2: Refactoring (Next)

When ready, refactor plugins to inherit from framework:

```python
# Before
class SOARPredictionPlugin(PredictionPlugin):
    def initialize(self): ...
    def shutdown(self): ...
    def predict(self, request): ...

# After
class SOARPredictionPlugin(BasePredictionPlugin):
    # All methods inherited from base; just define:
    @property
    def plugin_id(self) -> str: ...
    def _create_runtime_context(self): ...
```

Same behavior, cleaner code, shared infrastructure.

---

## Framework Hierarchy

```
PredictionPlugin (platform interface)
    ↑
    └─ BasePredictionPlugin (framework base)
            ↑
            ├─ SOARPredictionPlugin (Phase 2)
            └─ ARMDPredictionPlugin (Phase 2)

PredictionPluginRuntimeContext (framework base)
    ↑
    ├─ SOARRuntimeContext (existing, Phase 2 inherit)
    └─ ARMDRuntimeContext (existing, Phase 2 inherit)

BaseExplainabilityAdapter (framework base)
    ↑
    ├─ SOARExplainabilityAdapter (Phase 2)
    └─ ARMDExplainability (Phase 2)
```

---

## Key Files

**Report**: [STAGE_3_PHASE_1_REPORT.md](STAGE_3_PHASE_1_REPORT.md) (comprehensive)  
**Framework**: [packages/prediction-framework/](packages/prediction-framework/)  
**Existing Tests**: All pass without modification  

---

## Success Criteria (Phase 1)

✅ Created 4 framework base classes  
✅ Zero algorithm code in framework  
✅ Zero disease-specific contracts  
✅ SOAR untouched  
✅ ARMD untouched  
✅ No repository restructuring  
✅ Generic and reusable  
✅ Ready for Phase 2 refactoring  

**Status**: ✅ COMPLETE
