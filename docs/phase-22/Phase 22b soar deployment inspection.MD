# Phase 22B — SOAR Deployment Inspection

Ten deployments were discovered under the runtime-active root (`deployments/SOAR_GSK/SOAR_GSK/deployment/`) — confirmed by direct directory listing, not assumed. All ten are inspected below.

Organism and antimicrobial names shown here are **corrected, human-verified** readings of each deployment folder name — not the output of `DeploymentScanner._parse_deployment_id()`, which is proven wrong for every single deployment (see Phase 22C). The folder name itself is treated as directly-verifiable evidence (it is the literal directory the artifacts live in); the *parsing logic* applied to it by the scanner is the broken part.

---

## Deployment: `Cefixime_Haemophilus_influenzae`

- **Organism:** Haemophilus influenzae
- **Antimicrobial:** Cefixime
- **Model artifact:** `final_model.pkl` — `sklearn.calibration.CalibratedClassifierCV` wrapping a `sklearn.pipeline.Pipeline`
- **Preprocessing artifact:** embedded inside `final_model.pkl` (no separate file needed at runtime — see Phase 22F)
- **Runtime entry point:** `PredictionEngine._preprocess()` → `model.predict()` / `model.predict_proba()` (`apps/api/app/plugins/prediction/soar/prediction_engine.py`)
- **Load status:** OK
- **Input features (raw, verified from `model.feature_names_in_`):** ['Age', 'BodyLocation_Group', 'Region', 'Country', 'YearCollected', 'Beta_Lactamase_enc']
- **Feature order:** NOT_REQUIRED — verified. `model.feature_names_in_` selects columns from a `pandas.DataFrame` by **name**, not position (confirmed: the embedded `ColumnTransformer`'s per-transformer `columns` lists select by name). `PredictionEngine._preprocess()` also builds the DataFrame with `{name: payload[name] for name in expected_features}`, i.e. by name. Submitting the 5-6 fields in any order is safe.
- **Output:** binary class, decoded via `label_encoder.pkl` to `['R', 'S']` (Resistant / Susceptible — no Intermediate category exists for this deployment)
- **Decision threshold:** `0.25000000000000006` (probability of the "S" class must be ≥ this value to pass; from `optimal_threshold.json`, verified per-deployment — thresholds differ across deployments, do not assume a shared 0.5 cutoff)
- **Fitted categorical vocabulary (verified, extracted directly from the fitted encoders):**
  - `Region`: ['Asia', 'Europe', 'Middle East']
  - `BodyLocation_Group`: ['Blood', 'Other', 'Respiratory']
  - `Country`: ['Italy', 'Kuwait', 'Spain', 'Turkey', 'Ukraine', 'United Arab Emirates', 'Vietnam']
- **Evidence:** `scripts/inspect_soar_artifacts/inspect_runtime_deployments.py` output, entry `"Cefixime_Haemophilus_influenzae"` in `docs/phase-22/_raw_inspection_output.json`

## Deployment: `Cefotaxime_Haemophilus_influenzae`

- **Organism:** Haemophilus influenzae
- **Antimicrobial:** Cefotaxime
- **Model artifact:** `final_model.pkl` — `sklearn.calibration.CalibratedClassifierCV` wrapping a `sklearn.pipeline.Pipeline`
- **Preprocessing artifact:** embedded inside `final_model.pkl` (no separate file needed at runtime — see Phase 22F)
- **Runtime entry point:** `PredictionEngine._preprocess()` → `model.predict()` / `model.predict_proba()` (`apps/api/app/plugins/prediction/soar/prediction_engine.py`)
- **Load status:** OK
- **Input features (raw, verified from `model.feature_names_in_`):** ['Age', 'BodyLocation_Group', 'Region', 'Country', 'YearCollected', 'Beta_Lactamase_enc']
- **Feature order:** NOT_REQUIRED — verified. `model.feature_names_in_` selects columns from a `pandas.DataFrame` by **name**, not position (confirmed: the embedded `ColumnTransformer`'s per-transformer `columns` lists select by name). `PredictionEngine._preprocess()` also builds the DataFrame with `{name: payload[name] for name in expected_features}`, i.e. by name. Submitting the 5-6 fields in any order is safe.
- **Output:** binary class, decoded via `label_encoder.pkl` to `['R', 'S']` (Resistant / Susceptible — no Intermediate category exists for this deployment)
- **Decision threshold:** `0.3000000000000001` (probability of the "S" class must be ≥ this value to pass; from `optimal_threshold.json`, verified per-deployment — thresholds differ across deployments, do not assume a shared 0.5 cutoff)
- **Fitted categorical vocabulary (verified, extracted directly from the fitted encoders):**
  - `Region`: ['Asia', 'Europe', 'Middle East']
  - `BodyLocation_Group`: ['Blood', 'Other', 'Respiratory']
  - `Country`: ['Italy', 'Kuwait', 'Spain', 'Turkey', 'Ukraine', 'United Arab Emirates', 'Vietnam']
- **Evidence:** `scripts/inspect_soar_artifacts/inspect_runtime_deployments.py` output, entry `"Cefotaxime_Haemophilus_influenzae"` in `docs/phase-22/_raw_inspection_output.json`

## Deployment: `Cefpodoxime_Haemophilus_influenzae`

- **Organism:** Haemophilus influenzae
- **Antimicrobial:** Cefpodoxime
- **Model artifact:** `final_model.pkl` — `sklearn.calibration.CalibratedClassifierCV` wrapping a `sklearn.pipeline.Pipeline`
- **Preprocessing artifact:** embedded inside `final_model.pkl` (no separate file needed at runtime — see Phase 22F)
- **Runtime entry point:** `PredictionEngine._preprocess()` → `model.predict()` / `model.predict_proba()` (`apps/api/app/plugins/prediction/soar/prediction_engine.py`)
- **Load status:** OK
- **Input features (raw, verified from `model.feature_names_in_`):** ['Age', 'BodyLocation_Group', 'Region', 'Country', 'YearCollected', 'Beta_Lactamase_enc']
- **Feature order:** NOT_REQUIRED — verified. `model.feature_names_in_` selects columns from a `pandas.DataFrame` by **name**, not position (confirmed: the embedded `ColumnTransformer`'s per-transformer `columns` lists select by name). `PredictionEngine._preprocess()` also builds the DataFrame with `{name: payload[name] for name in expected_features}`, i.e. by name. Submitting the 5-6 fields in any order is safe.
- **Output:** binary class, decoded via `label_encoder.pkl` to `['R', 'S']` (Resistant / Susceptible — no Intermediate category exists for this deployment)
- **Decision threshold:** `0.25000000000000006` (probability of the "S" class must be ≥ this value to pass; from `optimal_threshold.json`, verified per-deployment — thresholds differ across deployments, do not assume a shared 0.5 cutoff)
- **Fitted categorical vocabulary (verified, extracted directly from the fitted encoders):**
  - `Region`: ['Asia', 'Europe', 'Middle East']
  - `BodyLocation_Group`: ['Blood', 'Other', 'Respiratory']
  - `Country`: ['Italy', 'Kuwait', 'Spain', 'Turkey', 'Ukraine', 'United Arab Emirates', 'Vietnam']
- **Evidence:** `scripts/inspect_soar_artifacts/inspect_runtime_deployments.py` output, entry `"Cefpodoxime_Haemophilus_influenzae"` in `docs/phase-22/_raw_inspection_output.json`

## Deployment: `Ceftibuten_Haemophilus_influenzae`

- **Organism:** Haemophilus influenzae
- **Antimicrobial:** Ceftibuten
- **Model artifact:** `final_model.pkl` — `sklearn.calibration.CalibratedClassifierCV` wrapping a `sklearn.pipeline.Pipeline`
- **Preprocessing artifact:** embedded inside `final_model.pkl` (no separate file needed at runtime — see Phase 22F)
- **Runtime entry point:** `PredictionEngine._preprocess()` → `model.predict()` / `model.predict_proba()` (`apps/api/app/plugins/prediction/soar/prediction_engine.py`)
- **Load status:** OK
- **Input features (raw, verified from `model.feature_names_in_`):** ['Age', 'BodyLocation_Group', 'Region', 'Country', 'YearCollected', 'Beta_Lactamase_enc']
- **Feature order:** NOT_REQUIRED — verified. `model.feature_names_in_` selects columns from a `pandas.DataFrame` by **name**, not position (confirmed: the embedded `ColumnTransformer`'s per-transformer `columns` lists select by name). `PredictionEngine._preprocess()` also builds the DataFrame with `{name: payload[name] for name in expected_features}`, i.e. by name. Submitting the 5-6 fields in any order is safe.
- **Output:** binary class, decoded via `label_encoder.pkl` to `['R', 'S']` (Resistant / Susceptible — no Intermediate category exists for this deployment)
- **Decision threshold:** `0.3500000000000001` (probability of the "S" class must be ≥ this value to pass; from `optimal_threshold.json`, verified per-deployment — thresholds differ across deployments, do not assume a shared 0.5 cutoff)
- **Fitted categorical vocabulary (verified, extracted directly from the fitted encoders):**
  - `Region`: ['Asia', 'Europe', 'Middle East']
  - `BodyLocation_Group`: ['Blood', 'Other', 'Respiratory']
  - `Country`: ['Italy', 'Kuwait', 'Spain', 'Turkey', 'Ukraine', 'United Arab Emirates', 'Vietnam']
- **Evidence:** `scripts/inspect_soar_artifacts/inspect_runtime_deployments.py` output, entry `"Ceftibuten_Haemophilus_influenzae"` in `docs/phase-22/_raw_inspection_output.json`

## Deployment: `Ceftriaxone_Haemophilus_influenzae`

- **Organism:** Haemophilus influenzae
- **Antimicrobial:** Ceftriaxone
- **Model artifact:** `final_model.pkl` — `sklearn.calibration.CalibratedClassifierCV` wrapping a `sklearn.pipeline.Pipeline`
- **Preprocessing artifact:** embedded inside `final_model.pkl` (no separate file needed at runtime — see Phase 22F)
- **Runtime entry point:** `PredictionEngine._preprocess()` → `model.predict()` / `model.predict_proba()` (`apps/api/app/plugins/prediction/soar/prediction_engine.py`)
- **Load status:** OK
- **Input features (raw, verified from `model.feature_names_in_`):** ['Age', 'BodyLocation_Group', 'Region', 'Country', 'YearCollected', 'Beta_Lactamase_enc']
- **Feature order:** NOT_REQUIRED — verified. `model.feature_names_in_` selects columns from a `pandas.DataFrame` by **name**, not position (confirmed: the embedded `ColumnTransformer`'s per-transformer `columns` lists select by name). `PredictionEngine._preprocess()` also builds the DataFrame with `{name: payload[name] for name in expected_features}`, i.e. by name. Submitting the 5-6 fields in any order is safe.
- **Output:** binary class, decoded via `label_encoder.pkl` to `['R', 'S']` (Resistant / Susceptible — no Intermediate category exists for this deployment)
- **Decision threshold:** `0.12500000000000003` (probability of the "S" class must be ≥ this value to pass; from `optimal_threshold.json`, verified per-deployment — thresholds differ across deployments, do not assume a shared 0.5 cutoff)
- **Fitted categorical vocabulary (verified, extracted directly from the fitted encoders):**
  - `Region`: ['Asia', 'Europe', 'Middle East']
  - `BodyLocation_Group`: ['Blood', 'Other', 'Respiratory']
  - `Country`: ['Bulgaria', 'Croatia', 'Czech Republic', 'Greece', 'Italy', 'Kuwait', 'Romania', 'Russia', 'Slovak Republic', 'Spain', 'Turkey', 'Ukraine', 'United Arab Emirates', 'Vietnam']
- **Evidence:** `scripts/inspect_soar_artifacts/inspect_runtime_deployments.py` output, entry `"Ceftriaxone_Haemophilus_influenzae"` in `docs/phase-22/_raw_inspection_output.json`

## Deployment: `Doxycycline_Streptococcus_pneumoniae`

- **Organism:** Streptococcus pneumoniae
- **Antimicrobial:** Doxycycline
- **Model artifact:** `final_model.pkl` — `sklearn.calibration.CalibratedClassifierCV` wrapping a `sklearn.pipeline.Pipeline`
- **Preprocessing artifact:** embedded inside `final_model.pkl` (no separate file needed at runtime — see Phase 22F)
- **Runtime entry point:** `PredictionEngine._preprocess()` → `model.predict()` / `model.predict_proba()` (`apps/api/app/plugins/prediction/soar/prediction_engine.py`)
- **Load status:** OK
- **Input features (raw, verified from `model.feature_names_in_`):** ['Age', 'BodyLocation_Group', 'Region', 'Country', 'YearCollected']
- **Feature order:** NOT_REQUIRED — verified. `model.feature_names_in_` selects columns from a `pandas.DataFrame` by **name**, not position (confirmed: the embedded `ColumnTransformer`'s per-transformer `columns` lists select by name). `PredictionEngine._preprocess()` also builds the DataFrame with `{name: payload[name] for name in expected_features}`, i.e. by name. Submitting the 5-6 fields in any order is safe.
- **Output:** binary class, decoded via `label_encoder.pkl` to `['R', 'S']` (Resistant / Susceptible — no Intermediate category exists for this deployment)
- **Decision threshold:** `0.3500000000000001` (probability of the "S" class must be ≥ this value to pass; from `optimal_threshold.json`, verified per-deployment — thresholds differ across deployments, do not assume a shared 0.5 cutoff)
- **Fitted categorical vocabulary (verified, extracted directly from the fitted encoders):**
  - `Region`: ['Asia', 'Europe', 'Middle East']
  - `BodyLocation_Group`: ['Blood', 'Other', 'Respiratory']
  - `Country`: ['Italy', 'Kuwait', 'Pakistan', 'Spain', 'Turkey', 'Ukraine', 'United Arab Emirates', 'Vietnam']
- **Evidence:** `scripts/inspect_soar_artifacts/inspect_runtime_deployments.py` output, entry `"Doxycycline_Streptococcus_pneumoniae"` in `docs/phase-22/_raw_inspection_output.json`

## Deployment: `Levofloxacin_Haemophilus_influenzae`

- **Organism:** Haemophilus influenzae
- **Antimicrobial:** Levofloxacin
- **Model artifact:** `final_model.pkl` — `sklearn.calibration.CalibratedClassifierCV` wrapping a `sklearn.pipeline.Pipeline`
- **Preprocessing artifact:** embedded inside `final_model.pkl` (no separate file needed at runtime — see Phase 22F)
- **Runtime entry point:** `PredictionEngine._preprocess()` → `model.predict()` / `model.predict_proba()` (`apps/api/app/plugins/prediction/soar/prediction_engine.py`)
- **Load status:** OK
- **Input features (raw, verified from `model.feature_names_in_`):** ['Age', 'BodyLocation_Group', 'Region', 'Country', 'YearCollected', 'Beta_Lactamase_enc']
- **Feature order:** NOT_REQUIRED — verified. `model.feature_names_in_` selects columns from a `pandas.DataFrame` by **name**, not position (confirmed: the embedded `ColumnTransformer`'s per-transformer `columns` lists select by name). `PredictionEngine._preprocess()` also builds the DataFrame with `{name: payload[name] for name in expected_features}`, i.e. by name. Submitting the 5-6 fields in any order is safe.
- **Output:** binary class, decoded via `label_encoder.pkl` to `['R', 'S']` (Resistant / Susceptible — no Intermediate category exists for this deployment)
- **Decision threshold:** `0.22500000000000003` (probability of the "S" class must be ≥ this value to pass; from `optimal_threshold.json`, verified per-deployment — thresholds differ across deployments, do not assume a shared 0.5 cutoff)
- **Fitted categorical vocabulary (verified, extracted directly from the fitted encoders):**
  - `Region`: ['Asia', 'Europe', 'Middle East']
  - `BodyLocation_Group`: ['Blood', 'Other', 'Respiratory']
  - `Country`: ['Bulgaria', 'Croatia', 'Czech Republic', 'Greece', 'India', 'Italy', 'Kuwait', 'Pakistan', 'Romania', 'Russia', 'Serbia', 'Slovak Republic', 'Spain', 'Turkey', 'Ukraine', 'United Arab Emirates', 'Vietnam']
- **Evidence:** `scripts/inspect_soar_artifacts/inspect_runtime_deployments.py` output, entry `"Levofloxacin_Haemophilus_influenzae"` in `docs/phase-22/_raw_inspection_output.json`

## Deployment: `Tetracycline_Haemophilus_influenzae`

- **Organism:** Haemophilus influenzae
- **Antimicrobial:** Tetracycline
- **Model artifact:** `final_model.pkl` — `sklearn.calibration.CalibratedClassifierCV` wrapping a `imblearn.pipeline.Pipeline`
- **Preprocessing artifact:** embedded inside `final_model.pkl` (no separate file needed at runtime — see Phase 22F)
- **Runtime entry point:** `PredictionEngine._preprocess()` → `model.predict()` / `model.predict_proba()` (`apps/api/app/plugins/prediction/soar/prediction_engine.py`)
- **Load status:** OK
- **Input features (raw, verified from `model.feature_names_in_`):** ['Age', 'BodyLocation_Group', 'Region', 'Country', 'YearCollected', 'Beta_Lactamase_enc']
- **Feature order:** NOT_REQUIRED — verified. `model.feature_names_in_` selects columns from a `pandas.DataFrame` by **name**, not position (confirmed: the embedded `ColumnTransformer`'s per-transformer `columns` lists select by name). `PredictionEngine._preprocess()` also builds the DataFrame with `{name: payload[name] for name in expected_features}`, i.e. by name. Submitting the 5-6 fields in any order is safe.
- **Output:** binary class, decoded via `label_encoder.pkl` to `['R', 'S']` (Resistant / Susceptible — no Intermediate category exists for this deployment)
- **Decision threshold:** `0.47500000000000014` (probability of the "S" class must be ≥ this value to pass; from `optimal_threshold.json`, verified per-deployment — thresholds differ across deployments, do not assume a shared 0.5 cutoff)
- **Fitted categorical vocabulary (verified, extracted directly from the fitted encoders):**
  - `Region`: ['Asia', 'Europe', 'Middle East']
  - `BodyLocation_Group`: ['Blood', 'Other', 'Respiratory']
  - `Country`: ['India', 'Italy', 'Kuwait', 'Spain', 'Turkey', 'Ukraine', 'United Arab Emirates', 'Vietnam']
- **Evidence:** `scripts/inspect_soar_artifacts/inspect_runtime_deployments.py` output, entry `"Tetracycline_Haemophilus_influenzae"` in `docs/phase-22/_raw_inspection_output.json`

## Deployment: `Tetracycline_Streptococcus_pneumoniae`

- **Organism:** Streptococcus pneumoniae
- **Antimicrobial:** Tetracycline
- **Model artifact:** `final_model.pkl` — `sklearn.calibration.CalibratedClassifierCV` wrapping a `sklearn.pipeline.Pipeline`
- **Preprocessing artifact:** embedded inside `final_model.pkl` (no separate file needed at runtime — see Phase 22F)
- **Runtime entry point:** `PredictionEngine._preprocess()` → `model.predict()` / `model.predict_proba()` (`apps/api/app/plugins/prediction/soar/prediction_engine.py`)
- **Load status:** OK
- **Input features (raw, verified from `model.feature_names_in_`):** ['Age', 'BodyLocation_Group', 'Region', 'Country', 'YearCollected']
- **Feature order:** NOT_REQUIRED — verified. `model.feature_names_in_` selects columns from a `pandas.DataFrame` by **name**, not position (confirmed: the embedded `ColumnTransformer`'s per-transformer `columns` lists select by name). `PredictionEngine._preprocess()` also builds the DataFrame with `{name: payload[name] for name in expected_features}`, i.e. by name. Submitting the 5-6 fields in any order is safe.
- **Output:** binary class, decoded via `label_encoder.pkl` to `['R', 'S']` (Resistant / Susceptible — no Intermediate category exists for this deployment)
- **Decision threshold:** `0.32500000000000007` (probability of the "S" class must be ≥ this value to pass; from `optimal_threshold.json`, verified per-deployment — thresholds differ across deployments, do not assume a shared 0.5 cutoff)
- **Fitted categorical vocabulary (verified, extracted directly from the fitted encoders):**
  - `Region`: ['Asia', 'Europe', 'Middle East']
  - `BodyLocation_Group`: ['Blood', 'Other', 'Respiratory']
  - `Country`: ['Italy', 'Kuwait', 'Pakistan', 'Spain', 'Turkey', 'Ukraine', 'United Arab Emirates', 'Vietnam']
- **Evidence:** `scripts/inspect_soar_artifacts/inspect_runtime_deployments.py` output, entry `"Tetracycline_Streptococcus_pneumoniae"` in `docs/phase-22/_raw_inspection_output.json`

## Deployment: `Trimethoprim_Sulfa_Haemophilus_influenzae`

- **Organism:** Haemophilus influenzae
- **Antimicrobial:** Trimethoprim-Sulfamethoxazole
- **Model artifact:** `final_model.pkl` — `sklearn.calibration.CalibratedClassifierCV` wrapping a `sklearn.pipeline.Pipeline`
- **Preprocessing artifact:** embedded inside `final_model.pkl` (no separate file needed at runtime — see Phase 22F)
- **Runtime entry point:** `PredictionEngine._preprocess()` → `model.predict()` / `model.predict_proba()` (`apps/api/app/plugins/prediction/soar/prediction_engine.py`)
- **Load status:** OK
- **Input features (raw, verified from `model.feature_names_in_`):** ['Age', 'BodyLocation_Group', 'Region', 'Country', 'YearCollected', 'Beta_Lactamase_enc']
- **Feature order:** NOT_REQUIRED — verified. `model.feature_names_in_` selects columns from a `pandas.DataFrame` by **name**, not position (confirmed: the embedded `ColumnTransformer`'s per-transformer `columns` lists select by name). `PredictionEngine._preprocess()` also builds the DataFrame with `{name: payload[name] for name in expected_features}`, i.e. by name. Submitting the 5-6 fields in any order is safe.
- **Output:** binary class, decoded via `label_encoder.pkl` to `['R', 'S']` (Resistant / Susceptible — no Intermediate category exists for this deployment)
- **Decision threshold:** `0.4500000000000001` (probability of the "S" class must be ≥ this value to pass; from `optimal_threshold.json`, verified per-deployment — thresholds differ across deployments, do not assume a shared 0.5 cutoff)
- **Fitted categorical vocabulary (verified, extracted directly from the fitted encoders):**
  - `Region`: ['Europe', 'Middle East']
  - `BodyLocation_Group`: ['Blood', 'Other', 'Respiratory']
  - `Country`: ['Bulgaria', 'Croatia', 'Czech Republic', 'Greece', 'Italy', 'Kuwait', 'Romania', 'Russia', 'Serbia', 'Slovak Republic', 'Spain', 'Turkey', 'Ukraine', 'United Arab Emirates']
- **Evidence:** `scripts/inspect_soar_artifacts/inspect_runtime_deployments.py` output, entry `"Trimethoprim_Sulfa_Haemophilus_influenzae"` in `docs/phase-22/_raw_inspection_output.json`

---

## Appendix — `Beta_Lactamase_enc` encoding: a genuine evidence gap

For the 8 *H. influenzae* deployments, `Beta_Lactamase_enc` passes through a `sklearn.preprocessing.FunctionTransformer` (identity passthrough) directly into the classifier — confirmed by direct inspection of the embedded `ColumnTransformer`'s `"bin"` transformer. Passthrough means the pipeline applies **no transformation and stores no mapping**. The column name (`_enc` suffix) strongly implies the training data supplied this as an already-encoded binary numeric value (0/1), not a raw string like `"Positive"`/`"Negative"`.

**No artifact inspected in this session records which numeric value (0 or 1) corresponds to "beta-lactamase positive" versus "negative."** This is exactly the kind of value that must not be guessed per the Phase 22 core rule. Before this field can be safely offered as a clinician-facing Yes/No/Unknown control, the correct 0/1 mapping must be confirmed from the original model-training documentation or the model-training team — not inferred from the column name alone.

## Appendix — `YearCollected`: evidence against naive "current year" defaulting

Direct inspection of the embedded `StandardScaler` fitted on `["Age", "YearCollected"]` (Ceftriaxone deployment, representative of the shared preprocessing structure) gives:

- `YearCollected` fitted mean ≈ **2019.53**
- `YearCollected` fitted standard deviation ≈ **0.99**

The training data's `YearCollected` values cluster tightly within roughly one year of 2019.5. Submitting today's date (2026) as `YearCollected` would standardize to a z-score of roughly **+6.5 standard deviations** — a severe out-of-distribution input `StandardScaler` does not clip, flag, or reject. The model would silently receive a value far outside anything it was trained or calibrated on, with no runtime error to indicate this. **This field must not be silently defaulted to "current year" without an explicit product/data-science decision**; treat it as `NOT_AVAILABLE` from any canonical clinical source (see Phase 22E) until that decision is made.