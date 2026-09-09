# Stage 3 — Shared Prediction Framework Extraction Plan

**Date**: 2026-08-13  
**Objective**: Extract demonstrably shared infrastructure from SOAR and ARMD plugins into the prediction framework  
**Outcome**: Plugin-agnostic, reusable framework supporting unlimited prediction plugins

---

## Phase 1: Analysis — Identify Shared Infrastructure

### Comparing SOAR and ARMD Architectures

#### SOAR Plugin Structure
```
soar_prediction_plugin.py (entrypoint)
├─ deployment_registry.py (scans artifact directories)
├─ model_loader.py (loads artifacts: models, encoders, preprocessors)
├─ runtime_context.py (lifecycle: RuntimeHealth, RuntimeMetadata)
├─ prediction_engine.py (executes predictions)
├─ explainability_adapter.py (generates explanations)
└─ artifact_registry.py (metadata about artifacts)
```

#### ARMD Plugin Structure
```
armd_prediction_plugin.py (entrypoint)
├─ runtime_context.py (lifecycle: ARMDRuntimeContext, RuntimeHealth)
├─ prediction_engine.py (executes predictions)
├─ preprocessing.py (feature preprocessing)
├─ explainability.py (generates explanations)
└─ adapters/
    └─ armd_adapter.py (wraps WP4 functions)
```

### Shared Infrastructure Identified

#### ✅ Level 1: Core Contracts (Already in Framework)
- `PredictionRequest` → unified input format
- `PredictionExecution` → intermediate execution output
- `ExplainabilityPayload` → unified explanation format
- `ModelPackage` → unified model representation
- `PredictionStatus` → execution status enum

**Status**: ✅ Already in `contracts.py`

#### ✅ Level 2: Plugin Lifecycle (Similar Patterns)

**SOAR**: `SOARRuntimeContext`
```python
def __init__(self, plugin_id, plugin_name, plugin_version, 
             deployment_registry, model_loader, prediction_engine, 
             explainability_adapter, configuration, logger, cache)
def initialize()
def health() → RuntimeHealth
```

**ARMD**: `ARMDRuntimeContext`
```python
def __init__(self, config)
def initialize()
def validate() → bool
def health() → RuntimeHealth
```

**Shared Pattern**:
- Dependency injection for core components
- Runtime health tracking
- Error accumulation
- Initialization sequence
- Uptime tracking

**Action**: Extract to `PredictionPluginRuntimeContext` (base class)

#### ✅ Level 3: Plugin Entrypoint (Identical Pattern)

**SOAR**: `SOARPredictionPlugin`
```python
def initialize() → creates runtime_context
def shutdown() → cleanup
def validate() → check readiness
def health() → PluginHealth
def predict(request) → PredictionResult
def reload() → refresh registry
def metadata() → PluginMetadata
```

**ARMD**: `ARMDPredictionPlugin`
```python
def initialize() → creates runtime_context
def shutdown() → cleanup
def validate() → check readiness
def health() → PluginHealth
def predict(request) → PredictionResult
def reload() → refresh registry
def metadata() → PluginMetadata
```

**Shared Pattern**:
- Identical interface
- Same lifecycle methods
- Same method signatures
- Delegates to runtime_context and engine

**Action**: Extract to `PredictionPluginBase` (abstract base class)

#### ✅ Level 4: Prediction Engine (Orchestration Only)

**SOAR**: `PredictionEngine`
- Orchestrates prediction flow
- No SOAR-specific algorithm

**ARMD**: `ARMDPredictionEngine`
- Orchestrates prediction flow
- No ARMD-specific algorithm (except data mapping)

**Shared Pattern**:
- Request validation
- Error handling
- Result formatting
- No clinical logic

**Action**: Extract to `BasePredictionEngine` or plugin-specific inheritance

#### ✅ Level 5: Explainability Adapter (Wrapper Pattern)

**SOAR**: `ExplainabilityAdapter`
```python
def explain() → generates explanations
```

**ARMD**: `ARMDExplainability`
```python
def explain() → delegates to adapter
```

**Shared Pattern**:
- Wraps underlying implementation
- Returns `ExplainabilityPayload`
- Graceful error handling

**Action**: Extract to `BaseExplainabilityAdapter` interface

#### ❌ Level 6: Deployment/Model Loading (Plugin-Specific)

**SOAR-specific**:
- `DeploymentRegistry` (scans artifact directories)
- `ModelLoader` (loads artifacts by category)
- `ArtifactRegistry` (tracks artifact metadata)

**ARMD-specific**:
- `ARMDAdapter` (wraps WP4 functions)

**Rationale**: These are plugin-specific strategies. No extraction.

---

## Extraction Phases

### Phase 1a: Base Plugin Runtime Context
**Scope**: Generic plugin lifecycle management

**Extract**:
- `RuntimeHealth` dataclass (generic)
- `PredictionPluginRuntimeContext` base class
  - `initialize()` template
  - `shutdown()` template
  - `health()` template
  - Error tracking
  - Uptime calculation

**Files**:
- Create: `packages/prediction-framework/runtime.py`

**Plugins Update**:
- `SOARRuntimeContext` inherits from `PredictionPluginRuntimeContext`
- `ARMDRuntimeContext` inherits from `PredictionPluginRuntimeContext`

---

### Phase 1b: Base Plugin Class
**Scope**: Generic plugin interface implementation

**Extract**:
- `BasePredictionPlugin` abstract class
  - `initialize()` implementation using runtime_context
  - `shutdown()` implementation
  - `validate()` implementation
  - `health()` implementation
  - `reload()` implementation
  - `metadata()` implementation
  - Properties: plugin_id, plugin_name, etc.

**Files**:
- Create: `packages/prediction-framework/plugin.py`

**Plugins Update**:
- `SOARPredictionPlugin` inherits from `BasePredictionPlugin`
- `ARMDPredictionPlugin` inherits from `BasePredictionPlugin`

---

### Phase 1c: Explainability Base Interface
**Scope**: Generic explainability adapter pattern

**Extract**:
- `BaseExplainabilityAdapter` abstract class
  - `explain()` method signature
  - Graceful error handling pattern
  - Return `ExplainabilityPayload` contract

**Files**:
- Create: `packages/prediction-framework/explainability.py`

**Plugins Update**:
- `SOARExplainabilityAdapter` inherits from `BaseExplainabilityAdapter`
- `ARMDExplainability` inherits from `BaseExplainabilityAdapter`

---

### Phase 1d: Exceptions & Utilities
**Scope**: Shared error handling and logging

**Extract**:
- `PredictionPluginError` (base exception)
  - `RuntimeInitializationError`
  - `PredictionExecutionError`
  - `ExplainabilityError`
  - `ValidationError`

**Files**:
- Create: `packages/prediction-framework/exceptions.py`
- Create: `packages/prediction-framework/logging.py` (optional)

**Plugins Update**:
- SOAR/ARMD import from framework exceptions

---

## Extraction Workflow

For each phase:

1. **Create** framework file with base class/interface
2. **Identify** all methods used by both plugins
3. **Extract** common logic to base class
4. **Update SOAR** to inherit from base
5. **Update ARMD** to inherit from base
6. **Test** that plugin behaviour is unchanged
7. **Report** files modified, rationale, verification

---

## Success Criteria

✅ **No prediction behaviour changes**
- SOAR predictions identical to before
- ARMD predictions identical to before
- All test outputs unchanged

✅ **Shared infrastructure in framework**
- `RuntimeHealth` and lifecycle in framework
- `BasePredictionPlugin` in framework
- Exceptions in framework
- Explainability base interface in framework

✅ **Plugins simplified**
- SOAR plugin 10-20% shorter
- ARMD plugin 10-20% shorter
- Reduced code duplication

✅ **Documentation**
- Framework interfaces documented
- Inheritance patterns clear
- Examples for new plugins

---

## Next Steps

1. Review this plan
2. Execute Phase 1a (Runtime Context)
3. Stop for review
4. Continue Phase 1b-1d
5. Final review before integration testing

