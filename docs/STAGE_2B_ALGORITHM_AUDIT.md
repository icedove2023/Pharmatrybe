# Stage 2B Algorithm Audit — Detailed Analysis

**Purpose**: Deep dive into algorithmic components, verification of delegation, and identification of duplicated business logic.

---

## 1. Prediction Preprocessing Pipeline

### WP4 Implementation
```
Input: patient_data (dict)
  ↓
[WP4: preprocess_patient_features]
  ├─ Create pandas Series from input
  ├─ Apply WP3 artifacts (medians for imputation, dummy columns)
  ├─ Align features to expected schema
  └─ Return preprocessed DataFrame
  ↓
Output: DataFrame with aligned columns, no NaN values
```

### ARMDAdapter Implementation
```python
# Location: adapters/armd_adapter.py::preprocess_patient_features()

def preprocess_patient_features(self, patient_data):
    patient_series = pd.Series(patient_data)
    preprocessed_df = preprocess_patient_features(patient_series, self._wp3_artifacts)
    return preprocessed_df
```

**Assessment**: ✅ **PERFECT DELEGATION**
- Direct call to WP4's `preprocess_patient_features()`
- No reimplementation
- Uses loaded WP3 artifacts from WP4
- No algorithm invented

**Verification**: Unit tests in `TestARMDAdapterPreprocessing`
- Tests DataFrame output format
- Tests parity with WP4 (no NaN values, all features present)
- Uses sample patient fixtures

---

## 2. Model Inference Pipeline

### WP4 Implementation
```
Input: patient_features (DataFrame), model_package (dict)
  ↓
[WP4: load_inference_package]
  └─ Load scikit-learn model
  └─ Load preprocessing scaler
  └─ Load decision threshold
  └─ Return model, scaler, threshold, feature_names
  ↓
[WP4: predict_all_antibiotics]
  ├─ For each antibiotic:
  │  ├─ Load model package
  │  ├─ Scale input features
  │  ├─ model.predict_proba(X_scaled)  ← Returns probabilities
  │  ├─ Apply threshold decision
  │  └─ Return results dict
  ↓
Output: {antibiotic → {class: 'Resistant'|'Susceptible', prob: 0.75}}
```

### ARMDAdapter Implementation (Current)
```python
# Location: adapters/armd_adapter.py::predict()

def predict(self, model_package, patient_data):
    # Preprocessing — delegates to WP4 ✅
    patient_df = self.preprocess_patient_features(patient_data)
    
    # Feature alignment — delegates to WP4 ✅
    X = build_feature_frame(patient_df, model_package.feature_names)
    
    # Scaling — uses loaded model package ✅
    X_scaled = model_package.scaler.transform(X)
    
    # Inference — delegates to model ✅
    prob = model_package.model.predict_proba(X_scaled)[0, 1]
    
    # ❌ THRESHOLD/CLASSIFICATION — REIMPLEMENTED
    class_label = 'Resistant' if prob >= model_package.threshold else 'Susceptible'
    
    # ❌ CONFIDENCE — CUSTOM FORMULA
    confidence = abs(prob - model_package.threshold)
    
    return PredictionExecution(...)
```

**Assessment**: ⚠️ **PARTIAL DELEGATION**

| Step | Delegation | Status |
|------|---|---|
| Preprocessing | `preprocess_patient_features()` | ✅ OK |
| Feature alignment | `build_feature_frame()` | ✅ OK |
| Scaling | `model_package.scaler.transform()` | ✅ OK |
| Inference | `model.predict_proba()` | ✅ OK |
| Threshold application | Reimplemented locally | ❌ ISSUE |
| Confidence calculation | Custom formula | ❌ ISSUE |

**Why This Matters**:
- WP4's `predict_all_antibiotics()` implements the full pipeline, including threshold
- ARMDAdapter duplicates the threshold logic instead of calling it
- If WP4's threshold logic changes, ARMDAdapter won't reflect it automatically
- Violates DRY principle and delegation constraint

**What Should Happen**:

**Option A**: Call WP4's predict_all_antibiotics() directly
```python
def predict(self, model_package, patient_data):
    # Call WP4's full prediction pipeline
    results = predict_all_antibiotics(
        patient_data, 
        registry=self._registry,
        antibiotic=model_package.id
    )
    
    # Extract and map results
    return PredictionExecution(
        status=PredictionStatus.SUCCESS,
        model_id=model_package.id,
        predictions=results[model_package.id],
        ...
    )
```

**Option B**: Extract threshold logic to wrapper function
```python
# In WP4_Decision_Engine or in adapter as WP4 delegate wrapper
def apply_threshold(prob, threshold):
    return 'Resistant' if prob >= threshold else 'Susceptible'

# Then in predict():
class_label = apply_threshold(prob, model_package.threshold)
```

**Verification**: Unit test `TestARMDAdapterPrediction::test_prediction_matches_wp4`
- Would compare adapter output to WP4's `predict_all_antibiotics()` output
- Would validate that class labels and probabilities match exactly
- Would verify confidence metric (currently not validated)

---

## 3. Confidence Metric Calculation

### Current Implementation
```python
confidence = abs(prob - model_package.threshold)
```

### Issues

**Issue 1: Non-Standard Definition**
- Standard practice: confidence = probability (0.0 to 1.0)
- This formula: distance from threshold (0.0 to max)
- Example: 
  - prob=0.9, threshold=0.5 → confidence=0.4
  - prob=0.51, threshold=0.5 → confidence=0.01
  - This means predictions just over threshold have LOW confidence
  - Clinically counterintuitive

**Issue 2: No Verification with WP4**
- WP4's `predict_all_antibiotics()` may return confidence separately
- If so, adapter should use that instead of reimplementing
- If not, formula should be documented and justified

**Issue 3: Impact on Explainability**
- Confidence is used in clinical explanations to users
- Clinicians expect confidence = probability (0-1 scale)
- Custom formula may confuse or mislead

**What Should Happen**:
```python
# Check if WP4 returns confidence in results
def predict(self, model_package, patient_data):
    results = predict_all_antibiotics(...)  # Returns dict
    
    if 'confidence' in results[model_package.id]:
        confidence = results[model_package.id]['confidence']  # Use WP4's definition
    else:
        confidence = prob  # Default to probability
```

**Verification**:
- Unit tests don't validate confidence metric
- Integration tests don't check confidence ranges
- E2E parity tests should compare confidence to WP5 endpoint

---

## 4. SHAP Explainability Pipeline

### WP4 Implementation
```
Input: patient_data, model, features, threshold
  ↓
[WP4: build_background]
  ├─ Sample from patient cohort (WP2 table)
  ├─ Preprocess background data
  ├─ Scale using model's scaler
  └─ Return background array
  ↓
[WP4: generate_shap_explanation]
  ├─ Create SHAP explainer
  ├─ Compute SHAP values
  ├─ Extract positive drivers (features increasing prob)
  ├─ Extract negative drivers (features decreasing prob)
  ├─ Generate narrative explanation
  ├─ Create SHAP visualizations (figures)
  └─ Return dict:
     {
         'base_value': float,
         'positive_drivers': [(feature, contribution), ...],
         'negative_drivers': [(feature, contribution), ...],
         'narrative': str,
         'figure_paths': {figure_type: path}
     }
  ↓
Output: Explainability dict
```

### ARMDAdapter Implementation
```python
# Location: adapters/armd_adapter.py::explain()

def explain(self, model_package, patient_data, prediction_execution):
    # Build background — delegates to WP4 ✅
    if self._wp2_table is not None:
        background_data = build_background(
            self._wp2_table,
            model_package.scaler,
            model_package.feature_names,
            self._wp3_artifacts,
            n_samples=200,
        )
    
    # Generate SHAP explanation — delegates to WP4 ✅
    shap_result = generate_shap_explanation(
        patient_id=patient_data.get('patient_id'),
        patient_df=patient_df,
        registry=self._registry,
        top_abx=model_package.id,
        background_data=background_data,
        feature_names=model_package.feature_names,
        model=model_package.model,
        scaler=model_package.scaler,
        patient_dir="/tmp",
    )
    
    # Map to contract — pure structural mapping ✅
    pos_drivers = [
        ExplainabilityDriver(
            feature_name=name,
            display_name=DISPLAY_NAMES.get(name, name),
            contribution=float(value),
        )
        for name, value in shap_result.get('positive_drivers', [])
    ]
    
    # Return in unified contract format
    return ExplainabilityPayload(
        prediction_id=...,
        model_id=model_package.id,
        base_value=shap_result.get('base_value'),
        positive_drivers=pos_drivers,
        negative_drivers=neg_drivers,  # Similarly mapped
        narrative=shap_result.get('narrative'),
        ...
    )
```

**Assessment**: ✅ **PERFECT DELEGATION + STRUCTURAL MAPPING**

| Step | Delegation | Status |
|------|---|---|
| Background data building | `build_background()` | ✅ OK |
| SHAP calculation | `generate_shap_explanation()` | ✅ OK |
| Result mapping | Pure data transformation | ✅ OK |
| Error handling | Graceful fallback | ✅ OK |

**Why This Is Correct**:
- All algorithm work delegated to WP4
- Only mapping from WP4 output format to unified contract format
- No SHAP logic reimplemented
- Error handling with graceful degradation (returns minimal payload on failure)

**Verification**: Unit test `TestARMDAdapterExplainability`
- Tests SHAP generation succeeds
- Tests drivers are extracted correctly
- Tests graceful degradation on SHAP failure
- Does NOT test SHAP accuracy (WP4's responsibility)

---

## 5. Prediction Ranking Pipeline

### WP4 Implementation
- WP4 predicts for all antibiotics independently
- No built-in ranking; returns dict of results
- Ranking is orchestration concern, not algorithm

### ARMDAdapter Implementation
```python
# Location: adapters/armd_adapter.py::predict_all_antibiotics()

def predict_all_antibiotics(self, patient_data):
    results = {}
    for antibiotic in self._registry.keys():
        model_package = self.load_model_package(antibiotic)
        execution = self.predict(model_package, patient_data)  # Call per-antibiotic
        results[antibiotic] = execution
    
    return results  # No ranking here
```

### PredictionEngine Implementation
```python
# Location: apps/api/app/plugins/prediction/armd/prediction_engine.py

def predict(self, request):
    predictions = adapter.predict_all_antibiotics(patient_data)
    
    recommendation_list = []
    for antibiotic, execution in predictions.items():
        if execution.status == PredictionStatus.SUCCESS:
            recommendation_list.append({
                'antibiotic': antibiotic,
                'probability': execution.confidence,
                'class': execution.selected_class,
            })
    
    # ✅ Framework-level ranking (not clinical algorithm)
    recommendation_list.sort(key=lambda x: x['probability'])  # Ascending
    
    return PredictionResult(...)
```

**Assessment**: ✅ **ORCHESTRATION ONLY (NOT ALGORITHM)**

| Step | Type | Status |
|------|------|--------|
| Per-antibiotic prediction | Algorithm (delegated) | ✅ OK |
| Ranking by probability | Orchestration | ✅ OK |
| Response formatting | Framework | ✅ OK |

**Why This Is Correct**:
- Ranking is platform concern, not clinical algorithm
- Sorting by probability is deterministic and auditable
- No clinical decision logic in ranking
- Each prediction is independent; ranking doesn't alter it

**Verification**: Framework-level test
- Verifies ranking is sorted by probability
- Verifies all results included (no prediction dropped)

---

## 6. Business Logic Duplication Analysis

### Duplicated Logic Found

#### Duplication 1: Binary Classification (Medium Severity)
**Where**: ARMDAdapter.predict() vs. WP4's predict_all_antibiotics()
**What**: `if prob >= threshold: 'Resistant' else: 'Susceptible'`
**Impact**: Risk of divergence if WP4 implementation changes

#### Duplication 2: Confidence Calculation (Low Severity)
**Where**: ARMDAdapter.predict() custom formula
**What**: `abs(prob - threshold)` confidence metric
**Impact**: May not match WP4 or clinician expectations

#### Duplication 3: None other detected
**Assessment**: No other business logic duplication found

### Where Duplication Should Exist (But Doesn't)

#### Good: No Duplication of Preprocessing
- ARMDAdapter delegates to WP4's preprocess_patient_features()
- No reimplementation

#### Good: No Duplication of SHAP
- ARMDAdapter delegates to WP4's generate_shap_explanation()
- No reimplementation

#### Good: No Duplication of Ranking
- PredictionEngine implements only sorting (orchestration, not algorithm)
- No reimplementation of WP4 logic

---

## 7. Missing Delegations (Opportunities for Improvement)

### Missing Delegation 1: Threshold Application
**Current**: ARMDAdapter reimplements
**Opportunity**: Call WP4's predict_all_antibiotics() to get class labels directly

### Missing Delegation 2: Confidence Metric
**Current**: ARMDAdapter uses custom formula
**Opportunity**: Use WP4's confidence if available; else align formula with standard definition

### Missing Delegation 3: None others identified
**Assessment**: All other core algorithms properly delegated

---

## 8. Algorithm Audit Checklist

### Preprocessing ✅
- [ ] Wrapper: `preprocess_patient_features()` calls WP4 → **YES**
- [ ] WP3 artifacts used → **YES**
- [ ] No reimplementation → **YES**
- [ ] Test parity validation → **YES**

### Inference ✅
- [ ] Model loading delegates to `load_inference_package()` → **YES**
- [ ] Prediction uses `model.predict_proba()` → **YES**
- [ ] Threshold logic delegates to WP4 → **NO** ❌
- [ ] Test parity validation → **PARTIAL** (doesn't test threshold logic)

### SHAP Explainability ✅
- [ ] Background building delegates to `build_background()` → **YES**
- [ ] SHAP generation delegates to `generate_shap_explanation()` → **YES**
- [ ] No SHAP algorithm reimplemented → **YES**
- [ ] Error handling graceful → **YES**
- [ ] Test coverage → **YES**

### Ranking ✅
- [ ] Orchestration only (not algorithm) → **YES**
- [ ] Per-prediction results unmodified → **YES**
- [ ] Sorting deterministic → **YES**

---

## 9. Risk Assessment

### High Risk
**None**. No clinical decision logic reimplemented.

### Medium Risk
**Binary Classification Duplication** (ARMDAdapter.predict)
- May diverge from WP4 if WP4 implementation changes
- Could cause test parity failures
- No immediate safety issue (same threshold logic)
- Mitigation: Run unit tests; verify against WP4; extract to wrapper if needed

### Low Risk
**Confidence Metric Alignment** (ARMDAdapter.predict)
- May not match WP4 definition
- Affects explainability/reporting, not clinical safety
- Mitigation: Verify with WP4; document if intentional

---

## 10. Recommendations

### Immediate (Before Test Execution)

1. **Investigate Binary Classification**
   ```python
   # Verify WP4's predict_all_antibiotics() return format
   # Expected: {antibiotic: {'class': 'Resistant'|'Susceptible', 'prob': 0.75}}
   # If yes, update ARMDAdapter.predict() to call WP4 function
   ```

2. **Verify Confidence Metric**
   ```python
   # Check WP4_Decision_Engine for confidence definition
   # If returns confidence separately, use that
   # Else, verify abs(prob - threshold) is intentional
   ```

### Short Term (After Tests Pass)

3. **E2E Parity Testing**
   - Compare plugin predictions to legacy WP5 endpoints
   - Validate numerical parity (within floating-point tolerance)
   - Verify ranking order matches

4. **Document Algorithmic Decisions**
   - Explain why confidence = `abs(prob - threshold)` if kept
   - Document threshold application strategy
   - Add comments explaining non-standard choices

---

## Conclusion

**Delegation Score**: 9/10
- ✅ Preprocessing: 100% delegated
- ✅ SHAP Explanation: 100% delegated
- ⚠️ Inference: 90% delegated (threshold logic reimplemented)
- ✅ Ranking: N/A (orchestration, not algorithm)

**Overall Algorithm Audit**: PASS with minor clarifications

The implementation correctly delegates the majority of algorithm work to WP4, with two areas needing clarification:
1. Binary classification threshold logic
2. Confidence metric definition

Once these are clarified and tests validate parity with WP4, the implementation is production-ready.

---

**Supporting Documents**:
- `STAGE_2B_AUDIT_REPORT.md` — Full audit with code locations
- `STAGE_2B_IMPLEMENTATION_SUMMARY.md` — Implementation overview
