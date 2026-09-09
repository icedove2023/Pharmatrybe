# Phase 22A — SOAR Artifact Inventory

Read-only inventory. No artifact was modified. All findings below are from direct inspection (file listings, `joblib.load()` of the actual pickled objects, JSON manifest parsing) — nothing is inferred from field names or assumed from documentation alone.

## 0. Critical discovery before the inventory: two candidate deployment roots exist, and they are not identical

`DeploymentScanner.__init__` (`apps/api/app/plugins/prediction/soar/deployment_scanner.py`) resolves its scan root as:

```python
supplied_deployment = repository_root / "deployments" / "SOAR_GSK" / "SOAR_GSK" / "deployment"
self.deployments_root = supplied_deployment if supplied_deployment.is_dir() else repository_root / "deployments" / "SOAR_GSK"
```

Both paths exist in this repository:

| Candidate | Exists | Contents per deployment | Last modified |
|---|---|---|---|
| `deployments/SOAR_GSK/SOAR_GSK/deployment/<id>/` (**this is the one actually scanned at runtime — it exists, so it wins**) | Yes | `final_model.pkl`, `label_encoder.pkl`, `optimal_threshold.json`, `evaluation_metrics.csv` (4 files only) | Jul 16 / Jul 29 |
| `deployments/SOAR_GSK/<id>/` (richer folder, NOT scanned at runtime because the above takes precedence) | Yes | 28 files including `feature_schema.json`, `model_card.json`, `metadata.json`, `preprocessing_pipeline.pkl`, `backend_contract.json`, `validation_report.json`, SBOM, security audit, etc. | Aug 9–10 |

**The rich, self-documenting metadata files (`feature_schema.json`, `model_card.json`, etc.) are not present in the folder containing the runtime model files.** They exist in the adjacent top-level deployment folders. The scanner now treats the nested folder as the runtime artifact source and resolves the same deployment ID in the adjacent metadata root; it does not infer identity from the folder name.

Practical consequence: every deployment inspected in Phase 22B below was inspected against the exact runtime-active `final_model.pkl` (loaded via `joblib.load`), not against the documentation-only top-level folder, specifically to avoid this trap.

Good news, verified in Phase 22F: the `final_model.pkl` binary is byte-identical between both locations (same file size, same original `Jul 16 00:51` timestamp preserved in both), so the *model* itself is not divergent — only the *supporting documentation artifacts* are absent from the runtime-scanned location.

## 1. Full artifact inventory

| Artifact | Path pattern | Type | Deployment | Purpose | Inspection status |
|---|---|---|---|---|---|
| `final_model.pkl` | `deployments/SOAR_GSK/SOAR_GSK/deployment/<id>/final_model.pkl` | joblib-pickled `sklearn.calibration.CalibratedClassifierCV` | All 10 | The actual runtime-loaded model | INSPECTED — loaded directly |
| `label_encoder.pkl` | same dir | joblib-pickled `sklearn.preprocessing.LabelEncoder` | All 10 | Decodes numeric class (0/1) to `"R"`/`"S"` | INSPECTED — loaded directly |
| `optimal_threshold.json` | same dir | JSON, `{"threshold": <float>}` | All 10 | Decision threshold applied to predicted probability | INSPECTED — parsed directly |
| `evaluation_metrics.csv` | same dir | CSV | All 10 | Held-out evaluation metrics | Present, not required for input-contract determination; not parsed in depth for Phase 22 |
| `feature_schema.json` | `deployments/SOAR_GSK/<id>/feature_schema.json` (top-level folder only) | JSON | All 10 | Documents raw feature names, transformer assignment | INSPECTED — used to cross-validate against live model, see Phase 22F |
| `model_card.json` | top-level folder only | JSON | All 10 | Documents algorithm, feature counts, target labels | INSPECTED (Ceftriaxone deployment, representative) |
| `preprocessing_summary.json` | top-level folder only | JSON | All 10 | Documents transformer pipeline order | INSPECTED (Ceftriaxone deployment, representative) |
| `metadata.json` | top-level folder only | JSON | All 10 | Full nested pipeline structure dump (classes, module paths, hyperparameters, per-transformer column lists) | INSPECTED (Ceftriaxone deployment, representative) — confirms `handle_unknown="ignore"` on `OneHotEncoder` |
| `preprocessing_pipeline.pkl` | top-level folder only | joblib-pickled `ColumnTransformer` | All 10 | Standalone copy of the same preprocessor embedded in `final_model.pkl` | NOT required at runtime — see Phase 22F, section "Is the standalone preprocessor artifact needed?" |
| `backend_contract.json` | top-level folder only | JSON | All 10 | States required/available feature count and compatibility flag | INSPECTED (Ceftriaxone: `required=21, available=21, compatible=true` — this "21" refers to post-encoding feature count, not raw input count; see Phase 22F for reconciliation) |
| `calibration.pkl` | top-level folder only | joblib-pickled calibration artifact | All 10 | Redundant with calibration already embedded in `final_model.pkl`'s `CalibratedClassifierCV` wrapper | Present, not required at runtime |
| SBOM / security audit / verification files | top-level folder only | JSON/text | All 10 | Build provenance, not a runtime input contract | Not required for Phase 22 scope |

## 2. Runtime code paths inspected

| File | Role |
|---|---|
| `apps/api/app/plugins/prediction/soar/deployment_scanner.py` | Discovers deployment folders, parses `deployment_id` into `organism`/`antimicrobial` (see Phase 22C — this parsing is broken) |
| `apps/api/app/plugins/prediction/soar/deployment_registry.py` | In-memory lookup by `deployment_id`, `organism`, `antimicrobial` |
| `apps/api/app/plugins/prediction/soar/artifact_registry.py` | Classifies files in a deployment folder into categories (`MODEL`, `ENCODER`, `PREPROCESSOR`, `THRESHOLD`, etc.) by exact filename match |
| `apps/api/app/plugins/prediction/soar/model_loader.py` | Loads classified artifacts via `joblib.load`; silently sets `preprocessor = None` if no `PREPROCESSOR`-category file is found (this is fine — see Phase 22F) |
| `apps/api/app/plugins/prediction/soar/prediction_engine.py` | `_preprocess()` builds a `pandas.DataFrame` directly from the raw payload keyed by `model.feature_names_in_`, then calls `model.predict()` — no separate preprocessing step is invoked |
| `apps/api/app/plugins/prediction/soar/soar_prediction_plugin.py` | `_select_deployment()` — the deployment routing logic (see Phase 22C) |
| `apps/api/app/plugins/prediction/soar/runtime_context.py` | Wires the above together for the plugin |
| `apps/api/app/api/v1/pipeline.py` | The actual HTTP entry point (`POST /pipeline/execute`) that ultimately invokes the SOAR plugin's `predict()` |

## 3. Inspection method

A read-only inspection script was added at `scripts/inspect_soar_artifacts/inspect_runtime_deployments.py`. It:
- Resolves the exact same deployment root `DeploymentScanner` resolves (confirming the nested-folder precedence above).
- Loads each `final_model.pkl` with `joblib.load()`.
- Extracts `feature_names_in_`, `classes_`, and — by drilling into `CalibratedClassifierCV.calibrated_classifiers_[0].estimator.named_steps["preprocessor"].transformers_` — the **fitted category vocabulary** of every categorical encoder.
- Loads `label_encoder.pkl` and extracts `.classes_`.
- Parses `optimal_threshold.json`.
- Writes all extracted evidence to `docs/phase-22/_raw_inspection_output.json` for traceability.

This script does not mutate any artifact and was executed only against local files already present in the repository.

Two Python dependencies were required to complete inspection that were not already available in this environment: `scikit-learn==1.9.0` (to match the version the artifacts were pickled with — a lower installed version raised `InconsistentVersionWarning` and, in one case, changed unpickling behavior) and, for one specific deployment, `imbalanced-learn` (see Phase 22B/22F — `Tetracycline_Haemophilus_influenzae` embeds an `imblearn.pipeline.Pipeline`). **`imbalanced-learn` is not declared in `apps/api/requirements.txt`** — this is a real, verified gap that will cause that one deployment to fail to load in a production environment provisioned strictly from the declared requirements file. This is documented as a required fix, not applied automatically (Phase 22 scope is inspection, not backend modification).