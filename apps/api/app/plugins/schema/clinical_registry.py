from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict


SAFE_TO_SHARE = "SAFE_TO_SHARE"
SHARE_WITH_TRANSFORMATION = "SHARE_WITH_TRANSFORMATION"
PLUGIN_SPECIFIC = "PLUGIN_SPECIFIC"
SEMANTIC_CONFLICT = "SEMANTIC_CONFLICT"
UNRESOLVED = "UNRESOLVED"


CANONICAL_CLINICAL_FIELDS: Dict[str, Dict[str, Any]] = {
    "age": {
        "canonical_field_id": "age",
        "display_name": "Patient age",
        "description": "Patient age at assessment.",
        "data_type": "integer",
        "unit": "years",
        "clinical_semantics": "Chronological patient age.",
    },
    "infection_site": {
        "canonical_field_id": "infection_site",
        "display_name": "Infection site",
        "description": "Anatomical site associated with the infection.",
        "data_type": "string",
        "unit": None,
        "clinical_semantics": "Anatomical infection location; not a syndrome or diagnosis.",
    },
    "organism": {
        "canonical_field_id": "organism",
        "display_name": "Organism",
        "description": "Organism identified or selected for the plugin operation.",
        "data_type": "string",
        "unit": None,
        "clinical_semantics": "Named organism; distinct from an unspecified pathogen concept.",
    },
    "pathogen": {
        "canonical_field_id": "pathogen",
        "display_name": "Pathogen",
        "description": "Suspected respiratory pathogen used by SOAR routing and prediction.",
        "data_type": "string",
        "unit": None,
        "clinical_semantics": "Suspected respiratory pathogen; not automatically interchangeable with organism.",
    },
    "severity": {
        "canonical_field_id": "severity",
        "display_name": "Clinical severity",
        "description": "Clinical severity classification or score supplied to the plugin.",
        "data_type": "string",
        "unit": None,
        "clinical_semantics": "Severity representation; the source scale is not established by the runtime contract.",
    },
    "culture": {
        "canonical_field_id": "culture",
        "display_name": "Culture observations",
        "description": "Microbiology culture and susceptibility observations.",
        "data_type": "string",
        "unit": None,
        "clinical_semantics": "Culture observation text; not an organism identity.",
    },
    "prior_antibiotics": {
        "canonical_field_id": "prior_antibiotics",
        "display_name": "Prior antibiotics",
        "description": "Whether antibiotic exposure occurred in the previous 90 days.",
        "data_type": "boolean",
        "unit": "previous 90 days",
        "clinical_semantics": "Prior antibiotic exposure indicator.",
    },
}

CANONICAL_PLUGIN_MAPPINGS: Dict[str, Dict[str, Dict[str, Any]]] = {
    "soar": {
        "age": {"classification": SAFE_TO_SHARE, "runtime_mapping": "deployment Age feature when present; exact model contract is deployment-specific"},
        "infection_site": {"classification": UNRESOLVED, "runtime_mapping": "deployment BodyLocation_Group or equivalent; no established transform"},
        "organism": {"classification": SEMANTIC_CONFLICT, "runtime_mapping": "deployment species/organism context"},
        "pathogen": {"classification": UNRESOLVED, "runtime_mapping": "deployment lookup/model-specific feature"},
        "severity": {"classification": UNRESOLVED, "runtime_mapping": "not established"},
        "culture": {"classification": PLUGIN_SPECIFIC, "runtime_mapping": "not established"},
    },
    "armd": {
        "age": {"classification": SAFE_TO_SHARE, "runtime_mapping": "age and derived age_group"},
        "infection_site": {"classification": UNRESOLVED, "runtime_mapping": "site-related engineered feature; no established transform"},
        "organism": {"classification": SEMANTIC_CONFLICT, "runtime_mapping": "n_prior_organisms and days_since_last_prior_organism"},
        "prior_antibiotics": {"classification": PLUGIN_SPECIFIC, "runtime_mapping": "exposure count and timing features"},
    },
    "who_knowledge": {},
}


def canonical_field_metadata() -> Dict[str, Dict[str, Any]]:
    return deepcopy(CANONICAL_CLINICAL_FIELDS)


def canonical_plugin_mappings() -> Dict[str, Dict[str, Dict[str, Any]]]:
    return deepcopy(CANONICAL_PLUGIN_MAPPINGS)


def canonical_field_schema(field_id: str, classification: str, **runtime: Any) -> Dict[str, Any]:
    """Return schema annotations without turning runtime features into UI fields."""
    metadata = CANONICAL_CLINICAL_FIELDS[field_id]
    annotation: Dict[str, Any] = {
        "x-canonical-field-id": field_id,
        "x-mapping-classification": classification,
        "x-unit": metadata["unit"],
        "x-clinical-semantics": metadata["clinical_semantics"],
    }
    if runtime:
        annotation["x-runtime-mapping"] = runtime
    return annotation
