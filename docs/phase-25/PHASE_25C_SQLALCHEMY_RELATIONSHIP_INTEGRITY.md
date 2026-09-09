# Phase 25C: SQLAlchemy Relationship Integrity

## Audit result
All 22 ORM F821 references were valid forward references. Each target model exists, each relationship uses a valid target string, and the `back_populates` pairs are coherent.

| Owner | Relationship targets | Join/contract |
|---|---|---|
| `Disease` | `Recommendation`, `Evidence`, `Diagnostic`, `Stewardship`, `Monitoring`, `FollowUp`, `Referral`, `Pathogen` | Disease-owned one-to-many relationships plus `disease_pathogens` many-to-many |
| `Diagnostic`, `Evidence`, `FollowUp`, `Monitoring`, `Referral`, `Stewardship` | `Disease` | Paired disease relationships |
| `Evidence` | `Recommendation` | Paired evidence relationship |
| `Drug` | `Recommendation` | Paired drug relationship |
| `Pathogen` | `Disease`, `Recommendation` | Existing many-to-many association tables |
| `Recommendation` | `Disease`, `Evidence`, `Drug`, `Pathogen` | Paired relationships and `recommendation_pathogens` |

Every affected module already used `from __future__ import annotations`. The fix adds `TYPE_CHECKING` imports only, preventing runtime circular imports while allowing Flake8 to resolve the names. Runtime imports of `app.models` succeeded after the changes.

`SQLALCHEMY_RELATIONSHIPS = PRESERVED`
