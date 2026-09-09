# Phase 20F End-to-End Provenance Validation Report

## Validation scope

The approved workflow is limited to WHO `SearchQuery.query_text`:

```text
Approved WHO SearchQuery contract
  -> exact registry resolution
  -> Phase 19 contract validation
  -> generic form/value validation
  -> WHO query adapter
  -> authenticated /who/search?q request
  -> retrieval response
```

SOAR and ARMD have no approved frontend workflow and therefore have no end-to-end form execution path. Their absence is an intentional fail-closed result.

## Provenance rules

Search results are knowledge retrieval output. They are not model predictions, recommendations, explainability evidence, or generated clinical reasoning. No default, placeholder, or inferred query value is submitted.

## Required tests

Tests cover exact contract resolution, provenance/approval, unsupported fields, invalid values, WHO query adaptation, SOAR routing non-inference, ARMD model-feature exclusion, and canonical authentication reuse.
