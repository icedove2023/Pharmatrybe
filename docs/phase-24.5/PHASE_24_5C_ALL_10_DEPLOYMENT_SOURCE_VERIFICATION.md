# Phase 24.5C - All 10 Deployment Source Verification

## Source chain
`SOAR_GSK.zip:phase9_automated_training.py` constructs the raw feature set and preprocessing pipeline. `deployment_reconstructed/<deployment>/feature_schema.json`, `preprocessing_summary.json`, `deployment_info.json`, and the runtime `deployment/<deployment>/final_model.pkl` reconcile the source contract to each deployment artifact. The same ten deployment IDs are present in the active repository registry.

## Matrix
| Deployment | Identity source | Raw features | Beta mapping | Preprocessing | Status |
|---|---|---|---|---|---|
| Cefixime_Haemophilus_influenzae | deployment_info.json | Age, YearCollected, Region, BodyLocation_Group, Country, Beta_Lactamase_enc | POS->1, NEG->0 | StandardScaler, OneHotEncoder, TargetEncoder, passthrough | READY |
| Cefotaxime_Haemophilus_influenzae | deployment_info.json | Age, YearCollected, Region, BodyLocation_Group, Country, Beta_Lactamase_enc | POS->1, NEG->0 | Same verified pipeline | READY |
| Cefpodoxime_Haemophilus_influenzae | deployment_info.json | Age, YearCollected, Region, BodyLocation_Group, Country, Beta_Lactamase_enc | POS->1, NEG->0 | Same verified pipeline | READY |
| Ceftibuten_Haemophilus_influenzae | deployment_info.json | Age, YearCollected, Region, BodyLocation_Group, Country, Beta_Lactamase_enc | POS->1, NEG->0 | Same verified pipeline | READY |
| Ceftriaxone_Haemophilus_influenzae | deployment_info.json | Age, YearCollected, Region, BodyLocation_Group, Country, Beta_Lactamase_enc | POS->1, NEG->0 | Same verified pipeline | READY |
| Doxycycline_Streptococcus_pneumoniae | deployment_info.json | Age, YearCollected, Region, BodyLocation_Group, Country | Not applicable | StandardScaler, OneHotEncoder, TargetEncoder | READY |
| Levofloxacin_Haemophilus_influenzae | deployment_info.json | Age, YearCollected, Region, BodyLocation_Group, Country, Beta_Lactamase_enc | POS->1, NEG->0 | Same verified pipeline | READY |
| Tetracycline_Haemophilus_influenzae | deployment_info.json | Age, YearCollected, Region, BodyLocation_Group, Country, Beta_Lactamase_enc | POS->1, NEG->0 | Same verified pipeline | READY |
| Tetracycline_Streptococcus_pneumoniae | deployment_info.json | Age, YearCollected, Region, BodyLocation_Group, Country | Not applicable | StandardScaler, OneHotEncoder, TargetEncoder | READY |
| Trimethoprim_Sulfa_Haemophilus_influenzae | deployment_info.json | Age, YearCollected, Region, BodyLocation_Group, Country, Beta_Lactamase_enc | POS->1, NEG->0 | Same verified pipeline | READY |

## Reconciliation notes
All ten feature schemas agree with the Phase 23 contract split: five common fields, plus beta-lactamase only for H. influenzae. Feature order is documented in the schema, while the runtime submits a named DataFrame and the pipeline selects named columns. No hidden frontend preprocessing is required. Unknown values are not covered by a verified default in the runtime contract and must be rejected or explicitly collected.
