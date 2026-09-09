# Phase 24.5B - Beta-Lactamase Encoding Evidence

## Decision
`AUTHORITATIVELY_RESOLVED`

## Primary authority
The archive's bundled Phase 9 training script contains the exact source transformation:

```python
df['Beta Lactamase'] = df['Beta Lactamase'].fillna('NEG')
df['Beta_Lactamase_enc'] = df['Beta Lactamase'].map({'POS': 1, 'NEG': 0})
```

Evidence reference: `SOAR_GSK.zip:phase9_automated_training.py:85-86`.

The bundled Phase 10 evaluation/export script independently repeats the same transformation:

```python
df['Beta Lactamase'] = df['Beta Lactamase'].fillna('NEG')
df['Beta_Lactamase_enc'] = df['Beta Lactamase'].map({'POS': 1, 'NEG': 0})
```

Evidence reference: `SOAR_GSK.zip:phase10_evaluate_and_export.py:76-77`.

## Mapping
| Source clinical value | Encoded model value | Evidence |
|---|---:|---|
| `POS` / Positive | `1` | Phase 9 training and Phase 10 export scripts |
| `NEG` / Negative | `0` | Phase 9 training and Phase 10 export scripts |
| Missing source value | `NEG`, then `0` in training preprocessing | Phase 9/10 scripts; not used as a frontend default |

The missing-value behavior is training-data preprocessing behavior. The frontend does not silently apply it to a missing clinician value; the controlled form requires an explicit clinical status.

## Independent reconciliation
The archive's reconstructed feature schema identifies `Beta_Lactamase_enc` as the sixth raw feature and assigns it to the `bin`/passthrough transformer. This confirms the source script's encoded output is the value consumed by the deployment pipeline.

## Version and confidence
- Mapping version: `SOAR_GSK_Phase9_Training_v1`
- Evidence source: archive source scripts, repeated by evaluation/export code
- Confidence: high
- Authority: authoritative for the bundled SOAR_GSK training/deployment pipeline

The implementation exposes only `POSITIVE` and `NEGATIVE` to clinicians, maps them at the resolver boundary, preserves clinician provenance, and rejects raw numeric bypasses.
