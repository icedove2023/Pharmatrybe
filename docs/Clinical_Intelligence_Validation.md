# Clinical Intelligence Validation

## Purpose

Validate that the Clinical Intelligence Layer integrates cleanly with the prediction and knowledge plugin ecosystem and preserves strict responsibility boundaries.

## Required behavior

### Prediction plugins

Prediction plugins are expected to provide:

- ranked antibiotic predictions,
- probability distributions,
- confidence values,
- model metadata,
- SHAP or explainability output.

They must not create recommendations or decide therapy.

### Knowledge plugins

Knowledge plugins are expected to provide:

- WHO/AWaRe guidance,
- stewardship rules,
- antimicrobial metadata,
- clinical evidence,
- guideline references.

They must not perform predictions or recommendations.

### Clinical Intelligence Layer

The pipeline and downstream engines are the only components allowed to merge evidence and produce clinician-facing recommendations.

## Workflow validation

Validated execution path:

1. User request enters the system.
2. Workflow Manager selects relevant plugins.
3. Plugin routing policy filters the plugin set.
4. Prediction plugin outputs are collected.
5. Knowledge plugin outputs are collected.
6. ClinicalDecisionContext aggregates the plugin outputs.
7. Clinical rules evaluate against candidate antibiotics from predictions.
8. Decision fusion ranks recommendations.
9. Recommendation generator formats the result.
10. Explainability engine produces evidence-linked explanations.
11. Final CDSS response is returned.

## Result

Validated successfully using the Stage 4 pipeline tests in:

- [apps/api/tests/test_clinical_intelligence_pipeline.py](apps/api/tests/test_clinical_intelligence_pipeline.py)

The passing validation command was:

```powershell
Set-Location 'C:\Users\Adetokunbo\Desktop\Pharmatrybe_project\Pharmatrybe\apps\api'; & 'C:\Users\Adetokunbo\Desktop\Pharmatrybe_project\Pharmatrybe\.venv\Scripts\python.exe' -m pytest tests/test_clinical_intelligence_pipeline.py -q
```

Output summary:

- 8 passed
- 0 failed

## Certification decision

The Clinical Intelligence Layer is valid for integration as the stable orchestration point between prediction and knowledge plugins.
