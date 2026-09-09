# Phase 25B: F821 Error Inventory

Initial reproduction produced **23 F821 errors**.

| File | Name(s) | Count | Classification |
|---|---|---:|---|
| `app/knowledge/providers/soar/soar_provider.py` | `SOARModelLoader` | 1 | `MISSING_RUNTIME_IMPORT` |
| `app/models/diagnostic.py` | `Disease` | 1 | `VALID_FORWARD_REFERENCE_MISSING_TYPE_IMPORT` |
| `app/models/disease.py` | `Recommendation`, `Evidence`, `Diagnostic`, `Stewardship`, `Monitoring`, `FollowUp`, `Referral`, `Pathogen` | 8 | `VALID_FORWARD_REFERENCE_MISSING_TYPE_IMPORT` |
| `app/models/drug.py` | `Recommendation` | 1 | `VALID_FORWARD_REFERENCE_MISSING_TYPE_IMPORT` |
| `app/models/evidence.py` | `Disease`, `Recommendation` | 2 | `VALID_FORWARD_REFERENCE_MISSING_TYPE_IMPORT` |
| `app/models/follow_up.py` | `Disease` | 1 | `VALID_FORWARD_REFERENCE_MISSING_TYPE_IMPORT` |
| `app/models/monitoring.py` | `Disease` | 1 | `VALID_FORWARD_REFERENCE_MISSING_TYPE_IMPORT` |
| `app/models/pathogen.py` | `Disease`, `Recommendation` | 2 | `VALID_FORWARD_REFERENCE_MISSING_TYPE_IMPORT` |
| `app/models/recommendation.py` | `Disease`, `Evidence`, `Drug`, `Pathogen` | 4 | `VALID_FORWARD_REFERENCE_MISSING_TYPE_IMPORT` |
| `app/models/referral.py` | `Disease` | 1 | `VALID_FORWARD_REFERENCE_MISSING_TYPE_IMPORT` |
| `app/models/stewardship.py` | `Disease` | 1 | `VALID_FORWARD_REFERENCE_MISSING_TYPE_IMPORT` |

The SQLAlchemy references were valid relationship targets. The SOAR loader was a real existing class and required an import in the provider module. No suppression was added.
