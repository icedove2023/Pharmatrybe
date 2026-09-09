# Framework Boundary Report

**Audit Date**: August 13, 2026  
**Scope**: Verify every extracted component belongs in its current location  
**Finding**: ✅ ALL COMPONENTS CORRECTLY LOCATED

---

## Analysis Summary

| Component | Current Location | Correct Location | Status | Recommendation |
|-----------|:----------------:|:----------------:|:------:|-----------------|
| runtime.py | packages/prediction-framework/ | ✅ CORRECT | ✅ PASS | Keep |
| plugin.py | packages/prediction-framework/ | ✅ CORRECT | ✅ PASS | Keep |
| explainability.py | packages/prediction-framework/ | ✅ CORRECT | ✅ PASS | Keep |
| exceptions.py | packages/prediction-framework/ | ✅ CORRECT | ✅ PASS | Keep |
| contracts.py | packages/prediction-framework/ | ✅ CORRECT | ✅ PASS | Keep |
| adapters/armd_adapter.py | packages/prediction-framework/adapters/ | ✅ CORRECT | ✅ PASS | Keep |

---

## Component Boundary Analysis

### 1. runtime.py

**Current Location**: `packages/prediction-framework/runtime.py`  
**Correct Location**: `packages/prediction-framework/` ✅  
**Belongs To**: Framework  
**Reason**: Base class for plugin lifecycle — infrastructure, not domain  
**Alternative Location Considered**: Could be in each plugin, but would duplicate code  
**Decision**: ✅ **FRAMEWORK IS CORRECT**

---

### 2. plugin.py

**Current Location**: `packages/prediction-framework/plugin.py`  
**Correct Location**: `packages/prediction-framework/` ✅  
**Belongs To**: Framework  
**Reason**: Generic PredictionPlugin interface implementation — infrastructure, not domain  
**Alternative Location Considered**: Could be in each plugin, but would duplicate code  
**Decision**: ✅ **FRAMEWORK IS CORRECT**

---

### 3. explainability.py

**Current Location**: `packages/prediction-framework/explainability.py`  
**Correct Location**: `packages/prediction-framework/` ✅  
**Belongs To**: Framework  
**Reason**: Generic explanation base class with error handling — infrastructure pattern  
**Alternative Location Considered**: Could be in each plugin, but duplicates error handling pattern  
**Decision**: ✅ **FRAMEWORK IS CORRECT**

---

### 4. exceptions.py

**Current Location**: `packages/prediction-framework/exceptions.py`  
**Correct Location**: `packages/prediction-framework/` ✅  
**Belongs To**: Framework  
**Reason**: Shared exception hierarchy — error semantics infrastructure  
**Alternative Location Considered**: Could be in each plugin, but would prevent unified error handling  
**Decision**: ✅ **FRAMEWORK IS CORRECT**

---

### 5. contracts.py

**Current Location**: `packages/prediction-framework/contracts.py`  
**Correct Location**: `packages/prediction-framework/` ✅  
**Belongs To**: Framework  
**Reason**: Unified data contracts for all plugins — platform integration infrastructure  
**Alternative Location Considered**: Could be in each plugin, but would duplicate contracts and break plugin interoperability  
**Decision**: ✅ **FRAMEWORK IS CORRECT**

---

### 6. adapters/armd_adapter.py

**Current Location**: `packages/prediction-framework/adapters/armd_adapter.py`  
**Correct Location**: `packages/prediction-framework/adapters/` ✅  
**Belongs To**: Framework (namespace for adapters)  
**Reason**: Adapter pattern (bridging legacy to framework contracts) is infrastructure  
**Alternative Location Considered**: Could be inside `apps/api/app/plugins/prediction/armd/` (plugin-specific)  
**Decision**: ✅ **FRAMEWORK IS CORRECT** — But with caveat

**Caveat Explanation**:
- Content is ARMD-specific (only ARMD uses ARMDAdapter)
- Pattern is generic (adapters will grow: soar_adapter.py, tb_adapter.py, etc.)
- Location rationale: `adapters/` is namespace for all plugin-specific adapters
- Future: adapters/soar_adapter.py, adapters/tb_adapter.py will be added

**Implication**: ARMDAdapter won't be reused by other plugins directly, but adapter pattern/infrastructure will be.

---

### 7. Contracts Qualified Elements

#### ClinicalCategory enum

**Current Location**: `packages/prediction-framework/contracts.py`  
**Correct Location**: ✅ CORRECT (but see note below)  
**Belongs To**: Framework (generic pattern) / Partial ARMD (specific values)  
**Reason**: Pattern (categorization) is generic; values are ARMD-specific  
**Alternative Location**: Could be in ARMD plugin contracts if future plugins need different categories  
**Decision**: ✅ **KEEP IN FRAMEWORK WITH DOCUMENTATION**

**Note**: If future Malaria plugin needs different categories (e.g., ENDEMIC, NON-ENDEMIC instead of AVOID, CAUTION), can be refactored. For now, keep as-is (no plugins broken).

---

#### RiskProfileData dataclass

**Current Location**: `packages/prediction-framework/contracts.py`  
**Correct Location**: ⚠️ PARTIALLY (see analysis below)  
**Belongs To**: Framework (risk profile pattern) / ARMD (specific implementation)  
**Reason**: Pattern (patient risk profile) is generic; implementation is ARMD-specific  
**Alternative Location**: Could be in ARMD plugin if other plugins need different structures  
**Decision**: 🟡 **KEEP IN FRAMEWORK WITH QUALIFICATION**

**Analysis**:
- **Used by**: ARMD only (SOAR doesn't generate risk profiles)
- **Reusable by**: Potentially TB, Malaria (if they need patient risk profiles)
- **Specific to ARMD**: Field "stewardship_alerts" (ARMD-specific concept)
- **Generic Part**: Field "risk_factors", "risk_level" pattern (applicable to all domains)

**Recommendation**: 
- Keep in framework (risk profiling is common pattern)
- Mark as "ARMD-originated, future plugins may extend" in docstring
- If TB plugin needs different structure, can be refactored without breaking ARMD

---

## Framework Organization Assessment

### Current Structure ✅

```
packages/prediction-framework/
├── __init__.py
├── runtime.py           # Plugin lifecycle base
├── plugin.py            # PredictionPlugin interface implementation
├── explainability.py    # Explainability adapter base
├── exceptions.py        # Exception hierarchy
├── contracts.py         # Data contracts
├── adapters/
│   ├── __init__.py
│   └── armd_adapter.py  # ARMD-specific WP4 wrapper
└── tests/
    ├── __init__.py
    └── test_armd_adapter.py
```

### Organizational Principles

| Principle | Implementation | Status |
|-----------|-----------------|--------|
| **Core Framework** (runtime.py, plugin.py, explainability.py, exceptions.py, contracts.py) | In root of prediction-framework/ | ✅ CORRECT |
| **Adapters** (plugin-specific legacy bridges) | In adapters/ subdirectory | ✅ CORRECT |
| **Tests** | Mirrored in tests/ subdirectory | ✅ CORRECT |
| **Future SOARAdapter** (if needed) | Would go in adapters/soar_adapter.py | ✅ READY |
| **Future TBAdapter** (if needed) | Would go in adapters/tb_adapter.py | ✅ READY |
| **Future Plugin-Specific Contracts** | Could stay in root if generic; in plugin if specific | ✅ READY |

---

## Relocation Assessment

### Could Any Framework Component be Better Located?

#### 1. Should adapters/ be inside plugins instead?

**Question**: Should adapters/armd_adapter.py be inside apps/api/app/plugins/prediction/armd/?

**Analysis**:
- Adapter pattern is infrastructure (bridging legacy to framework)
- adapters/ namespace will grow (armd_adapter.py, soar_adapter.py, tb_adapter.py)
- Adapters are framework-level component (all plugins use the adaptation pattern)
- Current location enables consistent adapter infrastructure

**Decision**: ✅ **CURRENT LOCATION IS CORRECT**

If moved to plugin:
- Would fragment adapter pattern across plugins
- Would make it unclear that adapters are shared infrastructure
- Would prevent code review of adapter pattern in one place

---

#### 2. Should contracts.py be split?

**Question**: Should generic contracts (ModelPackage, PredictionRequest) be separated from ARMD-specific contracts (RiskProfileData)?

**Analysis**:
- Core contracts (ModelPackage, PredictionRequest, PredictionExecution, ExplainabilityPayload, PredictionResult) are 100% generic
- Qualified contracts (ClinicalCategory, RiskProfileData) are ARMD-originated but pattern is generic
- Splitting would create contracts.py + armd_contracts.py (or armd/contracts.py)
- Not currently justified (only 2 qualified components; core contracts dominate)

**Decision**: ✅ **KEEP UNIFIED**

Rationale:
- Minimal separation benefit (2 out of 11 components)
- Would require plugins to import from multiple locations
- Can be refactored later if many plugin-specific contracts accumulate

---

#### 3. Should explainability_adapters.py be more generic?

**Question**: Should explainability.py be renamed to explainability_base.py or moved to bases/?

**Analysis**:
- Current name (explainability.py) is clear and concise
- Subdirectory structure (bases/, interfaces/) would add complexity
- Package structure already clear: framework knows it's base/infrastructure

**Decision**: ✅ **CURRENT NAMING IS CORRECT**

---

## Plugin-Side Boundary Review

### Apps/API Plugins: No Migration Needed

| Plugin Component | Current Location | Should Move? | Reason |
|------------------|:----------------:|:----------:|---------|
| **SOAR** | | | |
| soar_prediction_plugin.py | apps/api/app/plugins/prediction/soar/ | ❌ NO | Plugin-specific |
| runtime_context.py | apps/api/app/plugins/prediction/soar/ | ❌ NO | SOAR-specific implementation |
| prediction_engine.py | apps/api/app/plugins/prediction/soar/ | ❌ NO | SOAR algorithm |
| model_loader.py | apps/api/app/plugins/prediction/soar/ | ❌ NO | SOAR artifact loading |
| deployment_registry.py | apps/api/app/plugins/prediction/soar/ | ❌ NO | SOAR deployment tracking |
| explainability_adapter.py | apps/api/app/plugins/prediction/soar/ | ❌ NO | SOAR SHAP integration |
| **ARMD** | | | |
| armd_prediction_plugin.py | apps/api/app/plugins/prediction/armd/ | ❌ NO | Plugin-specific |
| runtime_context.py | apps/api/app/plugins/prediction/armd/ | ❌ NO | ARMD-specific implementation |
| prediction_engine.py | apps/api/app/plugins/prediction/armd/ | ❌ NO | ARMD orchestration |
| explainability.py | apps/api/app/plugins/prediction/armd/ | ❌ NO | ARMD explanation wrapping |

---

## Conclusion

### Framework Boundary Verification Result

✅ **ALL COMPONENTS CORRECTLY LOCATED**

**Findings**:
1. Core framework (runtime.py, plugin.py, explainability.py, exceptions.py, contracts.py) → Framework ✅
2. Adapters (armd_adapter.py) → Framework/adapters/ ✅
3. Plugin implementations → Apps/plugins/ ✅
4. Plugin-specific logic → Stays in plugins ✅

**No relocations needed.** Framework boundary is correctly drawn.

**Key Principle Upheld**: 
- **Framework**: Infrastructure (lifecycle, contracts, error handling, adapter patterns)
- **Plugins**: Domain logic (SOAR artifacts, ARMD WP4 wrapping, future TB models)

---

## Recommendations

### For Phase 2 (Plugin Refactoring)

✅ No changes needed to framework locations.  
✅ SOAR and ARMD can safely inherit from framework components.  
✅ Future plugins can use same framework structure.  

### For Future Enhancements

If future plugins need:
- New generic adapters → Add to adapters/
- Plugin-specific contracts → Keep in plugin (or add to contracts.py if pattern is generic)
- New error types → Add to exceptions.py if shared; keep in plugin if specific
- New base classes → Add to framework if pattern is shared; keep in plugin if specific

---

## Status

**Framework Boundary Report**: ✅ **PASS**

All components belong in their current locations. Framework is correctly structured for growth.
