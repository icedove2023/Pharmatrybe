# Phase 22C — SOAR Deployment Routing Audit

## 1. What actually selects a deployment

`SOARPredictionPlugin._select_deployment()` (`apps/api/app/plugins/prediction/soar/soar_prediction_plugin.py`, verified by direct read of the executable code):

```python
def _select_deployment(self, request):
    payload = request.payload
    if "organism" in payload:
        matches = self._runtime_context.deployment_registry.get_by_organism(str(payload["organism"]))
        if matches:
            return matches[0]

    if "antimicrobial" in payload:
        matches = self._runtime_context.deployment_registry.get_by_antimicrobial(str(payload["antimicrobial"]))
        if matches:
            return matches[0]

    all_deployments = [dep for dep in self._runtime_context.deployment_registry.get_all() if dep.status == "valid"]
    if all_deployments:
        return all_deployments[0]

    raise RuntimeError("No valid SOAR deployment available for prediction.")
```

`get_by_organism` / `get_by_antimicrobial` (`deployment_registry.py`) compare against `DeploymentInfo.organism` / `DeploymentInfo.antimicrobial`, which are populated at scan time by `DeploymentScanner._parse_deployment_id()`.

## 2. `_parse_deployment_id()` — executed directly against every real deployment ID, not assumed

```python
def _parse_deployment_id(self, deployment_id):
    separators = ["__", "-", "_"]
    for separator in separators:
        if separator in deployment_id:
            parts = deployment_id.split(separator)
            if len(parts) >= 2:
                return parts[0].strip() or None, parts[1].strip() or None
    return None, None
```

This was executed live against every real deployment folder name in this session (not simulated by hand). Verified output:

| `deployment_id` | Parsed `organism` (returned by the real function) | Parsed `antimicrobial` (returned by the real function) | Correct organism | Correct antimicrobial |
|---|---|---|---|---|
| `Ceftriaxone_Haemophilus_influenzae` | `Ceftriaxone` | `Haemophilus` | Haemophilus influenzae | Ceftriaxone |
| `Doxycycline_Streptococcus_pneumoniae` | `Doxycycline` | `Streptococcus` | Streptococcus pneumoniae | Doxycycline |
| `Trimethoprim_Sulfa_Haemophilus_influenzae` | `Trimethoprim` | `Sulfa` | Haemophilus influenzae | Trimethoprim-Sulfamethoxazole |

**Verdict: `DeploymentInfo.organism` and `DeploymentInfo.antimicrobial` are swapped relative to their field names for every single one of the 10 deployments, and both are truncated to the first word wherever the real name contains an underscore (every organism name in this dataset does — `Haemophilus_influenzae`, `Streptococcus_pneumoniae`).** For the compound antimicrobial `Trimethoprim-Sulfamethoxazole` (folder name `Trimethoprim_Sulfa_...`), the parsed value degrades further to the meaningless fragment `"Sulfa"`.

This is not a partial or edge-case bug. It is present in 10 of 10 deployments and follows directly from a single, deterministic parsing function applied uniformly to every folder name in the naming convention this dataset actually uses (`<Antimicrobial>_<Genus>_<species>`).

## 3. Consequence for `_select_deployment()` — traced through, not assumed

Take a clinically correct request: `{"organism": "Haemophilus influenzae", "antimicrobial": "Ceftriaxone"}`.

1. `get_by_organism("Haemophilus influenzae")` compares against the registry's stored `.organism` values, which — per section 2 — are actually antimicrobial names (`"Ceftriaxone"`, `"Cefotaxime"`, `"Doxycycline"`, …). `"Haemophilus influenzae"` matches none of them. **Zero matches, for every deployment.**
2. Falls through to `get_by_antimicrobial("Ceftriaxone")`, compared against the registry's stored `.antimicrobial` values, which are actually truncated organism fragments (`"Haemophilus"`, `"Streptococcus"`). `"Ceftriaxone"` matches none of them either. **Zero matches, for every deployment.**
3. Falls through to the final branch: `return all_deployments[0]` — the first `status == "valid"` deployment in directory-sort order, **regardless of what was actually requested.**

**This means the organism/antimicrobial matching paths in `_select_deployment()` cannot ever succeed for any real request, for any of the 10 deployments, given the current parsing logic.** Every SOAR prediction request, whatever drug and organism the clinician actually specifies, is silently routed to the same arbitrary first deployment (currently `Cefixime_Haemophilus_influenzae`, by alphabetical directory order). This was traced through the actual matching functions against real registry data, not inferred.

## 4. Routing classification

| Routing path | Classification | Evidence |
|---|---|---|
| Exact `organism` match | **UNKNOWN → in practice, NEVER SUCCEEDS** | Traced in section 3; `.organism` values are populated from broken parsing |
| Exact `antimicrobial` match | **UNKNOWN → in practice, NEVER SUCCEEDS** | Traced in section 3; `.antimicrobial` values are populated from broken parsing |
| Fallback (`all_deployments[0]`) | **FALLBACK — and it is the path taken on essentially every real request today** | Directly reachable and, per the above, the *only* reachable path for realistic organism/antimicrobial payload values |

No deployment currently qualifies as `EXACT` or `EXPLICIT` routing. The system is, in its current state, entirely `FALLBACK`-routed regardless of clinician input.

## 5. Safety requirement (per governing instructions): no arbitrary fallback

The instructions this audit was performed under are explicit:

> IF exact deployment match exists → use that deployment.
> ELSE → SOAR deployment unavailable.
> Do NOT implement: nearest deployment, similar organism, default organism, default antimicrobial, first available model, arbitrary fallback.

The code as it exists today violates this requirement on every request. This is the single highest-priority finding of the entire Phase 22 audit: **as currently built, a clinician requesting a SOAR prediction for one drug/organism combination will silently receive a prediction from a different, unrelated drug/organism model, with no error and no indication in the response that a substitution occurred.**

## 6. Current implementation status

1. **Completed:** the scanner no longer parses deployment identity from folder names. It reads `species` and `antibiotic` from `deployment_info.json`, including when runtime artifacts and metadata are stored in the two verified roots described in Phase 22A.
2. **Completed:** `_select_deployment()` requires an explicit `context.deployment_id`, looks it up exactly, and raises `DeploymentSelectionError` for missing, unknown, or invalid deployments. The former `all_deployments[0]` fallback is no longer present.
3. **Remaining contract work:** the response and controlled frontend registry still need to be reviewed against the Phase 22 provenance and deployment-specific input requirements before SOAR can be marked approved. This scanner change does not approve any unverified clinical input.