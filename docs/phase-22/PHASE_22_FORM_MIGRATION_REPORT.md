# Phase 22 Form Migration Report

## ARMD

Status: `PARTIALLY_MIGRATED`.

The assessment workflow now renders the approved `armd-direct-clinical-inputs@1.0.0` contract through `DynamicClinicalForm`. Only nine direct raw clinical fields are available. Values are synchronized into the existing clinical case store, and the governed ARMD adapter preserves them inside the ARMD payload boundary without preprocessing.

## SOAR

Status: `INTENTIONALLY_UNAVAILABLE`.

No SOAR field met the admission threshold. No deployment selector or dynamic SOAR form was created. Missing explicit routing context continues to fail safely.

## Legacy paths

Legacy static registry schemas remain compatibility metadata only. They are not contract sources and do not override the admitted ARMD contract.
