# Phase 24.5D - Open Questions Resolution Matrix

| Question | Previous status | ZIP evidence | Resolution |
|---|---|---|---|
| What does beta `0` mean? | Unresolved | Phase 9 and Phase 10 map `NEG` to `0` | Resolved: Negative |
| What does beta `1` mean? | Unresolved | Phase 9 and Phase 10 map `POS` to `1` | Resolved: Positive |
| Are additional required features present? | Verified five/six split | Feature schemas and training script | Resolved: no additional runtime features |
| Are country vocabularies authoritative? | Artifact-derived | Per-deployment fitted metadata/schema | Resolved: deployment-specific artifact vocabularies remain authoritative |
| Are Region values authoritative? | Artifact-derived | OneHotEncoder metadata and feature schemas | Resolved: Asia, Europe, Middle East for applicable verified deployments |
| Are BodyLocation_Group values authoritative? | Artifact-derived | OneHotEncoder metadata and training grouping | Resolved: Blood, Other, Respiratory |
| Is Age transformed? | Known preprocessing | Phase 9 and preprocessing summaries | Resolved: StandardScaler owned by runtime pipeline |
| Is YearCollected transformed? | Known preprocessing | Phase 9 and preprocessing summaries | Resolved: StandardScaler owned by runtime pipeline |
| How is beta preprocessed? | Passthrough, semantic source unknown | Phase 9 mapping plus schema `bin` passthrough | Resolved: source POS/NEG mapping, then passthrough |
| Is missing data allowed? | Mixed | Phase 9 fills source beta missing as NEG; runtime engine requires payload features | Resolved: no frontend silent default; explicit status required |
| Are deployment-specific differences present? | Verified | Ten schemas | Resolved: beta field only for eight H. influenzae deployments |
| Can eight H. influenzae deployments execute? | Blocked | Training source mapping is now authoritative | Resolved: yes, through controlled status mapping |
| Is the original raw dataset bundled? | Unknown | Archive file inventory | Unresolved: scripts reference external dataset not included in ZIP |
| Are all archive scripts safe to execute? | Not applicable | Inspection policy | Unresolved/not attempted by design; no archive code was executed |
