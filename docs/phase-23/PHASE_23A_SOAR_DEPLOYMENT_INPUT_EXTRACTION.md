# Phase 23A - SOAR Deployment Input Extraction

## Evidence boundary
The runtime root is `deployments/SOAR_GSK/SOAR_GSK/deployment`. Each runtime folder contains `final_model.pkl`, `label_encoder.pkl`, `optimal_threshold.json`, and metrics. Identity and feature schema are read from the adjacent `deployments/SOAR_GSK/<deployment>/deployment_info.json` and `feature_schema.json`. Folder names are identifiers only.

## Actual deployment count
10 deployments were verified.

## Authoritative input matrix
| Deployment | Organism | Antimicrobial | Required raw features | Optional | Runtime/schema |
|---|---|---|---|---|---|
| Cefixime_Haemophilus_influenzae | Haemophilus influenzae | Cefixime | Age, YearCollected, Region, BodyLocation_Group, Country, Beta_Lactamase_enc | None verified | Yes |
| Cefotaxime_Haemophilus_influenzae | Haemophilus influenzae | Cefotaxime | Age, YearCollected, Region, BodyLocation_Group, Country, Beta_Lactamase_enc | None verified | Yes |
| Cefpodoxime_Haemophilus_influenzae | Haemophilus influenzae | Cefpodoxime | Age, YearCollected, Region, BodyLocation_Group, Country, Beta_Lactamase_enc | None verified | Yes |
| Ceftibuten_Haemophilus_influenzae | Haemophilus influenzae | Ceftibuten | Age, YearCollected, Region, BodyLocation_Group, Country, Beta_Lactamase_enc | None verified | Yes |
| Ceftriaxone_Haemophilus_influenzae | Haemophilus influenzae | Ceftriaxone | Age, YearCollected, Region, BodyLocation_Group, Country, Beta_Lactamase_enc | None verified | Yes |
| Doxycycline_Streptococcus_pneumoniae | Streptococcus pneumoniae | Doxycycline | Age, YearCollected, Region, BodyLocation_Group, Country | None verified | Yes |
| Levofloxacin_Haemophilus_influenzae | Haemophilus influenzae | Levofloxacin | Age, YearCollected, Region, BodyLocation_Group, Country, Beta_Lactamase_enc | None verified | Yes |
| Tetracycline_Haemophilus_influenzae | Haemophilus influenzae | Tetracycline | Age, YearCollected, Region, BodyLocation_Group, Country, Beta_Lactamase_enc | None verified | Yes |
| Tetracycline_Streptococcus_pneumoniae | Streptococcus pneumoniae | Tetracycline | Age, YearCollected, Region, BodyLocation_Group, Country | None verified | Yes |
| Trimethoprim_Sulfa_Haemophilus_influenzae | Haemophilus influenzae | Trimethoprim_Sulfa | Age, YearCollected, Region, BodyLocation_Group, Country, Beta_Lactamase_enc | None verified | Yes |

`Age`, `YearCollected`, and the three categorical fields are raw model inputs. Region and BodyLocation_Group have verified vocabularies (`Asia`, `Europe`, `Middle East`; `Blood`, `Other`, `Respiratory`). Country vocabularies are deployment-specific and encoded in the TypeScript registry. No numeric minimum/maximum is explicitly represented in the inspected artifacts. Beta_Lactamase_enc is passthrough numeric, but its 0/1 meaning is not evidenced.

## Missing-value and preprocessing boundary
The runtime model/pipeline owns scaling and categorical encoding. The resolver does not encode values or invent defaults. Missing required fields are returned structurally; unresolved beta-lactamase semantics remain blocked.
