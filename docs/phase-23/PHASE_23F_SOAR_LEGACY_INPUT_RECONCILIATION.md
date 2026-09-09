# Phase 23F - SOAR Legacy Input Reconciliation

`pathogen`, `culture`, `infection_site`, `organism`, and `antimicrobial` are not model payload fields in the inspected deployment schemas. The current exact routing boundary uses `context.deployment_id`; organism and antimicrobial are verified deployment metadata, not substitute feature values.

No legacy field is mapped into `Age`, `YearCollected`, `Region`, `Country`, `BodyLocation_Group`, or `Beta_Lactamase_enc`. Legacy values must remain quarantined from the controlled SOAR execution payload unless an explicit future contract proves their use.
