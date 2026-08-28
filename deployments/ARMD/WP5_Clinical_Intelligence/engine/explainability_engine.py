"""
WP5 Module 2

Explainability Engine

This module wraps the validated WP4 SHAP implementation.

Responsibilities
----------------

• invoke WP4 SHAP generation

• collect generated figures

• return structured outputs

This module NEVER computes predictions.

Prediction remains inside WP4.

SHAP computation remains inside WP4.

Only orchestration happens here.
"""
from WP4.WP4_Decision_Engine import generate_shap_explanation

from ..schemas.structuredexplainability import (
    StructuredExplainability,
    FeatureContribution,
)
from __future__ import annotations

from pathlib import Path
from typing import Dict
import sys


# ---------------------------------------------------------------------
# Import WP4
# ---------------------------------------------------------------------

WP4_ROOT = Path(__file__).resolve().parents[2]

if str(WP4_ROOT) not in sys.path:
    sys.path.append(str(WP4_ROOT))


from WP4_Decision_Engine import (   # noqa
    generate_shap_explanation,
)


class ExplainabilityService:

    def build(
        self,
        patient_id,
        patient_df,
        registry,
        antibiotic,
        background,
        feature_names,
        model,
        scaler,
        patient_dir,
    ) -> StructuredExplainability:

        result = generate_shap_explanation(
            patient_id,
            patient_df,
            registry,
            antibiotic,
            background,
            feature_names,
            model,
            scaler,
            patient_dir,
        )

        positives = [
            FeatureContribution(
                feature=f,
                shap_value=float(v),
                direction="increase",
            )
            for f, v in result["positive_drivers"]
        ]

        negatives = [
            FeatureContribution(
                feature=f,
                shap_value=float(v),
                direction="decrease",
            )
            for f, v in result["negative_drivers"]
        ]

        return StructuredExplainability(
            antibiotic=antibiotic,
            probability=result["probability"],
            narrative=result["narrative"],
            positive_drivers=positives,
            negative_drivers=negatives,
            figures=result["figure_paths"],
        )