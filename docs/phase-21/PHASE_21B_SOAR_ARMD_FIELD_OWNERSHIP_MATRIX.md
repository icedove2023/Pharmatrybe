# Phase 21B SOAR and ARMD Field Ownership Matrix

Every candidate has exactly one primary classification. `Frontend authority` means an explicit approved authority to render/edit a field, not merely runtime acceptance.

## SOAR

| Field | Evidence source | Meaning | Producer / owner | Frontend authority | Transformation | Classification | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `deployment_id` | SOAR adapter, deployment contract, tests | Exact artifact deployment selector | Explicit caller/platform routing context | No clinician authority | Exact registry lookup | ROUTING_METADATA | Rejected |
| `Age` | SOAR feature schema and frozen runtime contract | Runtime numeric age field | Request-time producer not established | None established | Artifact scaling/passthrough | ARTIFACT_FIELD | Rejected |
| `YearCollected` | SOAR feature schema | Collection year | Request-time producer not established | None established | Numeric preprocessing | ARTIFACT_FIELD | Rejected |
| `Region` | SOAR feature schema | Collection region | Request-time producer not established | None established | One-hot encoding | ARTIFACT_FIELD | Rejected |
| `BodyLocation_Group` | SOAR feature schema and mapping reports | Artifact body-location category | No approved clinical mapping | None established | One-hot encoding | PREPROCESSING_VALUE | Rejected |
| `Country` | SOAR feature schema | Collection country | Request-time producer not established | None established | Target encoding | ARTIFACT_FIELD | Rejected |
| `Beta_Lactamase_enc` | SOAR deployment variants | Deployment-specific encoded value | No approved laboratory producer | None established | Passthrough/bin handling | PREPROCESSING_VALUE | Rejected |
| `organism` | Deployment metadata/scanner | Artifact identity metadata | Deployment registry | No clinical authority | Deployment identity only | SYSTEM_CONTEXT | Rejected |
| `antimicrobial` | Deployment metadata/scanner | Artifact identity metadata | Deployment registry | No clinical authority | Deployment identity only | SYSTEM_CONTEXT | Rejected |
| `pathogen` | Legacy support key | Unconfirmed routing concept | No confirmed producer | None | None | UNRESOLVED | Rejected |
| `infection_site` | Legacy frontend field | Clinical site | Legacy case UI only | No SOAR authority | No safe mapping | UNRESOLVED | Rejected |
| `severity` | Legacy frontend field | Clinical severity | Legacy case UI only | No SOAR authority | Not in runtime schema | UNRESOLVED | Rejected |
| `culture` | Legacy frontend field | Culture observation | Legacy case UI only | No SOAR authority | Not in runtime schema | UNRESOLVED | Rejected |

## ARMD

| Field / group | Evidence source | Meaning | Producer / owner | Frontend authority | Transformation | Classification | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `age` | ARMD runtime schema/WP4 | Patient age runtime value | Producer not specified at plugin boundary | None established | Derives age groups | UNRESOLVED | Rejected |
| `gender_male` | WP4 whitelist | Encoded sex indicator | WP4 preprocessing | None | Encoded feature | PREPROCESSING_VALUE | Rejected |
| encounter flags | WP4 whitelist | Care setting indicators | Producer not specified | None | Imputation/alignment | UNRESOLVED | Rejected |
| procedure/device flags | WP4 whitelist | Procedure/device context | Producer not specified | None | Imputation/alignment | UNRESOLVED | Rejected |
| laboratory/vital fields | WP4 whitelist | Measurements such as creatinine, WBC, temperature | Laboratory/record producer not established | None for manual editing | Cleaning/scaling | UNRESOLVED | Rejected |
| antibiotic history fields | WP4 whitelist | Counts/timing of prior exposure | Producer not specified | None | Cleaning/scaling | UNRESOLVED | Rejected |
| organism history fields | WP4 whitelist | Historical organism exposure aggregates | Producer not specified | None | Cleaning/scaling | PLUGIN_SPECIFIC | Rejected |
| `adi_score`, `adi_state_rank` | WP4 whitelist | Aggregate context values | Producer not specified | None | Runtime/model preprocessing | MODEL_FEATURE | Rejected |
| `age_group` | ARMD preprocessing | Age band | Backend preprocessing | None | One-hot derivation | DERIVED_VALUE | Rejected |
| `log_days_since_abx` | ARMD preprocessing | Log-transformed exposure timing | Backend preprocessing | None | Derived transform | DERIVED_VALUE | Rejected |
| `age_group_*` | Feature order/model metadata | Encoded age columns | Backend preprocessing | None | One-hot encoding | MODEL_FEATURE | Rejected |
| model vector | Model metadata/features | Antibiotic-specific feature vector | Backend model pipeline | None | Alignment/scaling | MODEL_FEATURE | Rejected |
| `infection_site` | Legacy frontend field | Clinical site | Legacy case UI only | No ARMD authority | No deterministic mapping | UNRESOLVED | Rejected |
| `prior_antibiotics` | Legacy frontend field | Boolean history alias | No proven mapping | None | No safe transform to count/timing fields | UNRESOLVED | Rejected |
| `recent_hospitalization` | Legacy frontend field | Hospitalization history | No proven mapping | None | No safe transform | UNRESOLVED | Rejected |

## Matrix conclusion

No SOAR or ARMD candidate satisfies all approval conditions: explicit meaning, identifiable owner, producer provenance, frontend authority, and safe frozen-boundary mapping. No contract is registered.
