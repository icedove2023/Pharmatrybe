# SOAR and ARMD Clinical Runtime Audit

**Audit date:** 2026-08-27  
**Scope:** Supplied `deployments/SOAR_GSK/SOAR_GSK` package, live SOAR/ARMD plugins, model loading, inference compatibility, and the canonical pipeline boundary.

## Executive Decision

The SOAR and ARMD plugin runtimes are operational after the compatibility repairs documented below. A real SOAR model and real ARMD models load successfully in the project Python 3.12 environment. A successful model execution is not equivalent to clinical validation, however. The supplied evidence supports technical runtime readiness and historical model-performance reporting, but it does **not** support a claim that the current SOAR predictions are clinically accurate for current practice.

The system must remain clinician-facing decision support. It must not be presented as autonomous prescribing or as clinically validated solely because the endpoint returns HTTP 200.

## Supplied Package Inventory

The supplied directory is a complete SOAR working/archive workspace rather than a single runtime root. It contains:

- Three deployment generations: `deployment`, `deployment_reconstructed`, and `deployment_reconstructed_v2`.
- Ten deployable model folders in the supplied `deployment` generation.
- Recovery, reconstruction, training, EDA, simulation, SHAP, verification, and extraction outputs.
- Source datasets, including GSK CSV/XLSX material.
- 151 pickle files, 682 JSON files, 225 CSV files, 328 PNG files, 31 Python scripts, 27 Markdown files, and additional logs/PDF/HTML artifacts, based on recursive inventory.

The runtime must point to:

```text
deployments/SOAR_GSK/SOAR_GSK/deployment
```

It must not point at the entire `SOAR_GSK/SOAR_GSK` workspace because directories such as `ml_output`, `contracts`, and recovery folders would be incorrectly interpreted as deployments.

## Artifact Findings

The supplied `deployment` generation contains, for each of ten deployments:

- `final_model.pkl`
- `label_encoder.pkl`
- `optimal_threshold.json`
- `evaluation_metrics.csv`

All ten model files load with `joblib.load` and are `CalibratedClassifierCV` models. The models contain a scikit-learn preprocessing pipeline with six raw fields:

- `Age`
- `YearCollected`
- `Region`
- `BodyLocation_Group`
- `Country`
- `Beta_Lactamase_enc`

The ten supplied deployment thresholds are numeric. Examples include:

- Cefixime / *H. influenzae*: `0.25`
- Cefotaxime / *H. influenzae*: `0.30`
- Ceftriaxone / *H. influenzae*: `0.125`
- Tetracycline / *H. influenzae*: `0.475`

The `deployment_reconstructed_v2` generation contains richer metadata and certification files, but its threshold files explicitly state that thresholds are unrecoverable and recommend `0.5`. It also contains verification records with inference failures. It is therefore not the selected runtime source.

## Clinical Evidence and Limitations

Historical evaluation output reports useful discrimination for some combinations, for example:

- Cefotaxime / *H. influenzae*: test ROC-AUC approximately `0.952`
- Ceftriaxone / *H. influenzae*: test ROC-AUC approximately `0.934`
- Cefixime / *H. influenzae*: test ROC-AUC approximately `0.857`
- Levofloxacin / *H. influenzae*: test ROC-AUC approximately `0.596`

These are historical held-out evaluation results, not prospective clinical validation. The supplied evidence also reports:

- Duplicate rows in the source data.
- Substantial missingness in antimicrobial fields.
- Class imbalance and insufficient classes for some drug/species combinations.
- External-validation domain shift, including ROC-AUC below `0.5` for some SOAR/GSK transfer directions.
- Synthetic clinical simulation without ground-truth outcomes.
- Conflicting certification records: some package certificates are marked `certified: false`, while later verification reports state `certified: true`.
- Historical verification inference failure: `could not convert string to float: 'value'`.

Therefore the models may be technically runnable, but clinical accuracy remains unproven and requires prospective or independently held-out validation with clinically approved thresholds and outcome definitions.

## Code Repairs Applied

### Shared prediction base

[packages/prediction-framework/plugin.py](../../packages/prediction-framework/plugin.py) no longer forwards `config=` into `object.__init__`, which had caused SOAR construction to fail with:

```text
TypeError: object.__init__() takes exactly one argument
```

### ARMD contract and runtime

[apps/api/app/plugins/prediction/armd/armd_prediction_plugin.py](../../apps/api/app/plugins/prediction/armd/armd_prediction_plugin.py):

- Aligned `PluginMetadata` fields with the live dataclass contract.
- Aligned `PluginHealth` fields with the live dataclass contract.
- Standardized the plugin version to `0.1.0`.
- Implemented missing `PredictionPlugin` methods so ARMD is concrete and instantiable.

[packages/prediction-framework/adapters/armd_adapter.py](../../packages/prediction-framework/adapters/armd_adapter.py):

- Fixed repository-root discovery independent of current working directory.
- Normalized stale absolute registry paths to the active repository model folders.
- Normalized antibiotic names safely when mapping names to model-folder names.

[apps/api/app/plugins/prediction/armd/prediction_engine.py](../../apps/api/app/plugins/prediction/armd/prediction_engine.py):

- Uses `PredictionRequest.payload`.
- Returns the actual platform `PredictionResult` contract.

### Plugin discovery

[apps/api/app/plugins/discovery/plugin_loader.py](../../apps/api/app/plugins/discovery/plugin_loader.py) loads internal `app.*` entrypoints through Python's package importer so relative imports do not create partially initialized modules.

### SOAR runtime

[apps/api/app/plugins/prediction/soar/deployment_scanner.py](../../apps/api/app/plugins/prediction/soar/deployment_scanner.py) prefers the supplied clean `deployment` generation and falls back to the historical sibling root only when the supplied generation is absent.

[apps/api/app/plugins/prediction/soar/model_loader.py](../../apps/api/app/plugins/prediction/soar/model_loader.py) uses `joblib.load` for serialized model artifacts. The `.pkl` files are joblib artifacts even though their extension is `.pkl`; standard `pickle.load` raised `STACK_GLOBAL requires str`.

[apps/api/app/plugins/prediction/soar/prediction_engine.py](../../apps/api/app/plugins/prediction/soar/prediction_engine.py) preserves pandas DataFrame column names for the scikit-learn `ColumnTransformer` pipeline.

[apps/api/app/plugins/prediction/soar/explainability_adapter.py](../../apps/api/app/plugins/prediction/soar/explainability_adapter.py) wraps SHAP matrix inputs back into the named DataFrame schema required by the SOAR model.

## Environment

The project environment is Python `3.12.10` and now contains:

- pandas `3.0.5`
- scikit-learn `1.9.0`
- XGBoost `3.4.1`
- SHAP `0.52.0`
- joblib
- matplotlib
- seaborn
- pyarrow `25.0.1`

The separate Python `3.14.6` installation also has the relevant scientific packages, but Python 3.14 is not needed to load the supplied models. The compatibility issue was joblib serialization and input schema, not the Python minor version.

The dependencies are declared in [apps/api/requirements.txt](../../apps/api/requirements.txt).

## Validation Results

### SOAR

Passed:

- Scanner discovers the supplied deployment root.
- Ten deployments are discovered with numeric thresholds.
- All ten supplied `final_model.pkl` files load with joblib.
- SOAR plugin initializes successfully.
- Isolated real SOAR inference succeeds:
  - Deployment: Cefixime / *H. influenzae*
  - Predicted class: `R`
  - Probability: approximately `0.95585`
  - Threshold: `0.25`

The full SHAP-enabled plugin call reached explainability after model inference. It requires additional runtime time because KernelExplainer evaluates the model repeatedly. The supplied v2 verification records also show that historical inference validation was not clean.

### ARMD

Passed:

- ARMD plugin is concrete and instantiable.
- ARMD registry loads 20 antibiotics.
- WP3 preprocessing artifacts load.
- The supplied WP2 Parquet table loads after installing pyarrow.
- WP2 shape: `118767 x 68`.
- ARMD real prediction previously returned a valid `PredictionResult` with model version `0.1.0`.

### PluginManager

Passed in a fresh process:

```text
[('armd', True), ('soar', True)]
[('armd', '0.1.0', True), ('soar', '0.1.0', True)]
```

### Canonical endpoint

A real ARMD request to `POST /api/v1/pipeline/execute` previously returned HTTP `200` with a canonical explainability response and a Ceftriaxone recommendation after loading all 20 ARMD models.

The endpoint remains the only recommendation synthesis boundary. Standalone SOAR and ARMD prediction endpoints were not added.

## Remaining Required Work Before Clinical Deployment

1. Obtain or recompute clinically approved SOAR thresholds using a documented validation cohort and an approved objective such as Youden's J, F1/F-beta, or an explicitly cost-sensitive criterion.
2. Resolve the discrepancy between historical verification reports and current runtime inference behavior.
3. Perform independent temporal, country-grouped, and prospective validation with held-out outcomes.
4. Review domain-shift findings with a clinical/microbiology owner before enabling any affected drug/species model.
5. Replace placeholder or synthetic clinical simulation evidence with real outcome-based evaluation.
6. Define model acceptance thresholds, calibration requirements, abstention behavior, and monitoring policy.
7. Preserve model hashes, training data identifiers, package versions, threshold provenance, and validation reports in an immutable audit record.
8. Have a qualified clinical antimicrobial-stewardship reviewer approve the model/version/threshold combination before production use.

## Final Status

- **Technical startup:** PASS for SOAR and ARMD.
- **Real model loading:** PASS for supplied SOAR deployment generation and ARMD WP3 artifacts.
- **Real isolated inference:** PASS for SOAR model core and ARMD prediction path.
- **Canonical pipeline:** Previously PASS for real ARMD-backed HTTP execution.
- **Clinical accuracy:** NOT ESTABLISHED.
- **Production clinical approval:** NOT GRANTED.

## Runtime-Focused Cleanup

On 2026-08-27, the nested SOAR workspace was reduced to the active runtime artifacts and retained clinical/provenance evidence.

Removed:

- `.venv`, `.vscode`, `__pycache__`, and empty `output` directories.
- `artifact_recovery` and `artifact_recovery_v2`.
- `deployment_reconstructed` and `deployment_reconstructed_v2` duplicate generations.
- All 31 top-level development, training, inspection, recovery, and verification Python scripts.
- `.env`, which contained a plaintext Supabase database password.

Retained:

- `deployment`, the active SOAR runtime root containing 10 model deployments.
- `ml_output`, verification outputs, extraction reports, EDA, SHAP evidence, contracts, source datasets, and the breakpoint PDF.

Post-cleanup validation confirmed that the active runtime root remains discoverable and contains all 10 `final_model.pkl` artifacts, along with their label encoders, numeric thresholds, and evaluation CSV files. The repository-level `.venv` used by the API was not removed.
