# Phase 24.5A - SOAR_GSK Archive Inventory

## Archive
`SOAR_GSK.zip` at the project root. The archive contains 1,086 entries. It was inspected with a ZIP reader and selected text/JSON entries were extracted to an isolated temporary directory outside the repository. No archive script was executed, no notebook was run, and no dependency was installed from the archive.

## Inventory classification
| Archive area | Contents | Classification | Inspection |
|---|---|---|---|
| `phase9_automated_training.py` | Training pipeline, raw feature construction, POS/NEG mapping, sklearn preprocessing | AUTHORITATIVE_CANDIDATE | Read statically |
| `phase10_evaluate_and_export.py` | Repeated preprocessing and deployment export path | AUTHORITATIVE_CANDIDATE | Read statically |
| `phase12_clinical_simulation.py` | Clinical simulation transform and replay logic | SUPPORTING_EVIDENCE | Read statically |
| `deployment_reconstructed/<id>/` | Reconstructed metadata, feature schemas, preprocessing summaries, manifests, label mappings | SUPPORTING_EVIDENCE | JSON read directly |
| `artifact_recovery/<id>/` | Recovery metadata and schemas | SUPPORTING_EVIDENCE | JSON read directly |
| `deployment/<id>/` | Runtime models, label encoders, thresholds, metrics | RUNTIME_ARTIFACT | Not executed from archive |
| `ml_output/phase9_training/` | Model outputs, metrics, SHAP summaries | SUPPORTING_EVIDENCE | File tree and text metadata inspected |
| `ml_output/phase10_evaluation*/` | Evaluation reports and SHAP summaries | SUPPORTING_EVIDENCE | Text metadata inspected |
| `verification_output/` | Certification registries and health dashboards | SUPPORTING_EVIDENCE | JSON/CSV read directly |
| root Python scripts | Phase 1-13 data preparation, training, validation, recovery | AUTHORITATIVE_CANDIDATE or SUPPORTING_EVIDENCE by script | Read selectively; never executed |
| images/SHAP HTML and binary model files | Visualizations and serialized artifacts | SUPPORTING_EVIDENCE or RUNTIME_ARTIFACT | Not treated as semantic authority by filename alone |

## Dataset finding
The archive does not contain the original `soar_merged_enriched.csv`, XLSX, Parquet, or equivalent raw training dataset. The Phase 9 and Phase 10 scripts reference an external path (`C:\Users\Adetokunbo\Desktop\villi\soar_merged_enriched.csv`) that is not bundled in the ZIP. Therefore raw-column cross-tabulation was not possible from the archive.

## High-value evidence
The missing raw dataset does not prevent resolution because the bundled training and export scripts explicitly define the transformation used to create `Beta_Lactamase_enc`, and the deployment metadata independently confirms that the resulting field is a required passthrough feature.
